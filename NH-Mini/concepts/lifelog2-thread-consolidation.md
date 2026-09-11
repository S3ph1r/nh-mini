---
title: "Thread Consolidation — Lifelog2"
type: concept
tags: [lifelog2, thread-consolidation, saghe, pipeline, llm, gemini, qwen]
sources: [lifelog2-project-context.md, stack-lifelog2.md, lifelog2-session-digest-2026-09-02-device-channel.md]
updated: 2026-09-02
---

# Thread Consolidation — Stage Z6

Lo **Stage Z6 (Thread Consolidation)** di [[entities/systems/stack-lifelog2|Lifelog2]] è il processo periodico che consolida gli episodi di vita quotidiana (Z3) in saghe, filoni di memoria o "Thread" a lungo termine (Z6). È implementato dal worker `worker_thread_consolidation.py`.

> **Correzione 2026-09-02** (verificato leggendo il codice reale, non riscritto qui
> sotto per storia ricostruibile — vedi `docs/lifelog2-session-digest-2026-09-02-
> device-channel.md` §3): questa pagina descrive l'architettura PRE-migrazione 0022.
> La tabella reale è `sagas` (non `threads`, rinominata dalla stessa migration), e
> l'unità narrativa reale sono i `conversation_threads` (non "memory atoms", tabella
> droppata dalla stessa migration — i prompt Z6 parlano ancora di "episodi" per
> compatibilità semantica, ma l'unità è il thread). L'"esecuzione periodica
> settimanale (la domenica notte)" descritta sotto **non risultava attiva**: la
> tabella `sagas` aveva 0 righe prima di oggi — il worker era dormiente, non
> schedulato attivamente, fino al primo dry-run reale di questa sessione (17
> episodi, 5 saghe create). L'architettura ibrida Cloud/Locale descritta sotto (§1)
> resta invece corretta e confermata dal codice reale.

---

## 1. Architettura Ibrida (Cloud vs Locale)

Il consolidamento richiede la valutazione simultanea di decine di filoni attivi e di un batch di nuovi episodi. Questa operazione richiede una grande finestra di contesto e una forte capacità di ragionamento cross-episodio. 

Per ottimizzare costi, risorse e tempi di inferenza GPU, lo Stage Z6 implementa un approccio **ibrido Cloud/Locale**:

```
[Nuovi Episodi + Saghe Attive]
       │
       ▼
 ┌───────────┐
 │  Pass 1   │ ──► Gemini Cloud (via ARIA Gateway)
 │  Mapping  │     Context Window grande per decisioni in batch (max BATCH_SIZE=15)
 └───────────┘
       │
       ▼ [Mappatura Ricevuta]
 ┌───────────┐
 │  Pass 2   │ ──► Qwen3 Locale (14B su ARIA PC139)
 │ Sintesi   │     Massima privacy per il consolidamento del testo dei ricordi
 └───────────┘
```

1. **Pass 1 — Mapping (Gemini Cloud)**: Utilizza l'API Gemini Cloud (tramite `get_aria_cloud_llm_client()`) per mappare in blocco gli episodi non threaded sui thread esistenti. La grande finestra di contesto di Gemini consente di valutare contemporaneamente l'intero set di saghe attive e decidere per ogni episodio se associarlo ad una saga esistente (`associate`), creare un nuovo filone (`create_new`) o ignorarlo (`ignore`).
2. **Pass 2 — Sintesi (Qwen3 Locale)**: Una volta decise le associazioni, interroga il modello Qwen3-14B locale su ARIA (`get_aria_llm_client()`) per riscrivere ed allineare la narrativa di ciascun thread modificato o creato, aggiornando la timeline, i punti di svolta (*turning points*) e le domande aperte (*open questions*).

---

## 2. Flusso Operativo del Worker

Il worker esegue periodicamente le seguenti fasi:

### Fase 1: Estrazione e Preparazione
- Carica tutte le saghe attive dalla tabella `threads` di PostgreSQL.
- Estrae tutti gli episodi degli ultimi `N` giorni (rolling window, default 30 giorni) e filtra in memoria quelli non ancora associati ad alcun thread.

### Fase 2: Mappatura Decisionale (Batch Mapping)
- Suddivide gli episodi in batch di dimensione massima `BATCH_SIZE = 15`.
- Invia ciascun batch a Gemini Cloud insieme all'elenco delle saghe attive.
- Ottiene in risposta una struttura JSON contenente le associazioni episodio $\rightarrow$ saga.

### Fase 3: Sintesi Narrativa e Aggiornamento
Per ogni Saga che ha ricevuto nuovi episodi, e per ogni nuova Saga da creare:
- Raccoglie tutti gli episodi associati ordinati cronologicamente.
- Recupera dal DB i singoli *memory atoms* sottostanti per fornire al modello evidenze testuali precise (comprese decisioni ed action items).
- Chiama Qwen3 locale con il prompt `stage_z6_synthesis` per generare:
  - Un nuovo titolo e descrizione fluida per la saga.
  - Una `timeline` aggiornata degli eventi chiave.
  - Un elenco strutturato di `turning_points`.
  - Un set di `open_questions` (loop aperti della vita dell'utente).

### Fase 4: Embedding e Persistenza
- Calcola un embedding semantico a 1024 dimensioni della descrizione combinata della saga usando il servizio Ollama su [[entities/containers/ct107-nhi-embeddings|CT107]] con modello `mxbai-embed-large`.
- Esegue l'upsert sicuro su PostgreSQL per aggiornare la tabella `threads` con i nuovi metadati ed il vettore dell'embedding.

---

## 3. Pianificazione e Esecuzione

Il worker è configurato per l'esecuzione periodica settimanale (la domenica notte) gestita tramite timer systemd installati su CT203.

Può anche essere lanciato manualmente per scopi di manutenzione o backfill:
```bash
python -m lifelog2.services.pipeline.worker_thread_consolidation --days 45 --limit 30
```

---
## Relazioni con altre pagine
- Stack di riferimento: [[entities/systems/stack-lifelog2|Lifelog2]]
- Piattaforma di inferenza: [[entities/systems/stack-aria|ARIA]]
- Struttura dei vettori: [[entities/containers/ct107-nhi-embeddings|CT107 Embeddings]]
- **Evoluzione pianificata**: [[concepts/lifelog2-refactor-roadmap]] — FASE 5 aggiunge filtro `data_pool='trusted'` a Z6 per escludere episodi flagged dalle saghe. FASE 4 produce episodi thread-puri che alimentano Z6 con input semanticamente coerenti.
