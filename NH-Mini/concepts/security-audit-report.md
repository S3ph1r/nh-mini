---
title: "Security Audit Report 2026-05-09"
type: concept
tags: [security, audit, sops, credentials]
updated: 2026-05-09
---

# NH-Mini Security Audit & Credential Centralization Report

**Data**: 2026-05-09
**Status**: 🟢 BONIFICATO

## Executive Summary
Eseguito audit completo su tutti i progetti in `sviluppi/` per identificare leak di credenziali e centralizzare la gestione dei segreti nel vault **SOPS**.

## Findings (Pre-Audit)

### 🔴 Criticità Elevate (Hardcoded Secrets)
| Progetto | File | Segreto Identificato |
| :--- | :--- | :--- |
| **Stratex** | `backend/stratex/scripts/*.py` | DB Password (`stratex_pass_2026`) |
| **DIAS** | `temp/*.py` | Google Gemini API Key (`AIzaSy...`) |
| **Lifelog2** | `scripts/v1_import.py` | MinIO Keys, DB Password, PC139 Pass |

### 🟡 Dispersione Configurazione
- Presenza di file `.env` locali sparsi in tutti i progetti.
- Mancanza di una fonte di verità centralizzata per le credenziali applicative.

---

## Azioni Intraprese

### 1. Bonifica Codebase
- Tutti i segreti hardcoded sopra elencati sono stati **rimossi** e sostituiti con `os.getenv()`.
- Gli script ora caricano la configurazione in modo sicuro dall'ambiente locale.

### 2. Centralizzazione nel Vault SOPS
I seguenti segreti sono stati migrati e criptati in `secrets/`:
- `secrets/stratex.main.enc.yaml`: Credenziali DB, Redis URL.
- `secrets/dias.main.enc.yaml`: Gemini API Key, Project ID.
- `secrets/ct105.postgres.enc.yaml`: Credenziali Postgres (riutilizzate per Stratex).
- `secrets/github.main.enc.yaml`: Token GitHub per deploy.

### 3. Protezione Git
- Verificato che tutti i repository (`root`, `stratex`, `dias`, `Lifelog2`) ignorino correttamente i file `.env`.
- La history di Git di **Lifelog2** è stata resettata e ripulita (Force Push) per eliminare tracce del primo commit non sicuro.

---

## Protocollo Operativo "Zero Leak"

1. **Mai** scrivere password o token nel codice sorgente o nei commenti del Wiki.
2. **Utilizzare** sempre `os.getenv()` con un fallback sicuro o un errore esplicito.
3. **Mantenere** le credenziali reali nel file `.env` locale (ignorato da Git).
4. **Backup** dei segreti: Se aggiungi una nuova chiave, salvala subito nel vault SOPS.

---
**Nota per Aria (PC 139)**: I servizi di runtime su PC 139 mantengono i loro token locali e continueranno a funzionare. La bonifica ha riguardato solo lo strato di sviluppo e il versionamento del codice.
