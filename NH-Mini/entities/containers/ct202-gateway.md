---
title: "CT202 — Internet Gateway"
type: entity
tags: [container, gateway, nginx, ngrok, networking]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT202 — Internet Gateway

Unico punto di ingresso HTTP dall'esterno. Nessuna application logic — solo proxy e tunnel.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 202 |
| Nome | ct202-gateway |
| IP | 192.168.1.202 |
| OS | Debian 12 minimal |
| RAM | 256 MB |
| CPU | 1 core |
| Storage | 4 GB |
| Porta 80 | nginx (ingresso ngrok) |
| Stato | running |
| Deployed | 2026-04-20 |

## Ruolo

Pattern **"unico ingresso"**: tutto il traffico HTTP esterno passa da qui. Nginx fa da reverse proxy verso i container interni. Ngrok fornisce il tunnel pubblico senza IP statico.

## Tunnel Ngrok

- URL pubblico: `obliging-fitting-cheetah.ngrok-free.app`
- Traffico: internet → ngrok → ct202:80 → nginx → container di destinazione

## Routing Nginx

| Path | Destinazione | Stato |
|------|--------------|-------|
| `/dias/` | CT201:8000 | ✅ attivo |
| `/grafana/` | CT103:3000 | 🔇 disabilitato (`.disabled`) |
| `/minio/` | CT104:9001 | 🔇 disabilitato (`.disabled`) |
| `/nhi/` | CT160:8000 | ~~obsoleto~~ — CT160 in dismissione |

Solo i file `.conf` (senza `.disabled`) vengono caricati da nginx.
Per aggiungere: `cp _template.disabled myapp.conf` → edita → `nginx -t && nginx -s reload`

## Design Philosophy

- **Minimalismo:** 256MB RAM, 1 CPU, 4GB — il più leggero di tutti
- **Separazione:** nessuna app logic nel gateway — solo proxy
- **Single entry point:** semplifica firewall e sicurezza

## Dipendenze

- **Espone (attivo):** [[ct201-dias-rt]]
- **Espone (disabilitato):** [[ct103-observability]], [[ct104-minio]]
- **Obsoleto:** [[ct160-nhi-core]] — in dismissione, route da rimuovere
- **Pattern:** vedi `knowledge/network/internet-gateway-pattern.mdc`

## Vedi anche

- [[concepts/dependency-map]] — flusso internet ingress
- [[ct201-dias-rt]], [[ct103-observability]] — servizi esposti
