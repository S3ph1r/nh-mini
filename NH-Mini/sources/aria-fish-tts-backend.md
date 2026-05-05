---
title: "ARIA — Fish S1-mini Backend TTS"
type: source
tags: [aria, fish, tts, voice-cloning, backend]
sources: []
updated: 2026-04-24
---

# ARIA — Fish S1-mini Backend TTS

**File raw:** `sviluppi/ARIA/docs/fish-tts-backend.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/aria-tts-backends]], [[concepts/aria-environments]]

## Takeaway chiave

- Fish S1-mini: qualità cinematica, 50+ emotion markers, WER italiano <1%, RTF ~1:5 su RTX 5060 Ti
- Architettura Dual-AR: AR-1 Semantic → AR-2 Acoustic → DAC Codec
- **Workaround critico glitch primo token**: iniettare `(break)` all'inizio di ogni chunk
- **Workaround VQGAN sm_120**: se PyTorch < 2.7 → `DEVICE="cpu"` in `voice_cloning_server.py`
- Voice Library: usa `ref.wav` (Fish) vs `ref_padded.wav` (Qwen3) — stessa cartella, file diversi

## Note di integrazione

- Stato attuale: 🔄 Da ricreare — il problema sm_120 richiede PyTorch 2.7+cu128 (documentato)
- Il parametro `normalize: False` nel payload API è critico — altrimenti i tag emotivi vengono strippati
- Chunking automatico per testi >250 parole: l'Orchestratore splitta e concatena con 80ms silenzio
- `job_id` nel payload interno è obbligatorio per Remote Skip idempotente di DIAS
