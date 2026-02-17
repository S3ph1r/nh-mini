#!/usr/bin/env bash
# NH_mini - Bootstrap Script
# Installazione framework NH su LXC Proxmox vuoto

set -eo pipefail

# Gestione parametri
SKIP_PROXMOX_CHECK=false
LXC_MODE=false
PROXMOX_IP=""

# Parsing argomenti
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-proxmox-check)
            SKIP_PROXMOX_CHECK=true
            shift
            ;;
        --lxc-mode)
            LXC_MODE=true
            shift
            ;;
        --proxmox-ip)
            PROXMOX_IP="$2"
            shift 2
            ;;
        *)
            # Argomento non riconosciuto, ignora
            shift
            ;;
    esac
done

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni output
banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        NH_mini                              ║"
    echo "║               Minimal Homelab Framework                     ║"
    echo "║                                                              ║"
    echo "║                   Bootstrap Installer                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

prompt() {
    echo -n -e "${BLUE}[?]${NC} $1: "
}

# Variabili globali
PROXMOX_HOST=""
SSH_KEY="${HOME}/.ssh/id_nh"
NH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# STEP 1: Banner + Prerequisiti Check
step1_prerequisiti() {
    banner
    info "STEP 1: Controllo prerequisiti"
    
    # Verifica LXC
    if [[ -f "/.dockerenv" ]] || [[ "${VIRTUALIZATION:-}" == "lxc" ]] || [[ -f "/proc/1/cgroup" && $(grep -c lxc /proc/1/cgroup) -gt 0 ]]; then
        success "Ambiente LXC rilevato"
    else
        warning "Ambiente LXC non confermato, ma procediamo comunque"
    fi
    
    # Verifica connessione Internet
    if ping -c 1 -W 2 github.com >/dev/null 2>&1; then
        success "Connessione Internet attiva"
    else
        error "Connessione Internet assente - alcuni download potrebbero fallire"
    fi
    
    # Verifica pacchetti essenziali
    local missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v ssh >/dev/null 2>&1 || missing+=("openssh-client")
    command -v git >/dev/null 2>&1 || missing+=("git")
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        warning "Pacchetti mancanti: ${missing[*]}"
        info "Installazione automatica via apt-get..."
        apt-get update -y >/dev/null 2>&1
        apt-get install -y "${missing[@]}" >/dev/null 2>&1 || error "Installazione fallita"
    fi
    
    success "Prerequisiti OK"
    echo
}

# STEP 2: Rilevamento Proxmox
step2_detect_proxmox() {
    info "STEP 2: Rilevamento Proxmox Host"
    
    # Inizializza variabile
    PROXMOX_HOST=""
    
    # Modalità LXC: usa IP fornito o auto-rileva
    if [[ "$LXC_MODE" == "true" ]]; then
        if [[ -n "$PROXMOX_IP" ]]; then
            PROXMOX_HOST="$PROXMOX_IP"
            info "Modalità LXC: uso IP Proxmox fornito: $PROXMOX_HOST"
        else
            # Auto-rileva gateway come fallback
            local gateway
            gateway=$(ip route | awk '/default/ {print $3}' | head -n1)
            if [[ -n "$gateway" ]]; then
                PROXMOX_HOST="$gateway"
                info "Modalità LXC: uso gateway rilevato: $PROXMOX_HOST"
            else
                error "Modalità LXC: IP Proxmox non fornito e gateway non rilevato"
                exit 1
            fi
        fi
    else
        # Modalità normale: chiedi all'utente
        # Auto-rileva gateway
        local gateway
        gateway=$(ip route | awk '/default/ {print $3}' | head -n1)
        
        if [[ -n "$gateway" ]]; then
            info "Gateway rilevato: $gateway"
            prompt "IP Proxmox host [${gateway}]"
            read -r PROXMOX_HOST
            PROXMOX_HOST=${PROXMOX_HOST:-$gateway}
        else
            prompt "IP Proxmox host"
            read -r PROXMOX_HOST
        fi
    fi
    
    # Verifica connessione (solo se non skippata)
    if [[ "$SKIP_PROXMOX_CHECK" == "false" ]]; then
        if ping -c 1 -W 2 "$PROXMOX_HOST" >/dev/null 2>&1; then
            success "Proxmox host raggiungibile: $PROXMOX_HOST"
        else
            error "Proxmox host non raggiungibile: $PROXMOX_HOST"
            exit 1
        fi
        
        # Verifica pct su host remoto
        if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "$SSH_KEY" root@"$PROXMOX_HOST" "which pct || which /usr/sbin/pct" >/dev/null 2>&1; then
            success "Comando pct disponibile su host remoto"
        else
            error "pct non trovato su $PROXMOX_HOST - assicurati sia un host Proxmox"
            exit 1
        fi
    else
        warning "Verifica Proxmox skippata (--skip-proxmox-check attivo)"
        success "Assumo ambiente LXC con SSH keys già configurate"
    fi
    
    echo
}

# STEP 3: Setup SSH
step3_setup_ssh() {
    info "STEP 3: Setup SSH (Critico)"
    
    # Modalità LXC: SSH già configurato da nh-setup-lxc.sh
    if [[ "$LXC_MODE" == "true" ]]; then
        info "Modalità LXC: SSH già configurato, skip setup manuale"
        
        # Verifica che SSH funzioni
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" "echo 'SSH test OK'" >/dev/null 2>&1; then
            success "SSH connection verificata in modalità LXC"
        else
            warning "SSH connection test fallito in modalità LXC"
            info "Assicurati che nh-setup-lxc.sh abbia configurato SSH correttamente"
        fi
        
        # Verifica pct access
        local container_count
        container_count=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" "pct list | tail -n +2 | wc -l" 2>/dev/null || echo "0")
        success "Accesso pct confermato - $container_count container rilevati"
        
        echo
        return
    fi
    
    info "Serve password Proxmox per autorizzare chiave SSH (uso temporaneo)"
    
    # Genera chiave SSH se non esiste
    if [[ ! -f "$SSH_KEY" ]]; then
        info "Generazione chiave SSH ed25519..."
        mkdir -p "$(dirname "$SSH_KEY")"
        ssh-keygen -t ed25519 -N "" -f "$SSH_KEY" -C "nh-mini-$(hostname)" >/dev/null 2>&1
        chmod 600 "$SSH_KEY"
        success "Chiave SSH generata: $SSH_KEY"
    else
        success "Chiave SSH esistente: $SSH_KEY"
    fi
    
    # Richiedi password (temporanea)
    local proxmox_pass
    prompt "Password root Proxmox (temporanea, per autorizzare SSH)"
    read -rs proxmox_pass
    echo
    
    # Installa chiave pubblica
    info "Installazione chiave pubblica su Proxmox..."
    
    # Usa sshpass se disponibile, altrimenti fallback
    if command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$proxmox_pass" ssh-copy-id -i "${SSH_KEY}.pub" -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" >/dev/null 2>&1 || {
            warning "ssh-copy-id fallito, provo metodo alternativo..."
            echo "$proxmox_pass" | ssh -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys" || {
                error "Installazione chiave SSH fallita"
                exit 1
            }
        }
    else
        # Fallback senza sshpass
        cat "${SSH_KEY}.pub" | ssh -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys" || {
            error "Installazione chiave SSH fallita"
            exit 1
        }
    fi
    
    # Test connessione
    info "Test connessione SSH..."
    if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "root@$PROXMOX_HOST" "echo 'SSH OK'" >/dev/null 2>&1; then
        success "SSH connection verificata!"
        success "Password Proxmox dimenticata (come promesso)"
    else
        error "SSH connection fallita - verifica manualmente"
        exit 1
    fi
    
    # Verifica pct access
    local container_count
    container_count=$(ssh -i "$SSH_KEY" "root@$PROXMOX_HOST" "pct list | tail -n +2 | wc -l")
    success "Accesso pct confermato - $container_count container rilevati"
    
    echo
}

# STEP 4: SOPS+Age Setup
step4_sops_age() {
    info "STEP 4: Setup SOPS+Age (Cifratura secrets)"
    
    # Modalità LXC: SOPS già configurato da nh-setup-lxc.sh
    if [[ "$LXC_MODE" == "true" ]]; then
        info "Modalità LXC: SOPS già configurato, verifico setup..."
        
        # Verifica che SOPS sia configurato
        if [[ -f "$HOME/.nh-mini/age.key" ]] && [[ -f "$NH_DIR/.sops.yaml" ]]; then
            success "Setup SOPS già completo in modalità LXC"
            
            # Carica ambiente SOPS
            if [[ -f "$HOME/.nh-mini/env" ]]; then
                source "$HOME/.nh-mini/env"
                success "Ambiente SOPS caricato"
            fi
        else
            warning "Setup SOPS incompleto in modalità LXC"
            info "Esegui: python3 scripts/setup_sops_local.py"
        fi
        
        echo
        return
    fi
    
    info "Master password protegge tutti i secrets futuri"
    
    # Installa sops e age se mancano
    if ! command -v sops >/dev/null 2>&1 || ! command -v age-keygen >/dev/null 2>&1; then
        info "Installazione sops e age..."
        apt-get update -y >/dev/null 2>&1
        apt-get install -y sops age >/dev/null 2>&1 || {
            error "Installazione sops/age fallita"
            exit 1
        }
    fi
    
    # Richiedi master password
    local master_pass master_pass_confirm
    while true; do
        prompt "Master password NH (min 12 caratteri)"
        read -rs master_pass
        echo
        
        if [[ ${#master_pass} -lt 12 ]]; then
            error "Password troppo corta (min 12 caratteri)"
            continue
        fi
        
        prompt "Conferma master password"
        read -rs master_pass_confirm
        echo
        
        if [[ "$master_pass" == "$master_pass_confirm" ]]; then
            break
        else
            error "Le password non coincidono"
        fi
    done
    
    # Genera chiave Age da password
    info "Generazione chiave Age..."
    local age_dir="${HOME}/.nh/age"
    local age_key="${age_dir}/age.key"
    
    mkdir -p "$age_dir"
    chmod 700 "$age_dir"
    
    # Genera chiave deterministica da password + salt
    local salt="nhmini$(date +%s)"
    local key_hex key_b64 pubkey
    key_hex=$(printf "%s" "${master_pass}${salt}" | sha256sum | awk '{print $1}')
    key_b64=$(echo "$key_hex" | xxd -r -p | base64 -w0)
    
    cat > "$age_key" <<EOF
# created: $(date -Iseconds)
# public key: $(echo "$key_hex" | head -c32)
age1unknown
AGE-SECRET-KEY-1${key_b64}
EOF
    chmod 600 "$age_key"
    
    # Estrai chiave pubblica
    pubkey=$(age-keygen -y "$age_key" 2>/dev/null || echo "age1unknown")
    
    # Pulisci password dalla memoria
    unset master_pass master_pass_confirm
    
    success "Chiave Age generata"
    echo
    warning "⚠ SALVA QUESTA CHIAVE PUBBLICA IN UN POSTO SICURO ⚠"
    echo "$pubkey"
    echo
    
    prompt "Hai salvato la chiave pubblica? (s/n)"
    local saved
    read -r saved
    if [[ "$saved" != "s" && "$saved" != "S" ]]; then
        error "Devi salvare la chiave pubblica prima di continuare"
        exit 1
    fi
    
    # Crea .sops.yaml
    cat > "${NH_DIR}/.sops.yaml" <<EOF
creation_rules:
  - path_regex: secrets/.*\.enc\.yaml$
    encrypted_regex: '^(password|token|api_key|secret)$'
    age:
      - $pubkey
EOF
    
    success "Configurazione SOPS completata"
    echo
}

# STEP 5: Discovery
step5_discovery() {
    info "STEP 5: Discovery infrastruttura"
    
    # Crea directory se mancano
    mkdir -p "${NH_DIR}/state"
    mkdir -p "${NH_DIR}/secrets"
    
    # Esegui discovery
    if [[ -f "${NH_DIR}/core/discovery.py" ]]; then
        info "Esecuzione discovery..."
        cd "$NH_DIR"
        python3 core/discovery.py || {
            warning "Discovery fallito - verifica core/discovery.py"
        }
        
        # Mostra risultati
        if [[ -f "${NH_DIR}/state/inventory.json" ]]; then
            local container_count
            container_count=$(jq '.containers | length' "${NH_DIR}/state/inventory.json" 2>/dev/null || echo "0")
            success "Discovery completato - $container_count container trovati"
            
            if [[ $container_count -gt 0 ]]; then
                info "Container rilevati:"
                jq -r '.containers[] | "  - \(.name) (VMID: \(.vmid), IP: \(.ip // "N/A"), Status: \(.status))"' "${NH_DIR}/state/inventory.json" 2>/dev/null || true
            fi
        else
            warning "File inventory.json non creato"
        fi
    else
        warning "discovery.py non trovato - salto discovery"
    fi
    
    echo
}

# STEP 6: Git Init
step6_git_init() {
    info "STEP 6: Inizializzazione Git"
    
    cd "$NH_DIR"
    
    if [[ ! -d ".git" ]]; then
        git init -q
        git config user.name "NH_mini Bootstrap"
        git config user.email "nh@localhost"
        
        # Crea commit iniziale
        git add . 2>/dev/null || true
        git commit -m "Initial NH bootstrap" 2>/dev/null || true
        
        success "Repository Git inizializzato"
    else
        info "Repository Git già esistente"
    fi
    
    echo
}

# STEP 7: Riepilogo
step7_summary() {
    info "STEP 7: Riepilogo finale"
    echo
    echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    BOOTSTRAP COMPLETATO!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
    echo
    
    echo "Credenziali e percorsi importanti:"
    echo "  📁 Directory NH:        $NH_DIR"
    echo "  🔑 Chiave SSH:          $SSH_KEY"
    echo "  🔐 Chiave Age:          ${HOME}/.nh/age/age.key"
    echo "  📋 Config SOPS:         ${NH_DIR}/.sops.yaml"
    echo "  📊 Inventory:           ${NH_DIR}/state/inventory.json"
    echo "  🔒 Secrets:             ${NH_DIR}/secrets/"
    echo
    
    echo "Prossimi passi consigliati:"
    echo "  1. Testa accesso SSH:  ssh -i $SSH_KEY root@$PROXMOX_HOST 'pct list'"
    echo "  2. Verifica discovery:   cd $NH_DIR && python3 core/discovery.py"
    echo "  3. Crea tuo container:   Documenta in knowledge/ e deploya"
    echo "  4. Backup chiavi:       Copia ~/.nh/age/age.key in luogo sicuro"
    echo
    
    warning "⚠  Ricorda: la chiave pubblica Age mostrata sopra è critica per recuperare secrets!"
    
    echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
}

# Main
main() {
    step1_prerequisiti
    step2_detect_proxmox
    step3_setup_ssh
    step4_sops_age
    step5_discovery
    step6_git_init
    step7_summary
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "NH-Mini Bootstrap Installer"
    echo ""
    echo "Options:"
    echo "  --skip-proxmox-check    Skip Proxmox connectivity verification"
    echo "  --lxc-mode             Run in LXC mode (pre-configured environment)"
    echo "  --proxmox-ip IP        Specify Proxmox host IP (for LXC mode)"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Modalità interattiva normale"
    echo "  $0 --skip-proxmox-check              # Salta verifica Proxmox"
    echo "  $0 --lxc-mode --proxmox-ip 192.168.1.2  # Modalità LXC"
    echo ""
    exit 0
}

# Gestione help
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    show_help
fi

# Esegui se non source-ato
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi