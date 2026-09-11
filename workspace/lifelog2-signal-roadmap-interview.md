# Lifelog2 — Intervista sulla direzione: segnali, valore, statistica

**Metodo** (2026-07-17): una domanda per volta con esempi e opzioni; Roberto risponde con
preferenze; le risposte vengono registrate qui sotto ogni domanda. Alla fine: roadmap
con la direzione, i segnali usati in ogni fase, e i criteri di decisione.

**Contesto di partenza** (dal ragionamento del 2026-07-17):
- Due regimi: evento (ora/giorno, errore pesa per intero, valore deperibile) vs
  accumulo (settimane/mesi, errore casuale si media, contano i bias sistematici).
- Distribuzione reale: ~90% dei thread è "counted" (solo statistica), ~10% significativo, ~3% prezioso.
- Principio: nessun thread esce a mani vuote — o gradua al semantico o versa nello statistico.
- LLM ai bordi, statistica nel mezzo. La ricorrenza è il segnale (per vp, fatti, pattern).

## Piano delle domande

1. Valore primario nei prossimi 1-3 mesi (quale "prodotto" viene prima) — ✅
2. signal_class del thread: deterministico, LLM o ibrido — ✅
3. Metriche baseline settimanali: quali famiglie contano — ✅
4. Cerchia relazionale: quando uno sconosciuto ricorrente viene promosso — ✅
5. Evidence accumulation sui fatti profilo: come cresce/decade la fiducia — ✅
6. Deviazioni e alert: cosa merita un'allerta e con che tolleranza — ✅
7. Oblio concreto: storage m4a vs testo/DB — ✅ (ribaltata: priorità è il cestino m4a)
8. Narrativa lunga (Z5): cosa vuoi leggere in una review settimanale/mensile

---

## Q1 — Valore primario nei prossimi 1-3 mesi

**Domanda**: nel breve periodo, quale prodotto deve maturare per primo e fare da metro
per le decisioni di priorità?

Opzioni proposte:
- **A. Memoria consultabile** — journal/search/thread detail: "cosa è successo, cosa è stato detto"
- **B. Azione** — open loops, promemoria, impegni estratti: il sistema ti ricorda cose
- **C. Profilo/statistica** — baseline, abitudini, cerchia: accumulare da subito per avere la derivata tra mesi

**Risposta Roberto**: **C base + B prodotto** — le metriche baseline partono subito in
background (l'accumulo non recuperato è irrecuperabile), il lavoro visibile va sugli
impegni/promemoria affidabili. La statistica è fondazione, l'azione è il prodotto quotidiano.

---

## Q2 — signal_class del thread: chi lo decide?

**Domanda**: la classificazione di utilità del thread (actionable / contestuale /
solo-statistica) la calcola una regola deterministica sui campi esistenti, la dichiara
Stage E (LLM), o un ibrido?

Opzioni:
- **A. Deterministico** — regola SQL/python su campi già estratti (importance, presenza, persone note, open_loops). Gratis, spiegabile, ricalcolabile su tutto lo storico in un UPDATE. Ma cieco alle sfumature.
- **B. LLM (Stage E)** — il modello risponde esplicitamente alle 3 domande ("cosa mi dice, chi partecipa, cosa ne estraggo"). Più fine, ma costa, non è retroattivo gratis, e aggiunge varianza.
- **C. Ibrido** — deterministico come default; l'LLM può solo PROMUOVERE (mai declassare) nei casi in cui trova valore che i numeri non vedono.

**Risposta Roberto**: **C. Ibrido** — base deterministica su campi esistenti (retroattiva,
ricalcolabile su tutto lo storico gratis); Stage E può solo PROMUOVERE, mai declassare,
con motivo loggato e misurabile (per poter validare quanto/quando l'LLM aggiunge valore
reale sopra la regola).

---

## Q3 — Metriche baseline settimanali: quali famiglie contano?

**Domanda**: quali famiglie di metriche materializzare da subito (SQL, zero LLM) come
fondazione per la derivata futura? Ogni settimana persa senza baseline è storia che non
si recupera più.

Famiglie candidate (puoi sceglierne più di una, o riordinarle per priorità):
- **Tempo/presenza**: minuti registrati/giorno, ratio personal/ambient/media, ore di silenzio
- **Sociale**: vp distinti visti, vp ricorrenti (cerchia), minuti con vp_R+altri vs vp_R solo
- **Contenuto**: topic dominanti della settimana, sentiment prevalente, luoghi (quando arriverà il GPS)
- **Produttività personale**: open_loops aperti/chiusi, action_items completati vs accumulati, decisioni prese
- **Qualità pipeline**: % turni HIGH/LOW/JUNK, % thread "counted" vs "significativi" (il tuo indicatore di quanto rumore c'è nella settimana)

**Risposta Roberto**: **Tutte e quattro le famiglie proposte** (tempo/presenza, sociale,
contenuto, produttività+qualità pipeline) — nessuna esclusa. La baseline parte completa
da subito, incluse le metriche di autodiagnosi della pipeline come parte della
fondazione, non solo come output finale a valle.

---

## Q4 — Cerchia relazionale: quando uno sconosciuto ricorrente viene promosso?

**Domanda**: un vp sconosciuto che ricompare nel tempo (stessi orari, thread con tua
presenza sostanziale) è candidato "persona della tua cerchia". Chi decide la promozione
da vp anonimo a persona nominata/taggata, e con quale criterio?

Opzioni:
- **A. Automatico per soglia** — N ricorrenze in M settimane con presenza sostanziale → promosso a "persona ricorrente non identificata", pronto per un nome quando/se lo dai tu
- **B. Sempre proposto, mai automatico** — il sistema segnala il candidato (come fa oggi l'Identity Detective), ma la promozione a persona è sempre una tua conferma esplicita
- **C. Ibrido per livello** — promozione automatica a "cluster ricorrente" (silenziosa, solo statistica interna); la nominazione con un nome vero resta sempre tua conferma

**Risposta Roberto**: **C. Ibrido per livello** — promozione automatica silenziosa a
"cluster ricorrente" (solo statistica interna, nessuna notifica); dare un NOME vero
resta sempre conferma tua esplicita, mai automatica.

---

## Q5 — Evidence accumulation sui fatti profilo: come cresce/decade la fiducia?

**Domanda**: oggi un fatto profilo (`user_profile_facts`) visto 1 volta e uno confermato
in 20 thread su 3 mesi hanno la stessa forza. Come deve funzionare l'accumulo di evidenza?

Opzioni:
- **A. Contatore semplice** — ogni conferma +1, ogni contraddizione -1 (o azzera); sopra soglia N conferme il fatto diventa "consolidato", visibile con più enfasi
- **B. Recency-weighted** — le conferme vecchie pesano meno delle recenti (i fatti di vita cambiano: un lavoro, un interesse); serve un decadimento temporale, non solo un contatore
- **C. Validazione esplicita** — il Profile Validator (già esistente) resta l'unico arbitro: i fatti restano "pending" finché non li confermi/correggi tu, l'accumulo serve solo a dargli priorità di revisione

**Risposta Roberto**: **B. Recency-weighted** — le conferme vecchie pesano meno delle
recenti, decadimento temporale oltre al conteggio: i fatti di vita cambiano (lavoro,
interessi) e un contatore semplice non lo cattura.

---

## Q6 — Deviazioni e alert: cosa merita un'allerta?

**Domanda**: una volta che esiste una baseline (settimane di metriche), il sistema può
notare deviazioni ("questa settimana molto meno sociale del solito", "pattern di sonno
alterato"). Quando e come deve diventare un'allerta attiva verso di te?

Opzioni:
- **A. Solo passivo** — le deviazioni si vedono nella review settimanale/mensile se la apri tu; nessuna notifica push, mai
- **B. Soglia statistica con notifica** — deviazione oltre N deviazioni standard dalla baseline personale → notifica Telegram (come già fa il sistema per altri allarmi)
- **C. Rimandato** — è troppo presto per deciderlo ora: prima si accumula la baseline, la domanda su alert/notifiche si riapre quando c'è abbastanza storia da giudicare cosa è "normale"

**Risposta Roberto**: **C. Rimandato** — troppo presto per deciderlo ora: prima si
accumula la baseline, la domanda su alert/notifiche si riapre quando c'è storia
sufficiente per giudicare cosa è "normale" per te.

---

## Q7 — Oblio concreto: cosa si butta, quando, cosa resta per sempre?

**Domanda**: la retention_class esiste già come colonna (counted/summarized/remembered/
preserved) ma senza enforcement. Con la logica di oggi ("nessun thread esce a mani
vuote"), cosa deve BUTTARE fisicamente l'oblio, e cosa deve restare per sempre?

Opzioni (componibili, non esclusive):
- **A. Cancellazione testo raw** — per i thread "counted" più vecchi di N mesi, elimina text_raw dei turni (privacy + spazio), ma conserva per sempre summary/topics/entities/i conteggi aggregati verso le metriche settimanali
- **B. Solo aggregazione, mai cancellazione** — nulla si cancella mai fisicamente: tutto ciò che serve alla statistica resta, il "counted" significa solo "non mostrato in UI", non "eliminato dal DB"
- **C. Cancellazione totale per i thread senza valore** — sotto una soglia minima (thread davvero vuoti/insignificanti, non solo "counted"), elimina anche il record del thread stesso, non solo il testo — mantenendo però il contributo già versato ai conteggi aggregati

**Risposta Roberto**: Ribalta la cornice della domanda — **il problema di spazio sono
gli m4a, non il testo/DB**. Proposta concreta:
- Non enforcement basato su retention_class del testo: **marcare gli m4a per l'oblio**
  dopo N mesi (nessuna cancellazione fisica finché c'è spazio)
- **Cestino, non cancellazione automatica**: quando lo spazio libero scende sotto il
  30-40%, un tasto esplicito in dashboard svuota il cestino — cancellazione fisica
  degli m4a marcati SOLO su azione utente
- Effetto collaterale accettato da gestire: il play di un turno il cui m4a è stato
  svuotato dal cestino deve fallire con errore gestito (non crash), non impedire lo
  svuotamento
- Testo/JSON/record DB: **mai un problema di spazio** per mesi/anni — non serve
  policy di cancellazione per questi

**Verifica dati** (Claude, 2026-07-17): confermato — l'intero DB Postgres dopo ~2000
segmenti processati pesa **38MB totali** (speaker_turns con embedding vocali inclusi:
13MB). Il testo/entità/summary sono rumore di fondo rispetto agli audio. La cornice
della Q7 (retention_class del *testo*) va quindi ridimensionata: la vera priorità di
"oblio" è la gestione dello storage degli m4a via cestino manuale, non una policy di
cancellazione automatica sui dati testuali.

---

## Q8 — Narrativa lunga (Z5): cosa vuoi leggere in una review settimanale/mensile?

**Domanda**: quando Z5 (week/month review) esisterà, sopra le metriche baseline, cosa
deve produrre come output concreto che consulti tu?

Opzioni:
- **A. Solo numeri/grafici** — dashboard con le curve delle metriche nel tempo (minuti sociali, topic ricorrenti, cerchia attiva), zero narrazione, tu interpreti
- **B. Narrazione breve stile Day Digest** — un paragrafo settimanale/mensile scritto da LLM sopra le metriche aggregate ("questa settimana rispetto alle precedenti: più tempo con X, meno con Y, nuovo topic emergente Z"), come estensione naturale del Day Digest già esistente
- **C. Rimandato** — troppo presto anche per questo: si decide la forma quando le metriche esistono davvero e si vede cosa emerge

**Risposta Roberto**: **B. Narrazione breve stile Day Digest** — paragrafo LLM sopra le
metriche aggregate, estensione naturale del Day Digest già esistente (stesso pattern
map-reduce/prompt versionato, stessa disciplina di grounding sui dati reali).

---

# ROADMAP — sintesi delle 8 risposte

## Direzione generale
**Statistica come fondazione silenziosa, azione come prodotto visibile.** La baseline
(metriche, signal_class, cluster ricorrenti) accumula da subito in background — ogni
settimana persa senza baseline è storia irrecuperabile. Il lavoro che si VEDE nei
prossimi mesi resta sugli impegni/promemoria affidabili (Q1). Ogni automazione tocca
solo lo strato silenzioso: tutto ciò che è VISIBILE all'utente (nome di una persona,
notifiche, cancellazioni fisiche) resta conferma esplicita (Q2, Q4, Q6, Q7).

## Fase 0 — Fondazione silenziosa (nessun costo LLM aggiuntivo, retroattiva su tutto lo storico)
Obiettivo: iniziare ad accumulare baseline SUBITO, anche su dati già esistenti.
1. **signal_class deterministico** (Q2): regola su campi già estratti (importance,
   self_present, persone note vs sconosciute, presenza open_loops) → 3 classi
   actionable/contestuale/statistica. Calcolabile con un UPDATE retroattivo su tutti i
   943 thread esistenti, zero LLM.
2. **Metriche settimanali materializzate** (Q3, tutte e 4 le famiglie): tempo/presenza,
   sociale, contenuto, produttività+qualità pipeline. SQL views/tabelle aggregate per
   settimana, backfillate sullo storico esistente (10+ giorni di dati) e poi aggiornate
   incrementalmente.
3. **Cluster ricorrenti silenziosi** (Q4): promozione automatica di vp ricorrenti a
   "cluster stabile" (puro bookkeeping interno, nessuna UI, nessuna notifica) — dà da
   mangiare alla metrica sociale e prepara il terreno per l'Identity Detective.

**Segnale di avanzamento fase 0 → fase 1**: signal_class calcolato su tutto lo storico
+ prime settimane di metriche materializzate e stabili (nessun bug di aggregazione).

## Fase 1 — Rifinitura ibrida (incrementale, costo LLM marginale)
4. **Stage E promote-only** (Q2): il prompt può alzare (mai abbassare) la signal_class
   di un thread rispetto al default deterministico, con motivo loggato — permette di
   MISURARE quanto/quando l'LLM vede valore che i numeri non vedono, prima di fidarsi.
5. **Evidence recency-weighted sui fatti profilo** (Q5): decadimento temporale oltre al
   conteggio conferme — un fatto confermato 3 mesi fa pesa meno di uno di questa settimana.

**Segnale di avanzamento fase 1 → fase 2**: N settimane consecutive di metriche
raccolte (soglia minima da fissare quando ci arriviamo — servono abbastanza settimane
perché "normale" significhi qualcosa).

## Fase 2 — Narrativa di lungo respiro (gated su storia sufficiente)
6. **Z5 week/month review** (Q8): stesso pattern del Day Digest (map-reduce, prompt
   versionato, grounding rigoroso) ma sopra le metriche aggregate invece che sopra i
   thread grezzi — "questa settimana rispetto alle precedenti: più tempo con X, nuovo
   topic Z, cerchia stabile".
7. **Riapertura Q6 (alert/deviazioni)**: deliberatamente rimandata — si riapre SOLO
   quando Z5 esiste e c'è abbastanza baseline da giudicare cosa è "normale" per l'utente.

## Fuori sequenza — Storage m4a (Q7, ribaltata rispetto alla domanda originale)
Non è una fase della roadmap dei segnali: è manutenzione infrastrutturale, innescata
dallo spazio libero reale su disco, non dal calendario.
- Marcatura "per l'oblio" degli m4a oltre N mesi (nessuna cancellazione finché c'è spazio)
- Tasto "svuota cestino" in dashboard, visibile/attivabile sotto soglia 30-40% spazio libero
- Cancellazione fisica SOLO su azione utente esplicita
- Gestire l'errore di playback per turni il cui m4a è stato svuotato (fallback UI, non crash)
- **Confermato con dati reali**: DB Postgres attuale = 38MB totali dopo ~2000 segmenti
  (speaker_turns con embedding: 13MB) — testo/JSON/record non sono mai un problema di
  spazio per mesi/anni; il costo vero è tutto negli audio.

## Principio di misura trasversale (da Q2, generalizzato)
Ogni componente ibrido (LLM sopra un default deterministico) deve loggare il motivo
quando devia dal default — è l'unico modo per sapere, con evidenza e non a sensazione,
se un livello successivo (LLM più caro, automazione più aggressiva) vale il costo.

---

## Implementazione Fase 0 — 2026-07-18

Deployato (commit `9278844`, DB migrations 0032-0033):
- `conversation_threads.signal_class` (actionable/contextual/statistical) — deterministico, calcolato ad ogni enrichment; backfill retroattivo su 943 thread: 46 actionable, 73 contextual, 824 statistical.
- Tabella `weekly_metrics` — 4 famiglie, popolata su 3 settimane storiche (dati discontinui: 08/06, 06/07, 13/07), worker `weekly_metrics` in TIER2_REGISTRY (giornaliero, refresh ultime 4 settimane).
- **Correzione in corsa**: la tabella `vp_recurrence` (tracciamento cluster per stringa `vp_stable_id`) era strutturalmente rotta — `SESSION_GAP_MIN=30min` rende gli id scope-di-sessione, mai persistenti tra settimane (0 cluster su 866 vp testati). Rimossa (migration 0033) e sostituita: `recurring_vps_seen` si appoggia al `person_id` già risolto da Z7 (`worker_profile_builder.run_social_clustering`), che fa correttamente la fusione cross-sessione via centroide d'embedding.
- **Incidente di processo scoperto**: il commit di ritiro del gate chimera (deciso il 17/07 dopo la tua calibrazione) non si era mai salvato — perso tra un cambio di modello e la compattazione della conversazione. LXC 203 girava ancora con `VP_R_CHIMERA_THRESHOLD=0.70`. Impatto verificato: zero, nessun segmento processato nella finestra. Rifatto e verificato esplicitamente post-deploy (HEAD + valore su disco controllati via SSH, non dato per scontato).
