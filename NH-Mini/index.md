# Wiki Index — NH-Mini Second Brain

Catalogo master di tutte le pagine wiki. Aggiornato ad ogni ingest.  
Per navigare: apri in Obsidian e usa la Graph View per vedere le connessioni.
_Ultimo aggiornamento: 2026-07-06_

---

## Overview

| Pagina | Descrizione |
|--------|-------------|
| [[overview]] | Sintesi completa del homelab — architettura, container, evoluzione |
| [[user-profile]] | Profilo utente Roberto — obiettivi, preferenze, stile decisionale, note sessione |

---

## Entities — Containers

| Pagina | VMID | Ruolo | Stato |
|--------|------|-------|-------|
| [[ct101-chromadb]] | 101 | Vector DB (ChromaDB) — stack NHI | running |
| [[ct103-observability]] | 103 | Grafana + Prometheus — monitoring | running |
| [[ct104-minio]] | 104 | Object storage S3 — condiviso | running |
| [[ct105-postgres]] | 105 | Database relazionale — condiviso | running |
| [[ct120-redis]] | 120 | Redis Universal State Bus | running |
| [[ct160-nhi-core]] | 160 | NHI-CORE v1.1 — AI core | running |
| [[ct190-nh-mini]] | 190 | NH-Mini agent framework ⭐ | running |
| [[ct201-dias-rt]] | 201 | DIAS runtime — dashboard + API | running |
| [[ct202-gateway]] | 202 | Internet gateway (nginx + ngrok) | running |
| [[ct203-lifelog]] | 203 | lifelog-v2 runtime — dashboard + API | active |
| [[ct204-shifter-rt]] | 204 | SHIFTER runtime — dashboard + API | running |

---

## Entities — Systems / Stack

| Pagina | Descrizione |
|--------|-------------|
| [[entities/systems/stack-aria\|stack-aria]] | ARIA — piattaforma inferenza AI (GPU Worker, TTS, ACE-Step, Sound Factory) |
| [[entities/systems/stack-dias\|stack-dias]] | DIAS — pipeline audiobook cinematico (10 stadi, Sound-on-Demand v4.1) |
| [[entities/systems/stack-nh-mini\|stack-nh-mini]] | NH-Mini — control plane CT190 (dashboard, service catalog, discovery daemon) |
| [[entities/systems/stack-stratex\|stack-stratex]] | Stratex — Wealth Intelligence System (gestione patrimoniale, AI ibrida, RAG) |
| [[entities/systems/stack-lifelog2\|stack-lifelog2]] | Lifelog2 — Personal memory OS (pipeline A→F+Detective+G, gate B→G, 8 viste frontend, identity resolution) |
| [[entities/systems/stack-shifter\|stack-shifter]] | SHIFTER — ControlRoom 24/7 Shift Manager (solutore CP-SAT, ferie, preferenze ed equità) |
| [[entities/services/service-asr-blackwell\|service-asr-blackwell]] | ASR Blackwell Service — Backend di trascrizione e biometria su PC 139 |

---

## Concepts — NH-Mini Framework

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/dependency-map\|dependency-map]] | Mappa dipendenze tra container e stack |
| [[concepts/nh-mini-philosophy\|nh-mini-philosophy]] | Filosofia e DNA operativo di NH-Mini |
| [[concepts/telegram-push-remediation\|telegram-push-remediation]] | Sistema notifiche push e auto-riparazione interattiva (Fase 3) |
| [[concepts/security-audit-report\|security-audit-report]] | Report audit sicurezza 2026-05-09 — centralizzazione SOPS e bonifica leak |
| [[docs/smart-troubleshooting-design\|smart-troubleshooting-design]] | Studio: Analisi intelligente, Local vs Cloud e Privacy (Fase 4+) |
| [[hard-triggers\|hard-triggers]] | `knowledge/agent/hard-triggers.mdc` — Protocolli operativi rigidi per l'agent |

---

## Concepts — Lifelog2

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/lifelog2_dev-pattern\|lifelog2_dev-pattern]] | Pattern dev Lifelog2 — orchestrator B→E+Detective, Stage F, API, MinIO, Redis, frontend workflow |
| [[concepts/lifelog2-places-intelligence\|lifelog2-places-intelligence]] | Places Intelligence — apprendimento luoghi (Place Detective, cover AI, /places dashboard) |
| [[concepts/lifelog2-quality-gate\|lifelog2-quality-gate]] | Quality Gate & Tiers — Regole Stage C1, Quality Tiers A/B/C, server-side floor ed asimmetria biometria/ASR |
| [[concepts/lifelog2-telemetry\|lifelog2-telemetry]] | Telemetry — Sistema di telemetria SQLite locale (6 tabelle) ed API REST per le statistiche della pipeline |
| [[concepts/lifelog2-thread-consolidation\|lifelog2-thread-consolidation]] | Thread Consolidation Z6 — Consolidamento episodi in saghe a lungo termine via Gemini Cloud + Qwen3 Locale |
| [[concepts/lifelog2-turn-classification\|lifelog2-turn-classification]] | Turn-Level Classification — algoritmo deterministico per classificare singoli turni diarizzati (personal/media_passive/dialogue_likely/ambiguous), problema mixed segment, soglie e limiti |
| [[concepts/lifelog2-refactor-roadmap\|lifelog2-refactor-roadmap]] | **Refactor Roadmap 2026-06-24** — Confidence Tier (Full/Standard/Minimal), dual pool Trusted/Flagged, Voiceprint Resolver C1, Stage D Thread-Aware, Grouper thread-based, cleanup analisi secondo livello. Task list spuntabile per 5 fasi. |
| [[concepts/lifelog2-tier2-alignment-roadmap\|lifelog2-tier2-alignment-roadmap]] | **Tier2 Alignment Roadmap — ✅ CHIUSA 2026-07-16** — Allineamento worker secondo livello al modello thread: migrazione completata 2026-07-13 (migrations 0029-0031), batch 1200 drenato senza perdite, primo giro Tier2 reale ok. Gap residui: GPS dall'app, Day Digest catchup, retention enforcement, drop memory_atoms. |
| `sviluppi/Lifelog2/docs/lifelog2-pipeline-validation-roadmap.md` | **✅ CHIUSO** — Piano operativo M0→M5 completato (2026-06-25). FASE 1 completata, 1301 segmenti processati, ghost cleanup, validazione pipeline. M5 superseded da conversation_thread_architecture. |
| `sviluppi/Lifelog2/docs/lifelog2-classification-evolution-blueprint-v1.md` | **P0-P3 ✅ Completati** — conversation_type, quality tier, dual pool, Z7/Detective filters, back-propagation. P4-P5 deferred. P6 superseded da [[lifelog2-conversation-thread-architecture-v1]]. |
| `sviluppi/Lifelog2/docs/lifelog2-conversation-thread-architecture-v1.md` | **✅ IMPLEMENTATA (FASE 3 completata 2026-07-16, vedi thread-refactor-roadmap chiusa)** — Architettura conversation_threads: schema conversation_threads + thread_turns, Stage F 4-pass rewrite (voiceprint resolution → thread assignment → cross-atom stitching → ARIA validation), lifecycle, vp_hash, canonical_label, migration plan, invarianti. |
| `src/backend/lifelog2/services/pipeline/stage_f_grouping.py` | **✅ RISCRITTO (2026-06-26)** — Nuovo Stage F: 4 pass deterministici + ARIA a chiusura. Pass1 vp_hash, Pass2 role, Pass3 thread stitching, Pass4 coherence validation. Deployato su LXC 203. |

---

## Concepts — ARIA

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/aria-redis-protocol\|aria-redis-protocol]] | Nomenclatura code Redis e schema payload (SOT) |
| [[concepts/aria-task-lifecycle\|aria-task-lifecycle]] | Ciclo di vita di un task ARIA (stati e transizioni) |
| [[concepts/aria-environments\|aria-environments]] | Architettura ambienti Python 3 livelli (Miniconda + conda envs) |
| [[concepts/aria-asset-server\|aria-asset-server]] | Gestione repository asset multimediali e caching (New) |
| [[concepts/aria-shutdown-protocol\|aria-shutdown-protocol]] | Sequenza di spegnimento safe per stack ARIA (New) |
| [[concepts/aria-tts-backends\|aria-tts-backends]] | Fish S1-mini vs Qwen3-TTS — confronto, emotion markers, voice library |
| [[concepts/aria-telemetry\|aria-telemetry]] | TelemetryDB SQLite — schema task_log, hook post_result, query analisi performance |
| [[concepts/aria-gemini-503-pattern\|aria-gemini-503-pattern]] | Pattern 503 Gemini free tier — fasce orarie, backoff progressivo, finestre ottimali |

---

## Concepts — DIAS

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/dias-pipeline\|dias-pipeline]] | Flusso dati completo dei 10 stadi DIAS |
| [[concepts/dias-sound-design\|dias-sound-design]] | Paradigma BBC/Star Wars — PAD/AMB/SFX/STING, regole quantitative |
| [[concepts/dias-acestep-contract\|dias-acestep-contract]] | Contratto DIAS↔ARIA ACE-Step: vocabolario Qwen3, parametri, HTDemucs |
| [[concepts/dias-stage0-preproduction\|dias-stage0-preproduction]] | Stage 0 Intelligence, Dashboard, Casting, Character Bible |
| [[concepts/dias-prompt-evolution\|dias-prompt-evolution]] | Versioni prompt con rationale — lezioni apprese Stage B/C/B2 (aggiornato B v1.3, C v2.5.0) |
| [[concepts/dias-voice-pipeline-quality\|dias-voice-pipeline-quality]] | Analisi qualitativa pipeline voce v1 — gap, fixes, tassonomia pause, priorità sviluppo |

---

## Concepts — SHIFTER

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/shifter-equity-boundary\|shifter-equity-boundary]] | Boundary di fine anno, effetto settimana 53 ed equità saldi carry-over |
| [[concepts/shifter-swap-analysis\|shifter-swap-analysis]] | Logica di validazione e strumento CLI per analizzare le streak di turni scambiabili |


---

## Sources — Ingerite
- [[sources/aria-asr-finalization|ARIA ASR Finalization & Autonomous Auth]]
- [[sources/asr-blackwell-migration|ASR Blackwell Migration & Voiceprint 256d]]

| Pagina | Sorgente raw | Data |
|--------|-------------|------|
| [[sources/infrastructure-map\|infrastructure-map]] | `knowledge/containers/infrastructure-map.mdc` | 2026-04-24 |
| [[sources/aria-project-context\|aria-project-context]] | `sviluppi/ARIA/.project-context` | 2026-04-24 |
| [[sources/aria-blueprint\|aria-blueprint]] | `sviluppi/ARIA/docs/ARIA-blueprint.md` | 2026-04-24 |
| [[sources/aria-api-contract\|aria-api-contract]] | `sviluppi/ARIA/docs/ARIA-API-Contract.md` | 2026-04-24 |
| [[sources/aria-service-registry\|aria-service-registry]] | `sviluppi/ARIA/docs/ARIA-Service-Registry.md` | 2026-04-24 |
| [[sources/aria-environments-setup\|aria-environments-setup]] | `sviluppi/ARIA/docs/environments-setup.md` | 2026-04-24 |
| [[sources/aria-master-roadmap\|aria-master-roadmap]] | `sviluppi/ARIA/docs/master-roadmap.md` | 2026-04-24 |
| [[sources/aria-fish-tts-backend\|aria-fish-tts-backend]] | `sviluppi/ARIA/docs/fish-tts-backend.md` | 2026-04-24 |
| [[sources/aria-qwen3-tts-backend\|aria-qwen3-tts-backend]] | `sviluppi/ARIA/docs/qwen3-tts-backend.md` | 2026-04-24 |
| [[sources/dias-project-context\|dias-project-context]] | `sviluppi/dias/.project-context` | 2026-04-24 |
| [[sources/dias-blueprint\|dias-blueprint]] | `sviluppi/dias/docs/blueprint.md` (v7.0) | 2026-04-24 |
| [[sources/dias-workflow-logic\|dias-workflow-logic]] | `sviluppi/dias/docs/dias-workflow-logic.md` (v10.0) | 2026-04-24 |
| [[sources/dias-production-standard\|dias-production-standard]] | `sviluppi/dias/docs/production-standard.md` (v3.0) | 2026-04-24 |
| [[sources/stack-aria-dashboard\|ARIA Dashboard v2.3 Pro]] | `sviluppi/ARIA/docs/dashboard-v2.3.md` | 2026-05-06 |
| [[sources/dias-inventory\|dias-inventory]] | `sviluppi/dias/docs/dias-inventory.md` (v2.0) | 2026-04-24 |
| [[sources/dias-aria-integration-master\|dias-aria-integration-master]] | `sviluppi/dias/docs/dias-aria-integration-master.md` | 2026-04-24 |
| [[sources/dias-preproduction-guide\|dias-preproduction-guide]] | `sviluppi/dias/docs/preproduction-guide.md` | 2026-04-24 |
| [[sources/dias-technical-reference\|dias-technical-reference]] | `sviluppi/dias/docs/technical-reference.md` | 2026-04-24 |
| [[sources/dias-prompt-evolution\|dias-prompt-evolution]] | `sviluppi/dias/docs/prompt-evolution.md` | 2026-04-24 |
| [[sources/dias-voice-pipeline-quality\|dias-voice-pipeline-quality]] | `sviluppi/dias/docs/dias-voice-pipeline-quality.md` | 2026-04-29 |
| [[sources/stratex-blueprint\|stratex-blueprint]] | `sviluppi/stratex/docs/blueprint.md` (v3.0) | 2026-05-04 |
| [[sources/stratex-project-context\|stratex-project-context]] | `sviluppi/stratex/.project-context` | 2026-05-06 |
| [[sources/lifelog2-project-context\|lifelog2-project-context]] | `sviluppi/Lifelog2/.project-context` | 2026-05-06 |
| [[sources/lifelog-asr-backend\|lifelog-asr-backend]] | `sviluppi/ARIA/docs/backends/lifelog-asr.md` | 2026-05-07 |
| [[sources/lifelog2-android-handoff\|lifelog2-android-handoff]] | `sviluppi/Lifelog2/docs/lifelog2_android_handoff.md` | 2026-05-11 |
| [[sources/lifelog2-identity-resolution\|lifelog2-identity-resolution]] | `sviluppi/Lifelog2/docs/lifelog2-identity-resolution-design.md` | 2026-05-12 |
| [[sources/lifelog-stage-d-blueprint\|lifelog-stage-d-blueprint]] | `sviluppi/Lifelog2/docs/lifelog-stage-d-blueprint-v1.md` | 2026-05-13 |
| [[sources/lifelog2-status-roadmap\|lifelog2-status-roadmap]] | `sviluppi/Lifelog2/docs/lifelog2-status-roadmap.md` | 2026-05-22 |

---

## Statistiche Wiki

- **Pagine totali:** 69
- **Entities containers:** 11
- **Entities systems:** 6 (ARIA, DIAS, NH-Mini, Stratex, Lifelog2, SHIFTER)
- **Concepts:** 21
- **Sources ingerite:** 26
- **Sorgenti non ingerite:** 0 (coda svuotata ✅)
- **Ultimo aggiornamento:** 2026-06-24 (Lifelog2 refactor roadmap: confidence tier, thread model, dual pool)

---

*Per aggiungere una nuova sorgente: workflow ingest in `CLAUDE.md` → aggiorna questo file.*
*Per documentare sviluppo NH-Mini: workflow DEV in `CLAUDE.md` → aggiorna questo file.*
