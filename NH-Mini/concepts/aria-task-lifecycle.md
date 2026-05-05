---
title: "ARIA — Ciclo di Vita di un Task"
type: concept
tags: [aria, task, redis, lifecycle, stati]
sources: [aria-blueprint.md]
updated: 2026-04-24
---

# ARIA — Ciclo di Vita di un Task

Descrizione degli stati e delle transizioni di un task ARIA dall'invio al consumo.

## Stati

```
CREATED → QUEUED → PROCESSING → DONE
                              → FAILED → RETRY → QUEUED
                                       → DEAD LETTER
```

| Stato | Descrizione |
|-------|-------------|
| CREATED | `submit_task()` chiamato dal client |
| QUEUED | Task in Redis (`LPUSH` sulla coda), job_id restituito al client |
| PROCESSING | ARIA ha preso il task (`BRPOP`), inferenza in corso |
| DONE | Inferenza completata, risultato in `aria:c:{client_id}:{job_id}` |
| FAILED | Errore durante l'inferenza |
| RETRY | Rimesso in coda con payload modificato (max 2 retry di default) |
| DEAD LETTER | Timeout scaduto o retry esauriti |

## Transizioni Speciali

### QUEUED → DEAD LETTER (timeout)
Il Dead Letter Handler del client monitora i task in coda. Se `now - queued_at > timeout_seconds` → dead letter.

### PROCESSING → QUEUED (crash recovery)
All'avvio di ARIA Server, controlla `aria:processing:*`. Task trovati in processing (da crash precedente) → rimessi in coda. **Zero perdita di task garantita.**

### QUEUED → QUEUED (semaforo RED)
Il task resta in coda silenziosamente. Non c'è timeout durante il semaforo RED — il timeout è relativo alla creazione, non all'inizio dell'esecuzione.

## Scenari Tipici

### Scenario normale (GPU disponibile)
```
t=0s   submit_task() → job_id restituito in <100ms
t=1s   ARIA preleva il task, carica modello
t=70s  inferenza completata → url in redis
t=70s  Watcher client: trova risultato, aggiorna pipeline
```

### Semaforo RED (utente sta giocando)
```
t=0s   ARIA finisce il task corrente
       semaforo RED → non consuma nuovi task
       task successivi si accumulano in coda
t+2h   utente finisce di giocare → semaforo GREEN
       ARIA riprende dalla coda senza perdere nulla
```

### PC gaming spento
```
t=0s   submit_task() → task in Redis OK (Redis è su LXC 120, sempre attivo)
t..8h  nessun heartbeat — client log: "server OFFLINE"
t+8h   PC gaming si accende → ARIA avvia, trova task in coda → esegue
```

### OOM durante inferenza
```
ARIA: torch.cuda.OutOfMemoryError
      → risultato con status="error", error_code="OOM"
      → torch.cuda.empty_cache()
      → rimette task in coda con payload ridotto (qualità/risoluzione)
      → retry_count++
      → dopo max_retries: dead letter
```

## Vedi anche

- [[concepts/aria-redis-protocol]] — nomenclatura code e schema payload
- [[stack-aria]] — sistema ARIA completo
- [[ct120-dias-brain]] — Redis infrastructure node (LXC 120)
