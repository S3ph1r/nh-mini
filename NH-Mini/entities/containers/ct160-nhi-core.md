---
title: "CT160 — NHI-CORE v1.1"
type: entity
tags: [container, nhi, ai, core]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT160 — NHI-CORE v1.1

Cuore del sistema **Natural Homelab Intelligence (NHI)**. Aggrega quattro servizi di supporto per fornire capacità AI al homelab.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 160 |
| Nome | NHI-CORE-v1.1 |
| IP | 192.168.1.160 |
| RAM | 4096 MB |
| CPU | default |
| Storage | 8 GB |
| Porta 8000 | NHI API |
| Porta 111 | RPC |
| Stato | running |

## Ruolo

Nodo centrale dello stack NHI. Coordina embeddings, vector search, storage e dati strutturati per le funzionalità AI del homelab.

## Dipendenze (stack NHI)

```
ct160 (NHI-CORE)
  → ct101 (ChromaDB)      : vector search
  → ct105 (PostgreSQL)    : dati strutturati
  → ct107 (Embeddings)    : generazione embedding
  → ct104 (MinIO)         : object storage
```

- **Esposto via:** [[ct202-gateway]] → ct160:8000 (NHI API)
- **Monitorato da:** [[ct103-observability]]

## Note

- CPU "default" — unico container senza CPU esplicite, potrebbe essere da ottimizzare
- Porta RPC 111 — verificare se necessaria o residuo di configurazione
- v1.1 nel nome indica versioning esplicito del container

## Vedi anche

- [[ct101-chromadb]], [[ct104-minio]], [[ct105-postgres]] — servizi dipendenti
- [[concepts/dependency-map]] — stack NHI completo
- [[ct202-gateway]] — esposizione API esterna
