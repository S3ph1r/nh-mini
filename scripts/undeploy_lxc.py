#!/usr/bin/env python3
"""
LXC Undeploy Script

Script esterno per undeploy container LXC con cleanup completo.
Richiede conferma utente per operazioni distruttive.
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Add NH-Mini to path
sys.path.append('/home/Projects/NH-Mini')

from core.secure_credential_manager import get_service_credential

def get_proxmox_credentials() -> dict:
    """Recupera credenziali Proxmox da SOPS"""
    creds = get_service_credential('proxmox', 'main')
    if creds:
        print("🔐 Credenziali Proxmox recuperate da SOPS")
        return creds
    
    # Errore se non troviamo credenziali
    raise RuntimeError("Credenziali Proxmox non trovate in SOPS. Usa: python3 save_proxmox_creds.py")

def run_ssh_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Execute SSH command on Proxmox host using SOPS credentials"""
    creds = get_proxmox_credentials()
    proxmox_host = creds['host']
    proxmox_user = creds['username']
    proxmox_password = creds['password']
    
    full_cmd = f"sshpass -p '{proxmox_password}' ssh {proxmox_user}@{proxmox_host} \"{command}\""
    print(f"🔍 SSH Command: {full_cmd}")
    return subprocess.run(full_cmd, shell=True, capture_output=True, text=True, check=check)

def check_container_exists(vmid: int) -> bool:
    """Check if container exists"""
    print(f"🔍 Checking if CT{vmid} exists...")
    
    result = run_ssh_command(f"pct list | grep '^{vmid}\\s'", check=False)
    exists = result.returncode == 0 and result.stdout.strip()
    
    if exists:
        print(f"✅ CT{vmid} found: {result.stdout.strip()}")
    else:
        print(f"❌ CT{vmid} not found")
    
    return exists

def remove_ssh_key(vmid: int) -> bool:
    """Remove SSH key from Proxmox authorized_keys"""
    print(f"🔑 Removing SSH key for CT{vmid}...")
    
    # Remove key with specific comment
    result = run_ssh_command(f"sed -i '/nh-ct{vmid}@proxmox/d' /root/.ssh/authorized_keys", check=False)
    
    if result.returncode == 0:
        print(f"✅ SSH key removed for CT{vmid}")
        return True
    else:
        print(f"⚠️  Failed to remove SSH key: {result.stderr}")
        return False

def stop_container(vmid: int) -> bool:
    """Stop LXC container"""
    print(f"🛑 Stopping CT{vmid}...")
    
    result = run_ssh_command(f"pct stop {vmid}", check=False)
    
    if result.returncode == 0:
        print(f"✅ CT{vmid} stopped successfully")
        return True
    else:
        # Check if already stopped
        if "not running" in result.stderr.lower():
            print(f"ℹ️  CT{vmid} already stopped")
            return True
        else:
            print(f"❌ Failed to stop CT{vmid}: {result.stderr}")
            return False

def destroy_container(vmid: int) -> bool:
    """Destroy LXC container"""
    print(f"💥 Destroying CT{vmid}...")
    
    result = run_ssh_command(f"pct destroy {vmid}", check=False)
    
    if result.returncode == 0:
        print(f"✅ CT{vmid} destroyed successfully")
        return True
    else:
        print(f"❌ Failed to destroy CT{vmid}: {result.stderr}")
        return False

def update_inventory(vmid: int) -> bool:
    """Remove container from inventory.json"""
    print(f"📋 Updating inventory...")
    
    inventory_path = Path("state/inventory.json")
    
    try:
        if not inventory_path.exists():
            print(f"⚠️  Inventory file not found")
            return True
        
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)
        
        # Find and remove container
        containers = inventory.get('containers', [])
        original_count = len(containers)
        
        inventory['containers'] = [c for c in containers if c.get('vmid') != vmid]
        
        if len(inventory['containers']) < original_count:
            print(f"✅ Removed CT{vmid} from inventory")
        else:
            print(f"ℹ️  CT{vmid} not found in inventory")
        
        # Save updated inventory
        with open(inventory_path, 'w') as f:
            json.dump(inventory, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update inventory: {e}")
        return False

def undeploy_container(vmid: int) -> bool:
    """Complete undeploy workflow"""
    print(f"🎯 Starting undeploy of CT{vmid}")
    print("=" * 50)
    
    success = True
    
    # Step 1: Check if container exists
    if not check_container_exists(vmid):
        print(f"❌ CT{vmid} does not exist, aborting")
        return False
    
    # Step 2: Remove SSH key
    if not remove_ssh_key(vmid):
        success = False
    
    # Step 3: Stop container
    if not stop_container(vmid):
        success = False
    
    # Step 4: Destroy container
    if not destroy_container(vmid):
        success = False
    
    # Step 5: Update inventory
    if not update_inventory(vmid):
        success = False
    
    print("=" * 50)
    if success:
        print(f"🎉 CT{vmid} undeployed successfully!")
    else:
        print(f"⚠️  CT{vmid} undeploy completed with some issues")
    
    return success

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/undeploy_lxc.py <vmid>")
        print("Example: python3 scripts/undeploy_lxc.py 198")
        sys.exit(1)
    
    try:
        vmid = int(sys.argv[1])
    except ValueError:
        print("❌ VMID must be a number")
        sys.exit(1)
    
    print(f"\n🎯 **NH LXC Undeploy Summary**")
    print(f"**Container:** CT{vmid}")
    print()
    
    response = input("Proceed with undeployment? (y/N): ")
    if response.lower() != 'y':
        print("❌ Undeployment cancelled")
        sys.exit(0)
    
    # Execute undeployment
    success = undeploy_container(vmid)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()