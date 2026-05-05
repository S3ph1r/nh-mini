#!/usr/bin/env python3
import json, os
from pathlib import Path
from datetime import datetime

def load_context():
    ctx = {"loaded_at": datetime.now().isoformat(), "host_reality": {}, "contracts": {}, "state": {}, "workspace": {}, "knowledge_index": []}
    hr = Path("core/host-reality.mdc")
    if hr.exists():
        ctx["host_reality"] = {"file": str(hr), "summary": "Proxmox/LXC/vmbr0"}
    dc = Path("core/description-contracts.mdc")
    if dc.exists():
        ctx["contracts"] = {"file": str(dc), "contracts": ["resource_declaration", "secrets_handling", "deployment_workflow", "network_exposure", "project_context"]}
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
        knowledge = [l.strip().split("→ ")[-1].strip() for l in lines if "→" in l and "knowledge/" in l]
        ctx["knowledge_index"] = knowledge[:15]
    
    # Carica workspace info
    ws_config = Path("workspace/active_config.json")
    if ws_config.exists():
        try:
            ws_data = json.loads(ws_config.read_text())
            current_link = Path("workspace/current_project")
            if current_link.is_symlink():
                target = current_link.readlink()
                ctx["workspace"] = {
                    "active_project": ws_data.get("active", "unknown"),
                    "target_path": str(target),
                    "last_switch": ws_data.get("last_switch", "unknown")
                }
            else:
                ctx["workspace"] = {"status": "no_symlink"}
        except Exception as e:
            ctx["workspace"] = {"error": str(e)}
    else:
        ctx["workspace"] = {"status": "no_config"}

    # Carica service catalog (no probe in loader per velocità — usare service_catalog.py per probe live)
    try:
        import sys as _sys
        _root = str(Path(__file__).resolve().parent.parent)
        if _root not in _sys.path:
            _sys.path.insert(0, _root)
        from core.service_catalog import get_catalog
        catalog = get_catalog(probe=False)
        ctx["service_catalog"] = {
            key: {"name": svc["name"], "endpoint": f"{svc.get('host','')}:{svc.get('port','')}" if svc.get("port") else svc.get("host",""), "purpose": svc["purpose"]}
            for key, svc in catalog.items()
            if not key.startswith("_")
        }
    except Exception as e:
        ctx["service_catalog"] = {"error": str(e)}

    # Carica system-context.md (snapshot infra real generato dal daemon)
    sys_ctx = Path("state/system-context.md")
    if sys_ctx.exists():
        ctx["system_context_file"] = str(sys_ctx)

    return ctx

if __name__ == "__main__":
    print(json.dumps(load_context(), indent=2))
