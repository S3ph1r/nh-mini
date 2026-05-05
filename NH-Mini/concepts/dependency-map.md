---
title: "Mappa Dipendenze Container"
type: concept
tags: [infrastructure, dependencies, networking]
sources: [infrastructure-map.md]
updated: 2026-05-04
---

# Mappa Dipendenze Container

Panoramica delle dipendenze tra container e nodi del homelab. Le frecce indicano "dipende da" / "comunica con".

## Stack NH-Mini / Stratex

```
ct190 (NH-Mini / Stratex Dev)
  → ct105 (PostgreSQL)  : dati strutturati + vettoriali (pgvector)
  → ct120 (Redis)       : task queue per AI
  → ct107 (nhi-embeddings) : generazione vettori (CPU)
  → ct104 (MinIO)       : storage report broker (PDF/CSV)
```

[[stack-stratex]] è il nuovo sistema di intelligence finanziaria. Utilizza lo stack infrastrutturale condiviso.

## Stack DIAS

```
ct120 (dias-brain)
  → Redis locale         : code e state interni
  → Gemini API           : analisi narrativa (esterno)
  → GPU Worker (PC 139)  : job queue via Redis (BRPOP/LPUSH)

ct201 (dias-rt)
  → ct120               : coordinator (dipendenza di deploy)
```

[[ct120-dias-brain]] è il coordinator centrale. Il [[ct201-dias-rt|runtime DIAS]] espone dashboard e API.

## Stack ARIA

```
GPU Worker (PC 139)
  → ct120 (Redis)        : ricezione job (BRPOP), risposta risultati (LPUSH)
  → HTTP Asset Server locale (porta 8082) : serve output ai client
```

Il GPU Worker è un nodo Windows esterno a Proxmox. Si attiva on-demand e serve tutti gli stack (DIAS, Stratex).

## Internet Gateway

```
Internet
  → ct202 (nginx:80)     : unico ingresso HTTP
    → ngrok tunnel        : obliging-fitting-cheetah.ngrok-free.app
    → ct201:5173          : DIAS Dashboard
    → ct201:8000          : DIAS API Hub
    → ct103:3000          : Grafana
    → ct104:9001          : MinIO Console
```

[[ct202-gateway]] è il singolo punto di ingresso.

## Servizi Condivisi (Core Infrastructure)

| Servizio | Container | Consumatori |
|---------|-----------|-------------|
| PostgreSQL + pgvector | [[ct105-postgres]] | Stratex, NH-Mini |
| Redis (Task Queue) | [[ct120-dias-brain]] | DIAS, ARIA, Stratex |
| Embeddings (CPU) | [[ct107-nhi-embeddings]] | Stratex, DIAS |
| MinIO S3 | [[ct104-minio]] | Stratex, NH-Mini |
| Monitoring | [[ct103-observability]] | Tutti |
