#!/usr/bin/env python3
"""
heartbeat.py — Daemon di monitoring NH-Mini.

Esegue probe su tutti i servizi del service catalog e sui container SOT,
scrive lo stato in state/alerts.json. Progettato per essere eseguito da
systemd timer ogni 5 minuti.

Comportamento:
  - Legge i servizi da core/service_catalog.py (STATIC_CATALOG) — dinamico
  - Legge lo stato container da state/inventory.json
  - Fa TCP probe su ogni servizio con porta
  - Genera/aggiorna state/alerts.json con alert attivi e risolti
  - Mantiene storico alert (non li cancella al primo probe OK — "resolved" invece)
  - Log in /var/log/nh-mini/heartbeat.log

Schema state/alerts.json:
  {
    "generated_at": "ISO8601",
    "summary": {"total": N, "high": N, "medium": N, "low": N},
    "alerts": [
      {
        "id": "redis-down-20260501T0923",
        "service_key": "redis",
        "service_name": "Redis Universal State Bus",
        "severity": "HIGH",
        "type": "SERVICE_DOWN | CONTAINER_STOPPED | DEGRADED",
        "message": "Redis non raggiungibile (TCP probe fallito su 192.168.1.120:6379)",
        "first_seen": "ISO8601",
        "last_checked": "ISO8601",
        "status": "active | resolved",
        "resolved_at": null | "ISO8601"
      }
    ],
    "healthy": ["gateway", "nh_mini_api"],
    "containers_checked": [{"vmid": 120, "name": "ct120-redis", "status": "running"}]
  }

Uso:
  python3 core/heartbeat.py           # esecuzione singola (da systemd)
  python3 core/heartbeat.py --dry-run # mostra cosa farebbe senza scrivere
  python3 core/heartbeat.py --watch   # loop ogni 30s (debug locale)
"""

import json
import sys
import socket
import logging
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
ALERTS_PATH = ROOT / "state" / "alerts.json"
LOG_PATH = Path("/var/log/nh-mini/heartbeat.log")

# Severity per tipo servizio
SERVICE_SEVERITY = {
    "redis":       "HIGH",    # bus condiviso: se cade, tutto cade
    "gateway":     "HIGH",    # internet entry point
    "aria_node":   "MEDIUM",  # on-demand, può essere spento
    "nh_mini_api": "LOW",     # la dashboard stessa
    "dias_api":    "HIGH",    # API runtime DIAS
    "sops_age":    "LOW",     # locale, non ha TCP probe
}

REAL_VMIDS = {120, 190, 201, 202}

# ── logging ───────────────────────────────────────────────────────────────────

def setup_logging(dry_run: bool = False):
    handlers = [logging.StreamHandler(sys.stdout)]
    if not dry_run:
        try:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(LOG_PATH))
        except PermissionError:
            pass  # non fatale — log solo su stdout

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [heartbeat] %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=handlers,
    )

log = logging.getLogger("heartbeat")


# ── helpers ───────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def probe_tcp(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError, socket.timeout):
        return False


def load_inventory() -> list[dict]:
    path = ROOT / "state" / "inventory.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text()).get("containers", [])
    except Exception:
        return []


def load_existing_alerts() -> dict:
    if not ALERTS_PATH.exists():
        return {"alerts": [], "healthy": [], "containers_checked": []}
    try:
        return json.loads(ALERTS_PATH.read_text())
    except Exception:
        return {"alerts": [], "healthy": [], "containers_checked": []}


def make_alert_id(service_key: str, alert_type: str) -> str:
    """ID stabile per un alert — non cambia tra probe successivi per lo stesso problema."""
    return f"{service_key}-{alert_type.lower()}"


# ── probe logic ───────────────────────────────────────────────────────────────

def probe_services(catalog: dict) -> tuple[list[dict], list[str]]:
    """
    Probe tutti i servizi nel catalog.
    Ritorna (new_alerts, healthy_keys).
    """
    new_alerts = []
    healthy = []

    for key, svc in catalog.items():
        if key.startswith("_"):
            continue

        host = svc.get("host")
        port = svc.get("port")
        name = svc.get("name", key)
        severity = SERVICE_SEVERITY.get(key, "MEDIUM")

        if not port:
            # Servizio locale senza porta TCP (es. sops_age) — skip probe
            log.info(f"  SKIP {key} — no TCP port")
            healthy.append(key)
            continue

        reachable = probe_tcp(host, port)
        if reachable:
            log.info(f"  OK   {key} ({host}:{port})")
            healthy.append(key)
        else:
            log.warning(f"  DOWN {key} ({host}:{port}) — probe failed")
            new_alerts.append({
                "id": make_alert_id(key, "service_down"),
                "service_key": key,
                "service_name": name,
                "severity": severity,
                "type": "SERVICE_DOWN",
                "message": f"{name} non raggiungibile (TCP probe fallito su {host}:{port})",
                "endpoint": f"{host}:{port}",
            })

    return new_alerts, healthy


def probe_containers(containers: list[dict]) -> list[dict]:
    """
    Verifica stato container SOT da inventory.json.
    Ritorna lista alert per container non running.
    """
    new_alerts = []
    real = [c for c in containers if c.get("vmid") in REAL_VMIDS]

    for c in real:
        vmid = c.get("vmid")
        name = c.get("name", f"ct{vmid}")
        status = c.get("status", "unknown")

        if status == "running":
            log.info(f"  OK   CT{vmid} ({name}) — {status}")
        else:
            log.warning(f"  DOWN CT{vmid} ({name}) — status: {status}")
            new_alerts.append({
                "id": make_alert_id(f"ct{vmid}", "container_stopped"),
                "service_key": f"ct{vmid}",
                "service_name": f"Container CT{vmid} ({name})",
                "severity": "HIGH",
                "type": "CONTAINER_STOPPED",
                "message": f"Container CT{vmid} ({name}) non è in stato running (status: {status})",
                "vmid": vmid,
            })

    return new_alerts


# ── alert merge ───────────────────────────────────────────────────────────────

def merge_alerts(existing_alerts: list[dict], new_alerts: list[dict], healthy_keys: list[str]) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Merge degli alert esistenti con quelli nuovi.
    - Alert già esistente + ancora in fault → aggiorna last_checked
    - Alert già esistente + ora healthy → marca resolved
    - Alert nuovo → aggiunge con first_seen = now
    - Alert già risolti da più di 24h → rimuove (pulizia storico)
    """
    now = now_iso()
    existing_by_id = {a["id"]: a for a in existing_alerts}
    new_by_id = {a["id"]: a for a in new_alerts}
    result = []
    newly_triggered = []
    newly_resolved = []

    # Processa alert nuovi (aggiungi o aggiorna)
    for alert_id, alert in new_by_id.items():
        if alert_id in existing_by_id:
            # Alert già noto — aggiorna last_checked, mantieni first_seen
            existing = existing_by_id[alert_id]
            existing["last_checked"] = now
            existing["status"] = "active"
            existing["resolved_at"] = None
            existing["message"] = alert["message"]  # aggiorna messaggio
            result.append(existing)
        else:
            # Alert nuovo
            alert["first_seen"] = now
            alert["last_checked"] = now
            alert["status"] = "active"
            alert["resolved_at"] = None
            result.append(alert)
            newly_triggered.append(alert)
            log.info(f"  NEW ALERT: {alert_id} — {alert['message']}")

    # Processa alert esistenti non più in fault
    for alert_id, existing in existing_by_id.items():
        if alert_id in new_by_id:
            continue  # già processato
        if existing.get("status") == "resolved":
            # Già risolto — mantieni per 24h poi rimuovi
            result.append(existing)
        else:
            # Era attivo, ora non c'è più — risolto
            existing["status"] = "resolved"
            existing["resolved_at"] = now
            existing["last_checked"] = now
            result.append(existing)
            newly_resolved.append(existing)
            log.info(f"  RESOLVED: {alert_id}")

    return result, newly_triggered, newly_resolved


def clean_old_resolved(alerts: list[dict], max_age_hours: int = 24) -> list[dict]:
    """Rimuove alert risolti da più di max_age_hours."""
    now = datetime.now(timezone.utc)
    result = []
    for a in alerts:
        if a.get("status") != "resolved":
            result.append(a)
            continue
        resolved_at = a.get("resolved_at")
        if not resolved_at:
            result.append(a)
            continue
        try:
            resolved_dt = datetime.fromisoformat(resolved_at)
            age_hours = (now - resolved_dt).total_seconds() / 3600
            if age_hours < max_age_hours:
                result.append(a)
            else:
                log.info(f"  CLEANUP resolved alert: {a['id']} (age: {age_hours:.1f}h)")
        except ValueError:
            result.append(a)
    return result


# ── main ──────────────────────────────────────────────────────────────────────

def run_heartbeat(dry_run: bool = False) -> dict:
    """
    Esegue un ciclo completo di heartbeat.
    Ritorna il contenuto di alerts.json aggiornato.
    """
    log.info("=== NH-Mini Heartbeat ===")

    # Importa service catalog (dinamico — si aggiorna con il sistema)
    sys.path.insert(0, str(ROOT))
    try:
        from core.service_catalog import STATIC_CATALOG
        catalog = STATIC_CATALOG
    except ImportError as e:
        log.error(f"Impossibile importare service_catalog: {e}")
        catalog = {}

    # Probe servizi
    log.info("── Service probe ─────────────────")
    service_alerts, healthy_services = probe_services(catalog)

    # Probe container
    log.info("── Container probe ───────────────")
    containers = load_inventory()
    container_alerts = probe_containers(containers)

    all_new_alerts = service_alerts + container_alerts

    # Merge con storico
    existing = load_existing_alerts()
    merged, newly_triggered, newly_resolved = merge_alerts(existing.get("alerts", []), all_new_alerts, healthy_services)
    merged = clean_old_resolved(merged)

    # Calcola summary
    active = [a for a in merged if a.get("status") == "active"]
    summary = {
        "total": len(active),
        "high":   sum(1 for a in active if a.get("severity") == "HIGH"),
        "medium": sum(1 for a in active if a.get("severity") == "MEDIUM"),
        "low":    sum(1 for a in active if a.get("severity") == "LOW"),
    }

    # Container SOT snapshot
    real_containers = [
        {"vmid": c["vmid"], "name": c.get("name", ""), "status": c.get("status", "unknown")}
        for c in containers if c.get("vmid") in REAL_VMIDS
    ]

    result = {
        "generated_at": now_iso(),
        "summary": summary,
        "alerts": merged,
        "healthy": healthy_services,
        "containers_checked": real_containers,
    }

    if dry_run:
        log.info("── DRY RUN — nessuna scrittura ──")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        ALERTS_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        log.info(f"── state/alerts.json aggiornato ─")
        
        # Invio notifiche Push via Telegram
        if newly_triggered or newly_resolved:
            log.info("── Invio Notifiche Telegram ──────")
            try:
                from core.telegram_bot import TelegramBot
                bot = TelegramBot()
                if bot.is_configured():
                    for alert in newly_triggered:
                        bot.send_alert(alert)
                    for alert in newly_resolved:
                        bot.send_message(f"✅ <b>RISOLTO</b>\nIl servizio <b>{alert.get('service_name', alert.get('service_key'))}</b> è tornato operativo.")
            except Exception as e:
                log.error(f"Errore invio Telegram: {e}")

    log.info(f"Summary: {summary['total']} alert attivi "
             f"(HIGH:{summary['high']} MED:{summary['medium']} LOW:{summary['low']})")
    log.info("=== Done ===")

    return result


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    watch   = "--watch" in sys.argv

    setup_logging(dry_run=dry_run)

    if watch:
        interval = 30
        log.info(f"Watch mode: probe ogni {interval}s (Ctrl+C per uscire)")
        while True:
            run_heartbeat(dry_run=dry_run)
            time.sleep(interval)
    else:
        result = run_heartbeat(dry_run=dry_run)
        # Exit code non-zero se ci sono alert HIGH
        high_count = result["summary"]["high"]
        sys.exit(1 if high_count > 0 else 0)
