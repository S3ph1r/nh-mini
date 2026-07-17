---
title: "Lifelog2 — Places Intelligence"
type: concept
tags: [lifelog2, places, GPS, intelligence, detective, pipeline]
sources: [stack-lifelog2.md, lifelog2-places-intelligence-spec-v1.md]
updated: 2026-05-27
---

# Places Intelligence — Lifelog2

Feature di apprendimento automatico dei luoghi frequentati dall'utente, basata su segnali multi-dimensionali accumulati nel tempo. Modello concettuale: stesso paradigma del [[concepts/lifelog2_dev-pattern|Detective worker]] per l'identità delle persone, applicato ai luoghi.

**Spec tecnica completa**: `sviluppi/Lifelog2/docs/lifelog2-places-intelligence-spec-v1.md`  
**Stato**: Fase 0–4 live (2026-05-27) — Fase 5 (Stage D context) pending

---

## Obiettivo

Il sistema deve capire nel tempo **cosa rappresenta ogni luogo** nella vita dell'utente — non solo la posizione geografica, ma il ruolo semantico: casa, ufficio, luoghi sociali ricorrenti. Ogni ipotesi è presentata con gli indizi che la supportano; l'utente conferma o rifiuta.

---

## Fondamenta già presenti

| Componente | Stato |
|-----------|-------|
| `raw_captures.lat/lon/accuracy_m` | ✅ live — GPS salvato ad ogni upload |
| `places` table con geocoding Nominatim | ✅ live — Stage F popola via find_or_create_place() |
| `memory_atoms.location_id → places` | ✅ live — Stage F assegna dopo grouping |
| `places.place_type` (home/work/transit/public/unknown) | ✅ parziale — mapping statico da tag OSM |
| [[entities/systems/stack-lifelog2\|stack-lifelog2]] Day Digest legge `places_visited` | ✅ live |

**Limitazione attuale**: GPS inviato solo su ~13% dei segmenti. Fix app Android eseguito 2026-05-27 — occorrono 2+ settimane per avere dati sufficienti al Place Detective.

---

## Segnali usati per l'inferenza

Il sistema aggrega per ogni luogo (tramite `location_id`):

| Segnale | Peso |
|---------|------|
| Ora del giorno (pattern tipico) | Alto |
| Giorno della settimana | Alto |
| Voiceprint ricorrenti (chi parla lì) | Alto |
| Frequenza e regolarità delle visite | Alto |
| `capture_class` distribution (personal/ambient/mixed) | Medio |
| Topic dominanti nei memory atom | Medio |
| Durata media per visita | Medio |

---

## Architettura

```
GPS raw_captures
  └─► Stage F: geocoding → places → location_id
         │
         ▼
  place_signals (materialized view)
  [visit_count, total_minutes, hour_histogram, dow_histogram,
   capture_class_dist, top_topics, frequent_persons]
         │
         ▼
  Worker Place Detective (domenica 03:30)
  [scoring home/work/social/transit per place]
         │
         ▼
  place_hypotheses (pending → confirmed/rejected)
         │
    ┌────┴────────────────────┐
    ▼                         ▼
  Stage G: cover image    Stage D: context "location: home"
  per places confermati   nel prompt Qwen3
    │
    ▼
  /places dashboard
  [mappa cluster + tiles Netflix + detail panel]
```

---

## Struttura dati nuova

**Nuove colonne su `places`:**
- `visit_count`, `total_minutes_spent` — aggiornati da Stage F
- `cover_image_key` — generato da Stage G quando place confermato
- `confirmed_type`, `confirmed_name`, `confirmed_at` — dopo conferma utente

**Nuova tabella `place_hypotheses`:**
- `suggested_type`, `confidence`, `evidence` (JSONB lista stringhe)
- `top_topics`, `frequent_persons`, `hour_histogram`, `dow_histogram`
- `status`: pending → confirmed | rejected

---

## Vista frontend `/places`

**Layout a tre zone:**
1. **Mappa Leaflet** (40% height) — cluster markers colorati per place_type, radius = log(visit_count)
2. **Top Places tiles** (scroll orizzontale, stile Netflix) — cover image AI-generated, stats, evidence, badge tipo+confidenza
3. **Detail panel** (slide-in) — mini-mappa, istogrammi ora/DOW, atom timeline, form conferma

**Tile design:** immagine evocativa generata da Flux2 (stesso Stage G degli episodi), con overlay gradient e statistiche chiave (visite, ore totali, persone ricorrenti, topic).

---

## Cosa NON fa

- Non usa il cambio di location come confine di episodio (una conversazione in auto resta un episodio unico)
- Non inferisce identità da posizione ("questa voce a casa → è il partner") — il Detective usa la voce, non il luogo
- Non reverse-geocoda ogni segmento (rispetta rate limit Nominatim 1 req/sec)
- Non mostra coordinate GPS precise in UI — solo nome del luogo

---

## Roadmap in 5 fasi

| Fase | Contenuto | Stato |
|------|-----------|-------|
| 0 | DB migration + Stage F contatori + place_signals view | ✅ live |
| 1 | Worker place_detective.py | ✅ live |
| 2 | Stage G cover per places | ✅ live |
| 3 | API endpoints backend | ✅ live |
| 4 | Frontend /places | ✅ live |
| 5 | Stage D context integration | 🔲 pending |

**Prerequisito bloccante**: 2+ settimane di dati GPS continui (dal fix app 2026-05-27).

---

## Link correlati

- [[concepts/lifelog2_dev-pattern]] — pattern dev Lifelog2 (orchestrator, Stage F, MinIO)
- [[entities/systems/stack-lifelog2]] — sistema completo Lifelog2
- [[entities/services/service-asr-blackwell]] — voiceprint che alimenta il segnale persone-per-luogo
