#!/usr/bin/env python3
"""
GitHub Push Script - Sicuro con SOPS+Age Credential System
Non hardcodare mai credenziali!
"""

import os
import sys
import subprocess
from pathlib import Path

# Aggiungi core e scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from credential_cache import clear_credential
from credential_manager import UnifiedCredentialManager

def check_git_repo():
    """Verifica se siamo in un repository git"""
    if not (Path.cwd() / ".git").exists():
        print("❌ Non sei in un repository Git")
        return False
    return True

def get_git_changes():
    """Mostra modifiche non committate"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if result.stdout:
            print("📋 Modifiche non committate:")
            print(result.stdout)
            return True
        else:
            print("✅ Nessuna modifica da committare")
            return False
    except Exception as e:
        print(f"❌ Errore git status: {e}")
        return False

def commit_changes():
    """Commit modifiche con messaggio"""
    try:
        # Add all changes
        subprocess.run(["git", "add", "."], check=True)
        
        # Chiedi messaggio commit
        print("📝 Inserisci messaggio commit (o 'annulla' per uscire):")
        message = input("> ").strip()
        
        if message.lower() == 'annulla':
            print("❌ Push annullato")
            return False
            
        if not message:
            message = "Update files"
            
        # Commit
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("✅ Commit effettuato")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore commit: {e}")
        return False

def get_github_token():
    """Ottieni token GitHub in modo sicuro usando SOPS+Age"""
    manager = UnifiedCredentialManager()
    
    # Prova a recuperare da SOPS/cache
    creds = manager.get_credential("github", "main", interactive=False)
    
    if creds and 'token' in creds:
        print("✅ Token GitHub trovato in SOPS")
        return creds['token']
    
    # Se non trovato, chiedi interattivo
    print("🔐 Per pushare su GitHub ho bisogno del tuo token.")
    print("   Puoi crearlo su: https://github.com/settings/tokens")
    print("   (richiede almeno i permessi: repo, write:packages)")
    print()
    
    # Richiedi credenziali interattive
    creds = manager.get_credential("github", "main", interactive=True)
    
    if creds and 'token' in creds:
        return creds['token']
    else:
        print("❌ Token GitHub richiesto per push")
        return None

def push_to_github(token):
    """Push con autenticazione sicura"""
    try:
        # Costruisci URL con token
        # Esempio: https://github.com/S3ph1r/nh-mini.git
        remote_url = "https://github.com/S3ph1r/nh-mini.git"
        auth_url = f"https://{token}@github.com/S3ph1r/nh-mini.git"
        
        # Configura remote se necessario
        try:
            subprocess.run(["git", "remote", "get-url", "origin"], 
                          check=True, capture_output=True)
        except:
            print("🔄 Configurazione remote origin...")
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        
        # Push
        print("🚀 Push in corso...")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                              capture_output=True, text=True, 
                              env={**os.environ, "GIT_ASKPASS": "echo", "GIT_USERNAME": token, "GIT_PASSWORD": token})
        
        if result.returncode == 0:
            print("✅ Push completato!")
            return True
        else:
            print(f"❌ Errore push: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante push: {e}")
        return False

def main():
    """Main flow - comportamento agent"""
    print("🔐 GitHub Push Script - Sicuro")
    print("=" * 40)
    
    # 1. Check repository
    if not check_git_repo():
        return False
    
    # 2. Mostra modifiche
    if not get_git_changes():
        return False
    
    # 3. Chiedi conferma
    print("\n🤔 Vuoi procedere con commit e push? (s/n): ", end="")
    if input().lower() != 's':
        print("❌ Push annullato")
        return False
    
    # 4. Commit
    if not commit_changes():
        return False
    
    # 5. Ottieni token (comportamento agent)
    token = get_github_token()
    if not token:
        # Questo è il comportamento chiave!
        print("\n📋 Per pushare su GitHub serve un token.")
        print("   1. Vai su https://github.com/settings/tokens")
        print("   2. Crea un token con permessi 'repo'")
        print("   3. Riesegui questo script quando hai il token")
        print("\n💡 L'agent si fermerà qui e aspetterà il tuo input")
        return False
    
    # 6. Push
    success = push_to_github(token)
    
    # 7. Pulisci token dalla cache (opzionale ma consigliato)
    if success:
        print("🧹 Pulizia token dalla cache...")
        clear_credential("github_token")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Interrotto")
        sys.exit(1)