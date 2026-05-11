#!/usr/bin/env python3
"""
nh-promote.py — Promuove un progetto da sviluppi/ a un RT LXC dedicato

Workflow:
  1. Legge .project-context del progetto
  2. Crea un nuovo LXC via deploy_lxc.py
  3. Carica il codice con rsync (src/ → /opt/{name}/)
  4. Opzionalmente configura un servizio systemd
  5. Aggiorna .project-context con il nodo RT
  6. Logga l'operazione

Uso:
    python3 scripts/nh-promote.py <project-name>
    python3 scripts/nh-promote.py dias --vmid 203 --memory 2048 --yes
"""

import argparse
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SVILUPPI = ROOT / "sviluppi"

SSH_KEY = Path.home() / ".ssh" / "id_ed25519"
if not SSH_KEY.exists():
    SSH_KEY = Path.home() / ".ssh" / "id_rsa"
SSH_OPTS = f"-i {SSH_KEY} -o StrictHostKeyChecking=no -o ConnectTimeout=10"


# ── helpers ───────────────────────────────────────────────────────────────────

def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{prompt}{suffix}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)


def ssh(ip: str, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    full = f"ssh {SSH_OPTS} root@{ip} '{cmd}'"
    return subprocess.run(full, shell=True, capture_output=True, text=True, check=check)


def rsync(src: str, ip: str, dst: str) -> bool:
    excludes = [
        "node_modules",
        ".svelte-kit",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".git",
        ".DS_Store"
    ]
    exclude_args = " ".join([f"--exclude='{e}'" for e in excludes])
    cmd = f"rsync -az --delete {exclude_args} -e 'ssh {SSH_OPTS}' {src} root@{ip}:{dst}"
    r = subprocess.run(cmd, shell=True, text=True)
    return r.returncode == 0


def load_project_context(project_dir: Path) -> dict:
    ctx_file = project_dir / ".project-context"
    if not ctx_file.exists():
        return {}
    try:
        return yaml.safe_load(ctx_file.read_text()) or {}
    except Exception:
        return {}


def save_project_context(project_dir: Path, ctx: dict) -> None:
    ctx_file = project_dir / ".project-context"
    ctx_file.write_text(yaml.dump(ctx, allow_unicode=True, default_flow_style=False))


# ── core logic ─────────────────────────────────────────────────────────────────

def deploy_rt_lxc(name: str, vmid: int, memory: int, cpu: int, storage: int,
                  template: str) -> bool:
    sys.path.insert(0, str(ROOT / "scripts"))
    from deploy_lxc import NHLXCDeployer
    deployer = NHLXCDeployer()
    return deployer.deploy(vmid=vmid, name=f"nh-{name}", template=template,
                           memory=memory, cpu=cpu, storage=storage)


def push_code(project_dir: Path, ip: str, remote_dir: str) -> bool:
    src_dir = project_dir / "src"
    if not src_dir.exists():
        print(f"⚠️  src/ non trovata in {project_dir} — skip rsync")
        return True

    print(f"   Creazione {remote_dir} su {ip}...")
    ssh(ip, f"mkdir -p {remote_dir}")

    print(f"   rsync src/ → {ip}:{remote_dir} ...")
    if rsync(str(src_dir) + "/", ip, remote_dir):
        # Also push requirements.txt if exists in root
        req_file = project_dir / "requirements.txt"
        if req_file.exists():
            print(f"   rsync requirements.txt → {ip}:{remote_dir} ...")
            rsync(str(req_file), ip, remote_dir)
        print(f"   ✅ Codice caricato")
        return True
    else:
        print(f"   ❌ rsync fallito")
        return False


def maybe_install_systemd(ip: str, name: str, remote_dir: str, entrypoint: str) -> bool:
    unit = textwrap.dedent(f"""\
        [Unit]
        Description={name} RT service
        After=network.target

        [Service]
        Type=simple
        WorkingDirectory={remote_dir}
        ExecStart={entrypoint}
        Restart=on-failure
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
    """)
    unit_path = f"/etc/systemd/system/{name}.service"
    print(f"   Scrittura {unit_path} su {ip}...")
    escaped = unit.replace("'", "'\\''")
    ssh(ip, f"echo '{escaped}' > {unit_path}")
    ssh(ip, "systemctl daemon-reload")
    ssh(ip, f"systemctl enable {name}.service")
    r = ssh(ip, f"systemctl start {name}.service", check=False)
    if r.returncode == 0:
        print(f"   ✅ Servizio {name}.service avviato")
        return True
    else:
        print(f"   ⚠️  Servizio non avviato — verifica manualmente: systemctl status {name}")
        return False


def update_project_context(project_dir: Path, name: str, vmid: int, ip: str) -> None:
    ctx = load_project_context(project_dir)
    if not ctx:
        print("   ⚠️  .project-context non trovato — skip aggiornamento")
        return

    infra = ctx.setdefault("INFRASTRUCTURE", {})
    nodes = infra.setdefault("nodes", [])

    rt_entry = f"Runtime Node: LXC {vmid} ({ip}) — deploy {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    # rimuovi entry RT precedenti e aggiungi la nuova
    nodes = [n for n in nodes if not str(n).startswith("Runtime Node:")]
    nodes.append(rt_entry)
    infra["nodes"] = nodes

    ctx["DEVELOPMENT_PHASE"]["phase"] = "production"

    save_project_context(project_dir, ctx)
    print(f"   ✅ .project-context aggiornato: RT Node = CT{vmid} ({ip})")


def append_wiki_log(name: str, vmid: int, ip: str) -> None:
    log_path = ROOT / "NH-Mini" / "log.md"
    if not log_path.exists():
        return
    entry = (
        f"\n---\n\n## [{datetime.now(timezone.utc).strftime('%Y-%m-%d')}] "
        f"promote | {name} → CT{vmid}\n\n"
        f"**nh-promote.py**: progetto promosso da sviluppi/ a RT LXC\n"
        f"- Progetto: {name}\n"
        f"- RT Node: CT{vmid} ({ip})\n"
        f"- Codice: rsync src/ → {ip}:/opt/{name}/\n"
    )
    with open(log_path, "a") as f:
        f.write(entry)
    print(f"   Log wiki aggiornato: NH-Mini/log.md")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Promuovi progetto NH-Mini a RT LXC")
    parser.add_argument("project", help="Nome progetto in sviluppi/")
    parser.add_argument("--vmid", type=int, help="VMID LXC (default: auto)")
    parser.add_argument("--memory", type=int, default=2048, help="RAM in MB (default: 2048)")
    parser.add_argument("--cpu", type=int, default=2, help="CPU cores (default: 2)")
    parser.add_argument("--storage", type=int, default=16, help="Disco in GB (default: 16)")
    parser.add_argument("--template", default="debian-12", help="Template OS (default: debian-12)")
    parser.add_argument("--entrypoint", help="Comando avvio servizio (es: 'python3 main.py')")
    parser.add_argument("--no-service", action="store_true", help="Non creare servizio systemd")
    parser.add_argument("--no-code", action="store_true", help="Non rsync il codice")
    parser.add_argument("--yes", "-y", action="store_true", help="Non chiedere conferma")
    args = parser.parse_args()

    name = args.project.strip()
    project_dir = SVILUPPI / name

    if not project_dir.exists():
        # Try lowercase as fallback
        name = name.lower()
        project_dir = SVILUPPI / name
        if not project_dir.exists():
            print(f"❌ Progetto '{args.project}' non trovato in {SVILUPPI}")
            sys.exit(1)

    ctx = load_project_context(project_dir)
    description = ctx.get("IDENTITY", {}).get("description", "—")
    stack = ctx.get("IDENTITY", {}).get("stack", "—")

    print(f"\n🚀 NH-Mini — Promozione Progetto a RT LXC\n")
    print(f"   Progetto:    {name}")
    print(f"   Descrizione: {description}")
    print(f"   Stack:       {stack}")
    print()

    # VMID selection
    vmid = args.vmid
    if not vmid:
        vmid_input = ask("VMID LXC (lascia vuoto per auto-detect)", "")
        vmid = int(vmid_input) if vmid_input.isdigit() else None

    # Entrypoint per systemd
    entrypoint = args.entrypoint
    if not args.no_service and not entrypoint and not args.yes:
        entrypoint = ask("Comando entrypoint servizio (es: 'python3 main.py', vuoto = salta)", "")
        if not entrypoint:
            args.no_service = True

    # IP attesa (deploy_lxc usa 192.168.1.{vmid})
    ip = f"192.168.1.{vmid}" if vmid else "TBD (dopo deploy)"
    remote_dir = f"/opt/{name}"

    print(f"""
📋 Riepilogo:
  Progetto:    {name}
  VMID:        CT{vmid or 'auto'}
  IP attesa:   {ip}
  RAM:         {args.memory}MB
  CPU:         {args.cpu} cores
  Storage:     {args.storage}GB
  Template:    {args.template}
  Codice:      {'rsync src/ → ' + remote_dir if not args.no_code else 'skip'}
  Servizio:    {entrypoint if not args.no_service and entrypoint else 'skip'}
""")

    if not args.yes:
        confirm = ask("Procedere con deploy RT LXC? (s/n)", "n").lower()
        if not confirm.startswith("s"):
            print("Annullato.")
            sys.exit(0)

    # ── Step 1: Deploy LXC ────────────────────────────────────────────────────
    print("\n📦 Step 1/4 — Deploy LXC...")
    ok = deploy_rt_lxc(name, vmid, args.memory, args.cpu, args.storage, args.template)
    if not ok:
        print("   ⚠️  Deploy LXC non ha creato un nuovo container (potrebbe già esistere).")
        # Verifichiamo se l'IP è raggiungibile prima di dare per scontato che possiamo procedere
        print(f"   🔍 Verifico raggiungibilità {ip}...")
        check_ssh = subprocess.run(f"nc -z -w 3 {ip} 22", shell=True, capture_output=True)
        if check_ssh.returncode != 0:
            print(f"❌ Impossibile raggiungere {ip} via SSH. Deploy o configurazione fallita.")
            sys.exit(1)
        print(f"   ✅ {ip} raggiungibile. Procedo col push codice.")

    # Recupera VMID reale se auto-assegnato
    if not vmid:
        import json
        inv_path = ROOT / "state" / "inventory.json"
        if inv_path.exists():
            inv = json.loads(inv_path.read_text())
            containers = inv if isinstance(inv, list) else inv.get("containers", [])
            match = [c for c in containers if c.get("name") == f"nh-{name}"]
            if match:
                vmid = match[-1].get("vmid")
                ip = f"192.168.1.{vmid}"
                print(f"   VMID assegnato: CT{vmid} ({ip})")

    # ── Step 2: Push codice ──────────────────────────────────────────────────
    print("\n📂 Step 2/4 — Push codice...")
    if not args.no_code:
        push_code(project_dir, ip, remote_dir)
    else:
        print("   Skip (--no-code)")

    # ── Step 3: Servizio systemd ─────────────────────────────────────────────
    print("\n⚙️  Step 3/4 — Configurazione servizio systemd...")
    if not args.no_service and entrypoint:
        maybe_install_systemd(ip, name, remote_dir, entrypoint)
    else:
        print("   Skip — configura manualmente se necessario")

    # ── Step 4: Aggiorna metadati ────────────────────────────────────────────
    print("\n📝 Step 4/4 — Aggiornamento metadati...")
    update_project_context(project_dir, name, vmid, ip)
    append_wiki_log(name, vmid, ip)

    print(f"""
✅ Promozione completata!

  RT Node: CT{vmid} — {ip}
  Codice:  {ip}:{remote_dir}
  SSH:     ssh -i {SSH_KEY} root@{ip}

⚠️  Prossimi passi manuali:
  1. Aggiorna knowledge/containers/infrastructure-map.mdc con CT{vmid}
  2. Aggiorna core/service_catalog.py se espone una API
  3. Configura nginx in CT202 se serve routing esterno:
       python3 scripts/setup_ct202_gateway.sh
  4. Triggera discovery: POST http://192.168.1.190:8080/api/discovery/refresh
""")


if __name__ == "__main__":
    main()
