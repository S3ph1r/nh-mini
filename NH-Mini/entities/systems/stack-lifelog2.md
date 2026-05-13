---
title: "Stack — Lifelog2"
type: entity
tags: [stack, lifelog, memory, pipeline, embedding, identity]
sources: [lifelog2-project-context.md, lifelog2-identity-resolution.md]
updated: 2026-05-13
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
  → CT203 Lifelog Runtime (FastAPI — pending approval)
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

- **Aesthetic**: "Obsidian Depth" — Nero grafite profondo (`oklch(0.06 0.01 250)`), vignette radiali e grana cinematografica (noise).
- **Core Concept**: Il ricordo come "Poster" (vertical aspect ratio). Ogni card è una copertina di un film/libro.
- **Interazioni**: Overlay Sidebar (hover-activated, z-9999), Right Rail Filmstrip (lista compatta dei recenti).
- **Typography**: Titoli in Inter (Sans), metadati tecnici in JetBrains Mono.

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
→ C (ASR + Diarize + Voiceprint 256d — PC 139 qwen3-asr-1.7b)
→ D (MemoryAtom LLM — PC 139 qwen3-14b-q4km)  ← Stage D v1 completo
→ E (Text Embedding 1024d — LXC 107 mxbai)
→ F (Grouping/Episodes — LXC 203)
→ G (Retention/Oblivion)
```

### Stage D — Enrichment Architecture

Stage D produce un **MemoryAtom** per segmento. Gli speaker restano anonimi (`SPEAKER_XX`) fino a Stage E.

- **Input**: transcript + speaker_turns (da Stage C via MinIO)
- **Task ARIA**: queue `aria:q:llm:local:qwen3-14b-q4km:lifelog`
- **Output MemoryAtom**: summary, event_type, topics, entities, speaker_turns_annotated (role_inferred), temporal_refs, confidence
- **Prompt versioning**: `prompts/config.json` → `prompts/stage_d_enrich_v{n}.txt` (nessun prompt hardcoded)
- **Timing warm**: ~55s totali (LLM load + inferenza), ~21s se già carico
- **Timing cold**: ~155-200s (ASR già scarico → LLM load + inferenza)

### Identity Resolution (3 livelli)

| Livello | Nome | Modalità | GPU |
|---------|------|----------|-----|
| RT (Stage D) | Speaker anonimi | MemoryAtom con SPEAKER_XX | LLM warm |
| Worker Detective | Inferenza identità da discourse | LLM solo (no ASR) — max 8 segmenti/call, ogni ora | LLM cold |
| Retroactive Indexer | Cosine similarity voiceprint 256d | CPU pura, scipy — < 5s su 1000+ segmenti | No GPU |

### Logica di Raggruppamento (Grouping)
- **Continuità**: Gap < 10 min + stesso GPS.
- **Isolamento Genere**: Il passaggio tra "Personal" e "Knowledge" (es. fine conversazione -> inizio podcast) forza la creazione di un nuovo gruppo/episodio, anche se temporalmente contiguo.

## Retention Classes

`ephemeral` → `generic` → `useful` → `important` → `sacred` + `sensitive` (vault separato)

## Stato Sviluppo

| Milestone | Stato | Note |
|-----------|-------|------|
| M0 — Foundation/Product Spec | ✅ Done | Blueprint, memory model, API contracts frozen (2026-05-07) |
| M1 — Infrastructure + API Ingest | ✅ Done | CT105 DB live, MinIO bucket live, FastAPI su CT190:8002, 4 endpoint Android testati, 20 segmenti V1 in pipeline |
| M2 — Pipeline Stage B (Preprocess) | ✅ Done | Consumer Redis `lifelog:stream:ingest`, ffmpeg WAV 16kHz, quality gate, MinIO `normalized-audio/`, emit `lifelog:stream:asr` (2026-05-07) |
| M3 — Pipeline Stage C (ASR) | ✅ Done | Refactored 2026-05-12: `capture_class` (personal/mixed/ambient/unknown), user-first voiceprint matching, drain loop fix, legacy user_id compat. |
| M4 — Stage D (LLM Enrichment) | ✅ Done 2026-05-13 | Blueprint v1 cristallizzato. Worker Stage D implementato con prompt esternalizzati (config.json + versioning). AriaLLMClient aggiornato (qwen3-14b-q4km, messages format). E2E test superato: 21s, MemoryAtom qualità alta. |
| M5 — Episode/Day Grouping | Pending | Aggregazione temporale, Day digest, Thread/Saga |
| M6 — Scoring/Retention v1 | Pending | Quality/attention scoring, retention class, oblio automatico |
| M7 — Frontend SvelteKit | 🔧 In test | **Cinematic UI Refactor completo**. Dashboard accessibile su CT203:5173. Navigazione overlay ok. |

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

### Migration 0004 (pianificata, post-Stage D)

```sql
ALTER TABLE persons ADD COLUMN identity_level       SMALLINT DEFAULT 0;
ALTER TABLE persons ADD COLUMN confirmed_at         TIMESTAMP WITH TIME ZONE;
ALTER TABLE persons ADD COLUMN confirmed_by         VARCHAR(64);
ALTER TABLE persons ADD COLUMN disambiguation_tag   VARCHAR(64);
ALTER TABLE persons ADD COLUMN identity_candidates  JSONB;
```

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
