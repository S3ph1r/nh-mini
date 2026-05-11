#!/usr/bin/env python3
"""
NH-Mini Secrets Sync
Decifra i segreti da SOPS e genera/aggiorna i file .env nei progetti.
Uso:
    python3 scripts/nh-secrets-sync.py dias
    python3 scripts/nh-secrets-sync.py stratex
    python3 scripts/nh-secrets-sync.py lifelog2
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Aggiungi root al path per caricare il framework core
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core.secure_credential_manager import get_service_credential

def sync_env(project_name: str):
    print(f"🔐 Sincronizzazione segreti per: {project_name}...")
    
    # Mapping progetto -> (servizio SOPS, folder name)
    mapping = {
        "dias": ("dias", "dias"),
        "stratex": ("stratex", "stratex"),
        "lifelog2": ("lifelog", "Lifelog2"), 
    }
    
    if project_name not in mapping:
        print(f"❌ Progetto '{project_name}' non configurato nel mapping di sincronizzazione.")
        return

    service_info = mapping[project_name]
    service, folder = service_info[0], service_info[1]
    creds = get_service_credential(service, "main" if project_name != "lifelog2" else "db")
    
    if not creds:
        print(f"❌ Impossibile recuperare credenziali per {service} dal vault SOPS.")
        return

    # Percorso del .env (sempre in sviluppi/{folder}/.env)
    env_path = ROOT / "sviluppi" / folder / ".env"
    
    # Genera contenuto (formato KEY=VAL)
    lines = [f"# Generato automaticamente da NH-Mini Secrets Sync ({datetime.now().isoformat()})\n"]
    
    # Per stratex e dias usiamo le chiavi mappate
    if project_name == "stratex":
        lines.append(f"DATABASE_URL={creds.get('database_url')}\n")
        lines.append(f"REDIS_URL={creds.get('redis_url')}\n")
    elif project_name == "dias":
        lines.append(f"GOOGLE_API_KEY={creds.get('google_api_key')}\n")
        lines.append(f"GOOGLE_PROJECT_ID={creds.get('google_project_id')}\n")
    elif project_name == "lifelog2":
        # Lifelog2 uses LIFELOG2_ prefix for most, but some are shared
        lines.append(f"LIFELOG2_DATABASE_URL=postgresql+asyncpg://{creds.get('username')}:{creds.get('password')}@{creds.get('host')}:{creds.get('port')}/lifelog_roberto\n")
        lines.append(f"LIFELOG2_REDIS_URL=redis://192.168.1.120:6379\n")
        lines.append(f"LIFELOG2_MINIO_ENDPOINT=192.168.1.104:9000\n")
        lines.append(f"LIFELOG2_MINIO_ACCESS_KEY={creds.get('minio_access_key')}\n")
        lines.append(f"LIFELOG2_MINIO_SECRET_KEY={creds.get('minio_secret_key')}\n")
        lines.append(f"NH_PC139_HOST={creds.get('pc139_host')}\n")
        lines.append(f"NH_PC139_USER={creds.get('pc139_user')}\n")
        lines.append(f"NH_PC139_PASS={creds.get('pc139_pass')}\n")
        
        # Add Google API Key for LLM Enrichment
        gemini_creds = get_service_credential("google_gemini", "main")
        if gemini_creds:
            lines.append(f"GOOGLE_API_KEY={gemini_creds.get('google_api_key')}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)
        
    print(f"✅ File .env aggiornato: {env_path}")
    print("⚠️  Ricorda di NON committare mai questo file!")

if __name__ == "__main__":
    from datetime import datetime
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/nh-secrets-sync.py <project_name>")
        sys.exit(1)
        
    sync_env(sys.argv[1])
