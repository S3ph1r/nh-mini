#!/usr/bin/env python3
import subprocess, json, shutil
from pathlib import Path
from datetime import datetime

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def discover():
    containers = []
    if shutil.which("pct"):
        lines = run("pct list").split("\n")[1:]
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            vmid = parts[0]
            status = parts[1] if len(parts) > 1 else "unknown"
            name = parts[-1] if len(parts) > 2 else f"ct{vmid}"
            config = run(f"pct config {vmid}")
            memory = "unknown"
            cores = "unknown"
            ip = None
            for cfg_line in config.split("\n"):
                if cfg_line.startswith("memory:"):
                    memory = cfg_line.split(":")[1].strip()
                elif cfg_line.startswith("cores:"):
                    cores = cfg_line.split(":")[1].strip()
                elif "ip=" in cfg_line:
                    ip = cfg_line.split("ip=")[1].split("/")[0].strip()
            containers.append({
                "vmid": int(vmid),
                "name": name,
                "status": status,
                "ip": ip,
                "resources": {"memory_mb": memory, "cores": cores},
                "nh_metadata": {"managed": name == "nh-core", "project_id": None, "deployed_standard": None}
            })
    state = {
        "meta": {
            "discovered_at": datetime.now().isoformat(),
            "discovery_version": "1.0",
            "nh_version": "1.0"
        },
        "node": {
            "hostname": run("hostname"),
            "proxmox_version": run("pveversion | awk '{print $2}'") if shutil.which("pveversion") else ""
        },
        "containers": containers
    }
    Path("state").mkdir(exist_ok=True)
    Path("state/inventory.json").write_text(json.dumps(state, indent=2))
    return state

if __name__ == "__main__":
    s = discover()
    print(f"Discovered {len(s['containers'])} containers")
    print("State saved to state/inventory.json")
