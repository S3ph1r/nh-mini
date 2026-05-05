---
title: "DIAS Pre-production Guide"
type: source
tags: [dias, preproduction, stage0, dashboard, casting]
sources: []
updated: 2026-04-24
---

# DIAS Pre-production Guide

**File raw:** `sviluppi/dias/docs/preproduction-guide.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/dias-stage0-preproduction]], [[concepts/dias-pipeline]]

## Takeaway chiave

- Struttura project-centric: `data/projects/{project_id}/` — ogni libro è una sandbox isolata
- Stage 0.1: `fingerprint.json` con Chapter Map + Stylistic Markers (toggle_paragraph vs enclosed_pair)
- Stage 0.2: `preproduction.json` con Character Bible + 3 palette sonore — fonte autoritativa per Speaker ID di Stage C
- Dashboard: 3D Cyber-Ring Carousel (Global Voice), Casting Table (per personaggio), Atmosphere Selection
- Il `preproduction.json` diventa contratto definitivo dopo il click "💾 Salva Dossier"
- Logica precedenza vocale Stage D: Casting personaggio > Global Voice > Default (`luca`)

## Note di integrazione

- La Global Voice può essere configurata prima del completamento di Stage 0 — non bloccante
- Per libri >800k caratteri: Sequential Contextual Injection in blocchi da ~400k con Summary preamble
- Il pulsante "Salva Dossier" è il punto di handoff tra il regista umano e la pipeline automatica
