---
title: "Lifelog2 — Roadmap Segnali e Statistica di Lungo Periodo"
type: concept
tags: [lifelog2, roadmap, signal-class, metriche, retention, profilo, z5]
sources: []
updated: 2026-07-18
---

# Lifelog2 — Roadmap Segnali e Statistica di Lungo Periodo

Distillato dall'intervista strutturata 2026-07-17 con Roberto (trascrizione completa:
`workspace/lifelog2-signal-roadmap-interview.md`). Nasce dall'audit di grounding sui
turni/thread dello stesso giorno: 90% dei 943 thread è "counted" (solo statistica), 10%
significativo, ~3% prezioso — la domanda diventa come far fruttare quel 90%.

## Cornice concettuale

Due regimi con fisica diversa:
- **Evento** (ora/giorno): l'errore del singolo turno pesa per intero, valore deperibile
  (un impegno, una decisione). Qui vive il journaling/promemoria.
- **Accumulo** (settimane/mesi/anni): l'errore casuale si media a zero da solo; contano
  solo i bias sistematici (identità, leak media→personale, date sbagliate — tutti
  bonificati nell'hardening del 13-17/07). Qui vive il profilo e la derivata nel tempo.

Principio: nessun thread esce a mani vuote — o gradua al semantico (pochi) o versa nella
statistica (tutti). LLM ai bordi, aggregazione statistica nel mezzo.

## Direzione decisa

**Statistica come fondazione silenziosa, azione come prodotto visibile.** La baseline
accumula da subito in background (ogni settimana persa è storia irrecuperabile); il
lavoro visibile nei prossimi mesi resta su impegni/promemoria affidabili. Ogni
automazione tocca solo lo strato silenzioso — tutto ciò che è visibile all'utente
(nome di una persona, notifiche, cancellazioni fisiche) resta conferma esplicita.

## Fase 0 — ✅ IMPLEMENTATA 2026-07-18 (fondazione silenziosa, zero LLM, retroattiva)
1. **signal_class deterministico** (actionable/contestuale/statistica) da campi già
   estratti — UPDATE retroattivo su tutto lo storico. **Fatto**: migration 0032,
   backfill 46 actionable / 73 contextual / 824 statistical su 943 thread. Prima
   superficie UI: badge + filtro nella grid Threads, chip nella pagina Day.
2. **Metriche settimanali materializzate**, tutte e 4 le famiglie: tempo/presenza,
   sociale, contenuto, produttività+qualità pipeline. **Fatto**: tabella
   `weekly_metrics`, worker giornaliero (`--since-weeks 4`), 3 settimane storiche
   popolate. Prima UI: card "Andamento settimanale" in Profile.
3. **Cluster vp ricorrenti silenziosi** — **disegno iniziale rivisto in corsa**: una
   tabella `vp_recurrence` basata su match di stringa `vp_stable_id` tra settimane
   si è rivelata strutturalmente impossibile (`SESSION_GAP_MIN=30min` in
   `stage_c1_gate.py` rende il vp scope-di-sessione, mai persistente — 0 cluster
   su 866 vp testati). Rimossa prima del deploy (migration 0033). Il meccanismo
   corretto esisteva già: Z7 (`worker_profile_builder.run_social_clustering`) fonde
   i cluster cross-sessione via centroide d'embedding — `weekly_metrics.
   recurring_vps_seen` si appoggia al `person_id` che Z7 risolve, invece di
   reinventare il clustering.

## Fase 1 — Rifinitura ibrida (incrementale)
4. Stage E **promote-only** sul signal_class (mai declassa), motivo sempre loggato —
   per misurare quanto/quando l'LLM vede valore oltre la regola.
5. **Evidence recency-weighted** sui fatti profilo (decadimento temporale, non solo
   contatore).

## Fase 2 — Narrativa di lungo respiro (gated su storia sufficiente)
6. **Z5 week/month review**: stesso pattern del Day Digest (map-reduce, prompt
   versionato, grounding rigoroso) sopra le metriche aggregate.
7. Riapertura **alert/deviazioni** — deliberatamente rimandata a quando Z5 esiste e
   c'è abbastanza baseline da giudicare cosa è "normale".

## Fuori sequenza — Storage m4a (non è una fase dei segnali, è manutenzione infra)
Innescato dallo spazio libero reale su disco, non dal calendario:
- Marcatura "per l'oblio" degli m4a oltre N mesi (nessuna cancellazione finché c'è spazio)
- Tasto "svuota cestino" in dashboard, attivabile sotto soglia 30-40% spazio libero
- Cancellazione fisica SOLO su azione utente esplicita; playback su turno evitto →
  errore gestito, non crash
- **Dato di realtà**: DB Postgres = 38MB totali dopo ~2000 segmenti (speaker_turns con
  embedding incluso: 13MB) — testo/JSON/record non sono mai un problema di spazio per
  mesi/anni; il costo vero è tutto negli m4a.

## Principio trasversale
Ogni componente ibrido logga il motivo quando devia dal default deterministico — unico
modo per decidere con evidenza, non a sensazione, se un livello più caro vale il costo.

## Vedi anche
- [[concepts/lifelog2-tier2-alignment-roadmap]] — migrazione Tier2 che rende possibile
  questa fase (thread-native, campi già estratti)
- `sviluppi/Lifelog2/docs/lifelog2-status-roadmap.md` — stato tecnico Tier1/Tier2
- `workspace/lifelog2-signal-roadmap-interview.md` — trascrizione completa dell'intervista
