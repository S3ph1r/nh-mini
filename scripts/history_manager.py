#!/usr/bin/env python3
"""
Sistema di Gestione Storico Sviluppo NH-Mini
Append-only logging per tracciare evoluzione sistema
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

HISTORY_FILE = Path(__file__).parent.parent / "knowledge" / "development" / "development-history.mdc"

class DevelopmentHistory:
    """Gestore del registro storico sviluppo"""
    
    VALID_CATEGORIES = ["ARCHITECTURE", "SECURITY", "FEATURE", "DEPRECATION", "BUGFIX", "REFACTOR"]
    VALID_IMPACTS = ["high", "medium", "low"]
    
    def __init__(self):
        self.history_file = HISTORY_FILE
        
    def add_entry(self, category: str, component: str, change: str, reason: str, 
                  author: str = "agent", impact: str = "medium", git_commit: Optional[str] = None) -> bool:
        """Aggiungi nuova entry allo storico"""
        
        # Validazione
        if category not in self.VALID_CATEGORIES:
            print(f"❌ Categoria non valida. Usa: {', '.join(self.VALID_CATEGORIES)}")
            return False
            
        if impact not in self.VALID_IMPACTS:
            print(f"❌ Impact non valido. Usa: {', '.join(self.VALID_IMPACTS)}")
            return False
        
        # Crea entry
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "category": category,
            "component": component,
            "change": change,
            "reason": reason,
            "author": author,
            "impact": impact
        }
        
        if git_commit:
            entry["git_commit"] = git_commit
            
        # Formatta per file markdown
        entry_md = f"""
### {entry['timestamp'][:10]} - {change[:50]}{'...' if len(change) > 50 else ''}
```json
{json.dumps(entry, ensure_ascii=False, indent=2)}
```
"""
        
        # Append to file
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(entry_md)
            print(f"✅ Entry aggiunta allo storico: {component} - {category}")
            return True
        except Exception as e:
            print(f"❌ Errore scrittura storico: {e}")
            return False
    
    def search_entries(self, category: Optional[str] = None, 
                      component: Optional[str] = None, 
                      impact: Optional[str] = None) -> List[Dict]:
        """Cerca entry nello storico"""
        
        entries = []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Trova tutti i blocchi JSON
            import re
            json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
            
            for block in json_blocks:
                try:
                    entry = json.loads(block.strip())
                    
                    # Filtra per criteri
                    if category and entry.get('category') != category:
                        continue
                    if component and component not in entry.get('component', ''):
                        continue
                    if impact and entry.get('impact') != impact:
                        continue
                        
                    entries.append(entry)
                    
                except json.JSONDecodeError:
                    continue
                    
        except FileNotFoundError:
            print("⚠️ File storico non trovato")
        except Exception as e:
            print(f"❌ Errore lettura storico: {e}")
            
        return entries
    
    def get_recent_entries(self, limit: int = 10) -> List[Dict]:
        """Ottieni entry recenti"""
        
        entries = self.search_entries()
        # Ordina per timestamp (decrescente)
        entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return entries[:limit]

def main():
    parser = argparse.ArgumentParser(description='Gestione Storico Sviluppo NH-Mini')
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    # Add entry
    add_parser = subparsers.add_parser('add', help='Aggiungi entry allo storico')
    add_parser.add_argument('--category', required=True, choices=DevelopmentHistory.VALID_CATEGORIES,
                           help='Categoria del cambiamento')
    add_parser.add_argument('--component', required=True, help='Componente coinvolto')
    add_parser.add_argument('--change', required=True, help='Descrizione cambiamento')
    add_parser.add_argument('--reason', required=True, help='Motivazione del cambiamento')
    add_parser.add_argument('--author', default='agent', help='Autore (default: agent)')
    add_parser.add_argument('--impact', default='medium', choices=DevelopmentHistory.VALID_IMPACTS,
                           help='Livello impatto (default: medium)')
    add_parser.add_argument('--git-commit', help='Hash commit git opzionale')
    
    # Search entries
    search_parser = subparsers.add_parser('search', help='Cerca nello storico')
    search_parser.add_argument('--category', choices=DevelopmentHistory.VALID_CATEGORIES,
                              help='Filtra per categoria')
    search_parser.add_argument('--component', help='Filtra per componente')
    search_parser.add_argument('--impact', choices=DevelopmentHistory.VALID_IMPACTS,
                              help='Filtra per impatto')
    
    # Recent entries
    recent_parser = subparsers.add_parser('recent', help='Entry recenti')
    recent_parser.add_argument('--limit', type=int, default=10, help='Numero entry (default: 10)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    history = DevelopmentHistory()
    
    if args.command == 'add':
        success = history.add_entry(
            category=args.category,
            component=args.component,
            change=args.change,
            reason=args.reason,
            author=args.author,
            impact=args.impact,
            git_commit=args.git_commit
        )
        sys.exit(0 if success else 1)
        
    elif args.command == 'search':
        entries = history.search_entries(
            category=args.category,
            component=args.component,
            impact=args.impact
        )
        
        if not entries:
            print("🔍 Nessuna entry trovata")
        else:
            print(f"📊 Trovate {len(entries)} entries:")
            for entry in entries:
                print(f"\n🕐 {entry['timestamp']} | {entry['category']} | {entry['component']}")
                print(f"   Cambiamento: {entry['change']}")
                print(f"   Motivo: {entry['reason']}")
                print(f"   Impatto: {entry['impact']}")
                
    elif args.command == 'recent':
        entries = history.get_recent_entries(args.limit)
        
        if not entries:
            print("📭 Nessuna entry nello storico")
        else:
            print(f"📈 Ultime {len(entries)} entries:")
            for entry in entries:
                print(f"\n🕐 {entry['timestamp']} | {entry['category']} | {entry['component']}")
                print(f"   {entry['change']}")
                print(f"   Motivo: {entry['reason']}")

if __name__ == "__main__":
    main()