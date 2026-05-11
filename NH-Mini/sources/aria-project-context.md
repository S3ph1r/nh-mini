---
title: "ARIA — .project-context"
type: source
tags: [aria, project-context, architettura]
sources: []
updated: 2026-05-09
---

# ARIA — .project-context

**File raw:** `sviluppi/ARIA/.project-context`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-aria]], [[concepts/aria-redis-protocol]]

## Takeaway chiave

- ARIA = "stampante di rete intelligente per AI" — trasforma PC gaming in servizio AI condiviso
- Architettura ibrida: codebase su LXC 190, runtime su Windows 11 PC Gaming
- 3 nodi: Infrastructure (Redis LXC 120), Brain (LXC 190), Worker GPU (PC 139)
- Backend attuali (maggio 2026): Fish TTS (8080), Voice Cloning (8081), HTTP Asset Server (8082), Qwen3-TTS (8083), ACE-Step (8084), Qwen3.5 LLM (8085), Audiocraft (8086), LifelogASR (8087 — 🔧 setup)
- Fase attuale: `testing`
- Credenziali Redis gestite via `settings_gui.py` → TODO: migrare a NH-Mini SOPS+Age

## Note di integrazione

- Override documentato: PC Windows espone porte sulla LAN (eccezione rispetto alla policy "no porte dirette")
- Nuovi ambienti Conda creati con `--prefix` isolato (es. `lifelog-asr`) — pattern corretto adottato per i nuovi backend
- Il deploy su Windows avviene via `git pull` dopo push da LXC 190
- Backend JIT: avviati on-demand, spenti dopo `IDLE_TIMEOUT_S=2700s` (45 min) di inattività — fix 2026-05-09

## Stato Consumi ARIA

- **DIAS** — TTS sceniche (Qwen3-TTS 8083) + Sound Design (ACE-Step 8084 / Audiocraft 8086)
- **Lifelog2** — STT + diarizzazione (LifelogASR 8087, coda `aria:q:stt:local:qwen3-asr-1.7b:lifelog`)
