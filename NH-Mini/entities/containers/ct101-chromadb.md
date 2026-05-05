---
title: "CT101 — ChromaDB"
type: entity
tags: [container, database, vector, ai, nhi]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT101 — ChromaDB

Vector database per embeddings AI. Componente fondamentale dello stack [[stack-nhi|NHI]].

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 101 |
| Nome | chromadb-lxc |
| IP | 192.168.1.101 |
| OS | Debian 12 |
| RAM | 2048 MB |
| CPU | 2 core |
| Storage | 10 GB |
| Porta | 8000 (ChromaDB API) |
| Stato | running |

## Ruolo

Fornisce ricerca vettoriale a [[ct160-nhi-core]] (NHI-CORE). Riceve embeddings generati da ct107 e li espone tramite ChromaDB API per similarity search.

## Dipendenze

- **Consumato da:** [[ct160-nhi-core]]
- **Embedding source:** ct107 (nhi-embeddings) → ct160 → ct101

## Note

- Isolation model: `instance` (un ChromaDB per tutto il sistema NHI)
- Nessun accesso diretto dall'esterno — solo rete interna

## Vedi anche

- [[concepts/dependency-map]] — dipendenze dello stack NHI
- [[ct160-nhi-core]] — il consumer principale
