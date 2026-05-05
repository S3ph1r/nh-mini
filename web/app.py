#!/usr/bin/env python3
"""
NH-Mini Dashboard — FastAPI backend
Serve la dashboard di controllo per CT190.
Porta: 8080
"""
import json
import subprocess
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
SVILUPPI_DIR = ROOT / "sviluppi"
WORKSPACE_CONFIG = ROOT / "workspace" / "active_config.json"
KNOWLEDGE_INFRA = ROOT / "knowledge" / "containers" / "infrastructure-map.mdc"

app = FastAPI(title="NH-Mini Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REAL_VMIDS = {120, 190, 201, 202}

# ── helpers ──────────────────────────────────────────────────────────────────

def load_inventory() -> dict:
    path = STATE_DIR / "inventory.json"
    if not path.exists():
        return {"containers": [], "summary": {}, "node": {}, "meta": {}}
    return json.loads(path.read_text())


def load_workspace() -> dict:
    if not WORKSPACE_CONFIG.exists():
        return {}
    return json.loads(WORKSPACE_CONFIG.read_text())


def get_projects() -> list[dict]:
    projects = []
    if not SVILUPPI_DIR.exists():
        return projects

    for d in sorted(SVILUPPI_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name.startswith("_"):
            continue

        ctx_path = d / ".project-context"
        ctx = {}
        if ctx_path.exists():
            try:
                ctx = yaml.safe_load(ctx_path.read_text()) or {}
            except Exception:
                try:
                    ctx = json.loads(ctx_path.read_text())
                except Exception:
                    pass

        identity = ctx.get("IDENTITY", ctx.get("identity", {}))
        description = (
            identity.get("description", "")
            or ctx.get("description", "")
        )
        stack = identity.get("stack", "")

        projects.append({
            "name": d.name,
            "path": str(d),
            "has_context": ctx_path.exists(),
            "description": str(description).strip() if description else "",
            "stack": stack,
            "status": ctx.get("STATUS", ctx.get("status", "development")),
            "version": identity.get("version", ctx.get("version", "")),
            "last_modified": datetime.fromtimestamp(
                d.stat().st_mtime, tz=timezone.utc
            ).isoformat(),
        })

    return projects


def run_ssh_proxmox(cmd: str) -> str:
    try:
        cfg_path = ROOT / "config" / "nh_config.json"
        cfg = json.loads(cfg_path.read_text())
        host = cfg["proxmox"]["host"]
        result = subprocess.run(
            f"ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o BatchMode=yes root@{host} \"{cmd}\"",
            shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "online", "service": "nh-mini-dashboard", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/overview")
def overview():
    inv = load_inventory()
    ws = load_workspace()
    projects = get_projects()
    containers = inv.get("containers", [])

    real = [c for c in containers if c["vmid"] in REAL_VMIDS]
    running = sum(1 for c in real if c["status"] == "running")

    return {
        "node": inv.get("node", {}),
        "real_infrastructure": {
            "total": len(real),
            "running": running,
            "stopped": len(real) - running,
        },
        "all_containers": inv.get("summary", {}),
        "projects": {
            "total": len(projects),
            "active_workspace": ws.get("active", "none"),
        },
        "last_discovery": inv.get("meta", {}).get("discovered_at"),
        "external_nodes": [
            {"name": "PC Gaming (ARIA)", "ip": "192.168.1.139", "role": "GPU inference RTX 5060 Ti 16GB"}
        ],
    }


@app.get("/api/infrastructure")
def infrastructure():
    inv = load_inventory()
    containers = inv.get("containers", [])

    real = [c for c in containers if c["vmid"] in REAL_VMIDS]
    legacy = [c for c in containers if c["vmid"] not in REAL_VMIDS]

    return {
        "real": real,
        "legacy": legacy,
        "external": [
            {"name": "PC Gaming (ARIA)", "ip": "192.168.1.139", "os": "Windows 11",
             "role": "ARIA Node Controller — GPU inference", "status": "on-demand"}
        ],
        "last_updated": inv.get("last_updated"),
    }


@app.get("/api/projects")
def projects_list():
    ws = load_workspace()
    projects = get_projects()
    active = ws.get("active", "")
    for p in projects:
        p["is_active"] = (p["name"].lower() == active.lower())
    return {"projects": projects, "active_workspace": active}


@app.get("/api/projects/{name}/context")
def project_context(name: str):
    project_dir = SVILUPPI_DIR / name
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    ctx_path = project_dir / ".project-context"
    if not ctx_path.exists():
        raise HTTPException(status_code=404, detail="No .project-context found")

    try:
        return json.loads(ctx_path.read_text())
    except Exception:
        return {"raw": ctx_path.read_text()}


@app.post("/api/containers/{vmid}/start")
def container_start(vmid: int):
    output = run_ssh_proxmox(f"pct start {vmid}")
    return {"vmid": vmid, "action": "start", "output": output}


@app.post("/api/containers/{vmid}/stop")
def container_stop(vmid: int):
    output = run_ssh_proxmox(f"pct stop {vmid}")
    return {"vmid": vmid, "action": "stop", "output": output}


@app.get("/api/services")
def services_list(probe: bool = False):
    import sys
    sys.path.insert(0, str(ROOT))
    from core.service_catalog import get_catalog
    catalog = get_catalog(probe=probe)
    return catalog


@app.post("/api/discovery/refresh")
def discovery_refresh():
    try:
        result = subprocess.run(
            ["/home/Projects/NH-Mini/scripts/nh-discovery.sh"],
            capture_output=True, text=True, timeout=60
        )
        return {"status": "ok" if result.returncode == 0 else "error", "output": result.stdout + result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
def alerts_list():
    """Ritorna gli alert attivi dal daemon heartbeat (state/alerts.json)."""
    path = STATE_DIR / "alerts.json"
    if not path.exists():
        return {
            "generated_at": None,
            "summary": {"total": 0, "high": 0, "medium": 0, "low": 0},
            "alerts": [],
            "healthy": [],
            "containers_checked": [],
            "heartbeat_status": "no_data",
        }
    data = json.loads(path.read_text())
    data["heartbeat_status"] = "ok"
    return data


@app.post("/api/heartbeat/run")
def heartbeat_run():
    """Trigger manuale del heartbeat (genera/aggiorna state/alerts.json)."""
    try:
        result = subprocess.run(
            ["python3", "/home/Projects/NH-Mini/core/heartbeat.py"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/Projects/NH-Mini"
        )
        return {
            "status": "ok" if result.returncode in (0, 1) else "error",
            "output": result.stdout[-2000:] + result.stderr[-500:],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/handover")
def handover():
    """Ritorna il session handover summary (state/session-handover.md)."""
    path = STATE_DIR / "session-handover.md"
    if not path.exists():
        return {"content": None, "exists": False}
    return {"content": path.read_text(), "exists": True}




# ── Static files + SPA ───────────────────────────────────────────────────────

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{path:path}")
def spa_fallback(path: str):
    candidate = STATIC_DIR / path
    if candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
