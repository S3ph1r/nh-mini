---
title: "CT105 — PostgreSQL"
type: entity
tags: [container, database, postgres, sql]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT105 — PostgreSQL

Database relazionale condiviso. Isolation model `schema_per_project` — ogni progetto ha il proprio schema.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 105 |
| Nome | postgres-lxc |
| IP | 192.168.1.105 |
| RAM | 4096 MB |
| CPU | 2 core |
| Storage | 10 GB |
| Porta | 5432 (PostgreSQL) |
| Stato | running |

## Ruolo

Database relazionale condiviso tra i progetti del homelab. L'isolation tramite schema evita la proliferazione di container DB separati.

## Dipendenze

- **Consumato da:** [[ct160-nhi-core]] (schema NHI)
- **Monitorato da:** [[ct103-observability]]

## Note

- RAM più alta (4GB) rispetto agli altri container DB — indica workload relazionale più pesante
- `schema_per_project`: ogni progetto che usa Postgres ha un proprio schema isolato
- Accesso solo dalla rete interna — nessuna porta esposta all'esterno

## Vedi anche

- [[concepts/dependency-map]] — consumatori del DB
- [[ct160-nhi-core]] — consumer principale
