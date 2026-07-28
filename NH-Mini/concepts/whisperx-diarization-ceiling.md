---
title: "WhisperX — il tetto della diarizzazione su audio ambientale"
type: concept
tags: [aria, whisperx, pyannote, diarizzazione, lifelog2, stage-c, qualita]
sources: [lifelog2-aria-diarization-report-2026-07-28.md]
updated: 2026-07-28
---

# WhisperX — il tetto della diarizzazione su audio ambientale

Esito della sessione del 2026-07-28 su [[stack-aria]]: **su registrazioni
ambientali con voci lontane e sovrapposte la diarizzazione ha un limite
fisico**, ora misurato. Non si supera con i parametri disponibili — si
riconosce e ci si progetta attorno.

> Questa pagina sostituisce `whisperx-word-level-turns.md`, che documentava il
> taglio per parola come soluzione prima che venisse misurato e ritirato.

## Il difetto di partenza

WhisperX assegna lo speaker di un **segmento** per durata dominante: un
segmento a cavallo di due parlanti collassa sul maggioritario e le parole
dell'altro vengono assorbite. Il backend concatenava poi i segmenti
consecutivi con la stessa etichetta.

Effetto su Lifelog2: turni da 37 s con dentro domanda e risposta di persone
diverse, uno da 299 s, 53% dei turni senza voiceprint utilizzabile, da cui le
"persone ricorrenti fantasma" e la voce dell'utente non riconosciuta.

## Cosa è stato provato — tutto misurato, tutto scartato

Stesso segmento reale, SNR 21 dB (tra i migliori disponibili), 4-5 parlanti:

| configurazione | intervalli | parlanti | <0.5s | alternanze brevi |
|---|---|---|---|---|
| **standard (in uso)** | 159 | 2 | 42 | 24 |
| `min_speakers=3` | 185 | 3 | 71 | 38 |
| `min_speakers=4` | 210 | 4 | 99 | 58 |
| `min_speakers=5` | 207 | 5 | 92 | 46 |
| `exclusive_diarization` | 180 | 2 | 72 | **78** |

- **Taglio per parola**: corretto in teoria (`assign_word_speakers` assegna lo
  speaker a ogni parola e whisperx lo scarta), ma amplifica il rumore — 30% dei
  turni finiva a 1-2 parole. Il voto per segmento è impreciso ma **filtra**.
- **`min_speakers`**: non separa meglio, taglia più fine lo stesso audio.
- **`exclusive_speaker_diarization`**: elimina le sovrapposizioni tagliando, e
  dove accavallarsi è la norma triplica le alternanze spurie.
- **Embedding per parlante** (`return_embeddings`): inutilizzabili come
  voiceprint — al massimo **+0.038** di somiglianza con identità confermate
  presenti nella registrazione, contro una soglia di 0.50. Sono impasti: due
  etichette per cinque persone.

Il warning `std(): degrees of freedom is <= 0` in pyannote lo conferma
dall'interno: lo statistics pooling gira su finestre da un frame.

## Un bug reale trovato per strada

Il wrapper dell'orchestratore (`aria_node_controller/backends/lifelog_whisperx.py`)
ricostruiva il body verso il backend con **soli tre campi**, scartando in
silenzio qualunque parametro di diarizzazione. Senza correggerlo avremmo
concluso che i parametri non servono **senza averli mai davvero provati**:
tre run con `min_speakers` diversi davano risultati identici perché il
parametro non arrivava.

## Cosa resta, e a cosa serve

I turni tornano a costruirsi per segmento. Ma il contratto ora porta segnali
nuovi, che **non servono a ricostruire i turni ma a etichettarli**:

| campo | uso previsto |
|---|---|
| `diarization_stats` | quanto la diarizzazione sta cedendo **su quel segmento**: intervalli, durate, quanti sotto 0.5s, alternanze brevi |
| `word_timestamps[].speaker` | verifica/ri-taglio a valle senza rifare inferenza |
| `speaker_embeddings` | oggi inutilizzabili, tornerebbero utili se la separazione migliorasse |

È l'asse "parlante" del gate di qualità di [[lifelog2-quality-gate]], ma
calcolato meglio di come era stato progettato: **non inferito dai sintomi sul
turno, ma misurato direttamente su quanto il modello cede**.

## La lezione

Il voto di maggioranza per segmento non stava sbagliando: **mascherava**. Il
taglio per parola non ha creato il problema, l'ha scoperchiato. E aver provato
tutte le leve native prima di aggiungerne di nostre ha evitato di costruire
un'euristica sopra una diagnosi sbagliata.

## Vedi anche
- [[stack-aria]] · [[stack-lifelog2]] · [[lifelog2-quality-gate]]
- `sviluppi/ARIA/docs/backends/lifelog-whisperx.md` §2bis — dettaglio tecnico
- `sviluppi/Lifelog2/docs/lifelog2-aria-diarization-report-2026-07-28.md`
