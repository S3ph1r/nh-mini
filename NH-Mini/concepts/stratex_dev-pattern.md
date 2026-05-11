---
title: "Stratex Dev Pattern"
type: concept
tags: [stratex, development, dashboard]
updated: 2026-05-11
---

# Stratex Dev Pattern

Il pattern di sviluppo per Stratex su CT190 (NH-Mini Control Plane) prevede un ambiente isolato che funge da sandbox prima della promozione in runtime.

## Architettura di Sviluppo

- **Backend**: FastAPI su porta `8001`.
- **Frontend**: Vite + React su porta `5174` (HMR attivo).
- **Database**: Connessione diretta a PostgreSQL su CT105 (database `stratex`).
- **Secrets**: Gestiti via SOPS + `.env` locale (non committato).

## Workflow Operativo

1. **Avvio Backend**:
   ```bash
   cd sviluppi/stratex/backend
   source .venv/bin/activate
   uvicorn stratex.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Avvio Frontend**:
   ```bash
   cd sviluppi/stratex/frontend
   npm run dev -- --host
   ```

## Integrazione NH-Mini
La dashboard di NH-Mini monitora il servizio `stratex_dev` verificando la porta `8001`. 
La remediation standard in caso di blocco è il kill forzato del processo via porta (`kill -9 $(lsof -t -i:8001)`).
