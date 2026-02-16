#!/usr/bin/env python3
"""
NH Agent Workspace Integration - Gestione automatica workspace in conversazioni
"""

import os
import sys
import json
from pathlib import Path

# Aggiungi core al path
core_path = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_path))

from workspace_manager import get_workspace_manager
from intent_parser import IntentParser

class AgentWorkspaceHandler:
    def __init__(self):
        self.wm = get_workspace_manager()
        self.parser = IntentParser()
    
    def check_user_intent(self, user_message: str) -> dict:
        """Controlla se l'utente vuole cambiare progetto"""
        intent = self.parser.parse_intent(user_message)
        
        if not intent or intent.intent != "switch_project":
            return {"action": "none"}
        
        project_name = intent.project
        
        # Verifica progetto esiste
        available_projects = [p.name for p in self.wm.list_projects()]
        
        if project_name not in available_projects:
            return {
                "action": "project_not_found",
                "project": project_name,
                "available": available_projects,
                "suggestions": [p for p in available_projects if project_name.lower() in p.lower()]
            }
        
        # Ottieni progetto corrente
        current = self.wm.get_active_project()
        current_name = current.name if current else None
        
        if current_name == project_name:
            return {
                "action": "already_active",
                "project": project_name
            }
        
        return {
            "action": "switch_project",
            "project": project_name,
            "current": current_name
        }
    
    def format_agent_response(self, intent_result: dict) -> str:
        """Formatta risposta agent per l'utente"""
        
        if intent_result["action"] == "none":
            return ""
        
        if intent_result["action"] == "project_not_found":
            project = intent_result["project"]
            available = intent_result["available"]
            suggestions = intent_result["suggestions"]
            
            response = f"❌ Progetto '{project}' non trovato.\n"
            response += f"📋 Progetti disponibili: {', '.join(available)}\n"
            
            if suggestions:
                response += f"💡 Forse intendevi: {', '.join(suggestions)}\n"
            
            response += "\nPer switchare: 'nh-switch <progetto>' o 'passa a progettoX'"
            return response
        
        if intent_result["action"] == "already_active":
            project = intent_result["project"]
            return f"✅ Sei già sul progetto '{project}'!"
        
        if intent_result["action"] == "switch_project":
            project = intent_result["project"]
            current = intent_result["current"]
            
            response = f"🔄 Vuoi switchare da '{current}' a '{project}'?\n"
            response += f"Scrivi 'sì' per confermare o 'nh-switch {project}' per procedere."
            return response
        
        return ""
    
    def get_workspace_info(self) -> str:
        """Info workspace per inizio conversazione"""
        active = self.wm.get_active_project()
        
        if active:
            return f"👋 Ciao! Stai lavorando sul progetto '{active.name}' in {active.path}"
        else:
            return "👋 Ciao! Nessun progetto attivo. Usa 'nh-switch --list' per vedere i progetti disponibili."
    
    def suggest_workspace_commands(self, user_message: str) -> list:
        """Suggerisci comandi workspace rilevanti"""
        suggestions = []
        
        # Se menziona progetti
        if any(word in user_message.lower() for word in ["progetto", "project", "frontend", "backend"]):
            suggestions.append("nh-switch --list")
            suggestions.append("nh-switch <nome_progetto>")
        
        # Se chiede dove si trova
        if any(phrase in user_message.lower() for word in ["dove", "where", "posizione", "location"]):
            suggestions.append("nh-switch --status")
        
        return suggestions

# Test rapido
if __name__ == "__main__":
    handler = AgentWorkspaceHandler()
    
    test_messages = [
        "ok passiamo al frontend del progetto4",
        "dove sto lavorando?",
        "quali progetti abbiamo?",
        "voglio lavorare sul backend"
    ]
    
    print("🤖 NH Agent Workspace Handler - Test")
    print("=" * 50)
    
    for msg in test_messages:
        result = handler.check_user_intent(msg)
        response = handler.format_agent_response(result)
        if response:
            print(f"\n📝 Utente: '{msg}'")
            print(f"🤖 Agent: {response}")