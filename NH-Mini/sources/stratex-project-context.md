---
title: "Stratex Project Context"
type: source
tags: [stratex, identity, finance, intelligence]
sources: [sviluppi/stratex/.project-context]
updated: 2026-05-06
---

# Stratex Project Context

**File raw**: `sviluppi/stratex/.project-context`
**Data ingest**: 2026-05-06
**Pagine toccate**: [[index]], [[stack-stratex]]

## Takeaway chiave

- **Identità**: Wealth Intelligence System per gestione patrimoniale e AI ibrida.
- **Stack**: FastAPI (backend), React (frontend), PostgreSQL + TimescaleDB + pgvector, Redis, Celery.
- **Nodi**: 
    - Dev/Logic: LXC 190 (NH-Mini).
    - DB Node: CT105 (Postgres Hub).
    - AI Node: PC139 (ARIA) via Redis + Gemini Flash diretto per enrichment batch.
- **Integrazione**: Utilizza il database centralizzato su CT105 e l'inferenza distribuita su PC139.
- **Intelligence Module**: RSS scraper (feedparser+trafilatura) + YouTube scraper (yt-dlp+transcript-api). Fonti gestite via `news_sources` table. Fetch loop ogni 12h in FastAPI lifespan.
- **Dashboard**: Completa con sezioni Home, Portfolio, Transactions, Intelligence, Tax Center, Settings.

## Note di integrazione

- Gestione segreti via SOPS+Age (`ct105.postgres`, `stratex.pc139`).
- Deviazione architetturale: Gemini Flash usato direttamente per enrichment batch (traduzione + scoring), non via Redis→ARIA. Motivazione: context window 250k per batch.
- Prossimo sviluppo: `enricher.py`, AI Chat SSE reale, Alert WebSocket.
