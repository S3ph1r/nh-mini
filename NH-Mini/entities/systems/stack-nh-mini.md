---
title: "NH-Mini — Control Plane CT190"
type: entity
tags: [nh-mini, control-plane, dashboard, framework, ct190]
sources: []
updated: 2026-04-24
---

# NH-Mini — Control Plane CT190

NH-Mini è il **centro di controllo e sviluppo** del homelab. Opera su [[ct190-nh-mini]] (192.168.1.190) e gestisce l'intera infrastruttura: deploy container, credenziali, workspace progetti, discovery automatico e dashboard web.

## Componenti Principali

| Componente | File | Scopo |
|-----------|------|-------|
| Discovery daemon | `scripts/nh-discovery.sh` + systemd timer | Aggiorna `state/inventory.json` e `state/system-context.md` ogni 15min |
| Dashboard web | `web/app.py` + `web/static/` | Control plane visuale su http://192.168.1.190:8080 |
| Service catalog | `core/service_catalog.py` | Catalogo servizi disponibili con TCP probe live |
| Loader | `core/loader.py` | Carica contesto completo all'init sessione agent |
| Credential manager | `core/secure_credential_manager.py` | SOPS+Age per tutte le credenziali |
| Workspace manager | `core/workspace_manager.py` | Multi-progetto in `sviluppi/` |
| Deploy/undeploy | `scripts/deploy_lxc.py`, `scripts/undeploy_lxc.py` | Provisioning LXC via SSH Proxmox |
| Nuovo progetto | `scripts/nh-new-project.py` | Scaffolding progetto in `sviluppi/` con `.project-context`, README, blueprint |
| Promozione RT | `scripts/nh-promote.py` | Promuove progetto dev → RT LXC (deploy + rsync + systemd) |

## Dashboard Web

Stack: FastAPI (Python) + Vanilla HTML/JS + warroom CSS (glassmorphism).
Accesso: solo LAN — NON esposta via [[ct202-gateway]].
Pagine: Overview · Infrastructure · Projects · **Services** · ARIA

La pagina **Services** mostra il service catalog live con TCP probe opzionale (`▶ Probe live`).
Vedi `knowledge/architecture/nh-mini-dashboard.mdc` per dettagli tecnici.

Vedi `knowledge/architecture/nh-mini-dashboard.mdc` per dettagli tecnici.

## Service Catalog (stato 2026-04-24)

| Servizio | Endpoint | Stato |
|---------|----------|-------|
| Redis bus | CT120:6379 | 🟢 available |
| Internet gateway | CT202:80 | 🟢 available |
| NH-Mini Dashboard API | CT190:8080 | 🟢 available |
| DIAS API Hub | CT201:8000 | 🟢 available |
| ARIA Node Controller | PC139:8080 | 🔴 on-demand |
| SOPS+Age | CT190 (local) | ⚪ local |

## Infrastruttura Reale Gestita

- [[ct120-dias-brain]] — Redis bus + DIAS pipeline CPU
- [[ct201-dias-rt]] — DIAS runtime dashboard + API
- [[ct202-gateway]] — Internet gateway nginx + ngrok
- [[concepts/dependency-map]] — dipendenze tra componenti
- GPU Worker PC139 — ARIA inferenza (nodo esterno, Win11)

## Evoluzione

| Data | Evento |
|------|--------|
| 2026-02-16 | Migrazione SOPS+Age |
| 2026-02-18 | Discovery daemon iniziale (ogni 15min) |
| 2026-04-20 | CT202 gateway deployed |
| 2026-04-24 | **Refactor control plane**: dashboard web, service catalog, `system-context.md`, separazione infra reale/legacy |
| 2026-04-24 | **Tooling progetti**: `nh-new-project.py` (scaffolding), `nh-promote.py` (dev→RT LXC), Services tab dashboard |
| 2026-04-24 | **ARIA sync**: push PC139 → GitHub, reset mirror CT190 — codebase allineata |

## Relazione con NHI-CORE (obsoleto)

NHI-CORE (CT160) era la precedente "faccia" del sistema — dashboard web con design system warroom, API per container management, cron daemon orario per discovery. NH-Mini ha assorbito queste funzioni:
- Discovery daemon: già esisteva, ora genera anche `system-context.md`
- Dashboard: portata e estesa su CT190 (warroom CSS copiato da NHI-CORE)
- CT160 è in dismissione progressiva

Il design system warroom (glassmorphism, 4 temi) è stato copiato da NHI-CORE API prima della dismissione. File locali in `web/static/css/`.
