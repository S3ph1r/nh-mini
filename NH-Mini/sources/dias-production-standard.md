---
title: "DIAS Production Standard v3.0"
type: source
tags: [dias, qualità, voce, sound-design, mixing]
sources: []
updated: 2026-04-24
---

# DIAS Production Standard v3.0

**File raw:** `sviluppi/dias/docs/production-standard.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/dias-sound-design]], [[entities/systems/stack-dias]]

## Takeaway chiave

- Formula Oscar: `subtalker_temperature=0.75`, `temperature=0.7` — questi parametri danno grana umana
- `voice_ref_text` è **mandatorio** — deve corrispondere esattamente al `ref_padded.wav` (metronomo fonetico)
- Le istruzioni TTS vanno in **inglese, in prosa** (non comandi tecnici)
- Tratto lungo (` - `) sostituisce `...` per le pause — i puntini di sospensione causano clicking in Qwen3-TTS
- Principio BBC: silenzio è il default — ogni suono deve guadagnarsi il diritto di esistere

## Note critiche (da non perdere)

- Accento inglese nel TTS italiano: verificare che `voice_ref_text` corrisponda esattamente all'audio di riferimento (es. Ezechiele 25:17 per tono drammatico)
- Ducking depth: `shallow=-6dB`, `medium=-12dB`, `deep=-18dB` — tre livelli, non più
- Fade speed: `snap=0.3s`, `smooth=1s`, `slow=2.5s`
- STING: mai a `start` di una scena, mai più di 1 per micro-chunk
