---
title: "NH-Mini — Filosofia e DNA Operativo"
type: concept
tags: [nh-mini, filosofia, framework, agent, principi]
sources: [nh-mini-readme.md]
updated: 2026-04-24
---

# NH-Mini — Filosofia e DNA Operativo

NH-Mini è un **framework autoconsapevole** per la gestione di ambienti homelab. Non è un semplice insieme di script: è un sistema con un'identità operativa definita, progettato per operare in autonomia tramite AI agent.

## Principi Fondamentali

### Minimalismo
- Niente prescrizioni architetturali — cresce con le tue esigenze
- Aggiungi solo ciò che serve, quando serve
- "Prefer minimal changes — non aggiungere complessità se non richiesta"

### Documentation First
- Documentazione prima del codice
- Se non è documentato, non esiste
- Ogni agente che legge i file di configurazione deve poter operare in autonomia

### Bootstrap Autonomo
- Installabile su LXC vuoto senza prerequisiti
- Un singolo script (`bootstrap.sh`) porta il sistema a zero

### Agent-Friendly
- Progettato per operazioni autonome via AI assistant
- Il sistema si descrive a se stesso tramite file strutturati
- L'agente dichiara il contesto operativo all'inizio di ogni sessione

### Open By Default
- Repository pubblico per filosofia: trasparenza, collaborazione, sicurezza tramite design
- Le configurazioni specifiche rimangono locali e private
- Sicurezza tramite design, non oscurità

## Autoconsapevolezza del Sistema

NH-Mini è autoconsapevole perché sa descrivere se stesso:

| File | Cosa descrive |
|------|---------------|
| `core/host-reality.mdc` | Realtà fisica del host Proxmox |
| `state/inventory.json` | Stato reale dei container (auto-aggiornato ogni 15min) |
| `config/nh_config.json` | Configurazione rete, host, default LXC |
| `workspace/active_config.json` | Progetto attivo nella sessione corrente |
| `core/incidents.mdc` | Registro errori di assunzione passati |
| `.cursorrules` | DNA operativo dell'agente (regole, limiti, workflow) |
| `CLAUDE.md` | Schema wiki LLM second brain |

## Regola della Physical Certainty

**Mai proporre un'operazione su un'entità senza aver eseguito un PROBE nella sessione corrente.**

Il GROUNDING RITUAL: ogni piano di implementazione deve iniziare con la parola `GROUNDED` seguita dall'evidenza fisica (log di probe). Se manca il grounding, il piano è INVALIDO.

Questo principio nasce dagli errori passati documentati in `core/incidents.mdc`.

## Separazione Operativa

Quando un progetto è attivo (es. DIAS, ARIA):

- **Leggi dal framework**: regole operative, contracts, security policy, infrastruttura
- **Opera nel progetto**: `sviluppi/{progetto}/src/`, `sviluppi/{progetto}/knowledge/`
- **Scrivi su NH-Mini solo se**: modifichi infrastruttura condivisa, aggiungi credenziali, scopri pattern riutilizzabili

## 4 Tipi di Contract

Ogni entità del sistema è descritta da un contract tipizzato (`core/description-contracts.mdc`):

1. **resource_declaration** — risorse infrastrutturali (container, storage)
2. **secrets_management** — gestione secrets (SOPS+Age)
3. **deployment_workflow** — processi di deployment (scripts, automazioni)
4. **network_exposure** — esposizione servizi (porte, routing)

## Confini Autonomia Agent

```
✅ CAN (autonomamente):
   - Leggere file, cercare nella knowledge base
   - Usare credential_manager
   - Deploy/undeploy LXC
   - Eseguire discovery, aggiornare deployments.log
   - Scrivere/aggiornare wiki (CLAUDE.md)

❌ MUST ASK (conferma utente):
   - Creare/distruggere container
   - Modificare .cursorrules
   - Creare nuovi knowledge entry
   - Cambiare progetto attivo
```

## Evoluzione

NH-Mini cresce organicamente. I pattern scoperti durante lo sviluppo dei progetti (ARIA, DIAS) vengono promossi a pattern del framework quando sono riutilizzabili.

Il wiki LLM (questo vault) è parte di questa filosofia: è il meccanismo con cui la conoscenza si accumula invece di essere ridericavata da zero ogni sessione.

## Vedi anche

- [[overview]] — stato corrente del homelab
- [[ct190-nh-mini]] — il container da cui opera l'agente
- [[concepts/dependency-map]] — mappa infrastruttura
