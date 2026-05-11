---
title: "ARIA Asset Server"
type: concept
tags: [aria, http, networking, storage]
sources: [orchestrator.py]
updated: 2026-05-06
---

# ARIA Asset Server

L'Asset Server è un micro-servizio HTTP integrato nell'orchestratore ARIA che permette ai client (come DIAS) di accedere istantaneamente ai file audio prodotti senza dover accedere direttamente al file system del PC 139.

## Funzionamento
Il server gira sulla porta **8082** e mappa una sottocartella specifica della root di ARIA verso l'esterno.

### Mappatura Percorsi
- **Cartella Fisica**: `%ARIA_ROOT%\data\outputs\`
- **URL Base**: `http://192.168.1.139:8082/`

Esempio:
Un file salvato in `C:\Users\Roberto\aria\data\outputs\scene-001.wav` diventa accessibile via web a `http://192.168.1.139:8082/scene-001.wav`.

## Architettura
- **Tecnologia**: Basato su `http.server.SimpleHTTPRequestHandler` di Python.
- **Concorrenza**: Gira in un thread dedicato (`daemon=True`) gestito dall'orchestratore.
- **Ciclo di vita**: Viene avviato all'init di ARIA e spento durante il [Robust Shutdown]([[concepts/aria-shutdown-protocol]]).

## Sicurezza
- Il server è configurato in **sola lettura**.
- È accessibile solo all'interno della LAN (192.168.1.0/24).
- Non supporta l'esecuzione di script (CGI disabilitato).

## Consumatori
- **DIAS**: Scarica i WAV per il mixaggio finale delle scene.
- **Dashboard**: Usa il server per permettere il play-test dei log direttamente dall'interfaccia web.

## Vedi anche
- [[entities/systems/stack-aria]]
- [[concepts/aria-task-lifecycle]]
