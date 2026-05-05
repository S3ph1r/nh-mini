---
title: "DIAS Workflow Logic v10.0"
type: source
tags: [dias, workflow, pipeline, flusso-dati]
sources: []
updated: 2026-04-24
---

# DIAS Workflow Logic v10.0

**File raw:** `sviluppi/dias/docs/dias-workflow-logic.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/dias-pipeline]]

## Takeaway chiave

- Revisione v10.0 — Aprile 2026: la versione più aggiornata del flusso dati
- Il "Master Clock" (Stage D → MasterTimingGrid) è il principio chiave che risolve il disallineamento storico audio AI
- Stage B2 va sempre **dopo** Stage D per leggere durate hardware, non stimarle
- Tre fasi dell'orchestratore B2: Macro → Micro → Aggregazione (sempre in questo ordine)
- Aggregazione deduplica per `canonical_id` → garantisce un solo asset per tipo nel shopping list

## Note di integrazione

- Il flusso semplificato `A → C → D → F` (file `.m4b`) è per produzione rapida senza sound design
- Lo script `run_b2_pipeline.py` è l'orchestratore ufficiale per Stage B2 (Macro + Micro + Aggregazione)
- La struttura directory `data/projects/{project_id}/` è la sandbox isolata per ogni libro
