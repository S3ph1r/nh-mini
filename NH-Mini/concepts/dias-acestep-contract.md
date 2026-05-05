---
title: "DIAS↔ARIA — Contratto ACE-Step (Sound-on-Demand v4.1)"
type: concept
tags: [dias, aria, ace-step, contratto, sound-design, redis]
sources: [dias-aria-integration-master.md]
updated: 2026-04-24
---

# DIAS↔ARIA — Contratto ACE-Step (Sound-on-Demand v4.1)

Contratto tecnico tra DIAS (Brain, LXC 190) e ARIA (GPU Worker, PC 139) per la produzione audio.

**Filosofia: Sound Factory JIT (Just-In-Time)**. Non esiste catalogo pre-prodotto, non esiste matching semantico su Redis. Ogni asset viene prodotto ex-novo su richiesta.

## Modello AI: ACE-Step 1.5 XL SFT (Unico)

| Campo | Valore |
|-------|--------|
| **Modello** | ACE-Step 1.5 XL SFT |
| **Hardware** | PC 139, RTX 5060 Ti 16GB VRAM |
| **Queue Redis** | `aria:q:mus:local:acestep-1.5-xl-sft:dias` |
| **Timing PAD** | ~4.5 minuti per 30 secondi di output |
| **Breakdown** | LM ~240s + DiT ~35s |
| **Output types** | `pad` \| `amb` \| `sfx` \| `sting` |

Non si usa MusicGen, AudioLDM, Stable Audio Open o altri modelli. ACE-Step gestisce tutti e quattro i tipi.

## Parametri per Tipo di Asset

| Tipo | `guidance_scale` | `duration_s` | `negative_prompt` |
|------|-----------------|-------------|-------------------|
| PAD | 4.5 (vintage) | durata capitolo (~480-1200s) | `epic, cinematic, generic ai, polished pop` |
| AMB | 7.0 (netto) | 4.0 (range 3-5s) | `music, melody, vocals, rhythm` |
| SFX | 7.0 | 0.5-1.5 (range 0.3-2s) | `music, melody, sustained, ambient` |
| STING | 6.0 | 3.0 (range 2-4s) | `ambient, sustained, loop, background` |

`inference_steps` default: 60. Non modificare senza benchmark.

## Vocabolario Qwen3 (Obbligatorio)

Il LM interno di ACE-Step è Qwen3. Il `production_tags` **deve** usare vocabolario da musicista/fonico. Termini da sound designer causano "prompt drift" (Qwen3 riscrive il prompt e il suono deriva).

| VIETATO | USA QUESTO |
|---------|-----------|
| spring reverb | analog reverb, vintage reverb |
| tape saturation | analog warmth, vintage recording |
| tape delay | vintage echo, analog delay |
| sub-bass drone | deep bass drone, low frequency bass |
| metallic percussive hits | metallic percussion, industrial hits |
| ARP 2600, Moog, Roland 808 | vintage analog synthesizer |
| sidechain compression | (omettere) |
| high-pass filter | (descrivere il risultato sonoro) |

Nomi di synth hardware specifici → descrizione generica del suono risultante.

## Schema SoundShoppingItem (Contratto JSON)

```json
{
  "type": "pad | amb | sfx | sting",
  "canonical_id": "{category}_{description}_{variant_num}",
  "production_prompt": "Descrizione leggibile (fallback/traceability)",
  "production_tags": "Comma-separated EN keywords: genere, strumenti, mood, texture",
  "negative_prompt": "Comma-separated EN exclusions per CFG",
  "guidance_scale": 4.5,
  "duration_s": 30.0,
  "scene_id": "chunk-000-micro-001-scene-003"
}
```

Il `canonical_id` è il campo critico per l'idempotenza: se un asset con quel canonical_id esiste già, viene riusato senza rigenerare.

## HTDemucs: Stem Separation per il PAD

ARIA esegue HTDemucs dopo la generazione ACE-Step del PAD:
- **Input**: WAV master PAD (~8-20 min)
- **Output**: 4 stem — `bass`, `drums`, `vocals`, `other`

Stage E usa i 4 stem dinamicamente:
- `low` → solo `bass`
- `mid` → `bass` + `other`
- `high` → `bass` + `other` + `drums` (+ vocals se presenti)

## Relazione con ARIA Service Registry

Il contratto DIAS-ARIA Sound-on-Demand **NON usa** il Service Registry:
- ❌ No `aria:registry:master`
- ❌ No `profile.json` di catalogazione
- ❌ No matching semantico all'85%

Il Service Registry è per la discovery di backend e asset (voci, LLM). La sound factory usa la coda Redis diretta: `aria:q:mus:local:acestep-1.5-xl-sft:dias`.

## Vedi anche

- [[concepts/dias-sound-design]] — regole qualitative PAD/AMB/SFX/STING (BBC/Star Wars)
- [[concepts/dias-pipeline]] — Stage D2 e Stage E nel flusso
- [[concepts/aria-redis-protocol]] — nomenclatura generale code ARIA
- [[stack-aria]] — sistema ARIA e ACE-Step backend
