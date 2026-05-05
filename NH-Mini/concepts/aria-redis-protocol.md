---
title: "ARIA — Protocollo Redis (API Contract v1.0)"
type: concept
tags: [aria, redis, api, protocollo, contratto]
sources: [aria-api-contract.md]
updated: 2026-04-24
---

# ARIA — Protocollo Redis (API Contract v1.0)

**Fonte di verità (SOT) per la comunicazione tra ARIA e qualsiasi client.**  
Se questo documento contraddice un blueprint, **questo vince**.

File originale: `sviluppi/ARIA/docs/ARIA-API-Contract.md`

## Nomenclatura Code

### Code di inferenza (ARIA Global)

```
aria:q:{env}:{provider}:{model_id}:{client_id}
```

| Campo | Valori |
|-------|--------|
| `env` | `cloud` \| `local` |
| `provider` | `google` \| `openai` \| `local` |
| `model_id` | es. `qwen3-tts-1.7b`, `gemini-flash-lite-latest` |
| `client_id` | es. `dias`, `mob` |

### Code di risposta (callback)

```
aria:c:{client_id}:{job_id}
```

Il client fa `BRPOP` su questa chiave per ricevere il risultato.

## Model IDs Mandatori

| Env | Provider | Model ID | Descrizione |
|-----|----------|----------|-------------|
| `cloud` | `google` | `gemini-1.5-flash-lite` | Cloud per regia e analisi |
| `local` | `local` | `qwen3-tts-1.7b` | TTS standard (5GB VRAM) |
| `local` | `local` | `fish-s1-mini` | TTS alta qualità + cloning |
| `local` | `local` | `qwen3.5-35b-moe-q3ks` | LLM locale (13GB VRAM) |
| `local` | `local` | `acestep-1.5-xl-sft` | Music/Sound generation (16GB VRAM) |

Riferimento canonico: `aria_node_controller/config/backends_manifest.json`

## Schema Payload

### Richiesta (Client → Redis via LPUSH)

```json
{
  "job_id": "uuid-univoco",
  "client_id": "dias",
  "model_type": "tts|llm|vision|music|stt",
  "provider": "local|google",
  "model_id": "qwen3-tts-1.7b",
  "callback_key": "aria:c:dias:{job_id}",
  "timeout_seconds": 1800,
  "payload": {
    "text": "testo da sintetizzare",
    "voice_id": "narratore",
    "pace_factor": 1.0
  }
}
```

### Risposta (ARIA → Redis via RPUSH, client BRPOP)

```json
{
  "status": "done|error|timeout",
  "job_id": "...",
  "output": {
    "audio_url": "http://192.168.1.139:8082/outputs/{job_id}.wav",
    "duration_seconds": 142.5
  },
  "error": null,
  "processing_time": 68.2
}
```

## Code Interne DIAS (private, NON parte del contratto ARIA)

```
dias:q:{stage_num}:{name}
  dias:q:1:ingest
  dias:q:2:semantic
  dias:q:4:voice
```

## Note Architetturali

- Il client invia **intenti** (`voice_id: "narratore"`), ARIA risolve i path fisici internamente
- L'output è sempre un **URL HTTP** (`audio_url`), mai un path di filesystem
- I risultati sono isolati per `client_id` — DIAS non vede mai i risultati di altri client
- Su LAN domestica: isolamento per naming convention, non per crittografia

## Vedi anche

- [[stack-aria]] — sistema ARIA completo
- [[concepts/aria-task-lifecycle]] — stati e transizioni di un task
- [[stack-dias]] — principale consumatore del protocollo
