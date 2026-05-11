---
title: "Profilo Utente — Roberto"
type: user_profile
updated: 2026-05-01
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
- L'agent cita "ARIA e Redis" come se fossero gli unici servizi disponibili — il catalogo è dinamico
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
