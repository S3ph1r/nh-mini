#!/usr/bin/env python3
"""
NH Intent Parser - Riconoscimento comandi natural language per workspace
"""

import re
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class IntentMatch:
    intent: str
    project: str
    confidence: float
    original_text: str

class IntentParser:
    def __init__(self):
        # Pattern per switch progetto
        self.switch_patterns = [
            # Italiano
            r"passa(?:mo)?\s+(?:al|a\s+il)?\s*(?:progetto|proj)\s+(\w+)",
            r"switch(?:a)?\s+(?:al|a\s+il)?\s*(?:progetto|proj)\s+(\w+)",
            r"voglio\s+lavorare\s+(?:sul|al)\s*(?:progetto|proj)\s+(\w+)",
            r"inizia(?:mo)?\s+(?:a\s+)?lavorare\s+(?:sul|al)\s*(?:progetto|proj)\s+(\w+)",
            r"cambia(?:mo)?\s+(?:progetto|proj)\s+(?:a\s+)?(\w+)",
            r"porta(?:mi)?\s+(?:al|a)\s*(?:progetto|proj)\s+(\w+)",
            
            # Inglese
            r"switch\s+(?:to|project)\s+(\w+)",
            r"change\s+(?:to\s+)?(?:project\s+)?(\w+)",
            r"go\s+to\s+(?:project\s+)?(\w+)",
            r"work\s+on\s+(?:project\s+)?(\w+)",
            r"start\s+working\s+on\s+(?:project\s+)?(\w+)",
            
            # Frontend specific
            r"passa(?:mo)?\s+(?:al|a\s+il)?\s*frontend\s+(?:del\s+)?(?:progetto|proj)\s+(\w+)",
            r"voglio\s+lavorare\s+sul\s+frontend\s+(?:del\s+)?(?:progetto|proj)\s+(\w+)",
            r"frontend\s+(?:di\s+)?(?:progetto|proj)\s+(\w+)",
            
            # Backend specific
            r"passa(?:mo)?\s+(?:al|a\s+il)?\s*backend\s+(?:del\s+)?(?:progetto|proj)\s+(\w+)",
            r"voglio\s+lavorare\s+sul\s+backend\s+(?:del\s+)?(?:progetto|proj)\s+(\w+)",
            r"backend\s+(?:di\s+)?(?:progetto|proj)\s+(\w+)",
        ]
        
        # Pattern per listare progetti
        self.list_patterns = [
            r"quali\s+(?:sono\s+)?(?:i\s+)?progetti",
            r"lista\s+(?:i\s+)?progetti",
            r"mostra\s+(?:mi\s+)?(?:i\s+)?progetti",
            r"che\s+progetti\s+c\'è",
            r"what\s+projects\s+(?:do\s+)?(?:we\s+)?(?:have|got)",
            r"list\s+(?:all\s+)?projects",
            r"show\s+(?:me\s+)?(?:all\s+)?projects",
        ]
        
        # Pattern per stato workspace
        self.status_patterns = [
            r"dove\s+(?:sto\s+)?lavorando",
            r"qual\s+è\s+(?:il\s+)?progetto\s+attivo",
            r"su\s+quale\s+progetto\s+sono",
            r"stato\s+(?:del\s+)?workspace",
            r"where\s+am\s+i\s+working",
            r"what\s+project\s+am\s+i\s+on",
            r"workspace\s+status",
        ]
    
    def parse_intent(self, text: str) -> Optional[IntentMatch]:
        """Parse testo per capire intent"""
        text = text.lower().strip()
        
        # Check switch project
        for pattern in self.switch_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project = match.group(1)
                confidence = self._calculate_confidence(text, pattern)
                return IntentMatch(
                    intent="switch_project",
                    project=project,
                    confidence=confidence,
                    original_text=text
                )
        
        # Check list projects
        for pattern in self.list_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentMatch(
                    intent="list_projects",
                    project="",
                    confidence=0.9,
                    original_text=text
                )
        
        # Check workspace status
        for pattern in self.status_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentMatch(
                    intent="workspace_status",
                    project="",
                    confidence=0.9,
                    original_text=text
                )
        
        return None
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """Calcola confidenza match"""
        base_confidence = 0.8
        
        # Aumenta confidenza se contiene parole chiave specifiche
        if any(word in text for word in ["frontend", "backend", "progetto", "project"]):
            base_confidence += 0.1
        
        # Diminuisci se molte parole extra
        words = len(text.split())
        if words > 10:
            base_confidence -= 0.2
        
        return min(base_confidence, 1.0)
    
    def extract_project_context(self, text: str) -> Dict[str, str]:
        """Estrai contesto aggiuntivo (frontend/backend)"""
        context = {}
        
        if re.search(r"frontend", text, re.IGNORECASE):
            context["type"] = "frontend"
        elif re.search(r"backend", text, re.IGNORECASE):
            context["type"] = "backend"
        
        if re.search(r"nuovo|new", text, re.IGNORECASE):
            context["action"] = "create"
        
        return context

# Test rapido
if __name__ == "__main__":
    parser = IntentParser()
    
    test_phrases = [
        "ok passiamo al frontend del progetto4",
        "voglio lavorare sul backend del progetto2",
        "switch to progetto3",
        "quali sono i progetti disponibili?",
        "dove sto lavorando?"
    ]
    
    print("🧠 NH Intent Parser - Test")
    print("=" * 40)
    
    for phrase in test_phrases:
        result = parser.parse_intent(phrase)
        if result:
            print(f"✅ '{phrase}' → {result.intent} (project: {result.project})")
        else:
            print(f"❌ '{phrase}' → Nessun intent riconosciuto")