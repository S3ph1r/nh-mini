#!/usr/bin/env bash
# NH-Mini: Setup completo LXC da Proxmox host
# Zero touch su Proxmox, tutto automatizzato

set -euo pipefail

# Colori output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
prompt() { echo -n -e "${BLUE}[?]${NC} $1: "; }

# Variabili globali
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NH_REPO="https://github.com/S3ph1r/nh-mini.git"

# Input utente
gather_input() {
    info "=== NH-Mini LXC Setup ==="
    info "Inserisci i parametri per configurare il container LXC"
    
    prompt "LXC ID da configurare"
    read -r LXC_ID
    
    prompt "IP LXC (es: 192.168.1.205)"
    read -r LXC_IP
    
    prompt "Password root Proxmox (temporanea, per setup SSH)"
    read -rs PROXMOX_PASS
    echo
    
    prompt "Password per credenziali NH-Mini (da ricordare)"
    read -rs NH_PASSWORD
    echo
    
    prompt "GitHub token (opzionale, per repo privati)"
    read -r GITHUB_TOKEN
    
    # Conferma
    echo
    info "Riepilogo configurazione:"
    info "  LXC ID: $LXC_ID"
    info "  IP LXC: $LXC_IP"
    info "  GitHub token: $([ -n "$GITHUB_TOKEN" ] && echo "Fornito" || echo "Nessuno")"
    
    prompt "Procedere con la configurazione? (s/N)"
    read -r CONFIRM
    if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
        error "Configurazione annullata"
        exit 1
    fi
}

# Verifica prerequisiti Proxmox
verify_proxmox() {
    info "Verifica ambiente Proxmox..."
    
    # Verifica comando pct
    if ! command -v pct >/dev/null 2>&1; then
        error "Comando 'pct' non trovato - assicurati di essere su un host Proxmox"
        exit 1
    fi
    
    # Verifica LXC esista
    if ! pct list | grep -q "^\\s*$LXC_ID\\s"; then
        error "Container LXC $LXC_ID non trovato"
        error "Container disponibili:"
        pct list
        exit 1
    fi
    
    # Verifica LXC sia running
    if ! pct status $LXC_ID | grep -q "status: running"; then
        info "Avvio container LXC $LXC_ID..."
        pct start $LXC_ID
        sleep 5
    fi
    
    success "Container LXC $LXC_ID verificato"
}

# Installa requirements in LXC
install_requirements() {
    info "Installazione requirements in LXC $LXC_ID..."
    
    pct exec $LXC_ID -- apt update
    pct exec $LXC_ID -- apt install -y \
        git \
        python3 \
        python3-pip \
        python3-yaml \
        curl \
        wget \
        openssh-client \
        sshpass
    
    success "Requirements installati"
}

# Setup SSH bidirezionale
setup_ssh() {
    info "Setup SSH bidirezionale..."
    
    # Genera chiave SSH in LXC se non esiste
    if ! pct exec $LXC_ID -- test -f /root/.ssh/id_ed25519; then
        info "Generazione chiave SSH in LXC..."
        pct exec $LXC_ID -- ssh-keygen -t ed25519 -N "" -f /root/.ssh/id_ed25519 -C "nh-mini-lxc-$LXC_ID"
        pct exec $LXC_ID -- chmod 600 /root/.ssh/id_ed25519
        pct exec $LXC_ID -- chmod 644 /root/.ssh/id_ed25519.pub
    fi
    
    # Ottieni chiave pubblica LXC
    LXC_PUB_KEY=$(pct exec $LXC_ID -- cat /root/.ssh/id_ed25519.pub)
    
    # Installa chiave pubblica su Proxmox (usa password temporanea)
    info "Installazione chiave pubblica su Proxmox..."
    echo "$PROXMOX_PASS" | sshpass -p "$PROXMOX_PASS" ssh -o StrictHostKeyChecking=no root@localhost \
        "mkdir -p /root/.ssh && echo '$LXC_PUB_KEY' >> /root/.ssh/authorized_keys && chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys"
    
    # Configura SSH client in LXC per Proxmox
    pct exec $LXC_ID -- mkdir -p /root/.ssh
    pct exec $LXC_ID -- bash -c "cat > /root/.ssh/config << 'EOF'
Host proxmox
    HostName 192.168.1.2
    User root
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
EOF"
    
    # Test connessione
    if pct exec $LXC_ID -- ssh -o ConnectTimeout=5 proxmox "echo 'SSH test OK'"; then
        success "SSH bidirezionale configurato"
    else
        warning "SSH test fallito, ma procediamo comunque"
    fi
}

# Clona repository NH-Mini
clone_repository() {
    info "Clonazione repository NH-Mini..."
    
    if [[ -n "$GITHUB_TOKEN" ]]; then
        # Usa token per repo privati
        REPO_URL="https://${GITHUB_TOKEN}@github.com/S3ph1r/nh-mini.git"
        info "Utilizzo GitHub token per accesso repository"
    else
        # Repo pubblico
        REPO_URL="$NH_REPO"
        info "Repository pubblico"
    fi
    
    # Clona in LXC
    pct exec $LXC_ID -- rm -rf /root/nh-mini 2>/dev/null || true
    pct exec $LXC_ID -- git clone "$REPO_URL" /root/nh-mini
    
    success "Repository clonato"
}

# Setup SOPS locale
setup_sops() {
    info "Setup SOPS e age per credenziali..."
    
    # Installa age se manca
    if ! pct exec $LXC_ID -- command -v age >/dev/null 2>&1; then
        info "Installazione age (encryption tool)..."
        pct exec $LXC_ID -- bash -c "
            cd /tmp &&
            wget -q https://github.com/FiloSottile/age/releases/latest/download/age-linux-amd64.tar.gz &&
            tar -xzf age-linux-amd64.tar.gz &&
            mv age/age /usr/local/bin/ &&
            mv age/age-keygen /usr/local/bin/ &&
            chmod +x /usr/local/bin/age* &&
            rm -rf age*"
    fi
    
    # Genera chiave age con password utente
    info "Generazione chiave age..."
    echo "$NH_PASSWORD" | pct exec $LXC_ID -- bash -c "
        mkdir -p /root/.nh-mini &&
        age-keygen -o /root/.nh-mini/age.key 2>/dev/null << 'EOF'
$NH_PASSWORD
$NH_PASSWORD
EOF"
    
    # Setup SOPS config
    pct exec $LXC_ID -- bash -c "cat > /root/nh-mini/.sops.yaml << 'EOF'
creation_rules:
  - path_regex: credentials/.*
    age: '$(pct exec $LXC_ID -- age-keygen -y /root/.nh-mini/age.key)'
EOF"
    
    success "SOPS configurato"
}

# Bootstrap NH-Mini
bootstrap_nh_mini() {
    info "Bootstrap NH-Mini..."
    
    # Crea file ambiente per password SOPS
    pct exec $LXC_ID -- bash -c "echo 'export NH_MINI_AGE_KEY_FILE=/root/.nh-mini/age.key' > /root/.nh-mini/env"
    
    # Esegui bootstrap con modalità LXC
    pct exec $LXC_ID -- bash -c "
        cd /root/nh-mini &&
        source /root/.nh-mini/env &&
        bash bootstrap.sh --lxc-mode --proxmox-ip 192.168.1.2"
    
    success "NH-Mini bootstrap completato"
}

# Main function
main() {
    # Verifica privilegi root
    if [[ $EUID -ne 0 ]]; then
        error "Questo script deve essere eseguito come root"
        exit 1
    fi
    
    gather_input
    verify_proxmox
    install_requirements
    setup_ssh
    clone_repository
    setup_sops
    bootstrap_nh_mini
    
    echo
    success "=== Setup NH-Mini completato! ==="
    info "Container LXC $LXC_ID è pronto con NH-Mini"
    info "Puoi accedere con: pct exec $LXC_ID -- bash"
    info "Directory NH-Mini: /root/nh-mini"
    info "Password credenziali: (quella che hai scelto)"
}

# Esecuzione
main "$@"