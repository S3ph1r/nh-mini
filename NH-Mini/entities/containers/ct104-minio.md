---
title: "CT104 — MinIO"
type: entity
tags: [container, storage, s3, minio]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT104 — MinIO

Object storage S3-compatibile condiviso. Usato principalmente dallo stack [[stack-nhi|NHI]].

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 104 |
| Nome | minio-lxc |
| IP | 192.168.1.104 |
| RAM | 2048 MB |
| CPU | 1 core |
| Storage | 10 GB |
| Porta 9000 | MinIO API (S3) |
| Porta 9001 | MinIO Console (web UI) |
| Stato | running |

## Ruolo

Fornisce object storage S3-compatibile. La Console MinIO è esposta all'esterno tramite [[ct202-gateway]].

## Dipendenze

- **Consumato da:** [[ct160-nhi-core]]
- **Esposto via:** [[ct202-gateway]] → ct104:9001 (Console)

## Note

- Isolation model: `instance`
- API S3 sulla 9000 per accesso programmatico
- Console sulla 9001 per gestione manuale bucket

## Vedi anche

- [[concepts/dependency-map]] — stack NHI
- [[ct160-nhi-core]] — consumer principale
