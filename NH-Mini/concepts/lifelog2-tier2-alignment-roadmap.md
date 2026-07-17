---
title: "Lifelog2 — Tier2 Alignment Roadmap: worker di secondo livello da atom a thread"
type: concept
tags: [lifelog2, roadmap, tier2, detective, day-digest, profile-builder, places, saghe, thread-model]
sources: [lifelog2-data-architecture-v1.md, lifelog2-intelligence-addendum-v1.md, lifelog2-places-intelligence-spec-v1.md]
updated: 2026-07-16
---

# Lifelog2 — Tier2 Alignment Roadmap (atom → thread)

Analisi 2026-07-13, con Tier1 (A→G) thread-native funzionante e in drain su ~1200 segmenti reali. Costruita su [[concepts/lifelog2-refactor-roadmap]] (FASE 5, mai completata) e sulla sezione "worker Tier2 affamati" di `sviluppi/Lifelog2/docs/lifelog2-data-architecture-v1.md`.

## Il problema

`memory_atoms` è **vuota dal 2026-06-29** (l'unico writer, il vecchio `stage_d_enrichment.py`, è archiviato). Tutti i worker di secondo livello la interrogano ancora come sorgente primaria: **girano, trovano 0 righe, escono "ok"** — no-op silenziosi da due settimane. Due di loro sono anche rotti a livello di schema (tabelle droppate/rinominate dalla migration 0022).

## Il nuovo contratto dati (cosa produce Tier1 fino a Stage G)

| Fonte | Campi utili per Tier2 |
|---|---|
| `conversation_threads` | title, summary, topics, `entities_json` {persons_mentioned, locations, organizations, projects, dates_mentioned}, `open_loops` [{text, type: action_item\|decision\|∅, resolved}] (**gated su self_present/vp_R**), sentiment, `coherence_score` (=importance cappata), thread_type (5 valori), `voiceprint_roster`, turn_count, started/ended_at, `data_pool`, embedding 1024d, cover, continues_from, `location_id` (**mai popolato — gap**) |
| `thread_turns` → `speaker_turns` | vp_stable_id, person_id, turn_reliability, testo, offsets, sequence_pos |
| `raw_captures` | GPS lat/lon (dal 2026-07-05 anche nel filename), timestamps |
| `days`, `persons`, `places`, `user_profile_facts` | tabelle output invariate |

## Roadmap per worker (ordine di esecuzione proposto)

### 1. Identity Detective — effort BASSO, priorità ALTA
**Oggi**: batch di `memory_atoms` con `pipeline_status='consolidated'` (status che **nessuno stage v2 imposta più** — doppio motivo di no-op) e `capture_class` personal/mixed → turni → LLM propone identity_candidates su `persons`.
**Fix**: sorgente = `conversation_threads` enriched con `thread_type IN ('personal_dialogue','personal_mono')` (media_passive escluso da addendum §2; ambient_dialogue con vp_R nel roster: **da decidere**), checkpoint su `updated_at`; turni via `thread_turns`. La logica candidati/persons resta invariata. Il roster con `canonical_label` è materia prima nuova e migliore (stable vp cross-atom).

### 2. Day Digest (Z4) — effort MEDIO, priorità ALTA
**Oggi**: legge `episodes` (**tabella droppata**) + `memory_atoms` (filtro `data_pool` della FASE 1 c'è ma filtra il nulla).
**Fix**: input = thread del giorno con `data_pool='trusted'`, tipi personal_* (+ soglia importance); campi title/summary/topics/open_loops; persone dal roster + `entities_json.persons_mentioned`; la query "persone del giorno" via speaker_turns è già thread-compatibile. Prompt v5→v6: rimuovere le difese anti-media (task SL-2 della FASE 5 — ora garantite a monte dai tier). Output su `days` invariato.

### 3. Profile Builder (Strato 1+2) — effort MEDIO
**Oggi**: Strato 1 estrae fatti da `decisions_json`/`action_items_json`/summary degli atom (signal A/B/C, addendum §8.4); Strato 2 pattern SQL su atom (topics 30gg, media 7gg) + social circle su speaker_turns.
**Fix**: Strato 1 → `open_loops` tipizzati del thread (il gate self_present è **già garantito da Stage E**, prima andava verificato) + summary thread; Strato 2 topics → `conversation_threads.topics`; media habits → statistiche su `thread_type='media_passive'` (segnale più pulito del vecchio conversation_type); social circle probabilmente **già funzionante** (è turn/person-based). `entities_json` (organizations, projects) = nuova materia prima per le categorie di fatto dell'addendum §5.2.

### 4. Geo-attach + Place Detective — effort MEDIO+, con prerequisito
**Gap a monte**: `conversation_threads.location_id` non è popolato da nessuno — il vecchio `find_or_create_place` viveva nello Stage F archiviato. I GPS ci sono (raw_captures).
**Fix in due parti**: (a) nuovo step geo-attach alla chiusura/enrichment del thread: da lat/lon delle capture dei suoi turni → `find_or_create_place` → `location_id`; (b) Place Detective: histogram ora/giorno da thread invece che da atom, persone-per-luogo via roster, distribuzione `thread_type` al posto di `capture_class`. Riferimento: `lifelog2-places-intelligence-spec-v1.md` §3.3 (la spec resta valida, cambia solo l'unità).

### 5. Saga Builder (Z6, ex Thread Consolidation) — effort ALTO, riscrittura
**Oggi**: rotto tre volte — `FROM threads` (rinominata `sagas` nella 0022), `FROM episodes` (droppata), `memory_atoms.episode_id` (colonna droppata).
**Fix**: riscrittura come consumer di thread finalizzati/enriched trusted personal: similarity via embedding 1024d (già su thread!) + LLM per timeline/turning_points. Schema `sagas`: `linked_episode_ids` → `linked_thread_ids`. **Decisione da prendere**: evolvere la tabella esistente (con le saghe legacy dentro) o ripartire pulita. Anche la pagina dashboard `/sagas` e gli endpoint `/dashboard/threads*` (che parlano con questo schema) vanno rivisti insieme.

### 6. Profile Validator — effort ZERO
Legge solo `user_profile_facts` → schema-independent, già funzionante. Torna utile appena il Profile Builder produce fatti nuovi.

### Cleanup finale (dopo 1-5)
- Rimuovere il ramo atom di `stage_g_covers.py` (no-op)
- Drop di `memory_atoms` + FK residue (`action_items.source_memory_id`, `thread_turns.memory_id`) quando nessun modulo la referenzia
- Aggiornare `lifelog2-data-architecture-v1.md` §4 con blocco datato di chiusura gap

## Punti aperti (decisioni per Roberto)

1. **Detective su ambient_dialogue**: includere thread ambient dove vp_R è nel roster? (più recall sulle identità, più rumore)
2. **Sagas**: evolvere tabella/dati esistenti o ripartire da zero?
3. **Retention per thread**: la retention_class atom-level (addendum §2) non ha equivalente thread — oggi l'unico gate è `data_pool`. Serve una retention differenziata per thread_type?

### Decisioni prese — 2026-07-13

1. **Detective**: analizza **qualsiasi classe di thread con vp_R nel roster** (non solo personal_*). Stessa regola per il Place Detective sui luoghi assegnati a thread con vp_R.
2. **Sagas** (delegata): si **evolve la tabella esistente** — nuova colonna `linked_thread_ids`; le righe legacy (solo `linked_episode_ids`) restano come storia e il nuovo builder le ignora. Nessuna migrazione distruttiva.
3. **Retention per thread**: replicare la logica atom-level — thread `personal_*` retention lunga, `ambient_*`/`media_passive` retention corta. Da progettare: colonna `retention_class` su `conversation_threads` + policy nel cleanup worker.

**Hardening aggiuntivo approvato** (post-drain coda corrente): (4) ciclo Tier1 a chunk per i catchup grossi — N segmenti C→C1→D→E→G per ciclo invece del drain ASR completo prima di C1, così i thread appaiono progressivamente in dashboard.

## Stato implementazione — 2026-07-13 (notte)

Tutti i worker della roadmap migrati e deployati su LXC 203 (commit `3be9254` → `52dfa5b`, migrations 0029-0031):

| # | Worker | Commit | Note |
|---|---|---|---|
| 1 | Identity Detective | `3be9254` | marker `detective_analyzed_at` (0029), prompt v4 con vp_R dichiarato owner, 31 thread già eleggibili |
| 2 | Day Digest Z4 | `dc7008c` | prompt v5 thread-native, open_loops strutturati come grounding, shape output invariata |
| 3 | Profile Builder | `e84cfef` | Strato 1 da open_loops; Z7 Tier B clustera per vp_stable_id (fusione cross-sessione); Strato 2 su thread |
| 4 | Geo-attach + Place Detective | `a750340` | `_geo_attach()` in Stage E (media GPS capture → find_or_create_place → location_id); detective su luoghi di thread con vp_R |
| 5 | Saga Builder Z6 | `52dfa5b` | `sagas.linked_thread_ids` (0030), consuma thread personali trusted, due-passi Gemini+Qwen3 invariato |
| 6 | Retention thread | `52dfa5b` | `retention_class` su conversation_threads (0031), scritta da Stage E, logica atom portata fedelmente. **Solo dato — enforcement cleanup da concordare** |

Profile Validator: verificato schema-independent, nessuna modifica. I worker caricano il codice nuovo allo spawn (nessun restart orchestrator necessario); primo giro reale a fine drain ASR del batch 1200.

**Cleanup rimandato**: drop di `memory_atoms` + FK residue, ramo atom di `stage_g_covers`, rinomina eventuale del worker sagas, aggiornamento data-architecture-v1 §4. I prompt Z6 parlano ancora di "episodi" (semanticamente equivalente, versione futura per la terminologia).

## Chiusura roadmap — 2026-07-16

Il batch 1200 è stato **drenato end-to-end senza perdite** (attraverso zombie WhisperX 14/07, migrazione rete + riavvio Proxmox 15/07, tokenizer corrotto 15/07) e la pipeline è passata in esercizio realtime. Primo giro reale dei Tier2 completato: tutti e 9 i worker `ok` senza failure, 106 thread analizzati dal detective, 14 persone / 1510 turni linkati da Z7, 11 saghe, 110 fatti profilo. L'hardening emerso dal drain (backpressure lockstep B⇄C, retry cronologico via Redis PEL, soft deadline, GPU lease, date thread da recording time — incluso fix `started_at` `c64a34e` del 16/07 con 74 thread riparati) è documentato in `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md` §8.

**Gap residui** (fotografia completa in `docs/lifelog2-status-roadmap.md`, blocco 2026-07-16): GPS quasi mai allegato dall'app Android (5-6/~1900 capture) → Places a zero per fame di dati, non per bug; Day Digest copre solo "ieri" → catchup `--days N` da lanciare per gli 11 giorni storici; retention `enforcement` mancante (322 thread con class NULL); cleanup `memory_atoms`; ciclo Tier1 a chunk approvato e ora applicabile.

## Vedi anche

- [[concepts/lifelog2-refactor-roadmap]] — FASE 5 (origine di questi task, ora superata da questa pagina per il Tier2)
- [[entities/systems/stack-lifelog2]] — stack e pipeline
- `sviluppi/Lifelog2/docs/lifelog2-data-architecture-v1.md` — contratto dati completo tabella per tabella
- `sviluppi/Lifelog2/docs/lifelog2-intelligence-addendum-v1.md` — intento originale del layer intelligence
