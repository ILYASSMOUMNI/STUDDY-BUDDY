"""
MCP Server (Model Context Protocol) — Couche 4 : Action & Résilience.

Abstraction totale entre la logique des agents et les sources de données.
Expose des outils standardisés pour : SQLite, VectorStore, fichiers locaux.
Chaque appel est logué et retourne succès/échec interprétable par l'orchestrateur.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


# ── Modèle d'un outil MCP ────────────────────────────────────────────────────

class MCPTool:
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Dict[str, Any],
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters = parameters

    def to_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {"type": "object", "properties": self.parameters},
        }


# ── Serveur MCP ───────────────────────────────────────────────────────────────

class MCPServer:
    """
    Serveur MCP local — implémentation du Model Context Protocol.

    Garantit :
    - Une interface unifiée pour toutes les sources de données (SQL, vectorstore, fichiers)
    - Un logging complet de chaque appel outil (succès/échec)
    - Une interprétation du retour d'action pour déclencher les chemins de repli
    """

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._call_log: List[Dict] = []
        self._setup_tools()
        print(f"[MCP] Serveur initialisé — {len(self._tools)} outils enregistrés")

    # ── Enregistrement des outils ─────────────────────────────────────────

    def _setup_tools(self):
        """Enregistre tous les outils disponibles pour les agents."""
        import backend.database as db
        from backend.vector_store import search, search_all_courses, course_is_indexed

        self.register_tool(
            name="get_student_profile",
            description="Récupère le profil, les stats et les lacunes d'un étudiant (SQLite)",
            handler=lambda p: {
                "student": db.get_student_by_email(p.get("email", "")) if p.get("email") else None,
                "stats": db.get_student_stats(p["student_id"]) if p.get("student_id") else {},
                "weaknesses": db.get_weaknesses(p["student_id"]) if p.get("student_id") else [],
            },
            parameters={
                "student_id": {"type": "integer", "description": "ID de l'étudiant"},
                "email": {"type": "string", "description": "Email de l'étudiant"},
            },
        )

        self.register_tool(
            name="search_knowledge",
            description="Recherche sémantique dans la base vectorielle ChromaDB (RAG)",
            handler=lambda p: {
                "results": (
                    search(p["course_id"], p["query"], p.get("top_k", 5))
                    if p.get("course_id")
                    else search_all_courses(p["query"], p.get("top_k", 5))
                ),
                "course_indexed": course_is_indexed(p["course_id"]) if p.get("course_id") else True,
            },
            parameters={
                "query": {"type": "string", "description": "Requête de recherche sémantique"},
                "course_id": {"type": "integer", "description": "ID du cours (optionnel)"},
                "top_k": {"type": "integer", "description": "Nombre de résultats"},
            },
        )

        self.register_tool(
            name="save_quiz_result",
            description="Sauvegarde un résultat de quiz dans SQLite et met à jour les lacunes",
            handler=lambda p: db.save_quiz_result(**p),
            parameters={
                "student_id": {"type": "integer"},
                "course_id": {"type": "integer"},
                "concept": {"type": "string"},
                "question": {"type": "string"},
                "student_answer": {"type": "string"},
                "correct_answer": {"type": "string"},
                "is_correct": {"type": "boolean"},
                "score": {"type": "number"},
            },
        )

        self.register_tool(
            name="list_courses",
            description="Liste tous les cours disponibles avec métadonnées (SQLite)",
            handler=lambda p: {"courses": db.get_all_courses()},
            parameters={},
        )

        self.register_tool(
            name="get_course_progress",
            description="Récupère la progression de l'étudiant par cours",
            handler=lambda p: {"progress": db.get_course_progress(p["student_id"])},
            parameters={"student_id": {"type": "integer"}},
        )

        self.register_tool(
            name="get_recommended_actions",
            description="Récupère les actions recommandées pour l'étudiant",
            handler=lambda p: {"actions": db.get_recommended_actions(p["student_id"])},
            parameters={"student_id": {"type": "integer"}},
        )

        self.register_tool(
            name="read_local_file",
            description="Lit un fichier local (txt, md) — accès fichiers locaux",
            handler=self._read_local_file,
            parameters={
                "file_path": {"type": "string", "description": "Chemin relatif du fichier"},
            },
        )

    def _read_local_file(self, params: Dict) -> Dict:
        import os
        path = params.get("file_path", "")
        # Sécurité : empêche la traversée de répertoire
        base = os.path.abspath("./data")
        full = os.path.abspath(os.path.join("./data", path))
        if not full.startswith(base):
            return {"error": "Accès refusé : chemin hors du répertoire autorisé"}
        try:
            with open(full, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "path": path, "size": len(content)}
        except FileNotFoundError:
            return {"error": f"Fichier non trouvé : {path}"}

    # ── API publique ──────────────────────────────────────────────────────

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: Dict,
    ):
        self._tools[name] = MCPTool(name, description, handler, parameters)

    def list_tools(self) -> List[Dict]:
        return [t.to_schema() for t in self._tools.values()]

    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """
        Exécute un outil MCP.
        Retourne un résultat structuré {"success": bool, "data": ...} ou {"error": ...}.
        L'orchestrateur interprète ce retour pour déclencher un chemin de repli si nécessaire.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params_keys": list(params.keys()),
            "success": False,
            "error": None,
        }

        if tool_name not in self._tools:
            log_entry["error"] = f"Outil inconnu : {tool_name}"
            self._call_log.append(log_entry)
            return {"success": False, "error": log_entry["error"]}

        try:
            result = self._tools[tool_name].handler(params)
            log_entry["success"] = True
            self._call_log.append(log_entry)
            return {"success": True, "data": result}
        except Exception as e:
            log_entry["error"] = str(e)
            self._call_log.append(log_entry)
            print(f"[MCP] ❌ Erreur tool '{tool_name}' : {e}")
            return {"success": False, "error": str(e), "tool": tool_name}

    def get_call_log(self, last_n: int = 20) -> List[Dict]:
        return self._call_log[-last_n:]

    def health_check(self) -> Dict:
        return {
            "status": "healthy",
            "tools_count": len(self._tools),
            "tool_names": list(self._tools.keys()),
            "total_calls": len(self._call_log),
            "failed_calls": sum(1 for e in self._call_log if not e["success"]),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
