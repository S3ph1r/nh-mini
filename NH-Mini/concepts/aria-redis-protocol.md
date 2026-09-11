---
title: "ARIA — Protocollo Redis (API Contract v1.0)"
type: concept
tags: [aria, redis, api, protocollo, contratto]
sources: [aria-api-contract.md]
updated: 2026-09-08
---

# ARIA — Protocollo Redis (API Contract v1.0)

**Fonte di verità (SOT) per la comunicazione tra ARIA e qualsiasi client.**  
Se questo documento contraddice un blueprint, **questo vince**.

File originale: `sviluppi/ARIA/docs/ARIA-API-Contract.md`

## Nomenclatura Code

### Code di inferenza (ARIA Global)

```
aria:q:{model_type}:{provider}:{model_id}:{client_id}
```

| Campo | Valori |
|-------|--------|
| `model_type` | `llm` \| `tts` \| `stt` \| `imagegen` \| `mus` |
| `provider` | `local` (GPU PC139) \| `google` (cloud) |
| `model_id` | es. `qwen3-14b-q4km`, `whisperx-large-v3`, `gemini-flash-lite-latest` |
| `client_id` | es. `lifelog`, `dias` |

> **[Correzione 2026-09-08]** Il campo 3 è `model_type`, non `env` — la distinzione
> locale/cloud vive nel campo 4 (`provider`). Schema verificato in
> `aria_node_controller/core/batch_optimizer.py::build_queue_key` e nel discovery loop
> `orchestrator.py::_run_loop` (scansiona il pattern `aria:q:*:local:{model_id}:*`).
> La versione precedente (`{env}` con valori `cloud|local`) non combaciava col codice.
> Esempi reali in produzione: `aria:q:llm:local:qwen3-14b-q4km:lifelog` (Lifelog2 →
> Qwen3-14B), `aria:q:stt:local:whisperx-large-v3:lifelog`,
> `aria:q:imagegen:local:flux2-klein-4b:lifelog`.

### Code di risposta (callback)

```
aria:c:{client_id}:{job_id}
```

Il client fa `BRPOP` su questa chiave per ricevere il risultato.

> **[Nota 2026-09-08]** La chiave di callback è **parametrica**: ARIA fa `RPUSH` su
> qualunque valore il client abbia messo in `task.callback_key`, non impone lo schema
> sopra. `AriaCloudLLMClient` (Lifelog2 cloud) segue la convenzione
> (`aria:c:lifelog:{job_id}`); `AriaLLMClient` (Lifelog2 → Qwen3-14B locale) usa invece
> `aria:result:llm:{job_id}`. Incoerenza nota, non un bug — da uniformare se si tocca
> il protocollo.

## Model IDs

**SOT: `aria_node_controller/config/backends_manifest.json`** — più il registro
hardcoded `model_logic_ids` in `orchestrator.py::_run_loop`: ogni nuovo `model_id`
va aggiunto *anche* lì o ARIA non scansiona la sua coda (non c'è auto-discovery dal
manifest).

| model_type | provider | Model ID | Stato |
|-----|----------|----------|-------|
| `tts` | `local` | `qwen3-tts-1.7b` | ✅ |
| `tts` | `local` | `fish-s1-mini` (+ companion `voice-cloning`) | ✅ |
| `stt` | `local` | `whisperx-large-v3` | ✅ primario |
| `stt` | `local` | `qwen3-asr-1.7b` | ⏸️ standby |
| `llm` | `local` | `qwen3-14b-q4km` | ✅ — llama-server.exe b9119, porta 8090 |
| `llm` | `local` | `qwen3.5-35b-moe-q3ks` | ⚠️ solo scaffolding — mai deployato (pesi assenti su PC139) |
| `imagegen` | `local` | `flux2-klein-4b` | ✅ |
| `mus` | `local` | `acestep-1.5-xl-sft`, `audiocraft-medium` | ✅ |
| `llm` | `google` | `gemini-flash-lite-latest` | ✅ cloud (via CloudManager, non dal GPU loop) |

> **[Correzione 2026-09-08]** La tabella precedente elencava 5 modelli — di cui
> `gemini-1.5-flash-lite` (ID cloud non più in uso) e `qwen3.5-35b-moe-q3ks` marcato
> "LLM locale operativo". L'indagine
> `sviluppi/ARIA/docs/qwen3-llm-wrapper-investigation-2026-09-08.md` §5 ha verificato
> dal vivo su PC139 che quel backend è **solo scaffolding** (cartella pesi inesistente,
> `FileNotFoundError` all'avvio). Il vero LLM locale in produzione è `qwen3-14b-q4km`,
> usato solo da Lifelog2.

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
