#!/usr/bin/env python3
"""
cf-url-watcher.py — Monitora l'URL del Cloudflare Quick Tunnel su CT202.

Legge http://192.168.1.202/gateway/cf-url.txt ogni minuto (via cf-url-watcher.timer).
Se l'URL cambia rispetto all'ultimo valore noto:
  1. Aggiorna /etc/authelia/configuration.yml su CT202 (sostituzione stringa
     esatta vecchio→nuovo hostname sui blocchi access_control/session) e
     riavvia authelia.service — senza questo passo Authelia risponde 400 su
     ogni auth_request per url che non riconosce (visto il 2026-07-15: Shifter
     bloccato dopo un semplice riavvio del tunnel, causa non ovvia da log).
  2. Invia notifica Telegram con l'esito di entrambi i passi (non solo l'URL).

State file: state/cf-url-last.txt
"""

import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "state" / "cf-url-last.txt"
CF_URL_ENDPOINT = "http://192.168.1.202/gateway/cf-url.txt"

GATEWAY_HOST = "192.168.1.202"
AUTHELIA_CONFIG = "/etc/authelia/configuration.yml"
SSH_TIMEOUT_S = 15

sys.path.insert(0, str(ROOT))
from core.telegram_bot import TelegramBot


def fetch_current_url() -> str | None:
    try:
        req = urllib.request.Request(CF_URL_ENDPOINT, headers={"User-Agent": "nh-mini-watcher"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.read().decode().strip()
    except Exception as e:
        print(f"[cf-url-watcher] Fetch fallito: {e}", file=sys.stderr)
        return None


def load_last_url() -> str | None:
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip() or None
    return None


def save_url(url: str):
    STATE_FILE.write_text(url + "\n")


def _run_ssh(remote_cmd: str) -> subprocess.CompletedProcess:
    """Stesso pattern di core/discovery.py:run_ssh — root key, no host-key prompt."""
    ssh_cmd = (
        f"ssh -i ~/.ssh/id_ed25519 "
        f"-o StrictHostKeyChecking=no "
        f"-o ConnectTimeout={SSH_TIMEOUT_S} "
        f"-o BatchMode=yes "
        f"root@{GATEWAY_HOST} "
        f"\"{remote_cmd}\""
    )
    return subprocess.run(
        ssh_cmd, shell=True, capture_output=True, text=True, timeout=SSH_TIMEOUT_S + 10
    )


def update_authelia_domain(old_host: str, new_host: str) -> tuple[bool, str]:
    """Sostituisce old_host → new_host in configuration.yml su CT202 e riavvia
    authelia. Tutti i riferimenti nel file sono la stessa stringa esatta
    (dominio access_control + session + redirection URL) — sed one-liner,
    niente parsing YAML. Ritorna (successo, messaggio diagnostico)."""
    escaped_old = old_host.replace(".", r"\.")
    sed_cmd = f"sed -i 's/{escaped_old}/{new_host}/g' {AUTHELIA_CONFIG}"
    r = _run_ssh(sed_cmd)
    if r.returncode != 0:
        return False, f"sed fallito su configuration.yml: {r.stderr.strip()[:200]}"

    # Verifica che la sostituzione abbia davvero preso piede prima di riavviare
    check = _run_ssh(f"grep -c '{new_host}' {AUTHELIA_CONFIG}")
    if check.returncode != 0 or not check.stdout.strip() or check.stdout.strip() == "0":
        return False, "sed eseguito ma nessuna occorrenza del nuovo host trovata nel file — non riavvio Authelia"

    restart = _run_ssh("systemctl restart authelia")
    if restart.returncode != 0:
        return False, f"config aggiornata ma restart authelia fallito: {restart.stderr.strip()[:200]}"

    # Conferma che il servizio sia tornato attivo, non solo che il comando sia uscito con rc=0
    status = _run_ssh("systemctl is-active authelia")
    if status.stdout.strip() != "active":
        return False, f"restart eseguito ma authelia non risulta active (stato: {status.stdout.strip()})"

    return True, f"configuration.yml aggiornato ({check.stdout.strip()} occorrenze) e authelia riavviato correttamente"


def main():
    current = fetch_current_url()
    if not current:
        print("[cf-url-watcher] URL non disponibile — CT202 raggiungibile?")
        return

    last = load_last_url()

    if current == last:
        print(f"[cf-url-watcher] URL invariata: {current}")
        return

    is_first = last is None
    save_url(current)

    if is_first:
        print(f"[cf-url-watcher] Prima rilevazione URL: {current}")
        return

    print(f"[cf-url-watcher] URL cambiata: {last} → {current}")

    # Estrai solo l'hostname (senza schema) per il sed — l'URL fetchato è
    # già "https://...trycloudflare.com" ma il vecchio valore salvato potrebbe
    # essere nello stesso formato: normalizza entrambi.
    def _hostname(url: str) -> str:
        return url.replace("https://", "").replace("http://", "").rstrip("/")

    old_host, new_host = _hostname(last), _hostname(current)
    authelia_ok, authelia_detail = update_authelia_domain(old_host, new_host)
    print(f"[cf-url-watcher] Authelia: {'OK' if authelia_ok else 'FALLITO'} — {authelia_detail}")

    bot = TelegramBot()
    if not bot.is_configured():
        print("[cf-url-watcher] Telegram non configurato — salto notifica.")
        return

    if authelia_ok:
        authelia_line = f"✅ Authelia aggiornato e riavviato automaticamente — Shifter e le altre app restano accessibili."
    else:
        authelia_line = (
            f"⚠️ <b>Aggiornamento automatico di Authelia FALLITO</b>: {authelia_detail}\n"
            f"Serve intervento manuale su {AUTHELIA_CONFIG} (CT202) prima che Shifter/Lifelog tornino accessibili."
        )

    msg = (
        "🌐 <b>Cloudflare Quick Tunnel — Nuova URL</b>\n\n"
        f"<b>Nuova:</b> <code>{current}</code>\n"
        f"<b>Precedente:</b> <code>{last}</code>\n\n"
        f"{authelia_line}"
    )
    ok = bot.send_message(msg)
    if ok:
        print("[cf-url-watcher] Notifica Telegram inviata.")
    else:
        print("[cf-url-watcher] Invio Telegram fallito.", file=sys.stderr)


if __name__ == "__main__":
    main()
