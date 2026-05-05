# Wiki Log — NH-Mini Second Brain

Log append-only di tutte le operazioni sul wiki.  
Formato entry: `## [YYYY-MM-DD] tipo | titolo`  
Tip: `grep "^## \[" log.md | tail -10` mostra le ultime 10 operazioni.

---

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
