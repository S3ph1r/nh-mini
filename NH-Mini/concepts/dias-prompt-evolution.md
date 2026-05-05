---
title: "DIAS — Evoluzione Prompt (Registry Versioni)"
type: concept
tags: [dias, prompt, versioni, llm, gemini, qualità]
sources: [dias-prompt-evolution.md, dias-inventory.md, dias-technical-reference.md]
updated: 2026-04-29
---

# DIAS — Evoluzione Prompt (Registry Versioni)

Registro delle versioni dei prompt DIAS con le lezioni chiave apprese. I prompt vivono in `config/prompts/` — un cambio di prompt non richiede modifiche al codice.

## Versioni Attuali in Produzione

| Stage | File | Versione File | Versione Interna | Stato |
|-------|------|--------------|-----------------|-------|
| 0.1 Discovery | `stage_0/0.1_discovery_v1.3.yaml` | v1.3 | — | ✅ |
| 0.2 Intelligence | `stage_0/0.2_intelligence_v1.0.yaml` | v1.0 | — | ✅ |
| B Semantic | `stage_b/b_semantic_v1.4.yaml` | **v1.4** | — | ✅ |
| B2-Macro | `stage_b2/b2_macro_v4.0.yaml` | v4.0 file | **v4.2** interna | ✅ |
| B2-Micro | `stage_b2/b2_micro_v4.0.yaml` | v4.0 file | **v4.1** interna | ✅ |
| B2-Director | `stage_b2/b2_micro_director_v1.0.yaml` | v1.0 | v1.0 | ✅ |
| B2-Engineer | `stage_b2/b2_micro_engineer_v1.0.yaml` | v1.0 | v1.0 | ✅ |
| C Scene | `stage_c/c_monastic_v2.5.0.yaml` | **v2.5.0** | — | ✅ |

**Nota**: il nome file e la versione interna possono divergere (es. `b2_macro_v4.0.yaml` ha versione interna v4.2).

---

## Stage 0: Intel

| Versione | Milestone | Cosa è cambiato |
|---------|-----------|----------------|
| Discovery v1.0 | Archetipo | Mappatura grezza capitoli |
| Discovery v1.1 | Stilistica | Analisi simboli dialogo (em-dash vs virgolette) |
| Discovery v1.2 | **Scansione Ossea** | Distinzione `toggle_paragraph` / `enclosed_pair` per normalizzazione |
| Intelligence v1.0 | **Creative DNA** | Fusione struttura + Casting + Palette sonore per Dashboard |

---

## Stage B: Semantic Analyzer

| Versione | Milestone | Cosa è cambiato |
|---------|-----------|----------------|
| v1.0 | Base | Valence, Arousal, Tension, Primary Emotion |
| v1.1 | **Dubbing Director** | Aggiunto Subtext (intento nascosto), `narrator_base_tone`, Mood Propagation per prevenire flickering tonale |
| v1.1 Logic | **Mediterranean** | Strategia bilingue: ragionamento in IT (comprensione sfumature), output in EN (compatibilità tecnica) |
| v1.2 | Enriched Subtext | `subtext`, `narrative_arc`, `narrator_base_tone` integrati direttamente; rimosso fallback hardcoded in Stage C |
| v1.2.1 | Entity Normalization | Istruzione esplicita: nomi entità senza articoli preposti ("Console" non "il Console"). Fix language slip su passaggi misti. |
| **v1.3** | **book_language** | `{book_language}` dinamico da `fingerprint.json → metadata.language`. Fix language slip su libri non italiani o capitoli con testo misto (es. diari in inglese in Hyperion). Rinforzo esplicito: "rispondi SEMPRE in {book_language} anche se il testo contiene passi in altre lingue". |
| **v1.4** | **Global Context** | Sezione CONTESTO OPERA in apertura: `{book_title}`, `{book_author}`, `{book_tone}` da `fingerprint.json → metadata` + `{block_index}`, `{total_blocks_in_chapter}`, `{chapter_number}` dal messaggio Stage A. Stage B non inferisce più il libro dal testo grezzo. Regola aggiunta: "Un blocco neutro in un'opera dark è comunque sotto-tensione". ~35 token aggiuntivi, schema JSON invariato. |

**Lezione chiave**: il "Mediterranean Prompting" (ragiona in italiano, produci in inglese) ha migliorato significativamente la comprensione delle sfumature narrative. Il `book_language` dinamico generalizza il principio a qualsiasi lingua sorgente. In v1.4 il DNA di Stage 0 (titolo, tono, posizione capitolo) scende in Stage B — Stage B non deve più inferire dal testo grezzo cosa sta leggendo.

---

## Stage C: Scene Director

| Versione | Milestone | Cosa è cambiato |
|---------|-----------|----------------|
| v1.1 | Archetipo | Prima segmentazione stabile |
| v1.5 | Theatrical | Mediterranean Prompting introdotto |
| v2.0 | Structural | Regole rigide per titoli e tag dialogo |
| v2.3 | **Monastic** | **Divieto assoluto** di modificare verbi, pronomi, struttura frase — risolto bug allucinazioni (cambio pronomi "lo" → "la") |
| v2.3.2 | Universal | Esempi con nomi generici (Marco/Julia) invece di personaggi specifici → evita bias sul libro corrente |
| v2.4.0 | **Monastic Final** | Integrazione placeholders Stage B + Character Profiles. Versione definitiva base. |
| **v2.5.0** | **Semantic Rhythm** | Aggiunta tassonomia pause semantiche a 6 livelli (50ms→2000ms) — fix pause piatte 100-200ms di v2.4. Aggiunto contesto numerico tension/arousal/valence nel blocco CONTESTO. Tutte le regole v2.4 invariate (additive). |

**Lezione chiave**: Stage C è il modulo più critico. La "fidelità monastica" (non modificare nulla del testo sorgente) è il principio che ha risolto più bug. In v2.5.0 si aggiunge la "consapevolezza ritmica" — le pause sono semantiche, non costanti.

---

## Stage B2-Macro: Musical Director

| Versione | Milestone | Cosa è cambiato |
|---------|-----------|----------------|
| v1.0–v3.x | Warehouse-First | Redis catalog, matching all'85%, stop-on-missing → **ARCHIVIATO** |
| **v4.0** | Sound-on-Demand | Zero catalogo Redis. PAD prodotto ex-novo da ACE-Step. PadRequest + PadArc. |
| **v4.2** (interna) | ACE-Step Ready | Arc proporzionality (segmenti proporzionali alla durata), Pre-build rule (`low` prima di ogni `high`), Vocabolario Qwen3 nel prompt, `roadmap_item` per structural roadmap. |

**Lezione chiave**: il vecchio sistema con Sound Library produceva segmenti arc di durata uniforme che non rispettavano la narrativa. Il vocabolario Qwen3 obbligatorio nel prompt ha eliminato il "prompt drift" di ACE-Step.

---

## Stage B2-Micro: Sound Designer (Monolitico)

| Versione | Milestone | Cosa è cambiato |
|---------|-----------|----------------|
| v4.0 | Sound-on-Demand | Shopping list diretta per ARIA ACE-Step |
| **v4.1** (interna) | **BBC/Star Wars Paradigm** | AMB: solo cambio fisico tra scene (max 1, 3-5s, non loop). SFX: "test 0" (c'è un momento culminante?). STING: solo rivelazioni irreversibili, timing middle/end. |

**Lezione chiave**: il cambio al paradigma BBC ha richiesto di riscrivere la definizione di "AMB" da "musica ambientale" a "segnale di cambio fisico tra scene consecutive". Differenza sottile ma critica per la qualità.

---

## Stage B2-Micro-Director / Engineer (Split)

| Versione | Milestone | Rationale |
|---------|-----------|----------|
| Director v1.0 | Separazione ruoli | L'LLM in modalità monolitica doveva fare decisioni narrative E tecniche simultaneamente → errori di consistenza `canonical_id`. Il Director vede solo il testo narrativo. |
| Engineer v1.0 | Conversione tecnica | La shopping list viene costruita PRIMA delle scenes_automation → strutturalmente impossibile il `canonical_id mismatch`. |

**Lezione chiave**: la modalità split ha risolto un bug strutturale della modalità monolitica. Non è solo una questione di qualità ma di correttezza formale del JSON.

---

## Lezioni Trasversali

1. **Nome file ≠ versione interna**: il file `b2_macro_v4.0.yaml` ha versione interna v4.2. Verificare sempre la versione interna documentata in `dias-inventory.md`, non solo il nome file.
2. **Prompt esternalizzati**: modificare un prompt non richiede toccare il codice. Versionare sempre il prompt con suffisso `_vX.Y`.
3. **Mediterranean Prompting**: funziona meglio per i testi italiani. Adottare sistematicamente.

## Vedi anche

- [[concepts/dias-pipeline]] — come i prompt si inseriscono nel flusso
- [[concepts/dias-voice-pipeline-quality]] — analisi qualitativa completa pipeline voce v1, gap residui, priorità
- [[concepts/dias-sound-design]] — principi BBC/Star Wars che guidano i prompt B2
- [[stack-dias]] — sistema DIAS completo
