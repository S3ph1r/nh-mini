---
title: "Lifelog2 — Turn-Level Classification"
type: concept
tags: [lifelog2, classification, diarization, pipeline, stage-c]
sources: []
updated: 2026-06-24
---

# Lifelog2 — Turn-Level Classification

## Il Problema

Lo stage C di Lifelog2 assegna una `conversation_type` all'intero segmento audio: `real_dialogue`, `personal_mono`, `media_passive`, `hybrid`, `ambient_voices`, `unknown`. Questo funziona bene per segmenti omogenei, ma fallisce quando un singolo segmento contiene contenuto misto — per esempio, una conversazione personale **e** un notiziario radio.

Il caso emblematico è l'atom **"Dolci, politica e chiacchiere"** del 2025-12-17:
- Roberto esce dal turno di notte, saluta i colleghi (dialogo reale)
- Sale in macchina, l'autoradio trasmette un notiziario (media passivo)
- Si ferma dal barista, compra bomboloni (dialogo reale breve)

WhisperX diarizza il tutto assegnando label `SPEAKER_00` sia al presentatore radio (198 parole, 85.9s) sia al barista (8 parole). Il sistema vedeva solo metriche aggregate: `avg_other_turn_s ≈ 33s` — al di sotto della soglia `media_passive` di 60s — e classificava il segmento come `real_dialogue`. Questo inquinava il Day Digest: il notiziario radio veniva erroneamente incluso nella sezione "vita personale" di Roberto.

## Il Limite della Diarizzazione

WhisperX assegna label (`SPEAKER_00`, `SPEAKER_01`, …) per cluster vocale. Lo stesso label può essere usato per:
- Il barista che dice "buongiorno" (8 parole)
- Il conduttore radiofonico che legge 3 minuti di notizie

Non c'è distinzione di identità. Senza voiceprint enrollment per ogni persona, il sistema non può sapere se `SPEAKER_00` è un collega o uno speaker TV.

## Tre Casi Fondamentali

| Caso | Struttura audio | Come distinguerlo |
|------|----------------|-------------------|
| 1 | Io 5s → interlocutore risponde 4m55s | Turno vicino a Roberto (gap < 30s), contesto dialogico |
| 2 | Io 5s → telegiornale 4m55s | Turno lungo isolato (gap pre > 15s, gap post > 30s), nessuna risposta Roberto |
| 3 | Io 5s → interlocutore 1m → radio 2m → interlocutore 1m | Mix: primo e terzo turno hanno contesto dialogico, secondo turno lungo e isolato |

I casi 1 e 2 sono indistinguibili **senza voiceprint** se l'interlocutore parla a lungo. La durata + il contesto (Roberto risponde?) è la nostra proxy principale.

## La Soluzione: Annotazione per Turno

Invece di classificare solo il segmento, classichiamo ogni singolo turno diarizzato con una `turn_class`. Il codice è in `_annotate_turn_classes()` nello [[stack-nh-mini]].

### Classi Assegnate per Turno

| Classe | Significato |
|--------|-------------|
| `personal` | Turno di Roberto (voiceprint match) |
| `media_passive` | Turno lungo isolato: durata ≥ 45s, nessuna risposta Roberto entro 30s, nessuna parola di Roberto nei 15s precedenti |
| `dialogue_likely` | Turno vicino a Roberto: gap_pre < 15s **oppure** Roberto risponde entro 30s |
| `ambiguous` | Turno non lungo ma isolato — la semantica (Stage D) dovrà risolvere |

### Costanti e Soglie

```python
_MEDIA_DUR_MS   = 45_000   # durata minima per sospettare media passivo
_RESPONSE_WIN_MS = 30_000  # Roberto risponde entro questo tempo → è dialogue
_GAP_PRE_MS      = 15_000  # Roberto parlava poco prima → è dialogue
```

### Algoritmo

Per ogni turno non-Roberto:
1. Calcola `gap_pre` = ms dall'ultimo turno di Roberto a inizio di questo turno
2. Calcola `gap_post` = ms dalla fine di questo turno al prossimo turno di Roberto
3. `in_dialogue_context = (gap_pre < 15s OR gap_post < 30s)`
4. Se `NOT in_dialogue_context AND dur >= 45s` → `media_passive`
5. Se `in_dialogue_context` → `dialogue_likely`
6. Altrimenti → `ambiguous`

## Il Fix alla Metrica Aggregata

L'`avg_other_turn_s` era vulnerabile ai turn brevi (barista, colleghi) che abbassavano la media nascondendo il turn radio lungo. Fix: aggiunta `max_other_turn_s` in `_compute_conversation_metrics()`.

Regola nuova in `_classify_conversation_type()`:
```python
# Hybrid: max_other_turn_s > 45s cattura l'outlier mascherato dalla avg
if max_t > 45 and avg_t < 60:
    return "hybrid", 0.75
```

`hybrid` indica: il segmento contiene **sia dialogo reale sia media embedded**. Riceve `analysis_tier=2.0` (uguale a `real_dialogue`) perché merita arricchimento completo in Stage D.

## Dove Vivono i Dati

- **DB**: `speaker_turns.turn_type` — stringa `personal|media_passive|dialogue_likely|ambiguous|NULL`
- **MinIO** (`transcripts/raw/.../segment_id.json`): ogni oggetto in `speaker_turns[]` ha il campo `turn_class`; il blob ha anche `turn_classes: {classe: count}` come riepilogo
- **Redis** (`lifelog:stream:c_done`): campo `max_other_turn_s` aggiunto al payload per Stage D

## Limitazioni Attuali

1. **Ambiguous non risolto**: i turni `ambiguous` (brevi, isolati) restano non classificati fino a Stage D. Stage D potrebbe usare la coerenza semantica per distinguere un collega che dice una frase secca da un DJ radiofonico.
2. **Interlocutore lungo**: un vero interlocutore che parla 5 minuti uninterrotto (caso 1) è identico a un podcast 5 minuti (caso 2). Senza voiceprint, la sola durata non basta.
3. **Voiceprint enrollment futuro**: quando le persone della cerchia di Roberto saranno enrollate, si potrà sostituire `dialogue_likely` con `dialogue_confirmed:Mario` e `media_passive` sarà residuale per speaker non identificati + lunga durata.

## Impatto a Valle

- **Stage D** (`stage_d_enrichment.py`): può filtrare i turni `media_passive` dal riepilogo personale e includerli solo nella sezione ambient dell'atom. Da implementare.
- **Day Digest**: l'`hybrid` conversation_type dovrebbe in futuro guidare la separazione del contenuto personale da quello media dentro l'atom. Attualmente non ancora usato a valle.
- **Backfill**: gli atom esistenti hanno `speaker_turns.turn_type = NULL`. Possibile backfill leggendo i blob MinIO ed eseguendo `_annotate_turn_classes()` offline, ma non prioritario.

## Vedi Anche

- [[stack-lifelog2]] — stack tecnico completo
- [[lifelog2-quality-gate]] — il gate Stage C1 che determina cosa va in Stage D
- [[lifelog2-thread-consolidation]] — come gli episodi vengono raggruppati
- [[concepts/lifelog2-refactor-roadmap]] — roadmap refactor 2026-06-24: il gap del Case 3 (interleaved media) ha motivato Fase 1 (Confidence Score) e Fase 3 (Stage D Thread-Aware)
