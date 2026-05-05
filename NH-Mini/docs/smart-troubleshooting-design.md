# Design: Autonomous Smart Troubleshooting (Fase 4+)

## Visione
Evolvere il sistema di alert "stupido" (solo rilevazione) in un sistema "intelligente" capace di analizzare i log, diagnosticare la causa radice e proporre soluzioni motivate all'utente via Telegram.

---

## 1. Analisi Comparativa Modelli (Stato dell'Arte Maggio 2026)

L'architettura si basa sull'hardware attuale: **NVIDIA RTX 5060 Ti (16GB VRAM)**.

| Modello | Quantizzazione | VRAM Reale | Capacità di Analisi | Ruolo Proposto |
| :--- | :--- | :--- | :--- | :--- |
| **Qwen 3.6-27B** | 4-bit (IQ4_XS) | ~14GB | **Alta (Logic/Code)**. Ottimo su Python e Linux. | **Local Brain (Triage)** |
| **DeepSeek-V4-Flash** | 2-bit | ~70GB+ | **Media (Degradata)**. Troppo pesante per 16GB. | **Sconsigliato (Local)** |
| **Gemini 3.1 / Sonnet 4.6** | Cloud (API) | N/A | **Massima (Visione d'insieme)**. Context window 1M+. | **Strategic Brain (Escalation)** |

### Vincoli Locali (16GB)
- **Context Limit**: Con 2GB di KV Cache residua, il modello locale può gestire circa **16k-32k token**.
- **Limiti di Indagine**: Non può analizzare script massivi (>2000 righe) in un colpo solo. Deve lavorare per "chunk" o estratti.

---

## 2. Protocollo di Interazione NH-Mini ↔ LLM

Il flusso di troubleshooting segue un modello a "richiesta di dati incrementale":

1.  **Trigger**: `heartbeat.py` rileva un errore.
2.  **Richiesta Iniziale (Payload)**:
    - `service_key`: Nome del servizio.
    - `error_log`: Ultime 15 righe di log.
    - `context_map`: Estratto del `service_catalog.py` relativo al servizio.
3.  **Analisi Iterativa**:
    - L'LLM può rispondere con un comando: `{"action": "request_data", "command": "df -h"}`.
    - NH-Mini esegue il comando e rimanda l'output.
4.  **Proposta Finale (JSON)**:
    - `analysis`: Spiegazione umana dell'errore.
    - `confidence`: Livello di certezza (0-1).
    - `remediation`: Comando suggerito per risolvere.

---

## 3. Gestione Privacy e Riservatezza (Sanitizzazione)

Per l'uso del Cloud (Gemini), è obbligatorio un passaggio di pulizia dati eseguito dal **Local Brain**:

- **Input**: Log grezzi, file di configurazione.
- **Processo**: Sostituzione di Password, Token, IP pubblici e PII con segnaposti.
- **Output**: Payload sanificato pronto per l'invio via API.

---

## 4. Disponibilità e Fallback (Resilienza 503)

NH-Mini deve rimanere funzionale anche se il Cloud è offline:

- **Primary**: Local Brain (Qwen 3.6). Se l'analisi è ad alta confidenza, invia l'alert con proposta.
- **Secondary (Cloud Upgrade)**: Se il problema è architettonico, scala al Cloud.
- **Fallback (Offline)**: Se il Cloud dà 503, NH-Mini degrada a "Modalità Manuale": invia l'alert grezzo a Telegram e chiede l'intervento dell'utente tramite l'IDE Antigravity.

---

## 5. Tooling e Logs Suggeriti per l'Analisi

Per una diagnosi efficace, il payload dovrebbe includere output da:
- `journalctl -u [service] -n 30`
- `docker logs [container] --tail 30` (se applicabile)
- `top -b -n 1` (carico CPU/RAM)
- `netstat -tulpn` (verifica porte)
- `df -h` (stato dischi)

---

*Documento creato il 1 Maggio 2026 a seguito della sessione di brainstorming architetturale.*
