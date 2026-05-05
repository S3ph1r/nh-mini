#!/bin/bash
# setup_ct202_gateway.sh
# Setup CT202 come Internet Gateway (nginx + ngrok)
# Eseguire sul container vergine come root dopo il primo boot.
#
# Uso: bash setup_ct202_gateway.sh <NGROK_AUTHTOKEN>
# Esempio: bash setup_ct202_gateway.sh 2abc123xyz...
#
# Per recuperare il token da SOPS (da NH-Mini):
#   python3 scripts/credential_manager.py get ngrok authtoken

set -euo pipefail

NGROK_TOKEN="${1:-}"
NGROK_DOMAIN="obliging-fitting-cheetah.ngrok-free.app"

# ─── Validazione ──────────────────────────────────────────────────────────────

if [[ -z "$NGROK_TOKEN" ]]; then
    echo "❌ Authtoken ngrok richiesto."
    echo "   Uso: bash $0 <NGROK_AUTHTOKEN>"
    echo "   Da NH-Mini: python3 scripts/credential_manager.py get ngrok authtoken"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CT202 — Internet Gateway Setup                         ║"
echo "║  nginx reverse proxy + ngrok tunnel                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ─── 1. Sistema base ──────────────────────────────────────────────────────────

echo "📦 [1/5] Aggiornamento sistema e installazione dipendenze..."
apt-get update -qq
apt-get install -y -qq nginx curl

# ─── 2. nginx — configurazione base ──────────────────────────────────────────

echo "🔧 [2/5] Configurazione nginx..."

# Rimuovi config default e eventuali file residui da run precedenti
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default
rm -f /etc/nginx/conf.d/*.conf /etc/nginx/conf.d/*.disabled 2>/dev/null || true

# Crea directory per i location block
mkdir -p /etc/nginx/locations.d

# Template location (per aggiungere nuovi servizi)
cat > /etc/nginx/locations.d/_template.disabled << 'EOF'
# TEMPLATE — Copia, rinomina (es: myapp.conf), rimuovi .disabled
# Poi: nginx -t && nginx -s reload

location /NOME-SERVIZIO/ {
    proxy_pass          http://192.168.1.XXX:PORTA/;
    proxy_set_header    Host              $host;
    proxy_set_header    X-Real-IP         $remote_addr;
    proxy_set_header    X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto $scheme;
    proxy_read_timeout  300s;
    proxy_buffering     off;
}
EOF

# DIAS location — CT201:8000
cat > /etc/nginx/locations.d/dias.conf << 'EOF'
location /dias/ {
    proxy_pass          http://192.168.1.201:8000/;
    proxy_set_header    Host              $host;
    proxy_set_header    X-Real-IP         $remote_addr;
    proxy_set_header    X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto $scheme;
    proxy_read_timeout  300s;
    proxy_buffering     off;
    proxy_http_version  1.1;
    proxy_set_header    Upgrade    $http_upgrade;
    proxy_set_header    Connection "upgrade";
}
EOF

# Grafana location (disabilitata — abilitare quando CT103 è configurato)
cat > /etc/nginx/locations.d/grafana.disabled << 'EOF'
location /grafana/ {
    proxy_pass          http://192.168.1.103:3000/;
    proxy_set_header    Host              $host;
    proxy_set_header    X-Real-IP         $remote_addr;
    proxy_set_header    X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header    X-Forwarded-Proto $scheme;
    proxy_read_timeout  300s;
}
# NOTA: Grafana richiede su CT103:
#   GF_SERVER_ROOT_URL=https://DOMINIO/grafana
#   GF_SERVER_SERVE_FROM_SUB_PATH=true
EOF

# Server block principale — include tutti i *.conf in locations.d/
cat > /etc/nginx/conf.d/gateway.conf << 'EOF'
server {
    listen 80;
    server_name _;

    access_log /var/log/nginx/gateway_access.log;
    error_log  /var/log/nginx/gateway_error.log;

    add_header ngrok-skip-browser-warning "true" always;

    location = /health {
        return 200 "ok\n";
        add_header Content-Type text/plain;
    }

    location = / {
        return 302 /dias/;
    }

    # Carica tutti i servizi abilitati
    include /etc/nginx/locations.d/*.conf;
}
EOF

nginx -t
systemctl enable nginx
systemctl restart nginx
echo "   ✅ nginx pronto"

# ─── 3. ngrok — installazione ────────────────────────────────────────────────

echo "🔧 [3/5] Installazione ngrok..."
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
    | tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
    | tee /etc/apt/sources.list.d/ngrok.list > /dev/null
apt-get update -qq
apt-get install -y -qq ngrok

ngrok config add-authtoken "$NGROK_TOKEN"
echo "   ✅ ngrok installato e configurato"

# ─── 4. systemd service per ngrok ────────────────────────────────────────────

echo "🔧 [4/5] Configurazione autostart ngrok (systemd)..."

cat > /etc/systemd/system/ngrok.service << EOF
[Unit]
Description=ngrok HTTP Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/ngrok http --domain=${NGROK_DOMAIN} 80
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ngrok
systemctl start ngrok
sleep 3

if systemctl is-active --quiet ngrok; then
    echo "   ✅ ngrok in esecuzione"
else
    echo "   ⚠️  ngrok non avviato — controlla: journalctl -u ngrok -n 20"
fi

# ─── 5. Summary ───────────────────────────────────────────────────────────────

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CT202 Gateway pronto"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URL pubblico:  https://${NGROK_DOMAIN}"
echo "🎯 Servizi attivi:"
echo "   /dias/    → CT201:8000 (DIAS Dashboard)"
echo ""
echo "📁 Config nginx: /etc/nginx/conf.d/"
echo "   Per aggiungere servizi: copia _template.conf.disabled"
echo ""
echo "🔧 Comandi utili:"
echo "   nginx -s reload               # Ricarica config nginx"
echo "   systemctl status ngrok        # Stato tunnel"
echo "   journalctl -u ngrok -f        # Log ngrok live"
echo ""
echo "⚠️  Ricorda: ogni app esposta deve essere configurata"
echo "   per il suo sub-path. Vedi:"
echo "   knowledge/network/internet-gateway-pattern.mdc"
