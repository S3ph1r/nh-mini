---
title: "DIAS Pipeline Dashboard & Orchestration"
type: entity
tags: [dias, pipeline, orchestration, sound-design]
sources: [overview.md]
updated: 2026-05-09
---

# DIAS Stack

Sistema di orchestrazione e visualizzazione per la produzione massiva di audiolibri (Radiofilm).

## Caratteristiche Principali

- **Orchestratore Seriale**: Gestisce la sequenza degli stadi (A-F) con monitoraggio real-time via Redis.
- **Dashboard Svelte 5**: Interfaccia premium con visualizzazione live del progresso, controllo pausa/resume e ispezione asset.
- **Infinite Scroll**: Implementato per gestire cataloghi massivi (>7000 file) senza degradazione delle performance.
- **Pausa Manuale**: Sistema di sospensione pulita della pipeline che garantisce l'atomicità dei file in corso.

## Architettura

- **LXC 201**: Nodo di runtime (Production).
- **Backend**: FastAPI (Python 3.12).
- **Frontend**: Svelte 5 (Vite + Tailwind).
- **Orchestration**: Redis (pub/sub + keyspace events per SSE).

## Ottimizzazioni Recenti (2026-05-09)

- **Heartbeat 5s**: Ridotto il loop di monitoraggio da 30s a 5s per una reattività immediata ai comandi.
- **Pause Consistency**: Estesa la logica di pausa a tutti i worker (Stage D2, E, F) e all'orchestratore globale.
- **Tab Contextualization**: Il carosello delle voci è ora limitato al tab di Pre-produzione.
- **Relocation**: Spostato il pulsante "Salva Pre-produzione" in alto per migliore accessibilità.

## Link Interni
- [[ct201-dias-rt]]
- [[stage-details]]
- [[pipeline-orchestration]]
