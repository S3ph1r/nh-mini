#!/usr/bin/env python3
"""
nh-session-end.py — Genera un handover summary leggibile dal session-journal.

Legge state/session-journal.md, estrae l'ultima entry END,
e produce state/session-handover.md — una pagina concisa e leggibile
per il bootstrapping della prossima sessione.

Uso:
  python3 scripts/nh-session-end.py          # genera handover da ultima END
  python3 scripts/nh-session-end.py --show   # stampa a video senza salvare
  python3 scripts/nh-session-end.py --all    # include anche le END precedenti

Note:
  - Se non c'è entry END nel journal, stampa un avviso e suggerisce di aggiungerla.
  - Il file session-handover.md viene letto dalla dashboard (GET /api/handover).
"""

import re
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "state" / "session-journal.md"
HANDOVER = ROOT / "state" / "session-handover.md"


def extract_last_end_block(text: str) -> tuple[str | None, str | None]:
    """
    Estrae la entry END più recente dal journal basandosi sul timestamp.
    Ritorna (timestamp, content) oppure (None, None) se non trovata.
    """
    pattern = r"(## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] END\n)(.*?)(?=\n## \[|\Z)"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    if not matches:
        return None, None
    
    # Ordina per timestamp decrescente e prendi il primo
    sorted_matches = sorted(matches, key=lambda m: m.group(2), reverse=True)
    latest = sorted_matches[0]
    return latest.group(2), latest.group(0)


def extract_section(block: str, section: str) -> str:
    """Estrae il contenuto di una sezione **Section:** dal blocco END."""
    pattern = rf"\*\*{re.escape(section)}[:\*]*(.*?)(?=\n\*\*|\Z)"
    m = re.search(pattern, block, re.DOTALL)
    if not m:
        return ""
    return m.group(1).strip()


def find_last_start_objective(text: str) -> str:
    """Trova l'obiettivo della sessione più recente (dal blocco START)."""
    pattern = r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] START\n(.*?)(?=\n## \[|\Z)"
    matches = list(re.finditer(pattern, text, re.DOTALL))
    if not matches:
        return ""
    
    # Ordina per timestamp decrescente e prendi il primo
    sorted_matches = sorted(matches, key=lambda m: m.group(1), reverse=True)
    latest = sorted_matches[0]
    
    # Estrai obiettivo
    block = latest.group(2)
    obj_m = re.search(r"\*\*Obiettivo[^:]*:\*\*\s*(.*?)(?=\n\*\*|\n---|\Z)", block, re.DOTALL)
    if obj_m:
        return obj_m.group(1).strip()
    # Prendi le prime righe del blocco START
    lines = [l for l in block.split("\n") if l.strip()]
    return "\n".join(lines[:5])


def generate_handover(show_only: bool = False) -> int:
    if not JOURNAL.exists():
        print("❌ state/session-journal.md non trovato.")
        print("   Crea il file con scripts/nh-session-end.py o avvia una sessione.")
        return 1

    text = JOURNAL.read_text()
    timestamp, end_block = extract_last_end_block(text)

    if not end_block:
        print("⚠️  Nessuna entry END trovata nel session-journal.")
        print("   Aggiungi un'entry al journal prima di chiudere la sessione:")
        print()
        print("   ## [HH:MM] END")
        print("   **Completato:** ...")
        print("   **Incompleto:** ...")
        print("   **Mine per il prossimo agent:** ...")
        return 1

    # Estrai sezioni dall'END block
    completato = extract_section(end_block, "Completato")
    incompleto = extract_section(end_block, "Incompleto")
    mine       = extract_section(end_block, "Mine per il prossimo agent")
    obiettivo  = find_last_start_objective(text)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    handover_content = f"""# Session Handover — NH-Mini

Generato automaticamente da `nh-session-end.py`  
Aggiornato: {now} · Basato su session-journal.md (ultima END: {timestamp})

---

## Obiettivo Sessione Precedente

{obiettivo or "_(non trovato nel journal)_"}

---

## Cosa è stato completato

{completato or "_(nessuna sezione Completato trovata nell'entry END)_"}

---

## Cosa è rimasto incompleto

{incompleto or "_(nessuna sezione Incompleto trovata nell'entry END)_"}

---

## ⚠️ Mine per il prossimo agent

{mine or "_(nessuna sezione Mine trovata nell'entry END)_"}

---

_Per il dettaglio completo: leggi `state/session-journal.md`_
"""

    if show_only:
        print(handover_content)
        return 0

    HANDOVER.write_text(handover_content)
    print(f"✅ Session handover generato → {HANDOVER}")
    print(f"   Basato su entry END del {timestamp}")
    print()
    print("─── Preview ──────────────────────────────────")
    # Stampa solo le mine (le più importanti)
    if mine:
        print("⚠️  Mine per il prossimo agent:")
        for line in mine.split("\n")[:5]:
            if line.strip():
                print(f"   {line}")
    return 0


if __name__ == "__main__":
    show_only = "--show" in sys.argv
    sys.exit(generate_handover(show_only=show_only))
