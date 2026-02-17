#!/usr/bin/env python3
"""
NH-Mini: Setup locale SOPS + Age per gestione credenziali
Zero configurazione su Proxmox, tutto locale in LXC
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

class SOPSLocalSetup:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.nh_mini_dir = self.base_dir / ".nh-mini"
        self.age_key_file = self.nh_mini_dir / "age.key"
        self.sops_config = self.base_dir / ".sops.yaml"
        self.env_file = self.nh_mini_dir / "env"
        
    def setup_directories(self) -> None:
        """Crea directory necessarie"""
        self.nh_mini_dir.mkdir(mode=0o700, exist_ok=True)
        (self.base_dir / "credentials").mkdir(mode=0o700, exist_ok=True)
        
    def generate_age_key(self, password: str) -> str:
        """Genera chiave age con password"""
        print("🔑 Generazione chiave age...")
        
        # Genera chiave con password
        cmd = ["age-keygen", "-o", str(self.age_key_file)]
        result = subprocess.run(
            cmd,
            input=f"{password}\n{password}\n",
            text=True,
            capture_output=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Errore generazione age key: {result.stderr}")
        
        # Imposta permessi sicuri
        os.chmod(self.age_key_file, 0o600)
        
        # Ottieni chiave pubblica
        pub_key_cmd = ["age-keygen", "-y", str(self.age_key_file)]
        pub_result = subprocess.run(pub_key_cmd, capture_output=True, text=True)
        
        if pub_result.returncode != 0:
            raise RuntimeError(f"Errore ottenimento chiave pubblica: {pub_result.stderr}")
        
        pub_key = pub_result.stdout.strip()
        print(f"✅ Chiave pubblica: {pub_key[:20]}...")
        return pub_key
    
    def create_sops_config(self, age_public_key: str) -> None:
        """Crea configurazione SOPS"""
        print("⚙️ Configurazione SOPS...")
        
        config = {
            "creation_rules": [
                {
                    "path_regex": "credentials/.*",
                    "age": age_public_key
                }
            ]
        }
        
        with open(self.sops_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Configurazione SOPS salvata in {self.sops_config}")
    
    def create_env_file(self) -> None:
        """Crea file ambiente per SOPS"""
        env_content = f"""# NH-Mini SOPS Environment
export NH_MINI_AGE_KEY_FILE="{self.age_key_file}"
export SOPS_AGE_KEY_FILE="{self.age_key_file}"
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        os.chmod(self.env_file, 0o600)
        print(f"✅ File ambiente creato: {self.env_file}")
    
    def create_sample_credentials(self) -> None:
        """Crea file credenziali di esempio"""
        sample_creds = {
            "github": {
                "token": "ghp_your_github_token_here",
                "username": "your_username"
            },
            "proxmox": {
                "host": "192.168.1.2",
                "user": "root",
                "password": "your_proxmox_password"
            },
            "example_service": {
                "api_key": "your_api_key_here",
                "endpoint": "https://api.example.com"
            }
        }
        
        sample_file = self.base_dir / "credentials" / "sample.yaml"
        
        # Salva in chiaro per reference
        with open(sample_file, 'w') as f:
            yaml.dump(sample_creds, f, default_flow_style=False)
        
        print(f"✅ File credenziali di esempio creato: {sample_file}")
        print("   Puoi usare 'sops credentials/secrets.yaml' per creare file encryptato")
    
    def verify_setup(self) -> bool:
        """Verifica che setup sia completo"""
        checks = [
            (self.nh_mini_dir.exists(), f"Directory {self.nh_mini_dir}"),
            (self.age_key_file.exists(), f"Chiave age {self.age_key_file}"),
            (self.sops_config.exists(), f"Config SOPS {self.sops_config}"),
            (self.env_file.exists(), f"File ambiente {self.env_file}"),
        ]
        
        all_good = True
        for check, description in checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_good = False
        
        return all_good
    
    def create_helper_script(self) -> None:
        """Crea script helper per gestione credenziali"""
        helper_content = f"""#!/usr/bin/env bash
# NH-Mini: Helper per gestione credenziali SOPS

# Carica ambiente
source {self.env_file}

# Funzioni utili
nh-credentials() {{
    if [[ $# -eq 0 ]]; then
        echo "Usage: nh-credentials <command> [args]"
        echo "Commands:"
        echo "  edit <file>   - Edit encrypted credential file"
        echo "  view <file>   - View encrypted credential file"
        echo "  list          - List credential files"
        echo "  sample        - Show sample credentials"
        return 1
    fi
    
    local cmd=$1
    shift
    
    case $cmd in
        edit)
            sops credentials/${{1:-secrets.yaml}}
            ;;
        view)
            sops --decrypt credentials/${{1:-secrets.yaml}}
            ;;
        list)
            ls -la credentials/
            ;;
        sample)
            cat credentials/sample.yaml
            ;;
        *)
            echo "Unknown command: $cmd"
            ;;
    esac
}}

# Alias comodi
alias nh-cred='nh-credentials'
alias nh-edit='sops credentials/secrets.yaml'
alias nh-view='sops --decrypt credentials/secrets.yaml'

echo "✅ NH-Mini credential helpers loaded!"
echo "Use: nh-credentials <command> or nh-edit / nh-view"
"""
        
        helper_script = self.base_dir / "nh-creds-helper.sh"
        with open(helper_script, 'w') as f:
            f.write(helper_content)
        
        os.chmod(helper_script, 0o755)
        print(f"✅ Script helper creato: {helper_script}")
        print("   Caricalo con: source nh-creds-helper.sh")
    
    def run_setup(self, password: str) -> bool:
        """Esecuzione completa setup"""
        try:
            print("🚀 Avvio setup SOPS locale...")
            
            self.setup_directories()
            age_pub_key = self.generate_age_key(password)
            self.create_sops_config(age_pub_key)
            self.create_env_file()
            self.create_sample_credentials()
            self.create_helper_script()
            
            print("\n📋 Verifica setup:")
            if self.verify_setup():
                print("\n🎉 Setup SOPS completato con successo!")
                print(f"\nProssimi passi:")
                print(f"1. Carica l'ambiente: source {self.env_file}")
                print(f"2. Crea credenziali: sops credentials/secrets.yaml")
                print(f"3. Usa l'helper: source nh-creds-helper.sh")
                return True
            else:
                print("\n❌ Setup incompleto - verifica errori sopra")
                return False
                
        except Exception as e:
            print(f"\n❌ Errore durante setup: {e}")
            return False

def main():
    """Main function con CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup SOPS locale per NH-Mini")
    parser.add_argument("--password", help="Password per chiave age")
    parser.add_argument("--base-dir", help="Directory base (default: current)")
    parser.add_argument("--verify", action="store_true", help="Verifica setup esistente")
    
    args = parser.parse_args()
    
    setup = SOPSLocalSetup(args.base_dir)
    
    if args.verify:
        print("🔍 Verifica setup SOPS esistente...")
        setup.verify_setup()
        return
    
    # Richiedi password se non fornita
    if not args.password:
        import getpass
        password = getpass.getpass("🔑 Inserisci password per credenziali NH-Mini: ")
        confirm = getpass.getpass("🔑 Conferma password: ")
        
        if password != confirm:
            print("❌ Le password non coincidono!")
            sys.exit(1)
        
        if len(password) < 8:
            print("❌ Password troppo corta (minimo 8 caratteri)")
            sys.exit(1)
    else:
        password = args.password
    
    # Esegui setup
    success = setup.run_setup(password)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()