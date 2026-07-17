---
title: "Quality Gate & Tiers — Lifelog2"
type: concept
tags: [lifelog2, quality-gate, quality-tiers, pipeline, asr, whisperx]
sources: [lifelog2-classification-evolution-blueprint-v1.md, stack-lifelog2.md]
updated: 2026-06-07
---

# Quality Gate & Tiers — Lifelog2

Il sistema di filtraggio e classificazione della qualità di [[entities/systems/stack-lifelog2|Lifelog2]] garantisce che il secondo cervello non venga inquinato da allucinazioni prodotte dal modello ASR (WhisperX) su audio degradato o rumoroso. Si articola in due livelli: lo **Stage C1 (Gate Meccanico)** e i **Transcript Quality Tiers (Qualità Acustica vs Semantica)**.

---

## 1. Stage C1 — Gate Meccanico (Zero-LLM)

Lo Stage C1 viene eseguito dal worker `stage_c1c2_gate.py` (lo Stage C2 è stato rimosso in quanto la logica di C1 è ritenuta sufficiente) a valle del completamento dello Stage C. Il suo scopo è analizzare le metriche strutturali del segmento e del trascritto per decidere il routing nella pipeline.

### Input Analizzati
- `n_turns`: Numero di turni di conversazione.
- `max_turn_s` e `avg_turn_s`: Durata massima e media dei turni.
- `n_speakers`: Numero di speaker distinti rilevati.
- `avg_logprob`: Log-probability media di WhisperX (qualità acustica).
- `speech_ratio`: Frazione del segmento contenente parlato (da Stage B).
- `duration_s`: Durata totale del segmento.

### Regole di Classificazione (`stage_c1_classifier.py`)
1. **Rule 0 (Loop Artifact)**: Se `n_turns == 0` $\rightarrow$ `route='discard'`. L'audio conteneva segnale ma WhisperX ha rimosso tutti i turni per evitare loop infiniti su silenzi o rumori ambientali.
2. **Rule 1 (Sparse)**: Se `n_turns <= 1` e `speech_ratio < 0.15` $\rightarrow$ `route='discard'`. L'audio contiene solo rumori di fondo transitori.
3. **Rule 2 (Trascrizione Inaffidabile)**: Se `avg_logprob < -0.55` $\rightarrow$ `route='discard'`. La confidenza acustica del modello è troppo bassa per considerare il testo utile.
4. **Rule 4 (Pass/Default)**: In tutti gli altri casi $\rightarrow$ `route='enrich'`. Il segmento ha superato il gate.

### Routing Decision
- **`discard`**: Il segmento viene scartato. Stato nel DB: `pipeline_status='discarded'` e `discard_reason='sparse'`. L'analisi si ferma qui (niente LLM).
- **`summary_only`**: Il segmento è segnato come completato senza passare per Stage D. Stato nel DB: `pipeline_status='done'` e `analysis_tier=0.0`.
- **`enrich`**: Il segmento viene inoltrato a Redis Stream `lifelog:stream:enrich` per essere consumato dallo Stage D (Enrichment).

---

## 2. Transcript Quality Tiers

Il sistema distingue due misure di qualità con semantiche diverse:
1. **Qualità Acustica (`avg_logprob` di WhisperX)**: Misura *pre-testo* che indica quanto il modello ASR fosse sicuro della trascrizione fonetica. Logprob bassi generano parole foneticamente simili ma errate (es. *Mediolambro* al posto di *Mediolanum*).
2. **Qualità Semantica (`tq_score` di Stage D LLM)**: Misura *post-testo* che valuta la coerenza del testo. Il LLM può ritenere un testo grammaticalmente coerente e fluido (tq_score alto) anche se le parole sono state inventate o allucinate da WhisperX.

Per risolvere questa "zona cieca" (audio degradato ma testo sintatticamente plausibile), il sistema suddivide il trascritto in tre tier basati su `avg_logprob`:

| Quality Tier | Soglia Logprob | Caratteristiche dell'Audio | Livello di Estrazione (Stage D) |
|--------------|----------------|----------------------------|---------------------------------|
| **Tier A** (Alta) | `avg_logprob > -0.25` | Podcast in cuffia, telefono vicino, voce pulita | **Full**: Estrae entità, decisioni, action items e persone menzionate. |
| **Tier B** (Ridotta) | `da -0.25 a -0.40` | Conversazione a media distanza (1-3m), rumore moderato | **Contextual**: Estrae solo summary, temi e sentiment. Sopprime le entità (nomi e luoghi non verificabili). |
| **Tier C** (Degradata) | `da -0.40 a -0.55` | Distanza >3m, bar/ristorante rumoroso, forti sovrapposizioni | **Contextual / Metadata-only**: Salva il contesto macroscopico ma vieta l'estrazione di dettagli e nomi. |

### Il Meccanismo del Server-Side Floor
Se il LLM di Stage D non rileva il degrado acustico e restituisce `extraction_level='full'` per un segmento Tier B o C:
1. Il backend esegue un **override automatico** a `contextual`.
2. Le entità estratte vengono rimosse per evitare di inquinare il knowledge graph.
3. Il punteggio di importanza viene cappato: `importance = min(importance, 0.40)`.

---

## 3. Asimmetria Voiceprint vs ASR

Esiste una discontinuità fondamentale tra la componente biometrica e quella testuale in ambienti difficili:
- **Voiceprint Identification (Stage C)**: Il matching del voiceprint (WeSpeaker/ResNet34 256d) avviene sullo spettrogramma audio, ed è **indipendente dalla qualità dell'ASR**. Funziona con alta precisione anche a `avg_logprob = -0.50`.
- **ASR Text Extraction (WhisperX)**: Fortemente influenzato dal rumore di fondo.

### Conseguenza Architetturale
In segmenti rumorosi (Tier B/C) con persone note:
1. **Sappiamo chi c'era**: Popoliamo correttamente `speaker_turns.person_id` (la presenza è un dato biometrico certo).
2. **Non sappiamo con certezza cosa si sia detto**: Sopprimiamo le entità dal testo allucinato. Il summary descriverà l'evento in modo generale ("il collega ha parlato di deployment") senza pretendere di estrarre nomi precisi.

---
## Relazioni con altre pagine
- Stack di riferimento: [[entities/systems/stack-lifelog2|Lifelog2]]
- Protocolli di rete: [[concepts/aria-redis-protocol|ARIA Redis Protocol]]
- Pattern di sviluppo: [[concepts/lifelog2_dev-pattern|Lifelog2 Dev Pattern]]
- **Evoluzione pianificata**: [[concepts/lifelog2-refactor-roadmap]] — FASE 1 estende C1 con Confidence Score multi-dimensionale (logprob × snr × speaker_count) e introduce dual pool Trusted/Flagged
