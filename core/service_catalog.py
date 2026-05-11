"""
service_catalog.py — Catalogo dei servizi disponibili a runtime.

Quando l'agent inizia una sessione di sviluppo, questo modulo fornisce
la "foto" di cosa è già disponibile nell'infrastruttura: Redis, gateway,
ARIA, storage, ecc. Evita di progettare da zero servizi già esistenti.

Uso:
    from core.service_catalog import get_catalog
    catalog = get_catalog()
    # catalog["redis"] → {"endpoint": "192.168.1.120:6379", "status": "available", ...}
"""

import json
import socket
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _probe_tcp(host: str, port: int, timeout: float = 2.0) -> bool:
    """Prova una connessione TCP per verificare se un servizio è raggiungibile."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def _load_inventory() -> list[dict]:
    path = PROJECT_ROOT / "state" / "inventory.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data.get("containers", [])


STATIC_CATALOG: dict[str, dict] = {
    "redis": {
        "name": "Redis Universal State Bus",
        "container": "CT120 (ct120-redis)",
        "host": "192.168.1.120",
        "port": 6379,
        "purpose": "Job queue e state bus condiviso. Usato da DIAS (pipeline) e ARIA (GPU jobs).",
        "pattern": "BRPOP/LPUSH per job queue, GET/SET per state, HSET per config",
        "consumers": ["DIAS pipeline", "ARIA Node Controller"],
        "notes": "maxmemory=2GB, policy=allkeys-lru, snapshot ogni 60s",
        "diagnostic": "ssh root@192.168.1.120 'journalctl -u redis-server -n 15 --no-pager'",
        "remediation": "ssh root@192.168.1.120 'systemctl restart redis-server'",
    },
    "gateway": {
        "name": "Internet Gateway",
        "container": "CT202 (ct202-gateway)",
        "host": "192.168.1.202",
        "port": 80,
        "purpose": "Unico punto di ingresso HTTP dall'esterno via ngrok + nginx reverse proxy.",
        "pattern": "nginx routing per path → target container. ngrok tunnel permanente.",
        "notes": "Aggiungere route in nginx.conf per esporre nuove app. 256MB RAM.",
        "ngrok_url": "obliging-fitting-cheetah.ngrok-free.app",
        "diagnostic": "ssh root@192.168.1.202 'journalctl -u nginx -n 15 --no-pager'",
        "remediation": "ssh root@192.168.1.202 'systemctl restart nginx'",
    },
    "aria_node": {
        "name": "ARIA Node Controller",
        "host": "192.168.1.139",
        "port": 8082,
        "purpose": "Inferenza AI su GPU (RTX 5060 Ti 16GB). TTS, ACE-Step, ASR, LLM.",
        "pattern": "Jobs via Redis su CT120. Output serviti via HTTP Asset Server :8082.",
        "backends": {
            "fish_tts": ":8080",
            "voice_cloning": ":8081",
            "asset_server": ":8082",
            "lifelog_asr": ":8087",
        },
        "os": "Windows 11",
        "notes": "On-demand. Comunica via Redis, non richiede SSH. SOT codice: PC139.",
        "diagnostic": "ssh roberto@192.168.1.139 'powershell -Command \"Get-Content C:\\Logs\\aria_node.log -Tail 15\"'",
        "remediation": "ssh roberto@192.168.1.139 'pm2 restart aria_node'",
    },
    "nh_mini_api": {
        "name": "NH-Mini Dashboard API",
        "container": "CT190 (NH-Mini)",
        "host": "192.168.1.190",
        "port": 8080,
        "purpose": "API di controllo NH-Mini — inventory, progetti, discovery refresh.",
        "endpoints": [
            "GET /api/overview",
            "GET /api/infrastructure",
            "GET /api/projects",
            "POST /api/discovery/refresh",
            "POST /api/containers/{vmid}/start|stop",
        ],
        "diagnostic": "journalctl -u nh-mini-api -n 15 --no-pager",
        "remediation": "systemctl restart nh-mini-api",
    },
    "dias_api": {
        "name": "DIAS API Hub",
        "container": "CT201 (dias-rt)",
        "host": "192.168.1.201",
        "port": 8000,
        "purpose": "API Hub DIAS — gestione progetti audiobook, pipeline control, voice registry.",
        "pattern": "REST API + SvelteKit dashboard embedded",
        "notes": "Per usare DIAS da altri progetti: chiamare /api/ su CT201:8000. Nota: Esiste istanza dev su CT190:8000.",
        "diagnostic": "ssh root@192.168.1.201 'journalctl -u dias-api -n 15 --no-pager'",
        "remediation": "ssh root@192.168.1.201 'systemctl restart dias-api'",
    },
    "stratex_dev": {
        "name": "Stratex Dev Dashboard",
        "container": "CT190 (NH-Mini)",
        "host": "192.168.1.190",
        "port": 8001,
        "purpose": "Wealth Intelligence System — Dashboard di sviluppo e API ingestion.",
        "pattern": "FastAPI (8001) + Vite/React (5174)",
        "notes": "In fase di sviluppo attivo su LXC 190. Database su CT105.",
        "diagnostic": "ps aux | grep stratex",
        "remediation": "kill -9 $(lsof -t -i:8001)",
    },
    "lifelog2_dev": {
        "name": "Lifelog2 Dev API",
        "container": "CT190 (NH-Mini)",
        "host": "192.168.1.190",
        "port": 8002,
        "purpose": "Personal memory operating layer — Backend di sviluppo.",
        "pattern": "FastAPI (8002) + SvelteKit (5173)",
        "notes": "In fase di sviluppo attivo su LXC 190. Database su CT105.",
        "diagnostic": "ls -R sviluppi/Lifelog2",
        "remediation": "kill -9 $(lsof -t -i:8002)",
    },
    "lifelog2_rt": {
        "name": "Lifelog2 Runtime API",
        "container": "CT203 (Lifelog (v2))",
        "host": "192.168.1.203",
        "port": 8002,
        "purpose": "Personal memory operating layer — Dashboard e API di produzione.",
        "pattern": "FastAPI (8002) + SvelteKit Dashboard",
        "notes": "Target runtime per Lifelog2. SOT per la memoria dell'utente.",
        "diagnostic": "ssh root@192.168.1.203 'journalctl -u lifelog2-api -n 15 --no-pager'",
        "remediation": "ssh root@192.168.1.203 'systemctl restart lifelog2-api'",
    },
    "sops_age": {
        "name": "SOPS+Age Credential Manager",
        "host": "CT190 (local)",
        "port": None,
        "purpose": "Gestione credenziali cifrate. Nessuna credenziale hardcoded.",
        "pattern": "namespace: service.key → scripts/credential_manager.py --get service.key",
        "notes": "Age key in ~/.config/sops/age/keys.txt. File cifrati in secrets/",
    },
}


def get_catalog(probe: bool = True) -> dict[str, dict]:
    """
    Ritorna il catalogo dei servizi con stato runtime opzionale (TCP probe).

    Args:
        probe: Se True, verifica la raggiungibilità via TCP (aggiunge ~2s per servizio down).
    """
    containers = _load_inventory()
    container_status = {c["vmid"]: c["status"] for c in containers}

    catalog = {}
    for key, svc in STATIC_CATALOG.items():
        entry = dict(svc)
        entry["key"] = key

        host = svc.get("host")
        port = svc.get("port")

        if probe and host and port:
            entry["reachable"] = _probe_tcp(host, port)
            entry["status"] = "available" if entry["reachable"] else "unreachable"
        elif probe and host and not port:
            entry["reachable"] = None
            entry["status"] = "local"
        else:
            entry["reachable"] = None
            entry["status"] = "unknown"

        catalog[key] = entry

    catalog["_meta"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "probe_enabled": probe,
        "containers_snapshot": len(containers),
    }
    return catalog


def catalog_summary(probe: bool = True) -> str:
    """Ritorna un sommario testuale del catalogo — per includere nel contesto agent."""
    catalog = get_catalog(probe=probe)
    lines = ["## Available Services (NH-Mini Service Catalog)", ""]

    for key, svc in catalog.items():
        if key.startswith("_"):
            continue
        status = svc.get("status", "unknown")
        icon = "🟢" if status == "available" else "🔴" if status == "unreachable" else "⚪"
        host_info = f"{svc.get('host', '')}:{svc.get('port', '')}" if svc.get("port") else svc.get("host", "")
        lines.append(f"### {icon} {svc['name']} (`{key}`)")
        lines.append(f"- **endpoint**: {host_info}")
        lines.append(f"- **purpose**: {svc['purpose']}")
        if svc.get("pattern"):
            lines.append(f"- **pattern**: {svc['pattern']}")
        if svc.get("notes"):
            lines.append(f"- **note**: {svc['notes']}")
        lines.append("")

    meta = catalog.get("_meta", {})
    lines.append(f"_Generated: {meta.get('generated_at', '')} · probe: {meta.get('probe_enabled')}_")
    return "\n".join(lines)


if __name__ == "__main__":
    print(catalog_summary(probe=True))
