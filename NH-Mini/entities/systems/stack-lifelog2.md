---
title: "Stack — Lifelog2"
type: entity
tags: [stack, lifelog, memory, pipeline, embedding, identity]
sources: [lifelog2-project-context.md, lifelog2-identity-resolution.md]
updated: 2026-05-16
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
| Z3 | Episode | Episode | Ore |
| Z4 | Day Digest | Day | Giorno |
| Z5 | Week/Month Review | (materialized views) | Settimana/mese |
| Z6 | Saga / Long Arc | Thread + topic_embedding(1024) | Mesi–anni |
| Z7 | Life Map | UserProfileFact | Anni–decenni |

## Embedding Architecture

- **MemoryAtom.embedding**: `vector(1024)` — mxbai-embed-large via CT107 Ollama
- **Thread.topic_embedding**: `vector(1024)` — mxbai-embed-large via CT107 Ollama
- **Person.voiceprint_embedding**: `vector(256)` — Qwen3-ASR embedding via ARIA PC139 (voiceprint_quality=1.0 su 6 campioni per Roberto)

CT107 promosso da legacy a infra reale: LXC always-on, CPU, Ollama con mxbai-embed-large già installato.

## Architettura Liquid Brain (Isolamento Totale)

V2 implementa il paradigma **Swap-In / Swap-Out**:
- **Staging Area**: Bucket locale cifrato per ricezione 24/7 (Cervello scollegato).
- **Swap-In**: Caricamento DB Postgres da PC 139 a LXC 105 all'accesso utente.
- **Active**: Elaborazione e scrittura dei media direttamente sul mount esterno (PC 139).
- **Swap-Out & Purge**: Esportazione DB aggiornato su PC 139 e **cancellazione fisica** dei dati da LXC 105/104 alla chiusura sessione.

Questo garantisce che il server NH-Mini sia un "guscio vuoto" senza dati personali quando l'utente non è attivo.

## Pipeline (A–G)

```
A (Ingest Android M4A) 
→ B (Preprocess WAV 16kHz — LXC 203)
→ C (ASR + Diarize + Voiceprint 256d — PC 139 WhisperX large-v3 [primary] / Qwen3-ASR-1.7b [standby])
→ D (MemoryAtom LLM — PC 139 qwen3-14b-q4km, prompt v5)
→ E (Text Embedding 1024d — LXC 107 mxbai)
→ F (Grouping/Episodes + visual_prompt LLM — LXC 203)
→ G (Episode Cover Generation — PC 139 FLUX.2-klein-4B)
→ H (Retention/Oblivion — futuro)
```

### Stage D — Enrichment Architecture

Stage D produce un **MemoryAtom** per segmento. Gli speaker restano anonimi (`SPEAKER_XX`) fino a Stage E.

- **Input**: transcript + speaker_turns (da Stage C via MinIO)
- **Task ARIA**: queue `aria:q:llm:local:qwen3-14b-q4km:lifelog`
- **Output MemoryAtom**: summary, event_type, topics, entities, speaker_turns_annotated, temporal_refs, confidence, `action_items` (v5+), `decisions` (v5+)
- **Prompt versioning**: `prompts/config.json` → `prompts/stage_d_enrich_v{n}.txt` (nessun prompt hardcoded)
- **Prompt v5** (2026-05-15): aggiunge `action_items` e `decisions` (array). Regole: solo task concreti, no vaghi intenti, no contenuto media passivo se non commentato dall'utente, max 5 ciascuno, lingua matched.
- **Noise filter**: `_NOISE_PHRASES` frozenset — filtra risposte LLM tipo "nessuna decisione esplicita" che entrano come stringhe nell'array.
- **`_parse_str_list()`**: helper condiviso per topics, action_items, decisions — normalizza str e list, applica noise filter.
- **Timing warm**: ~55s totali (LLM load + inferenza), ~21s se già carico
- **Timing cold**: ~155-200s (ASR già scarico → LLM load + inferenza)

### Identity Resolution (3 livelli)

| Livello | Nome | Modalità | GPU |
|---------|------|----------|-----|
| RT (Stage D) | Speaker anonimi | MemoryAtom con SPEAKER_XX | LLM warm |
| Worker Detective | Inferenza identità da discourse | LLM solo (no ASR) — max 8 segmenti/call, ogni ora | LLM cold |
| Retroactive Indexer | Cosine similarity voiceprint 256d | CPU pura, scipy — < 5s su 1000+ segmenti | No GPU |

### Stage F — Episode Grouping (4-Pass Sliding Window)

La continuità temporale da sola non è sufficiente a definire un episodio. Stage F usa un'architettura a 4 pass con LLM semantico.

**Pass 1 — Temporal Pre-filter (no LLM)**
- Gap > `AUTO_BREAK_MINUTES` (60 min) tra capture consecutive → rottura automatica, nessuna chiamata LLM
- Produce `candidate_groups`: liste di atom temporalmente adiacenti

**Pass 2 — Sliding Window LLM Boundary Detection**
- Ogni atom viene valutato rispetto all'episodio corrente via LLM (qwen3-14b)
- Input: `running_episode_summary` (max 180 token, compresso) + metadata del nuovo atom (~200-300 token)
- Output: `continue | break_before | break_within` + `updated_episode_summary`
- Segnali di rottura (priorità decrescente): cambio `event_type` (forte), GPS > 1km (forte), set persone disjoint (forte), gap > 30min (medio), cambio topic (medio), cambio `capture_class` (debole — inaffidabile su telefonate)
- Continuità forte garantita: `monologue + personal + gap < 15min` → sempre `continue`
- Prompt: `stage_f_boundary_v1.txt` (versioned)

**Pass 3 — Precise Split (solo se `break_within`)**
- Attivato solo quando la transizione avviene *dentro* un atom
- Legge il trascritto completo da MinIO, trova il turn index esatto
- Output: `AtomRef(from_turn, to_turn)` per sub-atom references
- Prompt: `stage_f_split_v1.txt` (versioned)

**Pass 4 — Episode Synthesis**
- Atom singolo: riusa `title`/`summary` esistente
- Multi-atom: LLM genera `title` (max 8 parole) + `narrative_summary` (3-5 frasi) + **`visual_prompt`** (v2+)
- `visual_prompt`: 20-40 parole inglese, stile flat minimalista senza volti/testo — usato da Stage G
- Prompt: `stage_f_episode_v2.txt` (corrente) — v1 senza visual_prompt (legacy)

**AtomRef dataclass**: `memory_id, row, from_turn, to_turn, is_partial` — permette referenze sub-atom (dal minuto X al minuto Y dell'atom N).

**Cutoff**: atom con `ended_at < NOW() - 10min` — l'ultimo episodio rimane "aperto" per estensione al run successivo.

**Bug storico risolto (2026-05-15)**: `_temporal_prefilter` non aggiornava `current_end` all'apertura di un nuovo gruppo → tutti i gap venivano calcolati rispetto al primo atom → 17 gruppi invece di 8.

**Capture-class elevation**: `personal > mixed > ambient > unknown` — l'episodio prende la classe dominante tra i suoi atom.

### Stage G — Episode Cover Generation (FLUX.2-klein-4B)

Worker batch: trova episodi con `visual_prompt IS NOT NULL AND cover_image_key IS NULL`, genera PNG via ARIA e salva URL MinIO.

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
| M3 — Pipeline Stage C (ASR) | ✅ Done | Refactored 2026-05-12: `capture_class`, user-first voiceprint, drain loop fix. **2026-05-14: WhisperX large-v3 (porta 8091) come backend primario** — sostituisce Qwen3-ASR-1.7B (standby). Timing Stage C: ~24s warm (vs ~55s). Pipeline A→E: 91s totali su 299s audio (3.3× realtime). |
| M4 — Stage D (LLM Enrichment) | ✅ Done 2026-05-13 | **Prompt v5** (2026-05-15): aggiunge `action_items` + `decisions` con noise filter `_NOISE_PHRASES`. v4 (2026-05-15): regola critica monologue vs podcast/broadcast. 2 atom misclassificati (`0a4bf747`, `be8217d1`) — da rielaborare con v5. Rerun su 19 atom completato: 7/19 hanno action_items/decisions non vuoti. |
| M4.5 — Stage E (Embedding + WAV cleanup) | ✅ Done 2026-05-13 | mxbai-embed-large 1024d via CT107, `memory_atoms.embedding` aggiornato, WAV MinIO eliminato, pipeline_status="consolidated". Fast Pipeline A→E operativa. |
| M5 — Episode/Day Grouping | ✅ Done | Stage F **live** 2026-05-15 — 4-pass sliding window, 8 gruppi → 12 episodi su 19 atom, bug prefilter fixato. **Orchestratore integrato** — Stage F ogni 30min, trigger `run_grouping`. **Worker Detective** live 2026-05-16 — identity inference LLM ogni 15min, Redis checkpoint. **Stage G live 2026-05-16** — cover generation FLUX.2-klein-4B, ogni 60min, trigger `run_covers`. |
| M6 — Scoring/Retention v1 | Pending | Quality/attention scoring, retention class, oblio automatico |
| M7 — Frontend SvelteKit | 🔧 In progress | **Cinematic UI** live su CT203:5173. **Control Plane v2** (2026-05-15): telemetria, pipeline dashboard. **Views B2–B7** (2026-05-16): Day, Map, People, Sagas, Timeline, Transcript. Sfondo bg.jpg + palette glassmorphism. |

## Frontend Views (CT203:5173)

| View | Route | Descrizione |
|------|-------|-------------|
| Dashboard | `/` | Hero episode, filmstrip rail, bande episodi multi-giorno |
| Day | `/day/[date]` | Episodi + atom del giorno, nav prev/next, link transcript |
| Map | `/map` | Leaflet CircleMarker GPS, filtro periodo, detail panel |
| People | `/people` | Directory persone, identity badge, voiceprint dot, filtro livello |
| Sagas | `/sagas` | Library episodi filtrabili per classe + tag, load-more |
| Timeline | `/timeline` | Linea verticale mese/giorno, spine SVG, dot colorati per classe |
| Transcript | `/transcript/[id]` | Speaker turns colorati, full text, sidebar metadata |
| Pipeline | `/pipeline` | Control Plane v2 — Workers, Streams, DB, Telemetria, Logs |

**Design system**: sfondo `bg.jpg` su elemento `html` (fixed, bypass SvelteKit overflow), gradiente darkening su `body`. Glass surfaces opacity 0.65–0.82. `--color-text-3: oklch(0.72)` (era 0.55).

## Dashboard API Endpoints (CT203:8002)

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/dashboard/summary` | GET | Hero episode + filmstrip |
| `/dashboard/day/{date}` | GET | Episodi + atom per data (YYYY-MM-DD, tz Rome) |
| `/dashboard/map?days=N` | GET | Punti GPS da MemoryAtom + RawCapture join |
| `/dashboard/sagas` | GET | Episodi paginati, filtro capture_class + tag |
| `/dashboard/people` | GET | Persone + stats identity level + episode count |
| `/dashboard/transcript/{atom_id}` | GET | Transcript MinIO con speaker_turns formattati |
| `/dashboard/recent` | GET | Atom recenti |
| `/dashboard/today` | GET | Alias per data odierna |

**Transcript pipeline**: `raw_transcript_key` (MinIO path) su `MemoryAtom` → endpoint legge JSON con `speaker_turns: [{speaker, start_ms, end_ms, text}]` → frontend mappa `SPEAKER_00→Voce A`.

**API live su CT190:8002** (dev — da migrare su CT203 quando approvato):
- `POST /api/v1/devices/register` ✅
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

Roberto Guareschi: `identity_level=3` (enrolled), `voiceprint_quality=0.6`.

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

## Link Correlati

- [[stack-nh-mini]]
- [[stack-aria]]
- [[ct105-postgres]]
- [[ct120-redis]]
- [[sources/lifelog2-project-context|lifelog2-project-context]]
- [[sources/lifelog2-identity-resolution|lifelog2-identity-resolution]]
