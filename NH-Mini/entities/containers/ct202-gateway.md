---
title: "CT202 — Internet Gateway"
type: entity
tags: [container, gateway, nginx, ngrok, cloudflare, authelia, networking]
sources: [infrastructure-map.md]
updated: 2026-09-02
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

## Vincolo reale: quota ngrok free-tier (2026-09-02) — ⚠️ ridimensionato 2026-09-02 (stessa sera)

> **Correzione, poche ore dopo**: la stima sotto ("avrebbe consumato ~86.400
> richieste/mese") era un worst-case mai verificato contro il contatore reale
> dell'agent. Verificato ora via `curl 127.0.0.1:4040/api/tunnels` sul host: il
> tunnel ngrok riporta **1.256 richieste HTTP totali in 51 giorni di uptime
> processo** (~740/mese) — un ventisettesimo della quota da 20.000. Nessun
> rischio reale di esaurimento a questo regime.
>
> **Causa dell'errore**: CT202 esegue *anche* `cloudflared` (quick tunnel,
> attivo dal 15/07, stesso target `http://localhost:80` di ngrok). La firma
> `127.0.0.1` nei log nginx è quindi **ambigua tra i due tunnel**, non prova
> univoca di instradamento ngrok come assunto sotto. Conteggio reale traffico
> telefono (`user-agent: okhttp`) in `gateway_access.log`: 26.677 richieste via
> quel loopback ambiguo, 1.930 via LAN diretta (`192.168.1.30`). Poiché l'agent
> ngrok ne rivendica solo 1.256 in tutto, le restanti ~25.400 sono quasi
> certamente transitate per Cloudflare (nessuna quota di questo tipo), non per
> ngrok. Non ancora verificato con certezza assoluta (servirebbe log dell'header
> `Host` per attribuzione univoca per-richiesta) — ma il contatore nativo
> dell'agent resta la fonte più autorevole per "quota ngrok consumata", ed è
> quello che conta qui.
>
> **Cosa resta valido**: l'heartbeat a 5 minuti (invece di 30s) resta comunque
> la scelta giusta per batteria/carico server, indipendentemente dal tunnel.
> **Cosa non è più valido**: l'inquadramento "rischio reale di esaurimento
> quota" e il parallelo con l'incidente ngrok DIAS del 24 aprile (quello sì
> confermato via commit reale, causa diversa — tab browser aperto che pollava
> `/api/projects/{id}` via URL pubblico ngrok, non ambiguità tra tunnel).

Il tunnel ngrok gira sul piano **gratuito** (dominio `*.ngrok-free.app`) — limite
verificato: **20.000 richieste HTTP/mese**, 1GB banda. Qualunque servizio che
instrada traffico frequente/periodico attraverso questo tunnel (non solo
Lifelog2) deve tenerne conto nel dimensionare la propria cadenza.

Trovato durante lo sviluppo del canale heartbeat di [[stack-lifelog2]]: un
heartbeat device→server a 30s di cadenza avrebbe da solo consumato ~86.400
richieste/mese (oltre 4× la quota) in circa una settimana — scoperto verificando
che tutto il traffico verso `/lifelog/` passa dal tunnel (firma `127.0.0.1` nei
log di nginx, segno dell'agent ngrok/cloudflared che inoltra in locale), non
dalla LAN diretta come inizialmente assunto. Corretto a 5 minuti lato app.

**Promemoria per futuri servizi**: qualunque nuovo canale periodico esposto via
`/lifelog/`, `/shifter/`, `/stratex/` o simili deve restare abbondantemente sotto
questa soglia, oppure va valutato un piano ngrok a pagamento o instradamento
diretto LAN quando possibile. **Aggiornamento**: dato il margine reale enorme
(~740/mese osservati contro 20.000 di limite), questo non è un vincolo stringente
allo stato attuale — resta un promemoria utile solo se il traffico via ngrok
specificamente (non Cloudflare, non LAN) dovesse crescere di un ordine di
grandezza.

## Vedi anche

- [[concepts/dependency-map]] — flusso internet ingress
- [[stack-shifter]], [[stack-dias]], [[stack-lifelog2]]
