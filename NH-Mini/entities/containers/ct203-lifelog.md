---
title: "CT203 — Lifelog (v2)"
type: entity
tags: [lxc, runtime, lifelog2]
sources: [infrastructure-map.mdc]
updated: 2026-05-09
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

| Servizio | Porta | Descrizione |
|----------|-------|-------------|
| `lifelog2-api` | 8002 | API Hub per ingestione e query memoria |
| `lifelog2-dashboard` | 5173 | Dashboard Memory OS (Svelte 5) |

## Configurazione Runtime

Il container è configurato con un environment Python 3.12 isolato in `/opt/lifelog2/venv`.
Riceve aggiornamenti da [[ct190-nh-mini|CT190]] tramite il protocollo di promozione (`nh-promote.py`).

## Dipendenze

- **Database**: [[postgres-lxc|CT105]] (DB `lifelog_roberto`)
- **State/Queue**: [[ct120-redis|CT120]]
- **Object Storage**: [[minio-lxc|CT104]] (Bucket `lifelog`)
- **Inference**: [[nhi-embeddings|CT107]] (Ollama) + [[pc139-aria|PC139]] (WhisperX)

## Log di Deploy

- **2026-05-09**: Inizializzazione LXC `lifelog-v2` via `deploy_lxc.py`. Applicato workaround protocollo NH-Mini per accesso root (`prepare-lxc-proxmox.sh`). Codice promosso da CT190.
