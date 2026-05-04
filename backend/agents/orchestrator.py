"""
Orchestrateur Multi-Agents — Coordination, retry, fallback et routage intelligent.
Couche 1 (Orchestration) du système SMA StudyBuddy.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from backend.agents.tutor_agent import TutorAgent
from backend.agents.assessment_agent import AssessmentAgent
from backend.agents.analysis_agent import AnalysisAgent

load_dotenv()


def _get_config():
    """Lit le fichier .env directement — ignore os.environ pour éviter les valeurs cachées."""
    from dotenv import dotenv_values
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    cfg = dotenv_values(env_path)

    # Priorité : GROQ (quota généreux) > GEMINI > OPENROUTER
    api_key = (
        cfg.get("GROQ_API_KEY")
        or cfg.get("GEMINI_API_KEY")
        or cfg.get("OPENROUTER_API_KEY", "")
    )

    if api_key.startswith("gsk_"):                        # Groq
        primary  = cfg.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        fallback = cfg.get("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant")
    elif api_key.startswith("AIzaSy"):                    # Google Gemini direct
        primary  = cfg.get("GEMINI_MODEL", "gemini-1.5-flash")
        fallback = cfg.get("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash-8b")
    else:                                                  # OpenRouter
        primary  = cfg.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
        fallback = cfg.get("FALLBACK_MODEL", "google/gemini-1.5-flash")

    print(f"[Config] Clé: {api_key[:12]}... | Modèle: {primary}")
    return api_key, primary, fallback


def _detect_provider(api_key: str) -> tuple[str, dict, bool]:
    """Retourne (base_url, extra_headers, is_openrouter) selon le type de clé API."""
    if api_key.startswith("gsk_"):      # Groq
        return "https://api.groq.com/openai/v1", {}, False
    if api_key.startswith("AIzaSy"):   # Google Gemini direct
        return "https://generativelanguage.googleapis.com/v1beta/openai/", {}, False
    return "https://openrouter.ai/api/v1", {  # OpenRouter
        "HTTP-Referer": "https://studybuddy.emsi.ma",
        "X-Title": "StudyBuddy EMSI",
    }, True


def _normalize_model(model: str, is_openrouter: bool) -> str:
    """
    OpenRouter  : needs provider/model-id format — add prefix if missing.
    Gemini direct: strip provider prefix if present (API only wants the short name).
    """
    if is_openrouter:
        if "/" in model:
            return model  # already fully-qualified
        name = model.lower()
        if "gemini" in name:
            return f"google/{model}"
        if any(x in name for x in ("gpt-", "o1-", "o3-")):
            return f"openai/{model}"
        if "claude" in name:
            return f"anthropic/{model}"
        return model
    else:
        # Gemini direct API — strip provider prefix if user wrote google/model-name
        if model.startswith("google/"):
            return model[len("google/"):]
        return model

# ── Rate limiter (15 RPM free tier = 1 req / 4 s) ───────────────────────────

_last_call_ts: float = 0.0
_MIN_CALL_INTERVAL = 4.0   # secondes entre deux appels API


def _rate_limit():
    """Attend si nécessaire pour ne pas dépasser 15 req/min."""
    global _last_call_ts
    wait = _MIN_CALL_INTERVAL - (time.time() - _last_call_ts)
    if wait > 0:
        time.sleep(wait)
    _last_call_ts = time.time()


# ── Singletons ──────────────────────────────────────────────────────────────

_client: Optional[OpenAI] = None
_orchestrator: Optional["AgentOrchestrator"] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key, _, _ = _get_config()
        base_url, extra_headers, _ = _detect_provider(api_key)
        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=extra_headers,
            timeout=60.0,
        )
    return _client


def get_orchestrator() -> "AgentOrchestrator":
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator


# ── Orchestrateur ────────────────────────────────────────────────────────────

_RESPONSE_CACHE: Dict[str, str] = {}
_RAG_CACHE: Dict[str, str] = {}
_CACHE_MAX_SIZE = 50


def _cache_key(*parts) -> str:
    return hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()


class AgentOrchestrator:
    """
    Orchestrateur principal du SMA StudyBuddy.

    Responsabilités :
    - Router les requêtes vers le bon agent (TutorAgent / AssessmentAgent / AnalysisAgent)
    - Récupérer le contexte RAG depuis le VectorStore (via MCP)
    - Gérer les erreurs API avec retry exponentiel + fallback model
    - Surveiller la fenêtre de contexte et déclencher la compression mémoire
    """

    MAX_RETRIES = 1  # 0 retry — fail fast, quota épuisé = inutile de réessayer
    BASE_DELAY  = 2

    def __init__(self):
        api_key, raw_primary, raw_fallback = _get_config()
        _, _, is_openrouter = _detect_provider(api_key)
        primary  = _normalize_model(raw_primary, is_openrouter)
        fallback = _normalize_model(raw_fallback, is_openrouter)
        client = get_client()
        self.tutor    = TutorAgent(client, primary)
        self.assessor = AssessmentAgent(client, primary, fallback)
        self.analyzer = AnalysisAgent(client, primary)
        print(f"[Orchestrator] Initialisé — provider: {'OpenRouter' if is_openrouter else 'Gemini'} modele: {primary}")

    # ── Contexte RAG (accès vectorstore via abstraction MCP) ───────────────

    def _build_rag_context(
        self,
        course_id: Optional[int],
        query: str,
        top_k: int = 3,
    ) -> str:
        """Construit le contexte RAG en interrogeant la base vectorielle (avec cache)."""
        key = _cache_key(course_id, query, top_k)
        if key in _RAG_CACHE:
            return _RAG_CACHE[key]

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
                relevant = chunks[:2]

            parts = ["=== CONTEXTE DU COURS ===\n"]
            for i, chunk in enumerate(relevant, 1):
                # Tronquer à 150 mots max par chunk pour limiter les tokens
                words = chunk['text'].split()
                text = " ".join(words[:150])
                parts.append(f"[Extrait {i}]\n{text}\n")
            parts.append("========================\n")
            result = "\n".join(parts)

            if len(_RAG_CACHE) >= _CACHE_MAX_SIZE:
                _RAG_CACHE.pop(next(iter(_RAG_CACHE)))
            _RAG_CACHE[key] = result
            return result

        except Exception as e:
            print(f"[Orchestrator] Erreur RAG : {e}")
            return ""

    # ── Gestion du fallback de modèle ─────────────────────────────────────

    def _activate_fallback(self):
        """Bascule tous les agents sur le modèle de secours."""
        api_key, _, raw_fallback = _get_config()
        _, _, is_openrouter = _detect_provider(api_key)
        fallback = _normalize_model(raw_fallback, is_openrouter)
        self.tutor.model    = fallback
        self.assessor.model = fallback
        self.analyzer.model = fallback
        print(f"[Orchestrator] Bascule sur le modele de secours : {fallback}")

    # ── Wrapper retry + fallback ───────────────────────────────────────────

    def _with_retry(self, fn, *args, **kwargs):
        """
        Respecte le rate limit avant chaque appel.
        Sur 429 : attend 15 s et retente une fois (quota RPM, pas RPD).
        """
        _rate_limit()
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # Attendre et réessayer une seule fois
                time.sleep(15)
                _rate_limit()
                try:
                    return fn(*args, **kwargs)
                except Exception as e2:
                    if "429" in str(e2) or "RESOURCE_EXHAUSTED" in str(e2):
                        raise RuntimeError("QUOTA_EXCEEDED") from e2
                    raise RuntimeError(f"Service IA indisponible : {e2}") from e2
            raise RuntimeError(f"Service IA indisponible : {e}") from e

    # ── API publique : TutorAgent ──────────────────────────────────────────

    def chat(
        self,
        messages: List[Dict],
        course_id: Optional[int],
        user_message: str,
        language: str = "fr",
        response_mode: str = "default",
    ) -> str:
        """Chat pédagogique augmenté par RAG — avec cache de réponse."""
        # Cache hit — évite un appel API pour la même question dans le même contexte
        cache_key = _cache_key(course_id, user_message, response_mode, language)
        if cache_key in _RESPONSE_CACHE:
            return _RESPONSE_CACHE[cache_key]

        rag = self._build_rag_context(course_id, user_message)
        result = self._with_retry(
            self.tutor.respond,
            messages=messages,
            rag_context=rag,
            user_message=user_message,
            language=language,
            response_mode=response_mode,
        )
        # Stocker en cache (LRU simple)
        if len(_RESPONSE_CACHE) >= _CACHE_MAX_SIZE:
            _RESPONSE_CACHE.pop(next(iter(_RESPONSE_CACHE)))
        _RESPONSE_CACHE[cache_key] = result
        return result

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
