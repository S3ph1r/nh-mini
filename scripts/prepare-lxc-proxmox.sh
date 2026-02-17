#!/bin/bash
# Script per preparare LXC da Proxmox host
# Usage: ./prepare-lxc-proxmox.sh <LXC_ID> <LXC_IP> [PASSWORD]

set -e

LXC_ID="${1:-200}"
LXC_IP="${2:-192.168.1.200}"
PASSWORD="${3:-nhmini2024}"

echo "🚀 Preparazione LXC $LXC_ID ($LXC_IP)"

# Verifica LXC esiste
if ! pct list | grep -q "\s$LXC_ID\s"; then
    echo "❌ LXC $LXC_ID non trovato"
    exit 1
fi

# Verifica LXC è running
if ! pct status "$LXC_ID" | grep -q "running"; then
    echo "📦 Avvio LXC $LXC_ID..."
    pct start "$LXC_ID"
    sleep 5
fi

echo "🔑 Reset password root..."
echo "root:$PASSWORD" | pct exec "$LXC_ID" -- chpasswd

echo "📦 Installazione pacchetti base..."
pct exec "$LXC_ID" -- bash -c '
    apt update >/dev/null 2>&1
    apt install -y git curl wget openssh-client python3 python3-pip >/dev/null 2>&1
'

echo "🔓 Abilitazione SSH root..."
pct exec "$LXC_ID" -- bash -c '
    # Backup config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup 2>/dev/null || true
    
    # Abilita root login
    sed -i "s/^#PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config
    sed -i "s/^PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config
    
    # Riavvia SSH
    systemctl restart sshd 2>/dev/null || service ssh restart
'

echo "✅ LXC $LXC_ID pronto!"
echo "📍 IP: $LXC_IP"
echo "🔑 Password: $PASSWORD"
echo ""
echo "Prossimi passi:"
echo "1. ssh root@$LXC_IP"
echo "2. git clone https://github.com/S3ph1r/nh-mini.git"
echo "3. cd nh-mini && ./scripts/nh-setup-lxc.sh"