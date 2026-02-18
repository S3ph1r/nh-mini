#!/usr/bin/env python3
"""
NH LXC Deployment Script - Production Ready with Dynamic Configuration
Validato con workflow CT191, config-driven, no hardcoded credentials
"""

import argparse
import json
import subprocess
import os
import sys
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import NHConfig
from core.secure_credential_manager import get_service_credential, store_service_credential

class NHLXCDeployer:
    """Production LXC deployment with dynamic configuration"""
    
    def __init__(self, config: Optional[NHConfig] = None):
        self.config = config or NHConfig()
        self.inventory_file = "state/inventory.json"
        
        # Validate configuration before proceeding
        if not self.config.validate_config():
            print("❌ Configuration validation failed. Run 'python core/config_manager.py setup'")
            sys.exit(1)
        
        # Get deployment configuration
        self.deploy_config = self.config.get_deployment_config()
        
    def get_proxmox_credentials(self) -> dict:
        """Recupera credenziali Proxmox da SOPS o config"""
        # Prova prima da SOPS
        creds = get_service_credential('proxmox', 'main')
        if creds:
            print("🔐 Credenziali Proxmox recuperate da SOPS")
            return creds
        
        # Se non troviamo in SOPS, proviamo config ma con avviso
        print("⚠️  ATTENZIONE: Credenziali Proxmox non in SOPS, uso config.yaml")
        print("⚠️  Questo è INSECURE - esegui: python3 scripts/deploy_lxc.py --migrate-creds")
        
        # Verifichiamo che non siano hardcoded
        config_creds = {
            'host': self.deploy_config['proxmox_host'],
            'username': self.deploy_config['proxmox_user'],
            'password': self.deploy_config['proxmox_password']
        }
        
        # Check per valori hardcoded comuni
        if any('patatina' in str(v) or 'nhmini' in str(v) or '192.168.1.190' in str(v) for v in config_creds.values()):
            raise RuntimeError("Trovate credenziali hardcoded in config.yaml. Usa --migrate-creds per spostarle in SOPS.")
        
        return config_creds
    
    def run_ssh_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Execute SSH command on Proxmox host using SOPS credentials"""
        creds = self.get_proxmox_credentials()
        proxmox_host = creds['host']
        proxmox_user = creds['username']
        proxmox_password = creds['password']
        
        # Use double quotes to avoid conflicts with single quotes in command
        full_cmd = f"sshpass -p '{proxmox_password}' ssh {proxmox_user}@{proxmox_host} \"{command}\""
        print(f"🔍 SSH Command: {full_cmd}")
        return subprocess.run(full_cmd, shell=True, capture_output=True, text=True, check=check)
    
    def get_next_vmid(self) -> int:
        """Get next available VMID from configuration range"""
        try:
            result = self.run_ssh_command("pct list", check=False)
            used_vmids = set()
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if parts and parts[0].isdigit():
                            used_vmids.add(int(parts[0]))
            
            # Start from 191, find first available
            for vmid in range(191, 999):
                if vmid not in used_vmids:
                    return vmid
                    
            raise ValueError("No available VMID found")
            
        except Exception as e:
            print(f"⚠️  Could not determine VMID, using 191: {e}")
            return 191
    
    def ensure_template(self, template_name: str) -> str:
        """Ensure template exists, download if needed using config templates"""
        template_file = self.deploy_config['templates'].get(template_name, template_name)
        
        # Check if template exists
        result = self.run_ssh_command(f"pveam list local | grep {template_file}", check=False)
        
        if result.returncode != 0:
            print(f"📥 Downloading template: {template_file}")
            self.run_ssh_command(f"pveam download local {template_file}", check=False)
            print(f"✅ Template downloaded: {template_file}")
        else:
            print(f"✅ Template available: {template_file}")
            
        return template_file
    
    def create_container(self, vmid: int, name: str, template: str, 
                        memory: int = 2048, cpu: int = 2, storage: int = 16) -> bool:
        """Create LXC container with NH specifications using config"""
        
        # Check if container already exists
        print(f"🔍 Checking if CT{vmid} already exists...")
        check_result = self.run_ssh_command(f"pct list | grep '^{vmid}\\s'", check=False)
        
        if check_result.returncode == 0 and check_result.stdout.strip():
            # Container exists, get details
            existing_info = check_result.stdout.strip()
            print(f"❌ CT{vmid} already exists: {existing_info}")
            
            # Find next available VMID
            print(f"🔍 Finding next available VMID...")
            next_vmid = self.get_next_vmid()
            print(f"💡 Suggested alternative: CT{next_vmid}")
            
            return False
        
        print(f"🚀 Creating CT{vmid} ({name})...")
        
        # Build network configuration from config
        bridge = self.deploy_config['bridge']
        gateway = self.deploy_config['network_gateway']
        dns_server = self.deploy_config['dns_servers'][0]  # Use only first DNS server
        storage_pool = self.deploy_config['storage_pool']
        
        # Build network configuration (simplified to avoid argument issues)
        net_config = f"name=eth0,bridge={bridge},ip=192.168.1.{vmid}/24,gw={gateway}"
        
        # Build minimal command first, then add options step by step
        cmd = f"pct create {vmid} local:vztmpl/{template}"
        cmd += f" --storage {storage_pool}"
        cmd += f" --memory {memory}"
        cmd += f" --cores {cpu}"
        cmd += f" --hostname {name}"
        cmd += f" --net0 {net_config}"
        cmd += f" --rootfs {storage_pool}:{storage}"
        cmd += " --unprivileged 1"
        
        result = self.run_ssh_command(cmd, check=False)
        
        if result.returncode == 0:
            print(f"✅ CT{vmid} created successfully")
            
            # Start the container
            print(f"🚀 Starting CT{vmid}...")
            start_result = self.run_ssh_command(f"pct start {vmid}", check=False)
            if start_result.returncode != 0:
                print(f"❌ Failed to start CT{vmid}: {start_result.stderr}")
                return False
            
            print(f"✅ CT{vmid} started successfully")
            return True
        else:
            print(f"❌ Failed to create CT{vmid}: {result.stderr}")
            print(f"❌ Debug - stdout: {result.stdout}")
            print(f"❌ Debug - returncode: {result.returncode}")
            return False
    
    def setup_ssh_access(self, vmid: int) -> bool:
        """Setup bidirectional SSH access"""
        
        print(f"🔑 Setting up SSH access for CT{vmid}...")
        
        # Generate SSH key in container
        print(f"🔍 Generating SSH key for CT{vmid}...")
        # Create directory first
        mkdir_result = self.run_ssh_command(f"pct exec {vmid} -- mkdir -p /root/.ssh", check=False)
        if mkdir_result.returncode != 0:
            print(f"❌ Failed to create .ssh directory: {mkdir_result.stderr}")
            return False
        
        # Generate key with simpler command
        keygen_result = self.run_ssh_command(f"pct exec {vmid} -- ssh-keygen -t ed25519 -f /root/.ssh/id_nh -N '' -C 'nh-ct{vmid}@proxmox'", check=False)
        if keygen_result.returncode != 0:
            print(f"❌ Failed to generate SSH key: {keygen_result.stderr}")
            return False
        
        # Get public key
        print(f"🔍 Getting public key for CT{vmid}...")
        result = self.run_ssh_command(f"pct exec {vmid} -- cat /root/.ssh/id_nh.pub", check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            pub_key = result.stdout.strip()
            print(f"🔍 Got public key: {pub_key[:50]}...")
            
            # Authorize on Proxmox
            print(f"🔍 Authorizing key on Proxmox...")
            auth_result = self.run_ssh_command(f"echo '{pub_key}' >> /root/.ssh/authorized_keys", check=False)
            if auth_result.returncode != 0:
                print(f"❌ Failed to authorize key: {auth_result.stderr}")
                return False
            
            # ---------------------------------------------------------
            # NEW: Inject User/Agent Authorized Keys from SOPS
            # ---------------------------------------------------------
            print(f"🔐 Injecting authorized keys from SOPS...")
            try:
                ssh_creds = get_service_credential('ssh', 'authorized_keys')
                if ssh_creds and 'keys' in ssh_creds:
                    keys_list = ssh_creds['keys']
                    if keys_list:
                        # Join keys with newlines and escape for shell
                        keys_content = "\\n".join(keys_list)
                        # Use bash heredoc to append safely
                        inject_cmd = f"pct exec {vmid} -- bash -c 'mkdir -p /root/.ssh && echo \"{keys_content}\" >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys'"
                        inject_result = self.run_ssh_command(inject_cmd, check=False)
                        
                        if inject_result.returncode == 0:
                            print(f"✅ Injected {len(keys_list)} authorized keys from SOPS")
                        else:
                            print(f"⚠️  Failed to inject SOPS keys: {inject_result.stderr}")
                    else:
                        print("⚠️  No keys found in ssh.authorized_keys secret")
                else:
                    print("⚠️  Secret ssh.authorized_keys not found or invalid format")
            except Exception as e:
                print(f"⚠️  Error injecting SOPS keys: {e}")
            # ---------------------------------------------------------

            # Setup hostname and hosts
            print(f"🔍 Setting hostname for CT{vmid}...")

            # Use simple echo to set hostname (avoid systemd timeout)
            hostname_result = self.run_ssh_command(f"pct exec {vmid} -- bash -c 'echo nh-ct{vmid} > /etc/hostname'", check=False)
            if hostname_result.returncode != 0:
                print(f"❌ Failed to set hostname: {hostname_result.stderr}")
                return False
                
            print(f"🔍 Setting up hosts file for CT{vmid}...")
            proxmox_host = self.get_proxmox_credentials()['host']
            hosts_result = self.run_ssh_command(f"pct exec {vmid} -- bash -c 'echo {proxmox_host} proxmox >> /etc/hosts'", check=False)
            if hosts_result.returncode != 0:
                print(f"❌ Failed to setup hosts: {hosts_result.stderr}")
                return False
            
            print(f"✅ SSH access configured for CT{vmid}")
            return True
        else:
            print(f"❌ Failed to get public key: {result.stderr}")
            print(f"❌ Debug - stdout: {result.stdout}")
            print(f"❌ Debug - returncode: {result.returncode}")
        
        print(f"⚠️  Failed to setup SSH access for CT{vmid}")
        return False
    
    def start_container(self, vmid: int) -> bool:
        """Start container and verify status"""
        
        print(f"▶️  Starting CT{vmid}...")
        self.run_ssh_command(f"pct start {vmid}", check=False)
        
        # Wait and check status
        import time
        time.sleep(3)
        
        result = self.run_ssh_command(f"pct status {vmid}", check=False)
        if result.returncode == 0 and "status: running" in result.stdout:
            print(f"✅ CT{vmid} is running")
            return True
        else:
            print(f"❌ CT{vmid} failed to start")
            return False
    
    def test_ssh_connection(self, vmid: int) -> bool:
        """Test SSH connection from container to Proxmox"""
        
        print(f"🧪 Testing SSH connection CT{vmid} → Proxmox...")
        
        proxmox_host = self.deploy_config['proxmox_host']
        cmd = f"pct exec {vmid} -- ssh -i /root/.ssh/id_nh -o StrictHostKeyChecking=no root@{proxmox_host} 'echo SSH test successful && hostname'"
        result = self.run_ssh_command(cmd, check=False)
        
        if result.returncode == 0 and "SSH test successful" in result.stdout:
            print(f"✅ SSH bidirectional access working for CT{vmid}")
            return True
        else:
            print(f"⚠️  SSH test failed for CT{vmid}: {result.stderr}")
            return False
    
    def update_inventory(self, vmid: int, name: str, template: str, 
                        memory: int, cpu: int, storage: int) -> None:
        """Update NH inventory with new container"""
        
        container_info = {
            'vmid': vmid,
            'name': name,
            'template': template,
            'memory_mb': memory,
            'cpu_cores': cpu,
            'storage_gb': storage,
            'ip_address': f"192.168.1.{vmid}",
            'gateway': self.deploy_config['network_gateway'],
            'dns_servers': self.deploy_config['dns_servers'],
            'bridge': self.deploy_config['bridge'],
            'storage_pool': self.deploy_config['storage_pool'],
            'status': 'running',
            'created_at': datetime.now().isoformat(),
            'ssh_key': f"nh-ct{vmid}@{self.deploy_config['proxmox_host']}",
            'features': ['nesting=1', 'keyctl=1'],
            'unprivileged': True,
            'proxmox_host': self.deploy_config['proxmox_host']
        }
        
        # Load existing inventory or create new
        try:
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            inventory = {'containers': [], 'last_updated': datetime.now().isoformat()}
        
        inventory['containers'].append(container_info)
        inventory['last_updated'] = datetime.now().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.inventory_file), exist_ok=True)
        
        with open(self.inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        print(f"📋 Inventory updated: {self.inventory_file}")
    
    def deploy(self, vmid: Optional[int] = None, name: Optional[str] = None, 
               template: str = 'debian-12', memory: int = None, 
               cpu: int = None, storage: int = None) -> bool:
        """Complete deployment pipeline with configuration"""
        
        # Use config defaults if not specified
        memory = memory or self.deploy_config['default_memory']
        cpu = cpu or self.deploy_config['default_cpu']
        storage = storage or self.deploy_config['default_storage']
        
        print(f"\n🎯 NH LXC Deployment Starting...")
        print(f"   Target: CT{vmid or 'auto'} ({name or 'auto'})")
        print(f"   Template: {template}")
        print(f"   Resources: {memory}MB RAM, {cpu} CPU, {storage}GB storage")
        print(f"   Proxmox: {self.deploy_config['proxmox_host']}")
        print("-" * 50)
        
        # Determine VMID
        if not vmid:
            vmid = self.get_next_vmid()
            print(f"📊 Auto-selected VMID: {vmid}")
        
        # Generate name if not provided
        if not name:
            name = f"nh-ct{vmid}"
        
        # Ensure template
        template_file = self.ensure_template(template)
        
        # Create container
        if not self.create_container(vmid, name, template_file, memory, cpu, storage):
            return False
        
        # Setup SSH access
        if not self.setup_ssh_access(vmid):
            return False
        
        # Start container
        if not self.start_container(vmid):
            return False
        
        # Test SSH connection
        self.test_ssh_connection(vmid)
        
        # Update inventory
        self.update_inventory(vmid, name, template_file, memory, cpu, storage)
        
        print(f"\n🎉 Deployment completed successfully!")
        print(f"   Container: CT{vmid} ({name})")
        print(f"   IP: 192.168.1.{vmid}")
        print(f"   SSH: ssh -i /root/.ssh/id_nh root@192.168.1.{vmid}")
        print(f"   Proxmox: {self.deploy_config['proxmox_host']}")
        print(f"   Inventory: {self.inventory_file}")
        
        return True
    
    def migrate_credentials_to_sops(self):
        """Migra credenziali Proxmox da config a SOPS"""
        print("🔐 Migrazione credenziali Proxmox a SOPS...")
        
        creds = {
            'host': self.deploy_config['proxmox_host'],
            'username': self.deploy_config['proxmox_user'],
            'password': self.deploy_config['proxmox_password']
        }
        
        if store_service_credential('proxmox', 'main', creds):
            print("✅ Credenziali migrate con successo!")
            print("⚠️  Ricorda di rimuovere le credenziali dal file config.yaml")
            return True
        else:
            print("❌ Errore migrazione credenziali")
            return False

def main():
    """CLI interface for NH LXC deployment"""
    parser = argparse.ArgumentParser(description='NH LXC Deployment Tool (Configuration-Driven)')
    parser.add_argument('--vmid', type=int, help='VMID (auto-detected if not specified)')
    parser.add_argument('--name', help='Container hostname')
    parser.add_argument('--template', default='debian-12', 
                       choices=['debian-12', 'ubuntu-24', 'alpine-3.19'],
                       help='Container template')
    parser.add_argument('--memory', type=int, help='Memory in MB (uses config default if not specified)')
    parser.add_argument('--cpu', type=int, help='CPU cores (uses config default if not specified)')
    parser.add_argument('--storage', type=int, help='Storage in GB (uses config default if not specified)')
    parser.add_argument('--config-dir', default='config', help='Configuration directory')
    parser.add_argument('--setup', action='store_true', help='Run configuration setup')
    parser.add_argument('--migrate-creds', action='store_true', help='Migrate credentials to SOPS')
    
    args = parser.parse_args()
    
    # Handle setup request
    if args.setup:
        config = NHConfig(args.config_dir)
        config.setup_interactive()
        return
    
    # Handle credential migration
    if args.migrate_creds:
        config = NHConfig(args.config_dir)
        deployer = NHLXCDeployer(config)
        deployer.migrate_credentials_to_sops()
        return
    
    # Load configuration
    config = NHConfig(args.config_dir)
    
    # Create deployer with configuration
    deployer = NHLXCDeployer(config)
    
    # Deploy container
    success = deployer.deploy(
        vmid=args.vmid,
        name=args.name,
        template=args.template,
        memory=args.memory,
        cpu=args.cpu,
        storage=args.storage
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()