"""
Orchestrateur Multi-Agents — Coordination, retry, fallback et routage intelligent.
Couche 1 (Orchestration) du système SMA StudyBuddy.
"""

from __future__ import annotations

import os
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from backend.agents.tutor_agent import TutorAgent
from backend.agents.assessment_agent import AssessmentAgent
from backend.agents.analysis_agent import AnalysisAgent

load_dotenv()

_PRIMARY_MODEL  = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
_FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "google/gemma-2-9b-it:free")
_API_KEY        = os.getenv("OPENROUTER_API_KEY", "")

# ── Singletons ──────────────────────────────────────────────────────────────

_client: Optional[OpenAI] = None
_orchestrator: Optional["AgentOrchestrator"] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://studybuddy.emsi.ma",
                "X-Title": "StudyBuddy EMSI",
            },
        )
    return _client


def get_orchestrator() -> "AgentOrchestrator":
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


# ── Orchestrateur ────────────────────────────────────────────────────────────

class AgentOrchestrator:
    """
    Orchestrateur principal du SMA StudyBuddy.

    Responsabilités :
    - Router les requêtes vers le bon agent (TutorAgent / AssessmentAgent / AnalysisAgent)
    - Récupérer le contexte RAG depuis le VectorStore (via MCP)
    - Gérer les erreurs API avec retry exponentiel + fallback model
    - Surveiller la fenêtre de contexte et déclencher la compression mémoire
    """

    MAX_RETRIES = 3
    BASE_DELAY  = 2  # secondes (exponentiel : 2, 4, 8)

    def __init__(self):
        client = get_client()
        self.tutor    = TutorAgent(client, _PRIMARY_MODEL)
        self.assessor = AssessmentAgent(client, _PRIMARY_MODEL, _FALLBACK_MODEL)
        self.analyzer = AnalysisAgent(client, _PRIMARY_MODEL)
        print(f"[Orchestrator] ✅ Initialisé — modèle: {_PRIMARY_MODEL} / fallback: {_FALLBACK_MODEL}")

    # ── Contexte RAG (accès vectorstore via abstraction MCP) ───────────────

    def _build_rag_context(
        self,
        course_id: Optional[int],
        query: str,
        top_k: int = 5,
    ) -> str:
        """Construit le contexte RAG en interrogeant la base vectorielle."""
        try:
            from backend.vector_store import search, search_all_courses

            chunks = (
                search(course_id, query, top_k=top_k)
                if course_id
                else search_all_courses(query, top_k=top_k)
            )
            if not chunks:
                return ""

            relevant = [c for c in chunks if c.get("distance", 1.0) < 0.85]
            if not relevant:
                relevant = chunks[:3]

            parts = ["=== CONTEXTE DU COURS ===\n"]
            for i, chunk in enumerate(relevant, 1):
                parts.append(f"[Extrait {i}]\n{chunk['text']}\n")
            parts.append("========================\n")
            return "\n".join(parts)

        except Exception as e:
            print(f"[Orchestrator] Erreur RAG : {e}")
            return ""

    # ── Wrapper retry + fallback ───────────────────────────────────────────

    def _with_retry(self, fn, *args, **kwargs):
        """
        Exécute fn avec retry exponentiel.
        Boucle d'observation & Fallback : interprète le retour d'action (succès/échec).
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                last_error = e
                wait = self.BASE_DELAY * (2 ** attempt)
                print(f"[Orchestrator] Tentative {attempt + 1}/{self.MAX_RETRIES} échouée ({e}), retry dans {wait}s")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(wait)
        # Chemin de repli : lever l'erreur pour que l'UI affiche un message gracieux
        raise RuntimeError(f"Service IA indisponible après {self.MAX_RETRIES} tentatives : {last_error}")

    # ── API publique : TutorAgent ──────────────────────────────────────────

    def chat(
        self,
        messages: List[Dict],
        course_id: Optional[int],
        user_message: str,
        language: str = "fr",
        response_mode: str = "default",
    ) -> str:
        """Chat pédagogique augmenté par RAG — délégué au TutorAgent."""
        rag = self._build_rag_context(course_id, user_message)
        return self._with_retry(
            self.tutor.respond,
            messages=messages,
            rag_context=rag,
            user_message=user_message,
            language=language,
            response_mode=response_mode,
        )

    def explain_concept(
        self,
        course_id: int,
        concept: str,
        student_level: str = "intermediate",
        language: str = "fr",
    ) -> str:
        """Explication détaillée pas à pas d'un concept — délégué au TutorAgent."""
        rag = self._build_rag_context(course_id, concept, top_k=5)
        level_note = f"Niveau de l'étudiant : {student_level}."
        return self._with_retry(
            self.tutor.respond,
            messages=[],
            rag_context=rag,
            user_message=f"Explique le concept : \"{concept}\". {level_note}",
            language=language,
            response_mode="step_by_step",
        )

    # ── API publique : AssessmentAgent ────────────────────────────────────

    def generate_quiz(
        self,
        course_id: int,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        language: str = "fr",
    ) -> Dict:
        """Génération de quiz QCM — délégué à l'AssessmentAgent."""
        rag = self._build_rag_context(course_id, topic, top_k=6)
        return self._with_retry(
            self.assessor.generate_quiz,
            rag_context=rag,
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            language=language,
        )

    def generate_targeted_quiz(
        self,
        course_id: int,
        weak_concepts: List[str],
        num_questions: int = 3,
        language: str = "fr",
    ) -> List[Dict]:
        """Quiz ciblé sur les lacunes — appelle AssessmentAgent par concept."""
        quizzes = []
        for concept in weak_concepts[:3]:
            quiz = self.generate_quiz(course_id, concept, num_questions, "targeted", language)
            if quiz.get("questions"):
                quizzes.append(quiz)
        return quizzes

    def evaluate_open_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        course_id: int,
    ) -> Dict:
        """Évaluation de réponse ouverte — délégué à l'AssessmentAgent."""
        return self._with_retry(
            self.assessor.evaluate_answer,
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer,
        )

    # ── API publique : AnalysisAgent ──────────────────────────────────────

    def analyze_weaknesses(
        self,
        wrong_answers: List[Dict],
        course_id: int,
        language: str = "fr",
    ) -> Dict:
        """Analyse des lacunes — délégué à l'AnalysisAgent."""
        concepts_query = " ".join(item.get("concept", "") for item in wrong_answers)
        rag = self._build_rag_context(course_id, concepts_query, top_k=3)
        return self._with_retry(
            self.analyzer.analyze_weaknesses,
            wrong_answers=wrong_answers,
            rag_context=rag,
            language=language,
        )

    def generate_study_plan(
        self,
        weaknesses: List[Dict],
        student_stats: Dict,
        language: str = "fr",
    ) -> Dict:
        """Plan d'étude personnalisé — délégué à l'AnalysisAgent."""
        return self._with_retry(
            self.analyzer.generate_study_plan,
            weaknesses=weaknesses,
            student_stats=student_stats,
            language=language,
        )

    def generate_progress_report(
        self,
        student_name: str,
        stats: Dict,
        weaknesses: List[Dict],
        language: str = "fr",
    ) -> str:
        """Rapport de progression — délégué à l'AnalysisAgent."""
        return self.analyzer.generate_progress_report(student_name, stats, weaknesses, language)
