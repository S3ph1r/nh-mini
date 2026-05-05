---
title: "Infrastructure Map — Container Proxmox"
type: source
tags: [infrastructure, containers, proxmox]
sources: []
updated: 2026-04-24
---

# Infrastructure Map — Container Proxmox

**File raw:** `knowledge/containers/infrastructure-map.mdc`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[overview]], [[ct101-chromadb]], [[ct103-observability]], [[ct104-minio]], [[ct105-postgres]], [[ct120-redis]], [[ct160-nhi-core]], [[ct190-nh-mini]], [[ct201-dias-rt]], [[ct202-gateway]], [[concepts/dependency-map]]

## Takeaway chiave

- 10 container attivi + GPU Worker esterno su subnet 192.168.1.0/24
- Tre stack applicativi indipendenti: NHI (ct160), DIAS (ct120+ct201), ARIA (GPU)
- Unico ingresso HTTP esterno: ct202 con nginx+ngrok
- ct190 (NH-Mini) è il container da cui opera l'agente AI
- Tutti i container: Debian 12, unprivileged, nesting=1

## Note di integrazione

- CT106 (WarRoom) e CT170 (nhi-backup) sono fermati — inclusi nella mappa ma esclusi dalle pagine wiki finché non tornano attivi
- CT107 (nhi-embeddings) è interno senza porte esposte — parte dello stack NHI
- Il GPU Worker è documentato nella [[concepts/dependency-map]] come nodo esterno, non come container Proxmox
- Le risorse RAM/CPU/storage sono dettagliate nelle singole pagine container
