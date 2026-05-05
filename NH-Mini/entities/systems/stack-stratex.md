---
title: "Stack — Stratex"
type: entity
tags: [system, finance, ai, strategy]
sources: [stratex-blueprint.md]
updated: 2026-05-04
---

# Stratex — Wealth Intelligence System

Stratex è un sistema personale di gestione patrimoniale e intelligence finanziaria che utilizza un approccio AI ibrido. È progettato per aggregare asset da broker, crypto exchange e banche, fornendo analisi avanzate e suggerimenti strategici.

## Architettura

Il sistema segue il pattern di separazione fisica di NH-Mini:
- **LXC 190 (NH-Mini)**: Ospita il backend (FastAPI), il database (PostgreSQL + TimescaleDB), i worker Celery e la dashboard React.
- **Nodo GPU (PC 139)**: Gestisce l'inferenza AI (LLM, Embedding, Sentiment) tramite code Redis.

## Componenti Principali

1. **Ingestion Engine**: Automatizza l'importazione di CSV/PDF dai broker usando agenti AI per mappare nuovi formati.
2. **Market Intelligence**: Scraping di news, Reddit, SEC e YouTube con analisi del sentiment e indicizzazione vettoriale (pgvector).
3. **RAG Engine**: Sistema di Retrieval-Augmented Generation per interrogare i dati di mercato e il portafoglio.
4. **Tax & Yield**: Moduli per il calcolo dell'efficienza fiscale (Tax-Loss Harvesting) e previsione dividendi.

## Relazioni

- **Dipende da**: [[stack-aria]] (per l'inferenza AI via Redis).
- **Gira su**: [[ct190-nh-mini]] (durante la fase di sviluppo).
- **Utilizza**: [[ct105-postgres]] (come riferimento per pattern DB, sebbene usi un'istanza locale dedicata).

## Stato Sviluppo

- **Fase**: Inizializzazione.
- **Prossimi Passi**: Setup dello schema database PostgreSQL + TimescaleDB e implementazione del primo parser di ingestion.
