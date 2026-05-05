---
title: "DIAS Technical Reference"
type: source
tags: [dias, deployment, redis, sops, sicurezza, systemd]
sources: []
updated: 2026-04-24
---

# DIAS Technical Reference

**File raw:** `sviluppi/dias/docs/technical-reference.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-dias]], [[concepts/dias-prompt-evolution]]

## Takeaway chiave

- Sicurezza: SOPS+Age standard NH-Mini — credenziali via `core/secure_credential_manager.py`
- DIAS tende a delegare le API key ad ARIA — DIAS non possiede API key Google dirette
- Redis produzione (LXC 120): maxmemory=2GB, policy=allkeys-lru, snapshot ogni 60s
- Deployment come servizi systemd (User=dias, Restart=always)
- Prompt esternalizzati in `config/prompts/` — cambio prompt senza toccare il codice

## Configurazione Redis LXC 120

```
maxmemory: 2GB
policy: allkeys-lru
persistence: save 60 10000
```

## Health Checks

```bash
redis-cli ping                              # Redis attivo?
redis-cli llen dias:queue:1:ingestion       # Monitor code
tail -f /var/log/dias/stage_a.log           # Log stage
```

## Note di integrazione

- Il pattern di delega API key ad ARIA riduce la superficie di attacco: solo ARIA gestisce le credenziali Google
- Le versioni interne dei prompt (es. v4.2 interna per `b2_macro_v4.0.yaml`) sono documentate in questo file nella sezione 4 — fonte autorevole per versioning
- `MOCK_SERVICES=false` per produzione, `true` per sviluppo offline
