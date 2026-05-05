---
title: "DIAS Prompt Evolution Registry"
type: source
tags: [dias, prompt, versioni, qualità, lezioni]
sources: []
updated: 2026-04-24
---

# DIAS Prompt Evolution Registry

**File raw:** `sviluppi/dias/docs/prompt-evolution.md`
**Data ingest:** 2026-04-24
**Pagine toccate:** [[concepts/dias-prompt-evolution]]

## Takeaway chiave

- Tutte le versioni di ogni prompt tracciate con rationale — una lezione per ogni bump di versione
- Stage C v2.3 "Monastic": il cambio più importante — divieto assoluto di modificare il testo sorgente ha eliminato il bug delle allucinazioni (cambio pronomi)
- Stage B v1.1 "Mediterranean": ragionamento in italiano + output in inglese — miglioramento qualità sfumature narrative
- Stage B2 v1.0-v3.x archiviati: architettura Warehouse-First con Redis catalog è obsoleta
- Modalità split Director/Engineer: rationale principale = impossibilità strutturale del canonical_id mismatch

## Note di integrazione

- Il documento spiega il "perché" dietro ogni versione — fondamentale per decidere se un nuovo prompt bug richiede bump o hotfix
- Le "Lezioni Trasversali" in fondo al documento sono le più preziose: Mediterranean Prompting, fidelità monastica, esternalizzazione prompt
- Questo file + [[concepts/dias-prompt-evolution]] sono la documentazione completa per il prompt engineering di DIAS
