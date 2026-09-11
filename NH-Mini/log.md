# Wiki Log — NH-Mini Second Brain

Log append-only di tutte le operazioni sul wiki.  
Formato entry: `## [YYYY-MM-DD] tipo | titolo`

> **Convenzione d'ordine — APPEND, crescente.** Le nuove entry si aggiungono SEMPRE in
> fondo al file, dopo l'ultima. Ordine cronologico crescente: la più vecchia in cima
> (subito sotto questa riga), la più recente in fondo. Mai prependere in cima — è la
> convenzione opposta di [[../state/session-journal.md|session-journal.md]] (PREPEND),
> non confonderle.
>
> **2026-09-02**: riordinato meccanicamente l'intero file (era in prepend per la
> maggior parte della sua storia nonostante l'header, con un blocco di backfill
> retroattivo in append cresciuto in coda — le due convenzioni miste producevano un
> ordine non cronologico). Nessuna entry riscritta o persa nel riordino: solo
> riposizionate. Trovata e corretta per strada una corruzione reale distinta: due
> commit consecutivi (`fa51b46`, `b3917ab`, 2026-07-28) avevano scritto il titolo di
> un'entry reale dentro questa riga di template invece che come nuova entry — il
> secondo aveva sovrascritto in-place il testo del primo (violando la regola
> append-only). Testo del primo recuperato da git e ripristinato come entry propria,
> marcata come superata dalla seconda.

## [2026-04-24] init | Inizializzazione wiki LLM

Creato il sistema wiki secondo il pattern LLM Wiki.

**Operazioni:**
- Creato `CLAUDE.md` — schema completo con regole, convenzioni, workflow
- Creato `NH-Mini/` come Obsidian vault wiki
- Creato `index.md`, `log.md`, `overview.md`
- Creata struttura cartelle: `entities/containers/`, `concepts/`, `sources/`

---

## [2026-04-24] ingest | Coda sorgenti ARIA e DIAS — 9 file rimanenti

**Sorgenti raw ingerite:**
- `sviluppi/ARIA/docs/ARIA-Service-Registry.md`
- `sviluppi/ARIA/docs/environments-setup.md`
- `sviluppi/ARIA/docs/master-roadmap.md`
- `sviluppi/ARIA/docs/fish-tts-backend.md`
- `sviluppi/ARIA/docs/qwen3-tts-backend.md`
- `sviluppi/dias/docs/dias-inventory.md` (v2.0)
- `sviluppi/dias/docs/dias-aria-integration-master.md`
- `sviluppi/dias/docs/preproduction-guide.md`
- `sviluppi/dias/docs/technical-reference.md`
- `sviluppi/dias/docs/prompt-evolution.md`

**Pagine create (concepts):**
- `concepts/aria-environments.md` — architettura 3 livelli Python, sm_120, CUDA
- `concepts/aria-tts-backends.md` — Fish vs Qwen3, emotion markers, voice library, workaround
- `concepts/dias-acestep-contract.md` — contratto DIAS↔ARIA, vocabolario Qwen3, HTDemucs
- `concepts/dias-stage0-preproduction.md` — Stage 0, Dashboard, Casting, precedenza vocale
- `concepts/dias-prompt-evolution.md` — tutte le versioni prompt con rationale

**Pagine create (sources):** 9 source summaries (aria-service-registry, environments-setup, master-roadmap, fish-tts-backend, qwen3-tts-backend, dias-inventory, dias-aria-integration-master, dias-preproduction-guide, dias-technical-reference, dias-prompt-evolution)

**Stato:** coda sorgenti svuotata ✅ — 18 sorgenti totali ingerite, 45 pagine wiki

---

## [2026-04-24] ingest | Progetti ARIA e DIAS — documentazione completa

**Sorgenti raw ingerite:**
- `sviluppi/ARIA/.project-context`
- `sviluppi/ARIA/README.md`
- `sviluppi/ARIA/docs/ARIA-master-index.md`
- `sviluppi/ARIA/docs/ARIA-blueprint.md` (v2.0)
- `sviluppi/ARIA/docs/ARIA-API-Contract.md` (v1.0)
- `sviluppi/dias/.project-context`
- `sviluppi/dias/docs/blueprint.md` (v7.0)
- `sviluppi/dias/docs/README.md` (v7.0)
- `sviluppi/dias/docs/dias-workflow-logic.md` (v10.0)
- `sviluppi/dias/docs/production-standard.md` (v3.0)

**Pagine create:**
- `entities/systems/stack-aria.md` — sistema ARIA completo
- `entities/systems/stack-dias.md` — sistema DIAS completo
- `concepts/aria-redis-protocol.md` — nomenclatura Redis (SOT)
- `concepts/aria-task-lifecycle.md` — ciclo vita task ARIA
- `concepts/dias-pipeline.md` — flusso dati 10 stadi
- `concepts/dias-sound-design.md` — paradigma BBC/Star Wars
- `concepts/nh-mini-philosophy.md` — DNA operativo framework
- `sources/aria-project-context.md`
- `sources/aria-blueprint.md`
- `sources/aria-api-contract.md`
- `sources/dias-project-context.md`
- `sources/dias-blueprint.md`
- `sources/dias-workflow-logic.md`
- `sources/dias-production-standard.md`

**Note:**
- Trovate credenziali in chiaro in `sviluppi/ARIA/docs/CURRENT_MISSION_SUMMARY.md` — NON ingerito per policy sicurezza
- `.project-context` DIAS non sincronizzato con blueprint v7.0 — blueprint è SOT
- 9 documenti ARIA/DIAS rimasti in coda (sorgenti non ingerite) — vedi index.md

---

## [2026-04-24] ingest | Infrastructure Map — Container Proxmox

**Sorgente raw:** `knowledge/containers/infrastructure-map.mdc`

**Pagine create:**
- `sources/infrastructure-map.md` — sommario sorgente
- `overview.md` — sintesi homelab (prima versione)
- `entities/containers/ct101-chromadb.md`
- `entities/containers/ct103-observability.md`
- `entities/containers/ct104-minio.md`
- `entities/containers/ct105-postgres.md`
- `entities/containers/ct120-dias-brain.md`
- `entities/containers/ct160-nhi-core.md`
- `entities/containers/ct190-nh-mini.md`
- `entities/containers/ct201-dias-rt.md`
- `entities/containers/ct202-gateway.md`
- `concepts/dependency-map.md`

**Note:** Prima versione di tutte le pagine container. CT106 (WarRoom) e CT107 (nhi-embeddings) e CT170 (nhi-backup) omessi perché fermati/interni senza ruolo attivo — aggiungere se tornano rilevanti. GPU Worker (PC Gaming) documentato nella dependency map come nodo esterno.

---

## [2026-04-24] refactor | NH-Mini diventa control plane — separazione infra reale da legacy

**Sessione di refactor architetturale.** Obiettivo: CT190 come centro di controllo unificato.

**Decisioni prese:**
- CT190 (NH-Mini) = dev center + control plane + dashboard
- CT160 (NHI-CORE v1.1) = legacy, da ritirare dopo port della dashboard
- Infra reale: CT190, CT120, CT201, CT202, PC139 (192.168.1.139)
- Tutto il resto (CT101-107, CT160, CT170, CT200, VM100) = legacy/reference

**Analisi effettuata:**
- NHI-CORE (CT160) scansiona Proxmox via API ogni ora con cron daemon, genera `.cursorrules` e `system-map.json`
- NHI-CORE è indipendente da NH-Mini: NON legge da CT190
- NHI-CORE ha design system `warroom` (glassmorphism) con 4 temi accessibili via API
- DIAS ha 1 progetto attivo: `cronache_del_silicio` in stato `processing`
- CT160 ha disco al 91.5% (670MB liberi) — non intervenire, container in dismissione

**File modificati:**
- `knowledge/containers/infrastructure-map.mdc` — refactored: sezione "Infrastruttura Reale" + sezione "Legacy/Reference"
- `NH-Mini/overview.md` — aggiornato con architettura reale, tabella legacy, roadmap refactor

**Roadmap avviata:**
- Step 1a: Discovery daemon su CT190 (systemd timer, hourly)
- Step 1b: NH-Mini Dashboard (FastAPI + vanilla HTML/JS + warroom CSS da NHI-CORE)
- Step 2: Service catalog (`core/service_catalog.py`)

---

## [2026-04-24] dev | Refactor NH-Mini control plane — completato

**Implementato:**

**Step 0 — Knowledge base**
- `knowledge/containers/infrastructure-map.mdc` refactored: sezione "Infrastruttura Reale" (CT190/120/201/202/PC139) + sezione "Legacy/Reference" (CT101-107, CT160, CT170, CT200, VM100)
- `NH-Mini/overview.md` aggiornato con architettura reale, tabella legacy, roadmap

**Step 1a — Discovery daemon**
- `scripts/nh-discovery.sh` — wrapper che esegue discovery.py + genera `state/system-context.md`
- `/etc/systemd/system/nh-discovery.service` aggiornato per usare il wrapper
- `/var/log/nh-mini/discovery.log` — log daemon
- `state/system-context.md` — nuovo file auto-generato ogni 15min con snapshot infra reale

**Step 1b — Dashboard NH-Mini**
- `web/app.py` — FastAPI backend su :8080 (local LAN only)
- `web/static/index.html` — SPA 4 pagine: Overview, Infrastructure, Projects, ARIA
- `web/static/js/dashboard.js` — logica frontend
- `web/static/css/warroom.css` + `tokens.css` — copiati da NHI-CORE prima della dismissione
- `web/static/css/dashboard.css` — componenti custom NH-Mini
- `/etc/systemd/system/nh-mini-dashboard.service` — abilitato al boot

**Step 2 — Service catalog**
- `core/service_catalog.py` — catalogo con TCP probe: redis, gateway, aria_node, nh_mini_api, dias_api, sops_age
- `core/loader.py` — aggiornato: include service_catalog e system_context_file

**Documentazione aggiornata:**
- `.cursorrules` → v5: nuovi script, nuovi file di stato, dashboard URL, sistema-context.md
- `knowledge/architecture/core-modules.mdc` → nuovi moduli, systemd units, relazione CLI↔API↔Dashboard
- `knowledge/architecture/nh-mini-dashboard.mdc` → creato: doc completa dashboard
- `CLAUDE.md` → aggiunta operazione DEV, raw sources aggiornate, tabella relazioni
- `NH-Mini/index.md` → aggiunto stack-nh-mini, statistiche aggiornate
- `NH-Mini/entities/systems/stack-nh-mini.md` → creato: entity page per NH-Mini stesso

---

## [2026-04-24] dev | nh-new-project.py + Services dashboard tab

**Implementato:**

**Services tab dashboard**
- `web/static/index.html` → nuova voce nav "Services" + sezione `#page-services` con probe button
- `web/static/js/dashboard.js` → `loadServices(probe)`: fetch `/api/services`, render cards con status icon/nome/endpoint/purpose/pattern/consumers/backends/notes
- `web/static/css/dashboard.css` → `.nh-services-grid`, `.nh-service-card`

**nh-new-project.py**
- `scripts/nh-new-project.py` → script interattivo + CLI per creare nuovi progetti in `sviluppi/`
  - Crea struttura: `src/`, `docs/`, `knowledge/`, `state/`, `scripts/`
  - Genera `.project-context` YAML (stesso formato di ARIA/DIAS)
  - Genera `README.md`, `docs/blueprint.md`, `knowledge/index.md`
  - Mostra servizi disponibili da `core/service_catalog.py`
  - Switch workspace automatico via `workspace_manager.py`
  - Appende entry in `NH-Mini/log.md`
  - Flags CLI: `--name`, `--description`, `--stack`, `--services`, `--rt-lxc`, `--yes`, `--no-switch`
- `.cursorrules` → aggiunto `nh-new-project.py` in SCRIPTS REFERENCE
- `knowledge/architecture/core-modules.mdc` → aggiunto `nh-new-project.py` in scripts table + diagrama

---

## [2026-04-24] dev | nh-promote.py — dev→RT LXC promotion script

**Implementato:**

- `scripts/nh-promote.py` → script per promuovere un progetto da `sviluppi/` a un RT LXC dedicato
  - Step 1: Deploy LXC via `deploy_lxc.NHLXCDeployer.deploy()` (VMID auto o manuale)
  - Step 2: rsync `src/` → `/opt/{name}/` sul nuovo container via SSH
  - Step 3: crea e abilita servizio systemd sul RT LXC (opzionale, con `--entrypoint`)
  - Step 4: aggiorna `.project-context` (aggiunge RT Node, imposta phase=production) + log wiki
  - Flags CLI: `project`, `--vmid`, `--memory`, `--cpu`, `--storage`, `--template`, `--entrypoint`, `--no-service`, `--no-code`, `--yes`
- `.cursorrules` → aggiunto `nh-promote.py` in SCRIPTS REFERENCE
- `knowledge/architecture/core-modules.mdc` → aggiunto `nh-promote.py` in scripts table + diagrama

---

## [2026-04-24] dev | DIAS monitoring fix — ngrok 727 + pipeline completion

**Contesto:** Sessione di diagnosi e fix post-completamento di *Cronache del Silicio*.

**Analisi pipeline completata:**
- Verificato completamento Stage D (2174/2174 WAV) e trigger automatico Stage F
- Stage F ha prodotto `/opt/dias/data/projects/cronache_del_silicio/final/cronache_del_silicio.m4b` (270 MB, ~4 min FFmpeg light mode)
- Accertato che `dias:q:5:music` con 2745 items è la coda Sound Factory (Stage D2) — saltata in questo run (pipeline voce-only A→D→F)
- QA campione Stage B/C: istruzioni recitazione eccellenti, numeri → parole perfetti, sistema fonetica inglese funzionale ma con inconsistenze `Nèxus`/`Nèksus`, `fràimuerk`/`freimuork` dovute a chunk processing indipendente

**Diagnosi ERR_NGROK_727:**
- Causa identificata: dashboard DIAS polling ogni 10s × 4-5 endpoint × tab aperto 48h = 20.008 richieste (limite free ngrok 20K/mese)
- Endpoint `/api/projects/{id}` restituisce 273 KB (lista 2174 file) ad ogni poll
- Nessuna richiesta da ARIA/PC139 — tutto traffic era browser dell'utente

**Fix implementati (commit `cc37b86`):**
- Nuovo endpoint `GET /api/projects/{id}/status/live` (~200 bytes) — solo contatori essenziali: status, active_stage, orchestrator_running, voice_done/total
- Frontend: polling cambiato da 10s (full loadData) → 60s (solo /status/live)
- Frontend: Page Visibility API — il polling si ferma quando il tab è nascosto, full reload al ritorno
- Risparmio stimato: ~97% di richieste ngrok in meno per i prossimi run
- Deploy su CT201: git pull + stash conflict risolto + npm build + systemctl restart

**File modificati:**
- `sviluppi/dias/src/api/main.py` — endpoint /status/live
- `sviluppi/dias/src/dashboard/src/lib/api.ts` — fetchProjectLiveStatus()
- `sviluppi/dias/src/dashboard/src/routes/projects/[id]/+page.svelte` — polling + visibility
- `sviluppi/dias/docs/technical-reference.md` — sezione 10 API Hub + monitoring

---

## [2026-04-24] dev | Wiki update — DEV + LINT sessione odierna

**Pagine aggiornate:**

- `entities/systems/stack-nh-mini.md` → aggiunto Services tab dashboard, `nh-new-project.py`, `nh-promote.py` nei componenti; eventi ARIA sync in evoluzione
- `entities/containers/ct202-gateway.md` → routing corretto: solo `/dias/` attivo, grafana/minio disabilitati, nhi obsoleto (CT160 dismissione)
- `index.md` → ultimo aggiornamento aggiornato

**LINT — problemi trovati e risolti:**
- ⚠️ `ct202-gateway.md`: routing NHI→CT160 marcato come attivo — era obsoleto → corretto
- ⚠️ `stack-nh-mini.md`: mancavano Services tab, nh-new-project.py, nh-promote.py → aggiunti

---

## [2026-04-26] dev | DIAS chapter propagation system — rilevamento matematico capitoli

**Contesto:** La pipeline DIAS produceva M4B con 1 solo capitolo invece di N. Causa radice: tre bug distinti in Stage F + nessuna propagazione del `chapter_id` da Stage A a Stage C.

**Analisi effettuata:**
- Stage F leggeva `chapters_list` (inesistente) invece di `chapters` → `chapter_titles` sempre vuoto
- Stage F leggeva field `name` invece di `title` → tutti i titoli stringa vuota
- Stage F usava `chapter_{num:03d}` per ordinal fallback → off-by-1 per Cronache ("Libro Primo" a pos 0 sfasava tutti)
- Stage A suddivideva per word-count senza rispettare i confini capitolo → un chunk poteva attraversare due capitoli
- Stage C hardcodava `"chapter_001"` per ogni scena ignorando i dati Stage A

**Implementato:**

**`src/common/chapter_detector.py`** (nuovo modulo, 483 righe)
- Zero chiamate LLM — rilevamento puro via regex e struttura testo
- 3 strategie per 3 tipologie di libro:
  - Tipo 1 (`Capitolo XIV: Titolo`): prefix-match regex case-insensitive nel sorgente; entità non-heading (es. "Libro Primo") assegnate a char 0
  - Tipo 2 (interi isolati su riga): `re.MULTILINE` con dedup first-occurrence per evitare falsi positivi dal TOC; supporto "Coda N" come numeri speciali 900+N
  - Tipo 3 (ALL-CAPS headings): clustering per dominant 2-word prefix (≥2 occorrenze = serie capitoli); whitelist PROLOGO/EPILOGO
- Cache `chapter_boundaries.json` in project root — non ricostruita a ogni run

**Stage A — `_chunk_by_chapters()` + `_load_or_build_chapter_boundaries()`**
- Testo suddiviso per capitolo PRIMA del word-count chunking
- `IngestionBlock` aggiunge `chapter_id` e `chapter_number` nei JSON micro-chunk
- Fallback invariato (pipeline voce-only senza boundaries) → `chapter_001` per tutto

**Stage C — `_load_block_chapter_id()`**
- Legge `chapter_id` dal JSON Stage A del blocco corrente
- Propaga il valore in ogni scene JSON prodotta

**Stage F — fix fingerprint reader + `ordinal_to_chapter` map**
- `fp.get("chapters", fp.get("chapters_list", []))` — compatibilità entrambe le chiavi
- `ch.get("title", ch.get("name", ""))` — field corretto
- `ordinal_to_chapter`: mappa `{ordinal_num → chapter_id}` costruita estraendo numeri romani dal prefisso di ogni titolo fingerprint
- Rilevamento boundary usa `ordinal_to_chapter.get(num)` invece del vecchio `chapter_{num:03d}`

**Validazione:**
- Cronache del Silicio (Tipo 1, 27 capitoli): 27/27 ✅
- Hyperion — Dan Simmons (Tipo 3, 6 capitoli): 6/6 ✅
- Uomini (Tipo 2, 28 capitoli): 28/28 ✅

**File modificati:**
- `sviluppi/dias/src/common/chapter_detector.py` — nuovo
- `sviluppi/dias/src/stages/stage_a_text_ingester.py` — chunking chapter-aware
- `sviluppi/dias/src/stages/stage_c_scene_director.py` — propagazione chapter_id
- `sviluppi/dias/src/stages/stage_f_audiobook.py` — fix fingerprint + ordinal map

**Wiki aggiornato:**
- `entities/systems/stack-dias.md` → sezione Chapter Propagation System + Evoluzione table

---

## [2026-04-29] dev | Voice pipeline quality analysis — Stage B v1.3 + Stage C v2.5.0

**Obiettivo sessione:** Analisi qualitativa completa pipeline voce v1 (Stage 0→A→B→C→D). Valutazione se le direzioni TTS prodotte sono ottimali per Qwen3-TTS. Versioning prompt e documentazione.

**Analisi condotta:**
- Lettura docs blueprint v7.0, workflow-logic v10.0, preproduction-guide
- Lettura codice reale Stage B `_distribute_micro_chunks`, Stage C prompt builder
- Lettura output Stage C su Cronache del Silicio (campione dialogo + pause)
- Identificazione gap: pause uniformi, valence/arousal/tension non usati, book_language hardcoded

**Modifiche apportate:**

`config/prompts/stage_b/b_semantic_v1.3.yaml` — nuovo
- `{book_language}` dinamico da `fingerprint.json → metadata.language`
- Rinforzo: "rispondi SEMPRE in {book_language} anche su testo misto"

`config/prompts/stage_c/c_monastic_v2.5.0.yaml` — nuovo (v2.4.0 → legacy/)
- Tassonomia pause semantiche a 6 livelli (50ms–2000ms) aggiunta a §1
- Contesto numerico tension/arousal/valence aggiunto al blocco CONTESTO
- Tutte le regole v2.4.0 invariate (modifiche additive)

`src/stages/stage_b_semantic_analyzer.py`
- Lettura `fingerprint.json` e sostituzione `{book_language}` nel prompt

`src/stages/stage_c_scene_director.py`
- Lettura tension/arousal/valence da `block_analysis` e sostituzione nel template

`config/dias.yaml` — stage_b v1.3, stage_c v2.5.0

**Documentazione creata:**
- `sviluppi/dias/docs/dias-voice-pipeline-quality.md` — analisi completa: logica carico cognitivo, design rationale, gap V1-1→V1-4, priorità
- `sviluppi/dias/docs/dias-state-of-gaps.md` — aggiunto V1-0→V1-4

**Wiki aggiornato:**
- `concepts/dias-prompt-evolution.md` → Stage B v1.3 + Stage C v2.5.0 con rationale
- `concepts/dias-voice-pipeline-quality.md` → nuova pagina concept (analisi qualitativa wiki-form)
- `index.md` → +2 entries, stats aggiornate (48 pagine, 12 concepts, 19 sources)

**Deploy:** push git → pull CT201 (stash/pop riuscito, merge automatico)

---

## [2026-04-29] dev | Stage B v1.4.0 — global context injection da Stage 0

**Obiettivo:** Stage B riceve il DNA di Stage 0 (titolo, autore, tono opera, posizione capitolo) invece di inferirlo dal testo grezzo.

**Modifiche apportate:**

`config/prompts/stage_b/b_semantic_v1.4.yaml` — nuovo
- Sezione CONTESTO OPERA in apertura: `{book_title}`, `{book_author}`, `{book_tone}`, posizione `{block_index}/{total_blocks_in_chapter}` capitolo `{chapter_number}`
- Regola aggiunta: "Un blocco neutro in un'opera dark è comunque sotto-tensione"
- ~35 token aggiuntivi per chiamata, schema JSON invariato

`src/stages/stage_b_semantic_analyzer.py`
- `_create_semantic_analysis_prompt(self, text, message)` — aggiunto parametro `message`
- Lettura `fingerprint.json → metadata.title/author/tone` (stesso blocco di v1.3 per language)
- Chapter position da `message.block_index / total_blocks_in_chapter / chapter_number`

`config/dias.yaml` — stage_b_prompt_path → v1.4
`docs/dias-state-of-gaps.md` — Gap V1-5 documentato e chiuso

**Wiki aggiornato:**
- `concepts/dias-prompt-evolution.md` → Stage B v1.4 aggiunto
- `concepts/dias-voice-pipeline-quality.md` → Gap V1-5 risolto

**Deploy:** push git → pull CT201 (stash/pop, merge automatico)

---

## [2026-04-30] dev | Dashboard SSE — real-time pipeline status push

**Feature:** Aggiornamento stato pipeline in tempo reale senza attendere il poll da 10s.

**Modifiche:**
- `src/common/orchestrator.py` — `_publish_state()` fa `redis.publish(dias:events:{project_id})` su ogni transizione (starting/running/paused/completed)
- `src/api/main.py` — endpoint SSE `GET /dias/api/projects/{id}/events`: subscribe Redis pubsub, stream `data: state_change` al browser
- `+page.svelte` — `EventSource` si connette all'SSE stream all'apertura pagina; `onmessage → pollLiveStatus()` immediato
- `+page.svelte` — optimistic update dopo resume click: `orchestratorRunning=true`, `pausedReason=null` prima che il poll risponda

**Fix bug build:** i build su CT201 devono usare `PUBLIC_BASE_PATH=/dias` (ora persistito in `/opt/dias/.env`). Senza questa variabile il SvelteKit `base=''` → `API_BASE=http://host:8000/api` invece di `/dias/api` → HTML al posto di JSON.

---

## [2026-05-01] update | Analisi parameter flow Stage C→D→Qwen3 + incoerenze documentali

**File modificati:**
- `concepts/aria-tts-backends.md` — aggiunta sezione parametri reali TTSRequest (LLM layer + Acoustic layer); marcata come [OBSOLETO] la "Mappa di fallback per emozioni DIAS" (non implementata in Stage D)
- `concepts/dias-voice-pipeline-quality.md` — aggiunta sezione "Analisi Parameter Flow Stage C→D→Qwen3"; corretto status gap `valence/arousal/tension` da ✅ a 🟡 Parziale; aggiunte proposte P1/P3/P4/P5 con rationale; aggiornate priorità sviluppo

**Scoperte chiave:**
- `pace_factor` e `pitch_shift` in Stage C: dead code confermato — design artifact pre-Qwen3, da eliminare (P5)
- `enable_dynamic_params = False` hardcoded in Stage D: blocca energy→temperature (P1)
- `subtalker_temperature` fisso a 0.75: troppo alto, proposta linkarlo ad arousal da Stage B (P4)
- `qwen3_instruct` (LLM prose) è il canale primario verso Qwen3 — temperature è secondario
- Stage B floats (tension/arousal/valence) confermati presenti in block_analysis e accessibili da Stage C

---

## [2026-05-01] dev | Fase 1 piano evolutivo NH-Mini — memoria agent e comportamenti standard

**Sessione architetturale.** Obiettivo: trasformare NH-Mini da sistema "può" a sistema "fa".

**Problema principale identificato:**
- Il Finalization Ritual posticipato non funziona: le sessioni finiscono quando il problema urgente è risolto, non quando "tutto è fatto"
- Le regole nel `.cursorrules` enumeravano dati specifici (es. "verifica ARIA e Redis") invece di puntare a meccanismi dinamici — diventano stantie ad ogni nuovo deploy

**Principio architetturale codificato:**
> Le regole nel `.cursorrules` puntano a meccanismi (script, file, protocolli), MAI a dati specifici (nomi servizi, IP, tecnologie). I meccanismi sono stabili; i dati cambiano.

**Implementato (Fase 1):**

**`state/session-journal.md`** — nuovo file
- Append-only, scritto DURANTE la sessione (non alla fine)
- Tipi entry: START | TASK | DECISION | BLOCKED | RESOLVED | DEVIATION | END
- Staffetta tra sessioni: se la sessione crasha, il record è già lì

**`NH-Mini/user-profile.md`** — nuovo file
- Profilo Roberto: obiettivi strategici, stile decisionale, preferenze tecniche
- Livelli di coinvolgimento per fase (brainstorming alto, monitoring basso)
- "Cose che fanno scattare la correzione" — segnali diagnostici per l'agent
- Sezione "Note di Sessione" — aggiornata dall'agent durante le sessioni

**`.cursorrules` → v6** — modificato
- INITIALIZATION: aggiunto lettura user-profile (step 2) e session-journal (step 3)
- SESSION JOURNAL: regola obbligatoria, punta al file dinamico, non al formato
- REUSE CHECK: punta a `python3 core/service_catalog.py` — MAI enumera servizi hardcoded
- TROUBLESHOOTING PROTOCOL: 7 step sequenziali (grounding → context → history → intent → diagnosi → azione → report)
- AUTONOMY BOUNDARIES: aggiornato (append journal, update user-profile note sessione, restart RT via SSH)
- META: regole per evoluzione sicura del DNA — principio meccanismi/dati, formato proposta modifica

**`NH-Mini/index.md`** — aggiornato
- Aggiunto `[[user-profile]]` nella sezione Overview
- Statistiche aggiornate: 50 pagine totali

---

## [2026-05-01] dev | Fase 2 piano evolutivo NH-Mini — Autonomia e Hard Triggers Protocol

- Completata **Fase 2 (Monitoraggio e Autonomia)** e implementazione **Hard Triggers Protocol**. 
- Creato daemon `heartbeat.py` e script `nh-session-end.py`, `nh-lint.py`. 
- Implementati 6 trigger procedurali (tra cui `/finalize`, `/troubleshoot`, `/doc`) per garantire resilienza della finestra di contesto. 
- Stabilito principio immutabilità Journal storico. Aggiornati `index.md`, `user-profile.md` e `development-history.mdc`.

---

## [2026-05-01] dev | ARIA Telemetria — TelemetryDB SQLite, token Gemini, docs

- Implementato `core/telemetry.py` in ARIA: classe `TelemetryDB` con SQLite WAL, thread-safe, hook in `AriaQueueManager.post_result()`.
- Aggiunto campo `usage` ad `AriaTaskResult` (token cloud provider).
- Aggiornati `gemini_worker.py` (cattura `usage_metadata`), `orchestrator.py` (wiring TelemetryDB), `queue_manager.py` (hook).
- Creato `docs/aria-telemetry.md` (schema, query SQL, garanzie robustezza) e aggiornato `docs/ARIA-blueprint.md` (principio #6 + sezione 16).
- Creato `docs/gemini-free-tier-503-behavior.md` con analisi pattern 503 per fascia oraria/giorno settimana.
- Allineato LXC 190 (ARIA dev) con `git pull` — 3 commit in ritardo, nessun conflitto.
- ARIA RT su PC 139 richiede riavvio per attivare telemetria (in attesa svuotamento coda DIAS Stage B).

---

## [2026-05-01] dev | Fase 3 piano evolutivo NH-Mini — Telegram Push & Approval-Based Remediation

- Implementata la **Fase 3 (Notifiche e Auto-Riparazione)**.
- Creato bot Telegram dedicato (`@Nh_mini_bot`) integrato nel Vault SOPS.
- Sviluppato `core/telegram_bot.py` per invio notifiche push e gestione interattiva tramite Inline Buttons.
- Integrato l'heartbeat con l'invio automatico di allarmi su Telegram, completi di log diagnostici prelevati via SSH dai container target.
- Istituito il **Troubleshooting Approval-Based**: l'agent propone il fix (es. riavvio servizio) su Telegram e lo esegue solo dopo esplicita approvazione dell'utente tramite click sul bottone.
- Ufficializzati i servizi systemd per la dashboard (`nh-mini-api.service`) e per il demone Telegram (`nh-telegram.service`).

## [2026-05-02] dev | Diagnosi crash Qwen3-TTS + reset quota Gemini RPD

- Diagnosticato crash silenzioso Qwen3-TTS su PC 139: causa ARIA orchestrator non in esecuzione (sessione Windows desktop), non crash del server. Manifest corretto, nessuna modifica necessaria.
- Reset manuale daily count Redis (`aria:rate_limit:google:daily_count:2026-05-02`) su LXC 120 per sbloccare pipeline DIAS Hyperion Stage C.
- Quota Google free tier (500 RPD) esaurita alle 19:50 IT — reset atteso a mezzanotte PDT (09:00 IT successivo).

## [2026-05-03] update | Audit end-to-end produzione + stato post-refactor P3/P4/P5

**File modificati:**
- `concepts/dias-voice-pipeline-quality.md` — aggiornati status P3/P4/P5 (✅ Deployed), P1 (🚫 Superceded), P2 (🚫 Skipped); aggiunta sezione "Audit end-to-end produzione 2026-05-03" con tabella parametri e analisi dialogue_notes; aggiornate priorità sviluppo
- `sources/aria-qwen3-tts-backend.md` — aggiunta nota su server di produzione reale

**Scoperte chiave:**
- Server Qwen3 di produzione: `backends/qwen3tts/server.py` (non `scripts/qwen3/qwen3_server.py`)
- Tutti i parametri critici fluiscono correttamente end-to-end post-P4 ✅
- `dialogue_notes` enrichment in ARIA: architetturalmente morto (Stage C → null, Stage D non forwarda)
- Impatto basso: carattere già bake-in in `qwen3_instruct` da Gemini Stage C

---

## [2026-05-03] dev | ARIA Rate Limiter intelligente + Dashboard web porta 8089

- **`rate_limiter.py`** — aggiunto tracking RPM/TPM (sliding window Redis), `report_daily_quota_exhausted()` con lockout fino a reset PDT, log ETA human-readable.
- **`cloud_manager.py`** — distinzione 429 RPD vs RPM, `record_usage(tokens)` post-task per sliding window.
- **`dashboard/server.py`** (nuovo) — pannello web FastAPI porta 8089: gauge limiti Google, semaforo GPU Redis, backend status (locali + cloud Gemini), code Redis live, task recenti SQLite, stats giornaliere.
- **`aria.bat`** — dashboard avviata hidden al boot via `PowerShell WindowStyle Hidden`.
- **`main_tray.py`** — voce menu `🖥️ Apri Dashboard (8089)` aggiunta al systray.
- Killato processo Qwen3-TTS residuo (PID 3228, avviato in sessione precedente per diagnostica).


---

## [2026-05-04] new-project | stratex

**Creato con nh-new-project.py**
- Description: Progetto Stratex
- Stack: Da definire
- Servizi: —
- Path: `sviluppi/stratex/`

---

## [2026-05-05] infra | CT120 rinominato dias-brain → ct120-redis

- Hostname Proxmox aggiornato: `pct set 120 --hostname ct120-redis`
- Rinomina propagata in 17 file: `infrastructure-map.mdc`, `core-modules.mdc`, `service_catalog.py`, `heartbeat.py`, `CLAUDE.md`, 13 pagine wiki
- `ct120-dias-brain.md` → `ct120-redis.md` (riscritta con ruolo corretto: Universal State Bus)
- Commit: `dd996bb`

---

## [2026-05-05] dev | Stratex — Alembic setup + DB verification

- DB CT105 verificato: 10 tabelle, 3843 transazioni, 236 asset, 1769 fx_rates
- Unica delta schema: `assets.country` mancante nel DB → migration `64edb06dccca` applicata
- `models.py`: `raw_data` aggiornato da `JSON` a `JSONB` (allineato al DB reale)
- Credenziali DB salvate in SOPS (`ct105.postgres`)
- `.env` gitignored, `.env.example` committabile, `session.py` senza hardcoded
- `psycopg2-binary` + `alembic` installati nel venv Stratex
## [2026-05-06] dev | Lifelog2: M0 architettura frozen — CT107 embedding service, memory model Z0-Z7, knowledge files

**Decisioni cristallizzate:**
- CT107 promosso da legacy a infra reale: embedding service Ollama mxbai-embed-large 1024d
- DB Postgres separati per persona (lifelog_roberto, lifelog_paola) su CT105
- pgvector: MemoryAtom/Thread vector(1024), Person voiceprint vector(192) via ARIA
- Export bundle: pg_dump + mc mirror → USB portabile (nessun detach realtime)
- V1 data inspected: 2482 memories, audio in chiaro — V2 cifra client-side da giorno 1
- Redis namespace: `lifelog:stream:{stage}` con 12 stream per pipeline A-K

**File modificati:**
- `sviluppi/Lifelog2/knowledge/architecture.md` — riscritta completa
- `sviluppi/Lifelog2/knowledge/memory-model.md` — riscritta completa (Z0-Z7, 13 entità, scoring 7d, retention, pipeline A-K)
- `sviluppi/Lifelog2/knowledge/development-log.md` — entry decisioni M0
- `NH-Mini/entities/systems/stack-lifelog2.md` — aggiornata con architettura frozen
- `knowledge/containers/infrastructure-map.mdc` — CT107 promosso, CT105 aggiornato con lifelog DB

## [2026-05-06] dev | Stratex: Intelligence module — RSS/YouTube scrapers, news feed dashboard, ItemDrawer

## [2026-05-06] dev | Stratex: Tax Center + Settings + Authelia auth

**File modificati/creati:**
- `sviluppi/stratex/frontend/src/components/sections/TaxCenterSection.tsx` — nuovo
- `sviluppi/stratex/frontend/src/components/sections/SettingsSection.tsx` — nuovo
- `sviluppi/stratex/frontend/src/api/hooks/useTaxSummary.ts` — nuovo
- `sviluppi/stratex/frontend/src/api/hooks/useTaxEvents.ts` — nuovo
- `sviluppi/stratex/frontend/src/api/hooks/useTaxTLH.ts` — nuovo
- `sviluppi/stratex/frontend/src/api/hooks/useSettings.ts` — nuovo
- `sviluppi/stratex/frontend/src/api/hooks/useMe.ts` — nuovo
- `sviluppi/stratex/backend/stratex/api/settings.py` — nuovo
- `sviluppi/stratex/backend/stratex/auth.py` — nuovo
- `CT202:/etc/nginx/locations.d/authelia.conf` — nuovo
- `CT202:/etc/nginx/locations.d/stratex.conf` — aggiornato (auth_request)
- `CT202:/etc/authelia/configuration.yml` — nuovo
- `CT202:/etc/authelia/users_database.yml` — nuovo

**Decisioni chiave:**
- Authelia v4.39.19 su CT202 (no Docker, binary, SQLite storage, file-based users)
- Forward-auth pattern nginx → FastAPI read `Remote-User` header → `get_current_user` dependency
- Settings in `user_preferences` key-value table (già in schema DB)

---

## [2026-05-06] ingest | Lifelog2 Project Context
- Initialized Lifelog2 as NH-Mini project.
- Updated service catalog with Stratex and Lifelog2 dev ports.
- Disabled local Redis on LXC 190.
## [2026-05-06] lint | Stratex Wiki Alignment
- Synced stack-stratex.md with real infrastructure (DB on CT105).
- Added sources/stratex-project-context.md.
- Updated components (Authelia, Tax Center) and dev phase.
## [2026-05-06] dev | ARIA PC 139: fix shutdown logic
- Implementata 'Nuclear Option' in `orchestrator.py` per killare processi backend via WINDOWTITLE su Windows.
- Aggiunta terminazione automatica della Dashboard (8089) nello `stop()` dell'orchestratore.
- Pulito `main_tray.py` delegando la chiusura all'orchestratore per coerenza.
## [2026-05-06] dev | ARIA PC 139: GPU Exclusivity & JIT Race Condition Fix
- Implementata esclusività assoluta GPU: ogni avvio di backend locale killa proattivamente qualsiasi altro backend attivo (sia tracciato che orfano via WINDOWTITLE).
- Introdotto flag `_starting` per gestire il warm-up dei modelli ed evitare istanziazioni multiple o kill prematuri durante il boot.
- Sincronizzati `orchestrator.py` e `main_tray.py` su PC 139.
## [2026-05-06] dev | ARIA Dashboard v2.0 - Async Engine & Infinite Scroll
## [2026-05-06] dev | ARIA Dashboard v2.3 Pro & Shutdown Stability
- Rifattorizzazione asincrona della Dashboard con Infinite Scrolling e Metrics Breakdown (Cloud/Local/Audio).
- Implementazione Heartbeat a 5Hz e Live Task Tracking per monitoraggio in tempo reale dei job.
- Risoluzione conflitti porta 8089 con Antigravity IDE (procedura di bind 0.0.0.0 e port forwarding).
- Implementazione Shutdown Robusto in 5 fasi con os._exit(0) per prevenire processi zombie su Windows.

---

---

## [2026-05-07] analysis | Hyperion (DIAS) produzione: telemetria ARIA + proiezione completamento

**Dati telemetria reale** (da `logs/aria-telemetry.db` su PC139):
- Qwen3-TTS: 6.084 task totali (5.973 ok, 111 errori 1.8%), periodo 3–7 maggio
- Throughput effettivo: **70 task/h** (ore attive, RTF medio 6.9, ~47s/scena)
- Audio prodotto: ~667 min = **11.1 ore di audio grezzo** (May 3–7)
- Sessioni: 4 totali, ARIA gira quasi 24/7 per Hyperion (gap >30 min molto rari)
- Avanzamento: **5.964/13.509 scene** (44.1%), rimanenti 7.545
- **ETA completamento: ~11–12 maggio** (4.5 giorni calendario a 24h/die)

---

## [2026-05-07] dev | ARIA + Lifelog2: backend STT Qwen3-ASR-1.7B + Stage B preprocessing

**ARIA PC139 — nuovo backend:**
- Env conda `lifelog-asr`: Python 3.12, PyTorch 2.11.0+cu128 (sm_120 native), qwen-asr 0.0.6, transformers==4.57.6 (pinnato), pyannote.audio 4.0.1 (NON 4.0.2+)
- Modelli scaricati: `qwen3-asr-1.7b` (~4.5 GB) + `qwen3-forced-aligner-0.6b` (~1.8 GB)
- File creati su PC139: `backends/lifelog_asr/server.py` (FastAPI :8087), `backends/lifelog_asr/asr_pipeline.py`, `aria_node_controller/backends/lifelog_asr.py`
- `orchestrator.py` patchato: import, `_lifelog_asr_backend`, `model_logic_ids`, elif branch, `_process_lifelog_asr_task()`
- `backends_manifest.json` aggiornato: entry `qwen3-asr-1.7b` porta 8087, env lifelog-asr, startup_wait 180s
- **Coda Redis:** `aria:q:stt:local:qwen3-asr-1.7b:lifelog` (pattern standard ARIA)
- **Doc ARIA creata:** `sviluppi/ARIA/docs/backends/lifelog-asr.md` (pipeline 3-modelli, confronto WER vs WhisperX, payload schema)
- `ARIA-Service-Registry.md` aggiornato: backend, coda, env, modelli, health check

**Lifelog2 — Stage B implementato:**
- `services/pipeline/stage_b_preprocess.py` — consumer Redis `lifelog:stream:ingest` (XREADGROUP)
- M4A → WAV 16kHz mono via ffmpeg, quality gate (duration, RMS), MinIO upload `normalized-audio/`, DB update, emit `lifelog:stream:asr`
- Testato: 20 segmenti V1 processati con successo; 1 segmento M1 di test rimosso (missing_file)

**Decisioni tecniche:**
- Qwen3-ASR-1.7B scelto su WhisperX: WER IT 5.40% vs ~8-10%, VRAM minore, timestamps integrati
- transformers==4.57.6 PINNATO (5.x degrada accuracy — issue #138)
- pyannote.audio==4.0.1 PINNATO (4.0.2+ pinna torch==2.8.0 e rompe l'env cu128)

---

## [2026-05-07] dev | Lifelog2: MinIO bucket live + 20 segmenti V1 importati in pipeline V2

**MinIO CT104:** bucket `lifelog` creato. Struttura: `raw-decrypted-temp/roberto/{YYYY}/{MM}/{DD}/`.
**V1 import:** 20 .m4a da PC139 D:\LifeLogData\ → MinIO → CT105 lifelog_roberto (RawCapture+Segment) → Redis lifelog:stream:ingest.
**Script:** `sviluppi/Lifelog2/scripts/v1_import.py`. Ground truth V1 disponibile per confronto ASR.
**Prossimo:** Stage A pipeline worker (consumer Redis, conversione WAV, preprocessing).

---

## [2026-05-07] dev | Lifelog2: M1 API ingest live — device register, policy poll, segment upload, status, idempotency

**Endpoint implementati e testati end-to-end contro CT105:**
- `POST /api/v1/devices/register` — crea Device, token hashed SHA-256, disabilita altri device
- `GET /api/v1/devices/me/policy` — Bearer auth, server_queue_depth live da DB
- `POST /api/v1/uploads/segments` — multipart, checksum verify, RawCapture+Segment atomico, Redis emit best-effort
- `GET /api/v1/uploads/segments/{idempotency_key}/status` — status pipeline con memory_atom_id
- Idempotency 409: duplicate upload restituisce segment_id esistente

**File creati:**
- `core/config.py` — aggiunto database_url, redis_url, enrollment_secret per utente
- `core/db.py` — async engine + session factory con lifespan
- `api/deps.py` — get_db, Bearer auth → Device
- `api/routers/devices.py`, `api/routers/uploads.py`
- `api/app.py` — router wiring + lifespan

**Test:** 11 pytest green + integration test live (device, upload, status, duplicate)
**Stato DB:** 1 device, 1 raw_capture, 1 segment inseriti nel test (dati dev su CT105)

## [2026-05-07] dev | Lifelog2: M1 DB live — lifelog_roberto su CT105, schema 14 tabelle applicato, pgvector attivo

**Operazioni:**
- `lifelog` user creato su CT105 Postgres con GRANT su schema public
- `lifelog_roberto` DB creato con extension `vector`
- `alembic upgrade head` completato: 14 tabelle + alembic_version su CT105
- `.env` scritto con LIFELOG2_DATABASE_URL (gitignored)
- CT203 rinviato: sviluppo M1/M2 avviene su CT190:8002 (già nel service catalog)

## [2026-05-07] dev | Lifelog2: M1 SQLAlchemy models — 14 entità, Alembic migration 0001, pgvector, 11 test green

**Prodotto:**
- `src/backend/lifelog2/models/` — package SQLAlchemy 2.0 con 5 moduli (base, auth, pipeline, memory, derived)
- 14 entità ORM: Device, RawCapture, Segment, SpeakerTurn, Place, Person, MemoryAtom, Episode, Day, Thread, Decision, ActionItem, UserProfileFact, MemoryConsolidationRecord
- `alembic/` inizializzato con env.py async, `alembic/versions/0001_initial_schema.py` manuale pgvector-aware
- Embedding: vector(1024) su MemoryAtom/Thread (mxbai-embed-large CT107), vector(192) su Person (SpeechBrain ARIA)
- `tests/test_models.py` — 10 test, tutti green. `pytest` 11/11.
- `pyproject.toml` aggiornato con `pgvector>=0.3`

**Prossimo step:** CT203 approval + `lifelog_roberto` DB su CT105 per applicare migration 0001

## [2026-05-07] dev | Lifelog2: M0 API contracts frozen — Android ingest, Redis Streams, ARIA contract

## [2026-05-09] dev | Lifelog2: Memory Shell (SvelteKit + Tailwind 4) + CT 203 Setup

**Frontend Genesis:**
- Inizializzato progetto SvelteKit 5 in `src/frontend/` con Tailwind 4 (@tailwindcss/vite).
- Configurato Design System "Memory OS": oklch colors (ink theme), typography (Instrument Serif, DM Sans, JetBrains Mono), cinematic effects (glassmorphism, hero glow).
- Implementati componenti core: `Sidebar` (collassabile), `HeroCinematic`, `ScoreRing` (radar chart SVG), `MemoryCard` (blur per sealed memories), `RetentionPill`.
- Layout 3 colonne con Right Rail (Filmstrip/Open/Pipeline) e Topbar Breadcrumbs.

**Backend Alignment:**
- `MemoryAtom` model: aggiornate `retention_class` a `ephemeral | counted | summarized | remembered | preserved | sealed` (allineato al blueprint v2).
- Nuovo router `api/routers/dashboard.py` con endpoint `/dashboard/today` (mock data per test UI) e `/dashboard/pipeline`.
- Vite Proxy configurato per instradare `/api` → `:8002`.

**Infrastructure (CT203):**
- Progettazione **CT203 — Lifelog (v2)** come nodo di Runtime (RT).
- Aggiornata `infrastructure-map.mdc` e creato wiki `entities/containers/ct203-lifelog.md`.
- Registrato `lifelog2_rt` nel `service_catalog.py` (192.168.1.203:8002).

---

## [2026-05-09] dev | ARIA: fix idle timeout orchestrator + riavvio confermato

**Bug risolto — orchestrator.py `_run_loop()` idle branch:**
- Sintomo: backend Qwen3-TTS rimasto attivo 3+ giorni senza spegnersi (DIAS in pausa manuale)
- Root cause: `if not decision:` iterava `known_models` (vuoto quando code Redis assenti) invece di `_procs` — `mark_idle()` non veniva mai chiamato, `shutdown_idle_backends()` non killava nessuno
- Fix: `for mid in list(self.process_manager._procs.keys()):`
- Deploy: commit su LXC 190 (`24c6d32`), push GitHub, pull su PC139. ARIA riavviata.
- Verifica post-restart: clean startup 13:22:42, solo 2 processi Python, nessun backend caricato. Telemetria: 10.951 task totali, ultimo TTS alle 10:20:36.

---

## [2026-05-09] promote | Lifelog2 → CT203

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: Lifelog2
- RT Node: CT203 (192.168.1.203)
- Codice: rsync src/ → 192.168.1.203:/opt/Lifelog2/
- Workaround: applicato 'rootpassword permitted' (prepare-lxc-proxmox.sh)

---

## [2026-05-09] promote | Lifelog2 → CT203

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: Lifelog2
- RT Node: CT203 (192.168.1.203)
- Codice: rsync src/ → 192.168.1.203:/opt/Lifelog2/

---

## [2026-05-09] promote | Lifelog2 → CT203

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: Lifelog2
- RT Node: CT203 (192.168.1.203)
- Codice: rsync src/ → 192.168.1.203:/opt/Lifelog2/

---

## [2026-05-09] promote | Lifelog2 → CT203

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: Lifelog2
- RT Node: CT203 (192.168.1.203)
- Codice: rsync src/ → 192.168.1.203:/opt/Lifelog2/

---

## [2026-05-09] ingest | security-audit-report
- **Audit Sicurezza**: Scansione completa codebase e centralizzazione segreti in SOPS.
- **Bonifica**: Pulizia password hardcoded in Stratex, DIAS e Lifelog2.
- **Nuovo Concept**: [[security-audit-report]]
## [2026-05-09] dev | Cinematic UI Refactor (Memory OS) su CT203
- Migrazione dashboard su CT203:5173
- Implementazione Design System 'Obsidian Depth' (ispirazione Apple TV+)
- Refactor MemoryCard (Poster format) e Hero Cinematic
- Overlay Sidebar con trigger globale z-9999
- Fix Vite proxy per sincronizzazione API Backend
## [2026-05-10] dev | Finalizzazione ARIA ASR Autonomous (MinIO Auth + Lang Mapping)
## [2026-05-10] dev | Lifelog2 Pipeline Evolution
- Refined Stage D into D1 (Voiceprint/Identity) and D2+D3 (Context-aware Enrichment via LLM).
- Defined grouping rules to separate 'Personal' from 'Knowledge' content.
- Updated Master Blueprint and Wiki entity.
## [2026-05-11] dev | Lifelog2: Global Registry + CT203 Live + Android Handoff

**Global Registry implementato e deployato:**
- Nuovo package `registry/` — SQLite `registry.db` sempre online su CT203
- `User` (username, bcrypt, encryption_salt) + `RegistryDevice` (token_hash, expires_at +1y)
- Router `POST /api/v1/auth/register` e `POST /api/v1/auth/login` — token opaque hex, salt per-user fisso
- `get_current_device` migrato da postgres a registry.db; `CurrentDevice` dataclass condiviso tra routers

**CT203 live:**
- systemd `lifelog2.service` creato e abilitato — uvicorn :8002
- CT202 nginx: `location /lifelog/` → CT203:8002 aggiunta, nginx reloadato
- Stack verificato end-to-end via ngrok: `obliging-fitting-cheetah.ngrok-free.app/lifelog/`

**Android handoff:**
- Audit gap app v1 vs contratti v2 — `ended_at` obbligatorio nel metadata upload (era omesso)
- `docs/lifelog2_android_handoff.md` + `docs/lifelog2_backend_handoff.md` documentati
- Flow onboarding: register→409→login (cascata senza schermata dedicata)

**Cleanup (simplify):** dedupati `_hash_token`/`_make_token`/`get_reg_db`, type fix `user_id: str`, guard double-init, path env var.

**Commit:** `01b0f99` (feat) + `4847762` (refactor) su repo Lifelog2. NH-Mini `58d013c`.

---

## [2026-05-11] dev | Lifelog2: Liquid Brain Architecture & Global Registry
- **Architettura**: Definito paradigma Swap-In/Out per l'archivio utente (Guscio vs Cervello).
- **Global Registry**: Progettazione `registry.db` su LXC 203 per Auth (JWT) e provisioning segreti (Salt).
- **Ingest**: Introdotto modello Ingest Parallelo (24/7) e Analisi Seriale (On-Demand).
- **App Android**: Audit completo e creazione documento di handoff per l'upgrade a v2.0 (Metadata JSON + Auth).
- **Legacy Sync**: Verificato parsing GPS/Timestamp dai nomi file .m4a per retrocompatibilità.

## [2026-05-12] dev | Lifelog2: Stage C refactor + voiceprint quality 1.0 + identity resolution design

**Stage C — `stage_c_asr.py` refactored:**
- `_classify_and_resolve()` sostituisce `_resolve_speaker_persons()` — nessun `Person(unknown)` in Stage C (deferred to Stage D)
- `capture_class` (personal/mixed/ambient/unknown) calcolato per ogni segment e scritto su `Segment.capture_class`
- User-first voiceprint matching: l'utente viene cercato per primo, poi le altre persone note
- Drain loop bug fix: `break` nel `for _stream, entries` non usciva dal `while True` — fix con list comprehension + check `if not msgs: break`
- Legacy `user_id` compat: Lifelog v1 usava string "roberto" — ora catch `ValueError` e skip self-match
- Migration `0003_segment_capture_class.py` applicata su CT203

**Voiceprint enrollment:**
- 4 campioni M4A legacy recuperati da PC139 `D:\LifeLogData\user_data\` via SCP
- Script one-shot `/tmp/enroll_legacy_vp.py`: decrypt → WAV → ARIA → weighted average → Person update
- Roberto: voiceprint_quality 0.40 (2 campioni) → **1.00 (6 campioni)**

**Stage B + voiceprint_worker:**
- Stesso drain loop fix applicato a entrambi i worker

**Identity Resolution Design:**
- `docs/lifelog2-identity-resolution-design.md` creato — design completo
- Stack certezza 0–3: Unknown → Candidato LLM → Confermato utente → Enrolled
- Migration 0004 pianificata (identity_level, confirmed_at, confirmed_by, disambiguation_tag, identity_candidates JSONB)
- Piano 6 fasi post-Stage D, stima 4-6 sessioni

**Wiki:** `sources/lifelog2-identity-resolution.md` creato, `stack-lifelog2.md` aggiornato, `index.md` aggiornato.

## [2026-05-13] dev | Wiki Sync: overview.md + service_catalog (ARIA LLM) + infra-map

- `overview.md` aggiornata: CT203 live, CT105/107 promossi, roadmap Lifelog2 A→E.
- `core/service_catalog.py`: aggiunto backend `lifelog_llm` (port 8090) su ARIA PC139.
- `knowledge/containers/infrastructure-map.mdc`: allineato con nuovi backend e date.
- Stato sistema verificato: 10 container running, core infrastructure stabile.

---

## [2026-05-13] dev | Lifelog2: Stage D+E operativi + E2E pipeline A→E testata + /doc sync

- Stage D LLM enrichment (qwen3-14b-q4km) + Stage E embedding (mxbai 1024d) implementati e testati.
- Fast Pipeline A→E formalizzata (greedy workers, Level 1). Async Workers Level 2 definiti (Detective, F, G).
- ARIA: backend LLM (qwen3-14b-q4km @ 8090, llama-server.exe b9119 sm_120) operativo su PC139.
- /doc Lifelog2: `architecture.md`, `development-log.md` aggiornati. Redis Streams table corretta.
- /doc ARIA: `aria-state-of-gaps.md` (A0-3 resolved), `ARIA-Service-Registry.md` (LLM backend + coda).
- `stack-lifelog2.md`: M4.5 Stage E added, M5 architettura Level 2 descritta.
- Redis cleanup: 2 callback orfane `aria:result:llm:*` eliminate.

---

## [2026-05-13] dev | Lifelog2 Stage D + ARIA qwen3-14b-q4km — E2E completo

- **Stage D Blueprint v1**: cristallizzato `Lifelog2/docs/lifelog-stage-d-blueprint-v1.md` — pipeline per segmento, timing (21s warm), modalità streaming/batch, worker detective, retroactive indexer.
- **Prompt versioning**: creati `prompts/config.json`, `prompts/stage_d_enrich_v1.txt`, `prompts/stage_d_detective_v1.txt`. Nessun prompt hardcoded in codice.
- **AriaLLMClient aggiornato**: modello `qwen3-14b-q4km`, queue `aria:q:llm:local:qwen3-14b-q4km:lifelog`, messages format con system prompt, thinking=False.
- **Stage D worker**: `stage_d_enrichment.py` riscritto — carica prompt da file, usa MemoryAtom schema v1 (event_type, speaker_turns_annotated, temporal_refs, confidence in entities_json).
- **ARIA backend qwen3-14b**: `launcher.py`, `lifelog_llm.py` (health /health, reasoning_content, /no_think), `backends_manifest.json` (porta 8090), `install_lifelog_llm.ps1`.
- **E2E test superato**: segmento 3599a424 (AI + mental health, Italian, 5 min) — MemoryAtom di alta qualità in 21s, 447 token, confidence 0.85.
- **Wiki aggiornata**: [[stack-lifelog2]] (M4 ✅, pipeline, identity resolution 3 livelli), [[stack-aria]] (qwen3-14b-q4km aggiunto).

## [2026-05-13] dev | Lifelog2 Fast Pipeline formalizzata — Stage D greedy + Stage E implementato

- **Architettura consolidata**: Fast Pipeline = A→B→C→D→E per ogni segmento. Worker greedy (count=100). Level 2 (Detective, F, G, Retroactive) completamente asincroni.
- **Stage D refactor**: count=1→100 (greedy batch), passa `normalized_audio_key` a Stage E, fix typo pipeline_status.
- **Stage E nuovo**: consumer `lifelog:stream:embed`, embedding mxbai-embed-large via CT107, WAV delete da MinIO, `pipeline_status="consolidated"`.
- **config.py**: aggiunti `ollama_url` e `ollama_embed_model` (override via env).
- **Confine pipeline**: dopo Stage E il ricordo è autosufficiente — testo, voiceprint 256d, MemoryAtom, embedding 1024d. I worker Level 2 leggono questi dati senza bisogno di riaprire audio.

## [2026-05-14] dev | Lifelog2: WhisperX large-v3 integrato in ARIA + E2E A→E validata + /doc sync

- WhisperX large-v3 sostituisce Qwen3-ASR-1.7B come backend STT primario di Lifelog2 (ARIA porta 8091, env `lifelog-whisperx`).
- Fix orchestratore ARIA: `model_logic_ids` aggiornato, `threading.RLock`, handler `LifelogWhisperXBackend` deployato.
- Pipeline A→E misurata: **~91s warm** su 299s audio (3.3× realtime). Bottleneck: GPU switch 35s (71% Stage D).
- Headroom Level 2: ~209s liberi per segmento → ~17 chiamate LLM warm nel budget. Worker L2 (Detective, F, G): solo blueprint, zero codice.
- /doc: `aria-state-of-gaps.md` (A0-4 resolved), `ARIA-blueprint.md` (§4 backends STT+LLM), `Lifelog2/knowledge/development-log.md`, `architecture.md`, `api-contracts.md` aggiornati.

---

## [2026-05-14] dev | Lifelog2: WhisperX large-v3 integrato in ARIA + E2E A→E validato

**WhisperX backend ARIA completo:**
- `backends/lifelog_whisperx/server.py` (FastAPI :8091, float16 Blackwell-safe, soundfile bypass ffmpeg)
- `aria_node_controller/backends/lifelog_whisperx.py` (LifelogWhisperXBackend handler class)
- `aria_node_controller/config/backends_manifest.json`: entry `whisperx-large-v3` porta 8091, env lifelog-whisperx, startup_wait 150s
- `orchestrator.py`: aggiunto `whisperx-large-v3` a `model_logic_ids` (era mancante → fix critico), `_process_asr_task` routing per model_id, import LifelogWhisperXBackend
- `stage_c_asr.py`: coda → `aria:q:stt:local:whisperx-large-v3:lifelog`, model_id → `whisperx-large-v3`
- Docs: `sviluppi/ARIA/docs/backends/lifelog-whisperx.md` (nuovo), `ARIA-Service-Registry.md` aggiornato

**Bug fix ARIA shutdown hang (threading.Lock → RLock):**
- `_ensure_single()` teneva `self._lock` (Lock non-reentrant) e chiamava `_kill_proc()` che acquisiva stesso lock → deadlock
- Fix: `self._lock = threading.RLock()` + taskkill timeout=5 + pre-join `_run_loop`

**E2E test A→E con WhisperX (segmento 14cc6f03, 299.6s audio):**
- Stage B: 0.4s (decrypt + WAV normalize)
- Stage C → WhisperX: 16.2s (1120 chars, 1 turn, lang=it)
- Stage D → qwen3-14b-q4km: ~12s (MemoryAtom `dfdfb622`, importance=0.40, retention=summarized)
- Stage E: embedding 1024d consolidato
- Total A→E: ~1m32s

**Confronto WhisperX vs qwen3-asr-1.7b (stesso audio):**
- qwen3-asr: 3987 chars, 35 turn, pesanti hallucinations (testo su legal AI inventato, ripetizioni multiple)
- WhisperX: 1120 chars, 1 turn, trascrizione corretta (conversazione auto elettrica, freno motore)
- WhisperX nettamente superiore su audio bassa qualità (SNR=6.1, speech=27%)

**Output salvati:** `/tmp/baseline_outputs/` (qwen3asr + whisperx transcript JSON + memory atom)

---

## [2026-05-15] dev | Lifelog2: Control Plane v2 — Telemetria SQLite + Pipeline Dashboard + CT203 timezone fix

- `core/telemetry.py` — SQLite writer 5 tabelle (upload_events, pipeline_events, grouping_runs, service_events, snapshot)
- Stage B/C/D/E/F instrumentati con timing `time.perf_counter()` + write telemetry
- `api/routers/telemetry.py` — 6 endpoint `/telemetry/*`
- `api/routers/orchestrator.py` riscritto — `/status` (Redis+Postgres reale), `/logs` (merge worker log file)
- `pipeline/+page.svelte` — Control Plane v2: Workers, Streams, DB Stats, Telemetria, Log Terminal
- CT203 timezone fixata a `Europe/Rome (CEST)` via bypass D-Bus (timedatectl bloccato)
- Backfill telemetria da log file: 163 upload, 165 Stage B, 34 C, 39 D/E, 2 grouping runs

## [2026-05-15] lint | Lifelog2 — 5 issues fixed

- **stack-lifelog2.md**: rimosso "pending approval" da CT203 (live 2026-05-09); aggiornato diagramma pipeline C (WhisperX primary) e D (v5, non "v1 completo").
- **service-asr-blackwell.md**: aggiunto WhisperX large-v3 come primary Lifelog2 backend (2026-05-14); Qwen3-ASR-1.7B degradato a standby.
- **sources/lifelog2-project-context.md**: rimosso "pending approval" da CT203.
- **concepts/lifelog2_dev-pattern.md**: aggiornato Stage A/B/C → B–E + orchestrator; era orfano. Aggiunto in `index.md`.

## [2026-05-15] dev | Lifelog2: Orchestrator Stage F + Stage D v5 (action_items/decisions) + Stage B metrics fix

- **Orchestratore integrato con Stage F**: Stage F gira come `asyncio.create_task` parallelo al loop B→E. Ogni 30min (`GROUPING_INTERVAL_S`), primo run dopo 60s startup delay. `asyncio.Event` per trigger manuale via Redis `{"cmd": "run_grouping"}`. Status API aggiornata con campo `grouping`.
- **Stage D v5**: aggiunge `action_items` e `decisions` agli output del MemoryAtom. Regole: solo task concreti, no media passivo, max 5 ciascuno. `_NOISE_PHRASES` frozenset filtra risposte noise LLM. `_parse_str_list()` helper condiviso.
- **Rerun Stage D su 19 atom**: script `scripts/rerun_stage_d_enrich.py` — lettura blob MinIO, LLM call, update solo action_items/decisions. 7/19 atom hanno dati non vuoti. Nota: path MinIO usa device UUID, non user_id; query usa `memory_atom_id.is_not(None)` (non pipeline_status).
- **Stage B metrics-on-discard fix**: `_reject()` ora persiste rms_db/snr_db/speech_ratio/duration_seconds anche sui segmenti scartati. Prima aveva NULL in DB. Tutti i call site aggiornati.
- **Wiki**: `stack-lifelog2.md` aggiornata con Orchestrator section, Stage D v5 details, Stage B fix note, milestone M4/M5 aggiornati.

## [2026-05-15] dev | Lifelog2: Stage F 4-pass sliding window + bug prefilter fix + Stage D v4

- **Stage F implementato** (4-pass: temporal pre-filter → LLM boundary → split → synthesis). Prompts versioned: `stage_f_boundary_v1.txt`, `stage_f_split_v1.txt`, `stage_f_episode_v1.txt`.
- **Bug `_temporal_prefilter` fixato**: `current_end` non si aggiornava all'apertura di un nuovo gruppo temporale → 17 gruppi invece di 8. Fix: `current_end = row["ended_at"]` nel branch `break`.
- **Stage D v4**: regola monologue vs podcast/broadcast aggiunta. Tono educativo/informativo a speaker unico → `podcast`, non `monologue`. Importance MAX 0.5 per media.
- **Alembic 0004**: `episode_id` su `memory_atoms`, `capture_class` su `episodes`. Applicata su CT203.
- **Risultato Stage F su 19 atoms**: 8 gruppi temporali → 12 episodi scritti (vs 18 errati di prima).
- **AtomRef**: sub-atom references (`from_turn`, `to_turn`) per episodi che tagliano a metà un atom.
- **Running episode summary**: contesto compresso max 180 token mantenuto tra le call LLM sliding window.

## [2026-05-16] dev | ARIA FLUX.2-klein-4B backend + Lifelog2 Stage G cover generation

**Stack implementato**
- `envs/flux-aria`: conda env Python 3.11 + PyTorch 2.7.0+cu128 + diffusers 0.39.0.dev0 (Flux2KleinPipeline live) + optimum-quanto 0.2.7 + transformers 5.8.1
- `backends/flux_imagegen/server.py`: FastAPI port 8092, Flux2KleinPipeline + Qwen3-4B text encoder INT8 (optimum-quanto, 7.5 GB → 3.75 GB VRAM) + transformer BF16 (~11 GB totale RTX 5060 Ti 16 GB)
- `backends_manifest.json`: entry `flux2-klein-4b` (port 8092, env=flux-aria, startup_wait=240)
- `aria_node_controller/backends/flux_imagegen.py`: FluxImageGenBackend HTTP adapter → localhost:8092
- `orchestrator.py`: `_process_flux_task()` + dispatch su `model_type=imagegen` + model_logic_ids aggiornato
- **Modello scaricato**: `data/assets/models/flux2-klein-4b/` (~15.8 GB — text_encoder 8 GB, transformer 7.75 GB, VAE 168 MB)

**Lifelog2 Stage G**
- `alembic/0006`: ADD `visual_prompt TEXT` a `episodes`
- `models/memory.py`: campo `visual_prompt` su Episode
- `prompts/stage_f_episode_v2.txt`: Pass 4 ora genera anche `visual_prompt` (20-40 parole inglese, stile flat minimalista)
- `core/aria_imagegen.py`: AriaImageGenClient (Redis queue `aria:q:imagegen:local:flux2-klein-4b:lifelog`)
- `stage_g_covers.py`: worker batch, processa episodi con visual_prompt ma senza cover_image_key
- `orchestrator.py` Lifelog2: `_covers_loop()` + `run_covers` command, interval=60min, startup delay=90min

**Architettura GPU swap**
- 1 swap totale: Stage F (Qwen3-14B warm) genera visual_prompt; Stage G swappa su FLUX
- Greedy batch: tutti gli episodi senza copertina in una sessione → minimizza swap frequency

**Test end-to-end (2026-05-16 07:00)**
- FLUX server avviato su PC 139, caricamento completo in 192s (quantizzazione INT8 63.6s)
- VRAM allocata: **12.8 GB** su 16 GB (3.2 GB headroom)
- 2 generazioni test OK: 12.6s (JIT cold), 6.4s (warm), 6.4s (stable)
- PNG 512×512 verificati in MinIO `aria-warehouse/lifelog-covers/` (bucket policy public GET impostata)
- URL diretto: `http://192.168.1.104:9000/aria-warehouse/lifelog-covers/test-episode-001.png` ✅

## [2026-05-16] dev | Lifelog2: Frontend Views B2–B7 + Background palette + Transcript endpoint

**Background & palette**
- `bg.jpg` (529KB, AI-generated) come sfondo globale su `html` element (workaround `overflow:hidden` SvelteKit)
- Gradiente scuro su `body` come overlay semitrasparente
- `glass`, `glass-sidebar`, `glass-card` opacity alzate (~0.65–0.82) per leggibilità su bg image
- `--color-text-3` alzato da `0.55` a `0.72`, `--color-text-2` da `0.80` a `0.90`
- `--color-surface-*` opacity alzate a `0.50–0.70`

**B2 — Day View** (`/day/[date]`)
- Redirect automatico da `/day` a data odierna (timezone Europe/Rome)
- Episodi espandibili (click header), atom row cliccabili con snippet + topic chips
- Header sticky con stats (episodi, atoms, durata, action items, decisioni)
- Navigazione prev/next giorno
- `has_transcript` flag su atom — mostra link "◎ Trascrizione →" se presente

**B3 — Map View** (`/map`)
- Leaflet dinamico (import in `onMount`), CartoDB Dark Matter tiles
- CircleMarker colorati per retention, dimensione per importance_score
- Detail panel slide-in (click marker), filtro periodo 30g/3m/1a/tutto
- `GET /dashboard/map?days=N` — join MemoryAtom + RawCapture su GPS

**B4 — Sagas View** (`/sagas`)
- Library di tutti gli episodi, raggruppati per data_label, filtrabili per capture_class + tag
- Load-more pagination (limit 30), importanza bar per episodio
- `GET /dashboard/sagas?limit&offset&capture_class&tag`

**B5 — People View** (`/people`)
- Directory persone da tabella `persons`, badge identity_level (0–3)
- Avatar con initials, indicator voiceprint dot se enrolled
- Conteggio episodi per persona (tally Python su `episodes.person_ids` JSONB)
- Filtro per livello (enrolled/confirmed/candidati/anonimi)
- Card espandibile con first_seen/last_seen/confidence/candidates JSON
- `GET /dashboard/people`

**B6 — Timeline View** (`/timeline`)
- Linea del tempo verticale con spine SVG, raggruppata per mese/anno
- Dot colorato per capture_class dell'episodio, importance bar
- Tutti gli episodi in una fetch (limit 500), buildGroups in frontend
- Link a `/day/{date_key}` per ogni episodio

**B7 — Transcript View** (`/transcript/[id]`)
- Legge `raw_transcript_key` da MemoryAtom, scarica JSON da MinIO
- Vista turni speaker (`Voce A`, `Voce B`, …) con timestamp mm:ss
- Vista testo completo toggle
- Filtro per singolo speaker
- Sidebar: riassunto, topics, action_items, decisioni, stats
- `GET /dashboard/transcript/{atom_id}`

## [2026-05-16] dev | Lifelog2: Identity Resolution — Migration 0005 + Worker Detective + raw_transcript_key

**A1 — raw_transcript_key su MemoryAtom**
- Campo `raw_transcript_key VARCHAR(512)` aggiunto al modello `MemoryAtom`
- Popolato in Stage D con la chiave MinIO del transcript JSON raw
- Formato: `transcripts/raw/{user_id}/{year}/{month}/{day}/{segment_id}.json`
- Necessario per Stage F Pass 3 (split intra-atom) e per la Transcript View

**A2 — Migration 0005 (Identity Resolution fields)**
- 5 nuove colonne su `persons`: `identity_level SMALLINT DEFAULT 0`, `confirmed_at`, `confirmed_by`, `disambiguation_tag`, `identity_candidates JSONB`
- Index su `identity_level`
- Backfill: `WHERE relationship_type='self' AND voiceprint_embedding IS NOT NULL` → level=3, confirmed_by='enrollment'
- Roberto Guareschi: level=3 (enrolled), voiceprint_quality=0.6, confermato manualmente
- `Person` model aggiornato con `SmallInteger` + 5 nuovi campi Mapped

**A3 — Worker Detective**
- Subprocess dell'orchestrator (come Stage F), delay 120s startup, ciclo 15min
- Legge ultimi 8 atom (Redis checkpoint `lifelog:detective:last_atom_ts`)
- Chiama LLM qwen3-14b: estrae nomi di persone dai transcript, produce `identity_candidates` JSONB
- Mai scrive `first_name`/`last_name` — solo `identity_candidates` (level=1)
- Dedup via JSONB `NOT (identity_candidates @> :dedup_check::jsonb)`
- Trigger manuale: `{"cmd": "run_detective"}` via Redis
- Telemetria: `record_stage("detective", "batch", "ok", elapsed_s, extra={atoms, candidates})`

## [2026-05-17] dev | Lifelog2 Memory Atom Covers & Fallback UI

## [2026-05-17] doc | /doc aria — FLUX backend + 0.0.0.0 fix + imagegen gaps

- **docs/ARIA-Service-Registry.md**: aggiunta coda `aria:q:imagegen:local:flux2-klein-4b:lifelog`, env `flux-aria`, sezione FLUX endpoint + DELETE pattern + nota 0.0.0.0 fix.
- **docs/aria-state-of-gaps.md**: gap A0-5 (no imagegen backend → resolved 2026-05-16), gap A0-6 (backends 127.0.0.1 → resolved 2026-05-17).
- **docs/ARIA-blueprint.md**: sezione Image Generation aggiornata con contratto reale FLUX.2-klein-4B (payload, callback output, DELETE cleanup pattern).

## [2026-05-17] doc | /doc lifelog2 — Stage G orchestratore + git alignment + ARIA 0.0.0.0

- **knowledge/architecture.md**: aggiornato package tree (stage_g_covers.py, orchestrator.py, worker_detective.py), tabella Level 2 (Stage G covers trigger-only), sezione Stage G flow e orchestratore async loops.
- **knowledge/api-contracts.md**: Sezione 4 ARIA Contract riscritta con contratti reali (ASR HTTP, LLM HTTP, FLUX Redis queue). Redis commands manuali per trigger stage. Campo `covers` in orchestrator status JSON.
- **knowledge/development-log.md**: entry 2026-05-17 (Stage G orchestratore, aria_imagegen fix, visual_prompt upgrade, detective bugfix, ARIA 0.0.0.0, git alignment).
- **NH-Mini/log.md**: questa entry.
- **Pagine wiki toccate**: [[ct203-lifelog]], [[service-asr-blackwell]]

## [2026-05-17] dev | FLUX no-MinIO pipeline completa + Git ARIA allineato + Stage G aggiornato

**Stato finale sessione:**
- **Git ARIA** (commit `9ed374a`, master PC 139 = origin): FLUX no-MinIO pipeline commissionata, WhisperX commits inclusi, push OK a `S3ph1r/ARIA`.
- **Git Lifelog2** (commit `cd069c9`, main CT203): `stage_g_covers.py` aggiornato.

**Architettura FLUX definitiva (no MinIO per immagini):**
- `backends/flux_imagegen/server.py`: salva JPEG in `ARIA_OUTPUT_DIR`, serve via asset server (port 8082), espone `DELETE /output/{filename}` per cleanup.
- `aria_node_controller/backends/flux_imagegen.py`: ritorna `job_id` + `image_url = http://{local_ip}:8082/{job_id}.jpeg`; `local_ip` passato dall'orchestratore.
- `stage_g_covers.py` (CT203): scarica da asset server, uploada in MinIO lifelog bucket (`covers/{date}/{ep_id}.jpeg`), chiama `DELETE http://192.168.1.139:8092/output/{job_id}.jpeg` per cleanup ARIA.

**ARIA richiede riavvio** per attivare:
- `orchestrator.py`: `ModelProcessManager.__init__` ora ha `self.local_ip = get_node_ip()` → `_health_check` bypassa Firebase Studio port-forward.
- `backends_manifest.json`: `startup_wait` Qwen3-14B = 600s.

**Stato Lifelog2 (14 episodi, 0 cover):** pipeline pronta per E2E. FLUX non ancora testato in produzione — repair script per 11 episodi senza visual_prompt da ri-avviare dopo restart ARIA.

## [2026-05-17] dev | ARIA health-check fix — Firebase Studio port conflict

- **Bug root cause**: Firebase Studio (Antigravity IDE Google), connesso via Remote SSH a LXC 190, fa port-forwarding automatico dei port 8090/8091/8093 su `127.0.0.1` del PC 139. L'orchestratore ARIA health-checkava `localhost:8090` e riceveva risposta da Firebase Studio invece di `llama-server` → timeout → loop infinito di riavvii Qwen3-14B.
- **Fix** (`orchestrator.py`, `_health_check`): `health_url.replace("localhost", self.local_ip)` — usa IP esterno (`192.168.1.139`) al posto di `localhost`, il traffico bypassa il loopback tunnel. `backends_manifest.json` invariato.
- **Problema scope**: `_health_check` è metodo di `ModelProcessManager`, non `NodeOrchestrator` — `self.local_ip` non esisteva. Fix: aggiunto `self.local_ip = get_node_ip()` in `ModelProcessManager.__init__`.
- **startup_wait Qwen3-14B**: 120s → 600s (il modello richiede ~10 min per caricarsi in VRAM).
- **Documentazione**: [[ARIA-Service-Registry]] aggiornato (Note Operative, Health URLs, FLUX backend); questo log; session-journal.

## [2026-05-20] dev | Lifelog2 Stage B CAMCORDER fix + voiceprint ottimizzato + rematch script

- **Stage B fix**: soglie quality gate differenziate per `audio_source` (CAMCORDER/ambient vs VOICE_RECOGNITION). I segmenti ambient non vengono più scartati per SNR basso.
- **Rejected M4A**: `_reject()` ora salva l'M4A in MinIO `quality-rejected/` prima di eliminarlo. Conservati per analisi qualità e oblivion scheduler futuro.
- **WAV lifecycle**: chiarito che Stage E è l'unico owner della WAV deletion (reverto errore su Stage C).
- **Voiceprint Roberto**: re-enrollment con clip 30s ottimizzato (offset 23.2s, senza silenzio). Match 25/7650 turns (top score 0.981). Audio in `voiceprints/enrollment_optimized/roberto_30s.m4a`.
- **Script `rematch_voiceprint.py`**: classificazione personal/mixed/ambient con `--threshold` e `--dry-run`. Deployato su CT203.
- **Wiki aggiornata**: `architecture.md`, `development-log.md`, `ct203-lifelog.md`.

## [2026-05-20] doc | audit lifelog2 — allineamento dev-runtime & verifica stato
- **Infrastruttura**: Verificato lo stato dei 4 servizi systemd attivi su LXC 203 (`lifelog2`, `lifelog2-ui`, `lifelog2-orchestrator`, `lifelog2-voiceprint`), tutti attivi e operativi.
- **Git Alignment**: Verificato il perfetto allineamento tra LXC 190 (dev) e LXC 203 (runtime) sul commit `330b864` (`feat(ui): /tasks page + stats popover + sidebar Tasks link`).
- **Wiki Update**: Aggiornato [[stack-lifelog2]] inserendo la nuova vista `/tasks` nelle tabelle e allineando lo stato dello sviluppo (M7: Frontend).
- **Gap Analysis**: Identificate le aree mancanti da completare per le prossime milestone: RAG / Ask Search (`/ask` e relative API), Vault/Retention (`/vault`), e Month View (`/month`).

## [2026-05-21] dev | Lifelog2 audio playback — 5 bug chain, dynaudnorm, MP3 streaming

- **Endpoint `GET /api/dashboard/segment/{id}/audio-clip`**: stream MP3 per speaker turn, TTFB ~60ms via `asyncio.create_subprocess_exec` + `dynaudnorm=g=15:f=500:r=0.9` (far-field normalization).
- **5 root cause chain risolti**: (1) far-field silenzioso −33dBFS → dynaudnorm; (2) browser timeout su clip lunghi → streaming subprocess; (3) Svelte 5 `$state` Proxy su HTMLAudioElement → TypeError silenzioso; (4) WebM/Opus OpusHead EBML incompleto in pipe → switch a MP3; (5) Chrome buffer interno stantio → `new Audio()` + cache-buster `?_t=`.
- **Gotcha documentato**: mai wrappare HTMLMediaElement in `$state` Svelte 5.
- **knowledge aggiornato**: `architecture.md`, `api-contracts.md`, `development-log.md` (Lifelog2).
- **history_manager**: entry FEATURE aggiunta (commit `68add51`).

## [2026-05-22] dev | Lifelog2 Strato V — LLM Validation Pass (Profile Intelligence)

- **Prompt creato**: `src/backend/lifelog2/prompts/stage_z7_profile_validator_v1.txt` — istruisce Qwen3 su ARIA a classificare fatti di profilo in 5 verdetti (`valid`, `invalid`, `third_party`, `context_limited`, `partial`) con output JSON strutturato.
- **Worker creato**: `src/backend/lifelog2/services/pipeline/worker_profile_validator.py` — seleziona fatti `user_confirmed=false` con confidenza in gray-zone `[0.40, 0.75]` e `validated_at IS NULL`, li elabora in batch da 8 tramite `AriaLLMClient` (Qwen3-14B-q4km), applica le azioni di validazione (flagging, prefix `[TERZO]`, aggiornamento confidenza) e registra l'audit in `memory_consolidation_records`.
- **UI aggiornata**: `src/frontend/src/routes/profile/+page.svelte` — classe `.is-flagged` attivata se `sensitivity='flagged'` o `confidence ≤ 0.05`, con desaturazione elegante (opacity 0.55, bordo rosso-ruggine, hover restore) per differenziare visivamente i fatti invalidati.
- **Deploy RT**: commit `4104f1a` su `S3ph1r/Lifelog2:main`, pull e test E2E su CT203 con ARIA libera. Full-scan iniziale completato (3 fatti validati, tutti `valid`). Timeout corretto da 120s → 600s per compatibilità con pipeline occupata.
- **Bug fix**: casting JSONB nell'audit log cambiato da `:after::jsonb` a `CAST(:after AS JSONB)` (incompatibilità con asyncpg/SQLAlchemy parametrizzato).
- **Pagine toccate**: [[stack-lifelog2]], [[log.md]]

## [2026-05-22] dev | Lifelog2 Z4 Day Digest & Temporal Aggregation

- **Day Digest Worker Backend**: Creato e testato con successo il worker `worker_day_digest.py` per l'aggregazione temporale giornaliera. Estrae in modo ottimizzato episodi, ricordi (atomi sparsi), persone viste, luoghi e argomenti deduplicati per una determinata data (fuso orario Europe/Rome). Interroga il modello Qwen3 su ARIA per produrre un diario narrativo, eventi chiave, open loops e un arco emotivo/di focus giornaliero in italiano strutturato in JSON, che viene memorizzato in modo efficiente tramite PostgreSQL `ON CONFLICT` con casting `jsonb` sicuro.
- **FastAPI /day Routing**: Modificato e verificato l'endpoint `/day/{date}` nel backend FastAPI (`dashboard.py`) per integrare fluidamente il payload del digest sotto la chiave `"digest"`, servendo sia i dati della timeline che il riassunto narrativo strutturato.
- **Svelte 5 Premium UI Layout**: Aggiornata l'interfaccia utente in `src/frontend/src/routes/day/[date]/+page.svelte` per integrare una vista glassmorphic cinematica di altissimo pregio estetico (OkLCH palettes, micro-animazioni). Mostra la sintesi narrativa quotidiana, gli eventi chiave, gli open loops evidenziati in stile "warning" e metachip interattivi per persone, luoghi e tag del giorno. Risolti ed eliminati tutti gli errori di compilazione e tipizzazione TypeScript del frontend tramite `svelte-check`.
- **Systemd Pipeline & Deployment**: Sviluppati i file di servizio systemd e i timer (`lifelog2-day-digest.service` e `lifelog2-day-digest.timer`) pianificati per l'esecuzione automatica del worker ogni notte alle 01:00 AM Europe/Rome su CT203.
- **Personal vs. Ambient Segmentation**: Evoluzione del prompt di Day Digest (`stage_z4_day_digest_v2.txt`) e del worker `worker_day_digest.py` per segmentare ricordi ed episodi quotidiani in base alla proprietà `capture_class` (personal, mixed, unknown per vita attiva vs ambient per media passivi). Il worker produce ora due narrative e due liste di eventi distinte in JSON, memorizzate in modo retrocompatibile in Postgres. La dashboard FastAPI (`dashboard.py`) gestisce il parsing e il fallback per i dati legacy, e l'interfaccia Svelte 5 renderizza separatamente la sezione "Sottofondo Ambientale & Media" in una scheda glassmorphic desaturata e visivamente differenziata rispetto all'attività principale.
- **Wiki e Documentazione**: Aggiornato [[log.md]] e [[entities/systems/stack-lifelog2|stack-lifelog2.md]] per tracciare lo sviluppo e l'evoluzione della segmentazione.

## [2026-05-22] dev | Lifelog2 RAG Chat, HNSW Vector Index & validated_at migration

- **Search Engine Foundation**: Migrazione `0012_hnsw_and_validated_at` applicata a database (CT105) con successo sia in Dev che in Runtime. Creato l'indice HNSW su `memory_atoms.embedding` (distanza coseno, 1024d) e aggiunta la colonna `validated_at` su `user_profile_facts`.
- **Backend RAG FastAPI**: Implementato l'endpoint `/api/dashboard/rag` che esegue l'embedding semantico tramite Ollama (`mxbai-embed-large`), interroga il database tramite pgvector cosine distance, compila il contesto semantico e formula una risposta RAG strutturata in JSON chiamando Qwen3 su ARIA via `AriaLLMClient`.
- **Frontend RAG Chat UI**: Sviluppata una magnifica vista di ricerca semantica `/search` in Svelte 5 (sintassi runes `$state`, `$derived`, `$effect`) con interfaccia chat cinematica premium, skeleton loader per il retrieval, parser interattivo di citazioni (`[1]`, `[2]`), e un pannello laterale per ispezionare gli atomi di provenienza citati collegandoli direttamente al visualizzatore di trascrizioni.
- **Infrastruttura & Lifecycle**: Integrato e abilitato nativamente a runtime il timer di pulizia audio settimanale `lifelog2-cleanup-audio.timer` su CT203. Tutti i servizi principali (`lifelog2`, `lifelog2-orchestrator`, `lifelog2-voiceprint`, `lifelog2-ui`) sono stati riavviati con successo e risultano attivi e stabili.
- **Wiki e Documentazione**: Aggiornato [[log.md]] per tracciare lo sviluppo.

## [2026-05-22] dev | Lifelog2 status roadmap + audit completo codebase

- **Audit completo**: scansione di tutta la codebase Lifelog2 (src/, docs/, deploy/, scripts/, migrations, prompts, frontend routes/components) + confronto con master blueprint e addendum intelligence.
- **Documento creato**: `docs/lifelog2-status-roadmap.md` — stato feature-by-feature su 10 aree (pipeline A→H, workers, intelligence layer, identity, livelli Z0–Z7, search/RAG, frontend, infra, roadmap P1→P5).
- **Blueprint aggiornato**: `lifelog-2.0-master-blueprint-v1.md` — aggiunta sezione "Documenti di riferimento operativo" con puntatori a tasklist, addendum, identity design, dashboard spec.
- **Gap principali emersi**: HNSW index mancante (embedding ci sono, sequential scan), Day Digest worker (Z4) inesistente, Thread worker (Z6) inesistente, Search/RAG non iniziato, M4A cleanup e Profile Builder timer non ancora abilitati su CT203, Stage H (oblivion) non iniziato, Liquid Brain non iniziato.
- **Wiki aggiornato**: index.md + log.md.

## [2026-05-22] dev | Lifelog2 voiceprint re-enrollment massivo + geocoding Nominatim

- **Re-enrollment 1175 segmenti**: producer su LXC 203, M4A→WAV via ffmpeg, push queue `aria:q:voiceprint:local:whisperx-large-v3:lifelog`, BRPOP callback, aggiornamento `speaker_turns.voiceprint_embedding`. Completato 0 errori in ~2.8h.
- **Multi-segment centroid Roberto**: media di 17 centroidi L2-normalizzati → L2-normalize → norm=1.000, 256d. Soglia 0.72: 582 turns matched (max_sim=0.9371). Precedente enrollment singolo segmento (25 match) superato.
- **Campioni manuale**: 154 WAV clip estratti e copiati su `D:\download\voiceprintsamples\` su ARIA PC. Verificati a campione dall'utente — tutti corretti.
- **person_id + capture_class**: 582 turns `person_id` → Roberto UUID; 93 segmenti promossi (92 ambient→mixed, 1 ambient→personal).
- **Fix ARIA git**: `aria_node_controller/backends/lifelog_whisperx.py` aggiunto routing `voiceprint_only` (stash pop perso in rebase); `backends/lifelog_whisperx/server.py` endpoint `/voiceprint` restituisce `{"status": "done", "output": {...}}`. Commit `84f6d92`, SCPed su PC139.
- **Geocoding implementato** (`src/backend/lifelog2/core/geocoding.py`): `find_or_create_place()` con `PlaceRef` dataclass, Nominatim OSM, merge radius 200m, rate limit 1 req/s.
- **Stage F integrato**: geocodifica automatica dopo creazione episodio → `episodes.place_ids` + `memory_atoms.location_id`.
- **Backfill script** (`scripts/backfill_geocoding.py`): 3 episodi geocodificati → "Via Louis Armstrong, Montanara" (44.7725, 10.3142). Commit `927ec73`.
- **Pending**: parsing GPS da filename M4A (formato sconosciuto, utente deve fornire esempio); `episodes.end_time` bug (= processing time invece di recording end).

## [2026-05-23] dev | Lifelog2 Stage F Deterministic Boundary Detection & Z7 Profile Builder Fix

- **Alembic Migration**: Creata ed eseguita la migrazione `0013_memory_atom_mode_timeline.py` per aggiungere le colonne `media_fingerprint` (`TEXT`) e `mode_timeline` (`JSONB`) su `memory_atoms`.
- **Modelli SQLAlchemy**: Aggiornato `MemoryAtom` in `models/memory.py`.
- **Prompt Stage D (v11)**: Creato `prompts/stage_d_enrich_v11.txt` per estrarre `media_fingerprint` e `conversation_type`, e impostato come default in `prompts/config.json`.
- **Stage D Integration**: Aggiornato `stage_d_enrichment.py` per estrarre e persistere i nuovi campi in `entities_json` e `media_fingerprint`.
- **Stage E Timeline**: Implementato il calcolo deterministico `_build_mode_timeline(...)` in `stage_e_embedding.py` leggendo i turni vocali e identificando contatti noti dal voiceprint.
- **Stage F Grouping State Machine**: Riscritto completamente il boundary detection in `stage_f_grouping.py` tramite Pass 1b deterministico con merge di silenzi < 5min, significatività del personal >= 60s, breaks a mezzanotte, soft break LLM ultraleggero solo in assenza di fingerprint identici, e calcolo automatico degli indici di split intra-atomo tramite turn offset, riducendo le chiamate LLM di oltre l'80% (da ~56 a ~8 al giorno).
- **Z7 Profile Builder Bugfix**: Corretto il bug SQL di casting di SQLAlchemy (`:src::jsonb` -> `CAST(:src AS jsonb)`) in `worker_profile_builder.py`.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-24] bugfix | Lifelog2 Cockpit layout duplicate cards and Svelte hydration crash

- **TypeScript Type Safety**: Resolved a Svelte page rendering failure (which left only the headline visible) by correcting type definitions and verifying reactive properties on `status.orchestrator` at runtime.
- **HTML Grid Clean-up**: Fixed a duplicate card layout bug where the Stage F (Episode Grouping) and Stage G (Visual Covers) blocks were mistakenly rendered inside the horizontal `streams-row` under the Redis Streams section due to an automated multi-match regex replace, cleanly keeping them exclusively inside the correct `workers-grid` layout.
- **HMR Hot-reload**: Synchronized the Svelte fix back to `ct203-lifelog` (192.168.1.203) using nested secure copy, successfully triggering Hot Module Replacement (HMR) with zero compilation errors.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-24] dev | CT202 Gateway Telemetry & Lifelog2 Control Plane Integration

- **Resource Resize**: Aumentate in modo permanente le risorse di `[[ct202-gateway|CT202]]` da Proxmox via SSH (RAM: 512 MB, disco: 6 GB) per ospitare il monitoraggio autonomo 24/7.
- **Standalone Dashboard**: Creata una dashboard standalone statico-client-side (Vanilla JS) su `[[ct202-gateway|CT202]]` all'indirizzo `/gateway/` che interroga Nginx `stub_status` e l'API locale di Ngrok in sicurezza (limitati solo a LAN), consumando esattamente **0 MB** di RAM aggiuntiva sul container.
- **FastAPI Backend Integration**: Modificato `[[api/routers/orchestrator.py]]` nel backend FastAPI di Lifelog2 su `[[ct203-lifelog|LXC 203]]` per interrogare asincronamente in parallelo gli endpoint metriche di CT202 con un timeout resiliente di 1.5 secondi, restituendo i dati live nella risposta di `/status`. Riavviato solo il servizio API, lasciando la pipeline worker in esecuzione senza interruzioni.
- **Svelte 5 UI Control Plane**: Aggiunta una card premium "Internet Gateway · CT202" nella pagina `/pipeline` Svelte 5 che mostra badge online/offline, tunnel pubblico attivo Ngrok, percentili di latenza, connessioni attive ed HTTP request rates in tempo reale con HMR istantaneo.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-24] dev | Lifelog2 Live Voiceprint Enrollment & Svelte Dashboard Audio Player

- **Live Voiceprint Enrollment**: Eseguito con successo lo script `enroll_user_voiceprint.py` live. Caricati permanentemente i 3 campioni audio `.m4a` da `D:\LifeLogData\user_data\` su MinIO, estratti gli speaker turn embeddings da 256 dimensioni tramite ARIA, e memorizzato il centroid pesato a livello utente in Postgres.
- **Diarizzazione Biometrica & Reclassification**: Eseguita la classificazione retroattiva automatica su 1222 segmenti audio: marcati 149 turni vocali appartenenti a Roberto (soglia coseno >= 0.75), portando alla promozione automatica di 13 segmenti personali e 22 segmenti misti.
- **Dashboard Audio Stream**: Esteso l'endpoint `/api/dashboard/profile/voiceprint-audio` per accettare un query parameter `index`, permettendo di streammare individualmente ciascuno dei 3 campioni di enrollment.
- **Svelte 5 UI Player Widgets**: Aggiornato `+page.svelte` per visualizzare tre comandi di riproduzione distinti (**▶ 1, ▶ 2, ▶ 3**) posizionati elegantemente di fianco al badge del profilo utente Roberto.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-25] dev | Lifelog2 Stage L2 Identity Review UI & API E2E Success

- **Backend Mutation Endpoints**: Sviluppate le API di mutazione delle persone in `dashboard.py`: `/people/{person_id}/confirm` (promozione a livello 2, assegnazione relazioni/disambiguation e cancellazione candidati), `/people/{person_id}/reject` (rifiuto selettivo dei candidati) e `/people/{person_id}/update` (modifica anagrafiche e tag esistenti).
- **PGVector Biometric Back-Propagation**: Integrato il ricalcolo nativo e retroattivo all'interno di `/confirm` tramite query PostgreSQL pgvector (soglia di match coseno $\ge 0.72$, ovvero distanza $\le 0.28$) per riassociare automaticamente i turni di speaker orfani (`person_id IS NULL`) alla persona confermata.
- **Premium Glassmorphic Identity Panel**: Aggiornato `/people/+page.svelte` in Svelte 5 con tipizzazione TypeScript (`Candidate[]`) per sostituire il dump JSON raw con un'interfaccia interattiva premium. Gli utenti vedono le evidenze virgolettate, la logica del Detective ed il form inline Frosted-glass di conferma con gestione della collisione per l'omonimia, il tag di disambiguazione ed i dropdown di relazione.
- **E2E Validation Success**: Eseguito il test di conferma su `CT203` (RT). Il trigger ha promosso con successo l'identità del proprietario `"Roberto Guareschi"` marcando a `null` i candidati ed aggiornando anagrafica, livello ed allineando i dati reali del DB.
- **Pagine toccate**: [[log.md]], [[NH-Mini/index.md]], [[entities/containers/ct203-lifelog.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-25] bugfix | Lifelog2 Detective JSON Truncation, NULL-safe Dedup, max_tokens Fix

- **Detective loop infinito risolto**: root cause = batch 8 atomi → output JSON > max_tokens=1536 → troncamento → parse fail → cursore Redis bloccato → stesso batch ripetuto ogni 15min per 3+ ore. Fix: `BATCH_SIZE=4`, `max_tokens=2048` per il Detective.
- **NULL-safe dedup fix critico**: `NOT (identity_candidates @> ...)` restituiva NULL silenzioso su persone senza candidati — zero candidati scritti in DB nonostante LLM corretto. Fix: `(IS NULL OR NOT (...))` + rowcount check.
- **AriaLLMClient.generate_json() parametrizzato**: `max_tokens` ora parametro opzionale (default 1536, backward-compatible). Ogni worker può ora specificare il proprio budget di output.
- **DB cleanup**: test artifacts (TEST_CANDIDATE, TEST_SA, TRACE_TEST) rimossi da `persons.identity_candidates`.
- **Dev/RT allineati**: LXC 190 e LXC 203 ora a commit `b4daf35` su `origin/main`.
- **Commits**: `7d501fe`, `ccc4db6`, `b4daf35` su `github.com/S3ph1r/Lifelog2`.
- **Pagine toccate**: [[log.md]], [[entities/containers/ct203-lifelog.md]]

## [2026-05-25] dev | Lifelog2 Stage Z7 Tier B Voiceprint Clustering E2E Success

- **Voiceprint Clustering Algorithm E2E**: Implementata la pipeline matematica e SQL nativa per lo **Stage Z7 / Tier B (Cerchia Sociale - Voiceprint Clustering)** all'interno del worker `worker_profile_builder.py`.
- **Math/SQL Refinement**: Ottimizzata la procedura di greedy cosine clustering (soglia >= 0.65) e di estrazione centroidi normalizzati L2. Risolto il crash su `persons` per colonne inesistenti (`created_at`/`updated_at`) sostituendole con `first_seen_at`/`last_seen_at`.
- **SQLAlchemy Bind Parameter Fix**: Corretto l'errore di sintassi in `_write_audit` per la query di persistenza dei log di consolidamento, rimpiazzando il cast PostgreSQL `:after::jsonb` con la notazione standard compatibile con asyncpg `CAST(:after AS jsonb)`.
- **E2E Validation Success**: Eseguito il run di bootstrap completo (`--full-scan`) su `CT203` (RT). La diagnostica pulita conferma la stabilità della base dati reale: **206 interlocutori ricorrenti anonimi** creati e persistiti in `persons`, **6.116 speaker turns** diarizzati e collegati biometricamente ai rispettivi cluster, e **206 fatti relazionali** generati e corroborati con confidenza dinamica scalata da 0.60 a 0.80.
- **Pagine toccate**: [[log.md]], [[NH-Mini/index.md]], [[entities/containers/ct203-lifelog.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-25] dev | Lifelog2 Identity Detective Greedy Batch Processing Optimization

- **Greedy Loop Activation**: Modificato il worker Identity Detective (`worker_detective.py`) introducendo un ciclo sequenziale fino a 5 batch (8 atomi/chiamata LLM) per ogni attivazione periodica (15min) o manuale.
- **Type-safe Early-exit**: Aggiunta la clausola `if atoms_processed == 0: break` nel ciclo greedy per terminare immediatamente l'esecuzione se la coda si esaurisce prima dei 5 batch, azzerando le query e le chiamate API ridondanti.
- **E2E Validation Success**: Eseguito il test manuale via Redis (`run_detective`). I log del container `CT203` (letti tramite `pct exec` da Proxmox) confermano l'elaborazione sequenziale e ininterrotta di 5 batch da 8 atomi l'uno (totale 40 atomi) completata in **3 minuti e 14 secondi** con 0 errori.
- **Pagine toccate**: [[log.md]], [[entities/containers/ct203-lifelog.md]]

## [2026-05-25] bugfix | Lifelog2 Identity Detective E2E Success & Parser Fallback

- **Detective Datetime Binding Fix**: Risolto il crash sistematico di `asyncpg` nel worker `worker_detective.py` dovuto al type-binding asincrono per `ma.created_at` (TIMESTAMPTZ), parsando la stringa ISO da Redis in un oggetto `datetime` nativo.
- **AriaLLMClient Robust Parser Fallback**: Risolto il baco nel parser regex di fallback di `llm.py` che cercava solo parentesi graffe `{}` per singoli oggetti, estendendo la ricerca anche a parentesi quadre `[]` per supportare con successo gli array JSON (utilizzati dal Detective per restituire i candidati).
- **E2E Success**: Il Detective ha completato con successo il suo primo run end-to-end pulito in 50.9 secondi, popolando i log con timestamp validi pronti per lo streaming live sul Cockpit Terminal.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-25] dev | Lifelog2 Cockpit premium layout evolution & Background Workers integration

- **Live Log Ticker UI**: Moved the live terminal window to the very top of the cockpit (just below the KPI summary bar), transforming it into a high-visibility compact ticker limited to 10 lines (150px height) for instantaneous pipeline monitoring. Integrated the inclusion of `[DETECTIVE]` (`detective.log`) into the FastAPI log aggregator to stream identity candidate analysis live.
- **Stage F & G Backlog Displays**: Added dynamic backlog counters (`CODA`) inside the Svelte cockpit cards for Stage F (Episode Grouping) and Stage G (Visual Covers / FLUX) using the backend database keys `status.db.memory_atoms_ungrouped` and `status.db.episodes_without_cover` respectively.
- **Background Intelligence Tiles**: Integrated the independent asynchronous workers into the `workers-grid` layout by adding premium tiles for **Stage L2 (Identity Detective)** and **Strato V (Profile Validator)**, complete with active running status indicators, interval/trigger notes, last/next run times, and dynamic task backlogs (`CODA` calculated via SQL queries).
- **Orchestrator Uptime & DB Alignments**: Modified `[[orchestrator.py]]` to natively track loop state, last run and next run timers for the Detective worker, exposing them in `/status` Redis JSON. Corrected `[[api/routers/orchestrator.py]]` to calculate real-time pending task counts (atomi consolidati non analizzati per Detective, fatti grigi non validati per Validator) and fixed `episodes_without_cover` count to accurately sum both episodes and atoms lacking covers.
- **Full Deployment & HMR**: Deployed all modifications to `[[ct203-lifelog|LXC 203]]` via SCP and restarted both `lifelog2` and `lifelog2-orchestrator` systemd services, cleanly hot-reloading the interface.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]], [[entities/containers/ct203-lifelog.md]]

## [2026-05-26] dev | Lifelog2 Production Release & Git Synchronization

- **Audit & Allineamento Checksum MD5**: Effettuato un audit di sicurezza comparativo calcolando gli MD5 dei file di produzione su **LXC 203** e confermando l'assoluta equivalenza byte-per-byte con i commit di sviluppo su **LXC 190** (`+page.svelte`, `people/+page.svelte`, `worker_profile_builder.py`, `check_db.py`), garantendo l'assenza di divergenze live.
- **Consolidamento Script Operativi**: Eseguito il backup via SCP e tracciato sotto Git un set di 5 preziosi script untracked di produzione per il debug ed il test dei livelli biometrici e dell'anagrafica self (`find_self.py`, `fix_self.py`, `cleanup_test.py`, `test_upgrade.py`, `audit_db.py`).
- **Release su GitHub & Deploy Produzione**: Committati 19 file consolidati e pushati sulla repository remota (`main -> main`). Puliti i file duplicati su **LXC 203** ed eseguito un allineamento pulito tramite `git reset --hard` e `git pull`, portando la produzione in perfetto pareggio con la codebase di sviluppo.
- **Riavvio Servizi di Produzione**: Riavviati con successo `lifelog2-orchestrator.service`, `lifelog2.service` e `lifelog2-ui.service` su **LXC 203**, ripristinando la telemetria, l'orchestratore sequential greedy ed i worker ASR/Intelligence a pieno regime con la nuova codebase attiva in memoria.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-26] bugfix | Lifelog2 Sagas scroll layout double scrollbar fix

- **Sagas Scroll Layout Fix**: Risolto il bug di scrolling bloccante nella vista delle Saghe (`/sagas/+page.svelte`) rimuovendo la regola `overflow-y: auto` dalla classe `.sagas-body`. Questa impostazione creava un'area di scrolling annidata indipendente rispetto al pannello principale `.main-content-panel`, bloccando in alto la card delle statistiche `Z6 · Cinematic Personal Analytics` e comprimendo la griglia delle saghe sottostanti in pochissimi pixel visibili.
- **Natural Global Scrolling**: Ora, la griglia delle saghe si espande naturalmente e l'intera pagina scolla all'interno dell'unico contenitore globale, permettendo alla card delle statistiche di scorrere naturalmente verso l'alto scomparendo sotto l'header sticky ed offrendo una navigazione fluida ad altezza intera.
- **Deploy di Produzione**: File copiato su `CT203` via SCP ed il servizio `lifelog2-ui.service` riavviato con successo.
- **Pagine toccate**: [[log.md]], [[sviluppi/Lifelog2/src/frontend/src/routes/sagas/+page.svelte]]

## [2026-05-26] dev | Stage Z6 Thread Consolidation E2E Success — Hybrid Gemini Cloud & Qwen3 Local via ARIA

- **Stage Z6 Pipeline Implementation**: Implementato con successo lo Stage Z6 (Thread Consolidation Worker) per Lifelog2, che consolida gli episodi quotidiani (Z3) in saghe tematiche a lungo termine (Z6), calcolando i vettori embedding a 1024d su PostgreSQL.
- **Hybrid AI Architecture**: Progettata e validata un'architettura ibrida per l'elaborazione ad alto contesto: la mappatura in batch degli episodi sui thread (che richiede una context window ampia) è delegata a Google Gemini tramite il nuovo `AriaCloudLLMClient`, mentre la sintesi e la timeline narrativa per ciascun thread è affidata a Qwen3 locale tramite `AriaLLMClient`.
- **SQLAlchemy/Postgres Cast Compatibility**: Corretto un bug critico di sintassi PostgreSQL per il driver asyncpg rimpiazzando l'operatore di array cast `:ep_ids::uuid[]` con `CAST(:ep_ids AS uuid[])` per scongiurare collisioni con il parser dei bind parameter di SQLAlchemy.
- **Production Validation Success**: Eseguito con successo il dry-run di validazione reale su **CT203** (produzione) tramite gateway Proxmox (`pct exec 203` e `pct push`). Il worker ha analizzato i 5 episodi di test, delegando a Gemini cloud la mappatura via Redis (tempo di risposta: 14 secondi, 5328 token processati) ed a Qwen3 locale la sintesi in parallelo, completando l'intero processo in 108.5 secondi senza errori.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

## [2026-05-26] doc | /doc lifelog2 — Svelte 5 Runes compiler fix, Postgres Duplicates Protection & Environment Agnostic Worker

- **Svelte 5 Runes Compiler Fix**: Risolto l'errore fatale di compilazione introdotto con Svelte 5 su `/people/+page.svelte` (deprecati i modifier pipe inline come `onsubmit|preventDefault`), spostando l'inibizione del submit all'interno del gestore `submitForm(e)` richiamando `e.preventDefault()` a livello programmatico.
- **Postgres Duplicates Protection**: Implementata una query SQL robusta basata su `.scalars().all()` in `worker_profile_builder.py` (`_build_profile`) per isolare e selezionare l'identità attiva a livello più elevato in presenza di record duplicati `relationship_type = 'self'`, scongiurando eccezioni `MultipleResultsFound` di SQLAlchemy ed il conseguente crash del cockpit.
- **Environment Agnostic Worker**: Integrato il caricamento asincrono e dinamico del file `.env` tramite `dotenv` all'interno di `worker_profile_builder.py` per rendere l'esecuzione offline e manuale del Profile Builder ed il clustering biometrico resiliente all'ambiente fisico (Dev `CT190` o Prod `CT203`).
- **Wiki & Docs Sync**: Sincronizzati i file architetturali di NH-Mini e del progetto Lifelog2 (`development-log.md`, `architecture.md` e `memory-model.md`) per censire l'implementazione del clustering biometrico non supervisionato Tier B (voiceprint a 256d con matching $\ge 0.65$) e l'Identity Resolution Upgrade per la cerchia sociale (promozione a Tier A pgvector $\ge 0.72$).
- **Pagine toccate**: [[log.md]], [[NH-Mini/index.md]], [[sviluppi/Lifelog2/knowledge/development-log.md]], [[sviluppi/Lifelog2/knowledge/architecture.md]], [[sviluppi/Lifelog2/knowledge/memory-model.md]]

## [2026-05-27] dev | Lifelog2 Places Intelligence — implementazione Fase 0–4 completa

- **Migration 0014**: nuove colonne `places` (visit_count, total_minutes_spent, cover_image_key, confirmed_*), tabella `place_hypotheses`, vista materializzata `place_signals`. Applicata su LXC 203 e verificata.
- **Stage F aggiornato**: geocoding ora incrementa `visit_count + total_minutes_spent` e refresha `place_signals` dopo ogni geocoding.
- **Worker Place Detective** (`worker_place_detective.py`): aggregazione segnali (ora, DOW, capture_class, topics, voiceprint), scoring rule-based per home/work/social/transit, upsert `place_hypotheses` con confidence ≥ 0.50. Nessun LLM — puro segnale statistico.
- **Orchestrator aggiornato**: `_place_detective_loop` integrato — schedule domenica 03:30, on-demand via `run_place_detective` Redis cmd, stato visibile in status JSON.
- **Stage G esteso**: `_fetch_pending_places()` + prompt templates per tipo (home/work/social/transit/unknown) + `covers/places/{id}.jpeg` MinIO schema.
- **API endpoints**: `GET /dashboard/places`, `GET /dashboard/places/{id}`, `GET /dashboard/places/{id}/atoms`, `POST /{id}/confirm`, `POST /{id}/reject`, `GET /cover/place/{id}`. Tutti live e testati.
- **Frontend `/places`**: Leaflet cluster map (40% vh, circle markers con radius=log(atom_count), dashed per ipotesi / solid per confermati), tiles Netflix-scroll (240px, cover AI, badge tipo+conf, stats, topics, evidence), detail panel 360px (mini-map, stats bar, class-bar, evidence list, confirm/reject form). Sidebar aggiornata: `/map` → `/places`.
- **Status**: Fase 0–4 live. Fase 5 (Stage D context) e Fase 2b GPS data (Detective attivo da domenica) pendenti.
- **Pagine toccate**: [[concepts/lifelog2-places-intelligence]], [[sources/lifelog2-status-roadmap]]

## [2026-05-27] dev | Lifelog2 Places Intelligence — spec tecnica e roadmap

- **Analisi GPS esistente**: verificato che raw_captures.lat/lon già salvato, Stage F già geocoda via Nominatim, places table con 1 record (home Via Louis Armstrong, Parma). GPS inviato su ~13% segmenti prima del fix app Android (27/05).
- **Spec tecnica v1**: scritta `sviluppi/Lifelog2/docs/lifelog2-places-intelligence-spec-v1.md` — DB migration, worker Place Detective, estensione Stage G per cover places, API endpoints, frontend `/places` con mappa cluster + tiles Netflix-style + detail panel.
- **Roadmap**: 5 fasi (Foundation DB → Detective worker → Stage G covers → API → Frontend), stima 13-19gg. Prerequisito: 2 settimane dati GPS continui (fix app eseguito oggi).
- **Principi di design**: stesso pattern Detective (suggerimento+evidenza, conferma utente). Location change NON usata per break episodi. Stage D riceverà context "location: home/work" dopo conferma.
- **Status roadmap aggiornato**: `lifelog2-status-roadmap.md` aggiornato con sezione P2b + stato visivo rapido.
- **Pagine toccate**: [[concepts/lifelog2-places-intelligence]], [[log.md]], [[NH-Mini/index.md]]

## [2026-05-28] dev | Lifelog2: Orchestrator parallel B+E + AriaLLMClient infinite-wait + Stage G threshold + Profile Validator timer

- **Orchestratore redesign** (commit `6a2b77d`): `_stage_b_loop` e `_stage_e_loop` autonomi e indipendenti, `ARIA_PIPELINE=[C,D]` seriale. `_reconciliation_loop` per segmenti orfani. Stage B non dipende mai da ARIA.
- **AriaLLMClient infinite-wait** (commit `7e58e75`): BRPOP hard timeout rimosso. Polling ogni 30s con re-push automatico se job consumato senza risposta. Tutti i worker ARIA-dipendenti ereditano il comportamento.
- **Stage G threshold** (commit `7295bc9`): `COVERS_MIN_TOTAL=10` — attende 10 cover pending prima di swappare FLUX in VRAM.
- **Profile Validator timer**: `lifelog2-profile-validator.timer` abilitato su CT203, giornaliero 03:00. Prima run: 339 fatti gray-zone processati in 43 batch Qwen3, 0 errori.

## [2026-05-29] dev | Lifelog2 Stage C/D quality gate — extraction_level + audio signals + prompt v13

- **Voiceprint P0 risolto**: identificato acoustic mismatch (VOICE_RECOGNITION vs CAMCORDER). Archiviate le 6 enrollment esistenti + centroid 256d. Ricostruito embedding Roberto con 2 soli campioni CAMCORDER. Abbassata soglia `VOICEPRINT_MATCH_THRESHOLD` 0.72 → 0.60 dopo verifica manuale di 15+ clip audio. Backfill su 10,694 speaker turns: 877 ora correttamente attributi a Roberto (capture_class=personal/mixed).
- **Stage C — audio quality signals**: aggiunti 4 campi al transcript JSON e al messaggio Redis Stage D: `avg_turn_duration_ms`, `min_turn_duration_ms`, `n_short_turns`, `inter_speaker_similarity` (coseno massimo tra embedding dei speaker). Il campo `inter_speaker_similarity > 0.78` segnala diarizzazione confusa.
- **Stage D — extraction_level gate**: `_format_user_message` ora riceve i segnali audio dal payload e li inietta nell'header utente (linee quality + warning ⚠ se diarizzazione confusa). Dopo risposta LLM, se `extraction_level ≠ full`, Stage D azzera server-side persons/locations/orgs/projects/actions/decisions/speaker_turns_annotated/temporal_refs. `metadata_only` → path ephemeral (come tq < 0.20). `hallucination_flags` ed `extraction_level` persistiti in `entities_json`.
- **Prompt stage_d_enrich_v13**: aggiunto campo `extraction_level` (full/contextual/metadata_only), `transcript_quality.hallucination_flags` con 8 pattern nominati (loop_residuo, nome_inventato, densita_entita_anomala, lingua_fantasma, coerenza_locale_incoerenza_globale, dettaglio_non_ancorato, nome_storpiato, frammento_isolato). Regole LLM esplicite su soglie tq + inter_speaker_similarity. `config.json` aggiornato v12 → v13.
- **Test validato**: Test A tq=0.50 → `extraction_level=contextual`, persons=[], hallucin_flags=['nome_storpiato'] ✅. Test B tq=0.80 → `extraction_level=full`, persons=['Alia'] ✅.
- **Deploy**: stage_c + stage_d + config.json + v13.txt copiati su LXC 203. Orchestrator riavviato.
- **Commit**: `4944c6a` (feat(stage-cd): quality gate extraction_level + audio signals v13)
- **Pagine toccate**: [[stack-lifelog2]]

## [2026-05-29] dev | Lifelog2 Stage D prompt v14 — quality gate iterativo + test su 12 campioni

- **Test baseline v13 (8 campioni A–H)**: confronto sistematico DB-stored (v12) vs live v13 su 8 segment_id reali da MinIO. Pattern rilevati: tq upward bias (6/8, Δtq ≈ +0.075), failure catastrofica su transcript degradato Test C (tq 0.20→0.60, full extraction, nome inventato), persons instabile (FP "l'ama", miss Antonio).
- **Prompt v14 — 7 fix**: (1) Total words nell'header + soglie extraction_level (< 30 → metadata_only, 30–60 → contextual); (2) frammento_isolato soglia 15→35 parole; (3) tq ceiling: Total words < 60 → score max 0.50; (4) decisions mixed: escludere prima persona plurale; (5) conv_type tv/radio: descrizione espansa per caso capture_class=mixed+broadcast; (6) server-side floor word_count < 50 + full → contextual; (7) server-side filter persons: `any(c.isupper() for c in p)`.
- **Iterazione Fix 7**: prima implementazione `p[0].isupper()` troppo aggressiva — dropped "dottoressa Bruzzone", "avvocato Macri" (titoli professionali italiani iniziano minuscolo). Fix: `any(c.isupper() for c in p)`, che richiede almeno una maiuscola ovunque nel token. Regressione rilevata (Test G 5/5→2/5) e corretta (4/5).
- **Server-side tq floor aggiuntivo**: `tq_score < 0.60 + full → contextual` — cattura il caso LLM che assegna tq basso ma sceglie comunque full. Fix ortogonale al word_count floor.
- **Test v14 finale (12 campioni A–L)**: aggiunti 4 campioni casuali (I, J, K, L). K: loop+incoerenza → contextual ✅. L: "Intesa" (banca) in persons → nuovo backlog entity-type bleeding.
- **Documentazione**: `sviluppi/Lifelog2/docs/stage_d_quality_gate.md` — rationale fix, backlog 5 issue, metodologia test, guidance future sessioni.
- **Script archiviati**: `docs/stage_d_tests/test_v14_{all,10,12}.py`.
- **Commits**: `6b1bef4` (feat v14), `d486c2a` (fix persons filter).
- **Pagine toccate**: [[stack-lifelog2]]

## [2026-05-30] dev | Lifelog2 Orchestrator Tier1/Tier2 refactor — voiceprint ARIA fix + single point of control

- **Root cause diagnosi:** voiceprint worker competeva con Stage C/D per ARIA (entrambi whisperx-large-v3). `ARIA_TIMEOUT_S=300s` < tempo reale ARIA sotto carico (~9 min). Enrollment stuck in Redis PEL indefinitamente. Domain shift (enrollment casa → recording ufficio) spiegava score 0.583 < threshold 0.60.
- **Tier1 ARIA serial loop:** `ARIA_PIPELINE` esteso con `stage_vp` come primo stage. VP enrollment processato prima di Stage C — WhisperX già in VRAM, zero model swap. `voiceprint.service` e `.timer` disabilitati.
- **TIER2_REGISTRY:** 6 worker sequenziali post-drain (detective 15min, day_digest 24h, profile_builder 7gg, profile_validator 24h, thread_consolidation 7gg, place_detective domenica 03:30). Hard timeout per worker via `asyncio.wait_for`.
- **Systemd audit:** 5 timer + 1 duplicato disabilitati (day_digest, profile_validator, profile_builder, thread_consolidation, thread_consolidator). Solo `cleanup.timer` mantenuto.
- **Worker health Redis:** `lifelog:worker:health:{name}` (no TTL) con `consecutive_failures`. Dashboard warning se > 0.
- **Doc aggiornata:** `knowledge/architecture.md`, `knowledge/api-contracts.md`, `knowledge/development-log.md`, `history_manager.py`.

## [2026-05-30] dev | Lifelog2 Pipeline Dashboard refactor — timer workers + stream lag + layout

- **Nuovo endpoint `GET /orchestrator/timers`**: stato dei 5 systemd timer workers (day_digest, profile_validator, profile_builder, thread_consolidation, thread_consolidator) via `systemctl show`. Campi: status idle/running/failed, last_trigger, next_elapse, duration_s.
- **Stream lag corretto**: `_stream_info()` ora legge `lag` via `XINFO GROUPS` sul consumer group associato. Prima si mostrava `length` (total history) — fuorviante. Tutti i lag = 0 (pipeline sana). Deadletter = 1449 msg permanenti (rejected, non da riprocessare).
- **Dashboard layout 2 colonne**: sinistra = tutti i workers (streaming B→E, batch F/G/Detective/PlaceDetective, background workers systemd); destra = DB stats + gateway + telemetria. KPI bar full-width, log terminal collassabile.
- **4 fix dati frontend**: TypeScript `StreamInfo` type aggiornato (lag vs first_entry); `formatNextTimer()` per timestamp futuri; CSS `.col-span-2`; `{@const}` Svelte 5 placement fix (500 error).

## [2026-05-31] dev | Lifelog2 Orchestrator tuning — Batch Tier1 trigger + Tier2 schedule calibration + two-service discovery

- **Batch Tier1 trigger:** `BATCH_MIN_SIZE=6`, `BATCH_MAX_WAIT_S=1800`. GPU swap ridotti da 12/h a 2/h (83%). Warm cache chain: WhisperX→Qwen3→Tier2 workers.
- **TIER2_REGISTRY schedule:** `profile_builder` 7gg→6h, `place_detective` domenica→6h, `thread_consolidation` 7gg→2gg + `--limit 30` + timeout 2700s.
- **Two-service architecture:** `lifelog2.service` (API) vs `lifelog2-orchestrator.service` (pipeline) — due processi distinti su CT203.
- **Commit:** `5b30553` (thread_consolidation), `486f4f7` (profile_builder + place_detective), `d236992` (batch trigger). Deploy CT203 ore 20:23 CEST.
- **Doc:** `knowledge/architecture.md`, `knowledge/development-log.md`.

## [2026-06-01] dev | Lifelog2 — conversation_type refactor deploy + Stage G placement + backfill 2025

- **Conversation type taxonomy live:** migration 0015, Stage C classifica real_dialogue/personal_mono/hybrid/media_passive/ambient_voices. Tier gate Stage D (analysis_tier≤1.0 → skip LLM). Z7/Detective filtrano su conversation_type. Verificato: 44 atoms tipizzati correttamente, persons=1.
- **Backfill 2025:** `backfill_asr_from_archive.py` — 1025 discarded (audio_deleted), 85 re-queued su stream:asr. DB pulito.
- **Stage G covers refactor:** commit `b509e4c`. Stage G FLUX2 ora triggerato dopo Tier2 (non da Stage F). Ordine D→Tier2→G = 2 swap GPU (era 3). Git pull su CT203, restart pendente.
- **Aggiornato:** `knowledge/architecture.md`, `knowledge/memory-model.md`, `knowledge/development-log.md`.

## [2026-06-01] dev | Lifelog2 — analisi empirica pipeline, fix voiceprint/detective, design blueprint classificazione

- **Fix sessione:** Stage Z7 capture_class filter (personal/mixed), detective loop while True, DETECTIVE_TIMEOUT_S 10min→24h, detective return 0 fix, VOICEPRINT_MATCH_THRESHOLD 0.60→0.50.
- **Analisi empirica:** segmento 799997ce identificato come caso canonico del problema — Roberto guarda TV, conduttore classificato come "giornalista/analista politico" (false identity). 25 su 33 detective candidates potenzialmente contaminati da media content.
- **Problema fondamentale scoperto:** `mixed` conflates real dialogue, media passive, ambient voices. `conversation_type` mancante è la radice di tutto.
- **Design document:** `sviluppi/Lifelog2/docs/lifelog2-classification-evolution-blueprint-v1.md` — conversation_type taxonomy, 8 scenari di vita reale, retroazione architettura, data model extensions, roadmap P0→P5.
- **Dati DB:** rematch 2309 turns Roberto, 5 Person provvisori eliminati, profile_builder --full-scan (33 nuovi persons, 1315 turns linkati).

## [2026-06-01] dev | Lifelog2 — implementazione conversation_type classification (refactor completo)

### Modifiche applicate (commit d351760)

**Migration 0015** — nuove colonne:
- `segments`: conversation_type, conversation_type_confidence, turn_taking_score, roberto_word_ratio, avg_nonroberto_turn_s, dominant_speaker_ratio, known_persons_present (UUID[]), capture_class_version, capture_class_updated_at, analysis_tier
- `speaker_turns`: person_confidence, turn_type
- `memory_atoms`: conversation_type, analysis_tier, invalidated_at, invalidated_reason, extracted_with_context
- `persons`: is_media_persona, media_source_hint, segment_count
- Nuova tabella: `reclassification_queue`

**Stage C** — calcolo in-memory conversation_type da speaker_turns (no LLM):
- `_compute_conversation_metrics()`, `_classify_conversation_type()`, `_assign_analysis_tier()`
- `_classify_and_resolve()` esteso: ora restituisce anche `speaker_to_score` e `user_labels`
- `person_confidence` salvato su speaker_turns
- conv_type, metrics, analysis_tier salvati su segments
- conv_type emesso in stream:enrich payload

**Stage D** — tier gate + conversation_type-aware:
- `analysis_tier <= 1.0` → skip LLM, salva atom stats-only (media_passive/ambient_voices)
- `_format_user_message()` aggiunto `conversation_type` nell'header prompt
- `_retention_from_importance()` aggiornato: media/ambient → "counted"
- importance cap per media_passive, ambient_voices
- MemoryAtom: conversation_type, analysis_tier, extracted_with_context salvati

**Z7 (profile_builder)**:
- Strato 1: filtro `conversation_type NOT IN (media_passive, ambient_voices)` + `invalidated_at IS NULL`
- Tier B clustering: filtro `conversation_type IN (real_dialogue, hybrid, unknown)` su speaker_turns
- Post-filter cross-day: cluster deve coprire ≥ 2 date distinte

**Detective** — doppio filtro:
- atoms query: `conversation_type NOT IN (media_passive, ambient_voices)`
- turns query: `turn_type != 'media'`

**Scripts**:
- `scripts/backfill_conversation_type.py` — calcola retroattivamente metrics+conv_type su tutti i segmenti
- `scripts/cleanup_contaminated_data.py` — elimina memory_atoms, episodes, profile_facts, persons non-Roberto, resetta segmenti a 'enriching'
- `scripts/requeue_for_enrichment.py` — re-emette segmenti 'enriching' su stream:enrich ricostruendo transcript_key

**Test**: 13 unit test in `tests/test_stage_c_conversation_type.py` (23/23 pass)

### Prossimi step (CT203 offline al momento del commit)

1. Attendere CT203 online
2. `git pull` su CT203
3. `alembic upgrade head` (migration 0015)
4. Fermare lifelog2-orchestrator.service
5. `python scripts/backfill_conversation_type.py --dry-run` → verifica distribuzione
6. `python scripts/cleanup_contaminated_data.py` (conferma interattiva)
7. Riavviare lifelog2-orchestrator.service
8. `python scripts/requeue_for_enrichment.py` → re-processa tutti i segmenti
9. Monitorare Stage D, Z7, Detective

## [2026-06-02] dev | Lifelog2 — People view identity context panel + per-turn diarized audio

- **Detective identity_level fix:** `GREATEST(identity_level, 1)` nella UPDATE candidati — persone con candidati LLM ora correttamente al level 1. Commit `6dd8506`.
- **3 nuovi endpoint:** `/people/{id}/context` (12 turni+has_audio), `/people/{id}/turn-audio/{turn_id}` (ffmpeg slice AAC), `/people/{id}/voice-sample`.
- **Frontend People view:** panel espanso con trascrizioni + ▶/■ per-turn audio. Bug fix: stale `audioUrl` reference in `fetchContext` (ReferenceError silenzioso bloccava contextLoading). Commit `b739425`.
- **Aggiornato:** `knowledge/architecture.md`, `knowledge/api-contracts.md`, `knowledge/development-log.md`.

## [2026-06-03] dev | Lifelog2 — Detective prompt v2 + fix confirm_person + fix episodes.person_ids

- **Detective prompt v2:** regola disambiguazione esplicita (direct_address / self_identification / confirmed_reference). Nessuna 3a persona come evidenza identity. `name_evidence_type` nel JSON output. Config aggiornato a v2, commit `bb1f3c4`.
- **fix(stage_f): episodes.person_ids** mai popolato — aggiunto query `speaker_turns` prima di INSERT Episode. Backfill SQL: 132/314 episodi aggiornati. Commit `d806176`.
- **fix(confirm_person): numpy bugs** — `ValueError: truth value of array` (cambiato `if not arr` → `if arr is None`) + `TypeError: float32 not JSON serializable` (cambiato `list()` → `.tolist()`). Commits `8b6ed35`, `15effb8`.
- **persons.confidence backfill:** 3 L1 persons con conf=0.000 nonostante candidates → backfill SQL da `max(candidate.confidence)`.
- **Oleksandra Filonenko confermata L2:** 67 turn backpropagati via confirm_person con voiceprint centroid.
- **L1 candidates cleanup + backfill:** 4 L1 persons azzerati (identity_candidates=NULL, confidence=0). Checkpoint Redis → 1970. Detective backfill avviato direttamente (no orchestratore). Risultati iniziali corretti: "collega IT - nome sconosciuto" vs il precedente "Marco/Antonio" per 3a persona.
- **Pendente:** `name_evidence_type` prodotto da v2 ma non salvato in DB dal worker — da fixare prossima sessione.

## [2026-06-03] dev | Lifelog2 — Stage C idempotency + dedup migration 0017 + People M3 + pipeline audit

- **Stage C crash recovery fix:** DELETE speaker_turns WHERE segment_id prima di ogni INSERT batch. Crash+XACK lag → nessun duplicato. Deployato su CT203.
- **Migration 0017:** rimossi 8,856 duplicati (42%) da crash recovery pre-fix. 11,988 righe pulite, 0 duplicati residui.
- **People View M3:** `GET /dashboard/people` arricchito con `n_turns`, `n_days`, `best_candidate`, `is_ready`, `is_ambiguous`. Frontend: badge "Pronto"/"Ambiguo", pill stat, filtro `ready`.
- **Detective checkpoint reset** a 1970 per forzare aggiornamento `persons.confidence` (era 0.00 dopo checkpoint avanzato senza candidates).
- **Pipeline audit:** script `/tmp/pipeline_audit.py` — 0 anomalie critiche Tier1. Gap identificato: 314 episodi con `person_ids=[]`. Z4 `key_events` sempre vuoti.
- **Aggiornato:** `knowledge/architecture.md` (Stage C idempotency, People M3), `knowledge/memory-model.md` (SpeakerTurn idempotency), `knowledge/api-contracts.md` (sezione 5d GET /dashboard/people), `knowledge/development-log.md`.

## [2026-06-04] dev | WhisperX — Allineamento contrattuale e documentazione metriche di qualità

- **WhisperX Quality Contract:** Il backend WhisperX (`sviluppi/ARIA/backends/lifelog_whisperx/server.py`) è stato aggiornato per includere metriche di qualità a livello di turno (`avg_logprob`, `no_speech_prob`) e a livello globale di trascrizione radice (`transcription_quality` con `avg_logprob_mean`, `no_speech_prob_mean`, `no_speech_prob_max`, `n_segments`).
- **Sincronizzazione Documentazione:** Eseguito il protocollo esteso `/doc lifelog2` e `/doc backend whisperx` per allineare le specifiche contrattuali ed architetturali.
- **Aggiornato:** `sviluppi/ARIA/docs/backends/lifelog-whisperx.md`, `sviluppi/ARIA/docs/ARIA-blueprint.md`, `sviluppi/Lifelog2/knowledge/api-contracts.md`, `sviluppi/Lifelog2/knowledge/architecture.md`, `NH-Mini/log.md` e `NH-Mini/index.md`.
- **Storico architetturale:** Committato con history_manager la feature `whisperx-quality-metrics` con impatto medium.

## [2026-06-07] dev | Wiki refresh: Stage C1, Quality Tiers, Z6 Thread Consolidation, Place Semantics, Telemetry

- **Quality Gate C1 & Quality Tiers**: Creazione di [[concepts/lifelog2-quality-gate|concepts/lifelog2-quality-gate.md]] per mappare la logica meccanica dello Stage C1 (`stage_c1_classifier.py` e `stage_c1c2_gate.py`). Definiti i Transcript Quality Tiers (Tier A >-0.25, Tier B -0.25/-0.40, Tier C -0.40/-0.55), il meccanismo del server-side floor (override a `contextual` e cap importanza a 0.40 su audio degradato) e l'asimmetria biometrica del voiceprint.
- **Thread Consolidation Z6**: Creazione di [[concepts/lifelog2-thread-consolidation|concepts/lifelog2-thread-consolidation.md]] per mappare il worker di consolidamento `worker_thread_consolidation.py`. Spiegato l'approccio ibrido (Gemini Cloud per il batch mapping e Qwen3 locale per la sintesi testuale), gli embedding 1024d in Postgres (`threads`) e la rolling window di 30 giorni.
- **Place Semantics & Detective**: Aggiornato [[entities/systems/stack-lifelog2|stack-lifelog2.md]] per includere le logiche del Place Detective (`worker_place_detective.py` con scoring euristico e revisione su `/places` UI) e il geocoding automatico in Stage F.
- **Identity Resolution**: Mappato l'utilizzo di `is_media_persona` e `speaker_turns.turn_type` per escludere i turni di conduttori TV/radio e podcast dall'inferenza d'identità del Detective.
- **Telemetry**: Creazione di [[concepts/lifelog2-telemetry|concepts/lifelog2-telemetry.md]] per descrivere l'architettura SQLite fire-and-forget locale (`telemetry.db`), lo schema delle 6 tabelle ed i relativi 6 endpoint API REST `/telemetry/*`.
- **Aggiornato Index**: Aggiornato [[index.md]] con i link ai nuovi concept e l'incremento delle statistiche del secondo cervello (pagine totali: 64, concepts: 19).

## [2026-06-07] dev | Lifelog2 — Orchestrator B→G gate, Stage B batch limit, V1 import tooling

- **Orchestrator _stage_b_gate**: introdotto gate ciclo completo B→G. Stage B aspetta `asyncio.Event` impostato da Stage G prima di ogni batch. Rimossi i wait parziali errati su stream:asr/enrich. Ciclo garantito: B(25) → C → D → E → F → Tier2 → G → gate → B.
- **MAX_MESSAGES_PER_RUN=25** in `stage_b_preprocess.py`: limita Stage B a 25 file per run per evitare saturazione MinIO su backlog.
- **V1 import tooling**: `import_v1_from_pc.py` (SCP da PC139, cifra, staged), `inject_queued_batch.py` (ri-accoda queued persi da Redis), `restore_encryption_key.py` (recovery AES-256 dopo reset registry).
- **Fix dati registry_devices**: creata entry LEGACY_DEVICE_ID per associare backlog V1 all'utente roberto. Script `emit_staged_segments.py` ha emesso 1469 staged su stream:ingest.
- **Allineamento dev/rt/GitHub**: tutti su commit `537fce1`, working tree clean su LXC 203.
- **Aggiornati**: `knowledge/architecture.md` (gate B→G, MAX_MESSAGES_PER_RUN, nuovi script), `knowledge/development-log.md` (entry 2026-06-07). History entry ARCHITECTURE/Lifelog2/Orchestrator.

## [2026-06-08] dev | Lifelog2 backlog V1 completato + fix ghost episodes + race condition Stage D

- **Backlog V1 smaltito**: 28 cicli B→G completati (07/06 07:18 → 08/06 23:16). 1242 segmenti consolidati, 830 episodi finali. Chiave cifratura roberto aggiornata (new salt + PBKDF2/AES-GCM).
- **Ghost episodes fix** (`c218817`): 171 episodi duplicati (Aug–Dec 2025) eliminati con `DELETE FROM episodes`. Root cause: Stage F rieseguito su stessi atom da reconciliation re-queue → creava secondo episodio per stessa finestra. Dashboard `/sagas` ora filtra ghost via subquery FK-atom.
- **Race condition Stage D fix** (`c218817`): `_reconciliation_loop` estesa con Sezione 2 per recovery segmenti stuck in `enriched` con `memory_atom_id IS NOT NULL`. 26 segmenti re-pushati a `stream:embed`, tutti processati da Stage E (vector=True).
- **Aggiornato**: `knowledge/architecture.md` (reconciliation sezione 2, dashboard ghost filter), `knowledge/development-log.md` (entry 2026-06-08/09). History entries: BUGFIX/Lifelog2/Orchestrator/ReconciliationLoop (high), BUGFIX/Lifelog2/Dashboard/SagasEndpoint (medium).
- **/lint Lifelog2**: 59 passed, 0 warnings, 0 errors ✅

## [2026-06-09] dev | Lifelog2 pipeline hardening — audit/spot_check scripts, Stage D idempotency fix, orchestrator drain e trim

- **scripts/pipeline_audit.py**: audit strutturale per stadi B→G su N segmenti; check post-refactor (colonne, nomi hardcoded)
- **scripts/pipeline_spot_check.py**: report qualitativo (trascrizione, score D, episode, cover) per campionamento umano
- **fix Stage D idempotency**: guard esteso a `{"enriched","consolidated","done","embedding"}` — preveniva doppio enrichment su restart (76 atom orfani eliminati)
- **feat orchestrator _drain_aria_queues**: SIGTERM → drain `aria:q:*:lifelog` prima di kill worker, elimina job ARIA orfani
- **feat orchestrator stream:enrich trim**: reconciliation ogni 10min → XTRIM maxlen=200 quando lag=0 e pending=0; 2500 entry → 204 (trim manuale validato)
- **Commits**: `dc028b1`, `9ad5646`, `419d36d`, `0c4db36`, `9b8e8e7`

## [2026-06-09] dev | Lifelog2 user-agnostic refactor — bonifica C2, identity_detective, prompt bias, DB columns, enrollment legacy

- **Stage C2 rimosso**: `stage_c1c2_gate.py` → `stage_c1_gate.py`; 10 prompt v1–v10 cancellati; consumer group `c1c2gate` → `c1gate`
- **identity_detective**: `worker_detective.py` → `worker_identity_detective.py`; prompt `stage_d_detective` → `identity_detective` v3 (user-agnostic)
- **Prompt debiasing**: `stage_d_enrich v16`, `stage_z4_day_digest v3`, `stage_z7_profile_validator v2`, `stage_z6_consolidator/synthesis v2` — zero "Roberto" nei prompt attivi
- **Worker claims dinamici**: `worker_profile_builder`, `worker_day_digest`, `worker_profile_validator` leggono nome utente da registry DB via `_get_active_user_display_name()`
- **DB migration 0019**: `roberto_word_ratio → owner_word_ratio`, `avg_nonroberto_turn_s → avg_other_turn_s` — applicata su LXC 203
- **Dashboard**: `_get_active_user_info()` → nome da registry DB; rimosso `{"name": "Roberto"}` hardcoded
- **stage_f_ambient_break_v1.txt**: prompt inline estratto da `stage_f_grouping.py`
- **Legacy enrollment rimosso**: `POST /api/v1/devices/register` + `enrollment_secret_roberto/paola` — superseded da `/auth/register`+`/login`
- **Pagine wiki aggiornate**: `knowledge/architecture.md`, `knowledge/development-log.md`, `stack-lifelog2.md`

## [2026-06-10] dev | SHIFTER — Weekend cohesion and strict weekend/holiday staffing

- **Vincoli Weekend**: Aggiunta penalizzazione (`diff_we * 120`) nell'obiettivo del solutore per minimizzare i weekend spezzati, privilegiando weekend interi lavorati o interi liberi.
- **Staffing Festivo/Weekend Rigido**: Modificato il vincolo di copertura sui fine settimana e sulle festività per limitare il personale assegnato esattamente al minimo previsto (`== reqs[s]`), garantendo il massimo riposo possibile a chi non lavora. Nei giorni feriali ordinari rimane la regola per assorbire il surplus (`>= reqs[s]`).
- **Solver Time Limit**: Ridotto il tempo massimo di calcolo del solutore da 45 a 15 secondi per garantire feedback veloci all'utente.

## [2026-06-10] dev | SHIFTER — Layout restyling and static preference alignment

- **Layout a Piena Larghezza**: Spostata la matrice del calendario mensile a piena larghezza per migliorare la visibilità orizzontale e spostati i pannelli delle preferenze e delle ferie al di sotto di esso.
- **Preferenze Gerarchiche**: Allineato il form di inserimento nel frontend per gestire la preferenza gerarchica statica (fascia e scelta 1-2-3) rimuovendo i campi obsoleti data e peso, e aggiornato il relativo rendering nella sidebar (ordinato per operatore e scelta).
- **Historian Seeder Bilanciato**: Riscritto l'allocatore storico in `seed.py` per distribuire equamente turni, notti e weekend lavorati YTD prima della data Pivot, eliminando sproporzioni ed assicurando la convergenza e fattibilità automatica del solutore pre-run all'avvio.
- **Solver Bugfix**: Risolto bug di persistenza dei recuperi storici fittizi (`dummy_candidates`) estendendo il ciclo di salvataggio a tutti i giorni feriali futuri.

## [2026-06-10] dev | SHIFTER — ControlRoom 24/7 Shift Manager scaffolding and logic validation

- **Sviluppo Core**: Inizializzato sotto-progetto in `sviluppi/SHIFTER/` con .project-context e requirements.
- **Database SQLite**: Modelli SQLAlchemy e script di seed con storico turni/ferie/recuperi per i 12 operatori di control room.
- **Motore di Ottimizzazione**: Sviluppato solutore CP-SAT (Google OR-Tools) con vincoli rigidi (copertura, presenza, unicità, ferie, riposo N->M) e soft (equità annuale, recuperi weekend, recuperi consecutivi, preferenze).
- **REST API & Frontend**: Endpoint FastAPI e dashboard SPA interattiva (Tailwind CSS, griglia calendario e KPI di validazione turni in tempo reale).
- **Test logic**: Scritto ed eseguito con successo il test di integrazione per il solutore CP-SAT.
- **Wiki**: Creata pagina `entities/systems/stack-shifter.md` ed aggiornato `index.md`.

## [2026-06-11] dev | NH-Mini Dashboard — Topology tab con grafo interattivo vis-network

- **Nuovo tab "Topology"** nella sidebar: icona rete SVG, voce `data-page="topology"`.
- **Backend**: endpoint `GET /api/topology` in `web/app.py` — restituisce 13 nodi e 12 archi statici derivati da `infrastructure-map.mdc`. Nodi con type, ip, ports, purpose. Archi con conn_type.
- **Frontend**: pagina `#page-topology` con:
  - Canvas `#topology-network` (vis-network force-directed, full-height)
  - Pannello dettaglio `#topology-detail` (compare al click su un nodo, mostra IP/ports/type/purpose)
  - Legenda in basso: chip colorati per tipo nodo (Control/Hypervisor/App/Gateway/Infra/GPU/External) e tipo connessione (SSH/HTTP/Redis/Postgres/S3/Monitoring)
- **vis-network**: caricata via CDN `unpkg.com` senza dipendenze npm. Singleton `_topoNetwork` — si inizializza solo al primo accesso alla tab, poi riutilizza l'istanza.
- **Dark theme**: nodi con bg scuro `#0f3460…#4c0519` e bordi colorati con glow (`box-shadow`). Archi colorati per protocollo (Redis=amber, HTTP=sky, Postgres=green, S3=teal, SSH=slate dashed, Monitoring=violet).
- **Physics**: `barnesHut` force-directed, si stabilizza automaticamente e congela per non sprecare CPU. Reset view con pulsante ⊙.
- **CSS**: `.nh-topology-page`, `.nh-topo-canvas`, `.nh-topo-detail`, `.nh-topo-legend`, `.nh-topo-chip`, `.nh-topo-edge-chip` aggiunti a `dashboard.css`.
- **Lint**: 62 check passati, 0 errori.
- **File modificati**: `web/app.py`, `web/static/index.html`, `web/static/js/dashboard.js`, `web/static/css/dashboard.css`.

## [2026-06-11] dev | NH-Mini Dashboard — Sidebar layout & fixed background refactor

- **Layout Riorganizzato**: Rimossa la topbar `<header class="nhi-topbar">` e introdotto un layout a sidebar fissa completa (260px, `position: fixed`, `height: 100vh`) con tre sezioni: brand/logo in cima, menu di navigazione al centro, indicatori di stato e pulsante refresh in fondo.
- **Fix Sfondo Bianco in Scroll**: Cambiato `.nhi-scene-bg` da `position: absolute` a `position: fixed !important` con dimensioni `100vw / 100vh` per mantenere il gradiente nordico fisso durante lo scroll. Aggiunto `background-color: #0b0f19` su `body` come fallback solido.
- **Premium Nav Items**: Aggiunto `.nhi-nav-item` con hover subtle (`rgba(255,255,255,0.06)`) e stato attivo accentuato (`rgba(38bdf8,0.1)` + `color: #38bdf8`), transizioni fluide `0.2s ease`.
- **Responsività Mobile**: Aggiunto `@media (max-width: 768px)` che converte la sidebar in un topbar compatto con navigazione orizzontale wrap, nascondendo gli indicatori di stato.
- **Glass Enhancement**: Potenziato backdrop-filter su `.nhi-glass` e `.nhi-glass-dark` a `blur(20px) saturate(190%)`.
- **Scrollbar Sidebar**: Aggiunto stile custom thin (4px) per la scrollbar verticale della sidebar in caso di overflow.
- **Binding JS Preservato**: Tutti gli ID DOM originali (`status-dot`, `status-text`, `btn-refresh`, `alerts-badge`, `last-discovery`, `nav-alerts-count`) mantenuti nella nuova struttura sidebar; nessuna modifica al controller JS `dashboard.js`.
- **Lint**: `nh-lint.py` eseguito con 0 errori, 62 check passati.
- **File modificati**: `web/static/css/dashboard.css`, `web/static/index.html`.

## [2026-06-11] dev | Lifelog2 — Pipeline Validation Roadmap (M0→M5)

- **Documento creato**: `sviluppi/Lifelog2/docs/lifelog2-pipeline-validation-roadmap.md`
- Piano operativo con 6 milestone (M0→M5) per validare pipeline Ingest→Tier 2 prima di Tier 3
- Baseline snapshot 2026-06-11 incluso (1281 consolidated, 1497 staged, quality tier A/B/C)
- M0: audit pre-batch (P0.5, days=0, segment_count, Z7/Detective filter) — stato: in corso
- M1: batch test 50 segmenti con test SQL per Stage C/D/F/Tier2
- M2: full batch 1497 con metriche di corpus
- M3: Tier 2 deep evaluation su tutti i worker
- M4: fix gap identificati da M3
- M5: Tier 3 design basato su evidenza empirica

## [2026-06-11] dev | Lifelog2 — Sezione 15 Blueprint: Tier 3 Synthetic Intelligence Layer

- **Documento aggiornato**: `sviluppi/Lifelog2/docs/lifelog2-classification-evolution-blueprint-v1.md`
- **Sezione 15 aggiunta**: Tier 3 — Synthetic Intelligence Layer
  - §15.1: memory atom come evidenza variabile (importance stimata al tempo t con contesto parziale)
  - §15.2: differenza fondamentale Tier 2 vs Tier 3 (cursor+importance vs RAG+frequenza/magnitudo)
  - §15.3: 6 principi di design Tier 3 (RAG primario, output derivati, autonomia dinamica, non riscrivere passato, periodi di vita, knowledge docs in RAG)
  - §15.4: tassonomia worker T3-A→F (Relationship Arc, Project Chronicle, Decision Archaeology, Behavioral Pattern, Life Period Detector, Entity Network Mapper)
  - §15.5: modello dati `knowledge_documents` con schema SQL e indici
  - §15.6: staleness e batch-triggered refresh (aggiornamento periodico, non real-time)
  - §15.7: autonomia dinamica — soglie calibrate sulla baseline storica individuale, non parametri hardcoded
  - §15.8: interazione tra layer (Tier 0→1→2→3→query)
  - §15.9: roadmap Tier 3 (P6)
- **Sezione 12 aggiornata**: aggiunto P6 con roadmap Tier 3 sintetica
- **Sezione 13 aggiornata**: aggiunti invarianti #9 (knowledge documents vs atom) e #10 (profilo utente come sequenza di periodi)
- **Ragionamento alla base**: il sistema non può sapere il giorno 1 quale importanza avrà nel tempo una relazione, un progetto, o una decisione. Tier 3 costruisce comprensione evolutiva via RAG senza filtri importance, producendo documenti sintetici persistenti che evolvono con la vita dell'utente.

## [2026-06-11] dev | NH-Mini — Dynamic Infrastructure Mapping & Heartbeat Monitoring Automation

- **Dynamic VMID Parsing**: Replaced hardcoded `REAL_VMIDS` with a dynamic extraction helper (`get_real_vmids()`) parsing from `knowledge/containers/infrastructure-map.mdc` as SOT inside the dashboard (`app.py`), the heartbeat daemon (`heartbeat.py`), the linter (`nh-lint.py`), and the system context generator (`nh-discovery.sh`).
- **Service Catalog Hot-Reload**: Integrated automatic reload of `core.service_catalog` in dashboard endpoints to prevent Uvicorn caching of service definitions.
- **Heartbeat & Linter Integration**: Updated `heartbeat.py` and `nh-lint.py` to use dynamic VMIDs, preventing false positives and automatically monitoring newly promoted LXCs.
- **Wiki Documentation**: Created container entity page `ct204-shifter-rt.md`, updated `stack-shifter.md`, and indexed it in `index.md`.
- **Governance & Configuration Sync**: Upgraded `.cursorrules` to version `v7` by removing hardcoded VMID strings from its reference list. Aligned header comments in `nh-discovery.sh` to reflect the actual 15-minute timer execution.

## [2026-06-11] dev | SHIFTER — Shift pill color adjustments

- **Vibrant Shift Pills**: Adjusted background opacity and gradients for shift badge pills (M=yellow, P=green, N=sky blue/azzurro, REC=orange) to ensure high visibility and contrast on the light frosted-glass background.
- **Label Color Contrast**: Enhanced contrast for shift text labels (`shift-label-M`, `shift-label-P`, etc.) and modal/equity badge definitions, making them elegant and highly legible.

## [2026-06-11] dev | SHIFTER — Dynamic Operators and Contract Requirements

- **Dynamic Operator Management**: Added endpoints and UI controls to view, add, update (inline name and group), and delete operators with cascading database integrity.
- **Dynamic Shift Requirements**: Modeled weekday coverage parameters in the DB (`requisiti_turno`), allowing administrators to adjust daily targets directly from the UI.
- **Feasibility Pre-run Validation**: Integrated checks inside the solver engine to abort execution and report meaningful errors if the operator pool is insufficient (less than 8 total or less than 3 presence operators).
- **Bugfix on Frontend Requirements Validation**: Refactored the JS calendar validation code to query the dynamic DB requirements rather than hardcoded logic.
- **Dashboard Initialization Fix**: Removed an obsolete window binding for `deletePreference` in `app.js`, resolving a ReferenceError that crashed JavaScript initialization on dashboard load.

## [2026-06-11] dev | SHIFTER — UI customizations, sorting, and weekend/holiday highlights

- **Differentiated Shift Colors**: Enhanced the visibility of shift cell backgrounds in `style.css` (increased opacity to 35% for M/P/N and 28-30% for REC/FER) to make shift strikes visually distinct.
- **Thinner Division Grid**: Implemented dedicated CSS rules to make borders between calendar cells extremely thin and semi-transparent (`rgba(255,255,255,0.04)`), allowing shift blocks of the same color to merge cleanly into a continuous strike.
- **Weekend and Holiday Columns**: Highlighted weekend columns in blue (`rgba(59, 130, 246, 0.10)`) and holiday columns in red (`rgba(239, 68, 68, 0.14)`) across both header and body cells to instantly distinguish rest/holiday periods.
- **Sorted Operator Lists**: Updated the operator loading logic in `app.js` to sort operators by group (with "smart" group first, and "presenza" second) and alphabetically (A-to-Z) inside each group.

## [2026-06-11] dev | SHIFTER — Rolling week-by-week solver implementation

- **Rolling Solver Refactor**: Restructured the solver in `solver.py` to use a rolling weekly approach. It now schedules 53 weeks sequentially (one week at a time) instead of a single 52-week global model, eliminating search space bloat and timeouts.
- **Future Recovery Booking**: Programmed the rolling solver to book recoveries into the following week ($W+1$) by saving them to the database. The next week's solver run loads these bookings and enforces them as hard constraints (`off == 1`).
- **Progressive YTD Equity**: Refactored YTD stats to be loaded dynamically from the SQLite database before each week's run. Spreads for turns (M/P/N), weekends worked, complete weekends, Sabati Singoli, consecutive recovery pairs, and split recoveries are progressively optimized via soft objectives.
- **Diagnostics and Verification**: The full 2026 calendar (1 Jan to 31 Dec) was successfully generated in ~45 seconds. The diagnostics script verified all 12 months with 0 errors. Equity spreads converged perfectly (max shift spread: 5, max weekend worked spread: 3, max recovery pairs spread: 1).

## [2026-06-11] dev | SHIFTER — Optimization of consecutive and split recovery distribution

- **YTD Split Recovery Balance**: Implemented mathematical tracking of Year-To-Date split recoveries (calculated as `Total Recoveries YTD - 2 * Consecutive Recovery Pairs YTD`) and integrated a balancing objective into the CP-SAT solver.
- **Equity Spread Penalty Calibration**: Increased the balancing weights for both consecutive recovery pairs and split recoveries YTD to `350`. This successfully reduced the YTD consecutive recovery pairs spread across the 12 operators from 8 to 6, and the YTD split recoveries spread from 20 to 11.
- **Solver Timeout**: Increased the solver time limit to 30 seconds to allow the solver to search for a highly balanced solution under these tighter equity constraints.
- **Diagnostics and Validation**: Verified the generated schedule with the diagnostics script. Found 0 violations (100% compliance with presence, coverage, and weekday work rules).
- **Database Seeding**: Successfully re-seeded the database and populated the optimized calendar.

## [2026-06-11] dev | SHIFTER: Gestione Rolling Carry-Forward e Allineamento Debiti
- **Risoluzione Bug Conteggio Debiti**: Corretto filtro in `main.py` per includere tutti i recuperi (rimossa condizione obsoleta `data_weekend_lavorato != None`), risolvendo il conteggio errato che riportava medie di 66 giorni di debito e 0 recuperi singoli/doppi.
- **Supporto Carry-Over nel Solver**: Modificato `solver.py` per includere il debito iniziale dell'operatore (`op.carry_over_rec`) nei vincoli di accumulo YTD dei recuperi e penalizzazioni.
- **Risoluzione Vincoli Database**: Droppate e ricreate le tabelle di database pulite per supportare la nullabilità della colonna `data_weekend_lavorato` nei recuperi.
- **Ponte Temporale 2027**: Risolto lo sdoppiamento dell'ultima settimana di dicembre correggendo la chiave di raggruppamento settimanale (`(d.isocalendar()[0], d.isocalendar()[1])` invece di `d.year`). Esteso l'orizzonte di pianificazione del solutore fino alla domenica successiva al 31 dicembre (3 gennaio 2027) per garantire che l'ultima settimana contenga il proprio weekend.
- **Coerenza Storica**: I turni e i recuperi dei primi 3 giorni del 2027 vengono calcolati e salvati nel database per servire da storico continuo per l'anno successivo, eliminando tutti i riposi feriali ingiustificati emersi a fine dicembre.
- **Layout Dashboard**: Spostata la sezione informativa delle tiles sotto il calendario della matrice mensile per ottimizzare lo scorrimento e la lettura della griglia.
- **Aggiornamento Servizio**: Riavviato server backend `uvicorn` per applicare a caldo le modifiche.

## [2026-06-11] dev | SHIFTER: Apple Glassmorphism (Neutral Light) & Allineamento Contrasto UI
- **Generazione Asset di Sfondo**: Generata un'immagine di sfondo personalizzata `obsidian_bg.png` raffigurante una goccia d'acqua che cade in una superficie calma creando onde concentriche ampie e sparse che si espandono su un gradiente bianco-azzurro luminoso e pulito (decentrata in alto a destra).
- **Stile Glassmorphic Frosted (Light)**: Applicata una trasparenza vetrosa bianca satinata (`glass-panel` con opacity 35% e backdrop blur) a tutte le tiles della dashboard, aumentandone la trasparenza e rifinendo le ombreggiature per light mode.
- **Pillole Stondate per i Turni**: Sostituite le caselle quadrate della matrice turni con capsule/pillole fluttuanti stondate (`.shift-badge-pill`) con bordi lucidi completi e trasparenza colorata ad effetto vetro. I testi dei turni ereditano tinte scure ad alto contrasto per massima leggibilità.
- **Colonne Sticky Bianche ad Alto Contrasto**: Le colonne fisse della matrice mensile (sia cells `td` che headers `th`) sono state impostate a sfondo solido bianco (`#ffffff !important`) con testi scuri a contrasto per nascondere lo scorrimento dei dati in background.
- **Espansione Matrice Mensile**: Rimosso il limite di altezza `max-h-[680px]` e la barra di scroll verticale interna, consentendo alla tabella di allineare tutti i 12 operatori in una singola vista espansa.
- **Immagini/Avatar degli Operatori**: Aggiunto un generatore SVG in-app che associa a ciascun operatore un avatar circolare unico con gradiente e silhouette personalizzata, visualizzato accanto al nome nella griglia del calendario, lista assenze, configurazione e tabella equità.
- **Allineamento Dynamic Classes**: Allineato il comportamento di `app.js` per utilizzare classi scure su elementi dinamici (es. text-slate-800, border-black/5), prevenendo problemi di contrasto su sfondi chiari.
- **Legibilità Griglia e Footer**: Ottimizzati i badge e le tabelle di equità e fabbisogni nel footer per garantire il perfetto contrasto dei colori di stato dei turni e dei warning su sfondo chiaro.


---

## [2026-06-11] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-11] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-11] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-12] dev | SHIFTER — Cross-month streak selection support

- **Selezione Persistente tra i Mesi**: Modificato `loadData` in `app.js` per accettare un flag `keepSelection = false`. Nel setup dei pulsanti di cambio mese (dropdown, precedente, successivo), viene ora invocato `loadData(true)` per mantenere lo stato di selezione in memoria durante la navigazione temporale.
- **Rappresentazione e Ripopolamento Highlights**: Aggiornato il loop di rendering dei giorni in `renderCalendar` per verificare se ciascuna cella appartiene all'intervallo memorizzato in `swapSelection` (anche se iniziato in un altro mese) ed evidenziarla in blu (`own-streak-highlight`) al caricamento del nuovo mese.
- **Auto-Interrogazione Candidati Inframese**: Estratta la logica di chiamata API per le compatibilità in una funzione asincrona globale `highlightSwapPossibilities`. Se al render del calendario è presente una selezione completa in memoria, viene fatta automaticamente la query asincrona al backend per visualizzare i candidati lampeggianti nel nuovo mese.

## [2026-06-12] dev | SHIFTER — Pulse-swap amber animation and stylesheet caching fixes

- **Animazione di Swap in Arancione (pulse-swap)**: Refactorizzata la classe `.pulse-swap` e l'animazione `@keyframes pulseSwap` in `style.css` per utilizzare l'arancione/ambra (`#f59e0b`). Aggiunto `!important` sul bordo e sull'animazione della pillola per forzarla a sovrascrivere i bordi specifici del turno (es. `.cell-shift-N`), che a loro volta avevano `!important` e impedivano la visualizzazione dell'animazione.
- **Cache-Busting per Risorse Statiche**: Aggiornato `index.html` per aggiungere il parametro di versione `?v=6` sia all'importazione di `style.css` che a `app.js`, forzando il browser del client ad aggiornare i fogli di stile e i file javascript.
- **Robustezza Javascript**: Modificato `app.js` per aggiungere un fallback sicuro (`(cand.warnings || [])`) durante la concatenazione dei warning in stringa, prevenendo interruzioni di esecuzione in caso di assenza del campo.

## [2026-06-12] dev | SHIFTER — Streak swap matching fix and manual edit modal disable

- **Filtro Preferenze Corretto**: Risolto un bug nel motore di scambio (`swap_engine.py`) che escludeva i candidati senza preferenze esplicite nel database (come Caniglia). Ora, se `cand_pref_list` è vuoto, l'operatore viene considerato compatibile e non viene scartato a priori.
- **Disattivazione Modal Forzatura**: Temporaneamente commentata la visualizzazione della modale di modifica manuale (`modalEdit` / "Modifica Turno") nel click handler delle celle del calendario in `app.js`. Questo consente di testare l'evidenziazione e il trigger dello scambio di streak compatibili senza l'interruzione della modale.

## [2026-06-13] dev | SHIFTER — Visual redesign of top navbar, sections, and compact sidebar column renaming

- **Mockup Top Navbar**: Implemented a dark glassmorphic navigation bar touching the top and side boundaries of the viewport, with the interlocking wave S logo, text `SHIFTER`, navigation tabs (`Dashboard`, `Schedule` underlined as active, `Reports`, `Settings`), and a profile avatar (with name `Sarah Kim` and chevron dropdown) on the right.
- **Month Navigation Capsule**: Moved the today date and month selector capsule from the header to the right of the `LIVE` section header, styling it with matching dark-glass parameters.
- **Section Headers Renamed**: Updated section titles to `LIVE`, `PLANNED`, and `HOLIDAYS` to improve page organization.
- **Compact Columns Renamed**: Renamed the carry-over column header `C.O.` to `REC` across the live and planned matrices, and updated the year closure confirmation prompt.
- **Sidebar Column Expansion**: Expanded the compact left-panel columns from `184px` to `198px` total (`cal-left-group` from `40px` to `54px`) to show the word `Gruppo` in full without clipping. Updated the holidays table sidebar to `162px` width.

## [2026-06-13] dev | SHIFTER — Relaxed weekly consistency constraint and resolved Week 25 infeasibility

- **Relaxed Weekly Consistency Constraint**: Modified the CP-SAT solver in `solver.py` to allow at most 2 shift types per operator per week (instead of a single hard-coded shift type), resolving the mathematical infeasibility in Week 25 where only 10 operators are active due to holidays.
- **Consecutive Switch Penalties**: Introduced consecutive-day shift type transition penalties (M -> P, M -> N, P -> N consecutively with weight `600`) and a multi-shift type week penalty (weight `2000`) in `solver.py` to maximize streak length and avoid daily shift flipping.
- **Year-Long Resolution**: Verified that the solver successfully schedules the entire 2026 horizon starting from January 1, 2026.

## [2026-06-13] dev | SHIFTER — Fixed holiday calendar rendering, scroll sync, and removed live calendar leave overlays

- **Holiday Seeder Upgrade (`seed_ferie_v3.py`)**: Re-seeded the `ferie` table to implement the refined business rule where weekend days (Saturdays/Sundays) and Italian national holidays do not deduct from the operator's 21-day balance. Consecutive blocks (2 weeks in peak summer/winter, 1 week scattered) insert calendar days in the DB to block shifts, but only weekdays count towards the 21 days limit. The remaining balance (typically 6 days) is scattered as single, double, or triple ferial days.
- **Leave Overlays Removed from Live Calendar**: Prevented the frontend from overlaying "FER" or "MAL" badges on the Live calendar grid. The Live calendar now solely displays the operator's actual shifts (M, P, N) and recoveries (REC), keeping the live schedule display clean.
- **Holiday Calendar Two-Panel Split Layout**: Duplicated the exact double-panel structure (fixed left panel for operators list with avatars and group badges, scrollable right panel for the day grid) from the live and planned matrices. Added CSS styling for `#ferie-left-panel` to ensure layout alignment and width compatibility.
- **Holiday Calendar Scroll Synchronization**: Enhanced the scroll synchronization mechanism (`scrollToMonth` and `scrollToDate` in `app.js`) to apply horizontal offsets to `#ferie-calendar-container` synchronously along with `#main-calendar-container` and `#planned-calendar-container`.
- **Consistent Holiday Badges Styling**: Updated the holiday table badge rendering in `app.js` to utilize the existing stylesheet classes `.cell-shift-FER` and `.cell-shift-MAL` for consistent and visually premium rendering.

## [2026-06-13] dev | SHIFTER — Implementation of Option A for carry-over UI inputs and dynamic live badges

- **Option A Carry-Over Separation**: Shifted the starting carry-over (`C.O.`) editable inputs to the Planned (Fixed) Calendar sidebar. The Live Calendar `C.O.` column now displays a read-only dynamic outstanding debt badge (pulses red if >0).
- **Delta-Based Carry-Over Formula**: Refactored `get_annual_summary` in `main.py` to calculate `carry_over_out` using planned baseline counts as a reference point. This cancels out any boundary effects (e.g. week 53) and ensures that removing a recovery immediately increments the live outstanding debt by +1.

## [2026-06-13] dev | SHIFTER — Analysis of year-boundary effects on YTD carry-over and new equity logic concept

- **Year-End boundary analysis**: Conducted a thorough diagnostic investigation on why Pellegrini's YTD carry-over debt did not increment when the user replaced a baseline recovery (`REC`) with a Morning shift (`M`) on June 16, 2026.
- **Root Cause Identified**: The CP-SAT solver plans week-by-week using ISO weeks. Week 53 of 2026 spans Dec 28, 2026 to Jan 3, 2027. The weekend shifts fall in 2027 (not counted in 2026 YTD WE), but their ferial recoveries are scheduled in 2026 (counted in 2026 YTD Rec), creating a +2 recovery surplus for Pellegrini in 2026. This surplus absorbs the manual removal of June 16 recovery, keeping the carry-over capped at 0.
- **Concept Created**: Added [[concepts/shifter-equity-boundary|shifter-equity-boundary]] and updated index.

## [2026-06-13] dev | SHIFTER — Batch manual override API and popover behavior enhancement

- **Batch Manual Overrides Endpoint (`main.py`)**: Created `POST /api/schedule/batch` to process multiple manual shift overrides within a single database transaction. The validation checks for N -> M rule violations are executed after flushing all changes, preventing transient violation errors when shifting an operator's multi-day baseline blocks (e.g. replacing a sick operator with consecutive Night shifts).
- **Batch Override Frontend Integration (`app.js`)**: Updated `applyShiftRange` to issue a single HTTP POST request to the batch endpoint.
- **Popover UX Improvement (`app.js`)**: Updated the cell click handler to only trigger the range actions popover on the second click (when a range or double-click single day is completed) rather than immediately on the first click.

## [2026-06-13] dev | SHIFTER — Range selection popover menu, manual overrides, recovery adjustment, and audit logging

- **Interactive Range Selection Popover**: Introduced a dynamic absolute-positioned popover menu (`#range-action-popover`) in `app.js` and `index.html` triggered by selecting a date range (or clicking a single cell) for any operator. The menu exposes quick links to search swaps (`highlightSwapPossibilities`), register leaves/sickness, force manual shifts, or cancel selection.
- **Unified Shift & Leave Range Application**: Implemented batch update functions `applyLeaveRange` and `applyShiftRange` in `app.js` to process operations across the entire selected date range by sending concurrent API calls to `/api/leaves` and `/api/schedule`.
- **Backend Overrides & Self-Correcting Carry-Over**: Refactored `save_manual_shift` in `main.py` to support `M, P, N, REC, RIPOSO`. Manual shift assignments (`M, P, N`) automatically delete conflicting recovery records on that date, incrementing the operator's debit. Setting a cell to `REC` deletes the shift and books a manual recovery (`data_weekend_lavorato = None`), decrementing the debit. Setting a cell to `RIPOSO` deletes both shift and recovery.
- **Date Boundary Constraints**: Blocked all calendar modifications (swaps, manual overrides, and leaves) on dates prior to the current date (`date.today()`) at both the frontend and backend levels.
- **Event Audit Log (Registro Modifiche)**: Created the `RegistroEventi` table schema in `database.py`. Implemented endpoint `GET /api/audit-log` in `main.py` and dynamic rendering in `app.js` inside a new "Registro Modifiche" tab (`tab-audit`, `#content-audit`) to display a detailed timeline of all manual calendar modifications.

## [2026-06-13] dev | SHIFTER — Baseline calendar annual summary columns replication

- **Summary Columns for Planned Grid**: Replicated the annual totals columns (M, P, N, WE, SAB, REC++, REC+, DÈB.) at the right end of the baseline/planned calendar matrix. Created a client-side dynamic calculator `computePlannedSummary` in `app.js` to compute the baseline statistics for each operator based on `schedule.turni_pianificati`, matching the exact mathematical rules of the backend.

## [2026-06-13] dev | SHIFTER — Enabled weekend and holiday shift swaps

- **Weekend Swap Restriction Removal**: Removed the frontend verification in `app.js` that blocked selecting and swapping weekend/holiday shifts. All swaps (both ferial and weekend) are now evaluated strictly by the backend solver logic (which validates minimum physical presence, maximum consecutive days, and rest periods).

## [2026-06-13] dev | SHIFTER — Same-day single-click swap validation and diagnostics

- **UX Improvement for Same-Day Swaps**: Enhanced the frontend click handler in `app.js` to automatically detect when a user clicks on a different operator's cell on the same day as the active selection start. The app automatically completes the selection range as a single-day streak, performs the API call to fetch swap options, and immediately triggers either the confirmation modal or the incompatibility alert displaying the detailed constraint violation reasons. This avoids requiring a double click on the same cell to select a single-day range first.

## [2026-06-13] dev | SHIFTER — Calendar two-panel split, selector fix, and colgroup alignment

- **Two-Panel Calendar Split**: Completely separated both the live calendar and the planned calendar into two distinct tables: a fixed-width left panel (274px wide, containing operator avatar, name, group badge, and carry-over) and a scrollable right panel (containing only the day grid). This solves visual alignment issues and keeps row heights perfectly aligned (34px via `.cal-row-op`).
- **Precise Month Selector Alignment**: Populated dynamic `<colgroup>` elements (`main-calendar-colgroup` and `planned-calendar-colgroup`) in the right panels to force a strict `36px` day column width. Removed the `cal-day-col` class from the month colspan header elements, preventing the browser from collapsing month columns and ensuring that `scrollToMonth` maps to the exact pixel offset (`daysBefore * 36`).
- **Footer Horizontal Alignment Fix**: Removed the obsolete prepended label cells (e.g. `<td colspan="3">` containing descriptive labels) from the right panel's footer rows (`validateShiftRequirements` counts), which were pushing the actual numeric counts to the right by several days. Transferred these descriptive labels to the left fixed panel (`main-left-req-*` rows) for clear alignment.
- **Incompatible Candidate Explanations & Click Alerts**: Refactored `SwapEngine.get_possibilities` to return incompatible candidates along with the specific reasons (e.g. "Riposo insufficiente (0h) Notte -> Mattina") in a new `candidati_incompatibili` response array. Added interactive alerts in `app.js` click handler to display these reasons when clicking an incompatible candidate, and added custom messages for invalid clicks (Saturdays/Sundays or REC shifts).
- **Complete Planned Calendar Integration**: Refactored `renderPlannedCalendar` in `app.js` to correctly render the left panel (with operator avatars and group badges) and right panel separately, instead of packing all cells into the right panel which caused structural mismatches.
- **Refresh Bugfix**: Updated carry-over changes and year closing logic to refresh the annual calendar using `getDaysInYear` rather than shrinking the view to a single month.
- **Backend Test Suite Green**: Updated `tests/test_solver_logic.py` to import and reference `TurnoEffettivo` instead of the obsolete `Turno` model class, successfully restoring integration test execution functionality.

## [2026-06-13] dev | SHIFTER: Analisi Streak Scambiabili in Dashboard & Gestione Ferie Interattiva
- **Analisi Streak CLI & API**: Creato lo script parametrizzato [analyze_swaps.py](file:///home/Projects/NH-Mini/sviluppi/SHIFTER/src/backend/analyze_swaps.py) e aggiunto l'endpoint `/api/swaps/analyze` per determinare le streak di turni scambiabili con altri operatori nell'anno 2026 senza violare i vincoli di riposo, presenza in sede o coesione.
- **Interfaccia In-App Swap Analyzer**: Integrato un pannello vetroso a fondo pagina per impostare operatore + turno ed esporre i risultati direttamente in una tabella interattiva con badge colorati e relativi warning di sicurezza.
- **Calendario Ferie Interattivo**: Modificata la griglia del calendario ferie per renderla cliccabile, consentendo di aggiungere o rimuovere giorni di ferie per qualsiasi operatore direttamente sulla cella.
- **Reset Ferie e Pulizia Audit**: Aggiunto un pulsante di cancellazione totale delle ferie (`DELETE /api/leaves`) e implementato la rimozione automatica delle entry di audit log (`RegistroEventi`) a partire dalla data di Pivot all'avvio del ricalcolo del solutore.
- **Documentazione Secondo Cervello**: Creata la pagina [[concepts/shifter-swap-analysis|shifter-swap-analysis]] e aggiornato l'indice generale [[index]] di NH-Mini.



---

## [2026-06-13] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-13] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-13] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-13] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-13] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-13] dev | SHIFTER: Manual override constraints, presence validation and carry-over weekend fix

- **Validazione Vincoli Forzature**: Aggiunti controlli per N->P, P->M e per il vincolo dei 6 giorni consecutivi alle forzature manuali singole e batch.
- **Mancato Incremento C.O.**: Semplificato e corretto il calcolo dei weekend lavorati YTD basandolo sul conteggio effettivo di tutti i sabati/domeniche lavorati (inclusi quelli isolati), risolvendo il mancato aggiornamento del carry-over (REC) nelle forzature domenicali.
- **Presenza Fisica**: Implementata la verifica del vincolo di presenza fisica minima (min 1 operatore in presenza per turno attivo) sulle forzature e rimozioni manuali (RIPOSO/REC/M/P/N).


---

## [2026-06-14] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-15] promote | SHIFTER → CT204

**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC
- Progetto: SHIFTER
- RT Node: CT204 (192.168.1.204)
- Codice: rsync src/ → 192.168.1.204:/opt/SHIFTER/

---

## [2026-06-16] dev | SHIFTER — Modello 16 persone / 13 linee + solutore H2 OPTIMAL

- **Schema DB operatori**: aggiunte colonne `linea` (INTEGER), `data_inizio` (DATE), `data_fine` (DATE); tabella espansa da 13 a 17 righe
- **Operatori storici inseriti** (id=14-17): Christian Daniel (linea 3, fine 2026-01-31), Martina Vitiello (linea 4, fine 2026-02-28), Dino Brusco (linea 12, fine 2026-01-16), Luca Del Gobbo (linea 13, fine 2026-02-15)
- **Rimappatura dati**: `turni_effettivi`, `recuperi_effettuati`, `turni_pianificati` corretti per attribuire i turni alla persona fisica corretta per ogni periodo
- **Pulizia REC spurii**: eliminati 15 recuperi Mouloudi pre-23/03 e 10 recuperi Petrascu pre-01/06 (generati da rec_populate durante periodo di vacanza della linea)
- **Saldi H1 finali** (tutti OK): Pagano +4, Mouloudi +3, Caniglia +1, Petrascu +1, Pellegrini 0 (CO=5), tutti gli altri +3÷+11
- **Solver fix 1**: filtro `data_fine IS NULL` in solver.py, main.py (3 endpoint), aggiunto guard `if r.operatore_id in op_hist_rec_dates` per recuperi di operatori storici
- **Solver fix 2**: rimosso il blocco di pre-assegnazione carry-over REC (causava INFEASIBLE week 27 per Pellegrini: 3 REC forzati in settimana con max 2 WE disponibili); il valore `carry_over_rec` resta nel budget constraint
- **Solver H2**: OPTIMAL — tutti i 13 operatori attivi hanno saldo ≥ 0 a fine anno; turni distribuiti su Jul-Dec 2026  

## [2026-06-17] dev | SHIFTER — Fix carry_out formula, UX audit, layout 2-colonne, raffinamenti wiki

- **Fix formula carry_over_out** (`main.py`): la formula precedente era degenere quando planned=actual (restituiva sempre carry_in). Ora: `carry_out = max(0, carry_in + H2_WE+FES - H2_REC)` con H2 = turni post pivot_date. Tutti gli operatori: carry_out=0 dopo run solutore H2.
- **Solutore H2 verificato**: saldo corretto — Guareschi carry_in=9 azzerato con 44 REC su 32 WE+FES in H2.
- **UX**: rimossa tabella MESE (ridondante), scroll calendari ora naviga per mese con toggle mese/giorno, operatori inattivi a fine anno in opacity 0.18, calendario HOLIDAYS rinominato FERIE PIAN. con ferie storiche H1 visibili.
- **Layout**: pannello Analisi Streak Scambiabili affiancato a Gestione Operatori nella griglia 2-colonne.
- **Wiki**: documentate design decision (LIVE/PLANNED divergenza voluta), architettura carry-over, blocco ferie trimestrale, backlog R1-R6 in `stack-shifter.md`.

## [2026-06-21] dev | SHIFTER — G/REP tracking, forzatura manuale, bypass lock admin, deploy CT204

- **G/REP nel live calendar**: le celle con `tipo=sostituzione` nella tabella ferie ora mostrano direttamente G (feriale) o REP (weekend/festivo) senza attendere il solutore; `sostMap` costruito al render da `leaves` filtrate.
- **Fix batch endpoint G/REP**: `/api/schedule/batch` non aveva branch per `fascia in ["G","REP"]` — cadeva silenziosamente senza scrivere nulla nel DB. Aggiunto branch con upsert su `turni_effettivi`.
- **Solver preserva G/REP manuali**: prima del clear, il solutore salva i `TurnoEffettivo` con fascia G/REP; dopo aver caricato `sostituzione_days`, i giorni manuali vengono aggiunti a `future_leaves` (bloccando M/P/N) e ripristinati nella fase persist.
- **Admin bypass lock trimestrale**: `isLocked` ora include `!isAdminView` — gli admin possono editare ferie in qualsiasi trimestre.
- **CSS version bump**: `style.css?v=11`, `app.js?v=21` — forza reload dei badge G/REP in tutti i client.
- **Deploy CT204**: rsync `backend/*.py` + `frontend/{index.html,app.js,style.css}` → `/opt/SHIFTER/`. Installate dipendenze mancanti dal venv: `openpyxl`, `python-multipart`. Servizio `SHIFTER.service` attivo e verificato (API `/api/operators` HTTP 200).

## [2026-06-22] dev | SHIFTER — calendar refactor, slide-in panel, git workflow LXC190→GitHub→CT204

- **Rimozione summary columns**: le colonne statistiche fisse sono state rimosse dal calendario LIVE e PLANNED; il markup e i colgroup corrispondenti sono stati ripuliti da `app.js` e `index.html`.
- **Pannello slide-in (LIVE only)**: nuovo pannello statistiche sul bordo destro, attivato via hover sulla strip trigger. Stessa struttura tabella del calendario (`cal-row-op` ecc.) per allineamento pixel-perfect delle righe operatore. Sfondo frosted glass `rgba(15,23,42,0.65)`.
- **Riduzione larghezze colonne**: `cal-left-group` 54→36px, `cal-day-col` 36→32px — 31 giorni del mese ora sempre visibili. `COL_WIDTH = 32` in app.js per scroll offset corretto.
- **Header "Gr."**: "Gruppo" rinominato "Gr." in tutti e 3 i calendari.
- **User mode filter**: celle oltre `pivot+3m` renderizzate come punto (nasconde pianificazione futura).
- **Default pivot**: `today+1` al page load; validazione client-side blocca run su pivot ≤ oggi senza bypass flag.
- **Git workflow stabilito**: primo commit `ce3d40b` con struttura `src/` su LXC 190 → force-push su `S3ph1r/SHIFTER` → CT204 allineata via `git reset --hard`. Service `WorkingDirectory` aggiornato a `/opt/SHIFTER/src`. Token git non persistito nei config file.

## [2026-06-23] dev | CV revision — benchmark con profili reali, ristrutturazione competenze e progetti R&D

- **Benchmark profili z/OS**: Analizzati profili reali di operatori senior italiani ed esteri. Rilevato il consensus sull'evitare codici di errore specifici (-911, B37) in favore di terminologie di processo.
- **Riorganizzazione Competenze**: Suddivise le skill in Consolidate (TWS, CA7, Control-M, DB2 locks, Helix, ServiceNow, VMware), Pregresse (Cobol, CICS, DB2 development, Endevor, ChangeMan) e R&D (Python, FastAPI, RAG, CP-SAT).
- **Esperienze Lavorative**: Mantenuta la cronologia e aggiornati i ruoli con i rispettivi stack storici; aggiornato il ruolo MPS Siena come "Operations Transition Coordinator".
- **Sideproject R&D**: Spostati i progetti homelab (DIAS, SHIFTER, Lifelog2, Stratex) nella sezione "Hobby, Interessi & R&D Personale" come studio architetturale indipendente.
- **File aggiornati**: `curriculum-vitae.md`, `online-profiles-drafts.md`, `cv-standard.html`, `cv-innovative.html`.

## [2026-06-23] dev | CT202 gateway — Telegram CF URL watcher, wiki aggiornata, service_catalog

- **cf-url-watcher**: `scripts/cf-url-watcher.py` + `cf-url-watcher.timer` su LXC 190 — polling ogni 60s di `http://192.168.1.202/gateway/cf-url.txt`. Se URL Cloudflare cambia → notifica Telegram. State in `state/cf-url-last.txt`.
- **Wiki gateway**: `ct202-gateway.md` completamente riscritto (era del 2026-04-24): routing table attuale, Authelia, Cloudflare, LAN block.
- **dependency-map.md**: aggiornato con nuove route e mention Cloudflare.
- **service_catalog.py**: gateway entry aggiornata — Cloudflare, Authelia, note route.

## [2026-06-23] dev | CT202 gateway — fix /gateway/ LAN, cleanup typo, Cloudflare doc, dashboard v2

- **Fix `/gateway/` LAN**: route mancante nel block `server_name 192.168.1.202` (`shifter-lan.conf`). Aggiunta duplicazione delle 3 location `/gateway/` — dashboard ora raggiungibile da `http://192.168.1.202/gateway/`.
- **Rimosso typo `/lifelo/`**: route morta rimossa da `lifelog.conf`.
- **CF URL sync**: script `/usr/local/bin/cf-url-sync.sh` + `cf-url-sync.timer` (ogni 30s) — scrive URL Cloudflare Quick Tunnel in `/var/www/html/gateway/cf-url.txt`.
- **Dashboard gateway v2**: aggiunta sezione Cloudflare (URL da cf-url.txt, badge effimero), route map statica, aggiornato titolo e stack info.
- **Documentazione riscritta**: `knowledge/network/internet-gateway-pattern.mdc` — architettura completa, 2 server block, route map, Authelia, Cloudflare Quick Tunnel, operazioni comuni.
- **Verifica backend**: CT201 DIAS ✅, CT203 Lifelog2 ✅, CT190 Stratex ✅, CT204 SHIFTER ✅, Authelia ✅.

## [2026-06-24] dev | Lifelog2 FASE 1 — Completata: Confidence Tier + Dual Pool + Day Digest Filter + Bulk Reenqueue

- **DB Reset completo**: 1301 atoms, 376 episodi, 2 giorni cancellati; 1301 segmenti resettati a `enriching` con `transcript_key` preservata (migration 0021)
- **Stage C fix 1 — Case 3**: `_annotate_turn_classes()` — turni lunghi (≥45s) in contesto dialogo → `ambiguous` (non `dialogue_likely`)
- **Stage C fix 2 — rwr<0.10**: `_classify_conversation_type()` — segmenti dove Roberto parla <10% delle parole → `ambient_voices` (non `real_dialogue`)
- **Prompt v18**: etichette ambiguous con durata `[SPEAKER_XX|?Xs]` + soglie: ≤15s dialogo, ≥45s presumi MEDIA
- **Migration 0020**: colonne `confidence_score`, `extraction_tier`, `data_pool` su `segments` e `memory_atoms`
- **Stage C1**: confidence score `logprob×0.5 + snr×0.3 + diarization×0.2`, tier full/standard/minimal, gate dual-pool trusted/flagged
- **worker_day_digest.py**: episodi filtrati per data_pool (solo trusted atoms in SEZIONE 1); episodi con 0 trusted atoms → SEZIONE 2 ambient
- **Test batch 2026-06-07**: 32 segmenti, 4 trusted (3 corretti + 1 corretto post-fix DB), digest validato: gaming podcast → SEZIONE 2, conversazioni reali → SEZIONE 1
- **Bulk reenqueue**: 1269 segmenti (2025-08-01 → 2026-06-24) pushati in `lifelog:stream:c_done`, orchestrator in drenaggio
- **Script**: `scripts/reenqueue_batch.py` — ricostruzione payload Stage C da DB + transcript_key senza ripetere WhisperX

## [2026-06-24] dev | Lifelog2 — Refactor Roadmap: Confidence Tier, Thread Model, Dual Pool

- **Documento creato**: `NH-Mini/concepts/lifelog2-refactor-roadmap.md` — roadmap operativa con task list spuntabile per 5 fasi
- **Fase 1**: Confidence Score multi-dimensionale in C1 (`logprob×0.5 + snr×0.3 + diarization×0.2`), tier Full/Standard/Minimal, dual pool Trusted/Flagged, Day Digest filtro data_pool
- **Fase 2**: Voiceprint Resolver in C1 — stable vp_ID cross-atom via cosine similarity contro session registry (Redis TTL 2h), tabella `session_voiceprints`
- **Fase 3**: Stage D Thread-Aware per tier=FULL — output `threads[]` con type/vp_set/ops, tabella `atom_threads`, prompt v18
- **Fase 4**: Thread Registry Redis + Grouper refactor Stage F — episodi semanticamente puri per tipo thread
- **Fase 5**: Cleanup analisi secondo livello — filtro data_pool in Z4/Z6/Z7, toggle frontend, backfill storico
- **Documenti aggiornati**: `lifelog2-quality-gate.md`, `lifelog2-turn-classification.md`, `lifelog2-thread-consolidation.md` con riferimento alla roadmap
- **Motivazione**: test reinject 2025-12-17 → 2026-06-24 ha rilevato gap Case 3 (interleaved media), confermato che i filtri meccanici soli sono insufficienti, identificato necessità di graceful degradation basata su qualità audio

## [2026-06-24] note | Lifelog2 M6 — gap retention/oblio documentati

- **Gap 1**: file `discarded` (nessun atom prodotto) non vengono cancellati da MinIO. `_reject()` Stage B swallows eccezione su `remove_object`; backfill non cancella sorgente. Valore zero, accumulo indefinito.
- **Gap 2**: `cleanup_ambient_audio.py` copre solo `capture_class='ambient'`. File mixed/personal e staging orfani non hanno policy.
- **Policy da implementare in M6**: discarded → 24h; consolidated → `retention_class` atom; staging orfani > 30gg → discard + delete.
- Annotato in `stack-lifelog2.md` sezione M6.

## [2026-06-24] dev | Lifelog2 Stage C — turn-level classification + Day Digest v4

- **`stage_c_asr.py`**: aggiunta `_annotate_turn_classes()` — classifica ogni turno diarizzato come `personal`/`media_passive`/`dialogue_likely`/`ambiguous` tramite logica deterministica (durata + contesto temporale con turni di Roberto). Scritto su `speaker_turns.turn_type` (DB), MinIO blob (`turn_class` per-turn + `turn_classes` dict), Redis emit (`max_other_turn_s`).
- **`_compute_conversation_metrics()`**: aggiunto `max_other_turn_s` per esporre outlier nascosti dalla media.
- **`_classify_conversation_type()`**: attivato `hybrid` conversation_type (`max_t > 45s AND avg_t < 60s`). `analysis_tier=2.0` per hybrid.
- **`worker_day_digest.py`**: prompt v4, atom-level grounding (`_render_episode()` bypassa `narrative_summary` se ci sono atom), query atoms per episodio, `has_ambient` guard, `max_tokens=3000`.
- **`stage_z4_day_digest_v4.txt`**: nuova versione prompt con sezioni SEZIONE1/SEZIONE2, regole anti-allucinazione ambient, divieto esplicito cross-sezione.
- **Concept doc creato**: `NH-Mini/concepts/lifelog2-turn-classification.md` — documenta il problema, i tre casi, l'algoritmo, le soglie, i limiti e la roadmap voiceprint.
- **Deploy**: `stage_c_asr.py` deployato su CT203 (syntax check OK).

## [2026-06-25] dev | Lifelog2 — validazione pipeline + ghost episode cleanup

- **Validazione end-to-end** completata: atoms trusted tracciati fino ai speaker_turns reali
- Tutti gli atom `personal_mono` verificati: testo turn Roberto corrisponde al summary LLM
- **Issue critico identificato**: misattribuzione voiceprint in `real_dialogue` — SPEAKER_01/02 attribuiti a Roberto con conf 0.51–0.56 perché unico voiceprint registrato; `attribution_source=None` su tutti i turn
- **Ghost cleanup**: `DELETE FROM episodes WHERE episode_id NOT IN (SELECT DISTINCT episode_id FROM memory_atoms WHERE episode_id IS NOT NULL)` → 163 eliminati, 209 rimasti
- Profile facts: 1001 totali, 944 con source_memory_ids; 16 relation facts senza provenance
- FASE 2 (Voiceprint Resolver) rimane il fix necessario per la misattribuzione in real_dialogue

## [2026-06-26] dev | Lifelog2 — FASE 3: Stage F riscritto (conversation thread formation)

- `stage_f_grouping.py` completamente riscritto (834 righe) — da episode-based a thread-based
- Pass 1: voiceprint resolution con centroidi per label WhisperX + vp_hash stabile (sha256/person:UUID)
- Pass 2: role classification da `speaker_turns.turn_type` (personal/media_passive/dialogue_likely/ambiguous)
- Pass 3: thread stitching deterministico — hash match + cosine fallback (0.65); split media/personal/ambient
- Pass 4: ARIA coherence validation solo per personal_dialogue/personal_mono/ambient_dialogue; chiusura silenziosa per media_passive/ambient_mono
- Timeout: personal 15min, media 8min
- Deployato su LXC 203 `/opt/Lifelog2/src/backend/lifelog2/services/pipeline/stage_f_grouping.py`

## [2026-06-26] dev | Lifelog2 — FASE 3: migration 0022 + correzioni doc architettura

- Migration 0022 applicata su DB: conversation_threads, thread_turns, sagas (ex threads), drop episodes, vp_hash su speaker_turns
- Doc lifelog2-conversation-thread-architecture-v1.md: 4 gap corretti dopo walkthrough scenari
  1. `turn_class` → `turn_type` (nome reale colonna DB in speaker_turns)
  2. `create_new_threads` splitting logic formalizzata (media → thread separato da personale)
  3. Pass 4 ARIA: solo thread personal_dialogue / personal_mono / ambient_dialogue; media_passive chiude senza ARIA
  4. "Thread closed non si riapre mai" reso esplicito in lifecycle e regole chiusura
  5. canonical_label scope-locale al thread (non globale)

## [2026-06-26] dev | Lifelog2 — doc audit + pulizia pre-FASE 3

- Aggiornato `lifelog2-pipeline-validation-roadmap.md`: M1-M5 ✅ completati/superseded; sezione "Riprendi da qui" sostituita con CHIUSO + sintesi risultati
- Aggiornato `lifelog2-classification-evolution-blueprint-v1.md`: header stato implementazione P0-P3 ✅ / P4-P5 deferred / P6 superseded; marker inline per ogni P
- Aggiornato `lifelog2-status-roadmap.md`: Stage F → ⚠️ in riscrittura; Z3 Episode → deprecato; Z6 → FASE 3; FASE 3 sezione aggiunta in roadmap; stato visivo aggiornato; P1-P3 check completati
- Aggiornato `lifelog2-intelligence-addendum-v1.md`: status → ✅ Implementato FASE 1
- Aggiornato `lifelog2-identity-resolution-design.md`: status → ✅ Implementato con note issue VOICEPRINT_MATCH_THRESHOLD
- Aggiornato `index.md`: pipeline-validation-roadmap → CHIUSO; blueprint → P0-P3 done; nuovo entry conversation-thread-architecture-v1
- Tutti i doc cross-referenziano [[lifelog2-conversation-thread-architecture-v1]] come doc attivo FASE 3

## [2026-06-26] dev | Lifelog2 — Conversation Thread Architecture design

- Progettata architettura `conversation_thread` come unità di analisi post-atom (FASE 3)
- Documento creato: `docs/lifelog2-conversation-thread-architecture-v1.md`
- Nuove tabelle: `conversation_threads` + `thread_turns` (vp_hash cross-atom normalization)
- Stage F riscritto: 4 pass deterministici + ARIA validation alla chiusura
- Thread sostituisce episode; `threads` → `sagas`; `episodes` → deprecata
- Worker Tier-2/3 operano su thread (non atom): profile_builder, identity_detective, Day Digest, Z6
- Invariante chiave: ARIA riceve sempre transcript con canonical_label, mai speaker_label_raw WhisperX

## [2026-06-27] dev | Lifelog2 — Architettura doc: thread types, Tier2 compat, Rilevanza Dinamica, P3 roadmap

- `knowledge/memory-model.md`: schema ConversationThread aggiornato a colonne reali DB (summary, topics, sentiment, coherence_score, data_pool, atom_count); thread_turns schema completo (vp_hash, thread_role, sequence_pos, ecc.); tabella classificazione thread_type; limitazione nota thread_type non aggiornato in _extend_thread(); sezione "Rilevanza Dinamica e Reclassificazione Thread" (data_pool, P3a/P3b/P3c pseudocode, worker visibility, media_passive vs ambient limitation)
- `knowledge/architecture.md`: sezione "Compatibilità Tier2 con architettura ConversationThread" — identity_detective/place_detective/profile_builder/profile_validator agnostici ✅; day_digest/thread_consolidation LEGACY ⚠️ (referenziano tabella episodes droppata); refactor plan per Day Digest (conversation_threads trusted) e Thread Consolidation (linked_thread_ids); P3 roadmap esteso P3a/P3b/P3c; worker visibility scope by data_pool
- `NH-Mini/entities/systems/stack-lifelog2.md`: Z3 Episode → ConversationThread; pipeline ASCII F/G aggiornati; Stage G "episodi" → "thread"; thread_turns schema completo; Day Digest legacy warning; nuova sezione "Rilevanza Dinamica dei Thread" (data_pool, retention, P3 back-propagation, limitazione extend)
- Investigazione: Fix 3 false positive (monitor query contava tutti VPs invece di solo ambient-role); fix post-run SQL progettato e pronto
- Background task disruption: due DB reset durante backfill (ore 13:48/13:55 CEST) — 134 thread/1014 thread_turns cancellati; DB pulito e pipeline ripartita; backfill completato a 1301/1301 atoms, 1012 thread

## [2026-06-27] lint | Lifelog2 — /lint lifelog2: memory-model + api-contracts aggiornati a FASE 3

- `knowledge/memory-model.md`: Z3 Episode → ConversationThread (schema completo + thread_turns join table); Saga (Z6) rinominata; refactors pending annotati inline
- `knowledge/api-contracts.md`: Section 5 Web API con legenda ✅/⚠️/🔲; DB snapshot e telemetry aggiornati; sezione 6b "Refactors Pending FASE 3" con 8 refactor prioritizzati
- 67 ✅, 1 ⚠️ (journal END stantio — normale), 0 ❌

## [2026-06-27] dev | Lifelog2 — Stage F/G fix: race condition orchestratore + ended_at + MAX_THREAD_GAP_S

- Orchestratore: rimosso `_covers_trigger.set()` dal main loop; aggiunto in `_grouping_loop` post-drain; rimosso timer startup 90s da `_covers_loop`. Stage G ora parte SOLO dopo Stage F drain completo.
- `MAX_THREAD_GAP_S`: 8h → 10 min (uniforme per tutti i thread_type — stesso semantico di CLOSE_AFTER_ATOMS=2)
- `ended_at`: `NOW()` → `last_atom_at` in tutti i path di chiusura (_close_thread_with_aria + _close_thread_no_turns)
- DB reset: 2571 thread_turns + 288 conversation_threads; backfill v2 ripartito con 1301 atoms (17:55 LXC 203)
- Wiki: `stack-lifelog2.md` (Stage F section → conversation_threads), `architecture.md` (orchestrator loops), `development-log.md` (entry 2026-06-27)

## [2026-06-29] dev | Lifelog2 — Cover fix: EpisodeCard bug, Stage D v19 prompt, atom cover backfill

- Bug: `EpisodeCard.svelte` ricostruiva cover URL con vecchio pattern `/api/dashboard/cover/${episode.id}` (endpoint episodi, tabella droppata) invece di usare `episode.cover_url` dall'API → fix: usa `episode.cover_url ?? null`
- Diagnostica: 1282 atom cover_image_key in DB erano stantie (file MinIO cancellati in sessioni precedenti); MinIO 0 file sotto `covers/atoms/`
- Stage D v18 → v19: style suffix visual_prompt cambiato da "flat vector illustration style, isometric, muted pastel color palette, clean studio background, minimalist" a "cinematic wide shot, atmospheric lighting, dramatic composition, photorealistic, no people" — allineato allo stile thread (FLUX non rende bene flat vector)
- SQL backfill: REPLACE suffix su 940 visual_prompt atom esistenti; UPDATE 1282 cover_image_key → NULL
- Stage G rilanciato: 1282 atom in coda, genera cover con nuovi visual_prompt cinematici
- config.json aggiornato: stage_d_enrich = v19 (LXC 203 + local dev)

## [2026-06-30] dev | Lifelog2 — FASE 2: Session Voiceprint Resolver deployato in Stage C

- Migration 0027: `session_voiceprints` (session_id, stable_vp_id, voiceprint_embedding, person_id, atom_count) + colonna `speaker_turns.vp_stable_id VARCHAR(32)`
- `_get_or_create_session_id()`: Redis-based, gap<30min=stessa sessione, TTL 90min, usa RawCapture.started_at reale (backfill-safe)
- `_resolve_voiceprints()`: cosine vs registro sessione; ≥0.82=match, 0.75-0.82 ambiguo=new, <0.75=new; `vp_R` sempre per Roberto, `vp_known_{8chars}` per enrolled, `vp_unk_{6chars}` per unknown
- Stream payload `c_done` arricchito con `session_id` e `vp_id_map` per Stage D
- Commit 1c5b10f pushato, LXC 203 sincronizzato; 7 unit test + 2 integration test OK
- Step 4 (live test cross-atom) pendente: richiede avvio pipeline da utente

## [2026-06-30] dev | Lifelog2 — Architettura thread: Stage D boundary authority, Stage E enrichment, Stage F rimosso

- Revisione architetturale completa del thread model (sessione 2026-06-30)
- **Stage D ridefinito**: non più enricher per atom, diventa boundary authority cross-atom — gira ad ogni atom, mantiene log thread aperti in DB, decide finalizzazione con LLM semantico
- **Stage E ridefinito**: thread enrichment batched — consuma thread finalizzati, 1 chiamata LLM per batch fino a 30K token, gestisce too_short/ambient senza LLM
- **Stage F rimosso**: i thread finalizzati sono l'unità semantica diretta, nessun grouper intermedio
- **Thread Builder superato**: la comprensione semantica di Stage D rende inutile un grouper deterministico a monte
- Regole finalizzazione: gap>10min (immediato) | 2 atom senza continuazione (pending→finalized) | 180 turni (force-cut Part N)
- Context budget Qwen3-14B su 16GB VRAM: ~30K token usabili; caso tipico ~8.7K token; max realistico 5-6 thread aperti simultaneamente (si risolvono entro 2 atom)
- Thread states: open → pending_finalization → finalized (+ too_short, ambient_incomprehensible)
- Thread Parts: force-cut produce Part 1/2/3 con parent_thread_id condiviso — card separate in dashboard
- Aggiornato `concepts/lifelog2-refactor-roadmap.md`: FASE 3 e FASE 4 riscritte, sequenza aggiornata, tabella "Cosa cambia"

## [2026-07-06] dev | Lifelog2 — Thread Builder v2: hardening completo, force-cut per volume, doc sync

Sessione lunga (2026-06-29 → 2026-07-06, più volte compattata) di hardening del Thread Builder v2 su dati reali. Documentazione completa in `sviluppi/Lifelog2/docs/lifelog2-thread-builder-hardening-2026-07.md` — questo entry è la sintesi.

- **Redesign identità voiceprint** (2026-07-04): eliminato bucket condiviso `vp_unk_nr` (causava frammentazione di thread — stessa conversazione spaccata in thread diversi a giorni di distanza). Sostituito da `vp_unk_noemb` + soglia `MIN_VP_TRUST_DUR_S=1.5s`. `turn_reliability` disaccoppiato dalla durata del turno, ora puro `avg_logprob`.
- **Gap-enforcement dinamico** (2026-07-05): da blocklist statica a state machine sequenziale in ordine cronologico reale — copre anche creazione thread dentro lo stesso batch.
- **Correzione meccanica mono/dialogue** (2026-07-04): `_correct_thread_type_at_closure()` corregge entrambi gli assi (personal↔ambient E mono↔dialogue) ad ogni chiusura thread.
- **Naming MinIO anti-disastro** (2026-07-05): chiave oggetto codifica timestamp+GPS invece di UUID casuale, sia in staging che archivio permanente.
- **Validazione end-to-end su dati reali** (2026-07-05/06): 675 segmenti reali da upload telefono, 168 thread con 0 violazioni gap.
- **Force-cut per volume di testo, non conteggio turni** (2026-07-06): causa radice di un thread da 47KB/15 turni che sforava il context LLM di Stage E (400 Bad Request, error-swallowing silenzioso). `FORCE_CUT_TURNS=180` non si accorgeva mai — il conteggio turni non dice nulla sul volume testo. Nuovo `THREAD_VOLUME_BUDGET_CHARS≈21620`, migration 0028. Bug scoperto in validazione: roster/rolling_summary non propagati ai thread creati da redirect (gap o volume) → Stage E arricchiva da roster vuota → allucinazioni. Fixato in due passi (`touched_thread_ids` + step dedicato post-LLM per l'eredità del rolling_summary).
- **Doc aggiornati**: `sviluppi/Lifelog2/knowledge/{architecture,memory-model,development-log}.md`, `sviluppi/Lifelog2/docs/lifelog2-thread-refactor-roadmap.md`, `NH-Mini/entities/systems/stack-lifelog2.md`, `NH-Mini/concepts/lifelog2-refactor-roadmap.md`.

## [2026-07-13] dev | Tier2 Alignment — tutti i worker migrati a thread e deployati

Implementata l'intera roadmap [[concepts/lifelog2-tier2-alignment-roadmap]] in una sessione notturna (durante il drain ASR del batch 1200): Identity Detective (marker 0029 + prompt v4), Day Digest (prompt v5), Profile Builder (Strato 1 da open_loops, Z7 per vp_stable_id), geo-attach in Stage E + Place Detective, Saga Builder su sagas.linked_thread_ids (0030), retention_class per thread (0031, solo dato). Commit `3be9254`→`52dfa5b`, migrations applicate su CT105. Dettaglio nel blocco datato della pagina roadmap.

## [2026-07-13] query | Tier2 Alignment Roadmap — worker secondo livello da atom a thread

Analisi della codebase dei 6 worker Tier2 (identity/place detective, day digest, profile builder, profile validator, thread consolidation) contro il nuovo contratto dati thread-native (Stage A→G). Esito: tutti no-op dal 2026-06-29 (memory_atoms vuota), thread_consolidation e day_digest rotti anche a schema (episodes droppata, threads→sagas). Roadmap in 6 punti con priorità, gap geo-attach `location_id`, 3 decisioni aperte. Nuova pagina [[concepts/lifelog2-tier2-alignment-roadmap]]. Fonti: data-architecture-v1 §4, intelligence-addendum-v1, places-intelligence-spec-v1, codice worker.

## [2026-07-14] dev | upgrade homelab connection to 5G CPE cascade (JC16)

Migrata la connessione internet principale di casa/homelab dal vecchio doppino telefonico ADSL/VDSL (RJ11) al router 5G JC16 CPE (Kena Mobile / TIM). Configurato il D-Link DVA-5592 come router in cascata impostando la porta WAN Ethernet (ETH5), abilitando il client DHCPv4 per ottenere l'IP `192.168.0.2` dal JC16 (`192.168.0.1`), e impostando la Rotta di Default sulla nuova interfaccia. Risolto un blocco di navigazione inserendo via CLI la regola NAPT mancante nella configurazione del D-Link per `"WAN Ethernet"`, e modificando i server DNS del DHCP server locale da quelli statici WindTre a quelli pubblici (`8.8.8.8`, `1.1.1.1`). Linea migrata e pienamente operativa via cavo a ~38 Mbps / 2.80 Mbps (cap di Kena).

## [2026-07-16] dev | Lifelog2 — chiusura refactor atom→thread + allineamento doc

- **Pipeline**: batch ~1200 segmenti drenato end-to-end senza perdite; ora in esercizio realtime. 937 thread (935 enriched), 927 cover, 14 persone/1510 turni linkati, 11 saghe.
- **Fix `c64a34e`**: started_at/last_turn_at dei thread dal primo turno assegnato (recording time, non processing) — 74 thread riparati via SQL.
- **Doc repo Lifelog2 allineati** (blocchi datati, storia preservata): status-roadmap (blocco stato 2026-07-16 in testa), hardening doc (§8: backpressure lockstep, retry PEL, soft deadline, GPU lease, date recording), thread-refactor-roadmap (CHIUSA), intelligence-addendum e places-spec (banner superamento atom→thread).
- **Wiki**: [[concepts/lifelog2-tier2-alignment-roadmap]] chiusa con blocco 2026-07-16; index aggiornato.
- **Gap noti**: GPS quasi assente dall'app Android (Places a zero), Day Digest catchup storico da lanciare, retention enforcement, drop memory_atoms, ciclo Tier1 a chunk.

---

## [2026-07-17] dev | Lifelog2 — calibrazione identità + intervista Roadmap Segnali

- **Calibrazione identità**: audit di grounding su un thread "live streaming" (1 turno utente su 11 narrato come partecipazione) ha portato a un'indagine sulla soglia voiceprint. Ipotesi iniziale (gate anti-chimera a 0.70) **smentita** da ascolto ground truth: 15/15 turni campione erano voce dell'utente, inclusi i chimera a 0.55. Soglia base 0.50 **confermata definitivamente**. Causa reale della distorsione: la diarizzazione non spezza il turno al cambio voce → parole di un podcast finiscono in un turno etichettato utente. Fix mantenuti: best-match resolution in C1, semantica di presenza in Stage E (prompt v5).
- **Incidente**: un commit di ritiro del gate anti-chimera non si era salvato (perso tra cambio modello e compattazione conversazione) — pipeline ha girato una notte con soglia sbagliata, zero impatto reale, scoperto verificando esplicitamente lo stato su LXC 203.
- **Intervista strutturata Roadmap Segnali**: 8 decisioni con Roberto su come sfruttare il 90% dei thread "solo statistici" — sintetizzate in [[concepts/lifelog2-signal-statistics-roadmap]].
- Dettagli: `workspace/vp-calibration-2026-07-17.md`, `workspace/lifelog2-signal-roadmap-interview.md`.

## [2026-07-18] dev | Lifelog2 — Roadmap Segnali Fase 0 + audit e fix frontend completo

- **Fase 0 implementata**: `conversation_threads.signal_class` (deterministico, backfill 46 actionable/73 contextual/824 statistical), tabella `weekly_metrics` (4 famiglie), worker giornaliero. Corretto in corsa un disegno errato (cluster vp per stringa — impossibile per via di `SESSION_GAP_MIN`) prima del deploy.
- **Audit frontend completo**: verifica dal vivo di tutte le 15 route → 4 endpoint a 500 in produzione (People era in nav primaria), causa comune modelli droppati/rinominati. Tutti sistemati: People, Sagas (dati reali dalle 11 saghe), Search/RAG, stats/monthly, Day detail, Tasks. Eliminate Timeline e Transcript (orfane). Prima UI per signal_class (badge+filtro) e weekly_metrics (card in Profile).
- **Bug aperto**: click su thread dalla grid → 501 nel dettaglio turni, in indagine.
- Dettagli tecnici: `sviluppi/Lifelog2/docs/lifelog2-status-roadmap.md` (blocco 2026-07-18), `lifelog2-thread-builder-hardening-2026-07.md` §9.

## [2026-07-21] dev | Lifelog2 — pratica di test sistematica + pulizia ORM completa

- **Nuova pratica scritta**: `sviluppi/Lifelog2/docs/lifelog2-dev-testing-practice.md` — la suite `tests/test_dashboard_smoke.py` (27 casi) è ora regola, non abitudine: un caso per endpoint dashboard, aggiornato nello stesso commit, verde prima di ogni deploy. Nata da 8 endpoint totali trovati rotti in silenzio in 3 giorni (4 il 18/07, altri 4 scoperti oggi scrivendo i test) + un test esistente rotto da un refactor di giugno mai notato.
- **Pulizia ORM completa**: rimosse Episode/Thread/MemoryAtom/ActionItem/Decision dopo verifica esaustiva di tutte le occorrenze. Trovati e riscritti /map, /places/{id}, /places/{id}/atoms, /people/{id}/context (tutti silenziosamente rotti, fuori scope dell'audit del 18/07) e la vista materializzata place_signals (stesso bug, mascherato da places vuota per GPS assente). Migration 0034 applicata sul DB di produzione con ok esplicito.
- **Verifica pipeline sotto carico reale**: con la registrazione riattivata, confermato via log WhisperX + telemetria che il degrado ASR è un fenomeno storico noto (max mai visto: 23 minuti per un segmento), e che il Thread Builder fermo da 5 giorni si è sbloccato da solo appena Tier1 ha avuto una finestra idle — nessuna soglia bloccante, solo scheduling che si autorisolve. Nessuna modifica al codice pipeline.
- Dettagli: `sviluppi/Lifelog2/docs/lifelog2-status-roadmap.md` blocco 2026-07-21.

## [2026-07-28] dev | WhisperX turni per parola — correzione ARIA alla causa a monte

> **Superata dalla voce successiva** (stesso giorno) dopo misura su audio reale — testo
> originale ricostruito da git (era stato sovrascritto in place da un edit successivo,
> contro la regola append-only; recuperato per storia ricostruibile, vedi commit `fa51b46`).

Correzione al backend `lifelog_whisperx` di ARIA (commit `abe9b1b`) che sana la causa a monte
di una lunga catena di problemi Lifelog2. WhisperX assegna lo speaker di un SEGMENTO per durata
dominante: un segmento a cavallo di due parlanti collassa sul maggioritario e le parole
dell'altro vengono assorbite; il backend concatenava poi i segmenti con la stessa etichetta.
Il "turno" era un blocco di tempo a etichetta dominante — misurati turni da 37s con domanda e
risposta di persone diverse, `n_segments_merged` fino a 79, uno da 299s, 53% dei turni senza
voiceprint utilizzabile. Da lì le persone ricorrenti fantasma e la voce dell'utente non
riconosciuta (cosine -0.007 col proprio centroide).

`assign_word_speakers` assegnava già lo speaker a ogni parola: il dato veniva scartato. Ora i
turni si tagliano sul cambio di speaker per parola. Aggiunto `speaker` ai word_timestamps.
Verificato offline su 5 casi (incluso il caso del bug e i tre fallback); non ancora su audio
reale — il backend non era in esecuzione, riparte col codice nuovo al prossimo task ASR.

Nuova pagina: `concepts/whisperx-word-level-turns.md`.

## [2026-07-28] dev | WhisperX: il tetto della diarizzazione — sostituisce la pagina sul taglio per parola

Indagine completa sul backend `lifelog_whisperx` di ARIA partendo dai raw text. Il difetto
c'era: whisperx assegna lo speaker di un segmento per durata dominante, quindi un segmento a
cavallo di due parlanti collassa sul maggioritario. Ma tutte le leve native provate per
correggerlo sono risultate PEGGIORATIVE, misurate sullo stesso segmento (SNR 21dB, 4-5 parlanti):
taglio per parola (30% dei turni a 1-2 parole), min_speakers 3/4/5 (da 42 a 99 frammenti sotto
0.5s), exclusive_speaker_diarization (alternanze spurie da 24 a 78). Gli embedding per parlante
di pyannote sono inutilizzabili come voiceprint: +0.038 di somiglianza con identità confermate
contro una soglia di 0.50.

Turni riportati alla costruzione per segmento. Restano nel contratto i segnali nuovi
(`diarization_stats`, speaker per parola, `speaker_embeddings`) per ETICHETTARE l'affidabilità
in Stage C1 invece di tentare estrazioni su materiale non attendibile.

Bug reale corretto per strada: il wrapper dell'orchestratore ricostruiva il body con soli tre
campi e scartava in silenzio ogni parametro di diarizzazione — senza accorgersene avremmo
concluso che i parametri non servono senza averli mai provati.

Pagina: `concepts/whisperx-diarization-ceiling.md` (sostituisce whisperx-word-level-turns).

## [2026-09-02] dev | Lifelog2 — guardia volume LLM, audit Z6, canale telemetria device

- **Guardia di volume/overflow condivisa** in `core/llm.py` (tutti i worker LLM): stima il prompt reale prima di ogni chiamata, riduce o rifiuta se il contesto non basta, ritenta con budget raddoppiato su risposte vicine al tetto (usage reali quando disponibili). Corretto anche un bug gemello in Stage D (budget di input turni congelato da v28 a v33, mai ricalcolato — stesso schema dell'incidente Stage E del 2026-08-30).
- **Audit tecnico Z6 (Saga Builder)**: mai eseguito contro dati reali prima di oggi (`sagas` a 0 righe) — corretta una riga stale nella wiki che affermava il contrario. Già ibrido (Gemini mapping + Qwen3 sintesi locale) contrariamente all'assunzione "solo Google". Trovato e corretto un tetto di volume mancante sulla sintesi per-saga. Primo dry-run reale: 17 episodi, 5 saghe create, dump verificati a mano.
- **Due indagini reali**: GPS che non si aggiorna durante un vero spostamento (causa probabile lato app, non risolta); sequestro del microfono durante le chiamate confermato empiricamente e per via documentale su tutte le strade soft (MediaProjection, tee sink AOSP, dump hardware MediaTek, Shizuku) — dichiarato chiuso su questo device senza root.
- **Nuovo canale device→server**: heartbeat (batteria/rete/GPS/mic/servizio) + sync rubrica (722 contatti) e registro chiamate (500 chiamate) — nuove tabelle Postgres, upsert su chiavi naturali in assenza di ID stabile dal device. Trovato e corretto un rischio reale di superamento della quota ngrok free-tier (20K richieste/mese) per cadenza heartbeat troppo aggressiva — vedi [[entities/containers/ct202-gateway]].
- **Frontend**: stato device espandibile (rubrica + ultime chiamate) negli header di `/` e `/pipeline`, glassmorphism in `/`.
- Dettagli: `sviluppi/Lifelog2/docs/lifelog2-session-digest-2026-09-02-device-channel.md`.

## [2026-09-02] lint | Riordino cronologico log.md e session-journal.md + convenzione d'ordine esplicita

Verifica richiesta dall'utente ("credo che alcuni registri di sviluppo siano prepend e non
append") su entrambi i file di log. Evidenza raccolta via `git log -p`: `log.md` era in
prepend per quasi tutta la sua storia nonostante l'header dicesse append, con un blocco di
backfill retroattivo (date dal 2026-05-01) cresciuto in coda per append — le due convenzioni
miste producevano un file non cronologico. `state/session-journal.md` (dichiarato prepend in
`.cursorrules`) aveva a sua volta entry fuori posizione (es. `2026-07-16 NOTA-ARIA` quasi in
fondo alle ~1900 righe invece che vicino alla cima).

Riordinati entrambi i file meccanicamente (script dedicato, dry-run verificato prima
dell'applicazione): `log.md` in ordine crescente (append), `session-journal.md` in ordine
decrescente (prepend). Nessuna entry riscritta o persa — solo riposizionate; a parità di
data/ora l'ordine relativo preesistente nel file è stato preservato (nessun segnale più fine
disponibile per distinguere l'ordine reale infra-giornata).

Trovata per strada una corruzione distinta e più seria in `log.md`: due commit consecutivi
(`fa51b46`, `b3917ab`, 2026-07-28) avevano scritto il titolo di un'entry reale dentro la riga
di template dell'header invece che come nuova entry — il secondo aveva sovrascritto in-place
il testo del primo, cancellandolo dal file vivo in violazione della regola append-only.
Testo del primo recuperato da git e ripristinato come entry propria, marcata come superata
dalla seconda (storia ricostruibile, mai cancellata).

Aggiunta ad entrambi i file una nota di convenzione esplicita in testa (non solo nell'header
prosa, ma come blocco `>` sempre visibile): `log.md` dichiara ora esplicitamente APPEND
crescente, `session-journal.md` dichiara ora esplicitamente PREPEND decrescente, ciascuno
con un rimando incrociato all'altro per evitare la confusione ricorrente. Non toccato
`.cursorrules` stesso (la sua doppia dicitura "Append-Only / Prepend-Only" per
session-journal.md resta ambigua nel testo, ma l'istruzione operativa è già inequivocabile
— "vanno aggiunte rigorosamente in cima"); modificarlo richiede conferma esplicita
dell'utente per la regola MUST ASK propria di quel file.

**Gap non affrontati in questa sessione** (segnalati, non risolti): `log.md` non ha entry tra
2026-07-21 e 2026-09-02 pur essendoci sei settimane di lavoro Lifelog2 documentato altrove;
diverse entry duplicate consecutive identiche (es. quattro `[2026-05-09] promote | Lifelog2 →
CT203`, cinque `[2026-06-13] promote | SHIFTER → CT204`) non deduplicate.

## [2026-09-02] fix | Correzione: la quota ngrok non era a rischio — errore di lettura nei log

L'entry precedente (stessa giornata) affermava un rischio reale di esaurimento quota ngrok
per la cadenza heartbeat a 30s. Verificato ora contro il contatore reale dell'agent ngrok
(`curl 127.0.0.1:4040/api/tunnels` su CT202): **1.256 richieste HTTP totali in 51 giorni di
uptime processo** (~740/mese) contro un limite di 20.000 — nessun rischio reale, né a 30s né
a 5 minuti di cadenza.

**Causa dell'errore**: avevo interpretato la firma `127.0.0.1` nei log di nginx come prova
che il traffico del telefono passasse dal tunnel ngrok. Scoperto ora che CT202 esegue
*anche* `cloudflared` (quick tunnel, attivo dal 15/07) verso lo stesso target
`http://localhost:80` — la firma `127.0.0.1` è ambigua fra i due tunnel, non prova univoca
di instradamento ngrok. Conteggio reale traffico telefono (`user-agent: okhttp`) in
`gateway_access.log`: 26.677 richieste via quel loopback ambiguo, 1.930 via LAN diretta.
Poiché l'agent ngrok ne rivendica solo 1.256 in tutto, le restanti ~25.400 sono quasi
certamente Cloudflare (nessuna quota di questo tipo), non ngrok.

**Cosa resta valido**: l'heartbeat a 5 minuti resta comunque la scelta giusta per
batteria/carico server. **Cosa cambia**: rimossa l'urgenza sul vincolo di quota ngrok per
Lifelog2 e il parallelo con l'incidente DIAS del 24/04 (quello confermato via commit reale,
meccanismo diverso — tab browser aperto su URL pubblico ngrok, non ambiguità fra tunnel).
Storia non cancellata, solo corretta — vedi blocchi datati in [[entities/containers/ct202-gateway]]
e [[entities/systems/stack-lifelog2]].

## [2026-09-02] dev | Blueprint app Android v2.3 — nuovo doc di riferimento + verifica contro il server

Ricevuto dall'agent Android Studio il blueprint tecnico v2.3 dell'app (architettura,
permessi, schemi JSON di ogni canale device→server, stato forensic sulla registrazione
chiamate). Creato `sviluppi/Lifelog2/docs/lifelog2-android-app-blueprint-v2.3.md` come
contratto di input SOT, referenziato da `README.md` e dal master blueprint (tabella
"Documenti di riferimento operativo" + §6.9 Android).

**Verificato contro il codice reale** (non trascritto a scatola chiusa): gli schemi
heartbeat/contacts/calls combaciano esattamente coi modelli Pydantic già implementati
oggi stesso (`devices.py::HeartbeatRequest`, `sync.py::ContactIn`/`CallIn`) — nessuna
discrepanza. Trovato un gap reale non bloccante: questi tre endpoint non erano ancora
documentati in `knowledge/api-contracts.md` — aggiunta sezione 1.6.

**Convergenza indipendente notata**: la conclusione forensic del blueprint sulla
registrazione chiamate (mute kernel-level, dump hardware MediaTek protetto da SELinux,
non incluso nei bug report) coincide con quanto verificato autonomamente lato
server/infra nella stessa giornata (silenzio digitale -91dBFS misurato, strade software
senza root chiuse per via documentale) — due indagini indipendenti convergenti, non
una che ripete l'altra.

Corretto un commento stantio in `devices.py` (cadenza heartbeat dichiarata "15-30s
proposta", reale 5 minuti). Pagine toccate: [[entities/systems/stack-lifelog2]].

## [2026-09-02] fix | Correzione: la registrazione chiamate NON è chiusa — letto il repo Android reale

L'entry precedente (stessa giornata) affermava una "convergenza indipendente" che
confermava la chiusura del percorso hardware-dump per la registrazione chiamate. Letto
ora il repo GitHub reale `S3ph1r/LifeLog` (privato, linkato da Roberto) invece di fidarsi
solo del riassunto ricevuto in chat — i file `.artifacts/*.artifact.md` dello stesso lotto
mostrano un'indagine **ancora attiva**, non conclusa: `handoff_device_specs.artifact.md`
riporta che due sorgenti audio (`VOICE_COMMUNICATION`, `MIC`) hanno prodotto "123KB di
dati binari non nulli" durante una chiamata reale — in tensione diretta con "maxAmplitude
ritorna 0" scritto nello stesso blueprint. "Non nullo" non è prova di audio reale (anche
il silenzio digitale codificato ha dimensione > 0): il codice reale calcola già un valore
di Peak Amplitude per ogni probe (che risolverebbe la domanda) ma non è riportato nel
documento letto. Trovata anche una richiesta di funzionalità non implementata — il server
che innesca da remoto un `adb bugreport` sul telefono per recuperare
`/data/vendor/audiohal/` — segnalata come decisione che spetta a Roberto, non
implementata.

**Cosa resta valido**: il percorso "soft" (API standard, MediaProjection, Shizuku) è
chiuso, verificato in modo solido e indipendente da entrambe le parti. **Cosa cambia**:
il percorso "hardware dump MediaTek" resta un'indagine aperta lato Android, non un esito
confermato — rimossa l'etichetta "chiuso" per questa parte specifica.

Trovate per strada altre 3 discrepanze reali tra il riassunto ricevuto e il repo
completo: specifiche audio (44.1kHz stereo 128kbps reali vs 16kHz mono 32kbps ancora
in `knowledge/api-contracts.md`, ora corretto), il segnale `context_data` (livelli
audio/luce/prossimità/movimento a 1Hz, già noto ma non presente nel riassunto), e una
divergenza di 15 minuti vs 1 minuto sulla persistenza GPS tra due documenti dello stesso
repo. Un link rotto nel README Android (puntava al backend V1 dismesso, non a
`Lifelog2`) segnalato ma non corretto (repo non nostro). Storia non cancellata, solo
corretta — vedi blocchi datati in `lifelog2-android-app-blueprint-v2.3.md` §6, §8.

## [2026-09-02] dev | AGENTS.md — canale di coordinamento diretto server↔app Android

Creato `sviluppi/Lifelog2/AGENTS.md` (root repo) su richiesta esplicita di Roberto: un
file letto da entrambi gli agent (Claude Code lato server, agente Android Studio lato
app) per allineamento tecnico cross-confine senza dover passare sempre da Roberto come
messaggero. Convenzione: entry datate `STATO | titolo` (`APERTO`/`RISPOSTO`/
`DECISIONE-UTENTE`), mai riscritte — stessa disciplina di storia ricostruibile di
`log.md`. Esplicitamente delimitato: allineamento tecnico sì, decisioni con impatto
privacy/prodotto no (restano di Roberto anche se emergono da una discussione lì).

Popolato con le 5 domande aperte di questa sessione (GPS background permission, Peak
Amplitude dei probe chiamata, persistenza GPS 15 vs 1 min, il "no" esplicito al
bugreport da remoto, link README da correggere). Referenziato da `README.md` e dal
master blueprint. Roberto istruirà l'agente Android a creare l'equivalente in
`S3ph1r/LifeLog`.

## [2026-09-08] lint | ARIA — correzione drift doc↔codice prima del redesign wrapper Qwen3-14B

Presa di coscienza del quadro generale (infra + progetti) prima di lavorare sul backend
JIT `qwen3-14b-q4km`. Trovati e corretti disallineamenti tra wiki e codice reale:

- **[[concepts/aria-redis-protocol]]** — schema coda corretto da `aria:q:{env}:{provider}:...`
  a `aria:q:{model_type}:{provider}:{model_id}:{client_id}` (verificato in
  `batch_optimizer.build_queue_key` + `orchestrator._run_loop`). Tabella Model IDs
  riscritta (elencava 5 modelli, uno cloud non più in uso; `qwen3.5-35b-moe-q3ks`
  marcato "operativo" ma è solo scaffolding). Aggiunta nota sulla chiave di callback
  parametrica (il client LLM locale di Lifelog2 usa `aria:result:llm:{job_id}`, non lo
  schema `aria:c:{client_id}:{job_id}`). Aggiunto puntatore a `model_logic_ids`
  hardcoded in `orchestrator.py`.
- **[[entities/systems/stack-aria]]** — `qwen3.5-35b-moe-q3ks` da "✅ Operativo" a
  "⚠️ Solo scaffolding" (pesi assenti su PC139, `FileNotFoundError` all'avvio —
  verificato dall'indagine `docs/qwen3-llm-wrapper-investigation-2026-09-08.md` §5).
  Riga consumatori Lifelog2: `qwen3-14b-q4km` non estrae più "MemoryAtom" (Stage D
  atom-based superato) ma alimenta Thread Builder/Enrichment D/E + Detective + Day Digest;
  Lifelog2 è l'**unico** consumatore del 14b locale.
- **[[index]]** — CT160 (NHI-CORE) da "running" a "stopped" (inventory reale).

Fonte primaria: `sviluppi/ARIA/docs/qwen3-llm-wrapper-investigation-2026-09-08.md`.
Non toccati (fuori scope, richiedono decisione utente): link orfani in `index.md` a
`concepts/aria-telemetry` e `concepts/aria-gemini-503-pattern` (pagine mai create — i
doc sorgente esistono in `sviluppi/ARIA/docs/`); CT200 running senza pagina wiki.

## [2026-09-08] dev | ARIA registrato nel workspace manager NH-Mini

Creato `sviluppi/ARIA/project_info.json` — ARIA non era elencato da `nh-switch.py`
(mancava il file richiesto da `workspace_manager.list_projects()`, che scansiona
`sviluppi/*/project_info.json`). Eseguito lo switch: `workspace/current_project →
sviluppi/ARIA`, `active_config.json` aggiornato (previous: SHIFTER, fermo da 2026-06-11).
Anche `dias` e `shifter-standalone` restano non registrati — non toccati.

## [2026-09-08] dev | ARIA — redesign wrapper LLM locale Qwen3-14B + deploy su PC139

Sessione lunga (indagine → design → verifica empirica → implementazione → deploy). Backend
`qwen3-14b-q4km`, unico consumatore Lifelog2. Doc: `sviluppi/ARIA/docs/qwen3-llm-wrapper-{investigation,redesign}-2026-09-08.md`,
`qwen3-14b-backend-spec-2026-09-09.md` (handoff per la parte Lifelog2).

**Problemi risolti** (indagine): `thinking=False` non ha mai avuto effetto dal 2026-05 (guardia
`/no_think` sempre falsa — Qwen3 ha sempre ragionato); whitelist a 8 campi in `run()` scartava
in silenzio ogni altro parametro; sampling fissi ai valori "thinking" anche in non-thinking.

**Redesign**: passthrough parametri completo (contratto `llm_contract` nel manifest, 19
`request_params` con schema); profili `thinking`/`non_thinking` completi con override per-campo;
`contract()`/`probe()` self-describing; `finish_reason` propagato; greedy guard.

**Verifica dal vivo su PC139** (build b10819): 3 leve thinking funzionanti
(`chat_template_kwargs.enable_thinking:false`, `reasoning_budget_tokens:0`, `/no_think`);
`reasoning_budget_tokens:N` è un cap reale sul pensiero; `reasoning_effort` NON supportato dal
template Qwen3-14B. Perf sana (42 tok/s gen, 1646 prompt su 8K), CUDA 13.3 ok.

**Deploy**: binario `b9119`→`b10819`/`cuda-13.3` in `tools\llama\` (b9119 in backup); ctx
16384→32768 + KV `q8_0` + `flash-attn` + `parallel 1` (~10.8 GB VRAM, ~2.4 GB liberi col
desktop attivo). **Nessun riavvio orchestratore**: `_build_cmd` ricarica il manifest e
`_process_lifelog_llm_task` ricarica il modulo backend ad ogni task. Commit ARIA `baa917e` +
`4bc78df` + `b0fb208`. 16 test offline passati, validato end-to-end via launcher.

**Drift wiki corretto** (vedi entry `lint` sopra): `aria-redis-protocol.md`, `stack-aria.md`,
`index.md`. `core-modules.mdc` aggiornato (nota su restart_aria non più necessario per questo backend).

**Resta**: `sviluppi/Lifelog2/src/backend/lifelog2/core/llm.py` (prossima sessione — handoff doc);
spot-check qualità KV q8 su dump Stage D reale.

## [2026-09-11] ingest | Lifelog2 — thinking Qwen3, reprocess generale, audit, riordino documentazione

**Contesto**: seguito diretto del redesign wrapper ARIA dell'8-9/09 (entry sopra) —
`thinking=True` cablato su tutti i worker Lifelog2 che chiamano Qwen3 (Stage D, Stage E,
identity_detective, thread_consolidation, day_digest, profile_validator), con budget
condiviso (`core/llm.py`) che divide correttamente prompt+tabella+riserva
reasoning+risposta invece di un `max_tokens` fisso.

**Stage D** tornato a v34b + reasoning generoso: 6/7 puliti sui 7 casi storici (contro
3/7 prima). **Reprocess generale da Stage C1** (11659 turni, 671 thread) — 4 bug trovati
e risolti durante il reprocess, nessuna scrittura dati sbagliata. **Audit dei 17 casi
storici noti**: i due problemi più vecchi (coda tabella persa in Stage D, attribuzione
scambiata in Stage E) confermati **risolti** sui dati reali. Trovato e corretto un bug
indipendente (`media_type` sempre NULL dal 08-21, cancello di volume rotto).

**Valutazione di avanzamento** (nuova, richiesta esplicita di Roberto): la formazione del
ricordo (A→G) è la metà matura del progetto, solo 4 problemi aperti. I worker secondari
sono ineguali — alcuni dormienti da settimane, i digest week/month/year narrativi non
esistono affatto. Conteggio onesto: 9-10 voci tra problemi/da completare/da costruire.

**Riordino documentazione**: `docs/README.md` (fermo 10gg) aggiornato con 32 doc mai
indicizzati; 1 documento superato archiviato per davvero (`docs/archive/`); le 4
`knowledge/*.md` di progetto (ferme 5-7 settimane) rinfrescate; nuovo
`docs/lifelog2-session-log.md` (log per sessione di sviluppo, ricorrente).

Pagine toccate: [[entities/systems/stack-lifelog2]], nuova
[[sources/lifelog2-thinking-reprocess-audit-2026-09-11]]. Dettaglio completo:
`sviluppi/Lifelog2/docs/lifelog2-session-log.md`, `lifelog2-post-audit-todo-2026-09-11.md`,
`lifelog2-status-roadmap.md` (STATO 2026-09-11).
