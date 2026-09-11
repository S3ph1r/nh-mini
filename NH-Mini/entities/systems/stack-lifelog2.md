---
title: "Stack — Lifelog2"
type: entity
tags: [stack, lifelog, memory, pipeline, embedding, identity, device, telemetry]
sources: [lifelog2-project-context.md, lifelog2-identity-resolution.md, lifelog2-session-digest-2026-09-02-device-channel.md, lifelog2-thinking-reprocess-audit-2026-09-11.md]
updated: 2026-09-11
---

# Stack — Lifelog2

**Lifelog2** è il Personal Memory Operating Layer del sistema NH-Mini: cattura audio Android cifrato,
lo trasforma in memoria strutturata multi-livello (Z0–Z7), la rende interrogabile tramite RAG
e la gestisce nel tempo con scoring, retention e oblio automatici.

## Architettura: Liquid Brain (M6+)
Lifelog2 opera come un **Guscio Vuoto** (Empty Shell) che carica on-demand l'esperienza dell'utente tramite una "cartuccia" virtuale (mount esterno). 

```
Android App (AES-GCM client-side)
  → CT202 Gateway
  → CT203 Lifelog Runtime (FastAPI — 🟢 live 2026-05-09)
  → CT120 Redis Streams (pipeline lifelog:stream:*)
  → CT105 Postgres (SOT — DB separati per persona)
  → CT104 MinIO (blob: audio cifrato, transcript, immagini)
  → CT107 Embedding Service (Ollama mxbai-embed-large 1024d)
  → PC139 ARIA (ASR, diarizzazione, voiceprint 256d, LLM enrichment qwen3-14b)
  → CT190 NH-Mini (control plane, dev center)
```

## Nodi Infrastrutturali

| Nodo | IP | Ruolo | Status |
|------|----|-------|--------|
| [[ct120-redis]] | 192.168.1.120:6379 | Redis Streams `lifelog:stream:*` | 🟢 live |
| [[ct105-postgres]] | 192.168.1.105:5432 | DB `lifelog_roberto` (pgvector, schema M1 applicato) | 🟢 live |
| CT104 MinIO | 192.168.1.104:9000 | Bucket `lifelog` — raw-decrypted-temp + altri prefissi | 🟢 live 2026-05-07 |
| CT107 nhi-embeddings | 192.168.1.107:11434 | Embedding service — mxbai-embed-large 1024d | 🟢 live |
| [[stack-aria]] PC139 | 192.168.1.139 | ASR, Diarize, Enrichment | 🟢 live |
| CT203 ct203-lifelog | 192.168.1.203:5173 | **Memory OS Dashboard** (SvelteKit) | 🟢 live |

## Design System: Obsidian Depth (Cinematic Memory OS)

L'interfaccia di Lifelog2 è stata evoluta da un modello glassmorphism generico a un sistema **Cinematic Dashboard** ispirato ad Apple TV+.

- **Aesthetic**: "Obsidian Depth" — Nero grafite profondo (`oklch(0.10 0.01 250)`), vignette radiali e grana cinematografica (noise).
- **Core Concept**: Il ricordo come "Poster" (vertical aspect ratio). Ogni card è una copertina di un film/libro.
- **Interazioni**: Overlay Sidebar (hover-activated, z-9999), Right Rail Filmstrip (lista compatta dei recenti), carousel orizzontali con wheel redirect e drag-to-scroll.
- **Typography**: Titoli in Inter (Sans), metadati tecnici in JetBrains Mono.

**Specifica tecnica completa della dashboard:**
`sviluppi/Lifelog2/docs/dashboard-spec-v1.md` — layout, componenti, mapping DB→API→UI, design tokens, roadmap viste future.

## Livelli di Zoom della Memoria (Z0–Z7)

| Livello | Nome | Entità DB | Granularità |
|---------|------|-----------|-------------|
| Z0 | Raw Evidence | RawCapture | Secondi |
| Z1 | Transcript/Turns | Segment, SpeakerTurn | Secondi–minuti |
| Z2 | Memory Atom | MemoryAtom + embedding(1024) | Minuti |
| Z3 | Conversation Thread | ConversationThread + thread_turns | Minuti–ore |
| Z4 | Day Digest | Day | Giorno |
| Z5 | Week/Month Review | (materialized views) | Settimana/mese |
| Z6 | Saga / Long Arc | Saga + topic_embedding(1024) | Mesi–anni |
| Z7 | Life Map | UserProfileFact | Anni–decenni |

## Embedding Architecture

- **MemoryAtom.embedding**: `vector(1024)` — mxbai-embed-large via CT107 Ollama
- **Thread.topic_embedding**: `vector(1024)` — mxbai-embed-large via CT107 Ollama
- **Person.voiceprint_embedding**: `vector(256)` — WeSpeakerResNet34 embedding via ARIA PC139. Roberto: **centroid di 17 segmenti** L2-normalizzati (norm=1.000, 256d). Re-enrollment massivo 2026-05-22: 1175 segmenti processati, **582 speaker_turns** matched con cosine ≥ 0.72 (max_sim=0.9371). ✅ Live 2026-05-22.

CT107 promosso da legacy a infra reale: LXC always-on, CPU, Ollama con mxbai-embed-large già installato.

## Architettura Liquid Brain (Isolamento Totale)

V2 implementa il paradigma **Swap-In / Swap-Out**:
- **Staging Area**: Bucket locale cifrato per ricezione 24/7 (Cervello scollegato).
- **Swap-In**: Caricamento DB Postgres da PC 139 a LXC 105 all'accesso utente.
- **Active**: Elaborazione e scrittura dei media direttamente sul mount esterno (PC 139).
- **Swap-Out & Purge**: Esportazione DB aggiornato su PC 139 e **cancellazione fisica** dei dati da LXC 105/104 alla chiusura sessione.

Questo garantisce che il server NH-Mini sia un "guscio vuoto" senza dati personali quando l'utente non è attivo.

## Pipeline (A–Z) — Thread Builder v2, turn-first (dal 2026-06-29)

> ⚠️ Il pipeline A→G qui sotto è la versione **corrente** (post Thread Builder v2). Le sezioni
> "Stage D — Enrichment Architecture" e "Stage F — Conversation Thread Grouping" più sotto in
> questa pagina descrivono ancora la versione **precedente** (atom-based, pre-2026-06-29) — non
> sono state riscritte per non perdere il riferimento storico, ma sono superate. Storia completa
> del redesign: `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md`.

```
A (Ingest Android M4A) 
→ B (Preprocess WAV 16kHz — LXC 203)
→ C (ASR + Diarize + Voiceprint 256d — PC 139 WhisperX large-v3 [primary])
→ C1 (Turn Classifier — LXC 203, vp_stable_id + turn_reliability meccanici, no LLM → Turn Log)
→ D (Thread Builder LLM — PC 139 qwen3-14b-q4km — decide confini semantici cross-atom sui turn)
→ E (Thread Enrichment LLM — PC 139 qwen3-14b-q4km — title/summary/topics sul thread chiuso)
→ F (Thread Embedding — LXC 107 mxbai 1024d, thread-level o thread_chunks se >20 turn)
→ G (Thread Cover Generation — PC 139 FLUX.2-klein-4B)
→ Z6 (Thread Consolidation — LXC 203 consolidamento saghe, ibrido: Gemini Cloud mapping + Qwen3 Locale sintesi)

**Identità voiceprint per turno** (`vp_stable_id`, redesign 2026-07-04): `vp_R` (self) ·
`vp_known_XXXXXXXX` (enrollata) · `vp_unk_XXXXXX` (identità distinta, coniata solo se durata
embedding ≥ 1.5s) · `vp_unk_noemb` (embedding inutilizzabile, mai identità — sostituisce il
vecchio bucket condiviso `vp_unk_nr` che causava frammentazione di thread). `turn_reliability`
(HIGH/LOW/JUNK) è puro `avg_logprob`, disaccoppiato dalla durata del turno.

**Chiusura thread** (tutta deterministica): gap >10min (state machine dinamica, non blocklist) ·
media_passive ≥30s (hard boundary). **Aggiornamento 2026-08-16**: il force-cut per volume di
testo in Stage D è stato **rimosso** — un thread resta sempre esattamente una riga
`conversation_threads`, mai spezzato a livello di entità. Il problema del volume che sforerebbe
il context LLM è stato spostato interamente in Stage E: il budget di caratteri viene calcolato
solo sui turni HIGH-reliability e, se eccede, Stage E divide il thread in "parti" puramente
metadata (`thread_turns.part_number`, nuovo campo — semantica diversa dal vecchio
`conversation_threads.part_number` ora morto) con un riassunto per parte in
`thread_part_summaries`; una chiamata LLM finale di fusione combina i riassunti di parte
nell'unico enrichment del thread. Contestualmente fixato anche un bug del gate `is_ambiguous`
(confrontava `THREAD_MIN_NARRATIVE_CHARS` contro il volume di TUTTI i turni invece dei soli HIGH)
e introdotto `audio_quality_score` su `conversation_threads` (media pesata di `avg_word_score`
per `word_count`, segnale continuo di affidabilità che affianca il gate binario `is_ambiguous`).
Dettagli completi: `sviluppi/Lifelog2/docs/lifelog2-data-architecture-v1.md` (blocco STATO
2026-08-16) e `sviluppi/Lifelog2/knowledge/architecture.md`.

[Worker indipendenti]
→ Identity Detective (ogni 15min, Qwen3 su ARIA → speaker → Person resolution)
→ Day Digest & Temporal Aggregation (giornaliero 01:00, Qwen3 su ARIA → Day Z4 divisi in Personal e Ambient)
→ Place Semantics & Detective (ogni 6h, LXC 203 euristica pura → PlaceHypothesis)
→ Profile Builder (ogni 6h, Strato 1+2 zero-LLM → UserProfileFact Z7)
→ Profile Validator — Strato V (ogni 24h, LLM gray-zone confidence 0.40–0.75)
```



### Stage D — Enrichment Architecture — ⚠️ SUPERATA (pre-2026-06-29, vedi Pipeline A–Z sopra)

Stage D produce un **MemoryAtom** per segmento. Gli speaker restano anonimi (`SPEAKER_XX`) fino a Stage E.

- **Input**: transcript + speaker_turns + `capture_class` (da Stage C via MinIO + Segment DB)
- **Task ARIA**: queue `aria:q:llm:local:qwen3-14b-q4km:lifelog`
- **Output MemoryAtom**: summary, topics, entities, decisions, action_items, sentiment, transcript_quality
- **Prompt versioning**: `prompts/config.json` → `prompts/stage_d_enrich_v{n}.txt` (nessun prompt hardcoded)
- **Prompt v15** (corrente): `extraction_level` a tre livelli (`full` / `contextual` / `metadata_only`). `metadata_only` attivato se quality score < 0.30 o < 30 parole o loop artifact: produce solo struttura, zero semantica, title = "Registrazione audio non elaborabile". `hallucination_flags` per rilevare loop e nomi inventati. `capture_class` ground truth invariato.
- **Noise filter**: `_NOISE_PHRASES` frozenset — filtra risposte LLM tipo "nessuna decisione esplicita".
- **`_parse_str_list()`**: normalizza str/list, applica noise filter per topics, action_items, decisions.
- **Timing warm**: ~49s totali (35s GPU switch + 12s inferenza)
- **Timing cold**: ~155-200s (LLM non in VRAM)

### Identity Resolution (3 livelli)

| Livello | Nome | Modalità | GPU |
|---------|------|----------|-----|
| RT (Stage D) | Speaker anonimi | MemoryAtom con SPEAKER_XX | LLM warm |
| Worker Detective | Inferenza identità da discourse | LLM solo (no ASR) — max 8 segmenti/call, ogni ora | LLM cold |
| Retroactive Indexer | Cosine similarity voiceprint 256d | CPU pura, scipy — < 5s su 1000+ segmenti | No GPU |

### Stage F — Conversation Thread Grouping — ⚠️ SUPERATA (atom-based, pre-2026-06-29)

> Sostituita dal Thread Builder v2 turn-first (Stage D nella pipeline corrente, vedi sopra):
> non più raggruppamento di atom per pass successivi, ma assegnazione diretta dei turn diarizzati
> via LLM. La "Limitazione nota" a fine sezione (thread_type non ricalcolato su extend) **è stata
> risolta** il 2026-07-04 con `_correct_thread_type_at_closure()`, che corregge entrambi gli assi
> (personal↔ambient E mono↔dialogue) ad ogni chiusura, non solo alla creazione.

Stage F v2 raggruppa memory atoms in `conversation_threads` in base al voiceprint roster degli speaker. Sostituisce il vecchio approccio 4-pass sliding window + episodes.

**Thread types:**

| Tipo | Condizione |
|------|-----------|
| `personal_dialogue` | Roberto + ≥1 interlocutore confermato |
| `personal_mono` | Solo Roberto |
| `media_passive` | Solo speaker media (TV/podcast), no Roberto |
| `ambient_dialogue` | Dialogo senza Roberto (o senza voiceprint) |
| `ambient_mono` | Mono ambientale |

**Pass 1 — vp_hash**: Per ogni speaker_turn, calcola sha256 del centroide voiceprint (o `person:{UUID}` per Roberto). Hashes persistiti su `speaker_turns.vp_hash`.

**Pass 2 — Role classification**: Classifica ogni turn come `roberto`, `interlocutor`, `media`, `ambient` da `speaker_turns.turn_type`. Costruisce il roster atom `{vp_hash → role}`.

**Pass 3 — Thread stitching**: Confronta roster atom con `voiceprint_roster` dei thread aperti. Match: vp_hash diretto o cosine ≥ `VP_COSINE_THRESHOLD=0.65` (fallback embedding). Roberto-anchor rule: thread `personal_*` richiedono Roberto presente. Thread tipo determinato dalla combinazione di ruoli nel roster.

**Pass 4 — ARIA closure**: Per ogni thread chiuso, chiama qwen3-14b per titolo + classificazione (`coherent`/`ambiguous`/`split_required`) + `visual_prompt` (40-60 parole, per Stage G). Geocoding: avg lat/lon atom → `find_or_create_place()`.

**Meccanismi di chiusura (doppio — stesso semantico):**
- `CLOSE_AFTER_ATOMS = 2`: 2 atom consecutivi senza match roster VP → chiusura atom-based (~10 min)
- `MAX_THREAD_GAP_S = 10 * 60`: gap temporale tra atom > 10 min → chiusura inline (usa timestamp atom, non wall clock — intercetta atom scartati a monte per bassa qualità che avrebbero creato falsi gap "silenzio=0")
- `atoms_without_turn`: counter per thread; incrementa solo su atom processato senza match, non su atom scartati/silenzio → ecco perché serve il timestamp-gap

**Correttezza timestamp (fix 2026-06-27):** `ended_at = last_atom_at` (timestamp contenuto atom, mai `NOW()`).

**Tabelle DB (migrations 0022–0024):**
- `conversation_threads`: thread_id, thread_type, thread_status, started_at, ended_at, last_atom_at, last_atom_at, voiceprint_roster (JSONB), atoms_without_turn, title, summary, topics, sentiment, coherence_score, atom_count, data_pool, place_id, visual_prompt, cover_image_key
- `thread_turns`: id, thread_id, memory_id, turn_id, vp_hash, person_id, canonical_label, thread_role, sequence_pos, atom_sequence, turn_offset_ms — join N:M atoms↔threads con metadati ruolo

### Stage G — Episode Cover Generation (FLUX.2-klein-4B)

Worker batch: trova `conversation_threads` con `visual_prompt IS NOT NULL AND cover_image_key IS NULL`, genera PNG via ARIA e salva URL MinIO.

**Stack ARIA:**
- Backend: `backends/flux_imagegen/server.py` — FastAPI porta 8092
- Pipeline: `Flux2KleinPipeline` (diffusers 0.39.0.dev0) + Qwen3-4B text encoder INT8 (`optimum-quanto`) + transformer BF16
- VRAM: **12.8 GB** allocati su 16 GB (3.2 GB headroom)
- Modello: `data/assets/models/flux2-klein-4b/` — 15.8 GB (text_enc 8 GB + transformer 7.75 GB + VAE 168 MB)
- Conda env: `envs/flux-aria` (Python 3.11 + PyTorch 2.7.0+cu128 + diffusers 0.39.0.dev0 + optimum-quanto 0.2.7)

**Comunicazione:**
- Lifelog2 → Redis queue `aria:q:imagegen:local:flux2-klein-4b:lifelog` (AriaImageGenClient)
- ARIA orchestrator → `_process_flux_task()` → HTTP POST localhost:8092/generate
- Output: PNG 512×512 in MinIO `aria-warehouse/lifelog-covers/{episode_id}.png`

**Timing (misurato):** 6.4s/immagine (512×512, 20 steps) una volta VRAM carica. Startup: 192s totali (pipeline load + quantizzazione INT8 in 63.6s). Prima generazione: ~12.6s (JIT warm-up).

**GPU Swap Architecture:** Stage F (Qwen3-14B warm) genera visual_prompt nella stessa sessione. Stage G swappa su FLUX. 1 swap GPU totale per entrambe le operazioni.

### Z4 Day Digest & Temporal Aggregation (2026-05-22)

Un worker periodico (`worker_day_digest.py`) esegue l'aggregazione giornaliera a livello di zoom Z4, sintetizzando l'intera giornata dell'utente.

> ⚠️ **LEGACY**: Il worker Day Digest referenzia ancora la tabella `episodes` (rimossa con migration 0022 — FASE 3 June 2026). Esce immediatamente senza elaborare nulla. Refactor pianificato: riscrivere per operare su `conversation_threads` (data_pool='trusted') + `memory_atoms`. Vedi [[concepts/lifelog2-thread-consolidation]].

- **Estrazione dei dati (Europe/Rome)**: Estrae tutti i `conversation_threads` (tipo `personal_*`) e `MemoryAtoms` registrati per una data specifica. I metadati temporali vengono convertiti in base alla timezone di Roma, mentre le interrogazioni al database Postgres avvengono in UTC per coerenza infrastrutturale.
- **Aggregazione Metadati**: Estrae persone incontrate (tramite join su `speaker_turns`), luoghi fisici e semantici visitati (tramite `places` geocodificati) e argomenti deduplicati del giorno.
- **Generazione LLM (Aria Qwen3)**: Costruisce un prompt testuale unificato e interroga Qwen3 per produrre:
  - `daily_digest`: Paragrafo narrativo in italiano fluido e intimo.
  - `key_events`: Fino a 4 eventi chiave sintetici e precisi.
  - `open_loops`: Task in sospeso, promesse o argomenti rimasti aperti.
  - `mood_arc`: Breve sintesi dell'andamento dell'umore e del focus emotivo.
- **Salvataggio Postgres**: Esegue l'upsert sicuro nella tabella `days` tramite casting standardizzato `CAST(:key_events AS jsonb)` per evitare conflitti SQLAlchemy raw SQL.
- **Pianificazione**: Servizio systemd `lifelog2-day-digest.service` e relativo timer `lifelog2-day-digest.timer` configurati a runtime su **LXC 203** per girare ogni notte all'**01:00 AM (Europe/Rome)** con modalità catch-up automatica (`--days N`).
- **Cinematic UI (Svelte 5 runes)**: Visualizzazione in cima alla route `/day/[date]` con una scheda premium glassmorphic, vignette dark, chip interattivi per persone/luoghi e warning box colorati per evidenziare visivamente gli open loops.

### Control Plane v2 (2026-05-15)


**Telemetry SQLite** (`/opt/Lifelog2/data/telemetry.db`) — statistiche pipeline persistenti. 5 tabelle: `upload_events`, `pipeline_events`, `grouping_runs`, `service_events`, `snapshot`. Worker B/C/D/E/F instrumentati con `time.perf_counter()`.

**API:** `GET /orchestrator/status` (Redis + Postgres reale), `GET /orchestrator/logs` (merge log file worker), `GET /telemetry/{summary,stages,recent,uploads/recent,grouping,daily}`.

**Pipeline Dashboard** (`/pipeline`): 5 sezioni — Workers (lag/pending/timing), Redis Streams (lunghezze reali), DB Stats, Telemetria, Log Terminal (polling 4s).

**CT203 timezone:** `Europe/Rome (CEST UTC+2)` — fixato 2026-05-15 via `ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime` (D-Bus `timedate1` era bloccato).

---

### Orchestrator — Sequential Greedy Coordinator

L'orchestratore (`lifelog2.services.orchestrator`) è il processo padre avviato da systemd. Gestisce i worker B–E e Stage F.

**Logica principale (B→E)**: Sequential greedy — controlla in ordine B→C→D→E il primo stage con lavoro (`lag > 0` o `pending > 0`), lo avvia e aspetta drain completo (`lag=0 AND pending=0`), poi lo ferma e ricomincia dal controllo. Un solo stage attivo alla volta.

**Stage F (parallelo)**: gira come `asyncio.create_task` indipendente ogni `GROUPING_INTERVAL_S` = 30 minuti. Primo run dopo 60s di startup delay. Usa `asyncio.create_subprocess_exec` (non `subprocess.Popen`) per compatibilità async. Un `asyncio.Event` (`_grouping_trigger`) permette trigger manuale interrompendo il sleep.

**`_reconciliation_loop`** (ogni 10min): **Sezione 1** — ri-emette su `stream:asr` segmenti stuck in `asr`/`preprocessed` (Stage B/C xadd fallito). **Sezione 2** (2026-06-08) — ri-emette su `stream:embed` segmenti stuck in `enriched` con `memory_atom_id IS NOT NULL` (Stage D race condition commit-before-xadd). Le due sezioni sono indipendenti.

**Comandi via Redis** (`LPUSH lifelog:orchestrator:cmd`):
- `{"cmd": "restart", "worker": "stage_c"}` — restart manuale worker
- `{"cmd": "run_grouping"}` — trigger immediato Stage F
- `{"cmd": "run_detective"}` — trigger immediato Worker Detective
- `{"cmd": "run_covers"}` — trigger immediato Stage G

**Status** (`lifelog:orchestrator:status`, TTL 30s): include `workers` (lag/pending/pid/uptime per ogni stage) + `grouping` (status/last_run_at/next_run_at/interval_s).

### Stage B — Preprocess Quality Metrics

**Fix 2026-05-15**: prima del fix, i segment scartati (too_short, low_rms, low_snr, no_speech) avevano NULL su `rms_db`, `snr_db`, `speech_ratio`, `duration_seconds` nel DB. La funzione `_reject()` ora accetta parametri opzionali per i quality metrics e li persiste sempre, permettendo analisi post-hoc sullo scarto.

**SNR proxy**: `snr_db = rms_db - (-40.0)`. Non è un vero SNR ma un proxy basato sul livello RMS. Un segmento a -39 dBFS → snr=1 dB → sotto soglia 3 dB → scarto.

## Retention Classes

`ephemeral` → `generic` → `useful` → `important` → `sacred` + `sensitive` (vault separato)

## Stato Sviluppo

| Milestone | Stato | Note |
|-----------|-------|------|
| M0 — Foundation/Product Spec | ✅ Done | Blueprint, memory model, API contracts frozen (2026-05-07) |
| M1 — Infrastructure + API Ingest | ✅ Done | CT105 DB live, MinIO bucket live, FastAPI su CT190:8002, 4 endpoint Android testati, 20 segmenti V1 in pipeline |
| M2 — Pipeline Stage B (Preprocess) | ✅ Done | Consumer Redis `lifelog:stream:ingest`, ffmpeg WAV 16kHz, quality gate, MinIO `normalized-audio/`, emit `lifelog:stream:asr` (2026-05-07) |
| M3 — Pipeline Stage C (ASR) | ✅ Done | Refactored 2026-05-12: `capture_class`, user-first voiceprint, drain loop fix. **2026-05-14: WhisperX large-v3 (porta 8091) come backend primario** — sostituisce Qwen3-ASR-1.7B (standby). Timing Stage C: ~24s warm (vs ~55s). Pipeline A→E: 91s totali su 299s audio (3.3× realtime). **2026-06-24: Turn-level classification** — `_annotate_turn_classes()` assegna `turn_class` (`personal`/`media_passive`/`dialogue_likely`/`ambiguous`) a ogni turno diarizzato. Nuovo campo `max_other_turn_s` in metriche; `hybrid` conversation_type attivato quando `max_t>45s AND avg_t<60s`. Scritto su `speaker_turns.turn_type`, MinIO blob e Redis emit. Vedi [[lifelog2-turn-classification]]. |
| M4 — Stage D (LLM Enrichment) | ✅ Done 2026-05-13 | **Prompt v10** (corrente, 2026-05-22): capture_class-aware + sentiment + transcript_quality + scoring tier. v8 (2026-05-20): prime versioni capture_class-aware. v5 (2026-05-15): action_items + decisions. Noise filter `_NOISE_PHRASES`. |
| M4.5 — Stage E (Embedding + WAV cleanup) | ✅ Done 2026-05-13 | mxbai-embed-large 1024d via CT107, `memory_atoms.embedding` aggiornato, WAV MinIO eliminato, pipeline_status="consolidated". Fast Pipeline A→E operativa. |
| M5 — Conversation Thread Grouping | ✅ Done | Stage F v1 live 2026-05-15 (episodes, 4-pass sliding window). **FASE 3 (2026-06-26):** Stage F v2 RISCRITTO — `conversation_threads` (5 tipi), VP roster per thread, `CLOSE_AFTER_ATOMS=2` + `MAX_THREAD_GAP_S=10min`, `ended_at=last_atom_at` (fix 2026-06-27). Migrations 0022-0024. Stage G trigger: da `_grouping_loop` post-drain (fix 2026-06-27 — rimossa race condition ARIA FLUX2/qwen3). DB reset + backfill v2: 1301 atoms, 2026-06-27. **Thread Builder v2 (2026-06-29 → 07-06, migration 0026/0028):** riscritto turn-first — D=Thread Builder LLM, E=Thread Enrichment LLM, F=Thread Embedding. Redesign identità VP (`vp_unk_nr`→`vp_unk_noemb`), gap-enforcement dinamico, correzione meccanica mono/dialogue, naming MinIO anti-disastro, force-cut per volume testo (non conteggio turni) — validato su 675 segmenti reali da telefono. Dettagli: `docs/lifelog2-thread-builder-hardening-2026-07.md`. |
| M5.5 — Thread Consolidation (Stage Z6) | ✅ Done 2026-05-26 | Worker periodico con approccio ibrido (Gemini cloud via ARIA per mapping in batch di max BATCH_SIZE=15 + Qwen3 locale per la sintesi dei singoli thread). Embedding 1024d salvati su Postgres. Testato e validato in produzione. **[Correzione 2026-09-02]**: verificato che `sagas` aveva 0 righe prima di oggi — il worker non era mai stato eseguito contro dati reali fino al primo dry-run di questa sessione (17 episodi, 5 saghe create, dump verificati). La riga sopra descriveva probabilmente uno stato pianificato/di test isolato, non un run reale continuativo — non cancellata, solo corretta qui. Vedi `docs/lifelog2-session-digest-2026-09-02-device-channel.md` §3. |
| M6 — Scoring/Retention v1 | Pending | Quality/attention scoring, retention class, oblio automatico. **Gap noti da risolvere in M6**: (1) `discarded` segments (audio senza atom prodotto) non vengono cancellati da MinIO — `_reject()` in Stage B tenta la cancellazione ma swallows l'eccezione; backfill non cancella mai il sorgente. File a valore zero si accumulano indefinitamente. (2) `cleanup_ambient_audio.py` copre solo `capture_class='ambient'`; nessuna policy per mixed/personal o staged abbandonati. (3) Policy corretta da implementare: `discarded` → cancellazione entro 24h; `consolidated` → retention basata su `retention_class` atom (ephemeral/counted/summarized/remembered/preserved); `staging` orfani > 30gg → discard + cancellazione. |
| M7 — Frontend SvelteKit | ✅ Done | **Cinematic UI** live su CT203:5173. Views: Dashboard, Day, Map, People, Sagas, Timeline, Transcript, Pipeline, Tasks, Profile. Audio playback MP3 su transcript. Sfondo bg.jpg + oklch. |
| M8 — Intelligence Layer Z7 | 🔧 In progress | **Profile Builder Strato 1+2 live** (2026-05-22). Strato V + Cerchia Tier B + HNSW index: P2 roadmap. `lifelog2-status-roadmap.md` come checklist periodica. |

## Frontend Views (CT203:5173)

| View | Route | Descrizione |
|------|-------|-------------|
| Dashboard | `/` | Hero episode, filmstrip rail, bande episodi multi-giorno |
| Day | `/day/[date]` | Episodi + atom del giorno, nav prev/next, link transcript |
| Tasks | `/tasks` | Tracciamento action items e decisioni estratte dai ricordi |
| Map | `/map` | Leaflet CircleMarker GPS, filtro periodo, detail panel |
| People | `/people` | Directory persone, identity badge, voiceprint dot, filtro livello |
| Sagas | `/sagas` | Library episodi filtrabili per classe + tag, load-more |
| Timeline | `/timeline` | Linea verticale mese/giorno, spine SVG, dot colorati per classe |
| Transcript | `/transcript/[id]` | Speaker turns colorati, full text, sidebar metadata, audio playback MP3 |
| Pipeline | `/pipeline` | Control Plane v2 — Workers, Streams, DB, Telemetria, Logs |
| Profile | `/profile` | UserProfileFact viewer — fatti estratti dal Profile Builder, confidenza, categorie |

**Design system**: sfondo `bg.jpg` su elemento `html` (fixed, bypass SvelteKit overflow), gradiente darkening su `body`. Glass surfaces opacity 0.65–0.82. `--color-text-3: oklch(0.72)` (era 0.55).

## Dashboard API Endpoints (CT203:8002)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/dashboard/summary` | GET | Hero episode + filmstrip |
| `/dashboard/day/{date}` | GET | Episodi + atom per data (YYYY-MM-DD, tz Rome) |
| `/dashboard/map?days=N` | GET | Punti GPS da MemoryAtom + RawCapture join |
| `/dashboard/sagas` | GET | Episodi paginati, filtro capture_class + tag — esclude episodi ghost (no FK-atom) via subquery (2026-06-08) |
| `/dashboard/people` | GET | Persone + stats identity level + episode count |
| `/dashboard/transcript/{atom_id}` | GET | Transcript MinIO con speaker_turns formattati |
| `/dashboard/recent` | GET | Atom recenti |
| `/dashboard/today` | GET | Alias per data odierna |
| `/dashboard/profile` | GET | UserProfileFact — lista fatti con confidenza, categoria, evidence |

**Transcript pipeline**: `raw_transcript_key` (MinIO path) su `MemoryAtom` → endpoint legge JSON con `speaker_turns: [{speaker, start_ms, end_ms, text}]` → frontend mappa `SPEAKER_00→Voce A`.

**API live su CT190:8002** (dev — da migrare su CT203 quando approvato):
- `GET /api/v1/devices/me/policy` ✅
- `POST /api/v1/uploads/segments` ✅
- `GET /api/v1/uploads/segments/{key}/status` ✅
- `GET /health` ✅

**Dataset test:** 20 segmenti V1 da PC139 (`D:\LifeLogData\`) in `raw-decrypted-temp/roberto/` su MinIO, `pipeline_status="queued"`. Ground truth V1 disponibile per confronto ASR.

## Architettura Liquid Brain (Swap-In/Out)

Per garantire privacy totale e portabilità, Lifelog2 separa il sistema (Guscio) dai dati (Cervello).

### 9.2 Global Registry (The Shell Layer) — ✅ live 2026-05-11

Situato stabilmente su **LXC 203**, il Global Registry (`registry.db` SQLite) è il database di sistema che non viene mai detaccato.
- **Funzione**: Auth (token opaque hex + bcrypt), provisioning `encryption_salt` (per-user, fisso), mapping device.
- **Endpoint live**: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- **Token**: opaque hex 64 char, SHA-256 in DB, scadenza +1 anno. Revoca immediata per cancellazione riga.
- **`encryption_salt`**: ritornato a ogni login — l'app lo usa per PBKDF2 → chiave AES-GCM locale.
- **Path**: `/opt/Lifelog2/registry.db` (override via `LIFELOG2_REGISTRY_DB` env var)

### 9.3 Ingest Parallelo vs Analisi Seriale (Il Proiettore)
- **Ingest (Always On)**: Ricezione audio cifrato da tutti i device autorizzati -> Staging su MinIO.
- **Analisi (On Demand)**: Solo un utente alla volta può caricare il proprio archivio (Swap-In) per l'analisi profonda dei ricordi.

## 10. Modello di Onboarding (Liquid Flow)
1. Inserimento URL ngrok nell'app.
2. Login/Register contro il Global Registry.
3. Ricezione automatica di `device_token` e `encryption_salt`.
4. Inizio cattura e invio.

## 11. Relazione con ARIA (PC 139)
Lifelog2 utilizza ARIA come motore di inferenza primario per:
- **ASR**: Trascrizione con diarizzazione.
- **Voiceprint**: Embedding 256d per l'identità biografica.
- **LLM**: Sintesi narrativa degli episodi.

## Identity Resolution System

Principio fondante: **una persona sbagliata è peggio di una persona sconosciuta.**

Lo stack di certezza si applica a ogni `Person` riconosciuta dal sistema:

| Livello | Nome | Trigger | Comportamento |
|---------|------|---------|---------------|
| 0 | Unknown | Voce nuova, nessun match | `Person(unknown-UUID)`, display `Sconosciuto A3F2` |
| 1 | Candidato LLM | LLM estrae nome da trascrizione | Solo `identity_candidates` JSONB — mai `first_name` |
| 2 | Confermato utente | Azione esplicita UI | `confirmed_by="user"` + back-propagation SpeakerTurn |
| 3 | Enrolled | Registrazione voiceprint intenzionale | Certezza assoluta, back-propagation immediata |

### Gestione Media & Podcast
Per evitare che conduttori TV, host di podcast o personaggi ricorrenti dei media vengano inseriti nel clustering delle persone reali a livello Z7, il modello Postgres prevede:
- `persons.is_media_persona` (Boolean): Flagga se la persona è una voce media.
- `persons.media_source_hint` (Text): Nota descrittiva della sorgente media (es. "Podcast XYZ host").
- `speaker_turns.turn_type` (String): Mappa la tipologia di turno (`speech`, `media`, `unknown`). I turni classificati come `media` vengono ignorati dal Worker Detective per l'inferenza d'identità.


**Regola assoluta**: nessun processo automatico (LLM, euristica, cosine similarity) può transitare da Livello 1 a Livello 2.

### Migration 0005 — ✅ Applicata 2026-05-16

```sql
ALTER TABLE persons ADD COLUMN identity_level       SMALLINT DEFAULT 0;
ALTER TABLE persons ADD COLUMN confirmed_at         TIMESTAMP WITH TIME ZONE;
ALTER TABLE persons ADD COLUMN confirmed_by         VARCHAR(64);
ALTER TABLE persons ADD COLUMN disambiguation_tag   VARCHAR(64);
ALTER TABLE persons ADD COLUMN identity_candidates  JSONB;
CREATE INDEX ix_persons_identity_level ON persons(identity_level);
-- Backfill: self + voiceprint → enrolled
UPDATE persons SET identity_level=3, confirmed_by='enrollment', confirmed_at=NOW()
WHERE relationship_type='self' AND voiceprint_embedding IS NOT NULL;
```

Roberto Guareschi: `identity_level=3` (enrolled). Voiceprint: weighted centroid da 3 campioni audio (.m4a in `D:\LifeLogData\user_data\`), 149 speaker_turns con cosine ≥ 0.75 assegnati (`person_id` + `capture_class` su 1222 segmenti: 1187 ambient, 22 mixed, 13 personal). ✅ Live 2026-05-24.

### Back-Propagation

Attivata SOLO su `identity_level >= 2`. Aggiorna:
- `SpeakerTurn.person_id` (tutti i turn con cosine ≥ 0.80 verso il voiceprint confermato)
- `MemoryAtom.entities_json` (sostituisce "Sconosciuto A3F2" con il nome)
- **MAI** `MemoryAtom.summary` o `title` (audit trail — le analisi restano fedeli al momento)

### Omonimi

Due "Marco" nel DB sono sempre distinti da `person_id` diversi e voiceprint diversi.
Il campo `disambiguation_tag` ("collega", "amico") è solo presentazionale.

**Design completo**: [[sources/lifelog2-identity-resolution|lifelog2-identity-resolution-design.md]]

---

## Place Semantics & Place Detective

Il worker periodico `worker_place_detective.py` (eseguito la domenica notte su LXC 203) analizza le abitudini dell'utente e deduce le tipologie di luoghi frequentati.
- **Inference Senza LLM**: Utilizza un sistema di scoring basato su euristiche e dati statistici (fasce orarie di presenza, giorni feriali vs festivi, durata della visita, tag semantici dei topic, e tipologia di persone presenti).
- **Classificazioni**: Mappa i luoghi in `home`, `work`, `social`, o `transit`.
- **Revisione Utente**: Le predizioni vengono salvate come `place_hypotheses` (stato `pending`). L'utente può confermare o modificare le ipotesi tramite l'interfaccia web `/places`.

---

## Rilevanza Dinamica dei Thread

Il contenuto di un thread è **immutabile** (le trascrizioni non cambiano), ma la sua **accessibilità** cambia nel tempo man mano che il sistema apprende nuove identità tramite VP enrollment.

### data_pool e visibilità worker

| data_pool | Contenuto | Worker Z4+ visibili |
|-----------|-----------|---------------------|
| `trusted` | Thread con Roberto confermato | Tutti (Day Digest, Profile Builder, Sagas, ecc.) |
| `flagged` | Media/ambient senza Roberto | Solo identity_detective, place_detective |
| `flagged_reclassifiable` | Flagged ma con VP ora confermati | identity_detective + reclassification_worker (P3c) |

### Categorizzazione retention

- **Trusted (personal_*)**: incluso in Day Digest, sagas, profile
- **Flagged reclassificabile**: riprocessabile con nuovi VP; può diventare `trusted` dopo conferma detective
- **Flagged permanente**: solo contesto contestuale (dove ero, cosa stava succedendo intorno), mai in digest personale

### P3 — VP Back-Propagation ai Thread

```
P3a (esistente): segment reclassification → speaker_turns.turn_type aggiornato
P3b (pianificato): VP confirm → thread_type + data_pool aggiornati su thread esistenti
P3c (pianificato): reclassification_worker batch → ripesca flagged_reclassifiable
```

**Vincolo Day Digest**: i digest già prodotti (Z4) sono storici stabili e NON vengono rielaborati. Solo i thread futuri o non ancora digeriti beneficiano del reclassification pass.

**Limitazione risolta (2026-07-04)**: `thread_type` viene ora ricalcolato ad ogni chiusura tramite `_correct_thread_type_at_closure()` (non solo alla creazione) — corregge sia l'asse personal↔ambient sia mono↔dialogue leggendo il roster reale del thread. Vedi `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md` §3.4.

**Schema completo**: [[concepts/lifelog2-thread-consolidation]] | [[sources/memory-model]]

---

## Guardia di volume/overflow LLM (2026-09-02)

`core/llm.py` — condiviso da TUTTI i worker LLM (Stage D, Stage E, Identity
Detective, Profile Validator, Day Digest, Z6) — stima il volume reale del prompt
prima di ogni chiamata (riduce `max_tokens` o rifiuta la chiamata se il contesto
non basta) e ritenta con budget raddoppiato se la risposta arriva vicina al tetto
richiesto (usage reali quando disponibili, non solo stima char/token). `thinking`
esposto come parametro vero per Qwen3 locale (prima sempre disattivato). Stage D
aveva un budget di input turni congelato da v28 a v33 mai ricalcolato — stesso
bug già visto in Stage E il 2026-08-30, qui corretto con
`_dynamic_turn_budgets_v28`. Z6 (sintesi per-saga) non aveva alcun tetto sul
volume di episodi accumulati in un run — ora bounded, gli episodi in eccesso
vengono rivalutati al run successivo invece di essere persi. Dettagli:
`docs/lifelog2-session-digest-2026-09-02-device-channel.md` §1-4.

## Canale telemetria device (heartbeat + rubrica + chiamate)

> **Contratto di input completo (permessi, schemi JSON, cadenze, stato
> registrazione chiamate)**: `sviluppi/Lifelog2/docs/lifelog2-android-app-blueprint-v2.3.md`
> — base di partenza per l'app Android, aggiornata 2026-09-02.

Nuovo canale disaccoppiato dall'upload dei segmenti (che riflette lo stato solo a
fine ciclo di 5 minuti): `POST /api/v1/devices/me/heartbeat` — batteria, rete,
GPS, mic attivo+RMS live, servizio attivo/in pausa — persistito nel Global
Registry SQLite (stessa fonte di identità/auth degli upload, nessun bisogno di
Redis per uno stato che è per natura "ultimo valore noto"). `GET
/api/dashboard/device-status` per la dashboard, "online" derivato da
`last_seen_at` vs soglia lato server.

**Cadenza**: 30s iniziali portati a 5 minuti per batteria/carico server.
~~Incidente reale: bruciava la quota free-tier di ngrok in circa una
settimana~~ — **ridimensionato lo stesso giorno**: il contatore reale
dell'agent ngrok (non i log nginx, ambigui tra ngrok e il `cloudflared` che
gira sullo stesso host) mostra ~740 richieste/mese osservate contro un limite
di 20.000 — nessun rischio reale di esaurimento verificato. Dettagli e causa
dell'errore di lettura: [[ct202-gateway]].

Nuove tabelle Postgres `synced_contacts`/`synced_calls` (migrazione 0056) —
sync giornaliera di rubrica e ultime 500 chiamate dal device, upsert su chiavi
naturali (numero di telefono; numero+timestamp per le chiamate) in assenza di
un ID stabile dal device. Terzo asse di segnale per l'identità/relazioni,
accanto a voiceprint (Z7) e co-presenza nei luoghi (place_relations). Non ancora
correlato ai `persons`/voiceprint esistenti — passo successivo non ancora
pianificato.

**Frontend**: stato device visibile come chip cliccabile negli header di `/` e
`/pipeline` (non nella sidebar, che è collassata/nascosta su `/pipeline`) — espande
un menu con rubrica scrollabile + ultime 10 chiamate. Dettagli:
`docs/lifelog2-session-digest-2026-09-02-device-channel.md` §8-10.

## Thinking Qwen3 + reprocess generale + audit (2026-09-08 → 09-11)

Redesign del wrapper ARIA↔llama-server per `qwen3-14b-q4km` (fatto su [[stack-aria]],
handoff `qwen3-14b-backend-spec-2026-09-09.md`): contesto 16384→32768, KV cache q8_0,
profili thinking/non_thinking coerenti, `reasoning_budget_tokens` come cap vero. Lato
Lifelog2: `thinking=True` cablato su tutti i worker Qwen3 (Stage D, Stage E,
identity_detective, thread_consolidation, day_digest, profile_validator) con budget
condiviso (`core/llm.py::estimate_char_budget`/`estimate_response_max_tokens` — prompt +
tabella + riserva reasoning + risposta, non più un `max_tokens` fisso).

**Stage D** tornato al prompt v34b (pre-minimizzazione) + reasoning generoso: 6/7 puliti
sui 7 casi storici noti (contro 3/7 prima). **Reprocess generale da Stage C1** (11659
speaker_turns, 671 conversation_threads, 371 arricchiti) — 4 bug trovati e risolti in
corsa durante il reprocess stesso (nessuna scrittura dati sbagliata: tutti fallivano "in
sicurezza"). **Audit sistematico** dei 17 casi storici noti: i due problemi più vecchi
(coda tabella persa in Stage D, attribuzione scambiata in Stage E) confermati **risolti**
sui dati reali. Trovato e corretto un bug indipendente (`media_type` sempre NULL su ogni
thread dal 2026-08-21, cancello di volume rotto).

**Scoperto**: la formazione del ricordo (A→G — ingest→identità→arricchimento→embedding→
cover) è la parte matura del progetto, con solo 4 problemi aperti. I worker secondari
(identity/place detective, day/week/month/year digest, profile builder/Z7, Saghe) sono
ineguali — alcuni dormienti da settimane, `month_digest`/`year_digest` non esistono
affatto. Dettaglio completo, incluso il conteggio onesto di quanto manca alla visione
del blueprint: `docs/lifelog2-status-roadmap.md` (STATO 2026-09-11) e
`docs/lifelog2-post-audit-todo-2026-09-11.md`.

**Riordino documentazione** nella stessa sessione: `docs/README.md` (indice curato, fermo
10 giorni) aggiornato con 32 documenti mai indicizzati; un documento marcato superato ma
mai spostato archiviato per davvero (`docs/archive/`); le 4 knowledge/*.md di progetto
(ferme 5-7 settimane) rinfrescate con banner + correzioni mirate; nuovo
`docs/lifelog2-session-log.md` (una voce per sessione di sviluppo, sostituisce
`knowledge/development-log.md` per le voci future).

## Link Correlati

- [[stack-nh-mini]]
- [[stack-aria]]
- [[ct105-postgres]]
- [[ct120-redis]]
- [[ct202-gateway|CT202 Gateway — vincolo quota ngrok]]
- [[concepts/lifelog2-quality-gate|Quality Gate & Tiers]]
- [[concepts/lifelog2-thread-consolidation|Thread Consolidation Z6]]
- [[concepts/lifelog2-refactor-roadmap|Thread Builder v2 — roadmap e hardening]]
- [[sources/lifelog2-project-context|lifelog2-project-context]]
- [[sources/lifelog2-identity-resolution|lifelog2-identity-resolution]]
- [[sources/lifelog2-thinking-reprocess-audit-2026-09-11|lifelog2-thinking-reprocess-audit-2026-09-11]]

