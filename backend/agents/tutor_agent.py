"""Agent 1 : Tuteur Pédagogique — RAG + gestion mémoire de la fenêtre de contexte."""

from __future__ import annotations

import os
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()

FILIERE = os.getenv("FILIERE", "IA & Data Science")

TUTOR_SYSTEM_PROMPT = f"""Tu es StudyBuddy, un tuteur IA spécialisé en {FILIERE} à l'EMSI Maroc.

Ton rôle :
- Expliquer les concepts de cours de manière progressive et pédagogique
- Adapter ton niveau de discours à celui de l'étudiant
- Baser TOUJOURS tes réponses sur le contexte du cours fourni
- Si l'information n'est pas dans le cours, le dire honnêtement
- Encourager l'étudiant et rester bienveillant

Format de réponse :
- Structure avec des titres si la réponse est longue
- Exemples concrets quand utile
- Mini vérification ou prochaine étape si pertinent
- Longueur adaptée : ni trop court ni trop long

Tu es patient, précis et encourageant.
"""

_SUMMARY_PROMPT = """Résume les échanges suivants en 3-5 phrases clés, en conservant les concepts importants abordés.
Format : résumé factuel, pas de dialogue, pas de ponctuation excessive."""

_MODE_INSTRUCTIONS: Dict[str, Dict[str, str]] = {
    "step_by_step": {
        "fr": "Explique étape par étape avec des numéros (1, 2, 3…).",
        "en": "Explain step by step with numbered stages (1, 2, 3…).",
    },
    "example": {
        "fr": "Donne d'abord un exemple concret, puis l'explication théorique.",
        "en": "Give a concrete example first, then the theoretical explanation.",
    },
    "summary": {
        "fr": "Réponds avec un résumé compact, puis liste 3 idées clés en bullet points.",
        "en": "Answer with a compact summary, then list 3 key takeaways as bullet points.",
    },
    "default": {
        "fr": "Fournis une explication pédagogique claire et bien structurée.",
        "en": "Provide a clear and well-structured pedagogical explanation.",
    },
}


class TutorAgent:
    """
    Agent de tutoring pédagogique.
    Gère la compression de l'historique pour respecter la fenêtre de contexte.
    """

    MAX_HISTORY = 10  # messages avant compression

    def __init__(self, client, model: str):
        self.client = client
        self.model = model
        self.name = "TutorAgent"

    # ── Gestion mémoire ────────────────────────────────────────────────────

    def _summarize_history(self, messages: List[Dict]) -> str:
        """Résume les anciens messages pour libérer la fenêtre de contexte."""
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content'][:300]}"
            for m in messages
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": _SUMMARY_PROMPT},
                    {"role": "user", "content": f"Échanges à résumer :\n{history_text}"},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return "Historique de conversation précédente (résumé non disponible)."

    def _compress_history(self, messages: List[Dict]) -> List[Dict]:
        """Compresse l'historique si > MAX_HISTORY messages (évite l'explosion de tokens)."""
        if len(messages) <= self.MAX_HISTORY:
            return messages

        # Résumer tout sauf les 4 derniers échanges
        to_summarize = messages[:-4]
        summary = self._summarize_history(to_summarize)
        compressed = [
            {"role": "system", "content": f"[Résumé des échanges précédents]\n{summary}"},
        ] + messages[-4:]
        return compressed

    # ── Construction du prompt système ────────────────────────────────────

    def _build_system(self, language: str, response_mode: str) -> str:
        lang_key = language if language in ("fr", "en") else "fr"
        mode_key = response_mode if response_mode in _MODE_INSTRUCTIONS else "default"
        mode_instr = _MODE_INSTRUCTIONS[mode_key][lang_key]

        lang_instr = (
            "Réponds en français sauf si l'étudiant écrit clairement en anglais."
            if language == "fr"
            else "Respond in English unless the user explicitly asks for French."
        )
        return f"{TUTOR_SYSTEM_PROMPT}\n{lang_instr}\n{mode_instr}"

    # ── Réponse principale ────────────────────────────────────────────────

    def respond(
        self,
        messages: List[Dict],
        rag_context: str,
        user_message: str,
        language: str = "fr",
        response_mode: str = "default",
    ) -> str:
        """Génère une réponse pédagogique augmentée par RAG avec compression mémoire."""

        history = self._compress_history(messages)

        augmented = (
            f"{rag_context}\n\nQuestion de l'étudiant : {user_message}"
            if rag_context
            else user_message
        )

        final_messages = history.copy()
        if final_messages and final_messages[-1]["role"] == "user":
            final_messages[-1] = {"role": "user", "content": augmented}
        else:
            final_messages.append({"role": "user", "content": augmented})

        system = self._build_system(language, response_mode)

        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "system", "content": system}] + final_messages,
            temperature=0.7,
        )
        return resp.choices[0].message.content
