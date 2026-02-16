#!/usr/bin/env python3
import os, sys, json, shutil, tempfile, subprocess
from pathlib import Path
from getpass import getpass

ROOT = Path(__file__).resolve().parents[1]
SECRETS_DIR = ROOT / "secrets"
SOPS_CONFIG = ROOT / ".sops.yaml"

def which(cmd):
    return shutil.which(cmd) is not None

def run(cmd, input_text=None):
    return subprocess.run(cmd, input=input_text, shell=True, text=True, capture_output=True)

def prompt(text, default=None, secret=False):
    if secret:
        val = getpass(f"{text}: ")
    else:
        suffix = f" [{default}]" if default else ""
        val = input(f"{text}{suffix}: ").strip()
        if not val and default is not None:
            val = default
    return val

def ensure_dirs():
    SECRETS_DIR.mkdir(exist_ok=True)

def configure_age():
    print("Configurazione age/sops")
    age_pubkey = None
    if which("age-keygen"):
        opt = prompt("Generare una nuova chiave age con age-keygen? (y/n)", "y")
        if opt.lower().startswith("y"):
            out = run("age-keygen")
            if out.returncode == 0:
                key = out.stdout
                home = Path.home() / ".nh" / "age"
                home.mkdir(parents=True, exist_ok=True)
                key_path = home / "age.key"
                key_path.write_text(key)
                os.chmod(key_path, 0o600)
                out_pub = run(f"age-keygen -y {key_path}")
                if out_pub.returncode == 0:
                    age_pubkey = out_pub.stdout.strip()
            else:
                print("age-keygen non eseguibile, fallback a chiave esistente")
    if not age_pubkey:
        age_pubkey = prompt("Incolla una age public key (age1...)", default=None)
    if not age_pubkey:
        print("Nessuna age public key fornita")
        return None
    cfg = {"creation_rules": [{"path_regex": r"secrets/.*\.enc\.yaml$", "encrypted_regex": "^(password|token_value|api_key)$", "age": [age_pubkey]}]}
    SOPS_CONFIG.write_text(json.dumps(cfg, indent=2))
    return age_pubkey

def build_secret_yaml(data):
    lines = []
    def w(k, v, indent=0):
        sp = "  " * indent
        if isinstance(v, dict):
            lines.append(f"{sp}{k}:")
            for kk, vv in v.items():
                w(kk, vv, indent+1)
        else:
            vv = "null" if v is None else str(v)
            if isinstance(v, str) and (":" in v or v.strip()=="" or v.lower()=="null"):
                vv = f"\"{v}\""
            lines.append(f"{sp}{k}: {vv}")
    for k, v in data.items():
        w(k, v, 0)
    return "\n".join(lines) + "\n"

def write_encrypted_secrets(doc):
    ensure_dirs()
    target = SECRETS_DIR / "nh.enc.yaml"
    if which("sops"):
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(doc)
            tmp_path = tmp.name
        cmd = f"sops --encrypt {tmp_path}"
        out = run(cmd)
        os.unlink(tmp_path)
        if out.returncode == 0:
            target.write_text(out.stdout)
            print(f"Creato {target}")
            return True
        else:
            print(out.stderr)
            return False
    else:
        print("sops non disponibile: impossibile creare file cifrato")
        return False

def main():
    print("NH Installer")
    proxmox_host = prompt("IP/Host Proxmox", default="10.0.0.2")
    proxmox_port = prompt("Porta Proxmox", default="8006")
    proxmox_user = prompt("Utente API Proxmox", default="root@pam")
    use_token = prompt("Usare API Token invece della password? (y/n)", default="y")
    token_name = None
    token_value = None
    password = None
    if use_token.lower().startswith("y"):
        token_name = prompt("Token name (user!token)", default=None)
        token_value = prompt("Token value", secret=True)
    else:
        password = prompt("Password", secret=True)
    agent_key = prompt("API key per agent (verrà cifrata)", secret=True)
    age_pub = configure_age()
    secrets = {
        "proxmox": {
            "host": proxmox_host,
            "port": int(proxmox_port) if proxmox_port.isdigit() else proxmox_port,
            "user": proxmox_user,
            "token_name": token_name,
            "token_value": token_value,
            "password": password
        },
        "agents": {
            "nh_core": {
                "api_key": agent_key
            }
        },
        "security": {
            "sops": "enabled" if which("sops") and age_pub else "disabled",
            "age_recipient": age_pub or ""
        }
    }
    yaml_doc = build_secret_yaml(secrets)
    ok = write_encrypted_secrets(yaml_doc)
    if not ok:
        print("Non è stato possibile creare secrets cifrati.")
        print("Installa sops e configura una age public key, poi riesegui.")
        sys.exit(1)
    print("Installazione completata")

if __name__ == "__main__":
    main()
