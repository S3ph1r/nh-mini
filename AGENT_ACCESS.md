# AGENT_ACCESS.md

Documentazione per operazioni autonome dell'agent NH_mini dopo installazione.

---

## 1. ACCESSO A PROXMOX (senza password)

**Metodo**: Chiave SSH dedicata  
**Percorso**: `~/.ssh/id_ed25519` (generata durante bootstrap)  
**Comando**: `ssh -i ~/.ssh/id_ed25519 root@{proxmox_host} "comandi"`  
**Nota**: Nessuna interazione utente richiesta, chiave pre-autorizzata

Esempi:
```bash
# Lista container
ssh -i ~/.ssh/id_ed25519 root@10.0.0.2 "pct list"

# Info container specifico
ssh -i ~/.ssh/id_ed25519 root@10.0.0.2 "pct config 100"
```

---

## 2. ACCESSO AD ALTRI LXC (creati da NH)

**Metodo**: `pct exec` via Proxmox  
**Percorso**: Attraverso SSH al Proxmox host (vedi punto 1)  
**Comando**: `ssh -i ~/.ssh/id_ed25519 root@{proxmox_host} "pct exec {vmid} -- comandi"`  
**Vantaggio**: Nessuna password necessaria, accesso root diretto da Proxmox

Esempi:
```bash
# Shell nel container 100
ssh -i ~/.ssh/id_ed25519 root@10.0.0.2 "pct exec 100 -- /bin/bash"

# Esegui comando specifico
ssh -i ~/.ssh/id_ed25519 root@10.0.0.2 "pct exec 101 -- apt-get update"
```

---

## 3. LETTURA SECRETS (quando servono)

**Metodo**: SOPS decrypt  
**Comando**: `sops -d secrets/{file}.enc.yaml`  
**Prompt**: "Master password NH:" (1 volta per sessione)  
**Cache**: 15 minuti di validità  
**Percorso chiave**: `~/.nh/age/age.key`

Esempi:
```bash
# Decrypt token GitHub
sops -d secrets/github_token.enc.yaml

# Decrypt API key esterna
sops -d secrets/api_keys.enc.yaml
```

**Note**:
- Master password richiesta solo la prima volta ogni 15 minuti
- I secrets in chiaro NON vengono mai salvati su disco
- Usa variabili d'ambiente temporanee per i valori decifrati

---

## 4. SCRITTURA SECRETS

**Metodo**: SOPS encrypt con chiave pubblica  
**Comando**: `echo "data" | sops -e > secrets/{file}.enc.yaml`  
**Vantaggio**: NON richiede password (usa chiave pubblica Age)  
**Automatico**: Processo completamente automatizzabile

Esempi:
```bash
# Crea nuovo secret
echo "ghp_xxxxxxxxxxxx" | sops -e > secrets/github_token.enc.yaml

# Aggiorna secret esistente
echo "new_api_key_123" | sops -e > secrets/new_service.enc.yaml
```

---

## 5. DISCOVERY INFRASTRUTTURA

**Metodo**: Script Python discovery  
**Comando**: `python3 core/discovery.py`  
**Accesso**: Via SSH al Proxmox host (vedi punto 1)  
**Output**: `state/inventory.json`  
**Frequenza**: Ogni 15 minuti automatico o on-demand

Esempi:
```bash
# Discovery manuale
python3 core/discovery.py

# Discovery con output verbose
python3 core/discovery.py --verbose
```

**Output discovery**:
```json
{
  "containers": {
    "100": {
      "hostname": "ct100-reverse-proxy",
      "ip": "10.0.0.100",
      "status": "running",
      "purpose": "reverse-proxy"
    }
  }
}
```

---

## CONVENZIONI E BEST PRACTICES

### Pattern hostname container
- Formato: `ct{vmid}-{purpose}`
- Esempio: `ct100-reverse-proxy`, `ct101-monitoring`

### Gestione secrets
- Mai salvare in chiaro nel repository
- Usare sempre estensione `.enc.yaml` per files cifrati
- Documentare sempre il contenuto in `secrets/README.md`

### Accesso automatico
- Tutti i comandi possono essere eseguiti senza interazione umana
- Le credenziali SSH sono pre-configurate
- La master password può essere fornita via variabile d'ambiente se necessario

### Sicurezza
- Le chiavi SSH private non vengono mai esposte
- I secrets vengono decifrati solo in memoria
- Ogni accesso SSH usa chiave dedicata senza passphrase

---

## VARIABILI D'AMBIENTE UTILI

```bash
# Override host Proxmox
export NH_PROXMOX_HOST="10.0.0.2"

# Override utente SSH
export NH_PROXMOX_SSH_USER="root"

# Chiave pubblica Age (per encrypt)
export NH_AGE_PUBKEY="age1xxxxxxxxxx"

# Master password (per decrypt automatico)
export NH_MASTER_PASSWORD="your_password_here"
```

---

*Questo documento viene aggiornato automaticamente quando cambiano le configurazioni di accesso.*