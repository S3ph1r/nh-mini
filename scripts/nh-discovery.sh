#!/bin/bash
# nh-discovery.sh — wrapper per il daemon di discovery Proxmox
# Eseguito da systemd ogni ora per aggiornare state/inventory.json
# e generare il contesto AI aggiornato.

set -e

NH_ROOT="/home/Projects/NH-Mini"
LOG_FILE="/var/log/nh-mini/discovery.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p /var/log/nh-mini

echo "[$TIMESTAMP] Starting discovery..." >> "$LOG_FILE"

cd "$NH_ROOT"

# 1. Aggiorna inventory.json
if python3 core/discovery.py >> "$LOG_FILE" 2>&1; then
    echo "[$TIMESTAMP] inventory.json updated OK" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ERROR: discovery.py failed" >> "$LOG_FILE"
    exit 1
fi

# 2. Genera state/system-context.md — snapshot leggibile dall'agent
python3 - << 'EOF' >> "$LOG_FILE" 2>&1
import json
from pathlib import Path
from datetime import datetime, timezone

root = Path("/home/Projects/NH-Mini")
inventory = json.loads((root / "state/inventory.json").read_text())

real_vmids = {190, 120, 201, 202}
real_names = {"NH-Mini", "dias-brain", "ct201-dias-rt", "ct202-gateway"}

lines = [
    "# NH-Mini System Context — Auto-generated",
    f"generated: {datetime.now(timezone.utc).isoformat()}",
    f"proxmox: {inventory['node'].get('hostname', 'unknown')} ({inventory['node'].get('proxmox_version', '')})",
    "",
    "## Real Infrastructure",
    "| VMID | Name | Status | IP |",
    "|------|------|--------|----|",
]

for c in inventory["containers"]:
    if c["vmid"] in real_vmids or c["name"] in real_names:
        ip = c.get("ip_address") or "—"
        lines.append(f"| {c['vmid']} | {c['name']} | {c['status']} | {ip} |")

lines += [
    "",
    "## External Nodes",
    "| Node | IP | Role |",
    "|------|----|------|",
    "| PC Gaming (ARIA) | 192.168.1.139 | GPU inference (RTX 5060 Ti 16GB) |",
    "",
    "## Summary",
    f"total_containers: {inventory['summary']['total']}",
    f"running: {inventory['summary']['running']}",
    f"stopped: {inventory['summary']['stopped']}",
]

(root / "state/system-context.md").write_text("\n".join(lines))
print("system-context.md generated OK")
EOF

echo "[$TIMESTAMP] Discovery complete" >> "$LOG_FILE"
