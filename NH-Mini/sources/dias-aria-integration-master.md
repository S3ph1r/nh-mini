---
title: "DIAS-ARIA Contratto Integrazione v3.0"
type: source
tags: [dias, aria, ace-step, contratto, sound-on-demand]
sources: []
updated: 2026-04-24
---

# DIAS-ARIA Contratto Integrazione v3.0

**File raw:** `sviluppi/dias/docs/dias-aria-integration-master.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/dias-acestep-contract]], [[concepts/dias-sound-design]]

## Takeaway chiave

- ACE-Step 1.5 XL SFT è l'**unico** modello per tutti gli asset (PAD/AMB/SFX/STING) — confermato
- Queue Redis: `aria:q:mus:local:acestep-1.5-xl-sft:dias` — naming conforme al contratto ARIA
- Vocabolario Qwen3 obbligatorio: tabella vietato/ammesso con 10+ sostituzioni (documentata in [[concepts/dias-acestep-contract]])
- HTDemucs stem separation per PAD: 4 stem (bass/drums/vocals/other) → Stage E gestisce dinamicamente
- ATTENZIONE: il contratto DIAS-ARIA NON usa il Service Registry — è Sound-on-Demand diretto

## Note di integrazione

- I parametri `guidance_scale` differenziati per tipo (PAD=4.5, AMB/SFX=7.0, STING=6.0) non sono arbitrari — bilanciamento tra coerenza e precisione del tipo di asset
- `inference_steps=60` (default PAD): non modificare senza benchmark comparativo
- Il campo `canonical_id` è la chiave per l'idempotenza — se esiste già un asset con quel canonical_id, non viene rigenerato
