---
title: "CT202 — Internet Gateway"
type: entity
tags: [container, gateway, nginx, ngrok, cloudflare, authelia, networking]
sources: [infrastructure-map.md]
updated: 2026-06-23
---

# CT202 — Internet Gateway

Unico punto di ingresso HTTP dall'esterno. Nessuna application logic — solo proxy, tunnel e autenticazione.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 202 |
| Nome | ct202-gateway |
| IP | 192.168.1.202 |
| OS | Debian 12 minimal |
| RAM | 512 MB |
| CPU | 1 core |
| Storage | 4 GB |
| Porta 80 | nginx reverse proxy |
| Stato | running |
| Deployed | 2026-04-20 |

## Servizi attivi

| Servizio | Systemd | Scopo |
|----------|---------|-------|
| nginx | `nginx.service` | Reverse proxy — routing per path |
| ngrok | `ngrok.service` | Tunnel internet → CT202:80 (dominio statico) |
| cloudflared | `cloudflared-quick.service` | Tunnel internet → CT202:80 (URL effimera) |
| authelia | `authelia.service` | SSO — protegge /shifter/ e /stratex/ |
| cf-url-sync | `cf-url-sync.timer` | Aggiorna `/var/www/html/gateway/cf-url.txt` ogni 30s |

## Tunnel pubblici

| Tunnel | URL | Tipo |
|--------|-----|------|
| ngrok | `obliging-fitting-cheetah.ngrok-free.app` | Dominio statico — non cambia mai |
| cloudflared-quick | vedi `state/cf-url-last.txt` su LXC 190 | Effimera — cambia ad ogni riavvio del servizio |

L'URL Cloudflare attuale è monitorata da `cf-url-watcher.timer` su LXC 190: se cambia, arriva notifica Telegram.

## Routing nginx

### Block catch-all — accessibile via ngrok + Cloudflare

| Path | Backend | Auth |
|------|---------|------|
| `/` | redirect → `/dias/` | — |
| `/health` | 200 OK | — |
| `/authelia` | `127.0.0.1:9091` | — |
| `/dias/` | CT201:8000 | aperto |
| `/lifelog/` | CT203:8002 | aperto |
| `/lifelog-ui/` | CT203:5173 | aperto |
| `/shifter/` | CT204:8000 | ✅ Authelia |
| `/stratex/` | CT190:8001 | ✅ Authelia |
| `/gateway/` | `/var/www/html/gateway/` | LAN only |

### Block LAN-direct (`server_name 192.168.1.202`)

| Path | Backend | Auth |
|------|---------|------|
| `/shifter/` | CT204:8000 | nessuna (headers admin hardcoded) |
| `/gateway/` | `/var/www/html/gateway/` | LAN only |

## Dashboard gateway

Accessibile solo da LAN: `http://192.168.1.202/gateway/`
Mostra: metriche nginx, URL ngrok live, URL Cloudflare, route map.

## Design Philosophy

- **Minimalismo**: CT202 può essere ricreato senza perdere dati — è stateless
- **Separazione**: nessuna app logic nel gateway — solo proxy
- **Documentazione SOT**: tutta la conoscenza vive su [[stack-nh-mini|LXC 190]], non sul container

## Dipendenze (route attive)

- **Espone**: [[ct201-dias-rt]], [[ct203-lifelog]], [[ct204-shifter-rt]]
- **Espone (con auth)**: SHIFTER (`/shifter/`), Stratex (`/stratex/`)
- **Pattern**: `knowledge/network/internet-gateway-pattern.mdc`

## Vedi anche

- [[concepts/dependency-map]] — flusso internet ingress
- [[stack-shifter]], [[stack-dias]], [[stack-lifelog2]]
