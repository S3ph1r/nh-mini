#!/usr/bin/env python3
"""
Credential Cache System - NH Framework
Sistema di cache per credenziali in memoria senza scrittura su disco
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CachedCredential:
    value: str
    timestamp: datetime
    expires_at: datetime
    source: str  # 'user_input', 'sops', 'environment'

class CredentialCache:
    """
    Cache in-memory per credenziali sensibili
    - Mai scrive su disco
    - Auto-expire dopo timeout
    - Richiede input utente se non in cache
    """
    
    def __init__(self, default_timeout_minutes: int = 15):
        self.cache: Dict[str, CachedCredential] = {}
        self.default_timeout = timedelta(minutes=default_timeout_minutes)
        self._session_id = os.getpid()  # Per debugging sessione
    
    def get(self, key: str, prompt_message: str = None, secret: bool = True) -> Optional[str]:
        """
        Ottiene credenziale dalla cache o richiede input utente
        
        Args:
            key: Nome credenziale (es: 'github_token', 'proxmox_password')
            prompt_message: Messaggio per l'utente se richiesto
            secret: Se True, nasconde input (per password/token)
        
        Returns:
            Valore credenziale o None se utente annulla
        """
        # Controlla cache valida
        if key in self.cache:
            cached = self.cache[key]
            if datetime.now() < cached.expires_at:
                print(f"ℹ️  Usando {key} dalla cache (fonte: {cached.source})")
                return cached.value
            else:
                print(f"ℹ️  Cache {key} scaduta, richiedo nuovo input")
                del self.cache[key]
        
        # Richiedi input utente
        if not prompt_message:
            prompt_message = f"Inserisci {key}: "
        
        try:
            if secret:
                import getpass
                value = getpass.getpass(prompt_message)
            else:
                value = input(prompt_message)
            
            if not value:
                print(f"⚠️  Input {key} annullato")
                return None
            
            # Salva in cache
            self._store(key, value, 'user_input')
            print(f"✅ {key} salvato in cache per {self.default_timeout.total_seconds()/60:.0f} minuti")
            return value
            
        except (KeyboardInterrupt, EOFError):
            print(f"\n⚠️  Input {key} interrotto")
            return None
    
    def _store(self, key: str, value: str, source: str):
        """Salva in cache (solo memoria)"""
        expires_at = datetime.now() + self.default_timeout
        self.cache[key] = CachedCredential(
            value=value,
            timestamp=datetime.now(),
            expires_at=expires_at,
            source=source
        )
    
    def clear(self, key: str = None):
        """Pulisce cache"""
        if key:
            if key in self.cache:
                del self.cache[key]
                print(f"🧹 Cache {key} pulita")
        else:
            self.cache.clear()
            print("🧹 Cache completa pulita")
    
    def status(self) -> Dict[str, Any]:
        """Stato cache per debugging"""
        now = datetime.now()
        return {
            'session_id': self._session_id,
            'cached_keys': list(self.cache.keys()),
            'expired_keys': [
                key for key, cred in self.cache.items()
                if now >= cred.expires_at
            ],
            'total_cached': len(self.cache)
        }

# Singleton globale per NH
cache = CredentialCache()

def get_credential(key: str, prompt_message: str = None, secret: bool = True) -> Optional[str]:
    """Funzione helper per ottenere credenziali"""
    return cache.get(key, prompt_message, secret)

def clear_credential(key: str = None):
    """Pulisce credenziali dalla cache"""
    cache.clear(key)

def cache_status() -> Dict[str, Any]:
    """Stato cache per debugging"""
    return cache.status()

if __name__ == "__main__":
    # Test rapido
    print("🔐 NH Credential Cache - Test")
    print("=" * 40)
    
    # Test cache
    token = get_credential("github_token", "GitHub Token: ")
    if token:
        print(f"Token ricevuto: {token[:8]}...")
        
        # Test riutilizzo cache
        token2 = get_credential("github_token")
        if token2:
            print("✅ Cache funzionante!")
    
    print("\n📊 Stato cache:")
    print(cache_status())