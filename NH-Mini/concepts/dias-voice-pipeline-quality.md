---
title: "DIAS — Qualità Pipeline Voce v1"
type: concept
tags: [dias, qualità, tts, qwen3, prompt, pipeline, analisi]
sources: [dias-voice-pipeline-quality.md]
updated: 2026-05-01
---

# DIAS — Qualità Pipeline Voce v1

Analisi qualitativa della pipeline voce-only (Stage 0→A→B→C→D). Versione 1 — musica, ambient, SFX esclusi.

**Documento sorgente completo:** `sviluppi/dias/docs/dias-voice-pipeline-quality.md`

---

## Obiettivo v1

Audiolibro professionale con massima qualità di narrazione e dialoghi. Il bar è "production studio", non "testo letto ad alta voce".

Il vincolo architetturale più importante: **Qwen3-TTS 1.7B è zero-shot amnesico** — ogni scena deve portare con sé tutto il contesto vocale nel campo `qwen3_instruct`. Non ricorda la scena precedente. Questo vincolo guida ogni scelta progettuale degli stage upstream.

---

## Catena dell'informazione verso il WAV

```
Stage 0.2 → vocal_profile fisico personaggio
               ↓
Stage C → qwen3_instruct[anchor] = vocal_profile tradotto in acustico inglese
               ↓  (costante per personaggio, invariato per tutto il libro)

Stage B  → narrator_base_tone + speaking_style per-scena + tension/arousal/valence
               ↓
Stage C → qwen3_instruct[direction] = stato emotivo specifico della battuta
               ↓  (varia scena per scena)

Stage C → clean_text = verbatim + correzioni fonetiche TTS
               ↓

Qwen3-TTS → WAV singolo
```

Il meccanismo del `vocal_profile` → `anchor` è il pezzo più intelligente del sistema: risolve il problema dell'identità vocale in un TTS amnesico senza richiedere fine-tuning per personaggio.

---

## Struttura qwen3_instruct

Struttura obbligatoria: `[Vocal anchor]. [Acting direction].`

| Tipo scena | Anchor | Direction |
|-----------|--------|-----------|
| Dialogo | Da `vocal_profile` del dossier (fisico, invariante) | Stato emotivo del personaggio in questa battuta |
| Narrazione | Libero, varia scena per scena | Emozione dominante della scena |
| Pensiero interiore | "hushed, inward voice" o "internalized whisper" | Conflitto o dubbio interiore |

---

## Valutazione qualitativa (aprile 2026)

### Cosa funziona bene

- `vocal_profile` fisico → anchor: meccanismo corretto per TTS amnesico
- `speaking_style` per-scena da Stage B: variazione emotiva corretta per personaggio
- `narrator_base_tone` con fallback quality-floor: qualità minima garantita
- `subtext` e `narrative_arc` come contesto direzionale: livello di analisi raro
- Segmentazione tipografica stretta: correttezza dialogo/narrazione/pensiero

### Gap identificati e stato

| Gap | Priorità | Stato |
|-----|---------|-------|
| `book_language` hardcoded "ITALIANO" in Stage B | Alta | ✅ Risolto — Stage B v1.3.0 |
| Pause semantiche uniformi (100-200ms piatte) | Alta | ✅ Risolto — Stage C v2.5.0 tassonomia 6 livelli |
| `valence`/`arousal`/`tension` non usati da Stage C | Media | 🟡 Parziale — esposti nel PROMPT CONTEXT come testo sì (v2.5.0), ma `_generate_voice_direction()` non li usa come float per calcolare parametri audio → P4 |
| Stage B senza contesto globale da Stage 0 | Alta | ✅ Risolto — Stage B v1.4.0 iniezione CONTESTO OPERA |
| `has_dialogue = true` per scene Narratore | Bassa | 🟡 Aperto — dipende da come Stage D usa il campo |
| Name matching fragile speaker → casting | Media | 🟡 Aperto — fuzzy match cognome da implementare |

---

## Tassonomia pause (da Stage C v2.5.0)

Le pause tra i WAV sono l'unico parametro di timing che Stage C controlla. Il loro impatto percettivo è significativo:

| Range | Contesto semantico |
|-------|-------------------|
| 50–100ms | Battute ravvicinate stesso scambio dialogico |
| 100–200ms | Fine battuta → Narratore di cornice ("disse lui") |
| 200–350ms | Narratore cornice → nuova battuta |
| 400–600ms | Fine paragrafo; cambio scena; stacco emotivo |
| 800–1500ms | Stacco narrativo importante; fine sequenza |
| 2000ms | Titolo capitolo/sezione |

Regola: alta tensione/arousal → pause più brevi. Scena riflessiva → pause più lunghe.

---

## Analisi Parameter Flow Stage C→D→Qwen3 [NEW - 2026-05-01]

Analisi del codice reale su CT201 (maggio 2026). Scoperte rilevanti per la qualità dell'output audio.

### Dead code confermato

`_generate_voice_direction()` in Stage C genera tre campi nel JSON di output che **non vengono mai letti** da Stage D né da Stage F:

| Campo | Generato da | Consumato da | Stato |
|-------|-------------|--------------|-------|
| `pace_factor` | Stage C lookup table | nessuno | ❌ Dead code |
| `pitch_shift` | Stage C lookup table | nessuno | ❌ Dead code |
| `energy` | Stage C lookup table | Stage D (solo se `enable_dynamic_params=True`) | ⚠️ Bloccato |

`enable_dynamic_params` in Stage D è `False` hardcoded (`getattr(self, "enable_dynamic_params", False)`) — quindi anche `energy` è di fatto inutilizzato.

**Diagnosi**: `pace_factor` e `pitch_shift` sono design artifact di un'era pre-Qwen3, quando si ipotizzava un TTS con parametri espliciti di velocità/intonazione o un layer di post-processing audio (ffmpeg `atempo`/`rubberband`). Con Qwen3, questi concetti si esprimono via `instruct` in prosa naturale — non via parametri numerici. Non sono "feature future da completare": sono un vicolo cieco architetturale da eliminare.

### I due canali verso Qwen3

Il pipeline Stage C→D→Qwen3 ha due canali distinti con impatto molto diverso:

| Canale | Campo | Impatto | Chi lo popola |
|--------|-------|---------|--------------|
| **Semantico (primario)** | `instruct` | Alto — Qwen3 legge e interpreta la prosa | LLM in Stage C prompt |
| **Variabilità LLM (secondario)** | `temperature` | Basso — range 0.6–0.8 | Stage D via `energy` |
| **Prosodia acustica** | `subtalker_temperature` | Medio — variazione fonetica | Stage D theatrical config |

### Problema subtalker_temperature

Stage D in modalità theatrical fissa `subtalker_temperature = 0.75`. Questo valore è **troppo alto** per narrazione stabile: controlla la variabilità del layer acustico (prosodia), e 0.75 può causare inconsistenza fonetica tra frasi consecutive.

Soluzione proposta: linkarlo ad `arousal` da Stage B: `subtalker_temp = 0.3 + (arousal * 0.4)`.
- arousal=0.2 (scena meditativa) → 0.38 (stabile, piatto)
- arousal=0.8 (scena intensa) → 0.62 (dinamico, espressivo)

### Proposte approvate (maggio 2026)

| ID | Dove | Cosa | Stato |
|----|------|------|-------|
| **P3** | Stage C prompt YAML | Per-scene `primary_emotion` dal LLM (v2.6.0) | ✅ Deployed 2026-05-02 |
| **P4** | Stage C `_generate_voice_direction()` | Formula da Stage B floats: `energy = 0.4 + (arousal * 0.5)`, `subtalker_temp = 0.3 + (arousal * 0.4)` | ✅ Deployed 2026-05-02 |
| **P5** | Stage C Python | Rimossi `pace_factor` e `pitch_shift` dall'output | ✅ Deployed 2026-05-02 |
| **P1** | Stage D `__init__` | `self.enable_dynamic_params = True` | 🚫 Superceded — Stage C scrive `temperature` top-level, Stage D la legge via `message.get()` senza toccare `enable_dynamic_params` |
| **P2** | Stage C lookup table | ~~Espandere a 12 emozioni~~ | 🚫 Skipped — P4 rende redundante |

**Perché P2 è stato skippato**: la lookup table agisce solo su `temperature` via un mapping discreto (stringa emozione → float). P4 usa i float continui di Stage B che funzionano per qualsiasi emozione senza dover mantenere un dizionario. P2 avrebbe avuto zero impatto su `instruct` (il canale primario).

---

## Audit end-to-end produzione (2026-05-03)

Verifica completa del flusso parametri in produzione su Hyperion (post P3+P4+P5).

### Server Qwen3 di produzione

Il server attivo è `C:\Users\Roberto\aria\backends\qwen3tts\server.py` (v1.0.0), avviato dall'orchestratore ARIA con:
```
python.exe C:\Users\Roberto\aria\backends\qwen3tts\server.py --model-path ... --port 8083
```
Il file `C:\Users\Roberto\aria\scripts\qwen3\qwen3_server.py` è un backup/bozza obsoleta non in produzione.

### Flusso parametri confermato ✅

| Parametro | Stage D invia | ARIA invia al server | Modello riceve |
|---|---|---|---|
| `instruct` (qwen3_instruct) | ✓ per-scena da Stage C v2.6.0 | ✓ | ✓ |
| `temperature` | ✓ calcolata da arousal (P4) | ✓ | ✓ |
| `top_p` | ✓ 0.9 | ✓ | ✓ |
| `subtalker_temperature` | ✓ calcolata da arousal (P4) | ✓ | ✓ |
| `subtalker_top_k` | ✗ non inviato | ✓ default 50 | ✓ |
| `subtalker_top_p` | ✗ non inviato | ✓ default 0.9 | ✓ |
| `voice_ref_audio_path` | ✗ | ✓ risolto da voice_id → ref_padded.wav | ✓ |
| `voice_ref_text` | ✗ | ✓ auto-letto da ref.txt (ICL mode) | ✓ |
| `language` | ✗ non inviato | ✓ default "Italian" | ✓ |

### Gap residuo: `dialogue_notes` enrichment (morto)

ARIA ha un meccanismo di arricchimento instruct per le scene di dialogo:
```python
if dialogue_notes and payload.get("has_dialogue", False):
    instruct = f"{instruct} Character notes: {dialogue_notes}"
```
Non scatta mai per due motivi sovrapposti:
1. Stage C produce sempre `dialogue_notes: null`
2. Stage D non forwarda `has_dialogue` né `dialogue_notes` nel payload ARIA

**Impatto**: basso. Il contesto personaggio è già sintetizzato da Gemini dentro `qwen3_instruct` a Stage C. La feature ha senso in uno scenario multi-voce futuro dove `qwen3_instruct` non può portare da sola tutta la caratterizzazione.

---

## Priorità sviluppo qualitativo v1

1. ~~P3 — Per-scene instruct~~ ✅ Deployed (Stage C v2.6.0)
2. ~~P4+P5 — Parameter flow + dead code cleanup~~ ✅ Deployed (2026-05-02)
3. **Validare Stage C v2.6.0** — produrre campioni Hyperion e confrontare con v2.5.0
4. **Fix name matching** (Gap V1-4) — analisi mismatch speaker → casting su Hyperion
5. **Audit vocal_profile Stage 0** — verificare specificità profili su libri reali
6. **narrator_base_tone a granularità micro** — attualmente uguale per tutti i micro-chunk del blocco
7. **`dialogue_notes` enrichment** — richiede: Stage C popola `dialogue_notes`, Stage D forwarda `has_dialogue` + `dialogue_notes`; priorità bassa finché casting è mono-voce

---

## Vedi anche

- [[concepts/dias-prompt-evolution]] — registro versioni prompt con rationale
- [[concepts/dias-stage0-preproduction]] — come vengono prodotti vocal_profile e casting
- [[concepts/dias-pipeline]] — flusso dati completo dei 10 stadi
- [[stack-dias]] — sistema DIAS completo
