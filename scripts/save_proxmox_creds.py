#!/usr/bin/env python3
"""
Tool sicuro per salvare credenziali Proxmox in SOPS

Usage:
    python3 scripts/save_proxmox_creds.py
    
Il tool chiederà interattivamente host, username e password
e li salverà in SOPS in modo sicuro.
"""

import sys
import os
sys.path.append('/home/Projects/NH-Mini')

from core.secure_credential_manager import store_service_credential

def main():
    print("🔐 Salvataggio credenziali Proxmox in SOPS")
    print("=" * 50)
    
    # Richiedi credenziali in modo interattivo
    host = input("Host Proxmox (es. 192.168.1.2): ").strip()
    if not host:
        print("❌ Host richiesto")
        return False
        
    username = input("Username (default: root): ").strip() or "root"
    password = input("Password: ").strip()
    if not password:
        print("❌ Password richiesta")
        return False
    
    # Crea credenziali
    creds = {
        'host': host,
        'username': username,
        'password': password
    }
    
    print(f"\n📋 Riepilogo:")
    print(f"   Host: {host}")
    print(f"   User: {username}")
    print(f"   Pass: {'*' * len(password)}")
    
    conferma = input("\nSalvare queste credenziali? (s/N): ").strip().lower()
    if conferma != 's':
        print("❌ Salvataggio annullato")
        return False
    
    # Salva in SOPS
    print("\n🔐 Salvataggio in SOPS...")
    if store_service_credential('proxmox', 'main', creds):
        print("✅ Credenziali Proxmox salvate con successo!")
        print(f"   File: secrets/proxmox.main.enc.yaml")
        return True
    else:
        print("❌ Errore nel salvataggio")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)