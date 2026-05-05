---
title: "ARIA Blueprint v2.0"
type: source
tags: [aria, blueprint, architettura, gpu]
sources: []
updated: 2026-04-24
---

# ARIA Blueprint v2.0

**File raw:** `sviluppi/ARIA/docs/ARIA-blueprint.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-aria]], [[concepts/aria-task-lifecycle]], [[concepts/aria-redis-protocol]]

## Takeaway chiave

- Principio "agnosticismo del client": ARIA non conosce DIAS, non conosce i clienti — comunica solo tramite intenti (`voice_id`, `intent_id`)
- HTTPAsset Server: architettura che sostituisce Samba/path di rete con URL HTTP locali
- Semaforo GPU a 4 stati (GREEN/RED/BUSY/OFFLINE) — utente controlla manualmente da tray icon
- RTX 5060 Ti su architettura `sm_120`: richiede PyTorch 2.7+ da indice CUDA 12.8 — le versioni standard crashano
- Bootstrap cold: git clone + Conda envs + aria-download.bat per modelli + copia voice library

## Note critiche di implementazione

- **sm_120 / RTX 5060 Ti**: `--index-url https://download.pytorch.org/whl/cu128` obbligatorio per ambienti Fish. Versioni standard <2.7 crashano sul modulo VQGAN CUDA.
- **Orchestratore → Risoluzione Intent**: ARIA inietta i path fisici delle voci (`%ARIA_ROOT%\data\voices\`) nel payload prima di passarlo al backend. Il client non deve mai conoscere questi path.
- **Risultato sempre URL**: output è sempre `"audio_url": "http://192.168.1.139:8082/..."`, mai un path filesystem.
- **Visione SOA (v2.0)**: evoluzione verso pipeline interamente locali (LLM + TTS su ARIA, zero dipendenza da API cloud).

## Note di integrazione

- Il blueprint descrive alcune funzionalità future (multi-GPU, streaming LLM, GGUF) — non implementate in v1
- Sezione "Archivio Legacy" documenta la vecchia architettura con Samba (eliminata — solo per riferimento storico)
