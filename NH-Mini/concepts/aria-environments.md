---
title: "ARIA — Architettura Ambienti Python (3 Livelli)"
type: concept
tags: [aria, python, conda, ambienti, gpu, windows]
sources: [aria-environments-setup.md, aria-blueprint.md]
updated: 2026-04-24
---

# ARIA — Architettura Ambienti Python (3 Livelli)

Architettura che garantisce isolamento totale tra backend, portabilità e avvio on-demand.

## Schema a 3 Livelli

```
LIVELLO 0: Miniconda Globale
  C:\Users\Roberto\miniconda3\python.exe
  Librerie: pystray, redis, PIL, customtkinter
  Esegue: main_tray.py (Orchestratore)
  NON carica modelli in VRAM

LIVELLO 1a: Ambiente Qwen3-TTS
  C:\Users\Roberto\aria\envs\qwen3tts\python.exe
  Python 3.12 + PyTorch 2.6+cu124 + qwen-tts + FastAPI
  Esegue: qwen3_server.py (porta 8083)
  VRAM: ~4-5 GB

LIVELLO 1b: Ambiente Fish-Speech
  C:\Users\Roberto\aria\envs\fish-speech-env\python.exe
  Python 3.10 + PyTorch 2.7+cu128 + fish-speech
  Esegue: tools/api_server.py (porta 8080)
           voice_cloning_server.py (porta 8081)
  VRAM: ~3-4 GB
```

## Variabili Deploy Corrente (PC Gaming)

| Variabile | Valore |
|-----------|--------|
| `%USERNAME%` | `Roberto` |
| `%ARIA_ROOT%` | `C:\Users\Roberto\aria` |
| `%MINICONDA_ROOT%` | `C:\Users\Roberto\miniconda3` |
| `%REDIS_HOST%` | `192.168.1.10` (CT120 su MiniPC) |
| `%GPU_NODE_IP%` | `192.168.1.139` (PC Gaming "INFINITY") |
| `%DEV_HOST_IP%` | `192.168.1.190` (LXC 190) |

## Porte Backend

| Porta | Backend | Ambiente |
|-------|---------|----------|
| 8080 | Fish S1-mini TTS | fish-speech-env |
| 8081 | Fish Voice Cloning (VQGAN) | fish-speech-env |
| 8082 | HTTP Asset Server (WAV output) | Orchestratore (Livello 0) |
| 8083 | Qwen3-TTS | qwen3tts |
| 8085 | LLM (futuro) | envs/llm |

## CUDA e sm_120 (RTX 5060 Ti — Architettura Blackwell)

**Problema**: PyTorch standard <2.7 non supporta sm_120. Il VQGAN di Fish crasha con `CUDA error: no kernel image`.

**Regola:**
- Qwen3: `torch >= 2.6.0` → `--index-url https://download.pytorch.org/whl/cu124`
- Fish + LLM: `torch >= 2.7.0` → `--index-url https://download.pytorch.org/whl/cu128`

**Non usare** `conda create --name` (crea in miniconda globale). **Usare sempre** `conda create --prefix %ARIA_ROOT%\envs\nome` (project-local).

## Come l'Orchestratore Avvia i Backend

L'Orchestratore non usa `conda activate`. Chiama direttamente il `python.exe` del backend come subprocess con finestra CMD visibile:

```python
# orchestrator.py → ModelProcessManager._build_cmd()
if model_id == "qwen3-tts-1.7b":
    python = aria_root / "envs" / "qwen3tts" / "python.exe"
    # avviato con subprocess.Popen() → finestra CMD visibile sul desktop
```

Backend spenti automaticamente dopo 45 min di inattività (`IDLE_TIMEOUT_S`).

## Bootstrap Cold (Nuovo Nodo GPU)

1. `git clone` del repo
2. Installa Miniconda globale
3. Crea ambienti con `conda create --prefix ...`
4. Installa dipendenze con PyTorch corretto per sm_120
5. Scarica modelli: `huggingface-cli download fishaudio/openaudio-s1-mini ...`
6. Avvia: `Avvia_Tutti_Server_ARIA.bat`

Template YAML disponibili in `envs/templates/` per ricostruzione rapida.

## Vedi anche

- [[stack-aria]] — sistema ARIA completo
- [[concepts/aria-tts-backends]] — confronto Fish vs Qwen3
- [[concepts/aria-redis-protocol]] — come i backend vengono invocati
