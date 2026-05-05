---
title: "DIAS Master Inventory v2.0"
type: source
tags: [dias, inventario, codebase, pydantic, modelli]
sources: []
updated: 2026-04-24
---

# DIAS Master Inventory v2.0

**File raw:** `sviluppi/dias/docs/dias-inventory.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-dias]], [[concepts/dias-pipeline]], [[concepts/dias-prompt-evolution]]

## Takeaway chiave

- Inventario tecnico definitivo: file Python, prompt YAML (con versioni), modelli Pydantic, dipendenze
- Moduli `src/common/`: `base_stage.py` (BaseStage foundation), `gateway_client.py` (bridge Redis ARIA), `registry.py` (MasterRegistry), `redis_factory.py` (switch Mock/Produzione)
- File legacy presenti ma non usati: `stage_b2_macro_v3_old.py`, `stage_b2_micro_v3_old.py` — pre-Sound-on-Demand
- Dashboard SvelteKit: `VoiceCarousel.svelte`, `CastingTable.svelte`, `AudioInspector.svelte`, `UploadModal.svelte`

## Modelli Pydantic Chiave (da `src/common/models.py`)

| Modello | Stage | Campi Critici |
|---------|-------|--------------|
| `MasterTimingGrid` | Stage D | `total_duration_seconds`, `macro_chunks{}` — il Master Clock |
| `MacroAnalysisResult` | Stage B | `primary_emotion`, `subtext`, `narrator_base_tone`, `entities_speaking_styles` |
| `SceneScript` | Stage C | `scene_id`, `text_content`, `voice_direction`, `tts_backend` |
| `SoundShoppingItem` | B2-Micro | `canonical_id`, `production_tags`, `guidance_scale`, `duration_s` |

## Note di integrazione

- Il `redis_factory.py` permette sviluppo offline con `MOCK_SERVICES=true` — utile per testare senza Redis/GPU attivi
- Il `MasterRegistry` in `registry.py` gestisce gli stati `PENDING`, `IN_FLIGHT`, `COMPLETED` per l'idempotenza
- Questo file è il riferimento per verificare la versione **interna** di ogni prompt (es. `b2_macro_v4.0.yaml` interno v4.2)
