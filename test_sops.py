#!/usr/bin/env python3
"""
Test semplice per SOPS+Age
"""

import os
import subprocess
import tempfile
import yaml

# Test dati
test_data = {
    'service': 'test',
    'credential_name': 'proxmox',
    'created_at': '2026-02-16T20:00:00Z',
    'data': {
        'username': 'test_user',
        'password': 'test_password_123'
    }
}

# Crea file temporaneo
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    yaml.dump(test_data, f, default_flow_style=False)
    temp_path = f.name

print(f"File temporaneo: {temp_path}")

# Test cifratura
env = os.environ.copy()
env['SOPS_AGE_KEY_FILE'] = os.path.expanduser('~/.age.key')

print("Test cifratura SOPS...")
try:
    result = subprocess.run([
        'sops', '--encrypt', '--age', 'age1808praju7clhp3q4e3fjp74nms6nmd3vvr4zleg54hw92ngdkq9sntzzjt',
        temp_path, '--output', 'secrets/test.proxmox.enc.yaml'
    ], env=env, capture_output=True, text=True, check=True)
    
    print("✅ Cifratura riuscita!")
    
    # Test decifrazione
    print("Test decifrazione SOPS...")
    result = subprocess.run([
        'sops', '--decrypt', 'secrets/test.proxmox.enc.yaml'
    ], env=env, capture_output=True, text=True, check=True)
    
    print("✅ Decifrazione riuscita!")
    print(f"Dati: {result.stdout[:100]}...")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Errore: {e}")
    print(f"Stdout: {e.stdout}")
    print(f"Stderr: {e.stderr}")

# Pulizia
os.unlink(temp_path)