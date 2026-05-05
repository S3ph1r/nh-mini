---
title: "Stratex — Blueprint Source"
type: source
tags: [stratex, architecture, finance, ai]
sources: [sviluppi/stratex/docs/blueprint.md]
updated: 2026-05-04
---

# Stratex — Blueprint Architetturale Unificato v3.0

**File raw**: `sviluppi/stratex/docs/blueprint.md`
**Data ingest**: 2026-05-04
**Pagine toccate**: [[stack-stratex]]

## Takeaway chiave

- **Architettura Ibrida**: Separazione netta tra LXC (logica, DB, dashboard) e Nodo GPU (inferenza AI via Redis).
- **Stack Moderno**: FastAPI, React, PostgreSQL con TimescaleDB e pgvector per gestire serie temporali e dati vettoriali.
- **Intelligence Finanziaria**: Sistema di RAG (Retrieval-Augmented Generation) che integra news, social (Reddit), dati SEC e YouTube.
- **Moduli Specializzati**: Ingestion automatica dei report broker (AI-powered), Open Banking (GoCardless), Tax Loss Harvesting e Dividend Forecaster.
- **Privacy**: Dati sensibili rimangono sull'LXC; solo prompt anonimizzati inviati al nodo GPU.

## Note di integrazione

- Il progetto è stato inizializzato in `sviluppi/stratex/`.
- Le credenziali per l'accesso ai dati su PC 139 sono state salvate in SOPS come `stratex.pc139`.
- La struttura segue rigorosamente il framework NH-Mini.
