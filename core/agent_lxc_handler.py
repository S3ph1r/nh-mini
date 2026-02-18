#!/usr/bin/env python3
"""
NH LXC Deployment Handler - Interattivo con raccolta info da utente
L'agent controllerà cosa manca e lo chiederà all'utente prima di procedere
"""

import json
import subprocess
import re
import os
import sys
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import NHConfig

class NHLXCHandler:
    """Handle LXC deployment requests with interactive user input collection"""
    
    def __init__(self):
        self.config = NHConfig()
        self.inventory_file = "state/inventory.json"
        self.workflow_file = "knowledge/workflows/lxc-deployment.mdc"
        
        # Load deployment configuration (may be incomplete)
        self.deploy_config = None
        self.missing_info = {}
        self._check_configuration_status()
    
    def _check_configuration_status(self):
        """Check what configuration is missing"""
        self.missing_info = self.config.get_missing_info()
        
        if self.config.validate_config():
            try:
                self.deploy_config = self.config.get_deployment_config()
            except ValueError:
                self.deploy_config = None
        else:
            self.deploy_config = None
    
    def collect_missing_info(self) -> Dict[str, str]:
        """Interactively collect missing information from user"""
        
        if not self.missing_info:
            return {}
        
        print("\n🔍 NH Framework - Configuration Required")
        print("=" * 50)
        print("L'agent ha rilevato che mancano alcune informazioni necessarie.")
        print("Per favore, fornisci le seguenti informazioni:")
        print()
        
        collected_info = {}
        
        for key, description in self.missing_info.items():
            while True:
                value = input(f"{description}: ").strip()
                
                if value:  # Non-empty input
                    # Basic validation
                    if key == 'proxmox_host' and not self._is_valid_ip_or_hostname(value):
                        print("⚠️  Invalid IP or hostname format. Please try again.")
                        continue
                    elif key == 'network_gateway' and not self._is_valid_ip(value):
                        print("⚠️  Invalid IP format. Please try again.")
                        continue
                    elif key == 'proxmox_password' and len(value) < 4:
                        print("⚠️  Password too short. Please try again.")
                        continue
                    
                    collected_info[key] = value
                    break
                else:
                    print("⚠️  This field is required. Please provide a value.")
        
        print("\n✅ Configuration information collected!")
        return collected_info
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Basic IP address validation"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                num = int(part)
                if not 0 <= num <= 255:
                    return False
            return True
        except ValueError:
            return False
    
    def _is_valid_ip_or_hostname(self, value: str) -> bool:
        """Basic IP or hostname validation"""
        # Check if it's an IP
        if self._is_valid_ip(value):
            return True
        
        # Basic hostname validation
        if len(value) < 1 or len(value) > 253:
            return False
        
        # Allow alphanumeric, hyphens, and dots
        import re
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(hostname_pattern, value))
    
    def ensure_configuration(self) -> bool:
        """Ensure configuration is complete, collecting missing info if needed"""
        
        if self.config.validate_config():
            return True
        
        if self.missing_info:
            print("\n⚠️  NH Framework configuration incomplete")
            print("L'agent rileva che servono alcune informazioni prima di procedere.")
            
            collected_info = self.collect_missing_info()
            
            if collected_info:
                success = self.config.interactive_setup(collected_info)
                
                if success:
                    self._check_configuration_status()
                    print("\n✅ Configuration completed successfully!")
                    return True
                else:
                    print("\n❌ Configuration failed. Please check the provided information.")
                    return False
            else:
                print("\n❌ No configuration information provided.")
                return False
        
        return False
    
    def detect_deployment_request(self, user_input: str) -> Optional[Dict]:
        """Detect if user is requesting LXC deployment"""
        
        # First ensure configuration is complete
        if not self.ensure_configuration():
            return None
        
        patterns = {
            'deploy_lxc': r'deploy.*lxc|lxc.*deploy',
            'new_container': r'nuovo.*container|container.*nuovo',
            'ct_specific': r'ct\d{3}|container\s+\d{3}',
            'need_container': r'ho\s+bisogno.*container|serve.*container'
        }
        
        user_input_lower = user_input.lower()
        matches = {}
        
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                matches[pattern_name] = True
        
        if not matches:
            return None
        
        # Extract VMID if specified
        vmid_match = re.search(r'ct(\d{3})', user_input_lower)
        vmid = int(vmid_match.group(1)) if vmid_match else None
        
        # Extract VMID from numbers in input (e.g., "deploy lxc 195")
        if not vmid:
            vmid_match = re.search(r'\b(19[1-9]|\d{3})\b', user_input)
            if vmid_match:
                vmid = int(vmid_match.group(1))
        
        # Extract requirements
        requirements = self.extract_requirements(user_input)
        
        # Extract hostname if specified
        hostname_match = re.search(r'hostname[:\s]+(\w+)', user_input_lower)
        if hostname_match:
            requirements['name'] = hostname_match.group(1)
        elif vmid:
            requirements['name'] = f"ct{vmid}"
        
        # Extract IP address if specified
        ip_match = re.search(r'ip[:\s]+((?:\d{1,3}\.){3}\d{1,3})', user_input_lower)
        if ip_match:
            requirements['ip'] = ip_match.group(1)
        
        return {
            'type': 'lxc_deployment',
            'patterns_matched': list(matches.keys()),
            'vmid': vmid,
            'requirements': requirements,
            'confidence': len(matches) / len(patterns),
            'timestamp': datetime.now().isoformat()
        }
    
    def extract_requirements(self, user_input: str) -> Dict:
        """Extract resource requirements from user input"""
        requirements = {
            'memory': None,
            'cpu': None,
            'storage': None,
            'template': None,
            'name': None,
            'ip': None
        }
        
        # Memory requirements
        memory_match = re.search(r'(\d+)\s*gb?\s*ram', user_input, re.IGNORECASE)
        if memory_match:
            requirements['memory'] = int(memory_match.group(1)) * 1024
        else:
            memory_match = re.search(r'(\d+)\s*mb?\s*ram', user_input, re.IGNORECASE)
            if memory_match:
                requirements['memory'] = int(memory_match.group(1))
        
        # CPU requirements
        cpu_match = re.search(r'(\d+)\s*core', user_input, re.IGNORECASE)
        if cpu_match:
            requirements['cpu'] = int(cpu_match.group(1))
        
        # Storage requirements
        storage_match = re.search(r'(\d+)\s*gb?\s*(?:storage|disk)', user_input, re.IGNORECASE)
        if storage_match:
            requirements['storage'] = int(storage_match.group(1))
        
        # Template preference
        if 'debian' in user_input.lower():
            requirements['template'] = 'debian-12'
        elif 'ubuntu' in user_input.lower():
            requirements['template'] = 'ubuntu-24'
        elif 'alpine' in user_input.lower():
            requirements['template'] = 'alpine-3.19'
        
        # Name preference
        name_match = re.search(r'chiam(?:a|o)\s+(\w+)', user_input, re.IGNORECASE)
        if name_match:
            requirements['name'] = name_match.group(1)
        
        return requirements
    
    def check_inventory(self, vmid: Optional[int] = None) -> Dict:
        """Check current inventory and available resources"""
        inventory = {'containers': [], 'available_vmids': [], 'last_updated': None}
        
        try:
            if os.path.exists(self.inventory_file):
                with open(self.inventory_file, 'r') as f:
                    inventory = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        
        # Find available VMIDs
        used_vmids = {container['vmid'] for container in inventory.get('containers', [])}
        available_vmids = [vmid for vmid in range(191, 999) if vmid not in used_vmids]
        
        inventory['available_vmids'] = available_vmids[:10]  # Top 10 available
        
        return inventory
    
    def validate_deployment_request(self, request: Dict) -> Tuple[bool, str]:
        """Validate if deployment request can be fulfilled"""
        
        if not self.deploy_config:
            return False, "Configuration not complete. Run setup first."
        
        vmid = request.get('vmid')
        inventory = self.check_inventory(vmid)
        
        # Check if specific VMID is available
        if vmid:
            if vmid in [container['vmid'] for container in inventory['containers']]:
                return False, f"CT{vmid} already exists"
            if not 191 <= vmid <= 999:
                return False, f"VMID {vmid} must be between 191-999"
        
        # Check available VMIDs
        if not inventory['available_vmids']:
            return False, "No available VMIDs (191-999 range full)"
        
        # Validate requirements against configuration
        requirements = request.get('requirements', {})
        
        # Check memory limits
        if requirements.get('memory'):
            max_memory = 16384  # 16GB reasonable limit
            if requirements['memory'] > max_memory:
                return False, f"Memory request {requirements['memory']}MB exceeds limit {max_memory}MB"
        
        # Check CPU limits
        if requirements.get('cpu'):
            max_cpu = 8  # 8 cores reasonable limit
            if requirements['cpu'] > max_cpu:
                return False, f"CPU request {requirements['cpu']} exceeds limit {max_cpu}"
        
        # Check storage limits
        if requirements.get('storage'):
            max_storage = 100  # 100GB reasonable limit
            if requirements['storage'] > max_storage:
                return False, f"Storage request {requirements['storage']}GB exceeds limit {max_storage}GB"
        
        return True, "Request validated successfully"
    
    def generate_deployment_command(self, request: Dict) -> str:
        """Generate deployment command based on request"""
        
        if not self.deploy_config:
            return "Configuration not available"
        
        requirements = request.get('requirements', {})
        vmid = request.get('vmid')
        
        # Build command with configuration-based defaults
        cmd_parts = ['python3', 'scripts/deploy_lxc.py']
        
        if vmid:
            cmd_parts.extend(['--vmid', str(vmid)])
        
        # Use requirements or config defaults
        if requirements.get('memory'):
            cmd_parts.extend(['--memory', str(requirements['memory'])])
        
        if requirements.get('cpu'):
            cmd_parts.extend(['--cpu', str(requirements['cpu'])])
        
        if requirements.get('storage'):
            cmd_parts.extend(['--storage', str(requirements['storage'])])
        
        if requirements.get('template'):
            cmd_parts.extend(['--template', requirements['template']])
        
        if requirements.get('name'):
            cmd_parts.extend(['--name', requirements['name']])
        
        # Note: IP is handled by the deploy script based on VMID
        # The deploy script automatically assigns 192.168.1.{vmid}
        
        return ' '.join(cmd_parts)
    
    def get_deployment_summary(self, request: Dict) -> str:
        """Generate human-readable deployment summary"""
        
        if not self.deploy_config:
            return "Configuration not available for deployment summary"
        
        requirements = request.get('requirements', {})
        vmid = request.get('vmid') or self.get_next_available_vmid()
        
        summary = f"""
🎯 **NH LXC Deployment Summary**

**Container:** CT{vmid}
**Template:** {requirements.get('template', 'debian-12')}
**Resources:** {requirements.get('memory', self.deploy_config['default_memory'])}MB RAM, {requirements.get('cpu', self.deploy_config['default_cpu'])} CPU, {requirements.get('storage', self.deploy_config['default_storage'])}GB storage
**Network:** IP 192.168.1.{vmid}/24, Gateway {self.deploy_config['network_gateway']}
**Proxmox:** {self.deploy_config['proxmox_host']}
**SSH:** Bidirectional access configured
**Features:** Unprivileged, nesting enabled, keyctl enabled

**Command:** `{self.generate_deployment_command(request)}`
"""
        
        return summary.strip()
    
    def get_next_available_vmid(self) -> int:
        """Get next available VMID from inventory"""
        inventory = self.check_inventory()
        return inventory['available_vmids'][0] if inventory['available_vmids'] else 191
    
    def run_deployment(self, request: Dict) -> bool:
        """Execute deployment using configured script"""
        
        if not self.deploy_config:
            print("❌ Configuration not available")
            return False
        
        command = self.generate_deployment_command(request)
        print(f"🚀 Executing: {command}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment completed successfully")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment execution error: {e}")
            return False
    
    def get_workflow_instructions(self) -> str:
        """Get workflow instructions for agents"""
        
        try:
            if os.path.exists(self.workflow_file):
                with open(self.workflow_file, 'r') as f:
                    return f.read()
        except IOError:
            pass
        
        return "Workflow file not found. Use deployment command directly."

    def detect_undeploy_request(self, user_input: str) -> Dict:
        """Detect LXC undeploy request from user input"""
        user_input_lower = user_input.lower()
        
        # Pattern per undeploy
        undeploy_patterns = [
            r'\b(elimina|rimuovi|distruggi|cancella)\s+(?:lxc|container|ct)\s+(\d+)',
            r'\bundeploy\s+(?:lxc|container|ct)\s+(\d+)',
            r'\b(?:lxc|container|ct)\s+(\d+)\s+(?:elimina|rimuovi|distruggi|cancella)',
        ]
        
        for pattern in undeploy_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                # Estrai il gruppo con il numero VMID (l'ultimo gruppo)
                vmid_str = match.groups()[-1] if match.groups() else None
                if vmid_str:
                    vmid = int(vmid_str)
                    return {
                        'type': 'lxc_undeploy',
                        'vmid': vmid,
                        'confidence': 0.9,
                        'timestamp': datetime.now().isoformat()
                    }
        
        # Prova estrazione generica VMID se non trovato
        vmid_match = re.search(r'\b(19[5-9]|20[0-9]|\d{3,4})\b', user_input)
        if vmid_match:
            vmid = int(vmid_match.group(1))
            return {
                'type': 'lxc_undeploy',
                'vmid': vmid,
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def execute_undeploy_request(self, request: Dict) -> bool:
        """Execute undeploy using external script"""
        vmid = request['vmid']
        
        print(f"🎯 **NH LXC Undeploy Summary**")
        print(f"**Container:** CT{vmid}")
        print(f"**Confidence:** {request['confidence']}")
        print()
        
        # Richiedi conferma per operazione distruttiva
        response = input("Proceed with undeployment? (y/N): ")
        if response.lower() != 'y':
            print("❌ Undeployment cancelled")
            return False
        
        # Execute external undeploy script
        try:
            result = subprocess.run([
                'python3', 'scripts/undeploy_lxc.py', str(vmid)
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print(f"⚠️  Errors: {result.stderr}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Failed to execute undeploy script: {e}")
            return False

def main():
    """CLI interface for testing deployment/undeploy detection"""
    
    if len(sys.argv) < 2:
        print("Usage: python core/agent_lxc_handler.py '<user_input>'")
        print("       python core/agent_lxc_handler.py test")
        sys.exit(1)
    
    handler = NHLXCHandler()
    
    if sys.argv[1] == 'test':
        test_inputs = [
            "ho bisogno di un nuovo container",
            "deploy lxc ct201 con 4GB RAM",
            "crea container debian con 2 core",
            "serve un container ubuntu 24.04",
            "elimina lxc 198",
            "rimuovi container 199"
        ]
        
        for test_input in test_inputs:
            print(f"\n🧪 Testing: '{test_input}'")
            
            # Test deploy detection
            result = handler.detect_deployment_request(test_input)
            if result:
                print(f"✅ Deploy Detected: {result}")
                print(f"📋 Summary: {handler.get_deployment_summary(result)}")
            else:
                # Test undeploy detection
                undeploy_result = handler.detect_undeploy_request(test_input)
                if undeploy_result:
                    print(f"✅ Undeploy Detected: {undeploy_result}")
                else:
                    print("❌ Not detected")
        return
    
    # Process user input
    user_input = ' '.join(sys.argv[1:])
    
    # Check for undeploy first (operazione distruttiva)
    undeploy_result = handler.detect_undeploy_request(user_input)
    if undeploy_result:
        print(f"✅ Undeploy request detected: {undeploy_result}")
        handler.execute_undeploy_request(undeploy_result)
        return
    
    # Check for deploy
    result = handler.detect_deployment_request(user_input)
    
    if result:
        print(f"✅ Deployment request detected: {result}")
        
        # Validate request
        valid, message = handler.validate_deployment_request(result)
        if valid:
            print(f"✅ {message}")
            print(f"\n{handler.get_deployment_summary(result)}")
            
            # Ask for confirmation
            response = input("\nProceed with deployment? (y/N): ").strip().lower()
            if response == 'y':
                handler.run_deployment(result)
            else:
                print("Deployment cancelled")
        else:
            print(f"❌ {message}")
    else:
        print("❌ No deployment or undeploy request detected")

if __name__ == "__main__":
    main()