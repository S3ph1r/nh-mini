---
title: "Stack — Stratex"
type: entity
tags: [system, finance, ai, strategy, intelligence]
sources: [stratex-blueprint.md, stratex-project-context.md]
updated: 2026-05-06
---

# Stratex — Wealth Intelligence System

Stratex è un sistema personale di gestione patrimoniale e intelligence finanziaria che utilizza un approccio AI ibrido. È progettato per aggregare asset da broker, crypto exchange e banche, fornendo analisi avanzate e suggerimenti strategici.

## Architettura

Il sistema segue il pattern di separazione fisica di NH-Mini:
- **LXC 190 (NH-Mini)**: Backend FastAPI (porta 8001), frontend React servito direttamente da uvicorn via StaticFiles.
- **LXC 105 (Postgres Hub)**: Database centralizzato PostgreSQL 16 + TimescaleDB + pgvector.
- **LXC 202 (Gateway)**: Authelia v4.39.19 (forward-auth) + nginx reverse proxy con auth_request.
- **Nodo GPU (PC 139 / ARIA)**: Inferenza AI per task futuri via Redis. Per il modulo intelligence, si usa **Gemini Flash** (chiamata diretta dall'LXC — vedere nota sotto).

## Componenti Implementati

1. **Ingestion Engine** (`backend/ingestion/`): Parser BGSAXO multi-sheet e Binance CSV. Dati reali caricati: ~4000 transazioni.
2. **Market Intelligence** (`backend/stratex/intelligence/`):
   - `news_sources` table: fonti RSS e YouTube gestite via API + dashboard.
   - `rss_scraper.py`: feedparser + trafilatura per testo completo articoli.
   - `youtube_scraper.py`: yt-dlp (channel→video list) + youtube-transcript-api v1.x.
   - `news_fetcher.py`: orchestratore fetch ogni 12h via asyncio loop in lifespan FastAPI.
   - Fonti attive: CNBC, FT Alphaville, SCMP Business, The Diplomat, Ars Technica, Hacker News, Marco Casario (YouTube).
3. **Tax Center** (`backend/stratex/api/tax.py`): calcolo plus/minusvalenze, TLH suggestions, export CSV.
4. **Settings** (`backend/stratex/api/settings.py`): preferenze utente via `user_preferences` table.
5. **Auth** (`backend/stratex/api/auth.py`): `get_current_user` dependency + `/api/me`.

## Dashboard Sezioni (Frontend)

| Sezione | Stato |
|---------|-------|
| Dashboard Home | Implementata (KPI, allocazione, P&L mensile) |
| Portfolio Analytics | Implementata |
| Transactions | Implementata |
| Intelligence | **Implementata** (Feed + Fonti + ItemDrawer full body) |
| AI Chat & Strategie | Mock panel (SSE reale pianificato) |
| Tax Center | Implementata (summary, events, TLH, export) |
| Cashflow | Parziale (estimated_annual_yield da transazioni) |
| Settings | Implementata (Profile, Display, Tax, System) |

## Nota Architetturale — Intelligence e AI

Il modulo Intelligence usa **Gemini Flash API** chiamato direttamente dall'LXC (deviazione dal pattern Redis→ARIA) per l'enrichment batch (traduzione + portfolio scoring). Motivazione: context window 250k token permette batch di tutti gli item in 1-2 chiamate vs molte chiamate per-item via Redis. L'enricher (`enricher.py`) è pianificato ma non ancora implementato.

## Relazioni

- **Dipende da**: [[stack-aria]] (per inferenza future via Redis — chat, embedding, analisi avanzate).
- **Usa anche**: Gemini Flash API (diretta, per enrichment batch intelligence).
- **Gira su**: [[ct190-nh-mini]] (sviluppo attivo, uvicorn diretto).
- **Utilizza**: [[ct105-postgres]] per persistenza dati finanziari e serie temporali.
- **Protetto da**: CT202 Authelia (forward-auth via nginx).

## Stato Sviluppo

- **Fase**: Sviluppo attivo — v0.2 (Intelligence + Dashboard completa).
- **Completato in questa sessione**: Intelligence section completa (feed, fonti, drawer), RSS/YouTube scrapers, fetch loop, DB schema news_sources + market_intelligence v2.
- **Prossimi Passi**: `enricher.py` Gemini batch, AI Chat SSE reale, Alert WebSocket, i18n Phase 0.
