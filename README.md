# NH_mini - Minimal Homelab Framework

⚠️ **SECURITY NOTICE**: Questo repository è in fase di sviluppo attivo. Leggi `SECURITY_POLICY.md` prima di contribuire.

Framework minimalista per gestire infrastrutture homelab su Proxmox/LXC con approccio "bootstrap first".

## Filosofia

NH_mini segue principi di minimalismo e organic growth:
- **Niente prescrizioni architetturali** - Cresce con le tue esigenze
- **Documentazione prima del codice** - I contracts definiscono il "cosa" prima del "come"
- **Bootstrap autonomo** - Installabile su LXC vuoto senza prerequisiti
- **Agent-friendly** - Progettato per operazioni autonome via AI assistant
- **Open by default** - Repository pubblico, sicurezza tramite design (non oscurità)

## Installazione Rapida

```bash
# Su LXC Proxmox vuoto (ct190 consigliato)
apt update && apt install -y curl git python3
wget https://raw.githubusercontent.com/yourusername/nh-mini/main/bootstrap.sh
chmod +x bootstrap.sh
./bootstrap.sh
```

Lo script chiederà:
- IP/hostname del tuo host Proxmox
- Password root (temporanea, solo per setup SSH)
- Master password per cifrare secrets (min 12 caratteri)

## Struttura

```
nh-mini/
├── core/                    # Componenti core
│   ├── host-reality.mdc     # Realtà fisica del host
│   ├── description-contracts.mdc  # 4 tipi di contracts
│   ├── discovery.py         # Scanner Proxmox
│   └── loader.py           # Caricamento contesto
├── state/                   # Stato dinamico
│   └── inventory.json      # Container rilevati
├── knowledge/              # Knowledge base organica
│   ├── README.md           # Guida knowledge
│   └── development/        # Documentazione sviluppo
├── secrets/                # Secrets cifrati (SOPS+Age)
└── bootstrap.sh            # Installer principale
```

## Contracts (4 Tipi)

1. **resource_declaration** - Risorse infrastrutturali
2. **secrets_management** - Gestione secrets
3. **deployment_workflow** - Processi di deployment
4. **network_exposure** - Esposizione servizi

Vedi `core/description-contracts.mdc` per dettagli.

## Uso Base

### Discovery infrastruttura
```bash
python3 core/discovery.py    # Aggiorna state/inventory.json
```

### Caricamento contesto per agent
```bash
python3 core/loader.py      # Output contesto completo
```

### Accesso container via agent
```bash
# Da AGENT_ACCESS.md - accesso autonomo
ssh -i ~/.ssh/id_ed25519 root@proxmox "pct exec 100 -- comando"
```

## Sicurezza

- **SSH key-based** - Nessuna password in chiaro
- **SOPS+Age** - Tutti i secrets cifrati
- **Principio minimo** - Solo accessi necessari
- **Backup obbligatorio** - Chiavi critiche salvate off-host

## Per Agent Futuri

### Workflow GitHub Push
Vedi `knowledge/development/github-push-workflow.mdc` per il processo completo di push su GitHub.

### Repository Visibilità
NH-mini è pubblico per filosofia: trasparenza, collaborazione, sicurezza tramite design.
Le tue configurazioni specifiche rimangono locali e private. Vedi `knowledge/architecture/repository-visibility-decision.mdc`

## Sviluppo

Il framework è auto-documentante. Per contribuire:

1. Leggi `knowledge/development/nh-self-bootstrap.mdc`
2. Segui i contracts in `core/description-contracts.mdc`
3. Documenta mentre sviluppi (non dopo)

## Troubleshooting

### Discovery fallisce
- Verifica SSH verso Proxmox: `ssh root@proxmox "pct list"`
- Controlla `state/inventory.json` esista

### Secrets non decifrano
- Master password corretta? (12+ caratteri)
- Chiave Age presente in `~/.nh/age/age.key`?

### Bootstrap blocca
- Tutti i pacchetti installati? (sops, age, git, ssh)
- Proxmox host raggiungibile?

## Roadmap

- [ ] Dashboard web minimale
- [ ] Templates container predefiniti
- [ ] Integrazione monitoring
- [ ] Backup automatizzati

## Licenza

MIT - Fai ciò che vuoi, documenta come usi NH.