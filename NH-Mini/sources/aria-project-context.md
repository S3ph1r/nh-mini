---
title: "ARIA — .project-context"
type: source
tags: [aria, project-context, architettura]
sources: []
updated: 2026-04-24
---

# ARIA — .project-context

**File raw:** `sviluppi/ARIA/.project-context`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-aria]], [[concepts/aria-redis-protocol]]

## Takeaway chiave

- ARIA = "stampante di rete intelligente per AI" — trasforma PC gaming in servizio AI condiviso
- Architettura ibrida: codebase su LXC 190, runtime su Windows 11 PC Gaming
- 3 nodi: Infrastructure (Redis LXC 120), Brain (LXC 190), Worker GPU (PC 139)
- Backend attuali: Fish TTS (porta 8080), Voice Cloning (8081), HTTP Asset Server (8082)
- Fase attuale: `testing`
- Credenziali Redis gestite via `settings_gui.py` → TODO: migrare a NH-Mini SOPS+Age

## Note di integrazione

- Override documentato: PC Windows espone porte sulla LAN (eccezione rispetto alla policy "no porte dirette")
- Gli ambienti Conda sono in Miniconda globale — TODO: isolare come `--prefix`
- Il deploy su Windows avviene via `git pull` o `scp` manuale (nessun CI automatico)
