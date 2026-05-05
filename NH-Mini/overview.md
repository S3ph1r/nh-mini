---
title: "NH-Mini Homelab — Overview"
type: overview
tags: [homelab, proxmox, overview, architettura]
sources: [infrastructure-map.md]
updated: 2026-04-24
---

# NH-Mini Homelab — Overview

Homelab basato su **Proxmox PVE 9.1.1** (MiniPC Ryzen5, 32GB RAM, 1TB) su subnet `192.168.1.0/24`.

**Filosofia operativa:** CT190 (NH-Mini) è il centro di controllo e sviluppo. L'agent AI opera da qui, sviluppa i progetti in `sviluppi/`, li deploya su LXC runtime dedicati, e gestisce l'intera infrastruttura via SSH a Proxmox.

## Infrastruttura Reale (SOT)

| VMID | Nome | Ruolo | IP | Status |
|------|------|-------|----|--------|
| 190 | **NH-Mini ⭐** | Dev center + Control plane (questo) | 192.168.1.190 | 🟢 running |
| 120 | dias-brain | DIAS pipeline CPU + **Redis bus condiviso** | 192.168.1.120 | 🟢 running |
| 201 | dias-rt | DIAS Dashboard + API Hub (runtime) | 192.168.1.201 | 🟢 running |
| 202 | ct202-gateway | Internet gateway (nginx + ngrok) | 192.168.1.202 | 🟢 running |
| — | **PC Gaming** | ARIA Node Controller (RTX 5060 Ti 16GB) | 192.168.1.139 | on-demand |

**CT190 ospita:** `sviluppi/dias/`, `sviluppi/ARIA/` e tutti i futuri progetti in sviluppo.

## Architettura a Strati

```
[Internet] → CT202 (nginx+ngrok) → [RT LXC per progetto]
                                          ↓
                                   Redis su CT120
                                          ↓
                                PC139 (ARIA GPU inference)

CT190 (NH-Mini) → SSH → Proxmox → gestisce tutti i container
CT190 → git pull/push → tutti i progetti
```

## Progetti Attivi

| Progetto | Dev | Runtime | Inferenza |
|---------|-----|---------|----------|
| [[stack-dias\|DIAS]] | CT190 (`sviluppi/dias/`) | CT201 | Gemini API (via ARIA) |
| [[stack-aria\|ARIA]] | PC139 (Win11, SOT) + CT190 (mirror) | PC139 | RTX 5060 Ti locale |

## Roadmap NH-Mini

- `2026-04-24` — Refactor avviato: CT190 diventa control plane unificato
- **In costruzione**: NH-Mini Dashboard (FastAPI + warroom UI) su CT190:8080
- **In costruzione**: Discovery daemon (auto-refresh `state/inventory.json` ogni ora)
- **In costruzione**: Service catalog (agent conosce i servizi disponibili a runtime)
- **Pianificato**: Workflow project lifecycle (create → dev → promote → RT LXC)
- **Studio Architetturale**: [[docs/smart-troubleshooting-design\|Smart Troubleshooting Design (Fase 4)]] — analisi locale vs cloud, privacy e sanificazione.

## Container Legacy / Reference

I seguenti container esistono come riferimento della fase sperimentale e non fanno parte dell'architettura attuale. Verranno eliminati quando serviranno le risorse.

| VMID | Nome | Note |
|------|------|------|
| VM100 | vm-ubuntu | Primo sistema Proxmox — obsoleto |
| CT101 | chromadb | Test vector DB — da ridistribuire se serve |
| CT103 | observability | Grafana reference — non configurato per infra attuale |
| CT104 | minio | Test object storage |
| CT105 | postgres | Test DB relazionale |
| CT106 | WarRoom | Progetto pre-NH-Mini — da rifare con filosofia NH-Mini |
| CT107 | nhi-embeddings | Stack NHI precedente |
| CT160 | NHI-CORE-v1.1 | Vecchia versione NH-Mini con dashboard — in dismissione |
| CT170 | nhi-backup | Backup stack precedente |
| CT200 | ct200 | Container dev/test generico |

## Principi Infrastrutturali

- Container: unprivileged, nesting=1, bridge vmbr0
- Credenziali: SOPS+Age — mai hardcoded
- SSH key-based da CT190 a Proxmox (192.168.1.2)
- ARIA su PC139 è caso speciale: Win11 + GPU, pattern SOT descritto in [[entities/systems/stack-aria]]

## Evoluzione

- `2026-02-16` — Migrazione SOPS+Age per secrets
- `2026-02-18` — CT120 dias-brain deployed
- `2026-03-07` — CT201 dias-rt deployed
- `2026-04-20` — CT202 internet gateway deployed
- `2026-04-24` — Wiki LLM inizializzato, refactor NH-Mini come control plane avviato
