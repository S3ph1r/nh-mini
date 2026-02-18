Ecco il nucleo minimale NH — \*\*solo ciò che serve al giorno 0\*\* per iniziare un'evoluzione coerente. Niente prescrizioni architetturali, niente standards predefiniti. Solo:

1\. \*\*Mappa del presente fisico\*\* (\`host-reality.mdc\`)  
2\. \*\*4 contratti atomici\*\* su \*come descrivere\* qualunque cosa si faccia (\`description-contracts.mdc\`)  
3\. \*\*Scanner minimale\*\* per mappare la realtà (\`discovery.py\`)  
4\. \*\*Indice dinamico\*\* che cresce con il knowledge accumulato (\`.cursorrules\`)

\---

\#\# 📁 Struttura Cartelle Minimale (Giorno 0\)

\`\`\`  
/opt/nh/  
├── core/  
│   ├── host-reality.mdc          \# Presente fisico (immutabile)  
│   ├── description-contracts.mdc \# 4 contratti atomici (immutabile)  
│   ├── discovery.py              \# Scanner Proxmox → state (30 righe)  
│   └── loader.py                 \# Carica contesto per agent (20 righe)  
├── state/  
│   └── inventory.json            \# Generato da discovery.py (vuoto all'inizio)  
├── knowledge/                    \# VUOTO all'inizio — cresce organicamente  
│   └── README.md                 \# "Questo è il tuo knowledge accumulato"  
├── .cursorrules                  \# Indice dinamico (cresce con te)  
└── bootstrap.sh                  \# Installazione one-shot (50 righe)  
\`\`\`

\---

\#\# 📄 File 1: \`core/host-reality.mdc\`

\`\`\`yaml  
\# host-reality.mdc — Il Presente Fisico (Immutabile)  
\# Descrive SOLO ciò che esiste ORA, non cosa sarà  
\# Questo file NON viene mai modificato — è la bussola fisica

host\_environment:  
  type: proxmox  
  container\_runtime: lxc  \# Non Docker, non VM  
  network:  
    bridge: vmbr0  
    subnet: 10.0.0.0/24  
    allocation: static  \# Non DHCP  
  storage:  
    root: /var/lib/vz  
    available\_gb: 950

constraints:  
  \- "Container hostname pattern: ct{vmid}-{purpose}"  
  \- "Mai esporre porte direttamente da app containers"  
  \- "Secrets mai in chiaro in git"  
\`\`\`

\---

\#\# 📄 File 2: \`core/description-contracts.mdc\`

\`\`\`yaml  
\# description-contracts.mdc — Regole su COME Descrivere (Immutabile)  
\# NON dice COSA fare. Dice COME descrivere qualunque cosa fai.  
\# Questo file NON viene mai modificato — è il contratto di coerenza

\# Contratto 1: Resource Declaration  
\# Come descrivere QUALSIASI risorsa (DB, cache, broker, ecc.)  
resource\_declaration:  
  purpose: "Descrivere una risorsa infrastrutturale"  
  required\_fields:  
    \- type          \# database | cache | message\_broker | storage  
    \- engine        \# postgresql-15 | redis-7 | ...  
    \- location      \# ct{vmid} | external | embedded  
    \- purpose       \# shared | project-specific | temporary  
    \- isolation\_model  \# schema\_per\_project | db\_namespace | instance  
  examples:  
    \- type: database, engine: postgresql-15, location: ct101, purpose: shared, isolation\_model: schema\_per\_project  
    \- type: cache, engine: redis-7, location: ct102, purpose: shared, isolation\_model: db\_namespace

\# Contratto 2: Secrets Handling  
\# Come descrivere QUALSIASI gestione secrets  
secrets\_handling:  
  purpose: "Descrivere gestione secrets per un progetto"  
  required\_fields:  
    \- encryption\_method  \# sops+age | vault | none (⚠️)  
    \- storage\_path       \# percorso relativo a /opt/nh/secrets/  
    \- access\_method      \# mounted\_file | env\_var | api\_call  
  examples:  
    \- encryption\_method: sops+age, storage\_path: secrets/{project}.enc.yaml, access\_method: mounted\_file

\# Contratto 3: Deployment Workflow  
\# Come descrivere QUALSIASI deploy su LXC  
deployment\_workflow:  
  purpose: "Descrivere deploy completo di un progetto"  
  required\_fields:  
    \- container\_allocation  \# ct{next} | existing:{vmid}  
    \- code\_source           \# git\_url | local\_path  
    \- service\_setup         \# systemd | pm2 | screen  
    \- health\_check          \# endpoint \+ expected\_status  
  examples:  
    \- container\_allocation: ct{next}, code\_source: git@github.com:user/project.git, service\_setup: systemd, health\_check: "/health → 200"

\# Contratto 4: Network Exposure  
\# Come descrivere QUALSIASI endpoint pubblico  
network\_exposure:  
  purpose: "Descrivere esposizione di un servizio alla rete"  
  required\_fields:  
    \- public\_endpoint   \# /api/project | project.home | ...  
    \- auth\_method       \# none | api\_key | jwt | basic\_auth  
    \- rate\_limiting     \# none | nginx\_lua | application  
  examples:  
    \- public\_endpoint: /api/{project}, auth\_method: api\_key, rate\_limiting: "100req/min via nginx"  
\`\`\`

\---

\#\# 📄 File 3: \`core/discovery.py\`

\`\`\`python  
\#\!/usr/bin/env python3  
"""  
discovery.py — Scanner minimale Proxmox → state/inventory.json  
Solo 30 righe. Output minimale ma sufficiente per contesto operativo.  
"""  
import subprocess, json, sys  
from pathlib import Path  
from datetime import datetime

def run(cmd):  
    return subprocess.run(cmd, shell=True, capture\_output=True, text=True).stdout.strip()

def discover():  
    containers \= \[\]  
    for line in run("pct list").split('\\n')\[1:\]:  
        if not line.strip(): continue  
        parts \= line.split()  
        vmid \= parts\[0\]  
        status \= parts\[1\]  
        name \= parts\[-1\] if len(parts) \> 2 else f"ct{vmid}"  
          
        \# Config base  
        config \= run(f"pct config {vmid}")  
        memory \= cores \= "unknown"  
        ip \= None  
        for cfg\_line in config.split('\\n'):  
            if cfg\_line.startswith('memory:'): memory \= cfg\_line.split(':')\[1\].strip()  
            elif cfg\_line.startswith('cores:'): cores \= cfg\_line.split(':')\[1\].strip()  
            elif 'ip=' in cfg\_line:   
                ip \= cfg\_line.split('ip=')\[1\].split('/')\[0\].strip()  
          
        containers.append({  
            "vmid": int(vmid),  
            "name": name,  
            "status": status,  
            "ip": ip,  
            "resources": {"memory\_mb": memory, "cores": cores},  
            "nh\_metadata": {  
                "managed": name \== "nh-core",  
                "project\_id": None,  
                "deployed\_standard": None  
            }  
        })  
      
    state \= {  
        "meta": {  
            "discovered\_at": datetime.now().isoformat(),  
            "discovery\_version": "1.0",  
            "nh\_version": "1.0"  
        },  
        "node": {  
            "hostname": run("hostname"),  
            "proxmox\_version": run("pveversion | awk '{print $2}'")  
        },  
        "containers": containers  
    }  
      
    Path("state").mkdir(exist\_ok=True)  
    Path("state/inventory.json").write\_text(json.dumps(state, indent=2))  
    return state

if \_\_name\_\_ \== "\_\_main\_\_":  
    state \= discover()  
    print(f"✅ Discovered {len(state\['containers'\])} containers")  
    print(f"📁 State saved to state/inventory.json")  
\`\`\`

\---

\#\# 📄 File 4: \`core/loader.py\`

\`\`\`python  
\#\!/usr/bin/env python3  
"""  
loader.py — Carica contesto per agent in \<2 secondi  
Output JSON leggibile da agent \+ umano  
"""  
import json, sys  
from pathlib import Path  
from datetime import datetime

def load\_context():  
    ctx \= {  
        "loaded\_at": datetime.now().isoformat(),  
        "host\_reality": {},  
        "contracts": {},  
        "state": {},  
        "knowledge\_index": \[\]  
    }  
      
    \# Host reality  
    hr \= Path("core/host-reality.mdc")  
    if hr.exists():  
        ctx\["host\_reality"\] \= {"file": str(hr), "summary": "Proxmox/LXC/vmbr0"}  
      
    \# Contracts  
    dc \= Path("core/description-contracts.mdc")  
    if dc.exists():  
        ctx\["contracts"\] \= {  
            "file": str(dc),  
            "contracts": \["resource\_declaration", "secrets\_handling", "deployment\_workflow", "network\_exposure"\]  
        }  
      
    \# State  
    inv \= Path("state/inventory.json")  
    if inv.exists():  
        state \= json.loads(inv.read\_text())  
        containers \= state.get("containers", \[\])  
        ctx\["state"\] \= {  
            "file": str(inv),  
            "containers\_count": len(containers),  
            "containers": \[f"{c\['vmid'\]}:{c\['name'\]}" for c in containers\[:5\]\],  \# Solo primi 5  
            "state\_age\_minutes": 0  \# Calcolato dal discovery  
        }  
      
    \# Knowledge index (da .cursorrules)  
    cr \= Path(".cursorrules")  
    if cr.exists():  
        lines \= cr.read\_text().split('\\n')  
        knowledge \= \[l.strip()\[2:\] for l in lines if l.strip().startswith('- "')\]  
        ctx\["knowledge\_index"\] \= knowledge\[:10\]  \# Solo primi 10 puntatori  
      
    return ctx

if \_\_name\_\_ \== "\_\_main\_\_":  
    ctx \= load\_context()  
    print(json.dumps(ctx, indent=2))  
\`\`\`

\---

\#\# 📄 File 5: \`.cursorrules\`

\`\`\`markdown  
\# NH Agent DNA — Giorno 0  
You operate NH Framework. NH provides MAP \+ DESCRIPTION RULES.  
You provide INTELLIGENCE.

\#\# Initialization (every session)  
1\. Load core/host-reality.mdc → know physical constraints (Proxmox/LXC/vmbr0)  
2\. Load core/description-contracts.mdc → know how to document anything  
3\. Load state/inventory.json → know current reality  
4\. Read this file → know where to find accumulated knowledge

\#\# Core Principle  
DO NOT INVENT NEW DESCRIPTION FORMATS.  
ALWAYS follow description-contracts.mdc.

\#\# Accumulated Knowledge (empty at start — grows over time)  
\# Quando crei qualcosa di nuovo che merita riuso:  
\# 1\. Documenta secondo description-contracts.mdc  
\# 2\. Salva in knowledge/{category}/{name}.mdc  
\# 3\. AGGIUNGI UNA RIGA QUI che punta al nuovo knowledge  
\#  
\# Esempio dopo aver creato primo LXC:  
\# \- "Per deploy LXC: vedi knowledge/deployment/lxc-proxmox.mdc"  
\#  
\# Questo file è il tuo indice. Cresce con te.

\#\# Autonomy Boundaries  
YOU CAN (no approval):  
\- Read files  
\- Run discovery (python3 core/discovery.py)  
\- Search knowledge/  
\- Append to state/deployments.log

YOU MUST ASK (approval required):  
\- Create/destroy containers  
\- Modify this file (.cursorrules)  
\- Create new knowledge/ entries (propose first)  
\`\`\`

\---

\#\# 📄 File 6: \`bootstrap.sh\`

\`\`\`bash  
\#\!/bin/bash  
\# bootstrap.sh — Installazione one-shot NH Framework  
set \-e

cat \<\< 'EOF'  
╔════════════════════════════════════════════════════════╗  
║  NH Framework — Nucleo Minimale per Homelab           ║  
║  Bootstrap v1.0 — Solo ciò che serve al giorno 0      ║  
╚════════════════════════════════════════════════════════╝  
EOF

echo ""  
echo "⚠️  Prerequisiti:"  
echo "   \- Esegui questo script SU Proxmox host O su LXC con accesso a pct"  
echo "   \- Utente: root"  
echo ""  
read \-p "Continuare? (y/n): " confirm  
\[\[ "$confirm" \!= "y" \]\] && exit 0

\# Verifica ambiente  
if \! command \-v pct &\> /dev/null; then  
    echo "❌ 'pct' command not found"  
    echo "   Esegui su Proxmox host o LXC con accesso API Proxmox"  
    exit 1  
fi

\# Crea struttura  
echo "📁 Creazione struttura /opt/nh..."  
install \-d /opt/nh/{core,state,knowledge}  
cd /opt/nh

\# Copia i file (qui simuliamo con cat \> file)  
cat \> core/host-reality.mdc \<\<'EOF'  
\# host-reality.mdc — Il Presente Fisico (Immutabile)  
host\_environment:  
  type: proxmox  
  container\_runtime: lxc  
  network:  
    bridge: vmbr0  
    subnet: 10.0.0.0/24  
    allocation: static  
  storage:  
    root: /var/lib/vz  
    available\_gb: 950  
constraints:  
  \- "Container hostname pattern: ct{vmid}-{purpose}"  
  \- "Mai esporre porte direttamente da app containers"  
  \- "Secrets mai in chiaro in git"  
EOF

cat \> core/description-contracts.mdc \<\<'EOF'  
\# description-contracts.mdc — Regole su COME Descrivere (Immutabile)  
resource\_declaration:  
  purpose: "Descrivere una risorsa infrastrutturale"  
  required\_fields:  
    \- type  
    \- engine  
    \- location  
    \- purpose  
    \- isolation\_model  
  examples:  
    \- type: database, engine: postgresql-15, location: ct101, purpose: shared, isolation\_model: schema\_per\_project

secrets\_handling:  
  purpose: "Descrivere gestione secrets per un progetto"  
  required\_fields:  
    \- encryption\_method  
    \- storage\_path  
    \- access\_method  
  examples:  
    \- encryption\_method: sops+age, storage\_path: secrets/{project}.enc.yaml, access\_method: mounted\_file

deployment\_workflow:  
  purpose: "Descrivere deploy completo di un progetto"  
  required\_fields:  
    \- container\_allocation  
    \- code\_source  
    \- service\_setup  
    \- health\_check  
  examples:  
    \- container\_allocation: ct{next}, code\_source: git@github.com:user/project.git, service\_setup: systemd, health\_check: "/health → 200"

network\_exposure:  
  purpose: "Descrivere esposizione di un servizio alla rete"  
  required\_fields:  
    \- public\_endpoint  
    \- auth\_method  
    \- rate\_limiting  
  examples:  
    \- public\_endpoint: /api/{project}, auth\_method: api\_key, rate\_limiting: "100req/min via nginx"  
EOF

\# discovery.py e loader.py (già definiti sopra — qui li copiamo)  
cat \> core/discovery.py \<\<'PYEOF'  
\#\!/usr/bin/env python3  
import subprocess, json, sys  
from pathlib import Path  
from datetime import datetime  
def run(cmd):  
    return subprocess.run(cmd, shell=True, capture\_output=True, text=True).stdout.strip()  
def discover():  
    containers \= \[\]  
    for line in run("pct list").split('\\n')\[1:\]:  
        if not line.strip(): continue  
        parts \= line.split()  
        vmid \= parts\[0\]  
        status \= parts\[1\]  
        name \= parts\[-1\] if len(parts) \> 2 else f"ct{vmid}"  
        config \= run(f"pct config {vmid}")  
        memory \= cores \= "unknown"  
        ip \= None  
        for cfg\_line in config.split('\\n'):  
            if cfg\_line.startswith('memory:'): memory \= cfg\_line.split(':')\[1\].strip()  
            elif cfg\_line.startswith('cores:'): cores \= cfg\_line.split(':')\[1\].strip()  
            elif 'ip=' in cfg\_line: ip \= cfg\_line.split('ip=')\[1\].split('/')\[0\].strip()  
        containers.append({  
            "vmid": int(vmid),  
            "name": name,  
            "status": status,  
            "ip": ip,  
            "resources": {"memory\_mb": memory, "cores": cores},  
            "nh\_metadata": {"managed": name \== "nh-core", "project\_id": None, "deployed\_standard": None}  
        })  
    state \= {  
        "meta": {"discovered\_at": datetime.now().isoformat(), "discovery\_version": "1.0", "nh\_version": "1.0"},  
        "node": {"hostname": run("hostname"), "proxmox\_version": run("pveversion | awk '{print $2}'")},  
        "containers": containers  
    }  
    Path("state").mkdir(exist\_ok=True)  
    Path("state/inventory.json").write\_text(json.dumps(state, indent=2))  
    return state  
if \_\_name\_\_ \== "\_\_main\_\_":  
    state \= discover()  
    print(f"✅ Discovered {len(state\['containers'\])} containers")  
    print(f"📁 State saved to state/inventory.json")  
PYEOF

chmod \+x core/discovery.py

cat \> core/loader.py \<\<'PYEOF'  
\#\!/usr/bin/env python3  
import json, sys  
from pathlib import Path  
from datetime import datetime  
def load\_context():  
    ctx \= {"loaded\_at": datetime.now().isoformat(), "host\_reality": {}, "contracts": {}, "state": {}, "knowledge\_index": \[\]}  
    hr \= Path("core/host-reality.mdc")  
    if hr.exists(): ctx\["host\_reality"\] \= {"file": str(hr), "summary": "Proxmox/LXC/vmbr0"}  
    dc \= Path("core/description-contracts.mdc")  
    if dc.exists(): ctx\["contracts"\] \= {"file": str(dc), "contracts": \["resource\_declaration", "secrets\_handling", "deployment\_workflow", "network\_exposure"\]}  
    inv \= Path("state/inventory.json")  
    if inv.exists():  
        state \= json.loads(inv.read\_text())  
        containers \= state.get("containers", \[\])  
        ctx\["state"\] \= {"file": str(inv), "containers\_count": len(containers), "containers": \[f"{c\['vmid'\]}:{c\['name'\]}" for c in containers\[:5\]\], "state\_age\_minutes": 0}  
    cr \= Path(".cursorrules")  
    if cr.exists():  
        lines \= cr.read\_text().split('\\n')  
        knowledge \= \[l.strip()\[2:\] for l in lines if l.strip().startswith('- "')\]  
        ctx\["knowledge\_index"\] \= knowledge\[:10\]  
    return ctx  
if \_\_name\_\_ \== "\_\_main\_\_":  
    ctx \= load\_context()  
    print(json.dumps(ctx, indent=2))  
PYEOF

chmod \+x core/loader.py

\# .cursorrules  
cat \> .cursorrules \<\<'EOF'  
\# NH Agent DNA — Giorno 0  
You operate NH Framework. NH provides MAP \+ DESCRIPTION RULES.  
You provide INTELLIGENCE.

\#\# Initialization (every session)  
1\. Load core/host-reality.mdc → know physical constraints (Proxmox/LXC/vmbr0)  
2\. Load core/description-contracts.mdc → know how to document anything  
3\. Load state/inventory.json → know current reality  
4\. Read this file → know where to find accumulated knowledge

\#\# Core Principle  
DO NOT INVENT NEW DESCRIPTION FORMATS.  
ALWAYS follow description-contracts.mdc.

\#\# Accumulated Knowledge (empty at start — grows over time)  
\# Quando crei qualcosa di nuovo che merita riuso:  
\# 1\. Documenta secondo description-contracts.mdc  
\# 2\. Salva in knowledge/{category}/{name}.mdc  
\# 3\. AGGIUNGI UNA RIGA QUI che punta al nuovo knowledge  
\#  
\# Esempio dopo aver creato primo LXC:  
\# \- "Per deploy LXC: vedi knowledge/deployment/lxc-proxmox.mdc"  
\#  
\# Questo file è il tuo indice. Cresce con te.

\#\# Autonomy Boundaries  
YOU CAN (no approval):  
\- Read files  
\- Run discovery (python3 core/discovery.py)  
\- Search knowledge/  
\- Append to state/deployments.log

YOU MUST ASK (approval required):  
\- Create/destroy containers  
\- Modify this file (.cursorrules)  
\- Create new knowledge/ entries (propose first)  
EOF

\# knowledge/README.md  
cat \> knowledge/README.md \<\<'EOF'  
\# NH Knowledge Accumulato

Questa directory contiene il \*\*knowledge organico\*\* accumulato dal tuo homelab.

\#\# Come cresce

1\. Fai qualcosa di nuovo (es. deploy LXC con Proxmox API)  
2\. Documenti secondo \`core/description-contracts.mdc\`  
3\. Salvi in \`knowledge/{category}/{name}.mdc\`  
4\. Aggiungi una riga in \`.cursorrules\` che punta al file

Esempio:  
\`\`\`  
knowledge/deployment/lxc-proxmox.mdc  
\`\`\`

Contenuto:  
\`\`\`yaml  
type: deployment\_workflow  
container\_allocation: ct{next}  
code\_source: git@github.com:...  
service\_setup: systemd  
health\_check: "/health → 200"  
notes: "Usa Proxmox API pct create, non template manuali"  
\`\`\`

Poi aggiungi in \`.cursorrules\`:  
\`\`\`  
\- "Per deploy LXC Proxmox: vedi knowledge/deployment/lxc-proxmox.mdc"  
\`\`\`

\#\# Struttura suggerita

knowledge/  
├── deployment/    \# Workflow deploy  
├── secrets/       \# Gestione secrets  
├── database/      \# Configurazioni DB  
├── network/       \# Routing, proxy, TLS  
└── patterns/      \# Pattern ricorrenti (es. fastapi-stack)

Non preoccuparti di creare la struttura ora. Cresce organicamente.  
EOF

\# Primo discovery  
echo ""  
echo "🔍 Esecuzione primo discovery..."  
python3 core/discovery.py

\# Summary  
echo ""  
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  
echo "✅ NH Framework Installato — Nucleo Minimale Pronto"  
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  
echo ""  
echo "📁 Percorso: /opt/nh"  
echo ""  
echo "📚 Contenuto:"  
echo "   core/host-reality.mdc          → Presente fisico (immutabile)"  
echo "   core/description-contracts.mdc → 4 contratti atomici (immutabile)"  
echo "   core/discovery.py              → Scanner Proxmox"  
echo "   core/loader.py                 → Carica contesto per agent"  
echo "   state/inventory.json           → Mappa infrastruttura (appena generata)"  
echo "   knowledge/                     → VUOTO — crescerà con te"  
echo "   .cursorrules                   → Indice dinamico (vuoto — crescerà)"  
echo ""  
echo "🚀 Prossimi passi:"  
echo "   1\. cd /opt/nh"  
echo "   2\. python3 core/loader.py      → Vedi contesto caricato"  
echo "   3\. Apri Trae/Antigravity su questa cartella"  
echo "   4\. Chiedi: 'Mostrami lo stato del sistema'"  
echo ""  
echo "💡 Ricorda: NH non prescrive architettura. Fornisce solo:"  
echo "   • Mappa del presente fisico"  
echo "   • Regole su COME descrivere ciò che fai"  
echo "   • Indice dinamico che cresce con il knowledge accumulato"  
echo ""  
echo "Il resto emerge organicamente dalla tua attività."  
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  
\`\`\`

\---

\#\# ✅ Cosa Devi Fare Ora (Passo-Passo)

\#\#\# Passo 1: Crea il Container NH Core  
Su Proxmox, crea un LXC Ubuntu 22.04/24.04:  
\- RAM: 512MB (basta)  
\- Storage: 4GB  
\- Network: bridge vmbr0, IP statico (es. \`10.0.0.100\`)  
\- \*\*Importante\*\*: Abilita nesting (\`nesting=1\`) per permettere a NH di gestire altri LXC

\#\#\# Passo 2: Esegui il Bootstrap  
Collegati in SSH al nuovo LXC come root:  
\`\`\`bash  
ssh root@10.0.0.100  
\`\`\`

Poi esegui:  
\`\`\`bash  
curl \-sL https://gist.githubusercontent.com/placeholder/nh-bootstrap/raw/bootstrap.sh | bash  
\`\`\`  
\*(Nota: per ora copia/incolla il contenuto di \`bootstrap.sh\` qui sopra in un file locale e eseguilo)\*

\#\#\# Passo 3: Verifica l'Installazione  
\`\`\`bash  
cd /opt/nh  
python3 core/loader.py  
\`\`\`  
Dovresti vedere:  
\`\`\`json  
{  
  "loaded\_at": "2026-02-13T10:30:00",  
  "host\_reality": { "summary": "Proxmox/LXC/vmbr0" },  
  "contracts": { "contracts": \["resource\_declaration", ...\] },  
  "state": { "containers\_count": 1, "containers": \["100:nh-core"\] },  
  "knowledge\_index": \[\]  
}  
\`\`\`

\#\#\# Passo 4: Connettiti con Trae  
1\. Apri Trae/Antigravity sul tuo PC  
2\. Connettiti in SSH al container NH (\`ssh root@10.0.0.100\`)  
3\. Apri la cartella \`/opt/nh\`  
4\. \*\*Prima cosa da dire a Trae\*\*:  
   \`\`\`  
   Carica il contesto NH e mostrami lo stato attuale del sistema  
   \`\`\`

\#\#\# Passo 5: Primo Progetto (Esempio)  
Chiedi a Trae:  
\`\`\`  
Voglio deployare un semplice servizio FastAPI che saluta l'utente.  
Non esistono ancora standard — documenta tutto secondo i contratti NH.  
Dopo il deploy, proponi se vale la pena creare un knowledge entry in knowledge/.  
\`\`\`

Trae:  
\- Leggerà \`host-reality.mdc\` → sa che è su Proxmox/LXC  
\- Leggerà \`description-contracts.mdc\` → sa come descrivere DB/secrets/deploy  
\- Farà discovery → vede solo CT100 (nh-core)  
\- Ti chiederà le decisioni architetturali (DB embedded/condiviso, ecc.)  
\- Eseguirà il deploy  
\- Documenterà in \`knowledge/deployment/fastapi-example.mdc\`  
\- Proporrà di aggiungere una riga in \`.cursorrules\`

\*\*Tu approvi la modifica a \`.cursorrules\`\*\* → l'indice cresce.

\---

\#\# 🧠 Perché Questo Funziona

| Problema | Soluzione NH |  
|----------|--------------|  
| Agent parte da zero ogni sessione | \`.cursorrules\` è indice dinamico → punta a knowledge accumulato |  
| Documentazione incoerente | \`description-contracts.mdc\` forza formato unico |  
| Pattern non rilevabili | Ogni operazione documentata → pattern emergono naturalmente |  
| Decisioni perse nel tempo | Knowledge salvato in \`knowledge/\` \+ puntato da \`.cursorrules\` |  
| Overhead iniziale | Giorno 0: solo 6 file minimi. Il resto emerge |

\*\*Non c'è lock-in architetturale\*\*. NH non dice "usa PostgreSQL". Dice "se usi un DB, descrivilo con questi 5 campi". La libertà è tua — la coerenza è garantita dai contratti.

\---

\#\# ⚠️ Avvertenza Critica

\*\*Non modificare mai manualmente\*\*:  
\- \`core/host-reality.mdc\` (descrive il presente fisico — immutabile)  
\- \`core/description-contracts.mdc\` (contratti di descrizione — immutabili)

\*\*Modifica liberamente\*\*:  
\- \`.cursorrules\` (indice dinamico — cresce con te)  
\- \`knowledge/\` (accumulo organico — tuo dominio)

Il nucleo è piccolo perché \*\*non deve essere grande\*\*. Deve solo fornire la bussola per navigare l'evoluzione organica del tuo homelab.

Pronto a iniziare? Copia \`bootstrap.sh\`, eseguilo sul tuo LXC, e apri Trae su \`/opt/nh\`. La prima sessione sarà caotica (nessun knowledge accumulato), ma la seconda sarà già più coerente — e la terza sarà organica.  
