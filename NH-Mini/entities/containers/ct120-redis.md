---
title: "CT120 — Redis Universal State Bus"
type: entity
tags: [container, redis, infrastructure, state-bus]
sources: [infrastructure-map.md]
updated: 2026-05-05
---

# CT120 — Redis Universal State Bus

Infrastructure node condiviso. Ospita Redis come message bus universale per tutti i progetti NH-Mini (DIAS, ARIA, Stratex). Non è legato a nessun progetto specifico.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 120 |
| Nome | ct120-redis |
| IP | 192.168.1.120 |
| OS | Debian 12.12 |
| RAM | 4096 MB |
| CPU | 4 core |
| Storage | 30 GB |
| Porta 6379 | Redis (accessibile su LAN) |
| Stato | running |
| Deployed | 2026-02-18 |

## Ruolo

Universal State Bus dell'intera infrastruttura NH-Mini. Ogni progetto che richiede code asincrone, pub/sub o stato condiviso usa Redis su questo container.

- **DIAS**: code pipeline (BRPOP/LPUSH), checkpoint stage, pausa/ripresa
- **ARIA**: job queue GPU (`aria:q:*`), semaforo, risultati callback (`aria:c:*`)
- **Stratex**: task queue inferenza AI via ARIA

## Dipendenze

- **Usato da:** [[ct201-dias-rt]] (DIAS pipeline), PC 139 ARIA (GPU jobs), [[ct190-nh-mini]] (heartbeat, service catalog)
- **Monitorato da:** [[ct103-observability]] (Redis exporter porta 9121)

## Architettura

```
ct201 (DIAS API Hub) ──► ct120:6379 (Redis) ◄── PC139 (ARIA Worker)
ct190 (NH-Mini)      ──► ct120:6379           ◄── Stratex backend
```

## Note

- maxmemory=2GB, policy=allkeys-lru, snapshot ogni 60s
- Redis non esposto all'esterno — solo LAN interna
- Rinominato da `dias-brain` → `ct120-redis` il 2026-05-05 (il nome era fuorviante)

## Vedi anche

- [[ct201-dias-rt]] — runtime DIAS
- [[stack-aria]] — stack ARIA (usa Redis come bus)
- [[concepts/dependency-map]] — mappa dipendenze completa
