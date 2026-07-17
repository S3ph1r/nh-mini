# Calibrazione voiceprint — sessione di ascolto 2026-07-17

15 turni attribuiti a vp_R, stratificati per (chimera × fascia confidence).
Per ognuno: apri il thread, trova il turno N, play, e segna `[io]` / `[non io]` / `[misto]`.
Base dashboard: http://192.168.1.203:5173

## Chimera (voci miste) — fascia 0.50–0.65 · previsione: per lo più NON io
- [ ] conf 0.546 — [thread 9771c28f](http://192.168.1.203:5173/thread/9771c28f-4edb-48eb-9870-1dd0b3e157f4) · turno 12 · 09/07 22:49 · "No, stiamo parlando di due belli. Tu sei bello e c'hai un competitor..."
- [ ] conf 0.602 — [thread 92e7de35](http://192.168.1.203:5173/thread/92e7de35-fd5a-4328-9ec1-fb69493fd49d) · turno 17 · 09/07 22:32 · "Io la maestà non te l'ho mai fatta riconoscere."
- [ ] conf 0.605 — [thread 58a3e192](http://192.168.1.203:5173/thread/58a3e192-249a-4fe1-ac52-4055d0691834) · turno 16 · 12/07 23:06 · "Ah, visto che non c'è un cazzo, facciamo tutto tutti..."
- [ ] conf 0.617 — [thread b05b659b](http://192.168.1.203:5173/thread/b05b659b-14e8-4c52-a2ab-97ef9fe303dd) · turno 5 · 12/06 21:10 · "Ve lo lascio a voi con il job o lo faccio io a mano?"

## Chimera — fascia 0.65–0.80 · la zona grigia che decide la soglia
- [ ] conf 0.688 — [thread 3f545ced](http://192.168.1.203:5173/thread/3f545ced-e600-4354-861b-2eaea99cd68d) · turno 87 · 09/07 22:01 · "Se non hai un lavoro, quindi non hai necessità di andare a lavorare..."
- [ ] conf 0.708 — [thread 99a43c1e](http://192.168.1.203:5173/thread/99a43c1e-c487-4db4-affa-8b7bf3d3bc22) · turno 76 · 12/07 05:06 · "Lascio la dolce inconvenza e il bando..."
- [ ] conf 0.722 — [thread 9cb296fd](http://192.168.1.203:5173/thread/9cb296fd-f629-49ed-8889-84ce3e6d7432) · turno 70 · 09/07 19:03 · "Lo decidi te, va a contribuire insieme al tuo TFR..."
- [ ] conf 0.739 — [thread b2e96153](http://192.168.1.203:5173/thread/b2e96153-d30f-4c6d-8ca3-2cc248a9de38) · turno 56 · 09/07 21:05 · "Ci ho dato 400 euro e l'ho detto, glielo risdò indietro..."

## Chimera — fascia 0.80+ · previsione: per lo più IO
- [ ] conf 0.803 — [thread ef5bcb9c](http://192.168.1.203:5173/thread/ef5bcb9c-1960-4ee6-86b2-9a154d99dd1e) · turno 8 · 12/07 02:16 · "Cioè ma io ci ho bisogno di gestore, gestore dovrò trovare..."
- [ ] conf 0.832 — [thread 675e955d](http://192.168.1.203:5173/thread/675e955d-87c7-4110-b96e-b10c048dbe46) · turno 9 · 12/06 14:19 · "Una mail. Ah, con messaggio. Ah, da chi?..."

## Puliti (voce singola) — 0.50–0.65
- [ ] conf 0.621 — [thread 87984e40](http://192.168.1.203:5173/thread/87984e40-c76c-45b2-89dc-bb674aa3f0b9) · turno 1 · 10/06 21:49 · "ah ma non c'entriamo mica noi però è quella della VPN?"
- [ ] conf 0.626 — [thread af5e2835](http://192.168.1.203:5173/thread/af5e2835-a526-4faf-a873-8685631c2aa5) · turno 75 · 10/07 00:47 · "O almeno di riprovare a riaggiornare..."

## Puliti — 0.65–0.80
- [ ] conf 0.685 — [thread 3034906d](http://192.168.1.203:5173/thread/3034906d-e627-4bad-91bb-d572547beb9a) · turno 3 · 12/06 16:31 · "ho capito in Francia preferisco andare a Chicago..."
- [ ] conf 0.754 — [thread 675e955d](http://192.168.1.203:5173/thread/675e955d-87c7-4110-b96e-b10c048dbe46) · turno 3 · 12/06 14:19 · "Quando scorrono i titoli di coda che Mauden è fallita..."

## Puliti — 0.80+ · previsione: IO
- [ ] conf 0.864 — [thread ca6b628d](http://192.168.1.203:5173/thread/ca6b628d-bf8f-4024-801a-346b21846073) · turno 21 · 12/06 11:29 · "Sì, sono da casa loro. ma il problema non è..."

## Cosa decideremo con i risultati
- Se i chimera 0.65–0.80 sono in maggioranza "non io" → alzare VP_R_CHIMERA_THRESHOLD da 0.70 a 0.80.
- Se i puliti 0.50–0.65 sono "io" → la soglia base 0.50 sui turni puliti resta.
- Se emergono "misto" (io + altri nello stesso turno) → conferma che il problema primario è la diarizzazione, non il matching.
- Con la ground truth: decidere se rifare la risoluzione identità sullo storico (re-resolve retroattivo).

---

## ESITO — 2026-07-17, ascolto completato da Roberto

**15/15 turni: voce dell'utente** ("al 99,9% è la mia voce"), in condizioni variabili — a volte degradata, a volte con altre voci che si inframmezzano.

### Decisioni prese
1. **VP_R_CHIMERA_THRESHOLD ritirato** (0.70 → 0.50): su audio 24/7 il flag chimera indica condizioni sporche, non identità sbagliata. Il matcher a soglia 0.50 è risultato preciso su tutto il range campionato.
2. **Best-match resolution mantenuto**: principled — interviene solo quando un cluster di sessione supera 0.82 E batte il match utente (protegge dai casi di label-splitting senza costo di recall).
3. **Semantica di presenza (Stage E v5) mantenuta**: è il vero fix della distorsione osservata — il caso "live streaming" era escalation narrativa su presenza marginale, non misattribuzione.
4. **Soglia base 0.50 confermata** — chiude anche il vecchio quesito "alzare a 0.65": no, taglierebbe turni genuini.
5. Niente re-resolve retroattivo: lo storico delle attribuzioni vp_R è affidabile.
