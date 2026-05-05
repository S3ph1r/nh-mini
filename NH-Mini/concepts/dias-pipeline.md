---
title: "DIAS — Pipeline Stadi (Flusso Dati)"
type: concept
tags: [dias, pipeline, stadi, flusso-dati, audiobook]
sources: [dias-blueprint.md, dias-workflow-logic.md]
updated: 2026-04-24
---

# DIAS — Pipeline Stadi (Flusso Dati)

Mappatura completa della pipeline DIAS v10.0 (Aprile 2026). Pipeline **strettamente seriale**: ogni stadio parte solo dopo che il precedente ha persistito su disco.

## Struttura Directory Progetti

```
sviluppi/dias/data/projects/{project_id}/
  fingerprint.json          ← Stage 0
  preproduction.json        ← Stage 0
  chunks/
    macro/chunk-{N}.json    ← Stage A
    micro/chunk-{N}-{M}.json← Stage A
  analysis/
    chunk_analysis-{N}.json ← Stage B
  scenes/
    scenes-{N}-{M}.json     ← Stage C
  voice/
    {BookID}-chunk-{N}-scenes-{YYYYMMDD_HHMMSS}.wav ← Stage D
  timing/
    master_timing_grid.json ← Stage D
  b2/
    macro-cue-{N}.json      ← Stage B2-Macro
    integrated-cue-{N}-{M}.json ← Stage B2-Micro
  sound_shopping_list_aggregata.json ← Aggregatore B2
  assets/                   ← Stage D2 (WAV da ARIA)
  final/                    ← Stage E (mixdown)
```

## Flusso Completo

### Stage 0 — Intel

**Input:** libro `.epub`/`.txt`
**Output:** `fingerprint.json` + `preproduction.json`

Due sotto-protocolli:
- `0.1`: Discovery strutturale (capitoli, personaggi, ambientazioni)
- `0.2`: DNA creativo + Casting (voce per personaggio, tono narrativo)

Il `preproduction.json` viene letto da tutti gli stage successivi come riferimento creativo.

### Stage A — TextIngester

**Input:** libro `.txt`
**Output:** macro-chunk (~2500 parole) + micro-chunk (~300 parole)

Scomposizione a imbuto: il capitolo viene prima spezzato in macro-chunk narrativi, poi ogni macro-chunk in micro-chunk per scena.

### Stage B — SemanticAnalyzer

**Input:** macro-chunk
**Output:** `ChunkAnalysis` per ogni macro-chunk

Analisi LLM (Gemini) di: `valence` (positivo/negativo), `arousal` (intensità), `tension`. Poi **Mood Propagation**: i valori macro vengono interpolati sui micro-chunk figli.

### Stage C — SceneDirector

**Input:** micro-chunk + `ChunkAnalysis` (Stage B)
**Output:** scenes file (array scene per micro-chunk)

Operazioni chiave:
- **Tag Splitting**: separa fisicamente i tag dialogo (`disse lui`) dalle battute
- **Istruzioni TTS**: in inglese, in prosa (es. `"Hushed, inward voice, very slow pace"`)
- **Segmentazione**: per Emotional Beat, non per lunghezza
- **Normalizzazione fonetica**: numeri → lettere, accenti disambiguanti

### Stage D — VoiceGenerator

**Input:** scenes file (Stage C)
**Output:** WAV fisici + `MasterTimingGrid`

Invia task TTS ad [[stack-aria|ARIA]] via Redis. Riceve URL audio. Scarica e salva WAV. Misura ogni durata al millisecondo → `MasterTimingGrid`.

**Questo è il Master Clock**: da qui in poi le durate sono millisecondi hardware, non stime testuali.

### Stage B2-Macro — Musical Director

**Input:** `ChunkAnalysis` + `MasterTimingGrid` + `preproduction.json`
**Output:** `MacroCue` per ogni macro-chunk

Produce:
- `PadRequest`: canonical_id + production_prompt + production_tags (ACE-Step) + parametri
- `PadArc`: partitura emotiva `{start_s, end_s, intensity, stem_layers}`

Prompt: `b2_macro_v4.0.yaml` (versione interna v4.2)

### Stage B2-Micro — Sound Designer

**Input:** `MacroCue` + scenes + `MasterTimingGrid`
**Output:** `IntegratedCueSheet` per ogni micro-chunk

Due modalità:

**Monolitica (default):**
```
micro-chunk → Gemini → IntegratedCueSheet {scenes_automation + shopping_list}
```

**Split Director/Engineer:**
```
B2-Micro-Director → SoundEventScore (eventi fisici, linguaggio naturale)
B2-Micro-Engineer → IntegratedCueSheet (spec ACE-Step, vocabolario Qwen3)
```

Il vantaggio dello split: la shopping list viene costruita prima delle scenes_automation, rendendo strutturalmente impossibile il `canonical_id mismatch`.

### Aggregatore B2

Raccoglie tutti `SoundShoppingItem` da tutti i `MicroCue` + tutti i `PadRequest` dai `MacroCue`. Deduplica per `canonical_id`.

Output: `sound_shopping_list_aggregata.json` → unico input di Stage D2.

### Stage D2 — Sound Factory Client

**Input:** `sound_shopping_list_aggregata.json`
**Output:** asset audio (PAD, AMB, SFX, STING) via [[stack-aria|ARIA]] ACE-Step

Invia richieste di generazione audio ad ARIA (`aria:q:mus:local:acestep-1.5-xl-sft:dias`). Ogni asset: ~4.5 minuti per 30 secondi generati (LM ~240s + DiT ~35s).

### Stage E — Mixdown

**Input:** WAV Stage D + `IntegratedCueSheet` + `MacroCue` + asset Stage D2
**Output:** traccia finale mixata per capitolo

Processo:
1. Carica WAV voce (Stage D)
2. ARIA esegue HTDemucs su PAD → 4 stem (bass/drums/vocals/other)
3. Assembla PAD dynamicamente via PadArc (low/mid/high)
4. Piazza AMB, SFX, STING sulla timeline assoluta
5. Applica ducking locale per ogni scena

## Flusso B2 Completo (Schema)

```
Stage B (ChunkAnalysis)
  + Stage D (MasterTimingGrid)
  + Stage 0 (preproduction.json)
        ↓
  B2-Macro → MacroCue {PadRequest + PadArc}
        ↓
  B2-Micro → IntegratedCueSheet {scenes_automation + shopping_list}
        ↓
  Aggregatore → sound_shopping_list_aggregata.json
        ↓
  Stage D2 → ARIA ACE-Step → WAV assets
        ↓
  Stage E → traccia finale
```

## Vedi anche

- [[stack-dias]] — sistema DIAS completo
- [[concepts/dias-sound-design]] — regole qualitative PAD/AMB/SFX/STING
- [[stack-aria]] — worker GPU (esegue D e D2)
- [[concepts/aria-redis-protocol]] — contratto Redis ARIA
