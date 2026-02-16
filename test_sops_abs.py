#!/usr/bin/env python3
"""
Test semplice per SOPS+Age con percorso assoluto
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

# Test cifratura con percorso assoluto
env = os.environ.copy()
env['SOPS_AGE_KEY_FILE'] = os.path.expanduser('~/.age.key')

output_path = os.path.abspath('secrets/test.proxmox.enc.yaml')
print(f"Output path: {output_path}")

print("Test cifratura SOPS...")
try:
    cmd = [
        'sops', '--encrypt', '--age', 'age1808praju7clhp3q4e3fjp74nms6nmd3vvr4zleg54hw92ngdkq9sntzzjt',
        temp_path, '--output', output_path
    ]
    print(f"Comando: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
    
    print("✅ Cifratura riuscita!")
    
    # Verifica file creato
    if os.path.exists(output_path):
        print(f"✅ File creato: {output_path}")
        
        # Test decifrazione
        print("Test decifrazione SOPS...")
        result = subprocess.run([
            'sops', '--decrypt', output_path
        ], env=env, capture_output=True, text=True, check=True)
        
        print("✅ Decifrazione riuscita!")
        print(f"Dati: {result.stdout[:100]}...")
    else:
        print(f"❌ File non creato: {output_path}")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Errore: {e}")
    print(f"Stdout: {e.stdout}")
    print(f"Stderr: {e.stderr}")

# Pulizia
os.unlink(temp_path)