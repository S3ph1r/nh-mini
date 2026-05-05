---
title: "CT103 — Observability"
type: entity
tags: [container, monitoring, grafana, prometheus]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT103 — Observability

Stack di monitoring centralizzato: **Grafana + Prometheus**. Monitora tutti i container attivi.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 103 |
| Nome | observability |
| IP | 192.168.1.103 |
| RAM | 2048 MB |
| CPU | 2 core |
| Storage | 10 GB |
| Porta 3000 | Grafana (dashboard) |
| Porta 9090 | Prometheus (metriche) |
| Porta 9121 | Redis exporter |
| Stato | running |

## Ruolo

Raccolta e visualizzazione metriche da tutta l'infrastruttura. Grafana esposto tramite [[ct202-gateway]] all'esterno.

## Dipendenze

- **Monitora:** tutti i container attivi
- **Esposto via:** [[ct202-gateway]] → ct103:3000 (Grafana)

## Note

- Redis exporter sulla porta 9121 — monitora Redis di [[ct120-dias-brain]]
- Prometheus scrape interval: da verificare

## Vedi anche

- [[concepts/dependency-map]] — flusso monitoring
- [[ct202-gateway]] — come viene esposto Grafana all'esterno
