---
title: "ARIA ASR Finalization & Autonomous Auth"
type: source
tags: [aria, asr, minio, sops, blackwell]
sources: [node_settings.json, asr_pipeline.py, server.py]
updated: 2026-05-10
---

# ARIA ASR Finalization & Autonomous Auth

**File raw**: `sviluppi/ARIA/backends/lifelog_asr/`
**Data ingest**: 2026-05-10
**Pagine toccate**: [[entities/systems/stack-aria]], [[entities/systems/stack-lifelog2]]

## Takeaway chiave

- **Autonomia Storage**: Integrazione client `minio` in ARIA per bypassare errori 403. Accesso autenticato automatico agli asset WAV.
- **Sicurezza**: Credenziali MinIO rimosse dal codice e centralizzate in `node_settings.json` (gestito via Tray Icon) e iniettate JIT via environment variables.
- **Compatibilità Lingua**: Mappatura automatica ISO 639-1 (es. `it` -> `Italian`) per compatibilità trasparente tra pipeline Lifelog2 e Qwen3-ASR.
- **Blackwell Optimization**: Pipeline operativa in BF16 su `sm_120`, risolti conflitti `WeightsUnpickler` con Torch 2.11+.

## Note di integrazione

- Il sistema è ora in grado di smaltire backlog massivi di trascrizione senza intervento manuale.
- Le impostazioni di rete (MinIO IP 192.168.1.104) sono persistite localmente sul nodo ARIA ma sincronizzabili via SOPS.
