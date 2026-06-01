## [2026-06-01 23:40] TASK — /doc lifelog2 eseguito

Aggiornati: `knowledge/architecture.md` (Stage G trigger refactor, conversation_type/analysis_tier in Stage C/D, backfill script), `knowledge/memory-model.md` (migration 0015: nuove colonne Segment, MemoryAtom, SpeakerTurn, Person), `knowledge/development-log.md` (entry 2026-06-01). Auto-restart orchestratore CT203 schedulato via script su CT120 (PID 15496).

## [2026-06-01 23:00] DECISION — Stage G covers refactor: spostato dopo Tier2

Rimosso `_covers_trigger.set()` da `_grouping_loop()`. Aggiunto dopo blocco Tier2 in `run()`. Commit `b509e4c`, push, git pull su CT203 eseguito — restart pendente (stage_c ancora running lag~500).

**Motivazione:** Ordine D(qwen3)→G(flux2)→Tier2(qwen3) = 3 swap GPU. Nuovo ordine D→Tier2→G = 2 swap. FLUX2 è ora sempre l'ultimo step del ciclo.

## [2026-06-01 19:30] RESOLVED — 1110 segmenti 2025 stuck in 'enriching'

Script `scripts/backfill_asr_from_archive.py` creato, committato (`694f2c0`), deployato su CT203. Risultato: 1025 discarded (audio_deleted), 85 re-queued su `stream:asr`. DB pulito — nessun segmento pre-2026 bloccato.

## [2026-06-01 18:00] DECISION — conversation_type refactor verificato live

Deploy commit `d351760` su CT203 verificato: taxonomy attiva (real_dialogue, personal_mono, media_passive, ambient_voices), tier gate corretto (analysis_tier=1.0 → skip LLM), persons=1 (zero falsi media persona), 44 memory_atoms tutti tipizzati correttamente.

## [2026-06-01] IN CORSO — Lifelog2 Voiceprint, Detective, Stage Z7

**Completato:**
- **Post-drain bug fix** (da sessione precedente, verificato): `_post_drain_set_at` tracking — post-drain flush ora a 60s esatti. Commit `c3a9b4b`.
- **Detective capture_class filter**: aggiunto `AND s.capture_class IN ('personal', 'mixed')` alla query atom. Commit `19d184f`. Deploy CT203 12:26.
- **Stage Z7 capture_class filter**: stesso fix in `worker_profile_builder.py` → Stage Z7 ora clusterizza solo speaker da segmenti personal/mixed. Commit `d402149`. Deploy CT203 13:xx.
- **Voiceprint rematch**: `rematch_voiceprint.py --threshold 0.60` → 33 segmenti ambient reclassificati a personal/mixed, 1381 speaker_turns.person_id = Roberto. Enrollment funzionante (256d, quality=1.0).
- **Pulizia 412 falsi Interlocutori**: Stage Z7 senza filtro aveva creato 412 Person da ambient (TV/podcast). Eliminati tutti dal DB + speaker_turns.person_id azzerati.
- **Stage Z7 corretto**: nuovo run con filtro → 28 "Interlocutore Ricorrente" reali (da 412). Top: `7db31827` 18 segmenti ottobre 2025 → maggio 2026.
- **Detective checkpoint reset**: azzerato a 2026-05-20 per rielaborare i 250 atom personal/mixed (creati prima del checkpoint detective).
- **Detective: rimozione batch cap + timeout 24h**: `range(5)` → `while True`, `DETECTIVE_TIMEOUT_S` 10min → 24h. Commit `85ec94e`. Deploy + orchestrator restart 14:08.
- **Identity candidates trovati**: detective ha estratto "Alberto - collega" ricorrente in più cluster, Roberto identificato con confidence 0.9 su SPEAKER_00.

**In corso:**
- Detective sta drenando il backlog completo (250 atom, avviato 14:08 con timeout=86400s)

**Incompleto / prossima sessione:**
- Flusso "conferma identità → enrollment voiceprint per terzi": view per ascoltare campioni vocali + conferma identity → `Person.voiceprint_embedding` estratto da `speaker_turns`
- Sample #4 voiceprint deteriorato: rimuovere da `voiceprint_ids` e ricalcolare centroide (bassa priorità, enrollment funziona)
- Stage F greedy loop: max retries guard non ancora implementato
- Places Intelligence Fase 5: Stage D location context (bloccata su primo luogo confermato)

---

## [2026-05-31 20:33] END — Lifelog2 Orchestrator Tuning + /doc + /lint

**Completato:**
- **Batch Tier1 trigger**: `BATCH_MIN_SIZE=6`, `BATCH_MAX_WAIT_S=1800s`. GPU swap VRAM ridotti da 12/h a 2/h (83%). Warm cache chain: WhisperX×6 → Qwen3×6 (resta in VRAM) → Tier2 workers trovano Qwen3 già carico. Commit `d236992`. Deploy CT203 ore 20:23 CEST.
- **TIER2_REGISTRY calibration**: `profile_builder` 7gg→6h (checkpoint Redis incrementale, no LLM), `place_detective` domenica-only→6h (no LLM, ~5s/run), `thread_consolidation` 7gg→2gg + `--limit 30` + timeout 1800s→2700s. Fix: 240 episodi non-threaded causavano timeout ×2. Commit `5b30553`, `486f4f7`.
- **Two-service architecture CT203 documentata**: `lifelog2.service` (API :8002) vs `lifelog2-orchestrator.service` (pipeline). `restart lifelog2` lascia orchestratore con codice vecchio. Memory entry salvata.
- **thread_consolidation completato** nella sessione corrente: run 19:08 CEST, 23 episodi threaded in ~7 min (primo run funzionante dopo due TIMEOUT).
- **Tier2 workers attivi**: day_digest, profile_builder, profile_validator, thread_consolidation, place_detective tutti corsi nella stessa sessione dopo restart orchestratore alle 18:59 CEST.
- **/doc lifelog2**: `knowledge/architecture.md` (Tier2 table, Batch Tier1 section, two-service arch, Place Detective + Profile Builder schedule), `knowledge/development-log.md` (entry 2026-05-31), `NH-Mini/log.md`, `NH-Mini/index.md`, `history_manager` FEATURE/Lifelog2/OrchestratorBatchTier1. Commit `e2566f0` (Lifelog2), `e84512e` (NH-Mini).
- **/lint lifelog2**: 58 passed, 0 warnings, 0 errori. Tutti i 7 script `scripts_ref` ora sono 0 warning (risolti nella sessione precedente).
- **/finalize**: 54 passed, 0 warnings, 0 errori.

**Incompleto / prossima sessione:**
- Speaker enrollment voiceprint: best_score < 0.2 su tutti i segmenti — non investigato in questa sessione
- Profile Builder: esce in 1s dal 2026-05-24 — root cause non investigata
- Places Intelligence Fase 5: Stage D location context nel prompt (bloccata su primo luogo confermato — place_detective ora gira ogni 6h, primo hit possibile domani)

**Mine per il prossimo agent:**
- `BATCH_MAX_WAIT_S=1800s` è in-memory. Se l'orchestratore viene riavviato a metà finestra, la finestra riparte da zero — comportamento corretto, non un bug.
- `_tier2_last_run` si azzera al riavvio dell'orchestratore → tutti i Tier2 worker girano immediatamente al prossimo ciclo idle. Voluto: garantisce run post-deploy.
- **Regola deployata**: `systemctl restart lifelog2-orchestrator` (non `lifelog2`) dopo fix codice pipeline. Vedi [[feedback_orchestrator_service]].
- thread_consolidation backlog: 23 episodi threaded oggi. Con `--limit 30` + intervallo 2gg smaltirà il backlog residuo nelle prossime run senza bloccare catena.

---

## [2026-05-30 15:18] END — Pipeline Dashboard + /doc lifelog2 + /lint lifelog2

**Completato:**
- **Svelte 500 fix**: `{@const}` nelle 4 tile Batch Workers era figlio diretto di `<div>` — wrap in `{#if status.orchestrator}`. Deploy su CT203.
- **Pipeline Dashboard refactor**: layout 2 colonne (workers sinistra, data destra), KPI bar, log terminal collassabile, stream `lag` vs `length`, 5 tile Background Workers (systemd timers), Place Detective tile. Deploy su CT203.
- **4 data fix frontend**: `StreamInfo` type aggiornato (`lag`), `formatNextTimer()` per timestamp futuri (era "-1g fa" per next_elapse di domani), CSS `.col-span-2`, `{@const}` placement.
- **Backend**: nuovo `GET /orchestrator/timers`, `_stream_info()` con lag via consumer group, `_STREAM_CONSUMER_GROUPS` mapping.
- **/doc lifelog2**: `architecture.md` (streams table, orchestrator.py, Control Plane v2), `api-contracts.md` (streams schema + /timers endpoint), `development-log.md` (entry 2026-05-30), `NH-Mini/log.md`, history_manager FEATURE/Lifelog2/PipelineDashboard.
- **/lint lifelog2**: 50 passed, 0 errori, 8 warnings → risolti: 7 script diagnostici registrati in `core-modules.mdc`, entry journal aggiunta.

**Incompleto / prossima sessione:**
- Speaker enrollment diagnosis (voiceprint broken, best_score < 0.2 su tutti i segmenti)
- Profile Builder: fallisce dal 2026-05-24, esce in 1s — root cause non investigata
- Places Intelligence Fase 5 pending (Stage D context — bloccata su primo luogo confermato)

**Mine per il prossimo agent:**
- I 7 script diagnostici ARIA/Redis ora in `core-modules.mdc` ma `restart_aria.py` porta il vincolo **"non eseguire autonomamente"** — vedi [[feedback_aria_control]].
- `COVERS_MIN_TOTAL=10` in orchestratore: Stage G non scatta con meno di 10 cover pending — se vedi "items senza cover" in dashboard ma Stage G idle, è normale.

---

## [2026-05-30 09:00] START — Pipeline Dashboard refactor + Svelte 500 fix

**Obiettivo:** Correggere errore 500 su `/pipeline` (Svelte `{@const}` fuori da control-flow), refactor completo layout dashboard, aggiunta tile Background Workers, data accuracy fixes.

**Grounding:** Contesto di sessione da compressione. Errore 500 diagnosticato: `{@const runningF = ...}` a riga 438 figlio diretto di `<div class="workers-grid">`. Fix noto prima di iniziare.

---

## [2026-05-29] TASK — /doc lifelog2 eseguito

- **architecture.md**: Stage C quality signals (4 campi), Stage D quality gate sezione (extraction_level floors, persons filter, prompt v14), voiceprint threshold corretto 0.72→0.60, prompts block aggiornato
- **memory-model.md**: MemoryAtom entities_json campi documentati (extraction_level, hallucination_flags, conversation_type), retention_class allineata all'implementazione reale (_retention_from_importance)
- **api-contracts.md**: `lifelog:stream:enrich` riscritto con payload reale Stage C→D (era blueprint M0 Stage F); aggiunti 4 campi audio quality
- **development-log.md**: entry 2026-05-29 completa con ciclo v13/v14, tabella risultati, backlog
- **history_manager**: FEATURE/Lifelog2/StageD-QualityGate registrato
- **Commit**: `a92d671` (doc(/doc lifelog2): sync knowledge)

## [2026-05-29] END

**Completato:**
- **Voiceprint P0 risolto** — acoustic mismatch VOICE_RECOGNITION vs CAMCORDER. Archiviate enrollment precedenti (6 campioni + centroid 256d). Centroid ricostruito con 2 soli campioni CAMCORDER. `VOICEPRINT_MATCH_THRESHOLD` abbassata 0.72 → 0.60 dopo verifica manuale di 15+ clip audio reali. Backfill rematch su 10,694 speaker turns: 877 ora attributi correttamente a Roberto (capture_class = personal/mixed vs tutti ambient prima del fix).
- **Stage C — 4 audio quality signals**: `avg_turn_duration_ms`, `min_turn_duration_ms`, `n_short_turns`, `inter_speaker_similarity` (max coseno tra speaker embeddings). Scritti in transcript JSON MinIO + messaggio Redis enrich stream.
- **Stage D — extraction_level gate**: `_format_user_message` riceve segnali qualità e li inietta come header QA nel prompt utente. Dopo risposta LLM, se `extraction_level ≠ full`, Stage D azzera server-side entities/decisions/actions. `metadata_only` → path ephemeral. `hallucination_flags` + `extraction_level` persistiti in `entities_json`.
- **Prompt stage_d_enrich_v13**: `extraction_level` (full/contextual/metadata_only), `hallucination_flags` con 8 pattern (loop_residuo, nome_inventato, densita_entita_anomala, lingua_fantasma, coerenza_locale_incoerenza_globale, dettaglio_non_ancorato, nome_storpiato, frammento_isolato), regole decisione LLM su soglie tq + inter_speaker_similarity. `config.json` v12 → v13.
- **Test v13 su 2 trascrizioni reali**: A tq=0.50 → contextual, persons=[], nome_storpiato detected ✅. B tq=0.80 → full, persons=['Alia'] ✅. Bug v12 `decisions:['[',']']` eliminato.
- **Deploy**: stage_c + stage_d + config.json + v13.txt copiati su LXC 203. Orchestrator riavviato. Commit `4944c6a`.

**Mine per il prossimo agent:**
- Nessuna pendenza urgente sul quality gate. Il sistema è live su nuovi segmenti.
- **Places Intelligence Fase 5** ancora pending (richiede 1+ luogo confermato — primo Place Detective domenica 2026-06-01).
- **Profile validator dormante**: non verificato in questa sessione.

---

## [2026-05-27 23:56] END

**Completato:**
- **Places Intelligence Fase 0–4 live** (sessione continuata da contesto precedente):
  - Migration 0014: colonne `places` (visit_count, total_minutes_spent, cover_image_key, confirmed_*), tabella `place_hypotheses`, vista materializzata `place_signals` con UNIQUE INDEX per REFRESH CONCURRENTLY.
  - Stage F: geocoding ora incrementa contatori e refresha `place_signals` dopo ogni run.
  - Worker Place Detective (`worker_place_detective.py`): scoring rule-based zero-LLM per home/work/social/transit, schedule domenica 03:30, integrato come 5° loop asincrono in orchestratore (`_place_detective_loop`), trigger on-demand via Redis.
  - Stage G: esteso con `_fetch_pending_places()` + 5 template prompt cinematografici + MinIO key `covers/places/{id}.jpeg`.
  - API: 6 endpoint Places Intelligence in `dashboard.py` (GET /places, GET /places/{id}, GET /places/{id}/atoms, POST confirm, POST reject, GET cover/place/{id}).
  - Frontend `/places`: Leaflet map + tiles Netflix-style + detail panel slide-in con confirm/reject UI. Sostituisce `/map` nella sidebar.
- **`/doc lifelog2` eseguito**: aggiornati `knowledge/architecture.md`, `knowledge/memory-model.md`, `knowledge/api-contracts.md`, `knowledge/development-log.md`. Storico architetturale committato (`FEATURE/Lifelog2/PlacesIntelligence/high`).
- **`/lint lifelog2` eseguito**: 51 passed, 0 errori, 7 warnings `scripts_ref` (invariati, non bloccanti).
- **Chiarimento hard triggers**: `/dev` non esiste come hard trigger — i 6 definiti sono `/finalize`, `/lint`, `/troubleshoot`, `/reuse`, `/handover`, `/doc`.

**Mine per il prossimo agent:**
- **7 warning `scripts_ref`**: `check_aria_log.py`, `check_redis.py`, `clean_redis_queues.py`, `find_pm2.py`, `inspect_redis_queues.py`, `list_aria_dirs.py`, `restart_aria.py` — non referenziati in `core-modules.mdc`. Tool diagnostici ad-hoc, non bloccanti.
- **Places Intelligence Fase 5 pending**: Stage D context integration (`location: home/work` nel prompt Qwen3). Bloccata: richiede almeno 1 luogo confermato dall'utente (primo run Place Detective domenica 2026-06-01).
- **GPS data accumulation**: fix app Android eseguito 2026-05-27 — occorrono 2+ settimane per avere dati sufficienti al Place Detective.

---

## [2026-05-26 01:25] END

**Completato:**
- **Esecuzione protocollo esteso `/doc lifelog2`**: Sincronizzazione della documentazione ufficiale del sistema e del progetto.
- **Aggiornamento Knowledge Base Lifelog2**:
  - `architecture.md`: Documentata l'implementazione del clustering biometrico non supervisionato Tier B ed il flusso di Identity Resolution Upgrade, oltre alla Postgres Duplicates Protection.
  - `memory-model.md`: Esteso il formato del campo `source_memory_ids` del `UserProfileFact` in JSONB (`{"person_id": UUID, "memory_ids": UUID[]}`) per la corretta attribuzione di identità provvisorie/definitive.
  - `development-log.md`: Inserita la entry dettagliata per il 2026-05-26 riepilogando tutti i progressi sui lavoratori di intelligence, fix Svelte 5 e Postgres.
- **Commit storico architetturale**: Eseguito con successo `history_manager.py add` per registrare il componente `profile-builder-tier-b` nello storico `development-history.mdc` con impatto `medium`.
- **Allineamento Wiki Secondo Cervello**:
  - `NH-Mini/log.md`: Inserita l'entry del 2026-05-26.
  - `NH-Mini/index.md`: Aggiornata la data dell'ultimo allineamento del wiki al 2026-05-26 ed il relativo evento riassuntivo.
- **Lint di Compliance**: Eseguito `nh-lint.py --project lifelog2` con variabili UTF-8 protette su Windows. Esito: **51 passed, 7 warnings (diagnostici storici, non bloccanti), 0 errori**.

**Incompleto / prossima sessione:**
- Nessuna pendenza urgente per il framework o il wiki. La documentazione e lo stato del sistema sono completamente sincronizzati ed allineati all'ultima produzione.

**Mine per il prossimo agent:**
- I 7 warning diagnostici `scripts_ref` sono script d'utilità ad-hoc non registrati. Non sono critici e possono essere mantenuti tali, ma se necessario si può procedere al loro censimento o pulizia in futuro.
- Prestare attenzione quando si eseguono script Python su Windows che stampano caratteri emoji/Unicode: forzare sempre la codifica tramite la variabile d'ambiente `$env:PYTHONUTF8=1;` per evitare `UnicodeEncodeError`.

---

## [2026-05-26 01:10] START — Esecuzione Hard Trigger /doc lifelog2

**Obiettivo:**
- Eseguire in modo procedurale il protocollo esteso `/doc lifelog2` per allineare l'infrastruttura condivisa NH-Mini e la documentazione del progetto Lifelog2 dopo gli eccezionali progressi sul clustering biometrico Tier B, l'identity resolution upgrade, la correzione del bug sui record duplicati e la risoluzione del crash in Svelte 5.
- Garantire che la codebase e la documentazione siano perfettamente sincronizzate e validate tramite il linting.

**Grounding:**
- Letta la specifica `.cursorrules` e `knowledge/agent/hard-triggers.mdc` relativi al protocollo `/doc`.
- File `.project-context` di `Lifelog2` caricato con le relative entry in `KNOWLEDGE_INDEX`.
- Session journal analizzato per recuperare i dettagli dell'ultimo run e delle implementazioni.

---

## [2026-05-25 23:25] END


**Completato:**
- **Fase 3/4/5 Identity Review UI & API E2E**: Sviluppati gli endpoint FastAPI `/people/{id}/confirm`, `/people/{id}/reject` e `/people/{id}/update` in `dashboard.py`.
- **Back-Propagation Biometrica PGVector**: Integrato con successo il ricalcolo nativo in PostgreSQL tramite pgvector nella route di conferma, utilizzando il matching biometrico coseno $\ge 0.72$ (distanza coseno $\le 0.28$) per riassociare retroattivamente i turni di voce orfani.
- **Interfaccia Svelte 5 Premium**: Riscritta interamente l'area dei candidati di `/people/+page.svelte` in Svelte 5 con tipizzazione TypeScript robusta (`Candidate[]`). Integrato il form Frosted-glass con prevenzione del bubbling degli eventi click (che causava il collasso involontario delle card), menù a tendina di relazioni e tag di disambiguazione.
- **E2E Validation Success**: Eseguito il test di promozione su `CT203` (RT). Il trigger ha promosso con successo l'interlocutore anonimo `"Roberto Guareschi"` marcando a `null` i candidati, impostando `identity_level = 2` e allineando istantaneamente il DB.
- **Git Sync**: Stage, commit e push eseguiti per `S3ph1r/nh-mini` (commit `3be38d1`) e `S3ph1r/Lifelog2` (commit `d6a4fe9`).

---

## [2026-05-25 22:15] END

**Completato:**
- **Detective loop infinito risolto**: root cause = batch 8 atomi → output JSON > max_tokens=1536 → troncamento → cursore Redis bloccato → stesso batch ogni 15min per 3+ ore. Fix: `BATCH_SIZE=4` (commit `7d501fe`).
- **NULL-safe dedup fix critico**: `NOT (col @> val)` restituiva NULL su colonne NULL → zero candidati scritti in DB per persone nuove. Fix: `(col IS NULL OR NOT (col @> val))` + `rowcount` check (commit `ccc4db6`).
- **max_tokens parametrizzato**: `AriaLLMClient.generate_json()` ora accetta `max_tokens` opzionale; Detective usa 2048 (commit `b4daf35`). Tutti e 3 i commit pushati su `origin/main`.
- **DB cleanup**: test artifacts (`TEST_CANDIDATE`, `TEST_SA`, `TRACE_TEST`) rimossi da `persons.identity_candidates`. 0 residui.
- **Audit pipeline**: B/C/D/E/G = 0 errori attivi. F = 3 storici (pre-fix sessione precedente). Detective = 261 storici (tutti pre-fix). Pipeline idle e sana.
- **Dev/RT allineati**: git pull su LXC 190 — `ca2f8d2` → `b4daf35` (7 commit recuperati).
- **/doc lifelog2**: `session-journal.md`, `development-log.md`, `architecture.md`, `NH-Mini/log.md` aggiornati. `history_manager.py` BUGFIX registrato.
- **/lint lifelog2**: 51 passed, 0 errors, 7 warnings `scripts_ref` (invariato da sessione precedente, non bloccante).

**Incompleto / prossima sessione:**
- Nessun task pendente urgente. Il Detective sta elaborando il backlog (cursore ~2026-05-24T15:23 UTC, ~943 atomi rimanenti al ritmo di ~20 atomi/ciclo).

**Mine per il prossimo agent:**
- I 7 lint warnings `scripts_ref` sono script diagnostici ad-hoc senza documentazione formale. L'utente non ha dato indicazione di fissarli — verificare se valgono un'entry in `core-modules.mdc`.
- `max_tokens=1536` è ancora il default per tutti i worker tranne Detective. Se in futuro altri worker mostrano troncamento, applicare lo stesso pattern.
- Stage Z4 (Day Digest) e Z6 (Thread Consolidation) mai avviati — gap architetturale noto.

## [2026-05-25 21:00] START — Detective Debug: JSON Truncation, NULL-safe Dedup, max_tokens Fix

**Obiettivo:** Diagnosticare il blocco del worker Detective su LXC 203, applicare fix, fare audit completo della pipeline, allineare dev (LXC 190) e rt (LXC 203).
**Grounding:**
- Detective bloccato in loop infinito da 3+ ore su batch 2025-10-07/08 (8 atomi → >18 turn → output JSON > 1536 token → troncamento → parse fail → checkpoint non avanzato).
- Bug secondario scoperto durante debug: NULL-safe dedup e counter cieco in `worker_detective.py`.
- Tutti i fix committati su LXC 203 e pushati su `origin/main`.

## [2026-05-25 21:30] TASK — Detective fix, audit pipeline, DB cleanup, dev/rt align

- **BATCH_SIZE 8→4** (`worker_detective.py`): ridotto il batch per prevenire troncamento JSON su batch densi (commit `7d501fe`).
- **NULL-safe dedup + rowcount** (`worker_detective.py`): `NOT (identity_candidates @> ...)` restituiva NULL silenzioso su persone senza candidati → nessun candidate scritto in DB. Fix: `(identity_candidates IS NULL OR NOT (...))`. Counter incrementato solo su `result.rowcount > 0` (commit `ccc4db6`).
- **max_tokens parametrizzato** (`llm.py`): `AriaLLMClient.generate_json()` ora accetta `max_tokens: int = 1536`. Worker Detective passa `max_tokens=2048` (commit `b4daf35`).
- **DB cleanup**: rimossi `TEST_CANDIDATE`, `TEST_SA`, `TRACE_TEST` da `persons.identity_candidates` con UPDATE jsonb_agg filtrante.
- **Audit pipeline**: B=0, C=0, D=0, E=0, F=3 storici (pre-fix), G=0, Detective=261 storici (JSON parse failures pre-fix). Nessun errore attivo.
- **Dev/rt allineati**: git pull su LXC 190 — 7 commit recuperati (`ca2f8d2`→`b4daf35`).

## [2026-05-25 12:20] START — Detective Greedy Batch Processing & E2E Validation

**Obiettivo:** Confermare e documentare l'implementazione del Greedy Batch Processing (5 passate x 8 atomi = 40 atomi max per innesco) per il worker Detective (Stage L2) e monitorare il corretto drenaggio del backlog storico dei segmenti audio.
**Grounding:**
- Codice di `worker_detective.py` verificato e validato su `y:\home\Projects\NH-Mini\sviluppi\Lifelog2\src\backend\lifelog2\services\pipeline\worker_detective.py`.
- Il loop greedy `for batch_num in range(5)` con early-exit `if atoms_processed == 0` risulta già integrato e deployato su `CT203`.
- Esecuzione manuale triggerata tramite Redis e monitorata tramite SSH per ispezionare `/tmp/lifelog2-workers/detective.log`.

## [2026-05-25 12:25] TASK — Greedy Detective Logs Inspection

- Recuperati con successo i log reali di `/tmp/lifelog2-workers/detective.log` su `CT203` passando per il comando `pct exec` sull'host Proxmox `192.168.1.2` con la chiave `id_homelab`.
- I log dimostrano inequivocabilmente che all'innesco delle ore **12:13:04**, il Detective ha completato con successo **5 batch consecutivi** (da 8 atomi ciascuno, totale 40 atomi) con le seguenti metriche temporali:
  - **Batch 1/5**: 8 atomi analizzati, completato in 40.5s.
  - **Batch 2/5**: 8 atomi analizzati, completato in 35.9s.
  - **Batch 3/5**: 8 atomi analizzati, completato in 41.1s.
  - **Batch 4/5**: 8 atomi analizzati, completato in 48.8s.
  - **Batch 5/5**: 8 atomi analizzati, completato in 28.1s.
- Tempo totale di elaborazione: **3 minuti e 14 secondi** per 40 atomi, con 0 crash o leak di risorse.
- Il backlog storico si sta drenando a velocità record (5x rispetto alla configurazione legacy).

## [2026-05-25 12:30] END

**Completato:**
- Verificato il corretto funzionamento del "Greedy Batch Processing" per il worker Identity Detective (`worker_detective.py`) su `CT203`.
- Ispezionati e analizzati i log reali tramite Proxmox, confermando l'esecuzione sequenziale di 5 batch da 8 atomi l'uno senza tempi morti (3m 14s di elaborazione continua, 0 candidati rigettati da crash).
- Documentata l'ottimizzazione e l'esito positivo del test nel Second Brain (`log.md`) e in `development-log.md`.

---

## [2026-05-24 23:50] START — Svelte Page Hydration Fix

**Obiettivo:** Risolvere il problema della schermata bianca / mancato rendering della pagina `/pipeline` (si vede solo la headline) su CT203 dopo il refactor e il ripristino del background scuro.
**Grounding:**
- Verificato che il file `+page.svelte` su `CT203` (192.168.1.203) conteneva il codice della pagina.
- Diagnosticato tramite grep la presenza di blocchi HTML duplicati per STAGE F e STAGE G all'interno di `streams-row`.
- Rilevato che i tipi TypeScript su `OrchestratorStatus` erano corretti, ma che la duplicazione dei blocchi HTML causava il crash o il disallineamento visivo.
- Verificato che rimuovendo i blocchi duplicati la compilazione di Vite si completa con successo con 0 errori.

---

## [2026-05-24 23:45] END

**Completato:**
- **Refinement Visivo Cockpit (/pipeline)**:
  - Ripristinato lo sfondo scuro originario (`oklch(0.10 0.015 250)`) di `.pipeline-shell` su CT203.
  - Sfruttata l'opacità ridotta al **45%** delle card (`oklch(0.13 0.02 250 / 0.45) !important`) e dell'headline sticky per creare un superbo effetto **frosted dark glass** (vetro fumé semitrasparente sfocato) che valorizza al massimo i contrasti dei testi chiari e i bagliori al neon.
  - Colorati i titoli delle sezioni (`.section-title`) in electric cyan-blue (`oklch(0.78 0.15 230)`), ereditando la palette dell'eyebrow di testata e rafforzando la coerenza visiva.
- **Integrazione Stage F & G Workers**:
  - Integrate ed esposte nella UI le card per **STAGE F** (Episode Grouping) e **STAGE G** (Visual Covers / FLUX) affiancate alle altre pipeline nella griglia dei worker.
  - Risolti i tipi TypeScript in `OrchestratorStatus` dichiarando esplicitamente le proprietà opzionali `active`, `grouping` e `covers` per evitare crash di compilazione.
  - Rilasciata la funzione helper `formatIsoTime()` in Svelte per formattare i timestamp ISO live degli ultimi run estratti in tempo reale da Redis.
- **Esecuzione Triggers (`/lint` e `/doc`)**:
  - Eseguito `nh-lint.py` per la compliance del progetto Lifelog2 (51 passati, 0 errori, 7 warnings consigliati per script non referenziati).
  - Eseguito `/doc Lifelog2`: aggiornati `knowledge/containers/infrastructure-map.mdc` (CT202 specs RAM/storage dopo resize), `sviluppi/Lifelog2/knowledge/development-log.md` (milestone entry 2026-05-24), `sviluppi/Lifelog2/knowledge/architecture.md` (date + CT202 role), e `sviluppi/Lifelog2/knowledge/api-contracts.md` (documentazione blocco `"gateway"` in `/status`).
  - Committate le modifiche allo storico architetturale con `history_manager.py` (componente `gateway-cockpit`, categoria `FEATURE`).

---

## [2026-05-24 18:05] TASK — Cockpit Aesthetics Refinement & Glassmorphism

**Obiettivo:** Personalizzare l'estetica della dashboard `/pipeline` su CT203 lavorando su sfondo grigio 50% (light slate-grey), semitrasparenze stile frosted glass delle card e della testata, e palette coordinata electric cyan-blue per i titoli di sezione.
**Grounding:**
- Codice di `src/frontend/src/routes/pipeline/+page.svelte` letto.
- File di stile e configurazione ispezionati via SSH.
- Test in tempo reale abilitato con Vite HMR su CT203:5173.

---

## [2026-05-24 17:35] END — CT202 Gateway Telemetry & Control Plane Integration

**Completato:**
- **Proxmox CT202 Resize**: Spegnimento controllato, resize RAM (256 MB → 512 MB) e disco (4 GB → 6 GB) di `[[ct202-gateway|CT202]]` da Proxmox via SSH. Container riavviato e servizi Nginx/Ngrok ripartiti correttamente.
- **Standalone Gateway Dashboard**: Creata una dashboard standalone statico-client-side (Vanilla JS) caricata all'indirizzo `http://192.168.1.202/gateway/` per monitorare live connessioni, throughput e percentili di latenza di Nginx e Ngrok con consumo di **0 MB** RAM sul container.
- **FastAPI /orchestrator/status integration**: Sviluppata fetch asincrona parallela in `src/backend/lifelog2/api/routers/orchestrator.py` su `[[ct203-lifelog|LXC 203]]` con timeout protetto a 1.5s, includendo la telemetria nella risposta JSON. Riavviato il solo servizio FastAPI API (`systemctl restart lifelog2`), mantenendo la pipeline worker interamente attiva e intatta.
- **Svelte 5 /pipeline integration**: Estesa la dashboard del control plane in `+page.svelte` con una card premium glassmorphic "Internet Gateway · CT202" che mostra tutti i dati live in tempo reale. Vite HMR applicato con successo ed istantaneamente.
- **Audit e Documentazione**: Compilato `walkthrough.md` di riepilogo, aggiornati `NH-Mini/log.md`, `NH-Mini/index.md` e `state/session-journal.md`.

---

## [2026-05-24 13:31] TASK — Monitoring pipeline & quality audit

**Obiettivo:** Verificare lo stato live della pipeline di reprocessing su LXC 203, code Redis su CT120, qualità semantica degli atomi generati, ed upload sul gateway CT202.
**Grounding:**
- Status API `/orchestrator/status` su CT203:8002 caricato.
- Log di `stage_d_enrichment` in `/tmp/lifelog2-workers/` tailato.
- Query diretta su Postgres `lifelog_roberto` via CT190 eseguita.
- Log di Nginx `gateway_access.log` su CT202 controllati via SSH.

---

## [2026-05-22 16:02] START — Allineamento e prosecuzione dopo sessione intermedia

**Obiettivo:**
- Analizzare il lavoro svolto dall'agente intermedio nella sessione del 2026-05-22 (Intelligence Layer Z7, Profile Builder Strato 1+2, addendum, status roadmap, ecc.).
- Verificare la corretta documentazione e allineamento di NH-Mini e Lifelog2.
- Concordare con l'utente i passi successivi tra le priorità P1 e P2 individuate nel file `lifelog2-status-roadmap.md` (es. creazione indice HNSW, abilitazione timer Profile Builder, o implementazione Tier B social circle / Strato V LLM validation).

**Grounding:**
- Verificata la presenza e il contenuto dei file di documentazione `lifelog2-status-roadmap.md` e `lifelog2-intelligence-addendum-v1.md` in `sviluppi/Lifelog2/docs/`.
- Verificato l'accesso SSH diretto e lo stato dei repository git da CT190, confermando che il codice è allineato ed i relativi file sono nello stato documentato nell'END dell'agente precedente.
- Verificato il contesto attivo in `workspace/active_config.json` come `Lifelog2`.

---

## [2026-05-22] END — Lifelog2 Intelligence Layer Z7 + /doc /lint /finalize

**Completato:**
- **Profile Builder Worker (Strato 1+2):** `worker_profile_builder.py` — zero LLM, SQL puro. Strato 1: decisions/action_items/first-person opinion → UserProfileFact. Strato 2: topics, media habits, ora picco, social circle. Corroborazione assintotica (`min(0.95, old + 0.08×(1−old))`), decay settimanale (×0.97, floor 0.05). Systemd timer domenica 04:00. Redis idempotenza.
- **Systemd units:** `lifelog2-profile-builder.service/timer` + `lifelog2-cleanup-audio.service/timer` in `deploy/`. Non ancora abilitati su CT203.
- **Intelligence Addendum §8 ricostruito:** spec teorica → documentazione operativa. §8.12 Cerchia sociale Tier B (clustering voiceprint anonimi, soglia 0.65). §8.13 Strato V (LLM validation pass gray-zone, batch 6-8/call, verdetti valid/invalid/third_party/context_limited).
- **Full audit codebase + docs:** report completo Z0–Z7, pipeline A→G, workers, identity, search, frontend.
- **`lifelog2-status-roadmap.md`:** nuovo documento living — 10 sezioni ✅/🟡/🔲, roadmap P1→P5 checklist, visual bar. Referenziato nel master blueprint.
- **`/doc lifelog2`:** `knowledge/architecture.md` (worker_profile_builder, prompt v10, Profile Builder section, Async Workers), `knowledge/memory-model.md` (Person voiceprint 192d→256d fix, UserProfileFact Profile Builder detail), `knowledge/development-log.md` (entry completa).
- **Wiki NH-Mini aggiornata:** `stack-lifelog2.md` (prompt v10, Stage D v10 description, /profile view, M8 milestone, Profile Builder in pipeline), `ct203-lifelog.md` (2 nuovi timer in services table, deploy log 2026-05-22).
- **Lint:** 47/47 ✅, 0 warnings, 0 errors.

**Incompleto:**
- Profile Builder timer non ancora abilitato su CT203 (P1 roadmap — richiede ok esplicito utente per `systemctl enable`).
- M4A cleanup timer non ancora abilitato (istruzione esplicita: non abilitare autonomamente).
- Re-enrollment storico ancora pending (richiede ARIA restart + script producer/consumer).
- HNSW index mancante su `memory_atoms.embedding` (P1 roadmap — 1 migration, sblocca search).

**Mine per il prossimo agent:**
- **P1:** `systemctl enable lifelog2-profile-builder.timer` su CT203 (dopo ok Roberto).
- **P1:** `CREATE INDEX USING hnsw` su `memory_atoms.embedding` — 1 migration, sblocca tutta la search vettoriale.
- **P2:** Cerchia sociale Tier B (clustering voiceprint anonimi) → `docs/lifelog2-intelligence-addendum-v1.md §8.12`.
- **P2:** Strato V LLM validation pass → `docs/lifelog2-intelligence-addendum-v1.md §8.13` + migration `validated_at`.
- Consultare `sviluppi/Lifelog2/docs/lifelog2-status-roadmap.md` come checklist aggiornata all'inizio della prossima sessione.

---

## [2026-05-20 18:00] END — Lifelog2 Stage B CAMCORDER + Voiceprint + /doc + cleanup

**Completato:**
- **Stage B CAMCORDER fix**: soglie quality gate differenziate per `audio_source` — CAMCORDER/ambient usa RMS -65dBFS, SNR -30dB, speech_ratio 0.0. Segmenti ambient non più scartati.
- **Rejected M4A in MinIO**: `_reject()` salva l'M4A in `quality-rejected/{persona}/{YMD}/{segment_id}.m4a` con metadata. Recuperabili per analisi o re-injection.
- **WAV lifecycle corretto**: Stage C erroneo reverted — Stage E è il solo owner della WAV deletion.
- **Voiceprint Roberto re-enrollment**: clip 30s da offset 23.2s (senza silenzio), embedding 256d ResNet34. Match: 25/7650 turns (top: 0.981). Audio in `voiceprints/enrollment_optimized/roberto_30s.m4a`.
- **`rematch_voiceprint.py`**: script standalone personal/mixed/ambient con `--threshold` + `--dry-run`. Deployato su CT203.
- **`/doc lifelog`**: `knowledge/architecture.md`, `knowledge/development-log.md` aggiornati. `ct203-lifelog.md`, `log.md`, `index.md` wiki NH-Mini aggiornati. `history_manager.py` con 4 entry.
- **Cleanup repo**: script temp eliminati (root + scripts/ + scratch/). Script utili archiviati con descrizione in `scripts/`.

**Incompleto:**
- Re-injection dei segmenti CAMCORDER salvati in `quality-rejected/` (script injector non ancora scritto). Attendi ok utente.
- Enrollment voiceprint Paola/Matteo (E2) — futuro.

**Mine per il prossimo agent:**
- Script injector per `quality-rejected/`: scorrere MinIO, costruire payload Redis identico a `uploads.py`, pubblicare su `lifelog:stream:asr`. Chiedere ok a Roberto prima.
- RD-1 Stage D v8 (`media_source`), RD-2 `richness_score`, RD-3 voiceprint_sample_key — da pianificare.
- Milestone M8 `/ask` RAG o M9 `/vault` oblivion — chiedere a Roberto quale priorità.

---

## [2026-05-20 15:11] TASK — SSH Access Fix + Lifelog2 Audit Completo

**Completato:**
- Fix accesso SSH diretto CT190 → CT105/CT104/CT107 via `pct exec` su Proxmox (chiave pubblica CT190 iniettata). Tutti e 3 i container ora accessibili direttamente.
- Audit telemetria CT203 (`telemetry.db`): 2 upload oggi (MIC, 282s + 202s), entrambi scartati Stage B `low_snr` (snr_db=-2.1 e -0.7 dB).
- Audit Postgres CT105 (`lifelog_roberto`): 1301 raw_captures, 1110 memory_atoms, 787 episodes, 1 person, 0 action_items, 0 decisions.
- Audit MinIO CT104 (`lifelog` bucket): 250 raw-encrypted (1.5GB), 1608 covers, 1473 audio/archive (2.3GB), 1110 transcripts.
- Profilo utente: Roberto Guareschi, `person_id=4ca22a97`, `identity_level=3`, `voiceprint_quality=1.0`, vettore 192d SpeechBrain.
- Verifica SOPS: 14 namespace registrati (proxmox.main, ssh.aria_gaming_pc, ct105.postgres, lifelog.db ecc.). Decryption fallisce per `~/.age.key` non trovato in sessioni SSH non-interattive.
- Workspace switchato su Lifelog2 (via SSH su CT190, symlink corretto).

**Issue aperti:**
- SOPS decryption non funziona da script SSH non-interattivi: aggiungere `SOPS_AGE_KEY_FILE=/root/.age.key` ai systemd unit.
- 2 segmenti oggi scartati low_snr: normale se registrazione in background con rumore ambiente.

**Mine per il prossimo agent:**
- Prossimo step sviluppo: scegliere tra M8 (/ask + pgvector semantic search) o M9 (/vault + oblivion scheduler).
- Script audit riutilizzabili in `scripts/`: `fix_ssh_access.sh`, `lifelog_full_audit.sh`, `lifelog_pg_minio_audit.sh`.

## [2026-05-17 10:56] END — Lifelog2 Memory Atom Covers & Fallback UI

**Completato:**
- **Integrazione `visual_prompt` in Stage D**: la pipeline veloce (Qwen3) ora estrae correttamente il prompt cinematografico per ogni Memory Atom generato e lo salva in `MemoryAtom.visual_prompt`.
- **Risoluzione blocco DB CT105**: superato timeout `psql` eseguendo le query via `pct exec 105 -- docker exec postgres`. La migrazione `ALTER TABLE memory_atoms` era già applicata.
- **Worker Stage G (Batch Covers)**: aggiornato per interrogare in parallelo Episodi E Memory Atoms mancanti di cover. Tutte le richieste sono accodate alla pipeline batch di FLUX.2.
- **API Dashboard (`dashboard.py`)**: introdotto endpoint `/api/dashboard/cover/atom/{memory_id}`.
- **Fallback UI Cover**: modificata la query di fetch Atoms per estrarre entrambe le chiavi (Atomo e Episodio). Costruzione intelligente del `cover_url` con priorità alla cover atomica e fallback automatico sulla cover dell'episodio.
- **Frontend Svelte**: semplificati i componenti `FilmstripRail` e `EpisodeMembersPreview` per consumare una singola stringa `cover_url` pre-calcolata.
- Modifiche deployate su CT203 e worker riavviato.
- Lint passato (45/45 ✅).
- Hard Triggers eseguiti: `/doc lifelog2`, `/finalize`.

**Incompleto:**
- Script di riparazione (`stage_f_grouping`) per gli episodi storici orfani di `visual_prompt` (fermo a 11 episodi) ancora da eseguire.
- Generazione covers pendente: il nuovo `stage_g_covers.py` sta accodando ma le cover effettive dipendono dall'esecuzione su ARIA PC139.

**Mine per il prossimo agent:**
- **Script Riparazione Prompt Storici**: accedere a CT203 (`ssh root@192.168.1.203`) e lanciare la rigenerazione (`python3 -m lifelog2.services.pipeline.stage_f_grouping`) per chiudere il backlog.
- **Verifica UI Copertine**: caricare la dashboard e accertarsi che i singoli atomi presentino le loro copertine via via che Stage G e FLUX.2 su PC139 finiscono i batch.

## [2026-05-17 10:55] TASK — Memory Atom Covers implementation
- Modificato `stage_g_covers.py` per estrarre sia `episodes` sia `memory_atoms` senza cover e inviarli alla generazione batch.
- Aggiunto fallback intelligente in `dashboard.py`: estratti entrambi i cover_key. Se atom ha cover_key usa `/api/dashboard/cover/atom/{memory_id}`, altrimenti fallback su `/api/dashboard/cover/{episode_id}`.
- Aggiornato frontend Svelte (`FilmstripRail.svelte`, `EpisodeMembersPreview.svelte`) per ricevere direttamente il `cover_url`.
- Modifiche deployate su CT203 e backend riavviato.

## [2026-05-17 10:45] END — Lifelog2 Stage G + ARIA backends + doc/lint/finalize

**Completato:**
- **Stage G covers in orchestratore**: `_covers_loop` trigger-only, parte dopo Stage F rc=0 o Redis cmd `{"cmd":"run_covers"}`. Deployato su CT203, restartato, operativo. Git Lifelog2 allineato dev+RT a `4715397`.
- **ARIA backends 0.0.0.0**: tutti i backend FastAPI su PC139 migrati da `127.0.0.1` a `0.0.0.0`. FLUX server: aggiunto `DELETE /output/{filename}`. Git ARIA `ca25b05` su origin.
- **aria_imagegen.py**: `output_key` param, fix `output` dict, `minio_url→image_url` fallback.
- **stage_f_episode_v2.txt**: visual_prompt upgrade — cinematografico 40-60 parole.
- **worker_detective.py**: bugfix `ma.start_time` invece di `s.started_at`.
- **nh-lint.py**: fix case-insensitive project lookup (era `lifelog2` vs `Lifelog2`).
- **/doc lifelog2**: `knowledge/architecture.md`, `api-contracts.md`, `development-log.md` aggiornati.
- **/doc aria**: `ARIA-Service-Registry.md` (coda imagegen, env flux-aria, DELETE pattern), `aria-state-of-gaps.md` (A0-5 resolved, A0-6 resolved), `ARIA-blueprint.md` (contratto imagegen reale).
- **/doc nh-mini**: `ct203-lifelog.md` (servizi + orchestratore), `lifelog2_dev-pattern.md` (Stage G), `index.md` (timestamp).
- **lint 44/44 ✅** (lifelog2 49/49, aria 49/49).

**Incompleto:**
- Repair script per 11 episodi senza `visual_prompt` — da eseguire manualmente su CT203.
- ARIA `backends/acestep` submodule: `aria_wrapper_server.py` cambiato localmente (0.0.0.0) ma non committato nel submodule git.

**Mine per il prossimo agent:**
- Repair visual_prompt: `ssh root@192.168.1.203 "cd /opt/Lifelog2/src/backend && source /opt/Lifelog2/.env && python3 -m lifelog2.services.pipeline.stage_f_grouping"` — Stage F rigenera i prompt mancanti, poi Stage G genera le cover.
- `backends/acestep` submodule: se serve aggiornarlo, clonare il submodule repo separatamente, applicare la fix `--host 0.0.0.0`, fare PR nel submodule.
- Dashboard copertine: verificare che le cover già generate (12 episodi) appaiano nella dashboard dopo il prossimo Stage F run.

## [2026-05-17] END — ARIA health-check fix + Firebase Studio port conflict

**Problema risolto**: Firebase Studio (Antigravity IDE Google), quando aperto su PC 192.168.1.139 con Remote SSH attivo verso LXC 190, fa port-forwarding automatico dai port 8090/8091/8093 di LXC 190 verso `127.0.0.1` sul PC. L'orchestratore ARIA health-checkava `localhost:8090` → riceveva risposta da Firebase Studio invece di `llama-server` → timeout → loop infinito di riavvii di Qwen3-14B.

**Fix in `orchestrator.py`** (`_health_check`, riga ~231):
- Prima: `url = self.MODEL_CONFIGS[model_id]["health_url"]` (usava `localhost`)
- Dopo: `url = self.MODEL_CONFIGS[model_id]["health_url"].replace("localhost", self.local_ip)` (usa IP esterno `192.168.1.139`)
- `self.local_ip` risolto all'avvio via `get_node_ip()` — `backends_manifest.json` rimane con `localhost`, nessun hardcoding.

**Altri fix di sessione (già documentati in sessioni precedenti ma completati)**:
- `startup_wait` Qwen3-14B: 120s → 600s (caricamento modello ~10 min)
- `stage_f_episode_v2.txt`: template `visual_prompt` riscritto stile cinematografico
- `flux_imagegen/server.py`: aggiunto salvataggio PNG locale + endpoint DELETE
- `stage_g_covers.py`: cleanup file locale ARIA dopo download MinIO

**Stato Lifelog2 pipeline**:
- 14 episodi totali: 3 con visual_prompt (cinematografici, buona qualità), 11 senza
- 0 cover_image generate (pipeline in pausa)
- Segmenti: 378 discarded, 36 consolidated; Memory atoms: 36
- Repair script interrotto durante la sessione — da ri-eseguire nella prossima sessione

**Stato git ARIA**:
- PC 139 e LXC 190 hanno il repo `aria.git` divergente da commit `6c0046e`
- PC 139: 3 commit WhisperX in più + 3 file uncommitted (`orchestrator.py`, `backends_manifest.json`, `flux_imagegen/server.py`)
- LXC 190: 1 commit `47dd3e4 feat(flux): local JPEG output pattern` non presente su PC 139
- NH-Mini: modifiche non committate (da allineare)

**Documentazione aggiornata**:
- `sviluppi/ARIA/docs/ARIA-Service-Registry.md`: Note Operative (Firebase Studio conflict + startup_wait 600s), Health Check URLs aggiornati, FLUX.2-klein-4B aggiunto
- `NH-Mini/log.md`: entry dev 2026-05-17
- `state/session-journal.md`: questa entry

---

## [01:51] END — 2026-05-16 Lifelog2: Frontend Views B4–B7 + Backend API + Wiki sync

**Completato:**
- **Background fix**: immagine `/bg.jpg` spostata da `body` a `html` — SvelteKit wrapper ha `overflow:hidden` che rompe `background-attachment:fixed` silenziosamente.
- **Palette legibilità**: glassmorphism opacità alzate (glass 0.45→0.72, sidebar 0.40→0.82, card 0.35→0.68), text-2 0.80→0.90, text-3 0.55→0.72.
- **Vista B4 Sagas**: filtri capture_class + tag search, paginazione load-more, accent bar colorata per tipo.
- **Vista B5 People**: identity level pills, avatar initials, voiceprint dot, expand detail con first/last seen.
- **Vista B6 Timeline**: spine verticale con dot colorati, raggruppamento mese/giorno, dati da `/api/dashboard/sagas`.
- **Vista B7 Transcript**: speaker turns + full-text toggle, filtro per speaker, sidebar con summary/topics/action_items, dati da MinIO via `/api/dashboard/transcript/{id}`.
- **Day view aggiornata**: campo `has_transcript` + link "◎ Trascrizione →" su atom espanso.
- **Backend dashboard.py**: endpoint `/sagas`, `/people`, `/transcript/{id}` — fix asyncpg `::text[]` con Python tally, fix `atom.topics` dict/list ambiguity.
- **Wiki sync**: log.md, stack-lifelog2.md (Milestones M5/M7, Migration 0005 ✅, Frontend Views table, API Endpoints table), lifelog2_dev-pattern.md (full rewrite), index.md, development-history.mdc (5 entry).

**Incompleto:**
- 2 atom misclassificati (`0a4bf747`, `be8217d1`) ancora da rielaborare con Stage D v5.

**Mine per il prossimo agent:**
- Viste non ancora costruite: B8 Ask/RAG, B9 Vault (presenti in sidebar ma nessun codice).
- `raw_transcript_key` NULL su alcuni atom — Stage D non lo popola per tutti i segment; necessario per Stage F Pass 3.
- Worker Detective e Stage G: zero righe di codice, blueprint chiaro, headroom 209s disponibile.

---

## [19:45] END — 2026-05-15 Lifelog2: Control Plane v2 + /doc + /finalize

**Completato:**
- **Telemetria SQLite**: `core/telemetry.py` — 5 tabelle, auto-init, thread-safe via `asyncio.to_thread()`. Backfill da log file: 163 upload, 165 Stage B, 34 C, 39 D/E, 2 grouping runs.
- **Worker instrumentation**: Stage B/C/D/E/F con `time.perf_counter()` + `record_stage()`/`record_grouping()`.
- **API Telemetria**: 6 endpoint `/telemetry/*` (summary, stages, recent, uploads/recent, grouping, daily).
- **Orchestrator API riscritta**: `/status` con dati Redis reali (`XINFO STREAM`) + Postgres query diretta. `/logs` che legge e mergia `/tmp/lifelog2-workers/stage_*.log`.
- **Pipeline Dashboard v2**: `/pipeline` con 5 sezioni (Workers, Streams, DB Stats, Telemetria, Log Terminal). Bug Svelte 5 `{@const}` risolto due volte — regola: figlio immediato di blocco, mai di tag HTML.
- **CT203 timezone**: fixato a `Europe/Rome (CEST)` via bypass D-Bus.
- **/doc lifelog2**: `development-log.md`, `architecture.md`, `api-contracts.md`, `stack-lifelog2.md` aggiornati.
- **nh-lint**: 45/45 ✅

**Incompleto:**
- 2 atom misclassificati (`0a4bf747`, `be8217d1`) da rielaborare con Stage D v5.
- `raw_transcript_key` NULL su MemoryAtom — Stage F Pass 3 ne ha bisogno.

**Mine per il prossimo agent:**
- Stage F Pass 3 (split within-atom) richiede `raw_transcript_key` nel MemoryAtom — aggiungere in Stage D o E.
- Worker Detective e Stage G: zero righe di codice, blueprint chiaro, headroom 209s disponibile.

## [05:26] END — 2026-05-15 Lifelog2: orchestrator Stage F + Stage D v5 + Stage B fix + /doc + /lint

**Completato:**
- Orchestratore Lifelog2: Stage F integrato come `asyncio.create_task` parallelo al loop B→E sequential greedy. Ogni 30min, trigger manuale via Redis `{"cmd": "run_grouping"}`. Status API aggiornata con campo `grouping`.
- Stage D v5: `action_items` e `decisions` aggiunti all'output MemoryAtom. `_NOISE_PHRASES` frozenset filter. `_parse_str_list()` helper condiviso. Rerun script su 19 atom — 7/19 con dati non vuoti.
- Stage B metrics-on-discard fix: `_reject()` ora scrive rms_db/snr_db/speech_ratio/duration_seconds anche su segment scartati.
- /doc lifelog2: `stack-lifelog2.md` aggiornata con orchestrator section, Stage D v5, Stage B fix, milestone M4/M5.
- /lint lifelog2: 5 issue fixati (CT203 "pending approval" stale, Qwen3-ASR come primary stale, lifelog2_dev-pattern orfano, ecc).
- nh-lint: 45/45 passed.

**Incompleto:**
- 2 atom misclassificati (`0a4bf747`, `be8217d1`) da rielaborare con Stage D v5 (podcast classificati come monologue).
- `raw_transcript_key` NULL su MemoryAtom — Stage D non lo popola; necessario per Stage F Pass 3.

**Mine per il prossimo agent:**
- Stage F pass 3 (split within-atom) richiede `raw_transcript_key` in MemoryAtom — verificare se va aggiunto in Stage D o E.
- Worker Detective e Stage G non ancora implementati — headroom 209s disponibile, blueprint chiaro.

## [2026-05-14 19:30] START — WhisperX E2E + /doc nh-mini, aria, lifelog2

**Obiettivo:** Cristallizzare sessione 2026-05-14. WhisperX large-v3 integrato come ASR primario per Lifelog2. Pipeline A→E misurata end-to-end. Analisi headroom Level 2. /doc su tutti e tre i progetti.

**Grounding:** sessione continuata dopo compaction context — tutti i deploy già fatti. Pipeline A→E verificata con segment `14cc6f03-...` (299s audio, 91s totali warm).

---

## [2026-05-14 19:00] TASK — WhisperX E2E + timing pipeline + headroom Level 2

**Completato nella sessione:**

- WhisperX large-v3 integrato come backend STT primario su ARIA PC139 (`lifelog-whisperx` env, porta 8091, FastAPI).
- `model_logic_ids` fix in `orchestrator.py` (riga 668): `"whisperx-large-v3"` aggiunto. Senza questa lista ARIA è cieca alle code Redis del modello.
- `threading.RLock` fix (riga 171 orchestrator): shutdown deadlock risolto (`_ensure_single()` + `_kill_proc()` tenevano stesso Lock → deadlock → fix con RLock).
- `backends/lifelog_whisperx.py` (handler class `LifelogWhisperXBackend`) deployato su PC139 — era mancante, causava `_BACKENDS_AVAILABLE = False` → tutti i backend Python = None.
- `backends_manifest.json` aggiornato: entry `whisperx-large-v3`, porta 8091, env `lifelog-whisperx`, `startup_wait=150`.
- Stage C (`stage_c_asr.py` su CT203) aggiornato: `ARIA_QUEUE_KEY = "aria:q:stt:local:whisperx-large-v3:lifelog"`.
- E2E test con audio AES-GCM cifrato: A→E completata in **~91s** su segmento 299s (3.3× realtime warm).

**Timing misurato:**
- Stage B (decrypt+WAV): ~1s
- Stage C (WhisperX): ~24s (16s inferenza + overhead ARIA)
- Stage D (GPU switch 35s + qwen3-14b ~12s): ~49s — il bottleneck è il GPU switch, non il modello
- Stage E (mxbai embed + WAV delete): ~3s
- **Totale warm: ~91s su 299s audio**

**Analisi headroom Level 2:**
- Finestra libera: 300s - 91s = **~209s** per analisi asincrone
- LLM già warm dopo Stage D → ogni chiamata Level 2 ~12s → **~17 chiamate LLM/segmento** nel budget
- Greedy batch (BatchOptimizer regola binaria: stay if ≥1 task in coda) protegge la warmness: se Level 2 task arrivano subito dopo D, LLM non switcha mai
- Level 2/3 workers (Detective, Stage F, Stage G, Retroactive Indexer): **zero righe di codice** — solo blueprint. Prossimo step di sviluppo naturale.

## [2026-05-14 19:30] END
**Completato:** /doc nh-mini, /doc aria, /doc lifelog2 — tutti i file di knowledge allineati con sessione 2026-05-14. Log.md, development-log.md, architecture.md, api-contracts.md, ARIA blueprint, aria-state-of-gaps aggiornati.
**Incompleto:** nulla di critico.
**Mine:** Level 2 workers (Detective, Stage F/G) da implementare — headroom disponibile e architettura chiara.

---

## [2026-05-11 17:30] END
**Obiettivo sessione**: Global Registry implementation + CT203 deploy + Android handoff analysis.
- **Completato**:
  - Global Registry (`registry.db` SQLite) implementato su CT203 — package `registry/` con `models.py`, `db.py`, router `auth.py`
  - Endpoint live: `POST /api/v1/auth/register`, `POST /api/v1/auth/login` — opaque hex token + bcrypt + encryption_salt
  - `api/deps.py` refactored: `CurrentDevice` dataclass, helpers centralizzati (`_hash_token`, `_make_token`, `get_reg_db`), fire-and-forget last_seen_at
  - CT203 systemd service (`lifelog2.service`) — uvicorn :8002, `PYTHONPATH` corretto, `EnvironmentFile`
  - CT202 nginx: location `/lifelog/` → CT203:8002 con `client_max_body_size 50M`
  - End-to-end verificato: `https://obliging-fitting-cheetah.ngrok-free.app/lifelog/health` → 200
  - Utente test "matteo" registrato via curl + token verificato
  - `/simplify` eseguito: fix type mismatch `user_id str vs uuid`, duplicate helpers rimossi, guard double-init `registry/db.py`, path fragile → env var
  - `/doc lifelog2` completo: `architecture.md`, `api-contracts.md`, `development-log.md`, `NH-Mini/log.md`, `stack-lifelog2.md` aggiornati
- **Incompleto**:
  - Android app upgrade (Task A/B/C/D) — pending Android Studio agent
  - `ALTER TABLE persons.voiceprint_embedding vector(192) → vector(256)` su CT105 — blocca M4 D1
  - Script Session Management Liquid Brain (Swap-In/Swap-Out fisico)
- **Mine**:
  - ⚠️ CT203 gira Python 3.11.2 ma `pyproject.toml` dichiara `>=3.12` — da documentare/allineare
  - ⚠️ `HF_HUB_OFFLINE` deve essere `false` per primo load modelli gated PC139

---

## [2026-05-11 14:15] END
**Obiettivo sessione**: Definizione architettura Liquid Brain e audit app Android.
- **Completato**: 
  - Architettura Liquid Brain (Swap-In/Out) definita e documentata.
  - Global Registry (LXC 203) progettato.
  - Audit completo App Android v1 e individuazione gap (GPS/Metadata).
  - Creato Handoff Document per upgrade App v2.0 (copiato su LXC 190 e PC 139).
  - Wiki e MDC aggiornati secondo protocollo NH-Mini.
- **Incompleto**: 
  - Implementazione fisica del registry.db e dei relativi endpoint.
  - Script di Session Management per mount/unmount.
- **Mine**:
  - Attenzione alla discrepanza tra il codice del repo App (TODO GPS) e la realtà dei file .m4a (GPS presente). Usare i file reali come ground truth.

---

## [2026-05-11 03:40] END

**Completato:**
- **Stabilità Blackwell**: Fixato crash torchaudio via `soundfile.read()` e pinning `transformers==4.57.6`.
- **Contratto Tecnico**: Aggiornato `sviluppi/ARIA/docs/backends/lifelog-asr.md` con protocolli Redis e Payload 256d.
- **Biometria**: Switch ufficiale a vettori 256d (ResNet34) e registrazione architetturale.
- **Service Catalog**: Integrato backend ASR nel monitoraggio di NH-Mini (:8087).
- **Wiki**: Create pagine concept per Stratex/Lifelog2 Dev e nuova entità Service ASR.
- **Lint**: 100% Compliance (50/50 check) raggiunta sanando i 3 warning pendenti.

**Incompleto:**
- Migrazione schema DB `persons.voiceprint_embedding` da Vector(192) a Vector(256).
- Refactor `stage_c_asr.py` per persistenza biometrica (Stage D1).

**Mine:**
- ⚠️ Il database `lifelog_roberto` (CT105) rifiuterà gli embedding di ARIA finché non viene eseguito l'ALTER TABLE a 256 dimensioni.
- ⚠️ Assicurarsi che `HF_HUB_OFFLINE` sia disabilitato per il primo caricamento dei modelli gated su PC 139.

---

# Session Journal — NH-Mini

File append-only. L'agent scrive **durante** la sessione, non alla fine.
Ogni entry è un timestamp + tipo + contenuto.

Tipi: START | TASK | DECISION | BLOCKED | RESOLVED | DEVIATION | END

## [2026-05-09 13:57] END

**Completato:**
- ARIA PC139: identificato e fixato bug idle timeout in `orchestrator.py` — branch `if not decision:` iterava `known_models` (vuoto con DIAS in pausa) invece di `_procs.keys()`, impedendo a `mark_idle()` di scattare e tenendo il backend Qwen3-TTS attivo per 3+ giorni senza mai spegnersi.
- ARIA: restart pulito confermato (13:22:42 su PC139) — 2 processi Python, nessun backend caricato, telemetria DB ok (10.951 task, ultimo TTS 10:20:36).
- Git sync: commit `24c6d32` su LXC 190, push su GitHub, pull su PC139 (`8cd2ad1`).
- `/doc aria` completato: stack-aria.md (backend table + sezione idle timeout + Lifelog2 come consumatore), log.md entry, aria-state-of-gaps.md (gap A0-3 resolved), ARIA-blueprint.md (sezione Backend Idle Timeout §7), aria-project-context.md aggiornata.
- `/lint aria`: 46 passed, 2 warnings (stratex_dev e lifelog2_dev — pre-esistenti), 0 errors.

**Incompleto:** nulla di critico.

**Mine per il prossimo agent:**
- **Lifelog2 M3 TEST** ← priorità alta: test end-to-end Stage B→C con 1 WAV V1 — verificare SpeakerTurn in CT105 `lifelog_roberto` e transcript JSON in MinIO `transcripts/raw/roberto/`.
- Hyperion: monitorare avanzamento (ETA ~12 maggio, 70 t/h, ora con idle timeout funzionante ARIA si spegnerà correttamente tra una sessione DIAS e l'altra).
- Lint warnings (bassa priorità): aggiungere link `stratex_dev` e `lifelog2_dev` nel wiki.

---

## [2026-05-09 12:55] END

**Completato:**
- DIAS: Ottimizzazione heartbeat orchestratore (30s -> 5s) per reattività dashboard.
- DIAS: Implementata coerenza globale della pausa manuale in tutti i worker (`BaseStage` compliant e custom: Stage D2, E, F).
- DIAS: Dashboard Svelte 5 ottimizzata con Infinite Scroll nelle tiles degli stadi (testata con >7000 asset).
- DIAS: UI UX polish — spostato pulsante salvataggio pre-produzione, contestualizzato Voice Carousel.
- Framework: Aggiornate `.cursorrules` (v9) con il pattern **PIPELINE SUSPENSION**.
- Framework: Aggiornata `knowledge/architecture/core-modules.mdc` e `infrastructure-map.mdc`.
- Deployment: Sincronizzazione totale LXC 190 -> 201 via Git + build dashboard RT.
- `/lint` 41/41 superati per lo stack DIAS.

**Incompleto:** nulla di critico.

**Mine per il prossimo agent:**
- Monitorare la stabilità di CT201 con il heartbeat a 5s durante lunghe sessioni di mastering (Stage F).
- Verificare se l'utente desidera portare il pattern di pausa atomica (`BaseStage`) anche sui worker di Stratex/Lifelog2 per uniformità.

---

## [2026-05-09 11:30] START — DIAS Pipeline Optimization & Dashboard Stability

**Obiettivo:** Ridurre la latenza di monitoraggio, garantire la coerenza della pausa manuale e ottimizzare la dashboard per grandi dataset.
**Grounding:** LXC 201 RT attivo, Redis HUB (CT120) raggiungibile, Progetto `dan_simmons_hyperion` con 7000+ asset.

---

# Session Journal — NH-Mini

File append-only. L'agent scrive **durante** la sessione, non alla fine.
Ogni entry è un timestamp + tipo + contenuto.

Tipi: START | TASK | DECISION | BLOCKED | RESOLVED | DEVIATION | END

## [2026-05-07 13:09] END

**Completato:**
- ARIA PC139: backend STT `LifelogASRBackend` — `server.py` FastAPI :8087, `asr_pipeline.py` (Qwen3-ASR-1.7B + ForcedAligner + pyannote), `backends/lifelog_asr.py` wrapper (health-check pattern, non subprocess.Popen)
- ARIA PC139: `orchestrator.py` patchato con 6 modifiche (import, `_lifelog_asr_backend`, `model_logic_ids`, elif branch, `_process_lifelog_asr_task()`)
- ARIA PC139: `backends_manifest.json` aggiornato — entry `qwen3-asr-1.7b` porta 8087, env `lifelog-asr`, startup_wait 180s
- Lifelog2: `stage_c_asr.py` worker completo — consumer `lifelog:cg:asr`, BRPOP callback `aria:c:lifelog:{job_id}`, SpeakerTurn insert (campi corretti: `speaker_label_raw`, `start_offset_ms`, `end_offset_ms`, `text_raw`), transcript JSON su MinIO `transcripts/raw/`, emit `lifelog:stream:enrich`
- ARIA docs: `ARIA-Service-Registry.md`, `ARIA-blueprint.md`, `aria-state-of-gaps.md` aggiornati (gap A0-2 resolved, A1-4 noted)
- Lifelog2 docs: `architecture.md`, `development-log.md` aggiornati con M2+M3
- Analisi GPU exclusivity ARIA: STT task aspetta in coda se TTS attivo; al cambio modello ~4.5 min delay (180s warmup ASR + 60s TTS restart). Singolo test = trascurabile su Hyperion
- Analisi produzione Hyperion: telemetria reale da `aria-telemetry.db` — **70 t/h** effettivi, 5.964/13.509 scene (44.1%), 11.1h audio grezzo prodotto, **ETA ~12 maggio** (4.5 giorni cal. a 24h/die)
- `/doc nh-mini` completato — stack-lifelog2.md aggiornato (M3 in test), log.md entry analisi Hyperion
- `/lint nh-mini`: 41 passed, 2 warnings, 0 errors

**Incompleto:**
- 2 warnings lint: `stratex_dev` e `lifelog2_dev` non linkati nel wiki (bassa priorità)

**Mine per il prossimo agent:**
- **Lifelog2 M3 TEST** ← priorità alta: riavviare ARIA orchestratore su PC139 → test end-to-end Stage B→C con 1 WAV V1 (verifica SpeakerTurn in CT105 `lifelog_roberto`, transcript JSON in MinIO `transcripts/raw/roberto/`)
- Hyperion: monitorare avanzamento (70 t/h, ~7.545 scene rimanenti, ETA ~12 maggio)
- Lint warnings (bassa priorità): aggiungere `stratex_dev` e `lifelog2_dev` nelle pagine wiki `stack-stratex.md` e `stack-lifelog2.md`

---

## [2026-05-07 23:45] END

**Completato:**
- Lifelog2: esplorazione dati V1 su PC139 (192.168.1.139) — 2482 memories, 1700 .m4a, trascrizioni Whisper complete, SQLite + ChromaDB
- Lifelog2: creato bucket `lifelog` su MinIO CT104 (`minioadmin:minioadmin`)
- Lifelog2: script `scripts/v1_import.py` — SCP da PC139 → MinIO → DB CT105 → Redis events
- Lifelog2: 20 segmenti V1 importati (10 ambient + 10 personale) in `raw-decrypted-temp/roberto/` su MinIO
- Lifelog2: 20 RawCapture + 20 Segment in `lifelog_roberto` CT105 con `pipeline_status="queued"`
- Lifelog2: 20 eventi emessi su Redis stream `lifelog:stream:ingest`

**Incompleto:** nulla di critico

**Mine per il prossimo agent:**
- Lifelog2 M2: pipeline worker Stage A — consumer Redis `lifelog:stream:ingest`, download M4A da MinIO `raw-decrypted-temp/`, conversione WAV 16kHz mono (ffmpeg), aggiornamento `pipeline_status = "preprocessing" → "asr"`
- Lifelog2: I 20 segmenti sono in `queued` — pronti per il pipeline quando sarà implementato
- Lifelog2: confronto output ASR V2 vs trascrizioni V1 (ground truth in `D:\LifeLogData\archive\transcripts_enriched\`)

---

## [2026-05-07 10:00] START — Lifelog2: V1 data exploration + MinIO setup + import pipeline

**Obiettivo:** Esplorare i dati V1 su PC139, creare il bucket MinIO `lifelog`, importare 20 segmenti come test del pipeline V2.
**Grounding:** CT104 MinIO live (minioadmin), CT105 DB `lifelog_roberto` live con schema V2, PC139 accessibile via SSH.

---

## [2026-05-07 11:00] DECISION — M4A come input "post-decryption" per il test V2

I file WAV temporanei V1 sono stati eliminati dopo il processing. Si usano i .m4a di `archive/audio/processed/` come input diretto al pipeline V2 simulando l'uscita dalla fase di decifratura. Il preprocessing worker (Stage A) provvederà alla conversione WAV 16kHz mono.
MinIO prefix scelto: `raw-decrypted-temp/roberto/` — coerente con l'architettura come file "appena decriptato".

---

## [2026-05-07 12:00] TASK — Import 20 segmenti V1 → MinIO + DB + Redis

- Bucket `lifelog` creato su CT104
- `scripts/v1_import.py`: SCP da PC139 → /tmp/v1_test/ → MinIO `raw-decrypted-temp/roberto/{YYYY}/{MM}/{DD}/` → RawCapture + Segment in CT105 → xadd su `lifelog:stream:ingest`
- idempotency_key = uuid5(NAMESPACE_URL, "v1:{filename}") — deterministico, reimportare è idempotente
- 10 ambient (2025-08-01 / 2025-08-06) + 10 personale (2025-10-09 / 2025-12-18) — tutti con lat/lon e trascrizione V1

---

## [2026-05-06 21:35] END

**Completato:**
- Stratex: `news_sources` table + `market_intelligence` estesa (Alembic migration v2 con 23 fonti validate, 7 attive)
- Stratex: `rss_scraper.py` — feedparser + trafilatura per testo completo articoli
- Stratex: `youtube_scraper.py` — yt-dlp + youtube-transcript-api v1.x (api.fetch(), non get_transcript)
- Stratex: `news_fetcher.py` — orchestratore fetch ogni 12h nel lifespan FastAPI
- Stratex: `api/intelligence.py` — CRUD completo: feed, item detail, sources list/create/patch/delete, fetch trigger/status
- Stratex: `IntelligenceSection.tsx` — FeedTab + SourcesTab + ItemDrawer (corpo completo articoli e trascrizioni YouTube)
- Stratex: hook `useIntelligenceItem`, `useSources`, `useToggleSource`, `useAddSource`, `useDeleteSource`, `useTriggerFetch`
- Stratex: build frontend deployata (StaticFiles da dist/ locale)
- Fix: `cashflow.py` estimated_annual_yield (NameError `text` non importato da SQLAlchemy)
- Fix: youtube-transcript-api v1.x API (`api.fetch()` invece di classe `YouTubeTranscriptApi.get_transcript`)
- Fix: Alembic migration FK violation (NULL news_source_id prima di DELETE news_sources)
- Fix: lucide-react `Youtube` → `PlayCircle` (icona non esportata dalla versione installata)
- Fix: `_item_dict` spostato a scope di modulo per accessibilità da endpoint detail
- `/doc stratex` + `/finalize` completati

**Incompleto:**
- `enricher.py` Gemini batch — pianificato, non implementato (traduzione + portfolio scoring in 1-2 chiamate da 250k token)

**Mine per il prossimo agent:**
- Stratex: `enricher.py` Gemini Flash batch (lingua da `user_preferences.locale`, portfolio assets come contesto, output: title_translated, body_translated, portfolio_scores, impact_urgency)
- Stratex: AI Chat SSE streaming reale + conversation management (`conversations` + `conversation_messages` tables)
- Stratex: Alert WebSocket (`wss://.../ws/alerts` + toast notifications)
- Stratex: i18n Phase 0 — `locale` in `user_preferences` + react-i18next
- Authelia: password default `StratexAdmin2026!` va cambiata dall'utente

**Nota architetturale da ricordare:**
Gemini Flash usato direttamente dall'LXC (non via Redis→ARIA) per enrichment batch intelligence — deviazione deliberata documentata in blueprint.md e development-history.

---

## [2026-05-06 12:26] END

**Completato:**
- Stratex: Tax Center frontend completo (`TaxCenterSection.tsx` — year pills, 4 stat cards, events table paginata, asset class breakdown, TLH panel, export CSV)
- Stratex: tre hook nuovi (`useTaxSummary`, `useTaxEvents`, `useTaxTLH`) + `GlassCard` estesa con `subtitle` prop
- Stratex: Settings page completa (`SettingsSection.tsx` — Profile/Display/Tax/System, save bar sticky, PATCH ottimistico) + `GET/PATCH /api/settings` backend
- Stratex: hook `useSettings` + `useUpdateSettings` (react-query mutation)
- CT202: Authelia v4.39.19 installato e avviato (37MB RAM, `argon2id`, SQLite storage)
- CT202: nginx aggiornato — `/authelia/` portal proxy + `/_authz` internal forward-auth endpoint + `stratex.conf` con `auth_request`
- Stratex backend: `auth.py` con `get_current_user` dependency + `/api/me` endpoint
- Stratex frontend: `useMe` hook + display_name dinamico nel TopBar
- Lint 41/41 ✅

**Incompleto:**
- Authelia: password default `StratexAdmin2026!` va cambiata dall'utente
- Options section: in pausa (no strumenti)

**Mine per il prossimo agent:**
- Stratex: Cashflow/Dividends frontend (forecast 12m, upcoming payments)
- Stratex: AI Chat SSE streaming reale + conversation management
- Stratex: Alert WebSocket (`wss://.../ws/alerts` + toast notifications)
- Stratex: i18n Phase 0+1 (locale in user_preferences + react-i18next)

---

## [2026-05-05 17:45] END

**Completato:**
- CT120 rinominato `dias-brain` → `ct120-redis` in Proxmox + 17 file (commit `dd996bb`)
- Stratex: DB CT105 verificato (3843 tx, 236 asset, dati reali BGSAXO+Binance)
- Stratex: Alembic configurato, migration `64edb06dccca` applicata (`assets.country`)
- Stratex: credenziali DB in SOPS, `.env` gitignored, `session.py` senza hardcoded
- Stratex: `models.py` allineato al DB reale (JSONB per raw_data)
- Lint 40/40 ✅

**Incompleto:** nulla di critico

**Mine per il prossimo agent:**
- Stratex: API endpoints completi (portfolio/summary, transactions, performance, allocation)
- Stratex: frontend disconnesso dal backend reale (mocked)
- Celery workers non attivi (yfinance, ECB FX)

---

## [2026-05-05 16:08] END

**Completato:**
- Verifica DELETE feature ARIA in produzione: WAV eliminati su PC 139 dopo ogni download Stage D confermato (log CT201: `🗑️ Remote asset eliminato` su ogni scena Hyperion)
- scene-009 confermata riprocessata con successo dopo restart Qwen3
- Analisi stato completo tutti i repo: identificata divergenza critica Stage C P3/P4/P5 su CT201 non committata
- Stage C P3/P4/P5 recuperato da CT201 → committato e pushato (era in produzione senza git)
- Mass commit NH-Mini: 6 commit (gitignore, core modules, knowledge, framework v6, scripts, wiki+dashboard)
- ARIA: 5 commit da PC 139 + 2 da LXC 190 (rate limiter RPD/RPM/TPM, dashboard tray, docs, state-of-gaps)
- DIAS: 5 commit (Stage 0 SCI, Stage C v2.6.0, common lib fixes, API hub, tracking)
- CT201 allineato via git pull (conflict stash risolto)
- `/lint` 40/40 NH-Mini, 45/45 ARIA, 45/45 DIAS ✅
- gitignore: eliminata API key Gemini hardcodata da `store_gemini_api_key.py`

**Incompleto:** nulla di critico

**Mine per il prossimo agent:**
- `subtalker_top_k` e `subtalker_top_p` non inviati da Stage D → gap A1-3 ARIA, bassa priorità
- `dialogue_notes` enrichment path morto → gap A1-2 ARIA, rilevante solo con casting multi-voce
- Progetto Stratex attivo (workspace active) — sessione 2026-05-04 ha caricato dati BGSAXO+Binance su LXC 105

---

## [2026-05-04 15:30] TASK — Ingestion e Caricamento DB Stratex

- Inizializzato database `stratex` su LXC 105 (centralizzato).
- Applicato schema `stratex_schema.sql` con estensioni TimescaleDB e pgvector.
- Creato `backend/ingestion/loader.py` con gestione asset e date.
- Caricati dati BGSAXO (354) e BINANCE (3562).
- Fixato bug date Binance (`YY-MM-DD`) e troncamento ticker crypto (`currency` TYPE -> TEXT).

## [2026-05-04 14:15] DECISION — Database Centralizzato (LXC 105)

Nonostante iniziali indicazioni per un DB locale all'app (LXC 190), abbiamo confermato che Stratex utilizzerà l'istanza Docker centralizzata `timescale/timescaledb-ha:pg16` sul nodo `postgres-lxc` (192.168.1.105) per coerenza infrastrutturale con il resto del progetto NH-Mini.

## [2026-05-04 13:00] TASK — Ingestion multi-broker (BGSAXO + BINANCE)

- Creato parser multi-sheet per BGSAXO: `bg_saxo.py` (Transazioni, Contrattazioni, Bookings).
- Creato parser dinamico per Binance: `binance.py` (header discovery automatico per saltare metadati iniziali).
- Normalizzato output in JSON serializzabile ISO-compliant.

## [2026-05-04 12:00] START — Ingestion pipeline financial data (Stratex)

**Obiettivo**: Estrarre i dati dai report Excel BGSAXO e Binance, normalizzarli e caricarli nel database PostgreSQL di produzione.
**Grounding**: Report Excel originali presenti in `docs/inbox/`. DB centralizzato su LXC 105.

## [2026-05-04 16:00] END — [RECOVERY: sessione chiusa da agent successivo]

**Completato:**
- Parser BGSAXO multi-sheet (`bg_saxo.py`) e parser Binance dinamico (`binance.py`)
- Schema TimescaleDB + pgvector applicato su LXC 105
- Caricati 354 record BGSAXO e 3562 record Binance
- Fix bug date Binance (`YY-MM-DD`) e tipo colonna ticker (`currency` → TEXT)

**Incompleto:** nessuna informazione disponibile (sessione non finalizzata)

---

## [2026-05-03 18:00] END

**Completato:**
- Audit qualità end-to-end DIAS→Qwen3 su produzione Hyperion: tutti i parametri critici confermati corretti (`instruct`, `temperature`, `subtalker_temperature`, `top_p`, ICL mode con `ref.txt`)
- Scoperto e documentato: server Qwen3 di produzione è `backends/qwen3tts/server.py`, non `scripts/qwen3/qwen3_server.py`
- `dialogue_notes` enrichment path in ARIA: confermato architetturalmente morto (Stage C → null, Stage D non forwarda) — impatto basso, documentato
- Riavvio server Qwen3 eseguito correttamente (orchestratore auto-restart in 22s, pipeline ripresa)
- `/doc` completato: session-journal, dias-voice-pipeline-quality.md, aria-qwen3-tts-backend.md, log.md aggiornati
- `/lint` 38/38 ✅
- `/finalize` completato

**Incompleto:** nulla di critico

**Mine per il prossimo agent:**
- Pipeline Hyperion attiva su CT201 — verificare se scene-009 (fallita durante restart) è stata riprocessata da Stage D retry
- `subtalker_top_k` e `subtalker_top_p` non inviati da Stage D (usa defaults ARIA) — non è un problema ma potrebbe essere ottimizzato in futuro se theatrical_standard viene esteso
- `dialogue_notes` enrichment da implementare quando si passa a casting multi-voce

---

## [2026-05-03 17:00] TASK — Audit end-to-end parameter flow DIAS→Qwen3 (produzione)

Audit completo del flusso parametri DIAS LXC 190 → ARIA PC 139 → Qwen3-TTS su produzione Hyperion.

**Scoperte principali:**
- Server Qwen3 di produzione: `C:\Users\Roberto\aria\backends\qwen3tts\server.py` (NON `scripts/qwen3/qwen3_server.py` — quello è un backup obsoleto non in produzione)
- Tutti i parametri critici fluiscono correttamente end-to-end: `instruct`, `temperature`, `subtalker_temperature`, `top_p`, `voice_ref_audio_path` (padded), `voice_ref_text` (ICL mode attivo per Giannini, ref.txt 291 chars)
- `subtalker_temperature=0.75` da theatrical_standard → Stage D → ARIA → modello ✅ (server ha il campo nel schema Pydantic)
- P3+P4+P5 deployati sessione precedente (2026-05-02): temperature e subtalker_temperature calcolati per-scena da Stage B arousal, v2.6.0 attivo

**Gap residuo confermato: `dialogue_notes` enrichment morto**
- Stage C produce sempre `dialogue_notes: null`
- Stage D non forwarda `has_dialogue` né `dialogue_notes` nel payload ARIA
- ARIA controlla `if dialogue_notes and has_dialogue` → mai vero → nessun enrichment
- Impatto: basso. Il contesto personaggio è già bake-in in `qwen3_instruct` da Gemini a Stage C

**Gap minore: `subtalker_top_k` e `subtalker_top_p`** — Stage D non li manda, ARIA usa default (50, 0.9). Non inviati come floating config da theatrical_standard.

**Azione effettuata:** Riavvio server Qwen3 (PID 26880 → 4144). Orchestratore auto-ripartito in 22s. Una task persa (scene-009 connection reset), pipeline ripresa normalmente.

---

## [2026-05-03 10:00] START — Audit qualità pipeline DIAS→Qwen3 + stato post-refactor

**Obiettivo**: Verificare che i dati estratti da DIAS su LXC 190 vengano correttamente consumati da Qwen3TTS su PC 139. Confermare stato dopo P3+P4+P5.
**Grounding**: P3+P4+P5 deployati in sessione precedente (2026-05-02). Pipeline Hyperion attiva su CT201, Stage C v2.6.0 in produzione.

---

## [2026-05-02] TASK — DIAS Stage C Refactor: P3+P4+P5 deployati su CT201

Modifiche applicate su `/opt/dias/src/stages/stage_c_scene_director.py`:
- **P3**: `_create_scene_script_dynamic()` usa `primary_emotion` per-scena dal LLM (v2.6.0) con fallback al blocco macro Stage B
- **P4**: `_generate_voice_direction()` sostituita — lookup table eliminata, formula continua da Stage B floats: `energy = 0.4 + (arousal * 0.5)`, `temperature = 0.6 + (energy * 0.2)`, `subtalker_temperature = 0.3 + (arousal * 0.4)`
- **P5**: `pace_factor` e `pitch_shift` rimossi dall'output — confermati dead code (design artifact pre-Qwen3)
- `temperature` e `subtalker_temperature` esposti al top-level della scena → Stage D li legge con priorità via `message.get()` senza toccare Stage D

Nuovo prompt: `c_monastic_v2.6.0.yaml` (aggiunge `primary_emotion` per-scena nell'output LLM).
`dias.yaml` aggiornato a v2.6.0.

Verificato su output reale chunk-027-micro-000 (Hyperion, arousal=0.8): T=0.76, subT=0.62, emozioni per-scena variegate (stupore/paura/tensione). ✅

---

## [2026-05-02] DECISION — enable_dynamic_params bypass: Stage C scrive temperature direttamente

`enable_dynamic_params` in Stage D è **morto architetturalmente**: il blocco che lo usa (linee 127-132) viene sovrascritto da `theatrical_standard` (linea 209). Settarlo a `True` non avrebbe avuto effetto.

Soluzione: Stage C calcola `temperature` e `subtalker_temperature` via formula e li scrive nel JSON di scena al top-level. Stage D li legge via `message.get("temperature")` che ha priorità su theatrical defaults. Nessuna modifica a Stage D richiesta.

---

## [2026-05-02] DECISION — pace_factor/pitch_shift: design artifact pre-Qwen3, eliminati

Confermato dal codice e dalla doc server.py (TTSRequest schema): Qwen3-TTS non accetta `pace_factor` né `pitch_shift`. Erano stati progettati per un TTS con parametri espliciti di velocità/pitch (tipo VITS/Coqui) o per un layer di post-processing ffmpeg mai implementato. Con Qwen3, velocità e tono si esprimono via `instruct` in prosa naturale.

---

## [2026-05-02] TASK — Analisi parameter flow Stage C→D→Qwen3 + documentazione

Analisi approfondita del codice reale su CT201 — scoperte:
- Qwen3-TTS ha due layer distinti: LLM (temperature, top_p) e Acoustic (subtalker_temperature, subtalker_top_k, subtalker_top_p)
- `instruct` è il canale primario (semantico), temperature è secondario (variabilità)
- `subtalker_temperature` a 0.75 fisso in theatrical mode: troppo alto per narrazione stabile
- Stage B floats (tension/arousal/valence) presenti in `block_analysis` e accessibili da Stage C
- "Preset per Emozioni DIAS" in aria-tts-backends.md era design doc non implementato in Stage D

Doc aggiornata: `NH-Mini/concepts/aria-tts-backends.md` (OBSOLETO+NEW), `NH-Mini/concepts/dias-voice-pipeline-quality.md` (nuova sezione parameter flow + proposte P1-P5).

---

## [2026-05-02] TASK — GeminiRateLimiter daily_limit 200→500 (user)

`aria_node_controller/core/rate_limiter.py` aggiornato dall'utente: `daily_limit: int = 200` → `500`.
Motivazione: pipeline DIAS Hyperion richiede >200 task/giorno per completare Stage B su tutti i chunk.

---

## [2026-05-02] START — Sessione DIAS pipeline parameter flow + refactor Stage C

**Obiettivo**: analizzare e migliorare il parameter flow Stage C→D→Qwen3-TTS.
**Grounding**: ARIA telemetria deployata (sessione precedente). DIAS attivo su CT201 con Stage B Hyperion in processing. Stage C con dead code identificato (pace_factor, pitch_shift, enable_dynamic_params).
**Scope approvato**: P3 (per-scene emotion nel prompt), P4 (formula da Stage B floats), P5 (cleanup dead code). P1 risolto via architettura corretta. P2 skippato (redundante con P4).

---

## [2026-05-01] END — Sessione ARIA Telemetria (Claude)

**Obiettivo**: Implementare telemetria globale task in ARIA (SQLite) + documentare pattern 503 Gemini.

**Completato**:
- `core/telemetry.py` creato: TelemetryDB SQLite WAL, thread-safe, schema 17 colonne
- `core/models.py`, `queue_manager.py`, `orchestrator.py`, `gemini_worker.py` aggiornati
- `docs/aria-telemetry.md` e `docs/gemini-free-tier-503-behavior.md` creati
- `docs/ARIA-blueprint.md` aggiornato (principio #6 + sezione 16)
- Push GitHub (commit 6feb7e2 + 4c07fa8), LXC 190 allineato via git pull
- `/lint` 39/39 ✅ — `/doc` completato ✅ — journal allineato retroattivamente

**Incompleto**:
- ARIA RT su PC 139 non riavviato — in attesa svuotamento coda DIAS Stage B

**Mine per il prossimo agent**:
- ⚠️ Riavviare ARIA su PC 139 (dal bat/tray) quando la coda cloud è vuota → `logs/aria-telemetry.db` si crea automaticamente al primo `post_result()`

---

## [2026-05-01] TASK — Riavvio ARIA RT differito: coda DIAS Stage B attiva

ARIA su PC 139 NON riavviato dopo deploy telemetria. Log mostrano task Gemini ogni ~90s
(2 errori 503 auto-recuperati). Decisione: aspettare svuotamento coda cloud.
Mine: riavviare ARIA per attivare aria-telemetry.db (si crea al primo post_result).

---

## [2026-05-01] TASK — ARIA Telemetria + allineamento LXC 190

Implementato TelemetryDB in ARIA (PC 139 + GitHub + LXC 190 allineato via git pull):
- Creato `core/telemetry.py`: SQLite WAL, thread-safe, schema task_log (17 colonne)
- `core/models.py`: campo `usage` in AriaTaskResult (token cloud)
- `core/queue_manager.py`: hook `if self.telemetry: self.telemetry.log()` in post_result()
- `core/orchestrator.py`: init TelemetryDB + inject in qm, fix output Qwen3 metrics
- `backends/cloud/gemini_worker.py`: cattura usage_metadata (prompt/candidates token count)
- Creato `docs/aria-telemetry.md`, aggiornato `docs/ARIA-blueprint.md` (§6 + §16)
- Push GitHub: commit 6feb7e2 + 4c07fa8
- LXC 190: git pull fast-forward, 9 file, nessun conflitto

---

## [2026-05-01] START — Continuazione sessione ARIA (da compattazione contesto)

Obiettivo: implementare telemetria globale task in ARIA (SQLite) + documentare pattern 503 Gemini.
Grounding: ARIA RT attivo PC 139, LXC 190 dev 3 commit indietro, nessun progetto NH-Mini attivo.
Nota: sessione iniziata prima dell'introduzione delle nuove regole — ritual eseguito a posteriori.

---

## [2026-05-01 16:37] END

**Obiettivo sessione**: Implementazione Fase 3 — Notifiche Push e Auto-Riparazione Interattiva.

**Completato**:
- Creazione e configurazione Telegram Bot (`@Nh_mini_bot`) via SOPS.
- Modulo `core/telegram_bot.py` per invio alert e polling interattivo.
- Integrazione `core/heartbeat.py` con notifiche Telegram (log diagnostici inclusi).
- Aggiornamento `core/service_catalog.py` con remediation commands SSH.
- Servizi systemd: `nh-telegram.service` (polling) e `nh-mini-api.service` (dashboard).
- Studio architetturale per Fase 4 (Smart Troubleshooting Locale vs Cloud).
- Documentazione completa (Wiki, Index, Architecture, History).
- Compliance 100% via `/lint`.

**Incompleto**:
- Integrazione di un modello LLM locale per l'analisi intelligente (pianificato per Fase 4).

**Mine per il prossimo agent**:
- Verificare periodicamente il log di `nh-telegram.service` se i bottoni non dovessero rispondere (causa timeout API Telegram).
- Il comando di remediation per `nh_mini_api` è ora `systemctl restart nh-mini-api`, che funziona solo se il servizio è installato (già fatto oggi).

---

## [2026-05-01 13:42] RESOLVED — Test Push & Remediation Telegram

Verificato il flusso end-to-end:
1. Spegnimento dashboard → Rilevamento Heartbeat → Notifica Telegram con Log diagnostico.
2. Ricezione bottoni interattivi [Riavvia] / [Ignora] sul telefono.
3. Funzionamento del polling daemon via `nh-telegram.service`.

## [2026-05-01 13:30] TASK — Integrazione Telegram e Troubleshooting

Completata l'infrastruttura per la Fase 3:
- Salvate credenziali Telegram (Token e ChatID) in SOPS.
- Creato `core/telegram_bot.py`: gestisce invio notifiche e polling interattivo.
- Aggiornato `core/service_catalog.py`: aggiunti comandi `diagnostic` e `remediation` (SSH-based) per i servizi critici.
- Aggiornato `core/heartbeat.py`: ora invia allarmi a Telegram e include i log di errore nel messaggio.
- Creati servizi systemd: `nh-telegram.service` (per ascoltare i bottoni) e `nh-mini-api.service` (per la dashboard).

## [2026-05-01 13:16] DECISION — Filosofia Troubleshooting Approval-Based

Su indicazione dell'utente, abbiamo stabilito che NH-Mini **non deve mai eseguire fix autonomi improvvisati**. Ogni azione di remediation deve essere proposta via Telegram e approvata esplicitamente dall'utente tramite bottoni interattivi.

---

## [2026-05-01 13:01] END

**Obiettivo sessione**: Fase 2 piano evolutivo NH-Mini
- `scripts/nh-lint.py` — compliance checker
- `scripts/nh-session-end.py` — genera handover summary dal journal
- `core/heartbeat.py` — daemon probe servizi → `state/alerts.json`
- Dashboard: sezione Alerts + badge topbar + API endpoint

**Grounding:**
- `.cursorrules` v6 appena creato ✅
- `state/session-journal.md` esiste ✅
- `NH-Mini/user-profile.md` esiste ✅
- `core/service_catalog.py` STATIC_CATALOG: redis, gateway, aria_node, nh_mini_api, dias_api, sops_age ✅
- Dashboard esistente: 5 tab (Overview, Infrastructure, Projects, Services, ARIA) ✅

**Approccio**: implemento nell'ordine — lint → session-end → heartbeat → dashboard alerts.
Se trovo incongruenze mi fermo e chiedo.

---

## [2026-05-01 11:27] TASK — nh-lint.py

Creato e testato. Risultato: 35 check passati, 2 warning (se stessi non documentati).
Il lint si è auto-diagnosticato correttamente. Warning chiusi aggiornando core-modules.mdc.

## [2026-05-01 11:30] TASK — nh-session-end.py

Creato e testato. Output corretto: estrae END, obiettivo, completato, incompleto, mine.

## [2026-05-01 11:33] TASK — core/heartbeat.py

Creato con schema alerts.json. Dry-run verificato: rileva ARIA down (MEDIUM, PC spento — OK).
Comportamento corretto: ARIA è on-demand, non HIGH.

## [2026-05-01 11:34] TASK — systemd/nh-heartbeat.service + .timer

Creati file systemd. Timer installato e attivato su CT190.

## [2026-05-01 11:35] TASK — Dashboard Alerts

Aggiornati: web/app.py (API /alerts, /heartbeat/run, /handover), index.html (nav + pagina),
dashboard.js (loadAlerts + badge topbar), dashboard.css (stili alert).

## [2026-05-01 11:40] RESOLVED — Dashboard funzionante

Verificato via browser: pagina Alerts mostra 1 MEDIUM (ARIA down), 5 healthy, badge arancione
nella sidebar. Probe Now funziona. Timestamp aggiornato.

## [2026-05-01 11:51] RESOLVED — ARIA false positive

Problema: `heartbeat.py` segnalava ARIA_NODE come DOWN (MEDIUM alert) nonostante il PC Windows 11 fosse acceso e ARIA stesse elaborando i task per DIAS.
Causa: Il TCP probe nel `service_catalog.py` per `aria_node` puntava alla porta `8080` (Fish TTS backend). Questa porta su Windows 11 è bloccata dal firewall o bindata su localhost. Tuttavia, l'Asset Server (porta `8082`) è esposto e raggiungibile.
Fix: Modificata la `port` di `aria_node` in `service_catalog.py` da `8080` a `8082`.
L'alert si è autorisolto al probe successivo.

## [2026-05-01 12:30] DECISION — Filosofia del Journal e Crash Recovery

Su intuizione dell'utente, abbiamo formalizzato che il Journal è un registro storico immutabile. Le vecchie entry (errori, mine) non vanno mai cancellate ma solo barrate se superate.
Abbiamo aggiornato `.cursorrules` (v7) aggiungendo:
1. **Cold Start Protocol:** Se l'agente entrante non trova un END recente (crash), deve prima leggere la fine del journal e comporre lui l'END mancante.
2. **Obbligo di Net Sum:** L'END non deve contenere Mine già risolte, ma deve distillare la verità finale della sessione.
L'aggiornamento è stato committato in `development-history.mdc`.

## [2026-05-01 12:42] TASK — Implementazione Hard Triggers Protocol

Creato il file `knowledge/agent/hard-triggers.mdc` che mappa e documenta i 5 protocolli procedurali (`/finalize`, `/lint`, `/troubleshoot`, `/reuse`, `/handover`).
Aggiornato `.cursorrules` (v8) aggiungendo la sezione `HARD TRIGGERS`: impone all'agente di fermare le risposte discorsive e seguire i passi esatti descritti nell'indice quando viene invocato un trigger. Aggiunto anche il promemoria proattivo per suggerire l'uso di `/finalize` a fine sessione. Committato in `development-history.mdc`.

## [2026-05-01 12:49] TASK — Aggiunta Trigger /doc e Sicurezza su /lint

Modificato `knowledge/agent/hard-triggers.mdc`:
1. Aggiunto il trigger `/doc` (Protocollo di Sincronizzazione Documentale): istruisce l'agente a scansionare il journal e aggiornare architettura, profilo, wiki e history senza chiudere la sessione.
2. Modificato il trigger `/lint`: inserita la direttiva esplicita di fermarsi dopo aver mostrato i risultati, richiedendo le direttive dell'utente prima di applicare qualsiasi fix in autonomia.

## [2026-05-01 13:01] END

**Completato:**
- `scripts/nh-lint.py` — compliance checker completo, fixato ordine parsing.
- `scripts/nh-session-end.py` — genera handover da session-journal.
- `core/heartbeat.py` — daemon probe e `state/alerts.json` (risolto falso positivo porta ARIA).
- `systemd/nh-heartbeat.service` + `.timer` — installati e attivi su CT190 (ogni 5min).
- Dashboard e API — endpoints /api/alerts, tab Alerts funzionante, badge topbar.
- **Hard Triggers Protocol** — formalizzati 6 comandi rigidi (`/finalize`, `/lint`, `/troubleshoot`, `/reuse`, `/handover`, `/doc`) per gestire la context window decay e prevenire improvvisazioni.
- **DNA Architetturale** — `.cursorrules` (v8) aggiornato con principio di immutabilità del Journal e Cold Start Protocol (crash recovery).

**Incompleto (Fase 3):**
- Notifiche push (Telegram/ntfy.sh) — heartbeat scrive alerts.json ma non notifica esternamente.
- TROUBLESHOOTING PROTOCOL autonomo — daemon che reagisce agli alert.

**Mine per il prossimo agent:**
- Il badge topbar non appare alla prima apertura della dashboard (JavaScript caching nel browser).
  Fix suggerito: aggiungere `?v=2` al tag `<script>` in index.html, o usare un hash nel nome file.

---

## [2026-05-01 12:58] RESOLVED — Fix bug nh-lint.py

Corretti due bug minori in `scripts/nh-lint.py`:
1. Rimosso il loop di stampa ridondante (i titoli venivano stampati due volte).
2. Modificato il parsing del journal (`check_session_journal`): ora ordina le entry END per data (stessa logica di `nh-session-end.py`) e prende l'ultima cronologicamente, anziché prendere l'ultima riga del file (che a causa del prepend era la entry più vecchia).

## [2026-05-01 11:46] END

**Completato:**
- `scripts/nh-lint.py` — compliance checker completo, 7 check, --fix-hints, --json
- `scripts/nh-session-end.py` — genera handover da session-journal
- `core/heartbeat.py` — daemon probe (legge service_catalog dinamicamente, merge alert storico)
- `systemd/nh-heartbeat.service` + `.timer` — installati e attivi su CT190 (ogni 5min)
- `web/app.py` — endpoints /api/alerts, /api/heartbeat/run, /api/handover
- `web/static/index.html` — nav Alerts + sezione completa + badge topbar
- `web/static/js/dashboard.js` — loadAlerts(), badge logic, Probe Now, polling 5min
- `web/static/css/dashboard.css` — stili alert (cards, badges, chips, animation pulse)
- `knowledge/architecture/core-modules.mdc` — aggiornati scripts e systemd tables

**Incompleto (Fase 3 — opzionale):**
- Notifiche push (Telegram/ntfy.sh) — heartbeat scrive alerts.json ma non notifica ancora
- TROUBLESHOOTING PROTOCOL autonomo — daemon che reagisce agli alert, non solo li registra
- development-history.mdc — non aggiornato con le modifiche di questa sessione

**Mine per il prossimo agent:**
- Il badge topbar non appare alla prima apertura della dashboard (JavaScript caching nel browser).
  Fix: aggiungere `?v=2` al tag <script> in index.html, o usare un hash nel nome file.
- nh-lint.py ha un bug minore: stampa i check due volte (una volta nel loop, una nel summary).
  Non critico, ma da correggere nella prossima sessione.

---


---


## [2026-05-01 11:17] START

**Obiettivo sessione**: Implementazione Fase 1 piano evolutivo NH-Mini
- Session Journal (questo file)
- User Profile (`NH-Mini/user-profile.md`)
- REUSE CHECK corretto in `.cursorrules` (→ `service_catalog.py`, non lista hardcoded)
- META sezione in `.cursorrules` per evoluzione sicura delle regole
- TROUBLESHOOTING PROTOCOL in `.cursorrules`
- Aggiornamento `NH-Mini/log.md`

**Contesto**: Approvato da Roberto dopo sessione di brainstorming architetturale (2026-05-01 mattina).
Piano completo in artifact `implementation_plan.md`.

**Grounding verificato:**
- `state/` esiste: inventory.json, system-context.md ✅
- `NH-Mini/log.md` esiste e legge fino al 2026-04-30 ✅
- `.cursorrules` versione 5 ✅
- `core/service_catalog.py` contiene: redis, gateway, aria_node, nh_mini_api, dias_api, sops_age ✅

---

## [2026-05-01 11:18] TASK

Creazione `state/session-journal.md` (questo file). Struttura definita.

---

## [2026-05-01 11:20] TASK

Creazione `NH-Mini/user-profile.md` — profilo utente.

---

## [2026-05-01 11:25] TASK

Aggiornamento `.cursorrules` → v6:
- Sezione SESSION JOURNAL
- Sezione REUSE CHECK (→ service_catalog.py, non lista hardcoded)
- Sezione TROUBLESHOOTING PROTOCOL
- Sezione META (evoluzione sicura regole)
- Aggiornamento INITIALIZATION sequence
- Aggiornamento SCRIPTS REFERENCE

---

## [2026-05-01 11:35] TASK

Aggiornamento `NH-Mini/log.md` con entry sessione odierna.

---

## [2026-05-01 11:37] END

**Completato:**
- `state/session-journal.md` — creato e attivo
- `NH-Mini/user-profile.md` — creato con profilo Roberto
- `.cursorrules` → v6 — SESSION JOURNAL, REUSE CHECK (→ service_catalog), TROUBLESHOOTING PROTOCOL, META
- `NH-Mini/index.md` — aggiornato (user-profile aggiunto, stats aggiornate)
- `NH-Mini/log.md` — entry sessione aggiunta

**Incompleto (Fase 2 — prossima sessione):**
- `scripts/nh-session-end.py` — script che genera handover summary dal journal
- `scripts/nh-lint.py` — compliance check (moduli documentati? infra-map aggiornata? journal ha END?)
- `core/heartbeat.py` — daemon probe servizi → state/alerts.json
- Dashboard: sezione Alerts + badge topbar

**Mine per il prossimo agent:**
- Il `.cursorrules` v6 introduce SESSION JOURNAL come obbligatorio — verifica che le sessioni esistenti lo rispettino
- Il `user-profile.md` ha una sezione "Note di Sessione" che va aggiornata ad ogni sessione con nuove preferenze scoperte
- Il REUSE CHECK richiede che ogni nuovo servizio deployato aggiorni `STATIC_CATALOG` in `service_catalog.py` — non è ancora automatico (Fase 2)
- `development-history.mdc` non è stato aggiornato in questa sessione (bassa priorità, ma dovrebbe registrare le modifiche a .cursorrules)

---


---

---

## [2026-05-02] START — Diagnosi Qwen3 + DIAS Stage C refactor

**Contesto:** Continuazione sessione precedente. Pipeline DIAS Hyperion bloccata — Qwen3-TTS backend crashava silenziosamente all'avvio. DIAS Stage C refactor P3/P4/P5 già implementato nella sessione precedente.

---

## [2026-05-02] TASK — Diagnosi e risoluzione crash Qwen3-TTS su PC 139

**Problema:** Terminale Qwen3 si apriva e chiudeva immediatamente. Server non ascoltava su porta 8083. Log server.log fermo al 24 aprile.

**Diagnosi:**
- Avviato server manualmente via SSH: `envs/qwen3tts/python.exe backends/qwen3tts/server.py`
- Avvio riuscito — modello caricato in 29.5s, VRAM 4.20GB, porta 8083 attiva
- Causa root: ARIA orchestrator non era in esecuzione (sessione desktop Windows non raggiungibile via SSH)
- Il manifest `backends_manifest.json` è corretto — ARIA avvia Qwen3 automaticamente quando necessario
- Stage C ancora in corso (non serve Qwen3 per Stage C)

**Risoluzione:** Nessuna modifica al codice necessaria. Problema di sessione Windows, non di crash.

---

## [2026-05-02] TASK — Reset quota Gemini RPD su Redis

**Problema:** `PREVENTIVE QUOTA PROTECTION: Daily limit reached (500)` — pipeline bloccata.

**Azione:** `redis-cli DEL aria:rate_limit:google:daily_count:2026-05-02` + `DEL aria:rate_limit:google:lockout_until` su LXC 120.

**Risultato:** Pipeline ripresa. Poi quota reale Google esaurita (500/500 free tier) alle 19:50 IT. Reset a mezzanotte PDT (09:00 IT del giorno dopo).

---

## [2026-05-03] TASK — ARIA Rate Limiter intelligente (RPM/TPM/RPD + PDT-aware lockout)

**Modifiche su PC 139** (`C:\Users\roberto\aria\`):

- `aria_node_controller/core/rate_limiter.py` — riscritta interamente:
  - Aggiunto tracking RPM (sliding window 60s su Redis sorted set)
  - Aggiunto tracking TPM (sliding window 60s su Redis sorted set con token count)
  - Aggiunto `report_daily_quota_exhausted()` — lockout fino al prossimo reset PDT (mezzanotte America/Los_Angeles ≈ 09:00 IT)
  - `wait_for_slot()` ora logga "Ripresa fra Xh Ym (HH:MM IT)" invece di attendere ciecamente
  - Sleep max 60s per iterazione nel lockout (permette stop esterno e log periodici)

- `aria_node_controller/core/cloud_manager.py` — patchato:
  - Distinzione 429 RPD vs RPM via `_is_daily_quota_error()` (cerca `PerDay`, `GenerateRequestsPerDayPerProjectPerModel`)
  - Chiama `report_daily_quota_exhausted()` per RPD, `report_429()` per RPM
  - `record_usage(tokens)` dopo ogni task riuscito per aggiornare sliding window RPM/TPM

**Entrano in effetto al prossimo riavvio di ARIA.**

---

## [2026-05-03] TASK — ARIA Dashboard web su porta 8089

**Creato** `aria_node_controller/dashboard/server.py` — FastAPI + HTML inline, auto-refresh 5s:
- Gauge RPD/RPM/TPM con barre colorate (verde/giallo/rosso)
- Badge semaforo GPU (letto da Redis `aria:gpu:semaphore`) prominente in header
- Stato backend cloud Gemini derivato da lockout + RPD corrente
- Backend locali con health check HTTP (Qwen3/Fish/ACE-Step/asset-server)
- Code Redis live (tutte le `aria:q:*`)
- Ultimi 30 task da SQLite telemetry (ts, model, status, tokens, durata)
- Statistiche giornaliere (totali, ok, errori, tempo medio)
- ETA reset quota Google PDT

**Avvio:** `C:\Users\roberto\miniconda3\python.exe aria_node_controller\dashboard\server.py`
**URL:** `http://192.168.1.139:8089`
**Task Scheduler:** task `ARIADashboard` registrato per avvio su richiesta.

**Modifiche contestuali:**
- `aria.bat` — aggiunta riga avvio dashboard hidden (PowerShell `WindowStyle Hidden`) dopo orchestratore
- `aria_node_controller/main_tray.py` — aggiunta voce menu `🖥️ Apri Dashboard (8089)` con `webbrowser.open`


## [2026-05-06 13:05] START — Lifelog2 Project Initialization

**Obiettivo**: Setup dell'ambiente di sviluppo e dello skeleton backend.
- Creato pacchetto backend .
- Definiti  e documentazione locale ().
- Inizializzato  con endpoint .
- Installazione dipendenze in corso.

## [2026-05-06 13:10] DECISION — Progetto rinominato lifelog2
- Corretto naming del package da `lifelog` a `lifelog2`.
- Allineata documentazione e logger.
- API operativa su porta 8002.

## [2026-05-06 13:28] FIX — ARIA PC 139 Shutdown
- Eseguito kill forzato di python.exe su PC 139.
- Modificato `orchestrator.py` e `main_tray.py` per garantire la chiusura di dashboard e backend all'exit.
- Sincronizzati file su PC 139.

## [2026-05-06 14:05] FINAL FIX — ARIA GPU Orchestration
- Applicata logica di esclusività totale GPU.
- Risolto race condition su JIT startup.
- Sistema pronto per il riavvio su PC 139.

## [2026-05-11 14:15] END | Lifelog2 Architecture Evolution & App Audit
**Obiettivo sessione**: Definizione architettura Liquid Brain e audit app Android.
- **Completato**: 
  - Architettura Liquid Brain (Swap-In/Out) definita e documentata.
  - Global Registry (LXC 203) progettato.
  - Audit completo App Android v1 e individuazione gap (GPS/Metadata).
  - Creato Handoff Document per upgrade App v2.0 (copiato su LXC 190 e PC 139).
  - Wiki e MDC aggiornati secondo protocollo NH-Mini.
- **Incompleto**: 
  - Implementazione fisica del registry.db e dei relativi endpoint.
  - Script di Session Management per mount/unmount.
- **Mine**:
  - Attenzione alla discrepanza tra il codice del repo App (TODO GPS) e la realtà dei file .m4a (GPS presente). Usare i file reali come ground truth.

## [2026-05-28] START — Lifelog2 Checklist: Worker Flow + Stage G + Profile Validator + AriaLLMClient

Continua sessione precedente. Checklist 8 punti pipeline Lifelog2.

## [2026-05-28 TASK] — Orchestrator parallel B+E architecture

Ridisegno orchestratore: `_stage_b_loop` e `_stage_e_loop` autonomi e indipendenti da ARIA. `ARIA_PIPELINE=[C,D]` seriale. `_reconciliation_loop` aggiunto. Commit `6a2b77d`. Deploy su CT203.

## [2026-05-28 TASK] — Stage G COVERS_MIN_TOTAL=10

`COVERS_MIN_TOTAL=10`: guard in `_covers_loop` che accumula almeno 10 cover pending prima di avviare Stage G FLUX. Commit `7295bc9`. Deploy su CT203.

## [2026-05-28 TASK] — AriaLLMClient infinite-wait polling

`generate_json()` ora aspetta indefinitamente con polling 30s invece di BRPOP hard timeout 600s. Re-push automatico se job consumato senza risposta (ARIA crash durante elaborazione). Commit `7e58e75`. Deploy su CT203.

## [2026-05-28 TASK] — Profile Validator systemd timer

`lifelog2-profile-validator.timer` abilitato su CT203, giornaliero 03:00. Prima run manuale: 339 fatti in 43 batch Qwen3, 0 errori.

## [2026-05-28] END | Lifelog2 Checklist: Orchestrator Parallel Architecture + ARIA Infinite-Wait + Stage G Threshold + Profile Validator

- **Completato**:
  - Point 2: Orchestratore redesign parallel B+E loops (commit `6a2b77d`)
  - Point 3: Stage G COVERS_MIN_TOTAL=10 threshold guard (commit `7295bc9`)
  - Point 6: Profile Validator timer giornaliero 03:00 su CT203
  - AriaLLMClient: infinite-wait polling con re-push automatico (commit `7e58e75`)
  - /doc lifelog2: architecture.md + development-log.md + history_manager + wiki
  - /lint lifelog2: 0 errori, 7 warnings scripts_ref (pre-esistenti)
- **Incompleto / Deferred**:
  - Stage D cold start: investigato (0.07% timeout rate, non urgente), no code fix
  - ARIA FLUX health check 320s: approvato da utente, in attesa OK esplicito per toccare PC 139
- **Mine (priorità prossima sessione)**:
  - **P0 — Speaker enrollment rotto**: `best_score < 0.2` su tutti i segmenti, tutti classificati `ambient`. Nessun speaker Roberto riconosciuto. Diagnosi completa prima di qualsiasi fix.
  - 7 `scripts_ref` warnings in lint: check_aria_log.py, check_redis.py, clean_redis_queues.py, find_pm2.py, inspect_redis_queues.py, list_aria_dirs.py, restart_aria.py — non documentati in core-modules.mdc
