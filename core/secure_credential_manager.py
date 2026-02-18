#!/usr/bin/env python3
"""
Secure Credential Manager - NH Framework
Gestore credenziali con SOPS + Age per sicurezza enterprise
"""

import os
import sys
import json
import yaml
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core.credential_cache import get_credential, clear_credential

class SecureCredentialManager:
    """
    Gestore credenziali sicuro con SOPS + Age
    - Cifra/decifra credenziali con Age
    - Gestisce file .sops.yaml
    - Richiede password Age all'utente quando necessario
    - Cache in-memory per performance
    """
    
    def __init__(self, secrets_dir: str = "secrets", age_key_path: str = None):
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(exist_ok=True)
        
        # Percorso chiave Age
        self.age_key_path = age_key_path or os.path.expanduser("~/.age.key")
        if not Path(self.age_key_path).exists():
            raise FileNotFoundError(f"Chiave Age non trovata: {self.age_key_path}")
        
        # Config SOPS
        self.sops_config_path = Path(".sops.yaml")
        self._ensure_sops_config()
    
    def _ensure_sops_config(self):
        """Crea configurazione SOPS se mancante"""
        if not self.sops_config_path.exists():
            config = {
                'creation_rules': [{
                    'path_regex': f'{self.secrets_dir}/.*\\.enc\\.yaml$',
                    'encrypted_regex': '^(password|token|api_key|secret|key|ssh_key|private_key)$',
                    'age': self._get_age_public_key()
                }]
            }
            
            with open(self.sops_config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            print(f"✅ Creato {self.sops_config_path}")
    
    def _get_age_public_key(self) -> str:
        """Estrae la chiave pubblica dal file chiave Age"""
        try:
            with open(self.age_key_path, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('# public key: '):
                        return line.replace('# public key: ', '').strip()
            
            # Se non trovata nel file, genera da chiave privata
            result = subprocess.run(
                ['age-keygen', '-y', self.age_key_path],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
            
        except Exception as e:
            raise RuntimeError(f"Impossibile ottenere chiave pubblica Age: {e}")
    
    def _get_age_key(self) -> str:
        """Ottiene chiave Age privata"""
        try:
            with open(self.age_key_path, 'r') as f:
                content = f.read().strip()
                # Rimuovi commenti e prendi solo la chiave
                lines = [line for line in content.split('\n') if not line.startswith('#')]
                return '\n'.join(lines)
        except Exception as e:
            raise RuntimeError(f"Impossibile leggere chiave Age: {e}")
    
    def store_credential(self, service: str, credential_name: str, data: Dict[str, Any]) -> bool:
        """Salva credenziali cifrate"""
        try:
            file_path = self.secrets_dir / f"{service}.{credential_name}.enc.yaml"
            
            # Prepara dati per SOPS
            sops_data = {
                'service': service,
                'credential_name': credential_name,
                'created_at': datetime.now().isoformat(),
                'data': data
            }
            
            # Salva temporaneamente in chiaro
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
            yaml.dump(sops_data, temp_file, default_flow_style=False)
            temp_file.close()
            
            # Cifra con SOPS (scrive su stdout)
            env = os.environ.copy()
            env['SOPS_AGE_KEY_FILE'] = str(self.age_key_path)
            
            result = subprocess.run([
                'sops', '--encrypt', '--age', self._get_age_public_key(),
                temp_file.name
            ], env=env, capture_output=True, text=True, check=True)
            
            # Scrivi output su file
            with open(file_path, 'w') as f:
                f.write(result.stdout)
            
            # Pulisci temporaneo
            os.unlink(temp_file.name)
            
            print(f"✅ Credenziali salvate: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Errore salvataggio credenziali: {e}")
            return False
    
    def get_credential(self, service: str, credential_name: str) -> Optional[Dict[str, Any]]:
        """Recupera credenziali decifrate"""
        try:
            file_path = self.secrets_dir / f"{service}.{credential_name}.enc.yaml"
            
            if not file_path.exists():
                return None
            
            # Decifra con SOPS
            env = os.environ.copy()
            env['SOPS_AGE_KEY_FILE'] = str(self.age_key_path)
            
            result = subprocess.run([
                'sops', '--decrypt', str(file_path)
            ], env=env, capture_output=True, text=True, check=True)
            
            # Parse risultato
            data = yaml.safe_load(result.stdout)
            return data.get('data', {})
            
        except Exception as e:
            print(f"❌ Errore recupero credenziali: {e}")
            return None
    
    def list_credentials(self) -> Dict[str, list]:
        """Elenca tutte le credenziali disponibili"""
        credentials = {}
        
        for file_path in self.secrets_dir.glob("*.enc.yaml"):
            if file_path.is_file():
                # Rimuovi .enc.yaml e split
                base_name = file_path.name.replace('.enc.yaml', '')
                parts = base_name.split('.')
                if len(parts) >= 2:
                    service = parts[0]
                    cred_name = '.'.join(parts[1:])
                    
                    if service not in credentials:
                        credentials[service] = []
                    credentials[service].append(cred_name)
        
        return credentials
    
    def delete_credential(self, service: str, credential_name: str) -> bool:
        """Elimina credenziali"""
        try:
            file_path = self.secrets_dir / f"{service}.{credential_name}.enc.yaml"
            
            if file_path.exists():
                file_path.unlink()
                print(f"🗑️  Credenziali eliminate: {file_path}")
                return True
            else:
                print(f"⚠️  Credenziali non trovate: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Errore eliminazione credenziali: {e}")
            return False

# Singleton globale per NH
_credential_manager: Optional[SecureCredentialManager] = None

def get_credential_manager() -> SecureCredentialManager:
    """Ottieni istanza singleton del gestore credenziali"""
    global _credential_manager
    
    if _credential_manager is None:
        _credential_manager = SecureCredentialManager()
    
    return _credential_manager

def store_service_credential(service: str, name: str, data: Dict[str, Any]) -> bool:
    """Helper per salvare credenziali servizio"""
    return get_credential_manager().store_credential(service, name, data)

def get_service_credential(service: str, name: str) -> Optional[Dict[str, Any]]:
    """Helper per recuperare credenziali servizio"""
    return get_credential_manager().get_credential(service, name)

if __name__ == "__main__":
    # Test del sistema
    print("🔐 NH Secure Credential Manager - Test")
    print("=" * 50)
    
    manager = get_credential_manager()
    
    # Test salvataggio
    test_data = {
        'username': 'test_user',
        'password': 'test_password_123',
        'api_key': 'test_api_key_secret'
    }
    
    if manager.store_credential('test', 'proxmox', test_data):
        print("✅ Credenziali salvate con successo")
        
        # Test recupero
        retrieved = manager.get_credential('test', 'proxmox')
        if retrieved:
            print(f"✅ Credenziali recuperate: {retrieved}")
        
        # Test lista
        creds = manager.list_credentials()
        print(f"📋 Credenziali disponibili: {creds}")
        
        # Cleanup
        manager.delete_credential('test', 'proxmox')
    
    print("\n🎯 Test completato!")