#!/usr/bin/env python3
import json, os
from pathlib import Path
from datetime import datetime

def load_context():
    ctx = {"loaded_at": datetime.now().isoformat(), "host_reality": {}, "contracts": {}, "state": {}, "knowledge_index": []}
    hr = Path("core/host-reality.mdc")
    if hr.exists():
        ctx["host_reality"] = {"file": str(hr), "summary": "Proxmox/LXC/vmbr0"}
    dc = Path("core/description-contracts.mdc")
    if dc.exists():
        ctx["contracts"] = {"file": str(dc), "contracts": ["resource_declaration", "secrets_handling", "deployment_workflow", "network_exposure"]}
    inv = Path("state/inventory.json")
    if inv.exists():
        state = json.loads(inv.read_text())
        containers = state.get("containers", [])
        mtime = datetime.fromtimestamp(os.path.getmtime(inv))
        age_min = max(0, int((datetime.now() - mtime).total_seconds() / 60))
        ctx["state"] = {"file": str(inv), "containers_count": len(containers), "containers": [f"{c.get('vmid')}:{c.get('name')}" for c in containers[:5]], "state_age_minutes": age_min}
    cr = Path(".cursorrules")
    if cr.exists():
        lines = cr.read_text().split("\n")
        knowledge = [l.strip()[2:] for l in lines if l.strip().startswith('- "')]
        ctx["knowledge_index"] = knowledge[:10]
    return ctx

if __name__ == "__main__":
    print(json.dumps(load_context(), indent=2))
