---
title: "Analisi Streak Scambiabili SHIFTER"
type: concept
tags: [shifter, planning, constraints, CLI]
sources: []
updated: 2026-06-13
---

# Analisi Streak Scambiabili SHIFTER

Questa pagina documenta la logica e lo strumento di analisi delle **streak scambiabili** all'interno dello stack [[entities/systems/stack-shifter|SHIFTER]].

## Obiettivo dell'Analisi

Lo scopo principale del motore di scambi è consentire agli operatori di scambiarsi interi blocchi di turni consecutivi (streak) omogenei senza rompere i vincoli operativi del sistema. Questo permette una gestione flessibile della turnistica post-solutore senza dover ricalcolare l'intera programmazione annuale.

## Lo Strumento CLI `analyze_swaps.py`

È stato implementato uno script parametrizzato in [analyze_swaps.py](file:///home/Projects/NH-Mini/sviluppi/SHIFTER/src/backend/analyze_swaps.py) per interrogare a riga di comando la fattibilità degli scambi per qualsiasi operatore e fascia oraria nell'arco dell'intero anno.

### Sintassi di Utilizzo

```bash
/home/Projects/NH-Mini/sviluppi/SHIFTER/.venv/bin/python3 src/backend/analyze_swaps.py --operator "Nome" --shift "Fascia" [--year 2026]
```

Esempi:
- Per analizzare i turni Mattina di **Guareschi**:
  ```bash
  /home/Projects/NH-Mini/sviluppi/SHIFTER/.venv/bin/python3 src/backend/analyze_swaps.py --operator Guareschi --shift M
  ```
- Per analizzare i turni Pomeriggio di **Materazzo**:
  ```bash
  /home/Projects/NH-Mini/sviluppi/SHIFTER/.venv/bin/python3 src/backend/analyze_swaps.py --operator Materazzo --shift P
  ```

## Logica di Validazione

Lo script richiama la classe `SwapEngine` definita in [swap_engine.py](file:///home/Projects/NH-Mini/sviluppi/SHIFTER/src/backend/swap_engine.py). Questa classe esegue i seguenti passaggi per ogni potenziale candidato:
1. **Verifica Presenza**: Il candidato deve lavorare in tutte le date della streak.
2. **Omogeneità**: I turni del candidato in quelle date devono essere tutti della stessa fascia.
3. **Turno Differente**: La fascia del candidato deve essere diversa da quella del richiedente.
4. **Preferenze Operatore**: Devono essere rispettate le preferenze dichiarate da entrambi gli operatori (se configurate).
5. **Presenza Fisica Minima**: Lo scambio simulato non deve lasciare alcun turno coperto solo da operatori del gruppo `smart`.
6. **Vincoli di Transizione**:
   - `N -> M` e `N -> P` sono vietati per evitare turni di riposo insufficienti (0h e 8h rispettivamente).
   - `P -> M` genera un warning (riposo ridotto a 8h).
