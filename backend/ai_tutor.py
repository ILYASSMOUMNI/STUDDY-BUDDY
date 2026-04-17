"""AI tutor helpers powered by OpenRouter + RAG."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from backend.vector_store import search, search_all_courses

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
FILIERE = os.getenv("FILIERE", "IA & Data Science")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://studybuddy.emsi.ma",
        "X-Title": "StudyBuddy EMSI",
    },
)

_BASE_TUTOR_PROMPT = f"""Tu es StudyBuddy, un tuteur IA specialise en {FILIERE}.
Tu aides les etudiants a comprendre leurs cours de maniere progressive et pedagogique.

Regles :
1. Base toujours tes explications sur le contexte du cours fourni.
2. Explique clairement et de facon structuree.
3. Adapte ton niveau si l'etudiant est perdu.
4. Termine si utile par une mini verification ou une prochaine etape.
5. Si l'information n'apparait pas dans le cours, dis-le honnetement.
"""

QUIZ_SYSTEM_PROMPT = f"""Tu es un generateur de quiz pedagogique pour la filiere {FILIERE}.
Tu generes des QCM bases strictement sur le contenu du cours fourni.

Reponds toujours en JSON valide, sans markdown ni backticks :
{{
  "concept": "nom du concept",
  "questions": [
    {{
      "id": 1,
      "question": "texte de la question",
      "choices": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_index": 0,
      "correct_answer": "A) ...",
      "explanation": "explication courte"
    }}
  ]
}}
"""

WEAKNESS_SYSTEM_PROMPT = """Tu es un analyseur pedagogique.
Reponds uniquement en JSON, sans markdown :
{"concepts_faibles": ["concept1"], "analyse": "...", "priorite": "..."}
"""


def build_rag_context(course_id: int, query: str, top_k: int = 5) -> str:
    chunks = search(course_id, query, top_k=top_k) if course_id else search_all_courses(query, top_k=top_k)
    if not chunks:
        return ""
    relevant = [c for c in chunks if c.get("distance", 1.0) < 0.85]
    if not relevant:
        relevant = chunks[:3]
    context = "=== CONTEXTE DU COURS ===\n\n"
    for index, chunk in enumerate(relevant, start=1):
        context += f"[Extrait {index}]\n{chunk['text']}\n\n"
    return context + "========================\n"


def _language_instruction(language: str) -> str:
    if language == "en":
        return "Respond in English unless the user explicitly asks for French."
    return "Reponds en francais sauf si l'etudiant ecrit clairement en anglais."


def _mode_instruction(response_mode: str, language: str) -> str:
    if response_mode == "step_by_step":
        return "Explain the answer step by step with numbered stages." if language == "en" else "Explique la reponse pas a pas avec des etapes numerotees."
    if response_mode == "example":
        return "Prioritize a concrete example before the explanation." if language == "en" else "Donne d'abord un exemple concret, puis l'explication."
    if response_mode == "summary":
        return "Answer with a compact summary, then 3 key takeaways." if language == "en" else "Reponds avec un resume compact, puis 3 idees cles."
    return "Provide a clear pedagogical explanation." if language == "en" else "Fournis une explication pedagogique claire."


def _build_tutor_prompt(language: str = "fr", response_mode: str = "default") -> str:
    return f"{_BASE_TUTOR_PROMPT}\n{_language_instruction(language)}\n{_mode_instruction(response_mode, language)}"


def _call(system: str, messages: List[Dict], max_tokens: int = 1500) -> str:
    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}] + messages,
        temperature=0.7,
    )
    return response.choices[0].message.content


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def chat_with_tutor(messages: List[Dict], course_id: int, user_message: str,
                    stream: bool = False, response_mode: str = "default",
                    language: str = "fr") -> str:
    rag = build_rag_context(course_id, user_message)
    augmented = f"{rag}\n\nQuestion de l'etudiant : {user_message}" if rag else user_message

    msgs = messages.copy()
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1] = {"role": "user", "content": augmented}
    else:
        msgs.append({"role": "user", "content": augmented})

    return _call(_build_tutor_prompt(language, response_mode), msgs, max_tokens=1500)


def generate_quiz(course_id: int, topic: str, num_questions: int = 5,
                  difficulty: str = "medium", language: str = "fr") -> Dict:
    rag = build_rag_context(course_id, topic, top_k=6)
    prompt = (
        f"{rag}\n"
        f"Genere {num_questions} questions QCM sur : \"{topic}\"\n"
        f"Niveau de difficulte : {difficulty}\n"
        f"Langue de sortie : {'anglais' if language == 'en' else 'francais'}\n"
        "Reponds uniquement avec le JSON, sans texte autour."
    )
    raw = _call(QUIZ_SYSTEM_PROMPT, [{"role": "user", "content": prompt}], max_tokens=2200)
    try:
        return _parse_json(raw)
    except Exception as exc:
        print(f"[AI_TUTOR] Quiz JSON parse error: {exc}\nRaw: {raw[:300]}")
        return {"concept": topic, "questions": [], "error": str(exc)}


def generate_targeted_quiz(course_id: int, weak_concepts: List[str], num_questions: int = 3,
                           language: str = "fr") -> List[Dict]:
    quizzes = []
    for concept in weak_concepts[:3]:
        quiz = generate_quiz(course_id, concept, num_questions, "targeted", language=language)
        if quiz.get("questions"):
            quizzes.append(quiz)
    return quizzes


def analyze_weaknesses(wrong_answers: List[Dict], course_id: int, language: str = "fr") -> Dict:
    if not wrong_answers:
        return {"concepts_faibles": [], "analyse": "Aucune erreur.", "priorite": None}

    errors = "\n".join(
        f"- Concept: {item['concept']} | Question: {item['question']} | "
        f"Student: {item['student_answer']} | Correct: {item['correct']}"
        for item in wrong_answers
    )
    rag = build_rag_context(course_id, " ".join(item["concept"] for item in wrong_answers), top_k=3)
    prompt = (
        f"{rag}\nErreurs de l'etudiant :\n{errors}\n"
        f"Langue d'analyse : {'anglais' if language == 'en' else 'francais'}\n"
        "Analyse et retourne uniquement le JSON."
    )
    raw = _call(WEAKNESS_SYSTEM_PROMPT, [{"role": "user", "content": prompt}], max_tokens=900)
    try:
        return _parse_json(raw)
    except Exception:
        return {
            "concepts_faibles": [item["concept"] for item in wrong_answers],
            "analyse": raw,
            "priorite": wrong_answers[0]["concept"],
        }


def explain_concept_step_by_step(course_id: int, concept: str,
                                 student_level: str = "intermediate",
                                 language: str = "fr") -> str:
    rag = build_rag_context(course_id, concept, top_k=5)
    prompt = (
        f"{rag}\nConcept a expliquer : \"{concept}\"\n"
        f"Niveau de l'etudiant : {student_level}\n"
        "Explique et structure la reponse clairement."
    )
    return _call(_build_tutor_prompt(language, "step_by_step"), [{"role": "user", "content": prompt}], max_tokens=1600)


def evaluate_open_answer(question: str, student_answer: str, correct_answer: str, course_id: int) -> Dict:
    prompt = (
        f"Question : {question}\n"
        f"Reponse correcte : {correct_answer}\n"
        f"Reponse de l'etudiant : {student_answer}\n"
        'Evalue et reponds en JSON : {"score": 0.0, "is_correct": true, "feedback": "..."}'
    )
    raw = _call("Tu es un evaluateur pedagogique.", [{"role": "user", "content": prompt}], max_tokens=300)
    try:
        return _parse_json(raw)
    except Exception:
        return {"score": 0.5, "is_correct": False, "feedback": raw}
