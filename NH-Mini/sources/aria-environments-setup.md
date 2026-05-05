---
title: "ARIA — Guida Ambienti Python"
type: source
tags: [aria, python, conda, ambienti, setup, windows]
sources: []
updated: 2026-04-24
---

# ARIA — Guida Ambienti Python

**File raw:** `sviluppi/ARIA/docs/environments-setup.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/aria-environments]], [[concepts/aria-tts-backends]]

## Takeaway chiave

- Architettura 3 livelli: Miniconda (Orchestratore) + conda env Qwen3 (Python 3.12, cu124) + conda env Fish (Python 3.10, cu128)
- **Sempre** `conda create --prefix` (project-local in `%ARIA_ROOT%\envs\`), mai `--name` (globale)
- RTX 5060 Ti sm_120: Qwen3 richiede `torch>=2.6+cu124`, Fish richiede `torch>=2.7+cu128`
- L'Orchestratore avvia i backend con `subprocess.Popen()` chiamando il `python.exe` diretto (no `conda activate`)
- Template YAML in `envs/templates/` per ricostruzione rapida degli ambienti

## Note di integrazione

- La finestra CMD visibile avviata dall'Orchestratore è intenzionale: permette di vedere i log di inferenza in tempo reale sul PC gaming
- `startup_wait=240s` per Qwen3 — il modello impiega ~30-60s per caricarsi in VRAM (prima volta più lento)
- Il setup dettagliato con comandi esatti è in questo file — consultarlo prima di ricreare gli ambienti
