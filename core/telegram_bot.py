#!/usr/bin/env python3
"""
telegram_bot.py — Modulo per invio notifiche push e polling interattivo.

Gestisce:
1. Invio messaggi (usato da heartbeat.py per inviare gli alert).
2. Invio messaggi con Inline Buttons (per chiedere approvazione).
3. Long-polling daemon (eseguibile stand-alone) per ascoltare i callback
   dei bottoni e triggerare i comandi di remediation.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import logging
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Aggiungi il root al sys.path per permettere import relativi
sys.path.insert(0, str(ROOT))

from scripts.credential_manager import UnifiedCredentialManager

log = logging.getLogger("telegram_bot")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [telegram] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

class TelegramBot:
    def __init__(self):
        self.token = None
        self.chat_id = None
        self._load_credentials()
        self.api_url = f"https://api.telegram.org/bot{self.token}/" if self.token else None
        
        # Carica il catalogo per i comandi di remediation
        try:
            from core.service_catalog import STATIC_CATALOG
            self.catalog = STATIC_CATALOG
        except ImportError:
            self.catalog = {}

    def _load_credentials(self):
        mgr = UnifiedCredentialManager()
        creds = mgr.get_credential("telegram", "nh_mini_bot", interactive=False)
        if creds:
            self.token = creds.get("token")
            self.chat_id = creds.get("chat_id")
        else:
            log.warning("Credenziali Telegram non trovate in SOPS. Il bot è disabilitato.")

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def _api_request(self, method: str, data: dict = None) -> dict:
        if not self.is_configured():
            return {"ok": False, "description": "Bot non configurato"}
            
        url = self.api_url + method
        
        if data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)
            
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                res_body = response.read()
                return json.loads(res_body)
        except urllib.error.URLError as e:
            err_msg = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            log.error(f"Telegram API Error ({method}): {err_msg}")
            return {"ok": False, "description": err_msg}

    def send_message(self, text: str, reply_markup: dict = None) -> bool:
        if not self.is_configured():
            return False
            
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        res = self._api_request("sendMessage", payload)
        return res.get("ok", False)

    def edit_message(self, message_id: int, text: str, reply_markup: dict = None) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
            
        res = self._api_request("editMessageText", payload)
        return res.get("ok", False)

    def answer_callback(self, callback_query_id: str, text: str = None):
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        self._api_request("answerCallbackQuery", payload)

    def _execute_command(self, cmd: str) -> tuple[bool, str]:
        """Esegue un comando shell e ritorna (success, output)."""
        log.info(f"Executing remediation command: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return True, result.stdout.strip() or "Comando eseguito con successo."
            else:
                return False, result.stderr.strip() or "Il comando ha fallito silenziosamente."
        except Exception as e:
            return False, str(e)

    def get_diagnostic_log(self, service_key: str) -> str:
        """Esegue il comando di diagnostica se configurato, altrimenti ritorna stringa vuota."""
        service = self.catalog.get(service_key, {})
        diag_cmd = service.get("diagnostic")
        if not diag_cmd:
            return ""
            
        success, output = self._execute_command(diag_cmd)
        if output:
            # Tronca il log a 1000 caratteri per evitare messaggi enormi
            if len(output) > 1000:
                output = "..." + output[-997:]
            return f"\n\n<b>Log (ultime righe):</b>\n<pre>{output}</pre>"
        return ""

    def send_alert(self, alert: dict):
        """Metodo Helper chiamato da heartbeat.py per inviare un nuovo alert."""
        severity = alert.get("severity", "MEDIUM")
        icon = "🚨" if severity == "HIGH" else "⚠️"
        service_key = alert.get("service_key", "")
        
        text = f"{icon} <b>NH-Mini ALERT ({severity})</b>\n\n"
        text += f"<b>Servizio:</b> {alert.get('service_name', service_key)}\n"
        text += f"<b>Errore:</b> {alert.get('message', 'Sconosciuto')}"
        
        text += self.get_diagnostic_log(service_key)
        
        service = self.catalog.get(service_key, {})
        remediation_cmd = service.get("remediation")
        
        reply_markup = None
        if remediation_cmd:
            text += "\n\n<i>Cosa vuoi fare?</i>"
            # Crea Inline Keyboard
            reply_markup = {
                "inline_keyboard": [
                    [
                        {"text": "🛠️ Riavvia", "callback_data": f"rem_yes:{service_key}"},
                        {"text": "👁️ Ignora", "callback_data": f"rem_no:{service_key}"}
                    ]
                ]
            }
            
        self.send_message(text, reply_markup=reply_markup)

    def poll_updates(self):
        """Ciclo di polling infinito per ascoltare i callback dei bottoni."""
        if not self.is_configured():
            log.error("Impossibile avviare il polling: bot non configurato.")
            return

        log.info("Avvio Telegram Polling Daemon...")
        offset = 0
        
        while True:
            try:
                res = self._api_request("getUpdates", {"offset": offset, "timeout": 30})
                if not res.get("ok"):
                    time.sleep(5)
                    continue
                    
                updates = res.get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    if "callback_query" in update:
                        self.handle_callback(update["callback_query"])
                        
            except KeyboardInterrupt:
                log.info("Polling interrotto dall'utente.")
                break
            except Exception as e:
                log.error(f"Errore durante il polling: {e}")
                time.sleep(5)

    def handle_callback(self, query: dict):
        """Gestisce il click dell'utente su un bottone interattivo."""
        query_id = query["id"]
        data = query.get("data", "")
        message = query.get("message", {})
        message_id = message.get("message_id")
        text = message.get("text", "") # Testo originale
        
        # Re-format per mantenere HTML originale se possibile
        original_html = text.replace("<", "&lt;").replace(">", "&gt;") 
        
        if data.startswith("rem_no:"):
            self.answer_callback(query_id, "Hai ignorato l'allarme.")
            self.edit_message(message_id, f"<s>{original_html}</s>\n\n👁️ <i>Ignorato manualmente.</i>")
            
        elif data.startswith("rem_yes:"):
            service_key = data.split(":", 1)[1]
            service = self.catalog.get(service_key, {})
            cmd = service.get("remediation")
            
            if not cmd:
                self.answer_callback(query_id, "Comando non trovato.")
                return
                
            self.answer_callback(query_id, "Avvio riparazione...")
            self.edit_message(message_id, f"{original_html}\n\n⏳ <i>Esecuzione riavvio in corso...</i>")
            
            success, output = self._execute_command(cmd)
            
            if success:
                self.edit_message(message_id, f"{original_html}\n\n✅ <b>Risolto:</b> Comando eseguito con successo.\n<pre>{output}</pre>")
            else:
                self.edit_message(message_id, f"{original_html}\n\n❌ <b>Fallito:</b> Il riavvio ha restituito un errore.\n<pre>{output}</pre>")

if __name__ == "__main__":
    bot = TelegramBot()
    if "--test" in sys.argv:
        print("Inviando messaggio di test...")
        bot.send_message("✅ <b>Test</b>\nIl modulo Telegram di NH-Mini è online e configurato.")
    elif "--poll" in sys.argv:
        bot.poll_updates()
    else:
        print("Uso:")
        print("  python3 core/telegram_bot.py --test  (invia messaggio test)")
        print("  python3 core/telegram_bot.py --poll  (avvia daemon in background)")
