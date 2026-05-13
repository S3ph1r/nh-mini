---
title: "ARIA — Adaptive Resource for Inference and AI"
type: entity
tags: [sistema, aria, gpu, tts, stt, llm, redis, windows]
sources: [aria-project-context.md, aria-blueprint.md, aria-api-contract.md]
updated: 2026-05-13
---

# ARIA — Adaptive Resource for Inference and AI

**"Stampante di rete intelligente per l'AI generativa"**

ARIA è la piattaforma di inferenza AI privata del homelab. Trasforma il PC gaming con GPU in un servizio di inferenza condiviso accessibile da qualsiasi dispositivo sulla LAN come se fosse un'API cloud — senza costi ricorrenti e senza privacy compromessa.

## Identità

| Campo | Valore |
|-------|--------|
| Fase | testing |
| Stack | Python 3.10+, Redis, pystray, customtkinter, Fish-Speech, PyTorch/CUDA |
| Codebase | `sviluppi/ARIA/` (sviluppata su [[ct190-nh-mini\|LXC 190]]) |
| Runtime | PC Gaming Win11, 192.168.1.139, RTX 5060 Ti 16GB VRAM |
| Blueprint | `sviluppi/ARIA/docs/ARIA-blueprint.md` |
| Contratto Redis | `sviluppi/ARIA/docs/ARIA-API-Contract.md` (SOT) |

## Topologia Fisica

```
LAN
  LXC 190 (Brain — codebase, sviluppo)
  LXC 120 (Redis — message bus, code, state)
  PC 139  (GPU Worker — inferenza, HTTP Asset Server)
```

Il codice vive su [[ct190-nh-mini|LXC 190]]. Il runtime di produzione gira su Windows 11. I file generati (WAV, MP4) restano locali sul PC 139 e vengono serviti via HTTP Asset Server (porta 8082).

## Componenti

### Node Controller (`aria_node_controller/`)

Processo daemon Windows che:
1. Monitora le code Redis (BRPOP)
2. Avvia backend AI come subprocess (on-demand)
3. Gestisce il semaforo GPU (gaming mode)
4. Espone HTTP Asset Server (porta 8082) per servire output

Entrypoint: `main_tray.py` (system tray icon)
Monitoring: [[stack-aria-dashboard|ARIA Dashboard v2.3 Pro]]
GUI configurazione: `settings_gui.py` (customtkinter)

### Backend AI (ambienti Conda separati)

| Backend | Model ID | Porta | VRAM | Stato |
|---------|----------|-------|------|-------|
| Qwen3-TTS | `qwen3-tts-1.7b` | 8083 | ~5 GB | ✅ Operativo |
| Fish S1-mini | `fish-s1-mini` | 8080 | ~4 GB | ✅ Operativo |
| Voice Cloning | (companion Fish) | 8081 | CPU | 🔄 Da ricreare |
| LLM | `qwen3.5-35b-moe-q3ks` | 8085 | ~13 GB | 🔲 In sviluppo |
| Cloud Gemini | `gemini-flash-lite-latest` | — | cloud | ✅ Routing attivo |
| ACE-Step Music | `acestep-1.5-xl-sft` | 8084 | ~8 GB | ✅ Per DIAS D2 |
| Lifelog ASR | `qwen3-asr-1.7b` | 8087 | ~9 GB | ✅ Operativo (Blackwell) |
| Lifelog LLM | `qwen3-14b-q4km` | 8090 | ~9 GB | ✅ Operativo — llama-server.exe b9119 (CUDA 13.1 sm_120) |

### HTTP Asset Server

Micro-server HTTP nativo integrato nell'orchestratore. Espone `outputs/` su porta 8082 in sola lettura.

```
PC 139: salva WAV → %ARIA_ROOT%\data\outputs\{job_id}.wav
        serve    → http://192.168.1.139:8082/outputs/{job_id}.wav
```

## Principi Fondamentali

1. **Non-blocking sempre** — `submit_task()` ritorna in <100ms in qualsiasi scenario
2. **Zero perdita di task** — task su Redis è persistente; crash recovery all'avvio
3. **Un modello alla volta in VRAM** — BatchOptimizer gestisce il cambio modello
4. **Agnosticismo del client** — il client invia intenti (voice_id, intent_id), ARIA risolve asset
5. **Privacy totale** — nessun dato lascia la rete locale

## Semaforo GPU

| Stato | Significato |
|-------|-------------|
| GREEN | GPU disponibile per inferenza |
| RED | GPU riservata all'utente (gaming) — code si accumulano |
| BUSY | Task in esecuzione (transizione automatica) |
| OFFLINE | PC spento — heartbeat assente da >30s |

## Gestione Backend (Idle Timeout)

Backend JIT: avviati on-demand al primo task, fermati automaticamente dopo `IDLE_TIMEOUT_S = 2700s` (45 min) di inattività. Il meccanismo è gestito da `ModelProcessManager` in `orchestrator.py`:

- `mark_idle(mid)` — marca un backend come idle (timestamp)
- `shutdown_idle_backends()` — killa i backend idle da > 45 min
- **Fix 2026-05-09**: il branch `if not decision:` ora itera `_procs.keys()` invece di `known_models`. Quando le code Redis sono vuote (client in pausa), `known_models` è vuoto ma `_procs` contiene i backend caricati — senza il fix `mark_idle()` non veniva mai chiamato.

## Consumatori Attuali

- **[[stack-dias|DIAS]]** — TTS (voce scene) + ACE-Step (sound design)
- **[[stack-lifelog2|Lifelog2]]** — STT (trascrizione audio + diarizzazione, coda `aria:q:stt:local:qwen3-asr-1.7b:lifelog`)

## Vedi anche

- [[stack-aria-dashboard]] — Monitoraggio live v2.3 Pro
- [[concepts/aria-redis-protocol]] — nomenclatura code e schema payload (SOT)
- [[concepts/aria-task-lifecycle]] — ciclo di vita di un task
- [[stack-dias]] — principale cliente ARIA
- [[ct120-redis]] — Redis su LXC 120 (infrastructure node)
- [[concepts/dependency-map]] — topologia infrastruttura

### Update 2026-05-11: Blackwell ASR Stability & Voiceprint
- **Blackwell Compatibility**: Risolti crash `libtorchcodec` su Windows/PC139 sostituendo `torchaudio.load` con `soundfile.read` nel backend ASR.
- **Pyannote 4.0.1 Integration**: Aggiornato `asr_pipeline.py` per gestire il nuovo oggetto `DiarizeOutput` e l'attributo `speaker_diarization`.
- **High-Res Voiceprint**: Passaggio da embedding 192d (SpeechBrain) a **256d (ResNet34)** nativo della pipeline ASR. **ATTENZIONE**: Richiede aggiornamento DB Lifelog2 (Vector(256)).
- **Gated Models Auth**: Implementato login globale Hugging Face nel server per accesso on-demand ai modelli protetti.
