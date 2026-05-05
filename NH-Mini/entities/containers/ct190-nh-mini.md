---
title: "CT190 — NH-Mini (Agent Framework)"
type: entity
tags: [container, nh-mini, agent, framework, operativo]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# CT190 — NH-Mini ⭐

Container operativo principale. **L'agente AI opera da qui.** Gestisce l'intera infrastruttura via SSH a Proxmox.

## Specifiche

| Campo | Valore |
|-------|--------|
| VMID | 190 |
| Nome | NH-Mini |
| IP | 192.168.1.190 |
| RAM | 4096 MB |
| CPU | 2 core |
| Storage | 8 GB |
| Porte | solo interne (agent IDE) |
| Stato | running |

## Ruolo

Framework operativo dell'agente AI. Contiene:
- Codebase NH-Mini (`/home/Projects/NH-Mini/`)
- Accesso SSH a Proxmox host per gestione container
- Knowledge base del sistema (directory `knowledge/`)
- Wiki LLM second brain (directory `NH-Mini/`)

## Capacità Operative

L'agente da ct190 può:
- `pct exec {vmid} -- comando` → eseguire comandi in qualsiasi container
- `pct create` / `pct destroy` → gestire container (con conferma utente)
- Leggere `state/inventory.json` → stato reale infrastruttura
- Aggiornare knowledge base e wiki

## Dipendenze

- **Gestisce:** tutti i container Proxmox via SSH
- **Usa per test:** [[ct200-dev]]
- **Regole operative:** `.cursorrules` (framework) + `CLAUDE.md` (wiki)

## Note

- Nessuna porta esposta — accesso solo interno (IDE)
- Unico container con accesso SSH privilegiato a Proxmox host
- Repository pubblico su GitHub per filosofia open-by-default

## Vedi anche

- [[overview]] — contesto generale homelab
- [[concepts/dependency-map]] — ruolo nel framework operativo
