---
title: "CT204 — SHIFTER Runtime"
type: entity
tags: [container, shifter, python, fastapi, solver]
sources: [infrastructure-map.md]
updated: 2026-06-11
---

# CT204 — SHIFTER Runtime

Runtime di produzione per lo stack SHIFTER. Ospita la Dashboard ed API di pianificazione turni ed equità della control room.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 204 |
| Nome | shifter-rt |
| IP | 192.168.1.204 |
| OS | Debian 12 (Standard) |
| RAM | 1024 MB |
| CPU | 1 core |
| Storage | 10 GB |
| Porta 8000 | API & Dashboard (FastAPI/Uvicorn) |
| Stato | running |
| Deployed | 2026-06-11 |

## Ruolo

Strato di produzione per SHIFTER. Ospita l'API backend FastAPI e la dashboard client integrata (porta 8000), eseguendo il solutore matematico basato su Google OR-Tools (CP-SAT) per la generazione dei turni del personale.

## Dipendenze

- **Dipende da:** [[stack-nh-mini]] (come sotto-progetto gestito)
- **Esposto via:** [[ct202-gateway]] (prossima integrazione proxy)

## Flusso

```
Utente interno → ct204:8000 (Dashboard / API)
                   → database locale SQLite (shifts.db)
                   → Google OR-Tools Solver
```

## Note

- Engine: Python FastAPI + SQLite + Google OR-Tools
- Deployed il 2026-06-11 tramite `nh-promote.py`

## Vedi anche

- [[entities/systems/stack-shifter|Stack — SHIFTER]]
- [[ct202-gateway]] — gateway di esposizione esterna
- [[concepts/dependency-map]] — mappa delle dipendenze dell'infrastruttura
