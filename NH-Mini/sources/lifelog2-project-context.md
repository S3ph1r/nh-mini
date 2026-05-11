---
title: "Lifelog2 Project Context"
type: source
tags: [lifelog, memory, project-context]
sources: [sviluppi/Lifelog2/.project-context]
updated: 2026-05-06
---

# Lifelog2 Project Context

**File raw**: `sviluppi/Lifelog2/.project-context`
**Data ingest**: 2026-05-06
**Pagine toccate**: [[index]], [[overview]], [[stack-lifelog2]]

## Takeaway chiave

- **Obiettivo**: Layer operativo per la memoria personale (Android audio capture → structured memories/RAG).
- **Stack**: FastAPI (backend), SvelteKit (frontend), Postgres + pgvector, Redis Streams, MinIO.
- **Infrastruttura**: Sviluppo su LXC 190, runtime previsto su `ct203-lifelog` (pending approval).
- **Integrazione**: Usa ARIA (PC139) per l'inferenza tramite il catalogo servizi di NH-Mini.

## Note di integrazione

- I venv sono isolati in `sviluppi/Lifelog2/.venv`.
- Utilizza i namespace Redis `lifelog:*` per evitare collisioni.
- Deve seguire rigorosamente il protocollo NH-Mini per la gestione dei segreti (SOPS+Age).
