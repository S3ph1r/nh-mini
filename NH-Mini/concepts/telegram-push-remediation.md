# Telegram Push & Approval-Based Remediation

## Panoramica
Il sistema di monitoraggio di NH-Mini non si limita a rilevare i guasti, ma interagisce con l'amministratore (Roberto) via Telegram per risolvere i problemi in modo sicuro e controllato.

## Architettura
Il sistema si basa su tre componenti:
1. **Heartbeat Daemon (`core/heartbeat.py`)**: Rileva il guasto, preleva i log via SSH e invia l'alert a Telegram.
2. **Telegram Bot Module (`core/telegram_bot.py`)**: Gestisce le API di Telegram e l'invio di messaggi con tastiere interattive.
3. **Polling Daemon (`nh-telegram.service`)**: Ascolta i click dell'utente sui bottoni Telegram e attiva i comandi di riparazione.

## Il Protocollo di Approvazione
Per evitare "improvvisazioni" o azioni distruttive da parte dell'AI, NH-Mini segue una politica di **Zero-Action-Without-Approval**:
- L'alert arriva su Telegram con un riepilogo del log.
- Sotto il messaggio compaiono due bottoni: `[🛠️ Riavvia]` e `[👁️ Ignora]`.
- Se l'utente preme `🛠️ Riavvia`, il sistema esegue il comando di *remediation* pre-configurato nel `service_catalog.py`.

## Sicurezza e Credenziali
- Il bot Telegram è dedicato (`@Nh_mini_bot`).
- Le credenziali (Token e ChatID) sono cifrate in **SOPS+Age** sotto il namespace `telegram.nh_mini_bot`.
- L'accesso ai container remoti per i restart avviene tramite **SSH keys senza password** (configurate tra CT190 e i target).

## Manutenzione
Per controllare lo stato dei servizi in background:
```bash
systemctl status nh-telegram.service  # Il demone che "ascolta" i bottoni
systemctl status nh-mini-api.service  # Il servizio della dashboard NH-Mini
```

## Troubleshooting
Se i bottoni su Telegram non rispondono, verificare che il servizio `nh-telegram.service` sia attivo e che i log in `/var/log/syslog` (con prefisso `nh-telegram`) non indichino errori di rete o di token.
