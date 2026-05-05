---
title: "ARIA — Confronto Backend TTS (Fish vs Qwen3)"
type: concept
tags: [aria, tts, fish, qwen3, backend, voice]
sources: [aria-fish-tts-backend.md, aria-qwen3-tts-backend.md, aria-environments-setup.md]
updated: 2026-05-01
---

# ARIA — Confronto Backend TTS (Fish vs Qwen3)

ARIA espone due backend TTS complementari. La scelta dipende dal contesto della scena.

## Confronto Rapido

| Criterio | Fish S1-mini | Qwen3-TTS 1.7B |
|----------|-------------|----------------|
| **Uso ideale** | Dialoghi emotivi, voci espressive | Narrazione calda, audiolibri lunghi |
| **Controllo stile** | Emotion markers espliciti `(scared)` | Istruzioni in prosa inglese naturale |
| **Qualità su testi lunghi** | ⚠️ Richiede chunking aggressivo | ✅ Eccellente, stabile |
| **Architettura** | Dual-AR (Semantic + Acoustic) | LLM Transformer + DAC Codec |
| **Python** | 3.10 (cu128) | 3.12 (cu124) |
| **Porta** | 8080 (TTS) + 8081 (Cloning) | 8083 |
| **VRAM** | ~3-4 GB | ~4-5 GB |
| **Sample rate output** | 44.1 kHz mono | 24 kHz mono |
| **Coda Redis** | `...fish-s1-mini:...` | `...qwen3-tts-1.7b:...` |
| **Stato** | 🔄 Da ricreare (sm_120) | ✅ Operativo |

---

## Fish S1-mini

### Architettura (Dual-AR)

```
testo + ref audio → AR-1 Semantic ("cosa dire") → AR-2 Acoustic ("come suona") → DAC → WAV
```

### Emotion Markers

50+ tag posizionati **prima** della parola target:

```
(scared)La porta era socchiusa... (whispering)qualcuno ci osservava.
```

| Tag | Effetto |
|-----|---------|
| `(scared)` | Voce tremante, accelerata |
| `(whispering)` | Volume basso, intimità |
| `(serious)` | Tono profondo, misurato |
| `(nervous)` | Leggero tremito |
| `(sighing)` | Respiro udibile |
| `(panicked)` | Voce alta, concitata |
| `(hesitating)` | Pause, incertezza |

### Workaround Critici

- **Glitch primo token**: Fish ha un artefatto sonoro sul primo token. Soluzione: l'Orchestratore inietta `(break)` all'inizio di ogni chunk.
- **VQGAN su CPU**: se PyTorch non supporta sm_120, impostare `DEVICE="cpu"` in `voice_cloning_server.py`. Più lento ma funzionante.
- **PyTorch obbligatorio**: `torch==2.7.0 --index-url https://download.pytorch.org/whl/cu128`

---

## Qwen3-TTS 1.7B

### Architettura (LLM → DAC)

```
testo + istruzione stile + ref audio → LLM Transformer 1.7B (12 token/s) → DAC → WAV
```

### Istruzioni in Prosa (Instruct)

```python
# ✅ Corretto: prosa narrativa in inglese
"Warm Italian male voice, professional audiobook narrator, calm and measured pace."

# ❌ Sbagliato: etichette tecniche
"Tone: warm, speed: slow"
```

### Parametri reali del server — TTSRequest schema [NEW - 2026-05-01]

Il server Qwen3 (porta 8083) accetta i seguenti parametri via `/tts`:

**Layer LLM** (controlla semantica e variabilità generativa):

| Parametro | Default | Note |
|-----------|---------|------|
| `instruct` | `"Warm Italian male voice..."` | Canale primario. Prosa in inglese. |
| `temperature` | 0.7 | Variabilità LLM. Range narrazione: 0.6–0.8 |
| `top_p` | 0.9 | Nucleus sampling |
| `repetition_penalty` | 1.1 | Riduce ripetizioni — raramente da toccare |
| `max_new_tokens` | 4096 | Limite token audio |

**Layer Acoustic** (controlla prosodia e dettaglio fonetico — indipendente dal LLM):

| Parametro | Default | Note |
|-----------|---------|------|
| `subtalker_temperature` | 0.4 | Variabilità prosodia acustica. 0.35 = stabile, 0.65 = espressivo |
| `subtalker_top_k` | 50 | Acoustic token sampling |
| `subtalker_top_p` | 0.9 | Acoustic nucleus sampling |

**Cosa Stage D invia effettivamente** (verificato da codice, maggio 2026):
`instruct`, `temperature`, `subtalker_temperature`, `top_p`. Gli altri usano i default del server — appropriati per narrazione.

**Nota su `subtalker_temperature`**: Stage D lo fissa a 0.75 in modalità theatrical. Valore troppo alto per narrazione stabile — proposta: linkarlo ad `arousal` da Stage B con formula `0.3 + (arousal * 0.4)`. Vedi [[concepts/dias-voice-pipeline-quality]].

---

### [OBSOLETO - 2026-05-01] Preset per Emozioni DIAS

> **Perché obsoleto**: questa tabella descriveva un meccanismo di fallback "ARIA side" (emotion → instruct) che non è mai stato implementato in Stage D. Stage D usa `message.get("qwen3_instruct") or default_instruct` dove `default_instruct` è una stringa fissa da config — non una mappa per emozione. Il canale corretto per il controllo emotivo è `qwen3_instruct` generato dal prompt LLM di Stage C. Vedi proposta P3 in [[concepts/dias-voice-pipeline-quality]].

| primary_emotion (DIAS) | Instruct |
|---|---|
| `neutral` | `"Warm male voice, Italian audiobook narrator, calm..."` |
| `suspense` | `"...tense and restrained, slightly slower, hushed intensity."` |
| `fear` | `"...anxious and cautious, slow deliberate, quiet."` |
| `sadness` | `"...melancholic and reflective, slow pace, soft."` |

### Auto-Padding (Bleeding Fonetico)

```
ref.wav → [finisce bruscamente] → artefatti nel generato
ref_padded.wav → [audio + 0.5s silenzio] → generato pulito ✅
```

Il server Qwen3 genera `ref_padded.wav` automaticamente con ffmpeg se non esiste.

### Variante Modello

Usare **esclusivamente** `Qwen3-TTS-12Hz-1.7B-Base`:
- ❌ `0.6B-Base` — bug long-silence
- ✅ `1.7B-Base` — `qwen3-tts-1.7b`
- ✅ `1.7B-CustomVoice` — `qwen3-tts-1.7b-customvoice` (6GB VRAM)

---

## Voice Library Condivisa

Entrambi i backend condividono la stessa library, ma usano file diversi:

```
%ARIA_ROOT%\data\voices\{voice_id}\
  ref.wav            ← usato da Fish TTS
  ref_padded.wav     ← usato da Qwen3 TTS (auto-generato se mancante)
  ref.txt            ← trascrizione (ICL ad alta fedeltà)
```

Voci disponibili: `angelo`, `luca`, `roberto`, `stella`, `fabrizio`, `francesco`, `giannini`, `harley`, `ilaria`, `jennifer`, `meredith`, `pino`, `rick`, `wednesday`, `gandalf`, `eleven`.

Per creare nuove voci: `python scripts/voice_prepper.py "URL_YouTube" "nome_voce"`

### Logica Priorità Voce (Stage D di DIAS)

1. **Casting personaggio** (da `preproduction.json`) — massima priorità
2. **Global Voice** (da Dashboard, per narrazione e personaggi non mappati)
3. **System Default** — `luca`

---

## Job ID nel Payload (Critical)

Il campo `job_id` nel payload interno è **obbligatorio** per garantire il "Remote Skip" di DIAS:

```json
{
  "payload": {
    "job_id": "Moby-Dick-chunk-001-scene-002",  // ← OBBLIGATORIO
    "text": "Il mare era calmo quel mattino...",
    "voice_id": "luca"
  }
}
```

Se omesso, il backend genera un UUID casuale — il file WAV non è rintracciabile deterministicamente.

## Vedi anche

- [[stack-aria]] — sistema ARIA completo
- [[concepts/aria-environments]] — ambienti Python e setup
- [[concepts/aria-redis-protocol]] — nomenclatura code e schema payload
- [[concepts/dias-sound-design]] — come DIAS usa TTS
