---
title: "CT203 — Lifelog (v2)"
type: entity
tags: [lxc, runtime, lifelog2]
sources: [infrastructure-map.mdc]
updated: 2026-05-22
---

# CT203 — Lifelog (v2)

**Stato**: 🟢 RUNTIME ATTIVO
**IP**: `192.168.1.203`
**Hostname**: `lifelog-v2`
**Progetto**: [[stack-lifelog2|Lifelog2]]
**Ruolo**: Nodo di esecuzione primario per la Dashboard e l'API di Lifelog2.

## Risorse

- **CPU**: 2 Cores
- **RAM**: 4096 MB
- **Storage**: 20 GB (local-lvm)
- **OS**: Debian 12

## Servizi Ospitati

| Servizio | Porta | Unit systemd | Descrizione |
|----------|-------|-------------|-------------|
| `lifelog2` | 8002 | `lifelog2.service` | API Hub ingestione e query memoria |
| `lifelog2-ui` | 5173 | `lifelog2-ui.service` | Dashboard Memory OS (Svelte 5) |
| `lifelog2-orchestrator` | — | `lifelog2-orchestrator.service` | Pipeline coordinator — sequential greedy B→E + Stage F/G/Detective |
| `lifelog2-voiceprint` | — | `lifelog2-voiceprint.service` | Voiceprint enrollment worker |
| `lifelog2-profile-builder` | — | `lifelog2-profile-builder.timer` | Profile Builder Strato 1+2 — domenica 04:00 (**⚠️ non ancora abilitato**) |
| `lifelog2-cleanup-audio` | — | `lifelog2-cleanup-audio.timer` | M4A cleanup ambient — domenica 03:00 (**⚠️ non abilitare autonomamente**) |

## Orchestratore Pipeline

`lifelog2-orchestrator` coordina quattro loop async indipendenti:
- **B→E (main)**: sequential greedy — avvia il primo stage con lavoro, aspetta drain, lo ferma
- **Stage F**: grouping episodi ogni 30min
- **Stage G**: cover generation FLUX — trigger-only, parte dopo ogni Stage F rc=0
- **Worker Detective**: identity clustering ogni 15min

Comandi manuali via Redis: `redis-cli LPUSH lifelog:orchestrator:cmd '{"cmd":"run_covers"}'`

## Configurazione Runtime

Python 3.12 isolato in `/opt/Lifelog2/.venv`. Environment variabili da `/opt/Lifelog2/.env`.
Aggiornamenti via git pull da `S3ph1r/Lifelog2` (branch `main`).

## Dipendenze

- **Database**: [[postgres-lxc|CT105]] (DB `lifelog_roberto`)
- **State/Queue**: [[ct120-redis|CT120]]
- **Object Storage**: [[minio-lxc|CT104]] (Bucket `lifelog`)
- **Inference**: [[nhi-embeddings|CT107]] (Ollama) + [[pc139-aria|PC139]] (WhisperX)

## Log di Deploy

- **2026-05-09**: Inizializzazione LXC `lifelog-v2` via `deploy_lxc.py`. Applicato workaround protocollo NH-Mini per accesso root (`prepare-lxc-proxmox.sh`). Codice promosso da CT190.
- **2026-05-17**: Stage G covers worker integrato nell'orchestratore. Git allineato a `4715397`. Pipeline E2E completa: 12/12 cover episodi generate su MinIO.
- **2026-05-20**: Stage B fix CAMCORDER (soglie ambient), rejected M4A ora salvati in `quality-rejected/`. Voiceprint Roberto re-enrollato con clip 30s ottimizzato (256d, match 25/7650 turns). Script `scripts/rematch_voiceprint.py` deployato in `/opt/Lifelog2/scripts/`.
- **2026-05-22**: Re-enrollment massivo ResNet293 (1175 segmenti, multi-segment centroid, 582 turns cosine ≥ 0.72). Geocoding Nominatim integrato in Stage F. Systemd units `lifelog2-profile-builder.service/timer` + `lifelog2-cleanup-audio.service/timer` pronti in `deploy/` (non ancora abilitati).
