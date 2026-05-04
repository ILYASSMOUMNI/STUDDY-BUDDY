"""Agent 2 : Évaluateur — Génération de quiz QCM + boucle d'auto-correction JSON."""

from __future__ import annotations

import json
import re
import time
from typing import Dict, List, Optional

QUIZ_SYSTEM_PROMPT = """Tu es un générateur de quiz pédagogique expert.

Règles STRICTES :
1. Génère des QCM basés UNIQUEMENT sur le contenu du cours fourni
2. Chaque question teste la compréhension, pas la mémorisation brute
3. Les choix incorrects doivent être plausibles (pas évidents)
4. L'explication doit clarifier POURQUOI la réponse est correcte

Format JSON OBLIGATOIRE (aucun markdown, aucun backtick, JSON pur) :
{
  "concept": "nom du concept testé",
  "questions": [
    {
      "id": 1,
      "question": "texte de la question ?",
      "choices": ["A) option1", "B) option2", "C) option3", "D) option4"],
      "correct_index": 0,
      "correct_answer": "A) option1",
      "explanation": "explication courte du pourquoi"
    }
  ]
}"""

EVALUATOR_SYSTEM_PROMPT = """Tu es un évaluateur pédagogique précis et bienveillant.
Réponds UNIQUEMENT en JSON valide (aucun markdown) :
{"score": 0.0, "is_correct": false, "feedback": "retour constructif court"}
"""

_DIFFICULTY_MAP = {
    "easy": "facile (concepts de base, définitions)",
    "medium": "moyen (compréhension et application directe)",
    "hard": "difficile (analyse, synthèse et cas pratiques)",
    "targeted": "ciblé sur les lacunes de l'étudiant",
}


class AssessmentAgent:
    """
    Agent d'évaluation avec :
    - Boucle d'auto-correction JSON (Self-Correction Loop, max 3 tentatives)
    - Fallback model si le modèle principal échoue
    """

    MAX_RETRIES = 2
    RETRY_DELAY = 1.0  # secondes

    def __init__(self, client, model: str, fallback_model: Optional[str] = None):
        self.client = client
        self.model = model
        self.fallback_model = fallback_model or model
        self.name = "AssessmentAgent"

    # ── Utilitaires ────────────────────────────────────────────────────────

    def _clean_json(self, raw: str) -> str:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
        return raw.strip()

    def _parse_json(self, raw: str) -> dict:
        return json.loads(self._clean_json(raw))

    def _call(
        self,
        system: str,
        user_content: str,
        max_tokens: int,
        temperature: float = 0.6,
        use_fallback: bool = False,
        json_mode: bool = False,
    ) -> str:
        model = self.fallback_model if use_fallback else self.model
        kwargs: dict = dict(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content

    # ── Génération de quiz ────────────────────────────────────────────────

    def generate_quiz(
        self,
        rag_context: str,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        language: str = "fr",
    ) -> Dict:
        """
        Génère un quiz QCM avec boucle d'auto-correction (Self-Correction Loop).
        Si le JSON est invalide, on demande à l'agent de se corriger.
        """
        diff_label = _DIFFICULTY_MAP.get(difficulty, difficulty)
        lang_label = "anglais" if language == "en" else "français"

        base_prompt = (
            f"{rag_context}\n\n"
            f"Génère exactement {num_questions} questions QCM sur : \"{topic}\"\n"
            f"Difficulté : {diff_label}\n"
            f"Langue de sortie : {lang_label}\n"
            "Réponds UNIQUEMENT avec le JSON, rien d'autre."
        )
        prompt = base_prompt

        for attempt in range(self.MAX_RETRIES):
            use_fallback = attempt == self.MAX_RETRIES - 1
            try:
                raw = self._call(QUIZ_SYSTEM_PROMPT, prompt, max_tokens=1800, use_fallback=use_fallback, json_mode=True)
                result = self._parse_json(raw)

                # Validation du schéma
                if "questions" not in result or not isinstance(result["questions"], list):
                    raise ValueError("Clé 'questions' absente ou invalide")
                if len(result["questions"]) == 0:
                    raise ValueError("Liste de questions vide")

                return result

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"[AssessmentAgent] Tentative {attempt + 1}/{self.MAX_RETRIES} – JSON invalide : {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    # Auto-correction : on informe l'agent de son erreur
                    prompt = (
                        f"{base_prompt}\n\n"
                        f"[CORRECTION REQUISE] Tentative précédente invalide : {e}. "
                        "Génère un JSON parfaitement valide, conforme au schéma demandé."
                    )
            except Exception as e:
                print(f"[AssessmentAgent] Erreur API tentative {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))

        return {"concept": topic, "questions": [], "error": "Échec après 3 tentatives"}

    # ── Évaluation de réponse ouverte ─────────────────────────────────────

    def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
    ) -> Dict:
        """Évalue une réponse ouverte avec feedback constructif."""
        prompt = (
            f"Question : {question}\n"
            f"Réponse correcte : {correct_answer}\n"
            f"Réponse de l'étudiant : {student_answer}\n"
            "Évalue et retourne le JSON."
        )
        try:
            raw = self._call(EVALUATOR_SYSTEM_PROMPT, prompt, max_tokens=300, temperature=0.3, json_mode=True)
            return self._parse_json(raw)
        except Exception:
            return {"score": 0.5, "is_correct": False, "feedback": "Évaluation non disponible."}
