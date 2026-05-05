---
title: "ARIA Service Registry & Universal Discovery v1.0"
type: source
tags: [aria, registry, discovery, redis]
sources: []
updated: 2026-04-24
---

# ARIA Service Registry & Universal Discovery v1.0

**File raw:** `sviluppi/ARIA/docs/ARIA-Service-Registry.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-aria]]

## Takeaway chiave

- ARIA pubblica su Redis `aria:registry:master` un catalogo dinamico di backend attivi e asset disponibili (voci, modelli, personas)
- Ogni asset ha `data/assets/{tipo}/{id}/profile.json` con schema standardizzato
- PC 139 è il SOT per i dati (modelli, voci audio). LXC 190 è il SOT per la logica del registro.
- Git sync: commits su LXC 190 + `git pull` su PC 139 — Git ignora i file pesanti (`.gitignore`)
- **ATTENZIONE**: `git push --force` da LXC 190 è vietato senza verifica che PC 139 sia allineato

## Note di integrazione

- Il Service Registry è per la discovery di backend e asset geneerali (voci per TTS, LLM per analisi)
- Il contratto DIAS-ARIA Sound-on-Demand **NON usa** il registry → vedi [[concepts/dias-acestep-contract]]
- Il catalog `aria:registry:master` viene ricostruito ad ogni avvio dell'orchestratore
