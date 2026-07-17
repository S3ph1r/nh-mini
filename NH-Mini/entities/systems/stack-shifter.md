---
title: "Stack — SHIFTER"
type: entity
tags: [stack, shifter, shifts, planning, cp-sat]
sources: []
updated: 2026-06-22
---

# Stack — SHIFTER

**SHIFTER** (ControlRoom 24/7 Shift Manager - CR-Shifts) è il modulo per la pianificazione e ottimizzazione dei turni del personale della control room. 

Il sistema combina un database locale per lo storico con un motore solutore matematico basato su programmazione a vincoli (Constraint Programming).

## Architettura e Integrazione

SHIFTER è deployato sul runtime LXC dedicato [[ct204-shifter-rt|CT204]] come servizio di produzione (`shifter_rt` / `SHIFTER Runtime API`), esposto sulla porta 8000 e in futuro tramite il reverse proxy di [[ct202-gateway|CT202]].

L'ambiente di sviluppo e testing locale risiede all'interno di [[stack-nh-mini|LXC 190]].

## Caratteristiche Principali

* **Solutore Rolling Settimanale (Week-by-Week)**: Risolve la pianificazione anno 2026 iterando sequenzialmente su 53 settimane ISO. Questa architettura riduce lo spazio di ricerca del solutore CP-SAT a intervalli di 7 giorni, eliminando timeout e pre-calcolando in tempo reale i saldi equità YTD (storico + futuro) prima di ogni run settimanale.
* **Coerenza Settimanale Rilassata & Penalità Transizioni**: Per superare l'infeasibility matematica nelle settimane con alta presenza di ferie (es. settimana 25), il vincolo di coerenza settimanale rigido è stato allentato consentendo fino a 2 tipologie di turni a settimana per operatore (penalizzato con peso 2000). Sono state inserite penalità consecutive per il cambio di turno giorno-giorno (peso 600) per massimizzare la lunghezza delle streak ed evitare il continuo flip dei turni.
* **Vincoli Hard (Sicurezza)**:
  * Copertura minima per fascia (M, P, N) impostata dinamicamente da database (`requisiti_turno`) per ciascun giorno della settimana.
  * Almeno 1 operatore in presenza fisica per ciascun turno.
  * Riposo minimo obbligatorio di 24 ore dopo il turno Notte (prevenzione N -> M).
  * Esclusione dei turni durante i giorni di ferie/malattia approvate.
  * Esclusione rigida dei recuperi feriali durante i giorni di ferie/malattia approvate (la ferialità a riposo per ferie non può essere consumata come recupero compensativo).
* **Vincoli Soft (Ottimizzazione ed Equità)**:
  * Assegnazione automatica dei riposi compensativi per i weekend lavorati (da pianificare in LUN-VEN delle settimane $W-1$ o $W+1$).
  * Incentivazione qualitativa dei recuperi consecutivi (es. due giorni di fila off) con pesi calibrati per evitare la frammentazione.
  * Forte penalizzazione per 3 o più recuperi feriali consecutivi (peso 5000), calcolata sia all'interno della singola settimana che a cavallo di settimane consecutive (cross-week), per spingere il solutore verso coppie o singoli recuperi.
  * Distribuzione equa e uniforme delle coppie di recupero consecutive tra tutti gli operatori (tramite minimizzazione dello spread) per evitare sproporzioni tra operatori in presenza e smart-working.
  * Equità annuale sul totale di turni notturni (N), pomeridiani (P), mattutini (M) e weekend lavorati.
  * Soddisfacimento delle preferenze espresse dagli operatori.

## Gestione Dinamica Operatori & Requisiti di Contratto

Il sistema supporta il controllo dinamico delle risorse e dei vincoli operativi tramite tre pannelli dedicati nella dashboard:
1. **Gestione Operatori**: Consente di aggiungere nuovi operatori, impostare il loro gruppo (`Smart` / `Presenza`) e specificare le preferenze individuali di turno (M-P-N con rango 1-3). Consente inoltre l'eliminazione con rimozione a cascata (`ON DELETE CASCADE`) dei turni e dei dati storici associati.
2. **Fabbisogni Minimi**: Consente di modificare ed aggiornare via DB i requisiti minimi di staffing giornalieri.
3. **Controllo Feasibility Pre-run**: Per prevenire fallimenti del solutore con pool ridotti, viene eseguito un controllo all'avvio. La risoluzione viene interrotta con errore HTTP 500 se:
    * Il pool totale ha meno operatori del massimo fabbisogno giornaliero ($\max(M+P+N)$, tipicamente $\ge 8$).
    * Il pool di operatori "in presenza" è inferiore a 3 (necessario per coprire M, P, N in sede ogni giorno).

## Interfaccia Grafica e UX (Calendario Triplo)

* **Matrice a Tre Griglie Sincronizzate**: Espone tre calendari paralleli ad allineamento orizzontale automatico e scroll condiviso per gestire e confrontare:
  * **Calendario Live (Effettivo)**: Mostra i turni reali e i recuperi goduti, integrando i badge dinamici delle ferie/malattie (`FER`/`MAL`) per gli operatori assenti. Colonne giornaliere `32px` (group `36px`), 31 giorni del mese sempre visibili nella viewport.
  * **Calendario Planned (Pianificato)**: Rappresenta il baseline originario generato dal solutore.
  * **Calendario Ferie (Holidays)**: Interattivo e cliccabile per inserire/rimuovere ferie e azzerarle globalmente.
* **Pannello Summary Slide-In (LIVE only)**: Il pannello statistiche annuali per operatore non è più una colonna fissa a destra della griglia, ma un pannello a comparsa posizionato sul bordo destro del calendario LIVE. Si attiva al passaggio del mouse su una strip trigger da 20px. Usa la stessa struttura tabella (`cal-row-op`, `cal-hdr-month`, `cal-hdr-day`, `cal-row-foot`) del calendario principale per allineamento pixel-perfect delle righe. Sfondo: `rgba(15,23,42,0.65)` con `backdrop-filter:blur(20px)`. Mostra: M, P, N, WE, SAB, FES, REC++, REC+, DÈB., FER, MAL per ogni operatore.
* **User Mode Filter**: In modalità user (non-admin), le celle del calendario LIVE oltre `pivot + 3 mesi` vengono renderizzate come punto grigio, nascondendo la pianificazione futura non ancora consolidata.
* **Default Pivot & Validazione**: Al caricamento della pagina, il campo data pivot viene impostato automaticamente a `today+1`. La UI blocca l'esecuzione del solutore se `pivotDate ≤ today` salvo attivazione del checkbox "Consenti Pivot nel passato" (`bypass_past_check`).
* **Menu Popover Dinamico**: Consente l'inserimento rapido di turni manuali, ferie e malattie su intervalli di date tramite drag-and-drop o doppio click.
* **Veste Grafica macOS Frosted Glass**: Tema grigio medio-scuro (obsidian/brushed silver) con onde d'acqua concentriche e cards semitrasparenti (`rgba(255, 255, 255, 0.35)`) con effetto sfocato (`backdrop-filter: blur(20px)`).
* **Pillole dei Turni Stondate e Satire**: Capsule dei turni (M, P, N, REC, FER, MAL) con colori saturi e vividi (Giallo per M, Verde per P, Notte=Azzurro, REC=Arancione, FER=Rosso, MAL=Rosa scuro) e testi ad alto contrasto per la massima leggibilità.
* **Avatar Silhouette**: Generatore di avatar SVG in-app che associa a ciascun operatore un'icona silhouette personalizzata con gradiente unico basato sull'hash del nome.

## Componenti

| Componente | File | Scopo |
| :--- | :--- | :--- |
| Database | `src/backend/database.py` | Definizione tabelle SQLite relazionali via SQLAlchemy |
| Seed | `src/backend/seed.py` | Inserimento anagrafica 12 operatori seed e storico |
| Solutore | `src/backend/solver.py` | Algoritmo CP-SAT con OR-Tools per turni ed equità |
| REST API | `src/backend/main.py` | FastAPI server ed endpoint di CRUD / trigger solve |
| Import XLS | `src/backend/import_utils.py` | Parser openpyxl per import turni da file .xlsx (richiede openpyxl + python-multipart) |
| Frontend | `src/frontend/` | Dashboard SPA premium in Tailwind CSS e Vanilla JS |

## Calendario Triplo — Design Decisions

La divergenza tra LIVE e PLANNED dopo ferie manuali o swap è **comportamento intenzionale**: PLANNED rappresenta la proposta equa originaria del solutore; LIVE riflette la realtà operativa con tutte le deviazioni. Questa dualità permette di visualizzare immediatamente l'impatto delle scelte discrezionali (ferie, malattie, scambi) rispetto al piano ottimale. Il solutore, al successivo re-run, riassorbe le deviazioni e tende nuovamente all'equità entro i vincoli residui.

## Architettura Carry-Over Recuperi

**Carry_in** (`carry_over_rec` in tabella operatori) = saldo netto WE+FES lavorati − REC presi, calcolato al `pivot_date` dell'ultimo run del solutore. Viene impostato manualmente prima del primo run (o da `close-year` per gli anni successivi).

**Carry_out** (calcolato dinamicamente da `/api/summary/annual`) = `max(0, carry_in + H2_WE+FES - H2_REC)`, dove H2 = turni post-pivot_date. Il solutore include il debito pregresso nell'obiettivo (peso 200) e lo azzera durante la pianificazione H2 attraverso RECs extra.

**Close-year**: l'endpoint `/api/summary/close-year` trasferisce `carry_out → carry_over_rec` per l'anno successivo. Da eseguire ogni 31 dicembre.

## G/REP — Sostituzione Operatori Gruppo R

Gli operatori del **gruppo R** (Brusco, Lanzavecchia) non sono assegnati dal solutore. Quando uno di essi è assente, un operatore standard lo copre: la sostituzione viene registrata come `tipo='sostituzione'` nella tabella ferie.

**Rendering nel Live Calendar**: il frontend costruisce `sostMap` da `leaves` filtrate per `tipo='sostituzione'` e mostra direttamente **G** (giorni feriali) o **REP** (weekend/festivi) nella cella, senza attendere il solutore.

**Forzatura manuale G/REP**: tramite il batch endpoint (`POST /api/schedule/batch`) è possibile assegnare fascia `G` o `REP` a qualunque cella del live calendar. Il solutore al re-run successivo preserva queste forzature (via `saved_manual_grep`) esattamente come preserva le ferie.

## Ferie Pianificate — Blocco Trimestrale

Il blocco è implementato **solo nel frontend** (funzione `isFerieLocked`), con pivot trimestrali fissi:
- Q1 Gen-Mar: bloccate dal 25/12 anno precedente
- Q2 Apr-Giu: bloccate dal 21/03
- Q3 Lug-Set: bloccate dal 21/06
- Q4 Ott-Dic: bloccate dal 21/09

**Admin bypass**: la variabile `isAdminView` disabilita il lock trimestrale per gli amministratori, che possono modificare ferie in qualunque trimestre dell'anno.

Il solutore **non aggiorna** il blocco ferie — sono sistemi indipendenti. Il backend accetta ferie per qualunque data futura (unico check: no passato).

**Flusso operativo raccomandato**: inserire tutte le ferie pianificate prima del pivot trimestrale, poi rilancio del solutore dal 1° del trimestre.

## Raffinamenti Futuri (Backlog)

| # | Descrizione | Impatto | Priorità |
|---|-------------|---------|----------|
| R1 | Blocco ferie lato backend (check trimestrale in `create_leave`) | Bassa — uso mono-admin | Bassa |
| R2 | `confirm()` su "Ricalcola Solutore" con bypass_past_check attivo | Prevenzione perdita dati accidentale | Media |
| R3 | `confirm()` su "Elimina Tutte le Ferie" | Prevenzione cancellazione accidentale | Media |
| R4 | Banner "PLANNED non sincronizzato" dopo ferie/swap manuali | UX chiarezza | Bassa |
| R5 | Reminder / workflow guidato per Close-Year a fine dicembre | Continuità dati 2027 | Media |
| R6 | Ottimizzazione render DOM (virtualizzazione 14k celle) | Performance su hardware lento | Bassa |

## Workflow di Deploy (Git-based)

A partire da 2026-06-22, il flusso di deploy ufficiale è:

```
LXC 190 (dev)              →   GitHub S3ph1r/SHIFTER   →   CT204 (prod)
sviluppi/SHIFTER/ (git)    →   git push origin main    →   git reset --hard origin/main
```

**CT204 service**: `WorkingDirectory=/opt/SHIFTER/src`, uvicorn punta a `backend.main:app`. Il DB `shifts.db` rimane in `/opt/SHIFTER/shifts.db` (fuori da `src/`), referenziato via env `SHIFTS_DB_PATH=/opt/SHIFTER/shifts.db` — non toccato da git pull.

**`.gitignore`** esclude: DB files, backups/, historical_import/, seed/populate scripts, scratch files con dati operatori, screenshots, test con nomi hardcoded.

## Relazioni con altri stack

* **Gestito da**: [[stack-nh-mini]] come sotto-progetto in `sviluppi/`.
* **Infrastruttura**: Descritto in [[overview]].
