#!/usr/bin/env python3
"""
nh-new-project.py — Crea un nuovo progetto NH-Mini in sviluppi/

Crea la struttura standard, il .project-context, aggiorna il workspace
e suggerisce i servizi già disponibili che il progetto può usare.

Uso:
    python3 scripts/nh-new-project.py                    # interattivo
    python3 scripts/nh-new-project.py --name myapp       # semi-interattivo
    python3 scripts/nh-new-project.py --name myapp \
        --description "La mia app" --stack "Python, FastAPI"  # non-interattivo
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVILUPPI = ROOT / "sviluppi"


# ── helpers ──────────────────────────────────────────────────────────────────

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{prompt}{suffix}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)


def load_service_catalog() -> dict:
    try:
        sys.path.insert(0, str(ROOT))
        from core.service_catalog import get_catalog
        return get_catalog(probe=False)
    except Exception:
        return {}


def format_services_hint(catalog: dict) -> str:
    lines = []
    for key, svc in catalog.items():
        if key.startswith("_"):
            continue
        ep = f"{svc.get('host', '')}:{svc.get('port', '')}" if svc.get("port") else svc.get("host", "")
        lines.append(f"  - {key}: {svc['name']} ({ep})")
    return "\n".join(lines)


# ── project creation ─────────────────────────────────────────────────────────

def create_project(name: str, description: str, stack: str,
                   services_used: list[str], has_rt_lxc: bool) -> Path:

    project_dir = SVILUPPI / name
    if project_dir.exists():
        print(f"❌ Il progetto '{name}' esiste già in {project_dir}")
        sys.exit(1)

    # Struttura cartelle
    dirs = ["src", "docs", "knowledge", "state", "scripts"]
    for d in dirs:
        (project_dir / d).mkdir(parents=True)

    # .project-context
    services_yaml = "\n".join(
        f"    - {s}: {s} (vedi core/service_catalog.py per endpoint)"
        for s in services_used
    ) if services_used else "    # Nessun servizio esterno dichiarato"

    rt_node = (
        "    - Runtime Node: LXC da definire — deploy con scripts/deploy_lxc.py"
        if has_rt_lxc else
        "    # Solo dev su CT190, nessun RT LXC previsto"
    )

    context = f"""IDENTITY:
  name: {name}
  description: {description}
  repo: locale
  stack: {stack}
  blueprint: docs/blueprint.md

ARCHITECTURE:
  overview: Da definire
  structure:
    src/: Codice sorgente
    docs/: Documentazione e blueprint
    knowledge/: Knowledge base del progetto
    state/: State files del progetto
    scripts/: Utility e script

INFRASTRUCTURE:
  nodes:
    - Dev Node: LXC 190 (NH-Mini) - Development & orchestration
{rt_node}
  services_used:
{services_yaml}
  storage: {project_dir}/

CREDENTIALS:
  list:
    # Aggiungere credenziali con: python3 scripts/credential_manager.py --store
    # Namespace: {name.lower()}.key_name

KNOWLEDGE_INDEX:
  entries:
    - docs/blueprint.md

DEVELOPMENT_PHASE:
  phase: development
  version: 0.1.0
  priorities: Da definire
  constraints: Da definire

OVERRIDES:
  # Aggiungi override specifici del progetto qui
"""
    (project_dir / ".project-context").write_text(context)

    # README
    readme = f"""# {name}

{description}

## Stack

{stack}

## Struttura

```
src/        — Codice sorgente
docs/       — Documentazione
knowledge/  — Knowledge base
state/      — State files
scripts/    — Utility
```

## Servizi usati

{chr(10).join(f'- {s}' for s in services_used) if services_used else '- Nessun servizio esterno dichiarato'}

## Avvio sviluppo

```bash
cd /home/Projects/NH-Mini
python3 scripts/nh-switch.py {name}
```

---
*Creato: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} — NH-Mini framework*
"""
    (project_dir / "README.md").write_text(readme)

    # docs/blueprint.md placeholder
    (project_dir / "docs" / "blueprint.md").write_text(
        f"# {name} — Blueprint\n\n> Da compilare\n\n## Obiettivo\n\n## Architettura\n\n## API / Interfacce\n"
    )

    # knowledge/index.md placeholder
    (project_dir / "knowledge" / "index.md").write_text(
        f"# Knowledge Index — {name}\n\n| File | Contenuto |\n|------|-----------|\n| (vuoto) | — |\n"
    )

    return project_dir


def switch_workspace(name: str) -> bool:
    try:
        from core.workspace_manager import get_workspace_manager
        wm = get_workspace_manager()
        wm.switch_project(name)
        return True
    except Exception as e:
        print(f"⚠️  Switch workspace fallito: {e}")
        print(f"   Puoi farlo manualmente: python3 scripts/nh-switch.py {name}")
        return False


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Crea un nuovo progetto NH-Mini")
    parser.add_argument("--name", help="Nome del progetto (slug, no spazi)")
    parser.add_argument("--description", help="Descrizione breve")
    parser.add_argument("--stack", help="Stack tecnologico (es: 'Python, FastAPI, Redis')")
    parser.add_argument("--services", help="Servizi usati (separati da virgola, es: 'redis,gateway')")
    parser.add_argument("--rt-lxc", action="store_true", help="Prevede un LXC runtime separato")
    parser.add_argument("--yes", "-y", action="store_true", help="Non chiedere conferma")
    parser.add_argument("--no-switch", action="store_true", help="Non cambiare workspace attivo")
    args = parser.parse_args()

    print("\n🛠️  NH-Mini — Nuovo Progetto\n")

    # Carica service catalog per suggerire servizi disponibili
    catalog = load_service_catalog()
    available_services = [k for k in catalog if not k.startswith("_")]

    # ── raccolta info ─────────────────────────────────────────────────────────

    name = args.name
    if not name:
        name = ask("Nome progetto (slug, no spazi, es: warroom-v2)")
    name = name.strip().lower().replace(" ", "-")
    if not name:
        print("❌ Nome obbligatorio.")
        sys.exit(1)

    description = args.description or ask("Descrizione", "Da definire")
    stack = args.stack or ask("Stack tecnologico", "Python")

    # Servizi disponibili
    print(f"\n📡 Servizi disponibili nell'infrastruttura:")
    print(format_services_hint(catalog))
    print()
    if args.services is not None:
        services_used = [s.strip() for s in args.services.split(",") if s.strip() and s.strip() in available_services]
    else:
        services_input = ask(
            f"Servizi che userai (separati da virgola, tra: {', '.join(available_services)})",
            ""
        )
        services_used = [s.strip() for s in services_input.split(",") if s.strip() and s.strip() in available_services]

    if args.rt_lxc:
        has_rt = True
    elif args.yes:
        has_rt = False
    else:
        has_rt = ask("Prevedi un LXC runtime separato? (s/n)", "n").lower().startswith("s")

    # ── riepilogo ─────────────────────────────────────────────────────────────

    print(f"""
📋 Riepilogo:
  Nome:        {name}
  Path:        {SVILUPPI / name}
  Descrizione: {description}
  Stack:       {stack}
  Servizi:     {', '.join(services_used) if services_used else '—'}
  RT LXC:      {'sì (da definire)' if has_rt else 'no'}
""")

    if not args.yes:
        confirm = ask("Procedere? (s/n)", "s").lower()
        if not confirm.startswith("s"):
            print("Annullato.")
            sys.exit(0)

    # ── crea progetto ─────────────────────────────────────────────────────────

    project_dir = create_project(name, description, stack, services_used, has_rt)
    print(f"\n✅ Progetto creato: {project_dir}")
    print(f"   Struttura: src/ docs/ knowledge/ state/ scripts/")
    print(f"   .project-context generato")

    # Switch workspace
    if not args.no_switch:
        if switch_workspace(name):
            print(f"   Workspace attivo: {name}")

    # ── prossimi passi ────────────────────────────────────────────────────────

    print(f"""
🚀 Prossimi passi:
  1. Compila il blueprint:      {project_dir}/docs/blueprint.md
  2. Aggiungi credenziali:      python3 scripts/credential_manager.py --store
  3. Inizia a sviluppare in:    {project_dir}/src/
  4. Quando pronto per RT:      python3 scripts/nh-promote.py {name}  [TODO]

  Dashboard:  http://192.168.1.190:8080 → Projects (il progetto è già visibile)
""")

    # ── aggiorna log NH-Mini ──────────────────────────────────────────────────
    log_path = ROOT / "NH-Mini" / "log.md"
    if log_path.exists():
        entry = (
            f"\n---\n\n## [{datetime.now(timezone.utc).strftime('%Y-%m-%d')}] "
            f"new-project | {name}\n\n"
            f"**Creato con nh-new-project.py**\n"
            f"- Description: {description}\n"
            f"- Stack: {stack}\n"
            f"- Servizi: {', '.join(services_used) if services_used else '—'}\n"
            f"- Path: `sviluppi/{name}/`\n"
        )
        with open(log_path, "a") as f:
            f.write(entry)
        print(f"   Log wiki aggiornato: NH-Mini/log.md")


if __name__ == "__main__":
    main()
