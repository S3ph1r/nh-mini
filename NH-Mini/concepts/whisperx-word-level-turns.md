---
title: "WhisperX — turni tagliati per parola, non per segmento"
type: concept
tags: [aria, whisperx, diarizzazione, lifelog2, stage-c, qualita]
sources: [lifelog2-aria-diarization-report-2026-07-28.md]
updated: 2026-07-28
---

# WhisperX — turni tagliati per parola, non per segmento

Correzione al backend `lifelog_whisperx` di ARIA (commit `abe9b1b`, 2026-07-28)
che sana la causa a monte di una lunga catena di problemi in [[stack-lifelog2]].

## Il difetto

WhisperX assegna lo speaker di un **segmento** per durata dominante — dal
sorgente: *"sum intersection durations per speaker and pick the dominant one"*.
Un segmento a cavallo di due parlanti **collassa sul maggioritario** e le parole
dell'altro vengono assorbite. Il backend poi concatenava i segmenti consecutivi
con la stessa etichetta.

Risultato: il "turno" non era un turno, era **un blocco di tempo a etichetta
dominante**.

## Perché contava

Misurato sui dati reali di Lifelog2 prima della correzione:

- turni da **37 s** con dentro domanda e risposta di **persone diverse**
- `n_segments_merged` fino a **79**; un turno da **299 s** (un intero segmento
  da 5 minuti)
- **53% dei turni** senza voiceprint utilizzabile: l'embedding era la media di
  più voci, quindi non somigliava a nessuno
- da lì le **"persone ricorrenti fantasma"** (cluster di embedding-miscuglio) e
  la voce dell'utente non riconosciuta — cosine **−0.007** col proprio centroide
- e l'impossibilità per il Thread Builder di segmentare semanticamente: nessun
  prompt può ricostruire un dialogo da turni che mescolano chi parla

## La correzione

`assign_word_speakers` assegna lo speaker anche a **ogni parola**: il dato
c'era già e veniva scartato. Ora i turni si tagliano dove cambia lo speaker
della parola, attraversando i confini di segmento.

Aggiunto anche `speaker` ai `word_timestamps` (campo additivo), così un
consumatore può ri-verificare o ri-tagliare senza rifare inferenza.

| situazione | esito |
|---|---|
| segmento a cavallo di due parlanti | **due turni distinti** |
| stesso parlante su più segmenti | un turno solo (invariato) |
| parola senza speaker | ricade sullo speaker del segmento |
| segmento senza allineamento a parole | blocco unico (comportamento precedente) |
| parola senza timestamp | eredita l'ultimo noto, non viene persa |

## Cosa NON risolve

Non ricostruisce l'audio: voci lontane e sovrapposte continueranno a produrre
turni inaffidabili. Serve comunque il gate di qualità progettato lato Lifelog2
([[lifelog2-quality-gate]]) — questa correzione ne riduce il numero, non li
elimina.

E **non recupera lo storico**: i transcript già su MinIO non hanno lo speaker
per parola. Vale dall'audio processato da qui in avanti, o riprocessando gli
m4a ancora disponibili (~1000 su 2000: gli altri li ha cancellati la policy di
retention prima della sua sospensione).

## Da valutare dopo, non insieme

`min_speakers`/`max_speakers` sono supportati da `DiarizationPipeline.__call__`
e ARIA **non li passa** (chiama senza parametri). Erano il candidato numero uno
prima di scoprire il difetto qui sopra; ora contano molto meno, e vanno comunque
**tarati sui dati** — forzare un minimo troppo alto crea parlanti inesistenti,
l'errore opposto e altrettanto dannoso.

## Vedi anche
- [[stack-aria]] · [[stack-lifelog2]] · [[aria-task-lifecycle]]
- [[lifelog2-quality-gate]] — i due assi di qualità in uscita da WhisperX
- `sviluppi/ARIA/docs/backends/lifelog-whisperx.md` §2bis — dettaglio tecnico
- `sviluppi/Lifelog2/docs/lifelog2-aria-diarization-report-2026-07-28.md` — il report che ha portato qui
