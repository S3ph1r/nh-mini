#!/usr/bin/env python3
"""
NH Configuration Manager - Gestione credenziali e configurazioni
Evita hardcoding di IP, password e altri parametri sensibili
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class NHConfig:
    """NH Framework Configuration Manager"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "nh_config.json"
        self.secrets_file = self.config_dir / "nh_secrets.json"
        
        # Default configuration
        self.defaults = {
            "proxmox": {
                "host": "192.168.1.2",
                "user": "root",
                "port": 22,
                "timeout": 30
            },
            "network": {
                "gateway": "192.168.1.1",
                "subnet": "192.168.1.0/24",
                "dns_primary": "1.1.1.1",
                "dns_secondary": "8.8.8.8"
            },
            "lxc": {
                "default_memory": 2048,
                "default_cpu": 2,
                "default_storage": 16,
                "bridge": "vmbr0",
                "storage_pool": "local-lvm"
            },
            "templates": {
                "debian-12": "debian-12-standard_12.12-1_amd64.tar.zst",
                "ubuntu-24": "ubuntu-24.04-standard_24.04-1_amd64.tar.zst",
                "alpine-3.19": "alpine-3.19-default_20240301_amd64.tar.zst"
            }
        }
        
        self.config = self.load_config()
        self.secrets = self.load_secrets()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create default config
        self.save_config(self.defaults)
        return self.defaults.copy()
    
    def load_secrets(self) -> Dict[str, Any]:
        """Load secrets from file or return empty dict"""
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def save_secrets(self, secrets: Dict[str, Any]) -> None:
        """Save secrets to file with restricted permissions"""
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.secrets_file, 0o600)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'proxmox.host')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret value with environment variable fallback"""
        # First check environment variables
        env_key = key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value
        
        # Then check secrets file
        return self.secrets.get(key, default)
    
    def get_proxmox_password(self) -> Optional[str]:
        """Get Proxmox password from SOPS with fallback chain"""
        # Priority: SOPS → env var → None
        try:
            from core.secure_credential_manager import get_service_credential
            creds = get_service_credential('proxmox', 'main')
            if creds and 'password' in creds:
                return creds['password']
        except Exception as e:
            print(f"⚠️  Errore recupero credenziali SOPS: {e}")
        
        # Fallback su env var
        return os.environ.get('PROXMOX_PASS')
    
    def update_config(self, key_path: str, value: Any) -> None:
        """Update configuration value"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config(self.config)
    
    def set_secret(self, key: str, value: Any) -> None:
        """Set secret value"""
        self.secrets[key] = value
        self.save_secrets(self.secrets)
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        required_keys = [
            'proxmox.host',
            'network.gateway'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                return False
        
        # Check if secrets are configured
        if not self.get_proxmox_password():
            return False
        
        return True
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get complete deployment configuration"""
        password = self.get_proxmox_password()
        if not password:
            raise ValueError("Proxmox password not configured")
            
        return {
            'proxmox_host': self.get('proxmox.host'),
            'proxmox_user': self.get('proxmox.user'),
            'proxmox_password': password,
            'network_gateway': self.get('network.gateway'),
            'dns_servers': [self.get('network.dns_primary'), self.get('network.dns_secondary')],
            'bridge': self.get('lxc.bridge'),
            'storage_pool': self.get('lxc.storage_pool'),
            'default_memory': self.get('lxc.default_memory'),
            'default_cpu': self.get('lxc.default_cpu'),
            'default_storage': self.get('lxc.default_storage'),
            'templates': self.get('templates')
        }
    
    def get_missing_info(self) -> Dict[str, str]:
        """Get information that needs to be provided by user"""
        missing = {}
        
        # Check required configuration
        if not self.get('proxmox.host'):
            missing['proxmox_host'] = "Proxmox host IP/hostname (e.g., 192.168.1.2)"
        
        if not self.get('network.gateway'):
            missing['network_gateway'] = "Network gateway IP (e.g., 192.168.1.1)"
        
        # Check secrets
        if not self.get_proxmox_password():
            missing['proxmox_password'] = "Proxmox root password"
        
        return missing
    
    def interactive_setup(self, provided_info: Dict[str, str] = None) -> bool:
        """Interactive setup with user-provided information"""
        
        if provided_info is None:
            provided_info = {}
        
        # Update configuration with provided info
        if 'proxmox_host' in provided_info:
            self.update_config('proxmox.host', provided_info['proxmox_host'])
        
        if 'network_gateway' in provided_info:
            self.update_config('network.gateway', provided_info['network_gateway'])
        
        # Update secrets
        if 'proxmox_password' in provided_info:
            self.set_secret('proxmox_password', provided_info['proxmox_password'])
        
        # Additional optional configuration
        if 'proxmox_user' in provided_info:
            self.update_config('proxmox.user', provided_info['proxmox_user'])
        
        if 'dns_primary' in provided_info:
            self.update_config('network.dns_primary', provided_info['dns_primary'])
        
        if 'dns_secondary' in provided_info:
            self.update_config('network.dns_secondary', provided_info['dns_secondary'])
        
        if 'bridge' in provided_info:
            self.update_config('lxc.bridge', provided_info['bridge'])
        
        if 'storage_pool' in provided_info:
            self.update_config('lxc.storage_pool', provided_info['storage_pool'])
        
        return self.validate_config()

def main():
    """CLI interface for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NH Framework Configuration Manager')
    parser.add_argument('action', choices=['setup', 'show', 'validate', 'missing'], 
                       help='Configuration action')
    parser.add_argument('--config-dir', default='config', 
                       help='Configuration directory')
    
    args = parser.parse_args()
    
    config = NHConfig(args.config_dir)
    
    if args.action == 'setup':
        print("🔧 Manual setup not supported. Use interactive agent mode.")
        print("💡 L'agent controllerà le info mancanti e le richiederà all'utente.")
        
    elif args.action == 'show':
        print("📋 Current Configuration:")
        print(json.dumps(config.config, indent=2))
        print(f"\n🔐 Secrets configured: {bool(config.secrets)}")
        
    elif args.action == 'validate':
        if config.validate_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has issues")
            missing = config.get_missing_info()
            if missing:
                print("\n🔍 Missing information:")
                for key, description in missing.items():
                    print(f"   {key}: {description}")
            sys.exit(1)
            
    elif args.action == 'missing':
        missing = config.get_missing_info()
        if missing:
            print("🔍 Missing configuration:")
            for key, description in missing.items():
                print(f"   {key}: {description}")
        else:
            print("✅ All configuration complete")

if __name__ == "__main__":
    main()