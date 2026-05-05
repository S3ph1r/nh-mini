---
title: "ARIA — Qwen3-TTS 1.7B Backend"
type: source
tags: [aria, qwen3, tts, backend, instruct]
sources: []
updated: 2026-04-24
---

# ARIA — Qwen3-TTS 1.7B Backend

**File raw:** `sviluppi/ARIA/docs/qwen3-tts-backend.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/aria-tts-backends]], [[concepts/aria-environments]]

## Takeaway chiave

- Qwen3-TTS: ideale per narrazione lunga, stabile su testi lunghi, controllo via prosa inglese naturale
- **Auto-Padding automatico**: il server genera `ref_padded.wav` (+ 0.5s silenzio) se non esiste — risolve bleeding fonetico
- Variante mandatoria: `Qwen3-TTS-12Hz-1.7B-Base` (la 0.6B ha bug long-silence)
- JIT Model Swap: se arriva task per `qwen3-tts-custom` mentre è attivo il Base, l'Orchestratore fa swap con `startup_wait=240s`
- `job_id` nel payload interno è **obbligatorio** per Remote Skip idempotente

## Note di integrazione

- Python 3.12 obbligatorio (Fish usa 3.10 — due ambienti separati)
- Flash Attention 2 opzionale ma consigliato (riduce VRAM e latenza) — wheel precompilato da GitHub releases
- Il server endpoint `/tts` risolve automaticamente `voice_id` → path `ref_padded.wav` + `ref.txt`
- **Server di produzione** (confermato 2026-05-03): `C:\Users\Roberto\aria\backends\qwen3tts\server.py` — avviato dall'orchestratore con argomenti CLI (`--model-path`, `--port`). Il file `scripts\qwen3\qwen3_server.py` è un backup obsoleto non in produzione.
- Il server production gestisce sia il modello Base (zero-shot cloning) che CustomVoice — rileva automaticamente il tipo dal modello caricato
- Preset instruct per emozioni DIAS documentati in [[concepts/aria-tts-backends]]
