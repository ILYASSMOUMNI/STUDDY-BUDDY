# backend/ai_tutor.py
# Moteur IA — OpenAI (GPT-4o / GPT-4o-mini) + RAG

import os
import json
import re
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from backend.vector_store import search, search_all_courses

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FILIERE = os.getenv("FILIERE", "IA & Data Science")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TUTOR_SYSTEM_PROMPT = f"""Tu es StudyBuddy, un tuteur IA spécialisé en {FILIERE}.
Tu aides les étudiants à comprendre leurs cours de manière progressive et pédagogique.

Règles :
1. Base TOUJOURS tes explications sur le contexte du cours fourni.
2. Explique étape par étape avec des exemples concrets.
3. Adapte ton niveau si l'étudiant est perdu.
4. Pose des questions de vérification à la fin.
5. Réponds en français sauf si l'étudiant écrit en anglais.
6. Si l'étudiant ne comprend pas, reformule avec une analogie différente.
"""

QUIZ_SYSTEM_PROMPT = f"""Tu es un générateur de quiz pédagogique pour la filière {FILIERE}.
Tu génères des QCM basés STRICTEMENT sur le contenu du cours fourni.

Réponds TOUJOURS en JSON valide :
{{
  "concept": "nom du concept",
  "questions": [
    {{
      "id": 1,
      "question": "texte",
      "choices": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_index": 0,
      "correct_answer": "A) ...",
      "explanation": "explication courte"
    }}
  ]
}}
Sans markdown ni backticks.
"""

WEAKNESS_SYSTEM_PROMPT = """Tu es un analyseur pédagogique. Identifie les lacunes.
Réponds UNIQUEMENT en JSON :
{"concepts_faibles": [...], "analyse": "...", "priorite": "..."}
"""


def build_rag_context(course_id: int, query: str, top_k: int = 5) -> str:
    chunks = search(course_id, query, top_k=top_k) if course_id else search_all_courses(query, top_k=top_k)
    if not chunks:
        return ""
    context = "=== CONTEXTE DU COURS ===\n\n"
    for i, c in enumerate(chunks, 1):
        context += f"[Extrait {i}]\n{c['text']}\n\n"
    return context + "========================\n"


def _call(system: str, messages: List[Dict], max_tokens: int = 1500) -> str:
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}] + messages,
        temperature=0.7
    )
    return resp.choices[0].message.content


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def chat_with_tutor(messages: List[Dict], course_id: int, user_message: str, stream: bool = False) -> str:
    rag = build_rag_context(course_id, user_message)
    augmented = f"{rag}\n\nQuestion de l'étudiant : {user_message}" if rag else user_message
    msgs = messages.copy()
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1] = {"role": "user", "content": augmented}
    else:
        msgs.append({"role": "user", "content": augmented})
    return _call(TUTOR_SYSTEM_PROMPT, msgs, 1500)


def generate_quiz(course_id: int, topic: str, num_questions: int = 5, difficulty: str = "moyen") -> Dict:
    rag = build_rag_context(course_id, topic, top_k=6)
    prompt = f"{rag}\nGénère {num_questions} QCM sur : \"{topic}\"\nDifficulté : {difficulty}\nJSON uniquement."
    raw = _call(QUIZ_SYSTEM_PROMPT, [{"role": "user", "content": prompt}], 2000)
    try:
        return _parse_json(raw)
    except Exception as e:
        return {"concept": topic, "questions": [], "error": str(e)}


def generate_targeted_quiz(course_id: int, weak_concepts: List[str], num_questions: int = 3) -> List[Dict]:
    return [q for c in weak_concepts[:3]
            for q in [generate_quiz(course_id, c, num_questions, "ciblé")]
            if q.get("questions")]


def analyze_weaknesses(wrong_answers: List[Dict], course_id: int) -> Dict:
    if not wrong_answers:
        return {"concepts_faibles": [], "analyse": "Aucune erreur.", "priorite": None}
    errors = "\n".join([f"- {w['concept']}: {w['question']} | Étudiant: {w['student_answer']} | Correcte: {w['correct']}" for w in wrong_answers])
    rag = build_rag_context(course_id, " ".join([w["concept"] for w in wrong_answers]), top_k=3)
    prompt = f"{rag}\nErreurs :\n{errors}\nAnalyse et JSON uniquement."
    raw = _call(WEAKNESS_SYSTEM_PROMPT, [{"role": "user", "content": prompt}], 800)
    try:
        return _parse_json(raw)
    except Exception:
        return {"concepts_faibles": [w["concept"] for w in wrong_answers], "analyse": raw, "priorite": None}


def explain_concept_step_by_step(course_id: int, concept: str, student_level: str = "débutant") -> str:
    rag = build_rag_context(course_id, concept, top_k=5)
    prompt = f"{rag}\nConcept : \"{concept}\"\nNiveau : {student_level}\nExplique pas à pas."
    return _call(TUTOR_SYSTEM_PROMPT, [{"role": "user", "content": prompt}], 1500)


def evaluate_open_answer(question: str, student_answer: str, correct_answer: str, course_id: int) -> Dict:
    prompt = f"Question: {question}\nCorrecte: {correct_answer}\nÉtudiant: {student_answer}\nJSON: {{\"score\":0.0-1.0,\"is_correct\":bool,\"feedback\":\"...\"}}"
    raw = _call("Évaluateur pédagogique.", [{"role": "user", "content": prompt}], 300)
    try:
        return _parse_json(raw)
    except Exception:
        return {"score": 0.5, "is_correct": False, "feedback": raw}
