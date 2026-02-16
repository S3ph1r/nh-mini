#!/usr/bin/env python3
"""
NH Workspace Manager - Gestione workspace virtuale per multi-progetto
Permette switch progetti senza cambiare IDE workspace
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ProjectInfo:
    name: str
    path: Path
    description: str
    created_at: str
    last_active: str

class WorkspaceManager:
    def __init__(self, nh_root: Path):
        self.nh_root = nh_root
        self.workspace_dir = nh_root / "workspace"
        self.sviluppi_dir = nh_root / "sviluppi"
        self.active_config = self.workspace_dir / "active_config.json"
        self.current_link = self.workspace_dir / "current_project"
        
        # Assicura strutture base
        self.workspace_dir.mkdir(exist_ok=True)
        self.sviluppi_dir.mkdir(exist_ok=True)
        
    def get_active_project(self) -> Optional[ProjectInfo]:
        """Ottieni info progetto attivo"""
        if not self.active_config.exists():
            return None
            
        try:
            with open(self.active_config) as f:
                config = json.load(f)
                
            project_name = config.get("active")
            if not project_name:
                return None
                
            project_path = self.sviluppi_dir / project_name
            if not project_path.exists():
                return None
                
            return ProjectInfo(
                name=project_name,
                path=project_path,
                description=config.get("description", ""),
                created_at=config.get("created_at", ""),
                last_active=config.get("last_active", "")
            )
        except Exception as e:
            print(f"Errore lettura config: {e}")
            return None
    
    def list_projects(self) -> list[ProjectInfo]:
        """Elenca tutti i progetti disponibili"""
        projects = []
        for project_dir in self.sviluppi_dir.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                config_file = project_dir / "project_info.json"
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            info = json.load(f)
                        projects.append(ProjectInfo(
                            name=project_dir.name,
                            path=project_dir,
                            description=info.get("description", ""),
                            created_at=info.get("created_at", ""),
                            last_active=info.get("last_active", "")
                        ))
                    except:
                        pass
        return projects
    
    def switch_project(self, project_name: str, force: bool = False) -> bool:
        """Switcha a nuovo progetto"""
        project_path = self.sviluppi_dir / project_name
        
        if not project_path.exists():
            print(f"❌ Progetto '{project_name}' non trovato")
            return False
        
        # Crea progetto info se mancante
        self._ensure_project_info(project_path, project_name)
        
        # Aggiorna symlink
        if self.current_link.exists() or self.current_link.is_symlink():
            self.current_link.unlink()
        
        self.current_link.symlink_to(project_path)
        
        # Aggiorna config
        config = {
            "active": project_name,
            "path": str(project_path),
            "last_switch": self._timestamp(),
            "previous": self.get_active_project().name if self.get_active_project() else None
        }
        
        with open(self.active_config, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Aggiorna project info
        self._update_project_activity(project_path)
        
        print(f"✅ Switch a '{project_name}' completato!")
        print(f"📍 Workspace attivo: {self.current_link}")
        return True
    
    def create_project(self, project_name: str, description: str = "") -> bool:
        """Crea nuovo progetto"""
        project_path = self.sviluppi_dir / project_name
        
        if project_path.exists():
            print(f"❌ Progetto '{project_name}' già esiste")
            return False
        
        # Crea struttura progetto
        project_path.mkdir(parents=True)
        
        # Crea project info
        project_info = {
            "name": project_name,
            "description": description,
            "created_at": self._timestamp(),
            "last_active": self._timestamp(),
            "nh_version": "1.0"
        }
        
        with open(project_path / "project_info.json", 'w') as f:
            json.dump(project_info, f, indent=2)
        
        # Crea strutture NH base
        (project_path / "knowledge").mkdir()
        (project_path / "state").mkdir()
        (project_path / "secrets").mkdir()
        
        print(f"✅ Progetto '{project_name}' creato!")
        return True
    
    def _ensure_project_info(self, project_path: Path, project_name: str):
        """Assicura che esista project_info.json"""
        config_file = project_path / "project_info.json"
        if not config_file.exists():
            project_info = {
                "name": project_name,
                "description": f"Progetto {project_name}",
                "created_at": self._timestamp(),
                "last_active": self._timestamp(),
                "nh_version": "1.0"
            }
            with open(config_file, 'w') as f:
                json.dump(project_info, f, indent=2)
    
    def _update_project_activity(self, project_path: Path):
        """Aggiorna timestamp ultima attività"""
        config_file = project_path / "project_info.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    info = json.load(f)
                info["last_active"] = self._timestamp()
                with open(config_file, 'w') as f:
                    json.dump(info, f, indent=2)
            except:
                pass
    
    def _timestamp(self) -> str:
        """Timestamp corrente"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def status(self) -> Dict[str, Any]:
        """Stato workspace completo"""
        active = self.get_active_project()
        projects = self.list_projects()
        
        return {
            "active_project": active.name if active else None,
            "active_path": str(active.path) if active else None,
            "total_projects": len(projects),
            "projects": [p.name for p in projects],
            "workspace_dir": str(self.workspace_dir),
            "sviluppi_dir": str(self.sviluppi_dir),
            "current_link_exists": self.current_link.exists(),
            "current_link_target": str(self.current_link.readlink()) if self.current_link.is_symlink() else None
        }

# Singleton globale
_workspace_manager = None

def get_workspace_manager() -> WorkspaceManager:
    """Ottieni workspace manager singleton"""
    global _workspace_manager
    if _workspace_manager is None:
        nh_root = Path(__file__).parent.parent
        _workspace_manager = WorkspaceManager(nh_root)
    return _workspace_manager

if __name__ == "__main__":
    # Test rapido
    wm = get_workspace_manager()
    print("🏗️  NH Workspace Manager - Test")
    print("=" * 40)
    print(json.dumps(wm.status(), indent=2))