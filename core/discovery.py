#!/usr/bin/env python3
"""
discovery.py — Scanner Proxmox → state/inventory.json
Funziona sia in locale (su Proxmox host) sia via SSH (da LXC container).
Legge configurazione da config/nh_config.json.
"""
import subprocess, json, shutil, sys
from pathlib import Path
from datetime import datetime, timezone

# Trova la root del progetto NH-Mini (dove sta config/)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def load_config():
    """Carica config/nh_config.json per ottenere host Proxmox e parametri."""
    config_path = PROJECT_ROOT / "config" / "nh_config.json"
    if not config_path.exists():
        print(f"⚠️  Config non trovata: {config_path}")
        return None
    return json.loads(config_path.read_text())


def run_local(cmd):
    """Esegue comando locale."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def run_ssh(cmd, config):
    """Esegue comando su Proxmox via SSH."""
    host = config["proxmox"]["host"]
    user = config["proxmox"].get("user", "root")
    port = config["proxmox"].get("port", 22)
    timeout = config["proxmox"].get("timeout", 30)
    
    ssh_cmd = (
        f"ssh -i ~/.ssh/id_ed25519 "
        f"-o StrictHostKeyChecking=no "
        f"-o ConnectTimeout={timeout} "
        f"-o BatchMode=yes "
        f"-p {port} {user}@{host} "
        f"\"{cmd}\""
    )
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=timeout + 10)
    if result.returncode != 0 and result.stderr:
        # Non fatale, ritorna stringa vuota
        return ""
    return result.stdout.strip()


def run_cmd(cmd, config, use_ssh):
    """Esegue comando locale o via SSH in base alla modalità."""
    if use_ssh:
        return run_ssh(cmd, config)
    return run_local(cmd)


def parse_container_config(config_text):
    """Parsa l'output di 'pct config VMID' ed estrae i campi utili."""
    info = {
        "memory_mb": "unknown",
        "cpu_cores": "unknown",
        "ip_address": None,
        "gateway": None,
        "dns_servers": [],
        "template": None,
        "storage_gb": "unknown",
        "bridge": None,
        "storage_pool": None,
        "unprivileged": False,
        "features": [],
    }
    
    for line in config_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if line.startswith("memory:"):
            info["memory_mb"] = line.split(":")[1].strip()
        elif line.startswith("cores:"):
            info["cpu_cores"] = line.split(":")[1].strip()
        elif line.startswith("nameserver:"):
            info["dns_servers"] = line.split(":")[1].strip().split()
        elif line.startswith("unprivileged:"):
            info["unprivileged"] = line.split(":")[1].strip() == "1"
        elif line.startswith("features:"):
            info["features"] = line.split(":")[1].strip().split(",")
        elif line.startswith("rootfs:"):
            # rootfs: local-lvm:vm-200-disk-0,size=16G
            rootfs = line.split(":", 1)[1].strip()
            parts = rootfs.split(",")
            # Estrai storage pool
            if ":" in parts[0]:
                info["storage_pool"] = parts[0].split(":")[0].strip()
            for part in parts:
                if part.strip().startswith("size="):
                    size_str = part.strip().split("=")[1]
                    info["storage_gb"] = size_str.rstrip("G")
        elif "ip=" in line:
            # net0: name=eth0,bridge=vmbr0,hwaddr=...,ip=192.168.1.200/24,gw=192.168.1.1,...
            if "bridge=" in line:
                for part in line.split(","):
                    if part.strip().startswith("bridge="):
                        info["bridge"] = part.strip().split("=")[1]
            if "ip=" in line:
                for part in line.split(","):
                    if part.strip().startswith("ip="):
                        ip_raw = part.strip().split("=")[1]
                        info["ip_address"] = ip_raw.split("/")[0]
            if "gw=" in line:
                for part in line.split(","):
                    if part.strip().startswith("gw="):
                        info["gateway"] = part.strip().split("=")[1]
    
    return info


def discover(verbose=False):
    """Discovery principale. Rileva modalità (locale/SSH) e scansiona container."""
    config = load_config()
    
    # Determina modalità: locale se pct esiste, altrimenti SSH
    use_ssh = not shutil.which("pct")
    
    if use_ssh and not config:
        print("❌ pct non disponibile localmente e config/nh_config.json mancante.")
        print("   Non posso raggiungere Proxmox.")
        sys.exit(1)
    
    mode = "SSH" if use_ssh else "locale"
    if verbose:
        print(f"🔍 Modalità discovery: {mode}")
        if use_ssh:
            print(f"   Target: {config['proxmox']['user']}@{config['proxmox']['host']}")
    
    # Test connessione SSH se necessario
    if use_ssh:
        test = run_ssh("echo ok", config)
        if test != "ok":
            print(f"❌ SSH verso Proxmox fallito ({config['proxmox']['host']})")
            print("   Verifica: ssh -i ~/.ssh/id_ed25519 root@{host} 'echo ok'")
            sys.exit(1)
    
    # Ottieni lista container
    pct_output = run_cmd("pct list", config, use_ssh)
    if not pct_output:
        print("⚠️  pct list ha ritornato output vuoto")
        containers = []
    else:
        lines = pct_output.split("\n")[1:]  # Skip header
        containers = []
        
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            
            vmid = parts[0]
            status = parts[1]
            # Il nome può avere spazi, ma tipicamente è l'ultima colonna
            # Format: VMID       Status     Lock         Name
            name = parts[-1] if len(parts) > 2 else f"ct{vmid}"
            
            if verbose:
                print(f"   📦 Scanning CT{vmid} ({name})...")
            
            # Ottieni config dettagliata
            config_text = run_cmd(f"pct config {vmid}", config, use_ssh)
            info = parse_container_config(config_text)
            
            containers.append({
                "vmid": int(vmid),
                "name": name,
                "status": status,
                "ip_address": info["ip_address"],
                "gateway": info["gateway"],
                "dns_servers": info["dns_servers"],
                "resources": {
                    "memory_mb": info["memory_mb"],
                    "cpu_cores": info["cpu_cores"],
                    "storage_gb": info["storage_gb"],
                },
                "network": {
                    "bridge": info["bridge"],
                },
                "storage_pool": info["storage_pool"],
                "unprivileged": info["unprivileged"],
                "features": info["features"],
            })
    
    # Ottieni info nodo Proxmox
    proxmox_hostname = run_cmd("hostname", config, use_ssh)
    proxmox_version = run_cmd("pveversion 2>/dev/null | awk '{print $1}'", config, use_ssh)
    
    state = {
        "meta": {
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "discovery_version": "2.0",
            "discovery_mode": mode,
            "nh_version": "1.0",
        },
        "node": {
            "hostname": proxmox_hostname,
            "proxmox_version": proxmox_version,
        },
        "containers": sorted(containers, key=lambda c: c["vmid"]),
        "summary": {
            "total": len(containers),
            "running": len([c for c in containers if c["status"] == "running"]),
            "stopped": len([c for c in containers if c["status"] == "stopped"]),
        },
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    
    # Salva state
    state_dir = PROJECT_ROOT / "state"
    state_dir.mkdir(exist_ok=True)
    state_path = state_dir / "inventory.json"
    state_path.write_text(json.dumps(state, indent=2))
    
    return state


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    state = discover(verbose=verbose)
    
    summary = state["summary"]
    print(f"✅ Discovered {summary['total']} containers "
          f"({summary['running']} running, {summary['stopped']} stopped)")
    print(f"📁 State saved to state/inventory.json")
    print(f"🕐 Mode: {state['meta']['discovery_mode']}")
