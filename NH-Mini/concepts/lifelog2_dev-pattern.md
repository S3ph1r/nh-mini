---
title: "Lifelog2 Dev Pattern"
type: concept
tags: [lifelog2, development, api, frontend]
updated: 2026-05-17
---

# Lifelog2 Dev Pattern

Lifelog2 segue un pattern di sviluppo asincrono basato su eventi Redis, persistenza MinIO e frontend SvelteKit in hot-reload su CT203.

## Architettura di Sviluppo

- **API Backend**: FastAPI/uvicorn su porta `8002` (CT203), servizio `lifelog2.service`.
- **Frontend**: SvelteKit + Vite dev su porta `5173` (CT203), servizio `lifelog2-ui.service`. Hot-reload automatico su modifica file.
- **Worker Pipeline**: `lifelog2-orchestrator.service` gestisce subprocess B→E sequential greedy + Stage F ogni 30min + Stage G covers (trigger-only dopo Stage F) + Worker Detective ogni 15min.
- **Object Storage**: Bucket `lifelog` su MinIO (CT104, `192.168.1.104:9000`). Credenziali default: `minioadmin/minioadmin`.
- **Database**: PostgreSQL su CT105 (`192.168.1.105:5432`, DB `lifelog_roberto`, user `lifelog`).
- **Redis**: CT120 (`192.168.1.120:6379`), stream `lifelog:stream:*`, comandi `lifelog:orchestrator:cmd`.

## Workflow Sviluppo Frontend

File locali in `sviluppi/Lifelog2/src/frontend/src/routes/`, sync via `sshpass + scp`:
```bash
sshpass -p 'lifelog_nh2026' scp <file_locale> root@192.168.1.203:<path_remoto>
```
Vite rileva il cambiamento e ricarica automaticamente. Per route nuove: creare directory + `+page.svelte` sia in locale che su CT203.

## Workflow Sviluppo Backend

Stesso pattern scp per `src/backend/lifelog2/`. Dopo modifica router o modelli:
```bash
sshpass -p 'lifelog_nh2026' ssh root@192.168.1.203 "systemctl restart lifelog2.service && sleep 3 && curl -s http://localhost:8002/health"
```

## Pattern API Dashboard

Ogni nuova vista frontend corrisponde a un endpoint in `lifelog2/api/routers/dashboard.py`. Convenzioni:
- Prefix `/dashboard/`
- `get_db` da `lifelog2.api.deps` per session SQLAlchemy async
- MinIO via `lifelog2.core.minio_client.get_minio()` + `asyncio.to_thread` per I/O sincrono
- Formattatori condivisi: `_fmt_time()`, `_fmt_date_label()`, `_fmt_date_key()`, `_duration_label()`

## Pattern Route SvelteKit (Svelte 5 Runes)

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  let data = $state<MyType | null>(null);
  let loading = $state(true);
  const derived = $derived(data?.field ?? []);
  async function load() { /* fetch /api/dashboard/... */ }
  onMount(load);
</script>
```

Proxy Vite: `/api/*` → `http://localhost:8002/*` (configurato in `vite.config.ts`).

## Integrazione NH-Mini

Il servizio è monitorato su CT203. Doc di riferimento: [[stack-lifelog2]].
