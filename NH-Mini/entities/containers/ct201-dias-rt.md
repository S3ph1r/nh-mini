---
title: "CT201 — DIAS Runtime"
type: entity
tags: [container, dias, nodejs, svelte, api]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT201 — DIAS Runtime

Runtime di produzione per lo stack DIAS. Ospita la Dashboard Svelte e l'API Hub Node.js. Interfaccia utente principale del progetto DIAS.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 201 |
| Nome | dias-rt |
| IP | 192.168.1.201 |
| OS | Debian 12 (Standard) |
| RAM | 4096 MB |
| CPU | 4 core |
| Storage | 20 GB |
| Porta 8000 | API Hub (Node.js) |
| Porta 5173 | Dashboard Svelte |
| Stato | running |
| Deployed | 2026-03-07 |

## Ruolo

Strato presentation + API del sistema DIAS. La Dashboard Svelte (porta 5173) è l'interfaccia utente. L'API Hub (porta 8000) gestisce le richieste e le invia al [[ct120-dias-brain|coordinator]].

## Dipendenze

- **Dipende da:** [[ct120-dias-brain]] (coordinator, job queue Redis)
- **Esposto via:** [[ct202-gateway]] → ct201:5173 (dashboard) e ct201:8000 (API)

## Flusso

```
Utente esterno → ct202 (nginx) → ct201:5173 (Dashboard)
                               → ct201:8000 (API Hub)
                                   → ct120 (Brain, Redis)
                                       → GPU Worker (inferenza)
```

## Note

- Engine: Node.js + Python (misto — API in Node, processing in Python?)
- Storage 20GB — significativo per un runtime, probabilmente include asset/output
- Deployed più tardi del brain (2026-03-07 vs 2026-02-18)

## Vedi anche

- [[ct120-dias-brain]] — coordinator DIAS
- [[ct202-gateway]] — gateway di esposizione esterna
- [[concepts/dependency-map]] — stack DIAS completo
