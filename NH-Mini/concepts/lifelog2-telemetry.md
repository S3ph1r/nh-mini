---
title: "Telemetry — Lifelog2"
type: concept
tags: [lifelog2, telemetry, database, sqlite, monitoring, api]
sources: [lifelog2-project-context.md, stack-lifelog2.md]
updated: 2026-06-07
---

# Telemetry — Lifelog2

Il sistema di telemetria di [[entities/systems/stack-lifelog2|Lifelog2]] raccoglie in tempo reale statistiche sull'elaborazione della pipeline, caricamenti audio, latenza delle chiamate verso [[entities/systems/stack-aria|ARIA]] ed eventi di sistema in modo da permettere il monitoraggio completo tramite la Dashboard.

---

## 1. Architettura e Meccanismo di Scrittura

- **Database SQLite dedicato**: Memorizzato in `/opt/Lifelog2/data/telemetry.db` su [[entities/containers/ct203-lifelog|CT203]].
- **Fire-and-Forget**: Le scritture sono asincrone e isolate dall'elaborazione principale. Gli errori di telemetria vengono loggati ma non bloccano mai l'avanzamento dei worker o delle API di ingest.
- **Thread-safe**: Utilizza `asyncio.to_thread` per delegare l'I/O sincrono di SQLite3 su un threadpool dedicato.
- **Auto-migrazioni**: Lo schema e i campi aggiuntivi vengono creati automaticamente alla prima chiamata di scrittura.

---

## 2. Schema del Database (`telemetry.py`)

Il database si articola in 6 tabelle principali:

```
                  ┌───────────────────────┐
                  │     upload_events     │  ◄── Monitoraggio dei caricamenti Android (Z0)
                  └───────────────────────┘
                              │
                  ┌───────────────────────┐
                  │    pipeline_events    │  ◄── Latenza e stato di ogni Stage (B→F)
                  └───────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  grouping_runs  │  │   covers_runs   │  │ daily_snapshots │
│ (Stage F stats) │  │ (Stage G stats) │  │  (Stats storici)│
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                  ┌───────────────────────┐
                  │    service_events     │  ◄── Daemon uptime/errors (orchestrator, digests)
                  └───────────────────────┘
```

### Table: `upload_events`
Registra gli eventi di caricamento dei file audio inviati dai dispositivi autorizzati:
- `id`: Chiave primaria.
- `ts`: Timestamp ISO dell'evento.
- `segment_id`: UUID del segmento associato.
- `user_id`: UUID dell'utente proprietario.
- `filename`: Nome originale del file.
- `audio_source` & `capture_mode`: Sorgente hardware (es. MIC) e modalità (ambient/intentional).
- `file_size_b`: Dimensione del file in byte.
- `started_at` & `ended_at`: Timestamp di inizio/fine della registrazione.
- `duration_s`: Durata effettiva della traccia audio in secondi.
- `lat`, `lon`, `accuracy_m`: Coordinate GPS e precisione del sensore al momento della registrazione.

### Table: `pipeline_events`
Traccia la latenza e lo stato di avanzamento per ciascun segmento all'interno della pipeline (Stage B, C, C1, D, E, F):
- `stage`: Identificativo dello Stage (B/C/C1/D/E/F).
- `segment_id`: UUID del segmento associato.
- `status`: Esito dell'operazione (`ok`, `error`, `reject`, `discarded`).
- `duration_s`: Tempo di elaborazione dello Stage calcolato con precisione tramite `time.perf_counter()`.
- `reason`: Dettaglio testuale in caso di scarto o fallimento (es. `low_snr`, `sparse`).
- `extra` (JSON): Metadati aggiuntivi (es. `aria_wait_s` per misurare il tempo di risposta di ARIA o `e2e_s` per la latenza end-to-end da caricamento a embedding completato).

### Table: `grouping_runs`
Monitora le esecuzioni dello Stage F (Episode Grouping):
- `atoms_processed`: Numero di Memory Atom considerati.
- `episodes_formed`: Numero di episodi creati o estesi.
- `duration_s`: Durata dell'inferenza semantica e di ordinamento.
- `llm_calls`: Numero di chiamate all'LLM (Qwen3).

### Table: `covers_runs`
Traccia il tempo e l'esito della generazione delle copertine (Stage G):
- `episodes_done`: Copertine create.
- `atoms_done`, `places_done`: Risoluzione delle copertine per atomi e luoghi.
- `errors`: Numero di errori GPU o I/O.

### Table: `service_events`
Monitora lo stato di salute dei vari daemon periodici (orchestratore, digest, thread consolidation):
- `service`: Nome del servizio (es. `day_digest`, `thread_consolidation`).
- `event`: Tipo di evento (`started`, `stopped`, `completed`, `failed`).
- `details` (JSON): Metadati o traceback di errore.

### Table: `daily_snapshots`
Tabella aggregata per velocizzare il caricamento della Dashboard:
- `uploads`, `processed`, `rejected`, `episodes`: Conteggi giornalieri.
- `avg_b_s`, `avg_c_s`, `avg_d_s`, `avg_e_s`: Tempi medi di esecuzione dei singoli stadi.

---

## 3. Endpoint API REST (`telemetry.py` router)

FastAPI (su porta `8002` di CT203) espone 6 endpoint per interrogare ed esporre questi dati al frontend SvelteKit:

1. **`GET /telemetry/summary`**: Ritorna le statistiche all-time, le medie storiche per stage, la latenza di rete ARIA (distinta per ASR ed LLM), la latenza E2E, la distribuzione degli `extraction_levels` (full vs contextual) e le modalità di acquisizione dominanti.
2. **`GET /telemetry/stages`**: Ritorna le durate min/max/avg e la P50 approssimata per ciascuno stadio.
3. **`GET /telemetry/recent`**: Ritorna le ultime righe di `pipeline_events` (utilizzato per visualizzare il registro di elaborazione realtime).
4. **`GET /telemetry/uploads/recent`**: Mostra la cronologia degli ultimi file ricevuti.
5. **`GET /telemetry/grouping`**: Mostra lo storico dei run di Stage F.
6. **`GET /telemetry/daily`**: Fornisce il conteggio giornaliero degli upload dell'ultima settimana per i grafici.

---
## Relazioni con altre pagine
- Stack principale: [[entities/systems/stack-lifelog2|Lifelog2]]
- Ingest Pipeline: [[concepts/lifelog2_dev-pattern|Lifelog2 Dev Pattern]]
- Telemetria di Inferenza: [[concepts/aria-telemetry|ARIA Telemetry]]
