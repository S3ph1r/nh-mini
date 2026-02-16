# Security Policy - NH Framework

type: security_policy
status: mandatory
date: 2026-02-16
enforcement: strict

## 🚨 REGOLE ASSOLUTE PER CREDENZIALI

### 1. **MAI HARDCODARE CREDENZIALI**
- ❌ `token = "ghp_123456789"`
- ❌ `password = "mypassword123"`
- ❌ `api_key = "sk-abcdef"`
- ✅ Usa sempre `core/credential_cache.py`
- ✅ Richiedi input utente o usa SOPS+Age

### 2. **CACHE IN-MEMORY OBBLIGATORIA**
```python
from core.credential_cache import get_credential

# ✅ CORRETTO
token = get_credential("github_token", "GitHub Token: ")
if not token:
    print("❌ Token richiesto per continuare")
    sys.exit(1)

# ❌ SBAGLIATO - MAI COSÌ
token = "ghp_123456789"  # MAI HARDCODARE!
```

### 3. **SEMPRE CHIEDI ALL'UTENTE**
- Se la credenziale non è in cache → **CHIEDI SEMPRE**
- Se l'utente non fornisce → **FERMATI E SEGNALA**
- **NON PROSEGUIRE** con valori di default

### 4. **NESSUNA SCRITTURA SU DISCO**
- Credenziali solo in **memoria temporanea**
- Cache auto-expire dopo 15 minuti
- **MAI** salvare su file `.txt`, `.env`, `.json`
- Solo SOPS+Age per secrets persistenti

### 5. **REPOSITORY VISIBILITY**
- **Fase sviluppo**: SEMPRE PRIVATO
- **Produzione**: Valutare caso per caso
- **Default**: Privato fino a decisione esplicita

## 🛡️ IMPLEMENTAZIONE SICURA

### Pattern Corretto per GitHub Operations
```python
def github_operation():
    # 1. Richiedi token
    token = get_credential("github_token", "GitHub Token: ")
    if not token:
        return False
    
    # 2. Usa token sicuro
    headers = {"Authorization": f"token {token}"}
    
    # 3. Pulisci dopo uso (opzionale)
    # clear_credential("github_token")
    
    return True
```

### Pattern Corretto per Proxmox Access
```python
def proxmox_command():
    # 1. Richiedi password (temporanea)
    password = get_credential("proxmox_password", "Password Proxmox (temp): ", secret=True)
    if not password:
        return False
    
    # 2. Usa password
    # ... esegui comando ...
    
    # 3. Dimentica password (obbligatorio per temp)
    clear_credential("proxmox_password")
    
    return True
```

## 🔍 CONTROLLI DI SICUREZZA

### Pre-Push Checklist
```bash
# Cerca token hardcodati
grep -r "ghp_\|github_pat_\|sk-" . --exclude-dir=.git

# Cerca password
grep -r "password.*=.*\"" . --exclude-dir=.git

# Cerca API keys
grep -r "api_key.*=.*\"" . --exclude-dir=.git
```

### Git Hook Consigliato
Crea `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Block commit if credentials found
if grep -r "ghp_\|github_pat_\|sk-" . --exclude-dir=.git --exclude="*.md"; then
    echo "❌ CREDENZIALI TROVATE NEL CODICE!"
    echo "Rimuovi prima di commitare."
    exit 1
fi
```

## 🚨 VIOLAZIONI POLICY

### Azioni Immediate
1. **Ferma tutte le operazioni**
2. **Rimuovi credenziali esposte**
3. **Cambia credenziali compromesse**
4. **Documenta incidente**
5. **Rivedi processo**

### Conseguenze
- Repository compromesso → **PRIVATO immediato**
- Token esposto → **Revoca e rigenera**
- Script compromesso → **Rewrite con pattern sicuro**

## 📋 ESEMPI DI ERRORE (DA EVITARE)

```python
# ❌ MALISSIMO - Mai fare così
github_token = "ghp_1234567890abcdef"
curl_cmd = f"curl -H 'Authorization: token {github_token}' https://api.github.com"

# ❌ SBAGLIATO - Anche peggio
with open("token.txt", "w") as f:
    f.write("ghp_1234567890abcdef")

# ❌ ERRATO - Environment non è sicuro se scritto
os.environ["GITHUB_TOKEN"] = "ghp_1234567890abcdef"
```

## ✅ ESEMPI CORRETTI

```python
# ✅ BENE - Cache sicura
token = get_credential("github_token", "GitHub Token: ")
if token:
    # usa token sicuro
    pass

# ✅ BENE - SOPS+Age per persistenti
# secrets/github_token.enc.yaml (cifrato)
token = decrypt_secret("github_token.enc.yaml")
```

## 🎯 POLICY AGENT

### Per Agent Futuri
1. **LEGGI QUESTO DOCUMENTO PRIMO**
2. **Usa sempre `core/credential_cache.py`**
3. **Se manca credenziale → CHIEDI UTENTE**
4. **Se utente non risponde → FERMATI**
5. **Mai proseguire con valori fake/default**

### Review Process
- **Ogni PR**: Verifica assenza credenziali hardcodate
- **Ogni script**: Deve usare credential cache
- **Ogni documento**: Deve linkare questa policy

---

**⚠️ VIOLARE QUESTA POLICY = SECURITY INCIDENT**
**🔒 SICUREZZA > COMODITÀ SEMPRE**