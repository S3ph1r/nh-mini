---
title: "DIAS — Distributed Immersive Audiobook System"
type: entity
tags: [sistema, dias, audiobook, pipeline, tts, gemini, redis]
sources: [dias-project-context.md, dias-blueprint.md, dias-workflow-logic.md, dias-production-standard.md]
updated: 2026-04-26
---

# DIAS — Distributed Immersive Audiobook System

**"Regista Narrativo"** che orchestra una pipeline distribuita per trasformare testi letterari in audiobook teatrali di qualità cinematografica.

Benchmark qualitativo: **BBC Radio Drama anni '80** e **Star Wars Audio Drama (NPR, 1981)**.

## Identità

| Campo | Valore |
|-------|--------|
| Fase | production_testing |
| Stack | Python, Redis, Google Gemini, [[stack-aria\|ARIA]] (Qwen3TTS, Fish, ACE-Step), FFmpeg |
| Codebase | `sviluppi/dias/` |
| Blueprint | `sviluppi/dias/docs/blueprint.md` (v7.0, Aprile 2026) |
| Container Brain | [[ct120-dias-brain]] (Redis) + [[ct190-nh-mini]] (codice) |
| Container Runtime | [[ct201-dias-rt]] (Dashboard + API Hub) |

## Ruoli dei Nodi

| Nodo | Ruolo | Cosa fa |
|------|-------|---------|
| LXC 190 (NH-Mini) | **Brain** | Esegue gli stage, gestisce il ciclo di vita del libro |
| LXC 120 (Redis) | **Infrastructure** | Universal State Bus — code e registry |
| PC 139 (ARIA GPU) | **Worker** | Inferenza TTS + ACE-Step (audio) |
| LXC 201 | **Runtime** | Dashboard Svelte + API Hub |

## Pipeline: 10 Stadi Seriali

La pipeline è **strettamente sequenziale** (Serial Handshake): ogni stadio inizia solo quando il precedente ha persistito su disco.

| Stage | Nome | Compito |
|-------|------|---------|
| **0** | Intel | Estrazione struttura (0.1) + DNA creativo + Casting (0.2) → `fingerprint.json`, `preproduction.json` |
| **A** | TextIngester | Scomposizione: Macro-chunk (~2500 parole) + Micro-chunk (~300 parole) |
| **B** | SemanticAnalyzer | Analisi emotiva macro (valence/arousal/tension) + Mood Propagation |
| **C** | SceneDirector | Tag Splitting, istruzioni TTS Qwen3, segmentazione per Emotional Beat |
| **D** | VoiceGenerator | TTS per ogni scena → WAV fisici + MasterTimingGrid |
| **B2-Macro** | Musical Director | Produce MacroCue (PadRequest + PadArc) per ogni macro-chunk |
| **B2-Micro** | Sound Designer | Produce IntegratedCueSheet + SoundShoppingList per ogni micro-chunk |
| **B2-Micro-Director** | Narrative Event Extractor | Estrae eventi fisici → SoundEventScore (modalità split v1.0) |
| **B2-Micro-Engineer** | ACE-Step Spec Generator | SoundEventScore → IntegratedCueSheet (modalità split v1.0) |
| **D2** | Sound Factory Client | Invia SoundShoppingList ad ARIA → produce asset audio via ACE-Step |
| **E** | Mixdown | Assembla voce + PAD stems (HTDemucs) + AMB/SFX/STING → traccia finale |

Per la pipeline semplificata (solo voce): `A → C → D → F` (audiobook `.m4b` rapido).

## Il Master Clock: La Voce Detta il Tempo

Stage D genera i WAV fisici e misura le durate al millisecondo. Stage B2 lavora **dopo** Stage D: non stima le durate, le legge dalla `MasterTimingGrid`. Stage E piazza i suoni perfettamente a tempo.

## Stage B2: Sound-on-Demand v4.1

Zero dipendenze da catalogo o sound library pre-esistente. Ogni asset prodotto ex-novo da [[stack-aria|ARIA]] su richiesta.

Modello unico: **ACE-Step 1.5 XL SFT** per tutti gli asset (PAD, AMB, SFX, STING).

### Modalità B2-Micro

| Modalità | Chiamate LLM | Comando |
|----------|-------------|---------|
| Monolitica (default) | 1 per micro-chunk | `run_b2_pipeline.py <project_id>` |
| Split Director/Engineer | 2 per micro-chunk | `run_b2_pipeline.py <project_id> --split` |

La modalità split risolve strutturalmente il problema del `canonical_id mismatch` nel shopping list.

## Standard Qualità: Formula Oscar (Voce)

Target: qualità sovrapponibile a ElevenLabs con Qwen3-TTS 1.7b.

| Parametro | Valore |
|-----------|--------|
| `subtalker_temperature` | 0.75 (grana umana) |
| `temperature` | 0.7 (bilanciamento) |
| `voice_ref_text` | **mandatorio** (metronomo fonetico) |

## Sound Design (Paradigma BBC/Star Wars)

**Il silenzio è il default. Un suono deve guadagnarsi il diritto di esistere.**

| Tipo | Durata | Frequenza |
|------|--------|-----------|
| PAD (tappeto musicale) | ~8-20 min per capitolo | sempre, gestito da PadArc |
| AMB (cambio scena) | 3-5 s | max 1 per micro-chunk |
| SFX (effetto puntuale) | 0.3-2 s | max 1 per scena |
| STING (accento orchestrale) | 2-4 s | max 1 per micro-chunk, mai a inizio scena |

Vedi [[concepts/dias-sound-design]] per le regole quantitative complete.

## Idempotenza Blindata (Master Registry)

Ogni stadio controlla tre fonti prima di agire:
1. Filesystem: il file output esiste su disco?
2. Redis Registry: il task è `COMPLETED` in `dias:registry:{book_id}`?
3. Redis Queues: il messaggio è presente in coda?

Se il file esiste → carica e salta l'esecuzione LLM.

## Monitoring: Architettura Dashboard

La dashboard DIAS (SvelteKit, CT201:8000) usa due modalità di fetch:

| Modalità | Endpoint | Payload | Quando |
|----------|---------|---------|--------|
| Full load | `GET /api/projects/{id}` | ~273 KB (lista file) | Mount + tab tornato visibile |
| Poll leggero | `GET /api/projects/{id}/status/live` | ~200 bytes | Ogni 60s (solo tab visibile) |

**Page Visibility API**: il polling si ferma quando il tab è nascosto (browser in background). Questo previene il consumo del limite ngrok (20K req/mese free tier) durante run lunghi come Stage D (48h+).

**Regola operativa**: per monitorare pipeline attive, usare l'IP interno `http://192.168.1.201:8000` — zero richieste ngrok.

## Primo Prodotto Completato

**Cronache del Silicio** — Aprile 2026

| Metrica | Valore |
|---------|--------|
| Scene totali | 2.174 |
| Pipeline | A → B → C → D → F (voce-only) |
| Output | `cronache_del_silicio.m4b` (270 MB) |
| Tempo Stage D | ~48h (GPU ARIA PC139) |
| Tempo Stage F | ~4 min (FFmpeg light mode, 1 core) |

## Evoluzione

| Data | Evento |
|------|--------|
| 2026-04-20 | CT202 gateway deployed |
| 2026-04-23 | Stage B/C: hotfix max_output_tokens, raw_decode parser, entity_id resolution |
| 2026-04-24 | *Cronache del Silicio* completato — primo audiobook m4b prodotto |
| 2026-04-24 | Dashboard: /status/live endpoint + Page Visibility API — fix ngrok 727 |
| 2026-04-26 | Chapter propagation system: `chapter_detector.py` + fix Stage F + Stage A/C chapter-aware |
| 2026-04-26 | Stage B prompt v1.2.1: normalizzazione nomi entità (rimozione articoli preposti) |

## Chapter Propagation System (v1.0 — 2026-04-26)

Ogni WAV del M4B finale porta ora il suo capitolo corretto, senza chiamate LLM.

### Architettura

```
fingerprint.json (Stage 0)
       │
       ▼
chapter_detector.py  ←── full_text (Stage A input)
       │  build_chapter_boundaries()
       │  Tipo 1: "Capitolo XIV: Titolo"  → prefix-match regex in sorgente
       │  Tipo 2: bare integers isolati   → re.MULTILINE + first-occurrence dedup
       │  Tipo 3: ALL-CAPS multi-word     → dominant-prefix clustering + whitelist
       ▼
chapter_boundaries.json  (cache in project_root)
       │
       ▼
Stage A — _chunk_by_chapters()
       │  Testo spezzato per capitolo PRIMA del word-count chunking
       │  → chunk non attraversa mai un confine capitolo
       │  IngestionBlock aggiunge: chapter_id, chapter_number
       ▼
Stage C — _load_block_chapter_id()
       │  Legge chapter_id dal JSON Stage A prima di creare scene
       │  Propaga chapter_id in ogni scene JSON
       ▼
Stage F — fingerprint reader + ordinal_to_chapter map
       │  Legge chapters (non chapters_list), title (non name)
       │  Costruisce subtitle_to_chapter + ordinal_to_chapter (da numeri romani)
       │  Rileva boundary WAV → inserisce [CHAPTER] in metadata FFmpeg
       ▼
M4B con capitoli corretti (n capitoli = n del fingerprint)
```

### Bug critici risolti (Stage F)

| Bug | Causa | Fix |
|-----|-------|-----|
| 0 titoli caricati | `fp.get("chapters_list")` ma fingerprint usa `chapters` | `fp.get("chapters", fp.get("chapters_list"))` |
| Tutti i titoli vuoti | `ch.get("name")` ma field è `title` | `ch.get("title", ch.get("name"))` |
| Capitoli off-by-1 (Cronache) | `chapter_{num:03d}` assume pos=ordinal ma "Libro Primo" sfasa | `ordinal_to_chapter` map costruita da fingerprint |

### Validazione

| Libro | Tipo | Capitoli fingerprint | Rilevati |
|-------|------|---------------------|---------|
| Cronache del Silicio | Tipo 1 (Capitolo XIV: Titolo) | 27 | 27/27 ✅ |
| Hyperion (Simmons) | Tipo 3 (ALL-CAPS headings) | 6 | 6/6 ✅ |
| Uomini (Tipo 2) | Tipo 2 (bare integers) | 28 | 28/28 ✅ |

### File coinvolti

| File | Ruolo |
|------|-------|
| `src/common/chapter_detector.py` | Core — rilevamento matematico boundaries |
| `src/stages/stage_a_text_ingester.py` | Chunking chapter-aware |
| `src/stages/stage_c_scene_director.py` | Propagazione chapter_id a scene |
| `src/stages/stage_f_audiobook.py` | Lettura fingerprint + metadata FFmpeg |
| `{project_root}/chapter_boundaries.json` | Cache boundaries (non ricostruita a ogni run) |

## Proposte di Sviluppo Future

| Priorità | Feature | Note |
|----------|---------|------|
| Media | **Dashboard multilingua (i18n)** | `paraglide-js` (@inlang/paraglide-sveltekit): compile-time, type-safe, zero runtime overhead. Richiede estrazione etichette UI in file `.po`/`.json` + variabile preferenza lingua nel profilo utente. Nessun cambio logica Python. |
| Bassa | **Stage B: lingua automatica dal fingerprint** | Stage 0 rileva `metadata.language`, lo scrive nel fingerprint. I prompt YAML ricevono `{book_language}` e Gemini si adatta. Rimuove il hardcoding "ITALIANO" dai template. |
| Bassa | **Stage B: raccordo post-processing nomi entità** | Normalizzazione fuzzy cross-chunk dopo Stage B per consolidare varianti residue (es. "Console"/"Il Console"). Alternativa al prompt fix, più robusta per libri con testi irregolari. |

## Dipendenze

- [[stack-aria]] — TTS (voce) + ACE-Step (audio) via Redis
- [[ct120-dias-brain]] — Redis come Universal State Bus
- [[ct201-dias-rt]] — Dashboard e API Hub runtime
- Gemini API — analisi semantica, B2 musical director (cloud, 1000 chiamate/giorno)

## Vedi anche

- [[concepts/dias-pipeline]] — flusso dati completo stage per stage
- [[concepts/dias-sound-design]] — paradigma BBC/Star Wars, regole quantitative
- [[stack-aria]] — worker GPU (consumer delle code DIAS)
