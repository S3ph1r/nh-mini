---
title: "SHIFTER — Boundary di Fine Anno ed Equità"
type: concept
tags: [shifter, equity, carry-over, solver, limits]
sources: []
updated: 2026-06-13
---

# Boundary di Fine Anno ed Equità in SHIFTER

Questa pagina documenta un'analisi dettagliata del comportamento del saldo di recupero (carry-over) e dell'equità annuale nel sistema [[entities/systems/stack-shifter|SHIFTER]] gestito sul runtime [[entities/containers/ct204-shifter-rt|ct204-shifter-rt]].

## Il Caso di Studio: Pellegrini (Giugno 2026)

Durante i test di forzatura manuale nella settimana dal 15 al 19 giugno 2026, si è notato che rimuovendo manualmente un giorno di recupero (`REC` sostituito da turno `M` il 16 giugno) per l'operatore Pellegrini, il contatore del carry-over finale (debito) a fondo tabella rimaneva fermo a `0`, anziché incrementare a `1`.

### Diagnostica del Database

Dall'analisi dei dati effettivi (`TurnoEffettivo` e `RecuperoEffettuato`) e pianificati (`TurnoPianificato` nella baseline) estratti dal database `shifts.db` per l'intero anno 2026, è emersa la seguente situazione per Pellegrini:

1. **Weekend Lavorati (WE)**: 61 giorni (derivati da 28 weekend completi in cui ha lavorato sia sabato che domenica, e 5 sabati singoli lavorati).
2. **Recuperi Pianificati (REC)**: 63 giorni nella baseline.
3. **Differenza Iniziale**: Pellegrini ha iniziato con un saldo di +2 recuperi pianificati rispetto ai weekend effettivamente lavorati nell'anno solare 2026.
4. **Effetto della Sostituzione (16 Giugno)**: Sostituendo il recupero del 16 giugno con un turno di mattina (`M`), il record di recupero è stato cancellato dal database, portando i suoi recuperi totali da 63 a 62.
5. **Calcolo del Carry-Over**: La formula del carry-over per i debiti YTD è:
   $$\text{carry\_over\_out} = \max(0, \text{carry\_over\_in} + \text{we\_days\_worked} - \text{rec\_dates\_len})$$
   Applicando i valori:
   * **Prima della modifica**: $\max(0, 0 + 61 - 63) = \max(0, -2) = 0$ (credito di 2 recuperi).
   * **Dopo la modifica**: $\max(0, 0 + 61 - 62) = \max(0, -1) = 0$ (credito di 1 recupero).

Poiché il saldo era in positivo (credito), Pellegrini ha "assorbito" la cancellazione del recupero senza generare un debito netto nell'anno solare corrente.

---

## Causa Radice: L'Effetto Boundary della Settimana 53

La discrepanza iniziale per cui molti operatori hanno un numero di recuperi pianificati superiore ai weekend lavorati nel 2026 (es. Pellegrini con 63 REC a fronte di 61 WE) è causata dall'**effetto boundary a fine anno (Settimana 53)**:

1. Il solutore CP-SAT in [[entities/systems/stack-shifter|SHIFTER]] pianifica su base settimanale seguendo le settimane ISO.
2. La **Settimana 53 del 2026** inizia lunedì 28 dicembre 2026 e termina domenica 3 gennaio 2027.
3. Pellegrini lavora il weekend di questa settimana, ossia sabato 2 gennaio 2027 e domenica 3 gennaio 2027.
4. Poiché questi due giorni ricadono nel 2027, **non vengono conteggiati** nei weekend lavorati YTD del 2026 (che termina rigorosamente il 31 dicembre 2026).
5. Tuttavia, i 2 giorni di riposo infrasettimanali associati a questa settimana ISO vengono pianificati dal solutore il 30 e 31 dicembre 2026.
6. Poiché questi riposi ricadono nel 2026, **vengono conteggiati** come recuperi presi nel 2026.
7. Di conseguenza, nel 2026 Pellegrini riceve 2 recuperi che in realtà compensano un weekend che lavorerà nel 2027, portando il suo bilancio 2026 in apparente "surplus" (+2).

Questo comportamento è fisiologico per le settimane a cavallo d'anno, e si compenserebbe naturalmente l'anno successivo (nel 2027 Pellegrini si troverebbe a lavorare il weekend del 2-3 gennaio senza recuperi corrispondenti nel 2027, generando un debito che riequilibrerebbe il tutto).

---

## Soluzione Proposta: Equità Relativa al Piano (Delta-Based)

Per allineare il comportamento del sistema all'intuito dell'utente (per cui qualsiasi rimozione manuale di un `REC` pianificato deve generare un debito immediato), si propone di ridefinire il calcolo del carry-over basandolo sul **delta rispetto al piano originario** anziché su conteggi assoluti.

### Nuova Formula

$$\text{carry\_over\_out} = \max\left(0, \text{planned\_carry\_over\_out} + (\text{actual\_we\_worked} - \text{planned\_we\_worked}) - (\text{actual\_recoveries} - \text{planned\_recoveries})\right)$$

### Esempio Applicato

Per Pellegrini:
* $\text{planned\_carry\_over\_out} = 0$
* $\text{planned\_we\_worked} = 61$, $\text{actual\_we\_worked} = 61 \implies \Delta\text{WE} = 0$
* $\text{planned\_recoveries} = 63$, $\text{actual\_recoveries} = 62 \implies \Delta\text{REC} = -1$

Applicando la nuova formula:
$$\text{carry\_over\_out} = \max(0, 0 + 0 - (-1)) = 1$$

Il debito incrementa correttamente a 1, neutralizzando l'effetto del surplus boundary originato dalla settimana 53.
