#!/usr/bin/env python3
"""
nh-lint.py — Compliance checker per il framework NH-Mini.

Verifica che lo stato del sistema sia coerente con le convenzioni:
- Ogni progetto in sviluppi/ ha un .project-context
- Ogni container SOT è documentato in infrastructure-map.mdc
- Ogni modulo in core/ ha una entry in core-modules.mdc
- Il session-journal.md ha una entry END recente
- Ogni servizio in STATIC_CATALOG ha documentazione wiki associata

Exit code:
  0 = tutto OK
  1 = warning (incongruenze non bloccanti)
  2 = errori (incongruenze bloccanti)

Uso:
  python3 scripts/nh-lint.py
  python3 scripts/nh-lint.py --fix-hints   # mostra come correggere ogni problema
  python3 scripts/nh-lint.py --json        # output JSON (per integrazione dashboard)
"""

import json
import sys
import re
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parent.parent

# ── helpers ──────────────────────────────────────────────────────────────────

RESET   = "\033[0m"
RED     = "\033[31m"
YELLOW  = "\033[33m"
GREEN   = "\033[32m"
CYAN    = "\033[36m"
BOLD    = "\033[1m"

def ok(msg):    print(f"  {GREEN}✅{RESET} {msg}")
def warn(msg):  print(f"  {YELLOW}⚠️ {RESET} {msg}")
def err(msg):   print(f"  {RED}❌{RESET} {msg}")
def info(msg):  print(f"  {CYAN}ℹ️ {RESET} {msg}")


class LintResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passes = []

    def error(self, check, message, fix_hint=""):
        self.errors.append({"check": check, "message": message, "fix_hint": fix_hint})

    def warning(self, check, message, fix_hint=""):
        self.warnings.append({"check": check, "message": message, "fix_hint": fix_hint})

    def passed(self, check, message):
        self.passes.append({"check": check, "message": message})

    @property
    def exit_code(self):
        if self.errors:
            return 2
        if self.warnings:
            return 1
        return 0


# ── checks ────────────────────────────────────────────────────────────────────

def check_projects(result: LintResult):
    """Ogni progetto in sviluppi/ deve avere .project-context."""
    sviluppi = ROOT / "sviluppi"
    if not sviluppi.exists():
        result.warning("projects", "Directory sviluppi/ non trovata")
        return

    for d in sorted(sviluppi.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name.startswith("_"):
            continue
        ctx = d / ".project-context"
        if ctx.exists():
            result.passed("projects", f"{d.name} → .project-context ✓")
        else:
            result.error(
                "projects",
                f"{d.name} — manca .project-context",
                fix_hint=f"python3 scripts/nh-new-project.py --name {d.name} --yes  oppure crea manualmente sviluppi/{d.name}/.project-context"
            )


def check_infrastructure(result: LintResult):
    """Ogni container SOT (VMID in REAL_VMIDS) deve essere in infrastructure-map.mdc."""
    REAL_VMIDS = {120, 190, 201, 202}
    inv_path = ROOT / "state" / "inventory.json"
    if not inv_path.exists():
        result.warning("infrastructure", "state/inventory.json non trovato — esegui nh-discovery.sh")
        return

    inv = json.loads(inv_path.read_text())
    containers = inv.get("containers", [])
    real = [c for c in containers if c["vmid"] in REAL_VMIDS]

    infra_map = (ROOT / "knowledge" / "containers" / "infrastructure-map.mdc").read_text()

    for c in real:
        name = c.get("name", "")
        vmid = c["vmid"]
        if f"CT{vmid}" in infra_map or name in infra_map:
            result.passed("infrastructure", f"CT{vmid} ({name}) → documentato in infrastructure-map.mdc")
        else:
            result.error(
                "infrastructure",
                f"CT{vmid} ({name}) — non trovato in infrastructure-map.mdc",
                fix_hint=f"Aggiungi sezione ### CT{vmid} — {name} in knowledge/containers/infrastructure-map.mdc"
            )


def check_core_modules(result: LintResult):
    """Ogni modulo .py in core/ deve avere un'entry in core-modules.mdc."""
    core_dir = ROOT / "core"
    core_doc = ROOT / "knowledge" / "architecture" / "core-modules.mdc"
    if not core_dir.exists():
        result.warning("core_modules", "Directory core/ non trovata")
        return
    if not core_doc.exists():
        result.error("core_modules", "knowledge/architecture/core-modules.mdc non trovato")
        return

    doc_text = core_doc.read_text()

    # Skip file interni (cache, init)
    SKIP = {"__init__.py", "__pycache__"}

    for f in sorted(core_dir.glob("*.py")):
        if f.name in SKIP:
            continue
        # Cerca il nome del modulo nella doc
        if f.stem in doc_text or f.name in doc_text:
            result.passed("core_modules", f"core/{f.name} → documentato in core-modules.mdc")
        else:
            result.warning(
                "core_modules",
                f"core/{f.name} — non trovato in core-modules.mdc",
                fix_hint=f"Aggiungi sezione '### {f.name}' in knowledge/architecture/core-modules.mdc"
            )


def check_service_catalog(result: LintResult):
    """Ogni servizio in STATIC_CATALOG deve avere documentazione nel wiki."""
    try:
        sys.path.insert(0, str(ROOT))
        from core.service_catalog import STATIC_CATALOG
    except ImportError as e:
        result.error("service_catalog", f"Impossibile importare service_catalog: {e}")
        return

    wiki_dir = ROOT / "NH-Mini"
    wiki_text = ""
    for f in wiki_dir.rglob("*.md"):
        try:
            wiki_text += f.read_text()
        except Exception:
            pass

    for key, svc in STATIC_CATALOG.items():
        name = svc.get("name", key)
        # Cerca il nome del servizio o la chiave nel wiki
        if key in wiki_text or name in wiki_text:
            result.passed("service_catalog", f"{key} ({name}) → documentato nel wiki")
        else:
            result.warning(
                "service_catalog",
                f"{key} ({name}) — non trovato nel wiki NH-Mini",
                fix_hint=f"Crea NH-Mini/concepts/{key}-pattern.md con documentazione d'integrazione"
            )


def check_session_journal(result: LintResult):
    """Il session-journal deve avere una entry END recente (ultime 48h)."""
    journal_path = ROOT / "state" / "session-journal.md"
    if not journal_path.exists():
        result.error(
            "session_journal",
            "state/session-journal.md non trovato",
            fix_hint="Il file viene creato automaticamente alla prima sessione. Probabilmente non è stato avviato correttamente."
        )
        return

    text = journal_path.read_text()

    # Cerca ultima entry END
    end_matches = list(re.finditer(r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] END", text))
    if not end_matches:
        result.warning(
            "session_journal",
            "Nessuna entry END trovata nel session-journal — la sessione precedente potrebbe non essere stata chiusa correttamente",
            fix_hint="Aggiungi un'entry ## [HH:MM] END con: completato, incompleto, mine"
        )
        return

    # Verifica che l'ultima END sia recente (48h)
    sorted_ends = sorted(end_matches, key=lambda m: m.group(1), reverse=True)
    last_end = sorted_ends[0]
    try:
        end_dt = datetime.strptime(last_end.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - end_dt
        if age > timedelta(hours=48):
            result.warning(
                "session_journal",
                f"Ultima entry END risale a {int(age.total_seconds() / 3600)}h fa — potrebbe essere stantia",
                fix_hint="Normale se non ci sono state sessioni recenti. Aggiungi START all'inizio della prossima sessione."
            )
        else:
            result.passed("session_journal", f"Entry END trovata ({last_end.group(1)}) — journal in ordine")
    except ValueError:
        result.warning("session_journal", "Formato timestamp END non parsabile")


def check_user_profile(result: LintResult):
    """Il profilo utente deve esistere."""
    profile = ROOT / "NH-Mini" / "user-profile.md"
    if profile.exists():
        result.passed("user_profile", "NH-Mini/user-profile.md esiste")
    else:
        result.error(
            "user_profile",
            "NH-Mini/user-profile.md non trovato",
            fix_hint="Crea il file seguendo il template in NH-Mini/user-profile.md (creato in Fase 1)"
        )


def check_scripts_reference(result: LintResult):
    """Ogni script in scripts/ deve essere menzionato in .cursorrules o core-modules.mdc."""
    scripts_dir = ROOT / "scripts"
    cursorrules = (ROOT / ".cursorrules").read_text() if (ROOT / ".cursorrules").exists() else ""
    core_doc_text = ""
    core_doc = ROOT / "knowledge" / "architecture" / "core-modules.mdc"
    if core_doc.exists():
        core_doc_text = core_doc.read_text()

    combined = cursorrules + core_doc_text

    SKIP = {"__init__.py", "__pycache__"}

    for f in sorted(scripts_dir.glob("*.py")):
        if f.name in SKIP:
            continue
        if f.stem in combined or f.name in combined:
            result.passed("scripts_ref", f"scripts/{f.name} → referenziato in docs")
        else:
            result.warning(
                "scripts_ref",
                f"scripts/{f.name} — non referenziato in .cursorrules né in core-modules.mdc",
                fix_hint=f"Aggiungi '{f.name}' alla tabella scripts in knowledge/architecture/core-modules.mdc"
            )


def check_project_knowledge_index(project_name: str, result: LintResult):
    """Verifica ogni entry KNOWLEDGE_INDEX del .project-context del progetto specificato."""
    project_dir = ROOT / "sviluppi" / project_name
    ctx_path = project_dir / ".project-context"

    if not project_dir.exists():
        result.error(
            "project_knowledge",
            f"Progetto '{project_name}' non trovato in sviluppi/",
            fix_hint=f"Verifica che sviluppi/{project_name}/ esista"
        )
        return

    if not ctx_path.exists():
        result.error(
            "project_knowledge",
            f"{project_name} — manca .project-context",
            fix_hint=f"Crea sviluppi/{project_name}/.project-context seguendo core/description-contracts.mdc"
        )
        return

    try:
        ctx = yaml.safe_load(ctx_path.read_text(encoding="utf-8"))
    except Exception as e:
        result.error("project_knowledge", f"{project_name} — .project-context non parsabile: {e}")
        return

    ki = ctx.get("KNOWLEDGE_INDEX", {})
    entries = ki.get("entries", []) if isinstance(ki, dict) else ki

    if not entries:
        result.warning(
            "project_knowledge",
            f"{project_name} — KNOWLEDGE_INDEX vuoto o assente",
            fix_hint=f"Aggiungi entries con path/doc_trigger/lint_check in sviluppi/{project_name}/.project-context"
        )
        return

    for entry in entries:
        if isinstance(entry, str):
            # Formato legacy (path solo)
            file_path = project_dir / entry
            if file_path.exists() and file_path.stat().st_size > 0:
                result.passed("project_knowledge", f"{project_name}/{entry} → esiste e non vuoto")
            elif not file_path.exists():
                result.error(
                    "project_knowledge",
                    f"{project_name}/{entry} — file non trovato",
                    fix_hint=f"Crea {entry} oppure rimuovi l'entry stantia dal KNOWLEDGE_INDEX"
                )
            else:
                result.warning(
                    "project_knowledge",
                    f"{project_name}/{entry} — file vuoto (0 byte)",
                    fix_hint=f"Popola {entry} oppure rimuovi l'entry dal KNOWLEDGE_INDEX"
                )
        elif isinstance(entry, dict):
            rel_path = entry.get("path", "")
            lint_check = entry.get("lint_check", "file exists")
            file_path = project_dir / rel_path

            if not file_path.exists():
                result.error(
                    "project_knowledge",
                    f"{project_name}/{rel_path} — file non trovato",
                    fix_hint=f"Crea {rel_path} oppure rimuovi l'entry stantia dal KNOWLEDGE_INDEX"
                )
            elif file_path.stat().st_size == 0:
                result.error(
                    "project_knowledge",
                    f"{project_name}/{rel_path} — file vuoto (0 byte) | lint_check: {lint_check}",
                    fix_hint=f"Popola {rel_path}"
                )
            elif "size >" in lint_check:
                # Estrae soglia dimensione dal lint_check (es. "size > 5KB")
                try:
                    threshold_str = re.search(r"size > (\d+)KB", lint_check).group(1)
                    threshold = int(threshold_str) * 1024
                    actual = file_path.stat().st_size
                    if actual < threshold:
                        result.warning(
                            "project_knowledge",
                            f"{project_name}/{rel_path} — dimensione {actual}B < soglia {threshold_str}KB | lint_check: {lint_check}",
                            fix_hint=f"Il file sembra incompleto — controlla che {rel_path} sia aggiornato"
                        )
                    else:
                        result.passed("project_knowledge", f"{project_name}/{rel_path} → {actual}B ✓")
                except (AttributeError, ValueError):
                    result.passed("project_knowledge", f"{project_name}/{rel_path} → esiste ✓")
            else:
                result.passed("project_knowledge", f"{project_name}/{rel_path} → esiste ✓")


# ── runner ────────────────────────────────────────────────────────────────────

CHECKS = [
    ("Projects", check_projects),
    ("Infrastructure Map", check_infrastructure),
    ("Core Modules Doc", check_core_modules),
    ("Service Catalog Wiki", check_service_catalog),
    ("Session Journal", check_session_journal),
    ("User Profile", check_user_profile),
    ("Scripts Reference", check_scripts_reference),
]


def run_lint(fix_hints: bool = False, as_json: bool = False) -> LintResult:
    result = LintResult()
    for title, check_fn in CHECKS:
        check_fn(result)
    return result


def print_summary(result: LintResult, fix_hints: bool = False):
    print(f"\n{BOLD}─── Summary ──────────────────────────────────{RESET}")
    print(f"  Passed:   {GREEN}{len(result.passes)}{RESET}")
    print(f"  Warnings: {YELLOW}{len(result.warnings)}{RESET}")
    print(f"  Errors:   {RED}{len(result.errors)}{RESET}")

    if result.errors:
        print(f"\n{BOLD}{RED}Errors (require action):{RESET}")
        for e in result.errors:
            print(f"  [{e['check']}] {e['message']}")
            if fix_hints and e.get("fix_hint"):
                print(f"    → Fix: {e['fix_hint']}")

    if result.warnings:
        print(f"\n{BOLD}{YELLOW}Warnings (recommended):{RESET}")
        for w in result.warnings:
            print(f"  [{w['check']}] {w['message']}")
            if fix_hints and w.get("fix_hint"):
                print(f"    → Fix: {w['fix_hint']}")

    if result.exit_code == 0:
        print(f"\n{GREEN}{BOLD}✅ All checks passed — system is compliant.{RESET}")
    elif result.exit_code == 1:
        print(f"\n{YELLOW}{BOLD}⚠️  Warnings found — system is functional but has gaps.{RESET}")
    else:
        print(f"\n{RED}{BOLD}❌ Errors found — action required before proceeding.{RESET}")
    print()


if __name__ == "__main__":
    fix_hints = "--fix-hints" in sys.argv
    as_json = "--json" in sys.argv

    # Parsing --project {app}
    project_arg = None
    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        if idx + 1 < len(sys.argv):
            project_arg = sys.argv[idx + 1]
        else:
            print("Errore: --project richiede un nome progetto (es. --project ARIA)")
            sys.exit(2)

    if as_json:
        result = run_lint(fix_hints=fix_hints, as_json=True)
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exit_code": result.exit_code,
            "summary": {
                "passed": len(result.passes),
                "warnings": len(result.warnings),
                "errors": len(result.errors),
            },
            "errors": result.errors,
            "warnings": result.warnings,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        # Print per-check results inline
        result = LintResult()
        print(f"\n{BOLD}NH-Mini Lint — Compliance Check{RESET}")
        print(f"Root: {ROOT}\n")
        for title, check_fn in CHECKS:
            print(f"{BOLD}{CYAN}{title}{RESET}")
            p_len, w_len, e_len = len(result.passes), len(result.warnings), len(result.errors)
            check_fn(result)
            for p in result.passes[p_len:]:
                ok(p["message"])
            for w in result.warnings[w_len:]:
                warn(w["message"])
            for e in result.errors[e_len:]:
                err(e["message"])
            print()

        if project_arg:
            print(f"{BOLD}{CYAN}Project Knowledge Index — {project_arg}{RESET}")
            p_len, w_len, e_len = len(result.passes), len(result.warnings), len(result.errors)
            check_project_knowledge_index(project_arg, result)
            for p in result.passes[p_len:]:
                ok(p["message"])
            for w in result.warnings[w_len:]:
                warn(w["message"])
            for e in result.errors[e_len:]:
                err(e["message"])
            print()

        print_summary(result, fix_hints=fix_hints)

    sys.exit(result.exit_code)
