---
title: "ARIA Dashboard v2.3 Pro"
type: system
tags: [aria, dashboard, monitoring, python]
sources: [server.py, orchestrator.py]
updated: 2026-05-06
---

# ARIA Dashboard v2.3 Pro

Sistema di monitoraggio e controllo in tempo reale per l'orchestratore ARIA. La versione 2.3 introduce un'architettura asincrona e un sistema di tracking granulare delle performance.

## Architettura Tecnica

- **Backend**: FastAPI + Uvicorn su porta `8089`.
- **Frontend**: Vanilla JS con AJAX polling (2s).
- **Infrastruttura**: Collegata via Redis (192.168.1.120) per heartbeat e telemetria.

## Feature Chiave

### 1. Asynchronous Log Engine
- **Infinite Scrolling**: Caricamento storico dinamico dei log (`aria_orchestrator.log`).
- **Auto-Snap**: Lo scroll rimane ancorato al fondo se l'utente non interagisce, garantendo la visione dei log in tempo reale.
- **Deduplicazione**: Hashing delle righe per prevenire duplicati durante il polling.

### 2. Live Task Tracking
- **Heartbeat (5Hz)**: L'orchestratore invia lo stato ogni 5 secondi.
- **Current Task**: Visualizzazione immediata del `job_id` attualmente in elaborazione per ogni backend (TTS locale e Cloud LLM).

### 3. Metrics Breakdown
Le performance giornaliere sono suddivise in tre categorie logiche:
- **Cloud LLM**: Task verso Google Gemini (RPM/TPM/RPD).
- **Local TTS**: Task verso Qwen3-TTS e Fish-Speech.
- **Audio Engine**: Task verso ACE-Step e AudioCraft.

## Gestione Rete e Conflitti

- **Porta 8089**: Risolto il conflitto con il bridge dell'IDE Antigravity. La dashboard effettua il bind su `0.0.0.0` per essere accessibile dall'esterno della rete (PC 139).
- **Asset Server**: Opera sulla porta `8082` per servire i file WAV generati.

## Shutdown Robusto

Per prevenire processi zombie su Windows, la procedura di uscita segue 5 fasi:
1. Stop CloudManager.
2. Shutdown AI Backends (Taskkill forzato).
3. Terminazione Dashboard Server (Timeout 5s).
4. Stop Asset Server.
5. Chiusura pool Redis + `os._exit(0)`.

## Link Correlati
- [[ct190-nh-mini|LXC 190 (Sviluppo)]]
- [[stack-nhi|NHI Stack]]
