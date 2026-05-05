---
title: "CT120 — DIAS Brain"
type: entity
tags: [container, dias, redis, ai, coordinator]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT120 — DIAS Brain

Coordinator centrale dello stack DIAS. Gestisce la pipeline narrativa e i CPU stages (A, B, C, F, G) tramite Redis come message bus.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 120 |
| Nome | dias-brain |
| IP | 192.168.1.120 |
| OS | Debian 12.12 |
| RAM | 4096 MB |
| CPU | 4 core |
| Storage | 30 GB |
| Porta 6379 | Redis (interno) |
| Stato | running |
| Deployed | 2026-02-18 |

## Ruolo

Coordinator della pipeline DIAS. Riceve job dal [[ct201-dias-rt|runtime]], li distribuisce ai worker via Redis (BRPOP/LPUSH), e coordina i CPU stages. Il **GPU Worker** esterno consuma la coda Redis per inferenza AI.

## Dipendenze

- **Comunica con:** [[ct201-dias-rt]] (riceve job dal runtime)
- **Message bus con:** GPU Worker (192.168.1.139) via Redis
- **AI backend:** Gemini API (esterno, per analisi narrativa)
- **Monitorato da:** [[ct103-observability]] (Redis exporter porta 9121)

## Architettura DIAS

```
ct201 (API Hub) → job → ct120 (Redis queue) → GPU Worker
GPU Worker → risultati → ct120 (Redis) → ct201 (risposta client)
```

## Note

- Storage 30GB — il più grande tra i container DIAS, probabilmente per dataset
- CPU 4 core — workload di coordinamento intenso
- Redis esposto internamente sulla 6379 — non all'esterno
- Codebase in `sviluppi/dias/`

## Vedi anche

- [[ct201-dias-rt]] — runtime/dashboard DIAS
- [[concepts/dependency-map]] — stack DIAS completo
