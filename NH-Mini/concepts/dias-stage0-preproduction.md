---
title: "DIAS — Stage 0 Intelligence & Pre-production"
type: concept
tags: [dias, stage0, preproduction, casting, dashboard, gemini]
sources: [dias-preproduction-guide.md, dias-blueprint.md]
updated: 2026-04-24
---

# DIAS — Stage 0 Intelligence & Pre-production

Stage 0 è il "Cervello Preventivo" di DIAS: analizza il libro in anticipo per estrarre struttura e DNA artistico. I suoi output guidano tutti gli stage successivi.

## Due Sotto-Protocolli

### Stage 0.1 — Discovery ("La Scansione Ossea")

- **Input**: libro `.epub`/`.txt`
- **Prompt**: `0.1_discovery_v1.2.yaml`
- **Output**: `fingerprint.json`

Contenuto del `fingerprint.json`:
- **Chapter Map**: ID e nomi dei capitoli (necessario per Stage A)
- **Stylistic Markers**: simboli dialogo (em-dash vs virgolette, `toggle_paragraph` vs `enclosed_pair`)

### Stage 0.2 — Intelligence ("L'Anima del Libro")

- **Input**: struttura da 0.1 + contenuto libro
- **Prompt**: `0.2_intelligence_v1.0.yaml`
- **Output**: `preproduction.json`

Contenuto del `preproduction.json`:
- **Character Bible**: lista esaustiva personaggi (Primary/Secondary/Tactical) con profili vocali (età, sesso, timbro). È la fonte autoritativa per gli Speaker ID di Stage C.
- **Sound Design Palette**: 3 proposte di mood sonoro per la Dashboard.

## Dashboard "Digital Director"

L'interfaccia utente di DIAS (su [[ct201-dias-rt]]) per la fase di pre-produzione:

### Componenti Dashboard

| Componente | Funzione |
|-----------|---------|
| **3D Cyber-Ring Carousel** | Selezione Global Voice con rotazione 3D e anteprime audio. Voci caricate dal Registry ARIA (Redis 120). |
| **Casting Table** | Assegnazione manuale doppiatori per ogni personaggio rilevato da Stage 0.2 |
| **Atmosphere Selection** | Scelta del mood sonoro tra le 3 palette proposte |
| **💾 Salva Dossier** | Scrive le scelte definitive in `preproduction.json` — pulsante critico |

### Logica Precedenza Vocale (Stage D)

Gerarchia di risoluzione della voce per ogni scena:

1. **Casting personaggio** — voce assegnata in Casting Table → massima priorità
2. **Global Voice** — dal carosello 3D (per narrazione e personaggi non mappati)
3. **System Default** — `luca` (narratore standard)

Il `preproduction.json` diventa il **contratto definitivo** per Stage D dopo il salvataggio dal utente.

## Struttura Directory Progetto

```
data/projects/{project_id}/
  source/          ← PDF originale + .txt estratto
  stages/          ← output intermedi per stage
  logs/            ← log analisi LLM per questo progetto
  final/           ← audio e JSON pronti
  fingerprint.json ← Stage 0.1
  preproduction.json ← Stage 0.2 (aggiornato dalla Dashboard)
```

## Note Tecniche

### Libri Grandi (>800k caratteri)
Strategia **Sequential Contextual Injection**:
- Divisione in blocchi da ~400k gestiti in modo ricorsivo
- Ogni blocco riceve il `Summary` e il JSON dei blocchi precedenti come "Preamble"
- Validato su "Hyperion" con patch di pausa 60s per rispettare i limiti TPM Gemini

### Stage 0 e Stage C
I profili dei personaggi definiti in 0.2 vengono iniettati in Stage C via Stage B, permettendo di:
- Assegnare correttamente lo `speaking_style` per personaggio
- Separare le battute dei personaggi dalla narrazione

### Global Voice vs Casting
- Global Voice: configurabile in qualsiasi momento (anche prima di Stage 0)
- Casting: richiede Stage 0.2 completato per popolare la lista personaggi

## Vedi anche

- [[concepts/dias-pipeline]] — Stage 0 nel flusso completo
- [[concepts/aria-tts-backends]] — voci disponibili per il Casting
- [[ct201-dias-rt]] — Dashboard e API Hub (runtime)
- [[stack-dias]] — sistema DIAS completo
