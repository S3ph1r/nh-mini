---
title: "Lifelog2 Identity Resolution Design"
type: source
tags: [lifelog2, identity, voiceprint, privacy, pipeline]
sources: []
updated: 2026-05-12
---

# Lifelog2 — Identity Resolution Design

**File raw**: `sviluppi/Lifelog2/docs/lifelog2-identity-resolution-design.md`
**Data ingest**: 2026-05-12
**Pagine toccate**: [[entities/systems/stack-lifelog2|stack-lifelog2]]

## Takeaway chiave

- **Principio fondante**: una persona sbagliata è peggio di una persona sconosciuta. Un errore di identità propaga errori storici in tutti i MemoryAtom passati e futuri.
- **Stack di Certezza 0–3**: Unknown → Candidato LLM → Confermato utente → Enrolled. La transizione 1→2 richiede SEMPRE azione esplicita utente.
- **`identity_candidates` JSONB**: campo append-only dove il LLM scrive suggerimenti (nome, confidence, evidence, source_type). Mai auto-promosso a `first_name`.
- **Back-propagation**: si attiva solo a Livello 2+. Aggiorna SpeakerTurn.person_id e MemoryAtom.entities_json per i turn storici. Non tocca mai summary/title (audit trail).
- **Omonimi**: distinti computazionalmente da person_id diverso e voiceprint diverso. `disambiguation_tag` è solo presentazionale.
- **Display derivato a runtime**: `display_name_for(person)` non è mai cached — calcolato da first_name + last_name + disambiguation_tag.

## Stage D — Estrazione candidati LLM

Il LLM di enrichment produce `speaker_identities` nel JSON di arricchimento:

```json
{
  "speaker_identities": [
    {
      "speaker_label": "SPEAKER_01",
      "candidate_name": "Marco",
      "confidence": 0.87,
      "evidence": "«Dai Marco, smettila!»",
      "source_type": "direct_address"
    }
  ]
}
```

`source_type`: `direct_address` (0.85) | `self_introduction` (0.90) | `third_party_reference` (0.65) | `implied_from_context` (0.40)

## Piano di sviluppo (6 fasi, post-Stage D)

| Fase | Contenuto | Stima |
|------|-----------|-------|
| 1 | Migration 0004 + SQLAlchemy model + Stage C aggiornato | 1 sessione |
| 2 | LLM candidate extraction in Stage D | integrata nello Stage D |
| 3 | API review-queue, confirm-identity, reject-candidate, merge | 1-2 sessioni |
| 4 | `backpropagate_identity()` job standalone | 1 sessione |
| 5 | Display layer frontend (badge certezza, evidence hover, review queue UI) | 2 sessioni |
| 6 | Enrollment-triggered merge (cosine > 0.90 → proposta merge) | 1 sessione |

## Note di integrazione

- Stage D è il prerequisito per le Fasi 1-4 — non avviare prima che Stage D sia operativo.
- `identity_candidates` è append-only — nessun processo automatico può cancellare candidati (audit trail).
- Il `person_id` è immutabile: il nome è solo un'etichetta mutabile sull'UUID. L'aggiornamento del nome si propaga automaticamente in tutte le viste senza back-propagation aggiuntiva.
