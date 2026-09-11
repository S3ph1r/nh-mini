---
title: "Profilo Utente — Roberto"
type: user_profile
updated: 2026-06-11
note: "Aggiornato dall'agent durante le sessioni. NON modificare manualmente se non per correzioni esplicite."
---

# Profilo Utente — Roberto

Questo file viene caricato durante l'INITIALIZATION di ogni sessione.
L'agent lo aggiorna autonomamente quando emergono nuove informazioni sulle preferenze, lo stile o gli obiettivi dell'utente.

---

## Obiettivi Strategici

- **NH-Mini come Personal Assistant autonomo**: sviluppo, deploy e monitoring di nuovi progetti con minimo intervento umano
- **Homelab come piattaforma AI privata**: no vendor lock-in, no dati fuori dalla LAN
- **Qualità cinematografica per DIAS**: benchmark BBC Radio Drama anni '80 e Star Wars Audio Drama (NPR, 1981)
- **Sistema che cresce in modo coerente**: la knowledge del passato deve essere disponibile e applicata ai nuovi sviluppi

---

## Stile Decisionale

- **Prima l'architettura**: ragiona sull'architettura complessiva prima di scendere nel codice
- **Blueprint completo prima di procedere**: vuole vedere le specifiche complete e approvarle prima che l'agent inizi a sviluppare
- **Iterazione su imprevisti**: accetta che le sessioni deviino — ma vuole che ogni deviazione sia tracciata
- **Checkpoint espliciti**: preferisce sessioni con checkpoint intermedi piuttosto che output monolitici alla fine
- **Attenzione ai principi, non solo ai task**: se l'agent viola un principio (es. hardcoda un IP, reinventa qualcosa che esiste), Roberto lo nota e corregge

---

## Preferenze Tecniche

| Area | Preferenza |
|------|-----------|
| API | Python + FastAPI |
| Frontend | Vanilla HTML/JS — no build step, agent-maintainable |
| CSS | Warroom design system (glassmorphism + aurora nordica) |
| Database | Redis per state/queue, PostgreSQL per dati strutturati (se serve) |
| Message bus | Redis su CT120 — già disponibile, usarlo prima di altro |
| Inferenza AI | ARIA su PC139 via Redis — no Google Cloud se evitabile |
| Container | LXC Debian 12 unprivileged + nesting=1 |
| Credenziali | SOPS+Age — mai hardcoded, mai in chiaro, mai nel repo |
| Gateway | CT202 nginx/ngrok — unico punto di ingresso, no nuove esposizioni dirette |
| Monitoring | Dashboard NH-Mini + notifiche push (da implementare) |

---

## Come Vuole Essere Coinvolto

| Fase | Livello di coinvolgimento |
|------|--------------------------|
| Brainstorming | Alto — discussione aperta, domande e risposte |
| Blueprint | Alto — revisione e approvazione esplicita richiesta |
| Sviluppo | Medio — checkpoint ogni sessione significativa |
| Deploy su RT LXC | Alto — approvazione esplicita richiesta |
| Esposizione internet | Alto — approvazione esplicita richiesta |
| Monitoring operativo | Basso — notifica push solo per severity HIGH |
| Fix automatici (restart) | Minimo — l'agent agisce, Roberto riceve report |

---

## Cose che Fanno Scattare la Correzione

- L'agent hardcoda IP, VMID, nomi servizi invece di leggerli da file di config
- L'agent cita "ARIA e Redis" come se fossero gli unici servizi disponibili — il catalogo &egrave; dinamico
- L'agent propone soluzioni esterne (Google Cloud API, nuovo container) senza prima verificare i servizi esistenti
- L'agent "dimentica" di aggiornare la doc dopo una sessione di sviluppo
- L'agent propone un Finalization Ritual posticipato invece di scrivere durante la sessione
- Le regole nel `.cursorrules` enumerano dati specifici invece di puntare a meccanismi dinamici

---

## Conoscenze Tecniche

| Area | Livello |
|------|---------|
| Architettura sistemi distribuiti | Alto |
| Proxmox / LXC / Linux | Alto |
| Python / FastAPI | Medio-alto |
| Redis (pattern BRPOP/LPUSH) | Medio |
| Frontend (HTML/CSS/JS) | Medio |
| AI/LLM (prompt engineering, pipeline) | Alto |
| Networking / nginx | Medio |
| SOPS+Age / secrets management | Medio |

---

## Note di Sessione (aggiornate dall'agent)

- **2026-05-01**: Prima sessione architetturale su NH-Mini come PA. Emersa chiaramente la distinzione "può" vs "fa". Ha corretto l'agent quando ha hardcodato ARIA/Redis invece di puntare al service_catalog dinamico. Questo è il segnale più importante: le regole devono puntare a meccanismi, non enumerare dati.
- **2026-05-01 (Pomeriggio)**: Stabilito il principio dell'immutabilità del Session Journal. L'utente esige che gli errori passati non vengano cancellati per far sembrare il file "pulito", ma marcati come risolti (es. barrati) per permettere l'audit forense e capire l'evoluzione delle scelte.
- **2026-05-01 (Sera)**: Implementata la Fase 3 (Telegram). L'utente ha ribadito il bisogno di **controllo assoluto**: nessun fix autonomo (remediation) deve essere eseguito senza approvazione esplicita via bottone Telegram. Preferenza per bot dedicati e sicuri via SOPS.
- **2026-05-01 (ARIA/Claude)**: Confermato uso parallelo di Claude e Gemini sugli stessi file CT190 — il framework è genuinamente model-agnostic. Roberto verifica sempre lo stato reale prima di agire (controlla i log prima di decidere sul riavvio). Apprezza spiegazione del rischio prima dell'azione. Ha corretto l'agent quando saltava il ritual — i protocolli rigidi valgono anche a sessione in corso.
- **2026-05-11**: Stabilizzata la pipeline ASR su Blackwell (PC 139). Roberto ha richiamato l'agent al rigoroso rispetto degli **Hard Triggers** e dei rituali (Journal, History). È emersa la necessità di allineare i modelli biometrici (vettori 256d vs legacy 192d) e di usare `soundfile` come standard per prevenire crash su Windows/Blackwell.
- **2026-06-11**: Introdotta l'estetica macOS Frosted Glass per SHIFTER. Roberto preferisce uno stile raffinato, inizialmente bianco/azzurro con ripples ampie, successivamente affinato ad un elegante grigio medio-scuro (obsidian/brushed silver) con capsule dei turni dai colori vividi e saturi ad alta leggibilità (giallo per M, verde per P, arancione per REC, azzurro per N).
- **2026-08-16**: Sessione lunga (refactor Stage D/E Lifelog2, riprocessamento storico, primo audit codebase modulo-per-modulo). Pattern emersi con forza:
  - **Verifica in doc PRIMA di cancellare "codice morto"**: quando ho proposto di rimuovere `_is_sunday_early_morning` (orchestrator.py) come dead code, Roberto ha chiesto di controllare prima la documentazione — ha trovato che era design deliberato già segnato "fatto" (scheduling domenicale di Place Detective), non codice abbandonato. Lezione: "orfano nel grep" non equivale a "morto", va incrociato con l'intento documentato prima di agire.
  - **Modifiche non-commento: elenco e discussione prima di eseguire**, anche quando l'agent è autorizzato a procedere in generale. Commenti/doc invece liberi.
  - **Metodo di audit preferito: un modulo alla volta, in ordine di pipeline, mai a macro-argomenti trasversali** — motivazione esplicita: ogni file deve ricevere un passaggio completo prima di passare al successivo, per avere sempre un punto di stop pulito.
  - **Diffidenza sana verso le mie ipotesi plausibili-ma-non-verificate**: mi ha corretto due volte sulla causa di un blocco della suite di test (non era contesa GPU, non era Ollama lento) — non arrabbiato, solo insistente nel chiedere l'evidenza reale prima di accettare una spiegazione. Pattern: quando dico "probabilmente è X", lui chiede sempre "hai verificato?" prima di procedere sulla base di X.
  - **Decisioni infrastrutturali pragmatiche**: su una possibile ottimizzazione GPU (iGPU Proxmox per Ollama), ha scartato il test empirico stesso quando il guadagno atteso era marginale E teneva conto di un fattore sistemico più ampio (non far competere risorse con la GPU reale su ARIA) — preferisce il ragionamento costo/beneficio esplicito alla sperimentazione quando l'esito è già ragionevolmente prevedibile.
  - **Vuole i protocolli NH-Mini rispettati alla lettera anche a sessione già lunga e avanzata** — ha invocato esplicitamente `/doc lifelog2` a metà sessione dopo essersi accorto che il session-journal non era stato aggiornato "durante", non "alla fine" come da regola.
- **2026-09-11**: Sessione lunghissima e multi-fase su Lifelog2 (redesign wrapper ARIA/thinking, taratura Stage D, reprocess generale, audit sistematico, riordino documentazione). Pattern nuovi o rinforzati:
  - **Problemi prima delle soluzioni, sempre**: durante l'audit ha chiesto esplicitamente di "vedere solo i problemi e scrivere una lista di cose da fare dopo" — niente proposte di fix mescolate alla scoperta, una fase separa dall'altra, e i problemi si affrontano uno alla volta anche quando la lista è lunga.
  - **Non si fida di un giudizio del modello (o mio) senza vedere il dato grezzo**: più volte ha chiesto di leggere per intero i turni raw prima di accettare che un thread fosse "corretto" o "sbagliato" (es. i 1966 turni di `0a9250ee`) — lo stesso principio della sessione dell'8/16 ("hai verificato?"), applicato ora sistematicamente al giudizio LLM della pipeline, non solo alle mie ipotesi.
  - **Contesta subito uno scope non minimale**: quando ho proposto che Z7 dovesse fare anche un giudizio media/reale, ha risposto "non capisco perché Z7 deve fare questa distinzione" e mi ha guidato a trovare — nel codice, non a parole — che il campo dedicato (`is_media_persona`) esisteva già e non era mai stato scritto. Non accetta una funzione allargata se il codice stesso suggerisce una separazione di responsabilità più pulita.
  - **Chiede sempre "questo sistema c'è già o va implementato?"** prima di discutere una soluzione — vuole la mappa dell'esistente (anche parziale/dormiente) separata dal design di quello che manca.
  - **Sulla documentazione**: non vuole fusioni/cancellazioni per "pulizia" (rispetta la storia ricostruibile) ma pretende che l'indice e i log restino davvero aggiornati, non solo scritti una volta — ha chiesto esplicitamente due nuovi artefatti ricorrenti (log per sessione, valutazione di avanzamento con conteggio onesto dei problemi) proprio per evitare che la conoscenza accumulata si stalizzi come già successo a `docs/README.md`/`knowledge/`.
  - **Lo stesso pattern dell'8/16 si è ripetuto identico**: session-journal NH-Mini mai toccato "durante" una sessione lunghissima, corretto solo a fine sessione su richiesta esplicita (`/doc`+`/lint`+`/finalize` in sequenza). Probabilmente vale la pena scrivere entry TASK/DECISION più proattivamente quando si opera a lungo dentro un progetto, non solo alla chiusura.
