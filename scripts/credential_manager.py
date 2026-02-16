#!/usr/bin/env python3
"""
Sistema Unificato di Gestione Credenziali NH-Mini
Tutte le credenziali in SOPS+Age con deduplicazione e cache intelligente
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from secure_credential_manager import get_service_credential, store_service_credential
from credential_cache import CredentialCache

class UnifiedCredentialManager:
    """Gestore unificato per tutte le credenziali del sistema"""
    
    def __init__(self):
        self.cache = CredentialCache()
        self.cache_duration = timedelta(minutes=15)
        
    def get_credential(self, service: str, key: str, interactive: bool = True) -> Optional[Dict[str, Any]]:
        """
        Recupera credenziali con strategia:
        1. Prova SOPS (persistente)
        2. Prova cache temporanea (15min)
        3. Se interactive=True, chiedi all'utente e salva in SOPS
        
        Args:
            service: Nome servizio (es: 'github', 'proxmox', 'db')
            key: Chiave specifica (es: 'main', 'backup', 'app1')
            interactive: Se True, chiedi all'utente se non trovato
        
        Returns:
            Dict con credenziali o None
        """
        service_key = f"{service}.{key}"
        
        # 1. Prova SOPS (persistente)
        try:
            creds = get_service_credential(service, key)
            if creds:
                print(f"🔐 Credenziali {service_key} trovate in SOPS")
                # Aggiorna anche cache per performance
                self.cache._store(service_key, json.dumps(creds), 'sops')
                return creds
        except Exception as e:
            print(f"⚠️  SOPS non disponibile per {service_key}: {e}")
        
        # 2. Prova cache temporanea
        cached = self.cache.get(service_key, "", secret=False)
        if cached:
            try:
                creds = json.loads(cached)
                print(f"⚡ Credenziali {service_key} trovate in cache")
                return creds
            except json.JSONDecodeError:
                pass
        
        # 3. Se interactive, chiedi all'utente
        if interactive:
            print(f"🔐 Credenziali {service_key} non trovate.")
            
            if service == "github":
                return self._interactive_github_setup(key)
            elif service == "proxmox":
                return self._interactive_proxmox_setup(key)
            else:
                return self._interactive_generic_setup(service, key)
        
        print(f"❌ Credenziali {service_key} non trovate e modalità non-interactive")
        return None
    
    def store_credential(self, service: str, key: str, data: Dict[str, Any], 
                        deduplicate: bool = True) -> bool:
        """
        Salva credenziali in SOPS con deduplicazione opzionale
        
        Args:
            service: Nome servizio
            key: Chiave specifica
            data: Dati credenziali
            deduplicate: Se True, verifica che non esistano già
        
        Returns:
            True se salvato con successo
        """
        service_key = f"{service}.{key}"
        
        # Verifica deduplicazione
        if deduplicate:
            existing = get_service_credential(service, key)
            if existing:
                print(f"⚠️  Credenziali {service_key} già esistenti, skip")
                return False
        
        # Salva in SOPS
        try:
            success = store_service_credential(service, key, data)
            if success:
                print(f"✅ Credenziali {service_key} salvate in SOPS")
                # Aggiorna anche cache
                self.cache._store(service_key, json.dumps(data), 'sops')
                return True
            else:
                print(f"❌ Errore salvataggio {service_key} in SOPS")
                return False
        except Exception as e:
            print(f"❌ Eccezione salvataggio {service_key}: {e}")
            return False
    
    def check_credential_exists(self, service: str, key: str) -> bool:
        """Verifica se credenziali esistono in SOPS"""
        try:
            creds = get_service_credential(service, key)
            return creds is not None
        except:
            return False
    
    def list_services(self) -> Dict[str, List[str]]:
        """Elenca tutti i servizi e le loro chiavi"""
        # Questa richiederebbe una funzione di listing da secure_credential_manager
        # Per ora restituiamo struttura vuota
        return {}
    
    def _interactive_github_setup(self, key: str) -> Optional[Dict[str, Any]]:
        """Setup interattivo per credenziali GitHub"""
        print("🐙 Setup GitHub Token:")
        print("   1. Vai su: https://github.com/settings/tokens")
        print("   2. Crea 'Personal Access Token'")
        print("   3. Seleziona almeno: repo, write:packages")
        print()
        
        from getpass import getpass
        token = getpass("🔑 Inserisci GitHub Token: ").strip()
        
        if not token:
            print("❌ Token non fornito")
            return None
        
        creds = {
            "token": token,
            "username": "S3ph1r",  # Il nostro username GitHub
            "created_at": datetime.utcnow().isoformat(),
            "note": "Token per push NH-Mini"
        }
        
        # Salva in SOPS
        if self.store_credential("github", key, creds):
            return creds
        else:
            return None
    
    def _interactive_proxmox_setup(self, key: str) -> Optional[Dict[str, Any]]:
        """Setup interattivo per credenziali Proxmox"""
        print("🔧 Setup Proxmox:")
        
        from getpass import getpass
        host = input("🌐 Proxmox Host (es: 192.168.1.2): ").strip() or "192.168.1.2"
        user = input("👤 Username (es: root@pam): ").strip() or "root@pam"
        password = getpass("🔑 Password: ").strip()
        
        if not password:
            print("❌ Password richiesta")
            return None
        
        creds = {
            "host": host,
            "username": user,
            "password": password,
            "created_at": datetime.utcnow().isoformat(),
            "note": "Credenziali Proxmox per NH-Mini"
        }
        
        # Salva in SOPS
        if self.store_credential("proxmox", key, creds):
            return creds
        else:
            return None
    
    def _interactive_generic_setup(self, service: str, key: str) -> Optional[Dict[str, Any]]:
        """Setup interattivo generico per qualsiasi servizio"""
        print(f"🔧 Setup {service}:")
        
        from getpass import getpass
        username = input(f"👤 Username per {service}: ").strip()
        password = getpass(f"🔑 Password per {service}: ").strip()
        
        if not password:
            print("❌ Password richiesta")
            return None
        
        creds = {
            "username": username,
            "password": password,
            "created_at": datetime.utcnow().isoformat(),
            "note": f"Credenziali {service} per NH-Mini"
        }
        
        # Salva in SOPS
        if self.store_credential(service, key, creds):
            return creds
        else:
            return None

def main():
    """CLI per gestione credenziali unificate"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestione Credenziali NH-Mini')
    parser.add_argument('--service', required=True, help='Nome servizio (github, proxmox, etc)')
    parser.add_argument('--key', required=True, help='Chiave specifica (main, backup, etc)')
    parser.add_argument('--get', action='store_true', help='Recupera credenziali')
    parser.add_argument('--store', help='Store JSON data (es: {"token":"abc123"})')
    parser.add_argument('--check', action='store_true', help='Verifica esistenza')
    parser.add_argument('--no-interactive', action='store_true', help='Disabilita input interattivo')
    
    args = parser.parse_args()
    
    manager = UnifiedCredentialManager()
    
    if args.get:
        creds = manager.get_credential(args.service, args.key, interactive=not args.no_interactive)
        if creds:
            print(json.dumps(creds, indent=2))
            sys.exit(0)
        else:
            print("❌ Credenziali non trovate")
            sys.exit(1)
    
    elif args.store:
        try:
            data = json.loads(args.store)
            success = manager.store_credential(args.service, args.key, data)
            sys.exit(0 if success else 1)
        except json.JSONDecodeError:
            print("❌ JSON non valido")
            sys.exit(1)
    
    elif args.check:
        exists = manager.check_credential_exists(args.service, args.key)
        print(f"{'✅' if exists else '❌'} Credenziali {args.service}.{args.key}")
        sys.exit(0 if exists else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()