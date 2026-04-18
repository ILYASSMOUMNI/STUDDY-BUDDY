"""Agent 3 : Analyste Pédagogique — Détection des lacunes, plan d'étude, rapport."""

from __future__ import annotations

import json
import re
from typing import Dict, List

ANALYSIS_SYSTEM_PROMPT = """Tu es un analyste pédagogique expert en apprentissage adaptatif.
Tu identifies les lacunes conceptuelles des étudiants et proposes des stratégies de remédiation.

Réponds UNIQUEMENT en JSON valide (aucun markdown) :
{
  "concepts_faibles": ["concept1", "concept2"],
  "analyse": "analyse détaillée des erreurs observées en 2-3 phrases",
  "priorite": "concept le plus urgent à revoir",
  "plan_etude": ["action concrète 1", "action concrète 2", "action concrète 3"],
  "niveau_global": "débutant|intermédiaire|avancé"
}"""

STUDY_PLAN_SYSTEM_PROMPT = """Tu es un conseiller pédagogique expert en IA & Data Science.
Génère un plan d'étude personnalisé et réaliste en JSON (aucun markdown) :
{
  "objectif": "objectif principal en une phrase",
  "sessions": [
    {
      "titre": "titre de la session",
      "duree_min": 30,
      "activite": "lecture|quiz|exercice|revision",
      "priorite": "haute|moyenne|faible",
      "description": "description courte"
    }
  ],
  "conseil_general": "conseil personnalisé et encourageant"
}"""


class AnalysisAgent:
    """
    Agent d'analyse des performances et de recommandation d'apprentissage.
    Fournit : analyse des lacunes, plan d'étude personnalisé, rapport de progression.
    """

    def __init__(self, client, model: str):
        self.client = client
        self.model = model
        self.name = "AnalysisAgent"

    # ── Utilitaires ────────────────────────────────────────────────────────

    def _call(self, system: str, user_content: str, max_tokens: int = 900) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content

    def _parse_json(self, raw: str) -> dict:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        return json.loads(raw.strip())

    # ── Analyse des lacunes ───────────────────────────────────────────────

    def analyze_weaknesses(
        self,
        wrong_answers: List[Dict],
        rag_context: str,
        language: str = "fr",
    ) -> Dict:
        """Analyse les erreurs de quiz et identifie les lacunes conceptuelles."""

        if not wrong_answers:
            return {
                "concepts_faibles": [],
                "analyse": "Aucune erreur — performance excellente !",
                "priorite": None,
                "plan_etude": [],
                "niveau_global": "avancé",
            }

        errors_text = "\n".join(
            f"- Concept: {item.get('concept', '?')} | "
            f"Question: {item.get('question', '?')} | "
            f"Réponse étudiant: {item.get('student_answer', '?')} | "
            f"Réponse correcte: {item.get('correct', '?')}"
            for item in wrong_answers
        )

        lang_note = "Réponds en anglais." if language == "en" else "Réponds en français."
        prompt = (
            f"{rag_context}\n\n"
            f"Erreurs de l'étudiant :\n{errors_text}\n\n"
            f"{lang_note}\n"
            "Analyse ces erreurs et retourne uniquement le JSON."
        )

        try:
            raw = self._call(ANALYSIS_SYSTEM_PROMPT, prompt, max_tokens=1000)
            return self._parse_json(raw)
        except Exception as e:
            print(f"[AnalysisAgent] analyze_weaknesses error: {e}")
            return {
                "concepts_faibles": [item.get("concept", "?") for item in wrong_answers],
                "analyse": "Analyse non disponible — réessayez ultérieurement.",
                "priorite": wrong_answers[0].get("concept") if wrong_answers else None,
                "plan_etude": ["Relire le cours", "Refaire le quiz", "Consulter le tuteur"],
                "niveau_global": "intermédiaire",
            }

    # ── Plan d'étude ──────────────────────────────────────────────────────

    def generate_study_plan(
        self,
        weaknesses: List[Dict],
        student_stats: Dict,
        language: str = "fr",
    ) -> Dict:
        """Génère un plan d'étude personnalisé basé sur les lacunes et les stats."""

        if not weaknesses:
            return {
                "objectif": "Maintenir l'excellence",
                "sessions": [],
                "conseil_general": "Excellent travail ! Continuez à pratiquer régulièrement.",
            }

        concepts = [w.get("concept", "?") for w in weaknesses[:5]]
        score = student_stats.get("score_global", 0)
        total = student_stats.get("total_questions", 0)
        lang_note = "Answer in English." if language == "en" else "Réponds en français."

        prompt = (
            f"Score global de l'étudiant : {score}% sur {total} questions.\n"
            f"Concepts à revoir (par priorité) : {', '.join(concepts)}\n"
            f"{lang_note}\n"
            "Génère un plan d'étude personnalisé et réaliste en JSON."
        )

        try:
            raw = self._call(STUDY_PLAN_SYSTEM_PROMPT, prompt, max_tokens=900)
            return self._parse_json(raw)
        except Exception as e:
            print(f"[AnalysisAgent] generate_study_plan error: {e}")
            return {
                "objectif": f"Maîtriser {concepts[0]}" if concepts else "Progresser",
                "sessions": [
                    {
                        "titre": f"Révision : {c}",
                        "duree_min": 30,
                        "activite": "quiz",
                        "priorite": "haute",
                        "description": f"Revoir les fondamentaux de {c}",
                    }
                    for c in concepts[:3]
                ],
                "conseil_general": "Concentrez-vous sur les concepts prioritaires, un à la fois.",
            }

    # ── Rapport de progression ────────────────────────────────────────────

    def generate_progress_report(
        self,
        student_name: str,
        stats: Dict,
        weaknesses: List[Dict],
        language: str = "fr",
    ) -> str:
        """Génère un rapport de progression textuel formaté."""

        score = stats.get("score_global", 0)
        total = stats.get("total_questions", 0)
        correct = stats.get("correct_answers", 0)
        weak_concepts = [w.get("concept", "?") for w in weaknesses[:3]]

        if language == "en":
            verdict = "Excellent!" if score >= 70 else "Keep practicing!" if score >= 50 else "Needs more work."
            weak_str = ", ".join(weak_concepts) if weak_concepts else "None"
            return (
                f"Progress Report — {student_name}\n"
                f"{'─' * 36}\n"
                f"Questions answered : {total}\n"
                f"Correct answers    : {correct}\n"
                f"Overall score      : {score}%\n"
                f"Concepts to review : {weak_str}\n"
                f"Verdict            : {verdict}"
            )
        else:
            verdict = "Excellent !" if score >= 70 else "Continuez vos efforts !" if score >= 50 else "Plus de travail nécessaire."
            weak_str = ", ".join(weak_concepts) if weak_concepts else "Aucun"
            return (
                f"Rapport de Progression — {student_name}\n"
                f"{'─' * 36}\n"
                f"Questions répondues  : {total}\n"
                f"Réponses correctes   : {correct}\n"
                f"Score global         : {score}%\n"
                f"Concepts à revoir    : {weak_str}\n"
                f"Verdict              : {verdict}"
            )
