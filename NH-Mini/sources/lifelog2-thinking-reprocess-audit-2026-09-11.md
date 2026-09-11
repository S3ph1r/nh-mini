---
title: "Lifelog2 — thinking Qwen3, reprocess generale, audit, riordino documentazione"
type: source
tags: [lifelog2, aria, qwen3, thinking, reprocess, audit, identity, documentazione]
sources: []
updated: 2026-09-11
---

# Lifelog2 — thinking Qwen3, reprocess generale, audit, riordino documentazione

**File raw**: sessione di sviluppo 2026-09-08 → 2026-09-11 (Claude Remote Control),
documentata in dettaglio in `sviluppi/Lifelog2/docs/lifelog2-session-log.md`.
**Data ingest**: 2026-09-11
**Pagine toccate**: [[stack-lifelog2]], [[stack-aria]]

## Takeaway chiave

- Il wrapper ARIA per `qwen3-14b-q4km` è stato ridisegnato (contesto 32768, profili
  thinking/non_thinking, `reasoning_budget_tokens` vero) e `thinking=True` è ora cablato
  su tutti i worker Lifelog2 che chiamano Qwen3, con un budget condiviso che divide
  correttamente prompt + tabella + riserva di reasoning + risposta.
- Il reprocess generale del corpus (11659 turni, 671 thread) ha confermato **risolti**,
  sui dati reali, i due problemi più vecchi e più citati negli audit precedenti: la coda
  tabella persa su thread lunghi in Stage D, e l'attribuzione scambiata in Stage E.
- La **formazione del ricordo** (ingest → identità → arricchimento → embedding → cover,
  "A→G") è la metà matura del progetto — solo 4 problemi aperti, nessuno grave. I
  **worker secondari** (identità/luoghi/digest/profilo) sono ineguali: alcuni dormienti
  da settimane, i digest week/month/year narrativi non esistono affatto (solo il day
  digest e metriche settimanali pure-SQL).
- Valutazione esplicita di avanzamento: se "finito" è la visione completa del blueprint
  originale, il progetto è a metà — se è "cattura + organizza in thread interrogabili con
  identità", quello c'è già. Conteggio onesto: 9-10 voci tra problemi aperti, sistemi da
  completare/verificare, e sistemi da costruire da zero.
- La documentazione di progetto (`docs/README.md`, `knowledge/*.md`) era rimasta indietro
  di settimane rispetto al ritmo di sviluppo — riordinata in questa sessione, e sono stati
  introdotti due nuovi artefatti pensati per non farla ristagnare di nuovo: un log per
  sessione di sviluppo e una valutazione di avanzamento con conteggio esplicito.

## Note di integrazione

- Priorità indicate per il prossimo giro di lavoro (nell'ordine): verificare se il modello
  rispetta il marcatore di non-citabilità `~` (rischio di fatti inventati su fino al ~45%
  dei turni HIGH se non lo rispetta); riprogettare la catena identità (Z7 solo clustering,
  identity_detective proprietario del giudizio reale-vs-media via reciprocità); dare al
  detective un modo sano di processare thread molto lunghi (bucket per volume, non
  sliding window).
- Nessuna azione richiesta su NH-Mini/infrastruttura condivisa — lavoro interamente dentro
  `sviluppi/Lifelog2/` e `sviluppi/ARIA/`.
