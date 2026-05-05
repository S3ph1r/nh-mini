# Wiki Index — NH-Mini Second Brain

Catalogo master di tutte le pagine wiki. Aggiornato ad ogni ingest.  
Per navigare: apri in Obsidian e usa la Graph View per vedere le connessioni.

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
| [[ct120-dias-brain]] | 120 | DIAS coordinator + Redis | running |
| [[ct160-nhi-core]] | 160 | NHI-CORE v1.1 — AI core | running |
| [[ct190-nh-mini]] | 190 | NH-Mini agent framework ⭐ | running |
| [[ct201-dias-rt]] | 201 | DIAS runtime — dashboard + API | running |
| [[ct202-gateway]] | 202 | Internet gateway (nginx + ngrok) | running |

---

## Entities — Systems / Stack

| Pagina | Descrizione |
|--------|-------------|
| [[entities/systems/stack-aria\|stack-aria]] | ARIA — piattaforma inferenza AI (GPU Worker, TTS, ACE-Step, Sound Factory) |
| [[entities/systems/stack-dias\|stack-dias]] | DIAS — pipeline audiobook cinematico (10 stadi, Sound-on-Demand v4.1) |
| [[entities/systems/stack-nh-mini\|stack-nh-mini]] | NH-Mini — control plane CT190 (dashboard, service catalog, discovery daemon) |
| [[entities/systems/stack-stratex\|stack-stratex]] | Stratex — Wealth Intelligence System (gestione patrimoniale, AI ibrida, RAG) |

---

## Concepts — NH-Mini Framework

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/dependency-map\|dependency-map]] | Mappa dipendenze tra container e stack |
| [[concepts/nh-mini-philosophy\|nh-mini-philosophy]] | Filosofia e DNA operativo di NH-Mini |
| [[concepts/telegram-push-remediation\|telegram-push-remediation]] | Sistema notifiche push e auto-riparazione interattiva (Fase 3) |
| [[docs/smart-troubleshooting-design\|smart-troubleshooting-design]] | Studio: Analisi intelligente, Local vs Cloud e Privacy (Fase 4+) |
| [[hard-triggers\|hard-triggers]] | `knowledge/agent/hard-triggers.mdc` — Protocolli operativi rigidi per l'agent |

---

## Concepts — ARIA

| Pagina | Descrizione |
|--------|-------------|
| [[concepts/aria-redis-protocol\|aria-redis-protocol]] | Nomenclatura code Redis e schema payload (SOT) |
| [[concepts/aria-task-lifecycle\|aria-task-lifecycle]] | Ciclo di vita di un task ARIA (stati e transizioni) |
| [[concepts/aria-environments\|aria-environments]] | Architettura ambienti Python 3 livelli (Miniconda + conda envs) |
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

## Sources — Ingerite

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
| [[sources/dias-inventory\|dias-inventory]] | `sviluppi/dias/docs/dias-inventory.md` (v2.0) | 2026-04-24 |
| [[sources/dias-aria-integration-master\|dias-aria-integration-master]] | `sviluppi/dias/docs/dias-aria-integration-master.md` | 2026-04-24 |
| [[sources/dias-preproduction-guide\|dias-preproduction-guide]] | `sviluppi/dias/docs/preproduction-guide.md` | 2026-04-24 |
| [[sources/dias-technical-reference\|dias-technical-reference]] | `sviluppi/dias/docs/technical-reference.md` | 2026-04-24 |
| [[sources/dias-prompt-evolution\|dias-prompt-evolution]] | `sviluppi/dias/docs/prompt-evolution.md` | 2026-04-24 |
| [[sources/dias-voice-pipeline-quality\|dias-voice-pipeline-quality]] | `sviluppi/dias/docs/dias-voice-pipeline-quality.md` | 2026-04-29 |
| [[sources/stratex-blueprint\|stratex-blueprint]] | `sviluppi/stratex/docs/blueprint.md` (v3.0) | 2026-05-04 |

---

## Statistiche Wiki

- **Pagine totali:** 54
- **Entities containers:** 9
- **Entities systems:** 4 (ARIA, DIAS, NH-Mini, Stratex)
- **Concepts:** 14
- **Sources ingerite:** 20
- **Sorgenti non ingerite:** 0 (coda svuotata ✅)
- **Ultimo aggiornamento:** 2026-05-04 (Inizializzazione Stratex — Import doc da PC 139)

---

*Per aggiungere una nuova sorgente: workflow ingest in `CLAUDE.md` → aggiorna questo file.*
*Per documentare sviluppo NH-Mini: workflow DEV in `CLAUDE.md` → aggiorna questo file.*
