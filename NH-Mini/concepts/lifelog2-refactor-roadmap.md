---
title: "Lifelog2 — Refactor Roadmap: Tier, Thread e Dati Affidabili"
type: concept
tags: [lifelog2, roadmap, refactor, confidence-tier, thread-model, pipeline, data-quality]
sources: [lifelog2-classification-evolution-blueprint-v1.md, lifelog-stage-d-blueprint-v1.md, lifelog2-pipeline-validation-roadmap.md, lifelog2-thread-builder-hardening-2026-07.md]
updated: 2026-07-06
---

# Lifelog2 — Refactor Roadmap: Tier, Thread e Dati Affidabili

Documento operativo del refactor emerso dalla sessione 2026-06-24. Sintetizza l'analisi completa del sistema corrente, i problemi fondamentali identificati, e le 5 fasi di intervento con task spuntabili. Costruito sull'architettura documentata in [[concepts/lifelog2-turn-classification]], [[concepts/lifelog2-quality-gate]], [[entities/systems/stack-lifelog2]].

---

## Perché questo refactor

### I tre problemi fondamentali

**Problema 1 — Non esiste un confidence score multi-dimensionale prima di Stage D.**
Stage C1 oggi decide con un gate binario (`avg_logprob < -0.55 → discard`). Tutto ciò che supera il gate entra in Stage D indistintamente. Un atom da un bar rumoroso con 5 speaker e logprob -0.45 riceve lo stesso trattamento di un monologo cristallino registrato in casa. Stage D produce JSON convincente su entrambi, senza sapere che uno è costruito su sabbie mobili.

**Problema 2 — Media contamina il personale senza filtro affidabile.**
`_annotate_turn_classes()` in Stage C classifica correttamente i turni isolati (Case 1 e 2), ma fallisce nel Case 3 (media interleaved con dialogo): un TG da 85s al bar viene etichettato `dialogue_likely` perché Roberto ha parlato prima e dopo. Stage D compensa leggendo il testo — ma questo è fragile, non determinisitco, e di fatto solo Stage C1 con `hybrid` conversation_type intercetta il pattern (via `max_other_turn_s > 45s`). Il Day Digest poi non usa questo segnale a valle.

**Problema 3 — Stage F (Episode) non conosce thread.**
Gli episodi sono raggruppamenti di atom per prossimità temporale. Non c'è concetto di "filo semantico" tra parlanti: un episodio mescola dialogo personale con media passivo dello stesso segmento fisico. Gli episodi non sono semanticamente puri → le analisi di secondo livello operano su miscele non classificate.

### Il paradigma mancante: due pool distinti

> **Il dato ha due pool: Trusted e Flagged.**
> Solo Trusted alimenta le analisi di secondo livello (Day Digest, Profile Builder, saghe, decisioni).
> Flagged è archiviato, ricercabile via API, ma non inquina nessuna aggregazione.

Questo si implementa con un **Confidence Score** calcolato in Stage C1, che determina il tier di estrazione e assegna ogni atom al pool corretto prima ancora che Stage D venga chiamato.

---

## Architettura Target — Overview

```
AUDIO IN
   │
Stage B ──► WAV 16kHz mono + quality gate (rms/snr/duration)
   │
Stage C ──► WhisperX ASR + diarization + _annotate_turn_classes() + metrics
   │
Stage C1 ──► [NUOVO] Confidence Score → extraction_tier (full/standard/minimal)
          ──► [NUOVO] Voiceprint Resolver → stable vp_ID cross-atom
          │
          ├── tier=MINIMAL ──► NO Stage D. Auto-titolo. Pool=flagged. STOP.
          ├── tier=STANDARD ──► Stage D (atom-level enrichment, imp≤0.55)
          └── tier=FULL ──► Stage D (cross-atom boundary authority)
   │
Stage D ──► [NUOVO] Boundary authority cross-atom per tier=FULL
   │         Mantiene log thread aperti in DB
   │         Assegna turni, aggiorna stati, finalizza thread
   │         Regole: gap>10min | 2 atom senza continuazione | 180 turni force-cut
   │         Output atom-level per tier=STANDARD (invariato)
   │
Stage E ──► [NUOVO] Thread Enrichment batched per tier=FULL
   │         Embedding per thread (tier=FULL) o per atom (tier=STANDARD)
   │
Stage G ──► Gate Trusted/Flagged → Day Digest filtra data_pool='trusted'

Note: Stage F (episodio grouper) rimosso — i thread finalizzati sono l'unità semantica diretta.
```

---

## Confidenze e Tier

### Formula Confidence Score

```python
def _compute_confidence(avg_logprob, snr_db, speaker_count, speech_ratio):
    transcript_conf = clip((avg_logprob + 1.2) / 0.9, 0.0, 1.0)
    # -0.30 → 1.0 | -0.55 → 0.72 | -0.75 → 0.50 | -1.20 → 0.0

    audio_quality = clip((snr_db - 3.0) / 20.0, 0.0, 1.0)
    # 3dB → 0.0 | 15dB → 0.60 | 23dB → 1.0

    diarization_c = clip(1.0 - (speaker_count - 2) * 0.15, 0.0, 1.0)
    # 2 speaker → 1.0 | 5 speaker → 0.55 | 8+ speaker → 0.0

    return transcript_conf * 0.50 + audio_quality * 0.30 + diarization_c * 0.20
```

### Tier e comportamento a valle

| Tier | Confidence | Stage D chiama | Pool | Threads |
|------|-----------|---------------|------|---------|
| **FULL** | ≥ 0.70 | Thread extraction, action items, decisions, persons | `trusted` | Sì |
| **STANDARD** | 0.40–0.69 | Summary atom-level, conv_type; importance ≤ 0.55 | `trusted` (flagged=partial) | No |
| **MINIMAL** | < 0.40 | Non chiamato — auto-titolo "audio complesso" | `flagged` | No |

### I tre casi reali mappati sui tier

| Scenario | Confidence stima | Tier | Pool |
|----------|-----------------|------|------|
| Casa + partner, ambiente silenzioso | ~0.97 | FULL | trusted |
| Podcast in cuffia, casa silenziosa | ~0.94 | FULL | trusted (ma media_passive → counted) |
| Ufficio rumoroso, colleghi, 4-6 speaker | ~0.44 | STANDARD o MINIMAL | trusted-partial o flagged |

---

## FASE 1 — Confidence Score e Dual Pool

**Dove**: Stage C1 (`stage_c1c2_gate.py`, `stage_c1_classifier.py`)
**Impatto immediato**: analisi di secondo livello non vengono più inquinate da audio degradato, anche senza thread model.

### Schema DB — campi nuovi

```sql
-- tabella segments
ALTER TABLE segments ADD COLUMN extraction_tier VARCHAR(8);
-- valori: 'full' | 'standard' | 'minimal'
ALTER TABLE segments ADD COLUMN confidence_score NUMERIC(4,3);

-- tabella memory_atoms
ALTER TABLE memory_atoms ADD COLUMN data_pool VARCHAR(8) DEFAULT 'trusted';
-- valori: 'trusted' | 'flagged'
```

### Task

- [ ] **C1-1** Implementare `_compute_confidence(avg_logprob, snr_db, speaker_count, speech_ratio)` in `stage_c1_classifier.py`
- [ ] **C1-2** Aggiungere colonne `extraction_tier` e `confidence_score` in `segments` (migration Alembic)
- [ ] **C1-3** Aggiungere colonna `data_pool` in `memory_atoms` (migration Alembic)
- [ ] **C1-4** Stage C1: scrivere `confidence_score` e `extraction_tier` su DB + emettere nel Redis payload verso Stage D
- [ ] **C1-5** Stage D: leggere `extraction_tier` dal payload e adattare comportamento — tier=MINIMAL → skip chiamata LLM, crea atom con `data_pool='flagged'`, titolo auto, `pipeline_status='done'`
- [ ] **C1-6** Stage D: tier=STANDARD → prompt esistente (v17 o successivo), ma `importance_score` cappato a 0.55, `data_pool='trusted'` con flag `partial=True` in metadata
- [ ] **C1-7** Stage G / `worker_day_digest.py`: aggiungere filtro `WHERE ma.data_pool = 'trusted'` a tutte le query di aggregazione
- [ ] **C1-8** Day Digest v5: aggiornare prompt per gestire correttamente anche atom STANDARD (summary senza entità) senza hallucinate dettagli
- [ ] **C1-9** Backfill: script offline che calcola `confidence_score` e `extraction_tier` sugli atom esistenti (da `avg_logprob` + `snr_db` già in DB) e aggiorna `data_pool` di conseguenza
- [ ] **C1-10** Test: verificare sui 3 scenari reali (casa/podcast/ufficio) che il tier sia corretto prima di merge

---

## FASE 2 — Voiceprint Resolver in C1

**Dove**: Stage C1 (nuovo step post-classification, pre-Stage D)
**Prerequisito**: FASE 1 completata.
**Scopo**: Sostituire le label locali WhisperX (`SPEAKER_00`, `SPEAKER_01`) con stable vp_ID cross-atom, rendendo il transcript comprensibile a Stage D attraverso più atom consecutivi.

### Principio

WhisperX assegna label SPEAKER_XX locali all'atom — si resettano a ogni segmento. I **voiceprint embedding** (256d ResNet34 Pyannote) sono invece fisicamente stabili: lo stesso parlante produce embedding simili in atom consecutivi della stessa sessione. Il resolver compara gli embedding dell'atom corrente con un session registry per assegnare stable ID coerenti.

```
Input:  speaker_turns atom_corrente {SPEAKER_00: emb_a, SPEAKER_01: emb_b}
        session_registry (Redis TTL 2h):
          {vp_hash_x: {stable_id: "vp_R", last_seen_at: T-3min, ...}}
          {vp_hash_y: {stable_id: "vp_unknown_a7f3", last_seen_at: T-3min, ...}}

Processo: cosine_similarity(emb_a, vp_hash_x) > 0.82 → SPEAKER_00 = "vp_R"
          cosine_similarity(emb_b, vp_hash_y) > 0.82 → SPEAKER_01 = "vp_unknown_a7f3"
          cosine_similarity(emb_b, qualsiasi existing) < 0.75 → SPEAKER_01 = "vp_new_c8d1"

Output: SPEAKER_00 → "vp_R"  |  SPEAKER_01 → "vp_unknown_a7f3"
```

**Soglie**: match se cosine similarity > 0.82, nuovo vp se < 0.75, ambiguous se 0.75–0.82 (trattato come nuovo in sessione, verificato alla prossima occorrenza).

**Solo per tier FULL** — tier STANDARD/MINIMAL ricevono solo la mappatura di Roberto (voiceprint enrollato, sempre matchabile).

### Schema DB

```sql
CREATE TABLE session_voiceprints (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    stable_vp_id VARCHAR(32) NOT NULL,    -- es. "vp_R", "vp_unknown_a7f3"
    voiceprint_embedding VECTOR(256) NOT NULL,
    person_id UUID REFERENCES persons(person_id),  -- NULL se non enrollato
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    atom_count INTEGER DEFAULT 1
);
```

**Session**: sequenza di atom con gap temporale < 30 minuti tra `ended_at` e `started_at` successivo.

### Task

- [ ] **VP-1** Creare tabella `session_voiceprints` (migration Alembic)
- [ ] **VP-2** Definire logica di sessione: funzione `get_or_create_session_id(user_id, atom_started_at, gap_minutes=30)` — cerca in Redis l'ultima sessione attiva, crea nuova se gap > 30min
- [ ] **VP-3** Implementare `_resolve_voiceprints(speaker_turns, session_id, user_id)` in Stage C1 — cosine similarity batch contro session registry, aggiornamento registry, ritorno dict `{SPEAKER_XX: stable_vp_id}`
- [ ] **VP-4** Stage C1: applicare la mappatura al transcript prima di emetterlo verso Stage D — sostituire label raw nel campo `speaker_turns` del payload Redis
- [ ] **VP-5** Stage D prompt v18: aggiornare per ricevere vp_R (Roberto) e vp_unknown_X invece di SPEAKER_XX — semplifica enormemente la comprensione dei thread
- [ ] **VP-6** Test: verificare cross-atom consistency su sessione di 3+ atom consecutivi (stessa sessione giornaliera)

---

## FASE 3 — Stage D: Thread Boundary Authority Cross-Atom [REVISIONE 2026-06-30]

**Dove**: Stage D (nuovo `stage_d_thread_boundary.py`) + tabelle `thread_candidates`, `thread_candidate_turns`
**Prerequisito**: FASE 2 completata (stable vp_ID disponibili).
**Solo per tier FULL.**

### Cambio architetturale

Il piano originale prevedeva Stage D come enricher per singolo atom, con Stage F come grouper cross-atom. Revisione 2026-06-30: Stage D diventa l'unica autorità semantica sui confini dei thread, cross-atom. Stage F rimosso. Stage E diventa l'enrichment layer.

**Valore aggiunto rispetto al vecchio approccio**: anziché arricchire atom misti e poi raggrupparli per similarità (episodi eterogenei), ora si identificano e cristallizzano i thread prima — unità omogenee per contesto, topic e parlanti — e si arricchisce ciascun thread finalizzato.

### Principio operativo

Stage D mantiene un log dei thread aperti in DB. Ad ogni atom per tier=FULL:
1. Legge stato thread aperti/pending (max 5-6 thread simultanei in atom con molti cambi di contesto, si risolvono entro 2 atom)
2. Legge nuovi turni da Stage C+C1 con tutti i metadati
3. Assegna turni al thread corretto o dichiara nuovo thread (anche confini intra-atom)
4. Aggiorna stati e rolling summary per thread lunghi
5. Finalizza thread secondo le regole di finalizzazione

### Stati thread

```
open → pending_finalization → finalized
         ↓ (se riprende entro 2 atom)
        open

Casi speciali (esclusi da Stage E):
  too_short             < 20 turni + nessun topic → label minima
  ambient_incomprehensible  speaker UNKNOWN, avg_word_score < 0.15
```

### Regole di finalizzazione

```
A) gap > 10 min tra ultimo turno thread e inizio atom corrente
   → FINALIZE immediato (gap batte topic e VP roster)

B) 2 atom consecutivi senza nuovi turni nel thread
   → FINALIZE (pending → finalized)

C) thread ≥ 180 turni (~60 min audio)
   → force-cut → FINALIZE Part N, apri Part N+1 con stesso parent_thread_id

Finalizzazione rapida (senza attendere 2 atom):
   - broadcast standalone: media_passive, speaker singolo, nessuna interazione
   - transazione completata con chiusura esplicita (addio, pagamento)

Thread Parts in dashboard: card separate con label "Parte 1 / Parte 2",
  timestamp = primo atom della parte, stesso parent_thread_id visibile.
```

### Gestione contesto LLM (Qwen3-14B, 16GB VRAM, Q4_K_M)

```
Modello:         ~8.5GB VRAM
KV cache:        ~6.5GB → ~35K token contesto
Budget sicuro:   30K token
Token per turno: ~120 token (testo + metadati JSON)

Caso tipico (1 thread aperto, 20 nuovi turni):
  system prompt + 40 turni thread + 20 nuovi = ~8.700 token   ← ampio margine

Caso complesso (5 thread in pending dopo atom ricco):
  system prompt + 5 thread × ~8 turni medi + 20 nuovi = ~9.100 token  ← ok
  Nota: i burst di thread aperti durano 1-2 atom poi si risolvono.
  Rolling summary solo per thread > 40 turni.

Force-cut: 180 turni → ~28.000 token per Stage E (entro budget)
```

### Schema DB

```sql
CREATE TABLE thread_candidates (
    thread_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID NOT NULL,
    status                VARCHAR(24) NOT NULL DEFAULT 'open',
    -- open | pending_finalization | finalized | too_short | ambient_incomprehensible
    pending_since_atom_id UUID REFERENCES memory_atoms(memory_id),
    parent_thread_id      UUID REFERENCES thread_candidates(thread_id),
    part_number           INTEGER DEFAULT 1,
    thread_type           VARCHAR(32),
    -- personal_dialogue | media_passive | personal_mono | ambient_dialogue
    vp_roster             TEXT[],
    turns_summary         TEXT,                -- rolling summary, aggiornato da Stage D
    first_atom_id         UUID REFERENCES memory_atoms(memory_id),
    last_atom_id          UUID REFERENCES memory_atoms(memory_id),
    atom_count            INTEGER DEFAULT 1,
    turn_count            INTEGER DEFAULT 0,
    created_at            TIMESTAMPTZ DEFAULT now(),
    finalized_at          TIMESTAMPTZ
);

CREATE TABLE thread_candidate_turns (
    id          SERIAL PRIMARY KEY,
    thread_id   UUID NOT NULL REFERENCES thread_candidates(thread_id),
    turn_id     UUID NOT NULL REFERENCES speaker_turns(turn_id),
    assigned_at TIMESTAMPTZ DEFAULT now()
);
```

**Il memory_atom rimane come contenitore fisico del segmento.** I thread sono unità cross-atom che ne attraversano più di uno.

### Stage D — struttura input/output per atom

```json
INPUT:
{
  "open_threads": [
    {
      "thread_id": "...",
      "type": "personal_dialogue",
      "turns_summary": "Roberto e collega parlano di deploy. 3 atom, 25 turni.",
      "last_turns": [...],
      "vp_roster": ["vp_R", "vp_unknown_a7f3"],
      "turn_count": 25,
      "gap_from_last_turn_s": 140
    }
  ],
  "new_turns": [...],
  "gap_from_prev_atom_s": 5
}

OUTPUT:
{
  "assignments": [
    {"turn_id": "...", "thread_id": "existing_or_new_uuid", "action": "append|new_thread"}
  ],
  "thread_updates": [
    {"thread_id": "...", "status": "open|pending_finalization|finalized|too_short",
     "reason": "gap_exceeded|no_continuation|semantic_closure|force_cut",
     "turns_summary_update": "..."}
  ]
}
```

### Task

- [ ] **TD3-1** Creare tabelle `thread_candidates` e `thread_candidate_turns` (migration Alembic)
- [ ] **TD3-2** Scrivere `stage_d_thread_boundary.py` — legge log DB, chiama Qwen3 locale, scrive stato aggiornato
- [ ] **TD3-3** Scrivere prompt `stage_d_boundary_v1.txt` in `prompts/` — regole finalizzazione, rolling summary, output JSON strutturato
- [ ] **TD3-4** `config.json`: aggiungere `"stage_d_boundary": "v1"` (prompt versioned, v1 mantiene il precedente come fallback)
- [ ] **TD3-5** Aggiungere colonna `thread_id` in `speaker_turns` (FK → thread_candidates, nullable)
- [ ] **TD3-6** Orchestrator: dopo Stage C1 per tier=FULL → chiama Stage D boundary (async via Redis queue)
- [ ] **TD3-7** Stage D: tier=STANDARD/MINIMAL → skip boundary, atom-level enrichment come attuale
- [ ] **TD3-8** Test: 5+ atom reali consecutivi — cross-atom continuity, force-cut podcast, micro-thread finalization, atom con 3 contesti (ufficio+notiziario+bar)

---

## FASE 4 — Stage E: Thread Enrichment Batched [REVISIONE 2026-06-30]

**Dove**: `stage_e_thread_enrichment.py` (sostituisce la logica di enrichment di Stage D per tier=FULL)
**Prerequisito**: FASE 3 completata.

### Principio

Stage E consuma la coda dei thread finalizzati da Stage D. Processa in batch fino al limite del contesto LLM. Per ogni thread nel batch: enrichment completo o label minima senza LLM.

I thread finalizzati sono l'unità semantica diretta — non sono più necessari episodi intermedi. Stage F (grouper) è rimosso.

### Batching e budget token

```
Stage E coda (Redis stream): thread_finalizzati[]

Per ogni batch:
  skip senza LLM:   too_short, ambient_incomprehensible → label minima rule-based
  accumula:         thread standard fino a ~28.000 token
  1 chiamata LLM:   enrichment array di tutti i thread del batch

Stima token per thread nel batch (120 token/turno):
  thread  8 turni  =    960 token
  thread 60 turni  =  7.200 token
  thread 180 turni = 21.600 token  (Part da sola, un batch intero)
```

### Output per thread arricchito

```json
{
  "thread_id": "...",
  "title": "Ordine al bar — bomboloni e caffè",
  "summary": "Roberto ordina due bomboloni con cioccolata e un caffè...",
  "topics": ["bar", "colazione"],
  "entities": ["Bar Centrale"],
  "persons": ["barista"],
  "places": ["bar"],
  "dates": [],
  "actions": [],
  "mood": "neutral",
  "importance": 0.30,
  "thread_type": "personal_dialogue",
  "part_label": null
}
```

**Thread Parts**: `part_label` = "Parte 1", "Parte 2" per thread con force-cut. Card separate in dashboard con stesso `parent_thread_id`. Timestamp = primo atom di ciascuna parte.

**Thread too_short**: enrichment minimale rule-based, label "Breve scambio", visibili in dashboard come collassati.

### Embedding

Thread arricchiti → embedding summary (mxbai-embed-large, 1024d su CT107). Invariato rispetto al vecchio Stage E, ma ora opera su thread (non atom) per tier=FULL.

### Task

- [ ] **TE-1** Scrivere `stage_e_thread_enrichment.py` — consumer Redis stream thread finalizzati, logica batching, parser risposta LLM
- [ ] **TE-2** Scrivere prompt `stage_e_enrichment_v1.txt` — multi-thread batch, output JSON array, gestione `part_label`
- [ ] **TE-3** `config.json`: aggiungere `"stage_e_enrichment": "v1"` (prompt versioned)
- [ ] **TE-4** Migration Alembic: aggiungere colonne enrichment su `thread_candidates` (title, summary, topics, entities, persons, places, mood, importance, part_label, embedding VECTOR(1024))
- [ ] **TE-5** Dashboard: card thread con timestamp primo atom; click → dettaglio turni + speaker; too_short collassati
- [ ] **TE-6** Test: batch con 3 thread piccoli + 1 grande — verifica budget token rispettato e enrichment corretto per tutti

---

## FASE 5 — Analisi secondo livello pulite

**Dove**: Stage Z4 (Day Digest), Stage Z6 (Thread Consolidation), Stage Z7 (Profile Builder), query frontend
**Prerequisito**: FASE 1 minimo (data_pool disponibile).
**Nota**: FASE 1 è sufficiente per ottenere il 70% del beneficio senza aspettare FASE 3–4.

### Regola universale

Tutte le aggregazioni di secondo livello aggiungono:

```sql
WHERE ma.data_pool = 'trusted'
  AND ma.retention_class != 'counted'
```

Il pool `flagged` è accessibile solo via query esplicita (endpoint `/api/atoms?pool=flagged`).

### Cosa vede Day Digest dopo FASE 1–5

- **Incluso**: atom trusted, personal_dialogue, personal_mono con importance > 0.25
- **Escluso**: atom flagged (MINIMAL tier), media_passive threads, ambient_dialogue threads
- **Narrativa**: solo ciò che Roberto ha vissuto direttamente, non ciò che trasmetteva la radio

### Task

- [ ] **SL-1** `worker_day_digest.py`: aggiungere filtro `data_pool = 'trusted'` alla query base atoms
- [ ] **SL-2** Day Digest v5 prompt: rimuovere la logica di difesa anti-media (ora gestita a monte dai tier) — semplificare il prompt
- [ ] **SL-3** `worker_thread_consolidation.py` (Z6): filtrare episodi `data_pool != 'flagged'` prima del mapping verso saghe
- [ ] **SL-4** Frontend `/timeline`: aggiungere toggle "Mostra tutto (incluso flagged)" — default OFF
- [ ] **SL-5** API endpoint `/api/atoms`: aggiungere parametro `?pool=trusted|flagged|all` — default `trusted`
- [ ] **SL-6** Frontend `/search`: ricerca fulltext include flagged ma con badge visivo "Qualità insufficiente"
- [ ] **SL-7** Backfill retroattivo: script che imposta `data_pool` sugli atom esistenti usando i campi già in DB (`avg_logprob`, `snr_db`, `analysis_tier`)

---

## Sequenza di implementazione

```
✅ FASE 1 — Completata 2026-06-25
  Confidence Score + extraction_tier + dual pool + Day Digest filtro data_pool

🔲 FASE 2 — Voiceprint Resolver in C1
  stable vp_ID cross-atom (prerequisito per Stage D boundary)

🔲 FASE 3 — Stage D Boundary Authority
  thread_candidates + thread_candidate_turns DB
  stage_d_thread_boundary.py + prompt v1
  [Test obbligatorio su 5+ atom reali prima di deploy]

🔲 FASE 4 — Stage E Thread Enrichment Batched
  stage_e_thread_enrichment.py + prompt v1
  Dashboard thread cards + too_short collapsing

🔲 FASE 5 — Analisi secondo livello pulite
  Day Digest, Thread Consolidation, Profile Builder su thread trusted
  Backfill data_pool su storico
```

---

## Cosa NON cambia

| Componente | Perché rimane invariato |
|------------|------------------------|
| Stage B (WAV + quality gate) | Solido, quality metrics già corretti |
| Stage C (WhisperX + diarization + per-turn embedding) | Rimane; per-turn VP embedding già refactored (2026-06-29) |
| Stage C1 (confidence score, tier, voiceprint resolver) | FASE 1 ✅ completata; FASE 2 da fare |
| Stage G (gate B→G) | Rimane, aggiunge solo filtro data_pool nella decisione |
| Schema MinIO | Nessun cambiamento ai path |
| Redis Streams | Nomi stream invariati — solo payload arricchito |
| Prompt versioning | Regola mantenuta — ogni prompt in file .txt versioned + config.json |
| Stage Z6 (Thread Consolidation) | Consumerà thread finalizzati invece di episodi (FASE 5) |

## Cosa cambia rispetto ai piani precedenti

| Componente | Decisione |
|------------|-----------|
| Stage F (episode grouper) | **Rimosso** — i thread finalizzati sono l'unità semantica diretta |
| Thread Builder (Stage F v2) | **Superato** — Stage D assorbe la logica cross-atom con comprensione semantica |
| Stage D (enrichment per atom) | **Ridefinito** come boundary authority cross-atom; enrichment passa a Stage E |
| Stage E | **Ridefinito** come thread enrichment batched; embedding invariato |
| Atom | Rimane artefatto fisico/forensico, non è più l'unità semantica di output |

---

## Cambio di paradigma — riepilogo

Il refactor non è un cambio architetturale radicale. È l'aggiunta di **un livello di classificazione della qualità** (FASE 1–2) che **precede** ogni estrazione semantica, e la propagazione di questa classificazione verso valle attraverso un sistema di pool. Il thread model (FASE 3–4) è un'estensione dell'output esistente di Stage D — non una sostituzione.

Il dato che si ottiene alla fine:

```
Ogni atom ha:
  confidence_score: 0.44
  extraction_tier: 'standard'
  data_pool: 'trusted' (partial)
  atom_threads: [{type: personal_dialogue, importance: 0.35, ...}]  (solo se tier=FULL)

Ogni episodio ha:
  thread_type: 'personal_dialogue'
  data_pool: 'trusted'

Day Digest vede:
  Solo trusted, solo personal/mixed, solo importance > 0.25
  → Narrativa pulita di ciò che Roberto ha vissuto direttamente
```

Il pool Flagged resta in Postgres e MinIO, ricercabile via API, ma **fisicamente separato dal flusso analitico**. Quando l'audio migliora (microfono migliore in ufficio, distanza ridotta), quegli atom possono essere riprocessati e promossi a Trusted.

---

## Aggiornamento post-implementazione (2026-06-29 → 2026-07-06)

Il Thread Builder (Fase 3 di questa roadmap) è stato implementato e poi sottoposto a un ciclo intenso di hardening su dati reali (upload da telefono, non più solo dataset sintetici). In sintesi rispetto al piano sopra:

- **Confidence/reliability**: `turn_reliability` (HIGH/LOW/JUNK) implementato come puramente funzione di `avg_logprob`, disaccoppiato dalla durata del turno.
- **Identità voiceprint**: eliminato il bucket condiviso `vp_unk_nr` (causava frammentazione — turni di persone diverse mescolati nello stesso bucket, la stessa conversazione spaccata in thread diversi a distanza di giorni). Sostituito da `vp_unk_noemb` (embedding inutilizzabile, mai identità) + soglia di durata `MIN_VP_TRUST_DUR_S=1.5s` per coniare nuove identità.
- **Thread semantici**: il Thread Builder LLM (Stage D) assegna i turn diarizzati direttamente ai thread — non più raggruppamento di episodi per prossimità temporale. Correzione meccanica del `thread_type` (personal↔ambient E mono↔dialogue) ad ogni chiusura, non solo alla creazione.
- **Force-cut per volume, non conteggio turni**: un thread con pochi turni ma ciascuno enorme (audio ambientale continuo) può sforare il context LLM di Stage E pur restando sotto qualunque soglia di conteggio turni — il force-cut ora si basa su un budget di caratteri/token, non su `FORCE_CUT_TURNS`.
- **Validato**: 675 segmenti reali processati puliti, 168 thread con 0 violazioni di gap.

Narrativa tecnica completa (causa → decisione → fix → validazione, con riferimenti ai commit): `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md`.

---

## Vedi Anche

- [[concepts/lifelog2-turn-classification]] — algoritmo deterministico turn-level (base di Fase 1)
- [[concepts/lifelog2-quality-gate]] — gate meccanico attuale Stage C1 (target di Fase 1)
- [[concepts/lifelog2-thread-consolidation]] — Stage Z6 saghe (target di Fase 5)
- [[entities/systems/stack-lifelog2]] — stack tecnico completo e pipeline attuale
- `sviluppi/Lifelog2/docs/lifelog2-classification-evolution-blueprint-v1.md` — blueprint classificazione e scenario analysis
- `sviluppi/Lifelog2/docs/lifelog2-pipeline-validation-roadmap.md` — piano operativo M0→M5 (baseline precedente)
- `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md` — hardening post-implementazione (2026-06-29 → 07-06)
