# Wiki Log — NH-Mini Second Brain

Log append-only di tutte le operazioni sul wiki.  
Formato entry: `## [YYYY-MM-DD] tipo | titolo`  
Tip: `grep "^## \[" log.md | tail -10` mostra le ultime 10 operazioni.

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

## [2026-05-23] dev | Lifelog2 Stage F Deterministic Boundary Detection & Z7 Profile Builder Fix

- **Alembic Migration**: Creata ed eseguita la migrazione `0013_memory_atom_mode_timeline.py` per aggiungere le colonne `media_fingerprint` (`TEXT`) e `mode_timeline` (`JSONB`) su `memory_atoms`.
- **Modelli SQLAlchemy**: Aggiornato `MemoryAtom` in `models/memory.py`.
- **Prompt Stage D (v11)**: Creato `prompts/stage_d_enrich_v11.txt` per estrarre `media_fingerprint` e `conversation_type`, e impostato come default in `prompts/config.json`.
- **Stage D Integration**: Aggiornato `stage_d_enrichment.py` per estrarre e persistere i nuovi campi in `entities_json` e `media_fingerprint`.
- **Stage E Timeline**: Implementato il calcolo deterministico `_build_mode_timeline(...)` in `stage_e_embedding.py` leggendo i turni vocali e identificando contatti noti dal voiceprint.
- **Stage F Grouping State Machine**: Riscritto completamente il boundary detection in `stage_f_grouping.py` tramite Pass 1b deterministico con merge di silenzi < 5min, significatività del personal >= 60s, breaks a mezzanotte, soft break LLM ultraleggero solo in assenza di fingerprint identici, e calcolo automatico degli indici di split intra-atomo tramite turn offset, riducendo le chiamate LLM di oltre l'80% (da ~56 a ~8 al giorno).
- **Z7 Profile Builder Bugfix**: Corretto il bug SQL di casting di SQLAlchemy (`:src::jsonb` -> `CAST(:src AS jsonb)`) in `worker_profile_builder.py`.
- **Pagine toccate**: [[log.md]], [[entities/systems/stack-lifelog2|stack-lifelog2.md]]

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

## [2026-05-21] dev | Lifelog2 audio playback — 5 bug chain, dynaudnorm, MP3 streaming

- **Endpoint `GET /api/dashboard/segment/{id}/audio-clip`**: stream MP3 per speaker turn, TTFB ~60ms via `asyncio.create_subprocess_exec` + `dynaudnorm=g=15:f=500:r=0.9` (far-field normalization).
- **5 root cause chain risolti**: (1) far-field silenzioso −33dBFS → dynaudnorm; (2) browser timeout su clip lunghi → streaming subprocess; (3) Svelte 5 `$state` Proxy su HTMLAudioElement → TypeError silenzioso; (4) WebM/Opus OpusHead EBML incompleto in pipe → switch a MP3; (5) Chrome buffer interno stantio → `new Audio()` + cache-buster `?_t=`.
- **Gotcha documentato**: mai wrappare HTMLMediaElement in `$state` Svelte 5.
- **knowledge aggiornato**: `architecture.md`, `api-contracts.md`, `development-log.md` (Lifelog2).
- **history_manager**: entry FEATURE aggiunta (commit `68add51`).

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

## [2026-05-14] dev | Lifelog2: WhisperX large-v3 integrato in ARIA + E2E A→E validata + /doc sync

- WhisperX large-v3 sostituisce Qwen3-ASR-1.7B come backend STT primario di Lifelog2 (ARIA porta 8091, env `lifelog-whisperx`).
- Fix orchestratore ARIA: `model_logic_ids` aggiornato, `threading.RLock`, handler `LifelogWhisperXBackend` deployato.
- Pipeline A→E misurata: **~91s warm** su 299s audio (3.3× realtime). Bottleneck: GPU switch 35s (71% Stage D).
- Headroom Level 2: ~209s liberi per segmento → ~17 chiamate LLM warm nel budget. Worker L2 (Detective, F, G): solo blueprint, zero codice.
- /doc: `aria-state-of-gaps.md` (A0-4 resolved), `ARIA-blueprint.md` (§4 backends STT+LLM), `Lifelog2/knowledge/development-log.md`, `architecture.md`, `api-contracts.md` aggiornati.

---

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
## [2026-05-11] dev | Lifelog2: Liquid Brain Architecture & Global Registry
- **Architettura**: Definito paradigma Swap-In/Out per l'archivio utente (Guscio vs Cervello).
- **Global Registry**: Progettazione `registry.db` su LXC 203 per Auth (JWT) e provisioning segreti (Salt).
- **Ingest**: Introdotto modello Ingest Parallelo (24/7) e Analisi Seriale (On-Demand).
- **App Android**: Audit completo e creazione documento di handoff per l'upgrade a v2.0 (Metadata JSON + Auth).
- **Legacy Sync**: Verificato parsing GPS/Timestamp dai nomi file .m4a per retrocompatibilità.

## [2026-05-13] dev | Lifelog2 Stage D + ARIA qwen3-14b-q4km — E2E completo

- **Stage D Blueprint v1**: cristallizzato `Lifelog2/docs/lifelog-stage-d-blueprint-v1.md` — pipeline per segmento, timing (21s warm), modalità streaming/batch, worker detective, retroactive indexer.
- **Prompt versioning**: creati `prompts/config.json`, `prompts/stage_d_enrich_v1.txt`, `prompts/stage_d_detective_v1.txt`. Nessun prompt hardcoded in codice.
- **AriaLLMClient aggiornato**: modello `qwen3-14b-q4km`, queue `aria:q:llm:local:qwen3-14b-q4km:lifelog`, messages format con system prompt, thinking=False.
- **Stage D worker**: `stage_d_enrichment.py` riscritto — carica prompt da file, usa MemoryAtom schema v1 (event_type, speaker_turns_annotated, temporal_refs, confidence in entities_json).
- **ARIA backend qwen3-14b**: `launcher.py`, `lifelog_llm.py` (health /health, reasoning_content, /no_think), `backends_manifest.json` (porta 8090), `install_lifelog_llm.ps1`.
- **E2E test superato**: segmento 3599a424 (AI + mental health, Italian, 5 min) — MemoryAtom di alta qualità in 21s, 447 token, confidence 0.85.
- **Wiki aggiornata**: [[stack-lifelog2]] (M4 ✅, pipeline, identity resolution 3 livelli), [[stack-aria]] (qwen3-14b-q4km aggiunto).

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

## [2026-05-13] dev | Lifelog2 Fast Pipeline formalizzata — Stage D greedy + Stage E implementato

- **Architettura consolidata**: Fast Pipeline = A→B→C→D→E per ogni segmento. Worker greedy (count=100). Level 2 (Detective, F, G, Retroactive) completamente asincroni.
- **Stage D refactor**: count=1→100 (greedy batch), passa `normalized_audio_key` a Stage E, fix typo pipeline_status.
- **Stage E nuovo**: consumer `lifelog:stream:embed`, embedding mxbai-embed-large via CT107, WAV delete da MinIO, `pipeline_status="consolidated"`.
- **config.py**: aggiunti `ollama_url` e `ollama_embed_model` (override via env).
- **Confine pipeline**: dopo Stage E il ricordo è autosufficiente — testo, voiceprint 256d, MemoryAtom, embedding 1024d. I worker Level 2 leggono questi dati senza bisogno di riaprire audio.
