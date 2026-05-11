---
title: "Lifelog2 Dev Pattern"
type: concept
tags: [lifelog2, development, api]
updated: 2026-05-11
---

# Lifelog2 Dev Pattern

Lifelog2 segue un pattern di sviluppo asincrono basato su eventi Redis e persistenza MinIO, con il control plane su CT190.

## Architettura di Sviluppo

- **API Backend**: FastAPI su porta `8002`.
- **Worker Pipeline**: Processi Python indipendenti (Stage A, B, C) che consumano stream Redis.
- **Object Storage**: Bucket `lifelog` su MinIO (CT104).
- **Database**: PostgreSQL su CT105 (database `lifelog_roberto`).

## Workflow Operativo

1. **Avvio API**:
   ```bash
   cd sviluppi/Lifelog2/src/backend
   source .venv/bin/activate
   uvicorn lifelog2.main:app --host 0.0.0.0 --port 8002 --reload
   ```

2. **Test Pipeline**:
   Gli script di test (es. `scratch/inject_asr_task.py`) vengono usati per simulare l'arrivo di nuovi dati biometrici o trascrizioni.

## Integrazione NH-Mini
Il servizio `lifelog2_dev` è monitorato su porta `8002`. 
La documentazione di riferimento per la produzione si trova in `NH-Mini/entities/systems/stack-lifelog2.md`.
