---
title: "ARIA API Contract v1.0"
type: source
tags: [aria, api, redis, contratto, nomenclatura]
sources: []
updated: 2026-04-24
---

# ARIA API Contract v1.0

**File raw:** `sviluppi/ARIA/docs/ARIA-API-Contract.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/aria-redis-protocol]]

## Takeaway chiave

- Questo documento è il **SOT assoluto** per la comunicazione Redis tra ARIA e client
- Pattern code inferenza: `aria:q:{env}:{provider}:{model_id}:{client_id}`
- Pattern code risposta: `aria:c:{client_id}:{job_id}`
- 4 model_id mandatori: `gemini-1.5-flash-lite`, `qwen3-tts-1.7b`, `fish-s1-mini`, `qwen3.5-35b-moe-q3ks`
- Code interne DIAS (`dias:q:*`) NON fanno parte del contratto ARIA

## Note di integrazione

- Il file `backends_manifest.json` è l'anagrafe backend reale — il contratto lo referenzia come SOT per porte e comandi
- L'output è sempre `audio_url` (URL HTTP), mai path filesystem
- Il documento è datato 2026-03-23 — verificare se i model_id si sono aggiornati
