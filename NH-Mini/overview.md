---
title: "NH-Mini Homelab — Overview"
type: overview
tags: [homelab, proxmox, overview, architettura]
sources: [infrastructure-map.md]
updated: 2026-05-13
---

# NH-Mini Homelab — Overview

Homelab basato su **Proxmox PVE 9.1.1** (MiniPC Ryzen5, 32GB RAM, 1TB) su subnet `192.168.1.0/24`.

**Filosofia operativa:** CT190 (NH-Mini) è il centro di controllo e sviluppo. L'agent AI opera da qui, sviluppa i progetti in `sviluppi/`, li deploya su LXC runtime dedicati, e gestisce l'intera infrastruttura via SSH a Proxmox.

## Infrastruttura Reale (SOT)

| VMID | Nome | Ruolo | IP | Status |
|------|------|-------|----|--------|
| 190 | **NH-Mini ⭐** | Dev center + Control plane | 192.168.1.190 | 🟢 running |
| 120 | ct120-redis | **Redis Universal State Bus** (Shared Hub) | 192.168.1.120 | 🟢 running |
| 201 | dias-rt | DIAS Runtime (Dashboard + API) | 192.168.1.201 | 🟢 running |
| 203 | lifelog-v2 | **Lifelog2 Runtime (Liquid Brain Shell)** | 192.168.1.203 | 🟢 running |
| 202 | ct202-gateway | Internet gateway (nginx + ngrok) | 192.168.1.202 | 🟢 running |
| 105 | postgres-lxc | **Postgres Hub** (Stratex, Lifelog2, Core) | 192.168.1.105 | 🟢 running |
| 107 | nhi-embeddings | **Embedding Service** (Ollama mxbai 1024d) | 192.168.1.107 | 🟢 running |
| — | **PC Gaming** | ARIA Node Controller (RTX 5060 Ti) | 192.168.1.139 | 🟢 running |

## Architettura a Strati

```
[Internet] → CT202 (nginx+ngrok) → [RT LXC per progetto (CT201, CT203)]
                                           ↓
                                    Redis su CT120
                                           ↓
                                 PC139 (ARIA GPU inference)
                                           ↓
                                 CT105 (Postgres) / CT107 (Embedding)

CT190 (NH-Mini) → SSH → Proxmox → gestisce tutti i container
CT190 → git pull/push → tutti i progetti in sviluppi/
```

## Progetti Attivi

| Progetto | Fase | Runtime | Inferenza |
|---------|------|---------|----------|
| [[stack-dias\|DIAS]] | Produzione | CT201 | Gemini / Qwen3-TTS (ARIA) |
| [[stack-aria\|ARIA]] | Supporto Core | PC139 | RTX 5060 Ti (TTS, ASR, LLM) |
| [[stack-lifelog2\|Lifelog2]] | **Live / Fast Pipeline** | CT203 | ARIA (ASR, LLM) + CT107 (Embed) |
| [[stack-stratex\|Stratex]] | Produzione (Stasi) | CT190/CT202 | Local DB (CT105) |

## Roadmap NH-Mini

- `2026-05-01` — Fase 1-3 Evoluzione: Telegram Push, Journaling, Hard Triggers.
- `2026-05-09` — Promozione Lifelog2 a CT203 (Runtime live).
- `2026-05-13` — **Lifelog2 Fast Pipeline A→E** operativa end-to-end.
- **In corso**: Async Workers Level 2 per Lifelog2 (Detective, Context building).
- **Pianificato**: Consolidamento Dashboard NH-Mini (unificazione monitoraggio ARIA/DIAS).

## Evoluzione Recente

- `2026-05-01` — Implementato sistema notifiche interattive via Telegram.
- `2026-05-04` — Migrazione Stratex su Postgres CT105.
- `2026-05-06` — Promozione CT107 (Ollama) a infrastruttura reale.
- `2026-05-11` — CT203 Live con Global Registry per Lifelog2.
- `2026-05-13` — Attivato backend LLM Qwen3-14b su PC139 per arricchimento memorie.
- `2026-09-02` — Lifelog2: guardia di volume/overflow condivisa per tutte le chiamate LLM, primo audit+run reale di Z6 (mai eseguito prima), nuovo canale telemetria device (heartbeat + rubrica + chiamate) con relativa UI. Trovato e corretto un rischio reale di quota ngrok — vedi [[ct202-gateway]].
