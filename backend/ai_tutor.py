"""
AI Tutor — Façade publique vers l'orchestrateur multi-agents.
Conserve la même API publique pour ne pas modifier les pages frontend.
Toute la logique IA est déléguée à backend.agents.orchestrator.
"""

from __future__ import annotations

from typing import Dict, List

from backend.agents.orchestrator import get_orchestrator


# ── Chat pédagogique ──────────────────────────────────────────────────────────

def chat_with_tutor(
    messages: List[Dict],
    course_id: int,
    user_message: str,
    stream: bool = False,  # noqa: ARG001 — conservé pour compatibilité API
    response_mode: str = "default",
    language: str = "fr",
) -> str:
    """Répond à une question de l'étudiant via le TutorAgent (RAG + mémoire)."""
    try:
        return get_orchestrator().chat(
            messages=messages,
            course_id=course_id,
            user_message=user_message,
            language=language,
            response_mode=response_mode,
        )
    except RuntimeError as e:
        err = str(e)
        if "QUOTA_EXCEEDED" in err:
            return (
                "⚠️ **Quota Gemini épuisé** pour aujourd'hui.\n\n"
                "Solutions :\n"
                "1. Attendez la réinitialisation quotidienne (minuit heure Pacifique)\n"
                "2. Générez une nouvelle clé API sur [Google AI Studio](https://aistudio.google.com/app/apikey)\n"
                "3. Activez la facturation sur votre projet Google Cloud pour lever la limite"
            ) if language == "fr" else (
                "⚠️ **Gemini quota exhausted** for today.\n\n"
                "Solutions:\n"
                "1. Wait for daily reset (midnight Pacific time)\n"
                "2. Generate a new API key at [Google AI Studio](https://aistudio.google.com/app/apikey)\n"
                "3. Enable billing on your Google Cloud project to remove the limit"
            )
        return (
            "⚠️ Le service IA est temporairement indisponible. Réessayez dans quelques instants."
            if language == "fr"
            else "⚠️ AI service temporarily unavailable. Please retry."
        )


# ── Génération de quiz ────────────────────────────────────────────────────────

def generate_quiz(
    course_id: int,
    topic: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    language: str = "fr",
) -> Dict:
    """Génère un quiz QCM via l'AssessmentAgent avec auto-correction JSON."""
    try:
        return get_orchestrator().generate_quiz(
            course_id=course_id,
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            language=language,
        )
    except Exception as e:
        return {"concept": topic, "questions": [], "error": str(e)}


def generate_targeted_quiz(
    course_id: int,
    weak_concepts: List[str],
    num_questions: int = 3,
    language: str = "fr",
) -> List[Dict]:
    """Génère des quiz ciblés sur les lacunes de l'étudiant."""
    try:
        return get_orchestrator().generate_targeted_quiz(
            course_id=course_id,
            weak_concepts=weak_concepts,
            num_questions=num_questions,
            language=language,
        )
    except Exception:
        return []


# ── Analyse des lacunes ───────────────────────────────────────────────────────

def analyze_weaknesses(
    wrong_answers: List[Dict],
    course_id: int,
    language: str = "fr",
) -> Dict:
    """Analyse les erreurs de quiz et identifie les lacunes via l'AnalysisAgent."""
    try:
        return get_orchestrator().analyze_weaknesses(
            wrong_answers=wrong_answers,
            course_id=course_id,
            language=language,
        )
    except Exception:
        return {
            "concepts_faibles": [item.get("concept", "?") for item in wrong_answers],
            "analyse": "Analyse non disponible.",
            "priorite": wrong_answers[0].get("concept") if wrong_answers else None,
            "plan_etude": [],
            "niveau_global": "intermédiaire",
        }


def generate_study_plan(
    weaknesses: List[Dict],
    student_stats: Dict,
    language: str = "fr",
) -> Dict:
    """Génère un plan d'étude personnalisé via l'AnalysisAgent."""
    try:
        return get_orchestrator().generate_study_plan(
            weaknesses=weaknesses,
            student_stats=student_stats,
            language=language,
        )
    except Exception:
        return {"objectif": "Continuer l'apprentissage", "sessions": [], "conseil_general": ""}


# ── Explication de concept ────────────────────────────────────────────────────

def explain_concept_step_by_step(
    course_id: int,
    concept: str,
    student_level: str = "intermediate",
    language: str = "fr",
) -> str:
    """Explication détaillée pas à pas d'un concept via le TutorAgent."""
    try:
        return get_orchestrator().explain_concept(
            course_id=course_id,
            concept=concept,
            student_level=student_level,
            language=language,
        )
    except RuntimeError:
        return "⚠️ Service IA indisponible. Réessayez dans quelques instants."


# ── Évaluation de réponse ─────────────────────────────────────────────────────

def evaluate_open_answer(
    question: str,
    student_answer: str,
    correct_answer: str,
    course_id: int,
) -> Dict:
    """Évalue une réponse ouverte via l'AssessmentAgent."""
    try:
        return get_orchestrator().evaluate_open_answer(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer,
            course_id=course_id,
        )
    except Exception:
        return {"score": 0.5, "is_correct": False, "feedback": "Évaluation non disponible."}


# ── Rapport de progression ────────────────────────────────────────────────────

def generate_progress_report(
    student_name: str,
    stats: Dict,
    weaknesses: List[Dict],
    language: str = "fr",
) -> str:
    """Génère un rapport de progression textuel via l'AnalysisAgent."""
    return get_orchestrator().generate_progress_report(student_name, stats, weaknesses, language)
