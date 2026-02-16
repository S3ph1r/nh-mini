#!/usr/bin/env python3
"""
NH Project Switch - Interfaccia naturale per cambio progetto
"""

import sys
import os
from pathlib import Path

# Aggiungi core al path
core_path = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_path))

from workspace_manager import get_workspace_manager
from intent_parser import IntentParser

def print_status():
    """Mostra stato workspace"""
    wm = get_workspace_manager()
    status = wm.status()
    
    print("🏗️  NH Workspace Status")
    print("=" * 40)
    
    if status["active_project"]:
        print(f"📍 Progetto attivo: {status['active_project']}")
        print(f"📂 Path: {status['current_link_target']}")
    else:
        print("❌ Nessun progetto attivo")
    
    print(f"📋 Progetti disponibili: {len(status['projects'])}")
    for proj in status["projects"]:
        print(f"   • {proj}")

def switch_project(project_name: str):
    """Switch a progetto con conferma"""
    wm = get_workspace_manager()
    
    # Verifica progetto esiste
    if project_name not in [p.name for p in wm.list_projects()]:
        print(f"❌ Progetto '{project_name}' non trovato")
        
        # Suggerisci simili
        projects = [p.name for p in wm.list_projects()]
        simili = [p for p in projects if project_name.lower() in p.lower()]
        if simili:
            print(f"💡 Forse intendevi: {', '.join(simili)}")
        return False
    
    # Chiedi conferma se c'è progetto attivo
    active = wm.get_active_project()
    if active:
        print(f"🔄 Cambiando da '{active.name}' a '{project_name}'")
        print("Procedo? (s/n): ", end="", flush=True)
        
        response = input().strip().lower()
        if response not in ['s', 'si', 'yes', 'y']:
            print("❌ Switch annullato")
            return False
    
    # Esegui switch
    return wm.switch_project(project_name)

def handle_natural_language(text: str):
    """Gestisci linguaggio naturale"""
    parser = IntentParser()
    wm = get_workspace_manager()
    
    intent = parser.parse_intent(text)
    
    if not intent:
        print("❓ Non ho capito l'intento")
        print("💡 Prova: 'passa a progetto4', 'lista progetti', 'dove sto lavorando'")
        return False
    
    print(f"🧠 Intent rilevato: {intent.intent}")
    
    if intent.intent == "switch_project":
        return switch_project(intent.project)
    
    elif intent.intent == "list_projects":
        projects = wm.list_projects()
        print("📋 Progetti disponibili:")
        for proj in projects:
            print(f"   • {proj.name} - {proj.description}")
        return True
    
    elif intent.intent == "workspace_status":
        print_status()
        return True
    
    return False

def main():
    """Main CLI"""
    if len(sys.argv) < 2:
        print("🏗️  NH Project Switch")
        print("Uso:")
        print("  nh-switch <nome_progetto>     # Switch diretto")
        print("  nh-switch 'passa a progetto4' # Linguaggio naturale")
        print("  nh-switch --status            # Stato workspace")
        print("  nh-switch --list              # Lista progetti")
        print()
        print_status()
        return
    
    arg = sys.argv[1]
    
    if arg == "--status":
        print_status()
        return
    
    if arg == "--list":
        wm = get_workspace_manager()
        projects = wm.list_projects()
        print("📋 Progetti disponibili:")
        for proj in projects:
            print(f"   • {proj.name} - {proj.description}")
        return
    
    # Prova comando diretto prima
    wm = get_workspace_manager()
    if any(p.name == arg for p in wm.list_projects()):
        switch_project(arg)
    else:
        # Prova linguaggio naturale
        handle_natural_language(arg)

if __name__ == "__main__":
    main()