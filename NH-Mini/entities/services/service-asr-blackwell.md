---
title: "Service: ASR Blackwell"
type: entity
tags: [asr, blackwell, voiceprint, pyannote]
sources: [asr-blackwell-migration.md]
updated: 2026-05-11
---

# Service: ASR Blackwell

Servizio ASR di produzione ottimizzato per GPU Blackwell (`sm_120`), ospitato su PC 139.

## Stack Tecnologico

- **Model**: Qwen3-ASR-1.7B (Local, BF16).
- **Diarization**: Pyannote 4.0.1 (API DiarizeOutput).
- **Embedding**: ResNet34 (wespeaker-voxceleb-resnet34-LM) -> **256 dimensioni**.
- **Audio Loading**: Soundfile (bypass Torchaudio `libtorchcodec` crash).

## Endpoint e Code

- **Listen Port**: `8087` (HTTP Health Check).
- **Redis Queue**: `aria:q:stt:local:qwen3-asr-1.7b:lifelog` (via LXC 120).
- **Callback**: `aria:c:lifelog:{job_id}`.

## Protocollo Operativo Blackwell

Per mantenere la stabilità del servizio su PC 139, seguire rigorosamente:
1. **HF_HUB_OFFLINE=0**: Deve essere settato prima degli import HuggingFace per autenticare i modelli gated.
2. **HF_HOME**: Reindirizzato a `data\assets\models\huggingface` per portabilità.
3. **No Torchaudio.load**: Usare sempre `soundfile.read` per prevenire kernel panic del driver audio Blackwell su Windows.

## Output Schema (Lifelog2 Compatible)

Il servizio restituisce un JSON contenente:
- `transcript`: Testo completo.
- `speaker_turns`: Segmenti temporali mappati per parlatore.
- `voiceprints`: Dizionario `{SPEAKER_XX: [vector256]}`.
- `word_timestamps`: Timing granulare.
