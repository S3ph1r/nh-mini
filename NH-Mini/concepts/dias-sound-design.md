---
title: "DIAS — Paradigma Sound Design BBC/Star Wars"
type: concept
tags: [dias, sound-design, bbc, audio, pad, sfx, mixing]
sources: [dias-blueprint.md, dias-production-standard.md]
updated: 2026-04-24
---

# DIAS — Paradigma Sound Design BBC/Star Wars

**Principio fondamentale**: il silenzio è il default. Un suono deve guadagnarsi il diritto di esistere.

La voce e i dialoghi sono i protagonisti assoluti. La musica PAD è un personaggio invisibile che respira con la narrazione. AMB, SFX e STING sono punteggiatura rara e precisa.

Benchmark: **BBC Radio Drama anni '80** + **Star Wars Audio Drama (NPR, 1981)**

## I 4 Layer Audio

### PAD (Tappeto Musicale Continuo)

Prodotto da ACE-Step 1.5 XL SFT. Sempre presente per l'intera durata del capitolo (~8-20 minuti).

[[stack-aria|ARIA]] esegue HTDemucs per separare 4 stem:
- `bass` — frequenze basse
- `drums` — elementi percussivi
- `vocals` — contenuto vocale/coro
- `other` — melodia, pad, archi, tutto il resto

Stage E gestisce i 4 stem dinamicamente via PadArc:
- `low` = solo bass
- `mid` = bass + other
- `high` = bass + other + drums (+ vocals se presenti)

**Ducking depth per scena:**

| Livello | dB | Quando |
|---------|-----|--------|
| `shallow` | -6 dB | scena intensa, voce forte |
| `medium` | -12 dB | narrazione standard (default) |
| `deep` | -18 dB | momento intimo, voce sommessa |

**Fade speed:**

| Speed | Tempo | Quando |
|-------|-------|--------|
| `snap` | 0.3s | cambio improvviso |
| `smooth` | 1s | transizione naturale (default) |
| `slow` | 2.5s | dissolvenza lenta, finali scena |

**Automazione PAD:**
- `ducking` (default) — abbassa durante la voce
- `build` — crescendo verso climax
- `neutral` — volume costante

---

### AMB (Ambiente — cambio di scena)

- Durata: **3-5 secondi** (non è un loop)
- Scopo: segnalare il cambio di ambientazione fisica tra scene consecutive
- **Max 1 per micro-chunk** — spesso zero
- Si applica solo alla scena in cui avviene il cambio
- Esempio: interno → esterno, silenzio → folla

---

### SFX (Effetto Puntuale)

- Durata: **0.3-2 secondi**
- Scopo: evento fisico culminante della scena (l'azione accade, non la preparazione)
- **Max 1 per scena** — meno è meglio
- `sfx_timing`: `start` | `middle` | `end`

---

### STING (Accento Orchestrale)

- Durata: **2-4 secondi**
- Scopo: sottolineatura per rivelazioni narrative irreversibili (svolta, morte, tradimento)
- **Max 1 per micro-chunk** — mai all'inizio di una scena
- `sting_timing`: `middle` | `end` (mai `start`)

---

## Timing ACE-Step (ARIA)

| Asset | Durata output | Tempo generazione |
|-------|--------------|-------------------|
| PAD capitolo | 8-20 minuti | ~4.5 min per 30s output |
| AMB | 3-5 s | ~1-2 min |
| SFX | 0.3-2 s | ~1 min |
| STING | 2-4 s | ~1 min |

Queue Redis: `aria:q:mus:local:acestep-1.5-xl-sft:dias`

---

## Standard Voce: Formula Oscar

Target: qualità sovrapponibile a ElevenLabs con Qwen3-TTS 1.7b.

| Parametro | Valore Target | Effetto |
|-----------|---------------|---------|
| `subtalker_temperature` | **0.75** | Grana umana e sospiri naturali |
| `temperature` | **0.7** | Bilanciamento fedeltà/variazione |
| `top_p` / `top_k` | **0.8+ / 50** | Campionamento stabile |
| `voice_ref_text` | **mandatorio** | Metronomo fonetico — deve corrispondere al `ref_padded.wav` |

---

## Punteggiatura Audio (Stage C)

Regole per preparare il testo prima del TTS:

- **Tratto lungo (` - `)**: pause drammatiche e sospensioni pulite (sostituisce `...` che causano clicking)
- **Virgola extra (`,`)**: forza il respiro naturale
- **CAPS o virgolette**: enfasi su parole chiave
- **Numeri → lettere**: `"2042"` → `"duemilaquarantadue"`
- **Accenti disambiguanti**: solo per parole ambigue (`"pàtina"`, `"scivolò"`)
- **Titoli**: scene dedicate con `pause_after_ms = 2000`

---

## Istruzioni TTS (Stage C → ARIA)

Descrizioni fisiche ed emotive in **inglese, in prosa**. Non comandi tecnici secchi.

✅ Corretto: `"Hushed, inward voice, very slow pace. Private doubt laced with concealed tension."`
❌ Sbagliato: `"voice: slow, emotion: doubt"`

---

## Vedi anche

- [[stack-dias]] — sistema DIAS completo
- [[concepts/dias-pipeline]] — come vengono generati i layer audio nella pipeline
- [[stack-aria]] — ACE-Step e TTS (worker GPU)
