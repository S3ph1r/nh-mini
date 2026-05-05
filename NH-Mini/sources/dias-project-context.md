---
title: "DIAS — .project-context"
type: source
tags: [dias, project-context, architettura]
sources: []
updated: 2026-04-24
---

# DIAS — .project-context

**File raw:** `sviluppi/dias/.project-context`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[entities/systems/stack-dias]], [[concepts/dias-pipeline]]

## Takeaway chiave

- DIAS = "Regista" (segmentazione, istruzioni stilistiche) che delega la generazione ad ARIA su GPU remota
- Pipeline a 7 stadi (A-G) strettamente sequenziale
- Nodi: Brain (LXC 190), Infrastructure (Redis LXC 120), Worker (ARIA PC 139)
- Fase attuale: `production_testing` — validazione massiva 503 scene su ARIA
- Constraint principale: quota Gemini (1000 chiamate/giorno) e disponibilità GPU ARIA

## Note di integrazione

- Lo stage D è `VoiceGenProxy` nel .project-context ma corrisponde a Stage D nel blueprint — il blueprint (v7.0) è più aggiornato e autorevole
- La priorità attuale è Stage E (MusicGen → rimpiazzato da ACE-Step nel blueprint v7.0)
- Il .project-context non è aggiornato alla v7.0 del blueprint — preferire il blueprint per le specifiche correnti
