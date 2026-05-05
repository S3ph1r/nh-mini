---
title: "ARIA Master Roadmap v2.1"
type: source
tags: [aria, roadmap, stato, completato, da-fare]
sources: []
updated: 2026-04-24
---

# ARIA Master Roadmap v2.1

**File raw:** `sviluppi/ARIA/docs/master-roadmap.md`
**Data ingest:** 2026-04-24 (documento aggiornato al 2026-03-14)
**Pagine toccate:** [[entities/systems/stack-aria]]

## Stato Componenti (al 2026-03-14)

### ✅ Completati (Infrastruttura)
- Redis Message Mesh decoupled
- Heartbeat Redis v2.1 (`aria:global:node:{ip}:status`)
- Idempotenza lato Worker (skip GPU se file esistente)
- HTTP Asset Server (porta 8082)
- Cloud Gateway v2.0 con Rate Limiting & Quota centralizzati

### ✅ Completati (Orchestratore)
- Queue Manager v2.1
- Gemini Rate Limiter (Pacing 30s + Lockout 10min)
- Result Writer (TTL 24h)
- Semaforo (Tray App)
- Crash Recovery (Visibility Lock)
- VRAM Manager (load/unload automatizzato)
- Batch Optimizer (priorità code, JIT swapping)

### Stato Backend

| Backend | Stato |
|---------|-------|
| Qwen3-TTS | ✅ Operativo |
| Cloud Gemini | ✅ Operativo |
| Fish-Speech | 🔄 In Ripristino (sm_120 issue) |
| Music & SFX | 🔲 Progettato |

### 🔲 Non ancora implementati
- ARIA Health Dashboard (Streamlit) — monitoraggio GPU e Heartbeats
- DIAS Project Dashboard (Streamlit) — stato avanzamento audiolibro

## Note di integrazione

- La roadmap è aggiornata al 2026-03-14 — verificare stato Fish dopo quella data
- Le dashboard Streamlit sono pianificate ma non prioritarie rispetto alla pipeline audio
