"""
StudyBuddy v2 — FastAPI backend (replaces Streamlit)
All AI/DB logic reused from backend/ package unchanged.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from backend.database import init_db
init_db()

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="StudyBuddy", version="2.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ────────────────────────────────────────────────────────────

class LoginBody(BaseModel):
    name: str
    email: str

class ChatBody(BaseModel):
    student_id: int
    course_id: Optional[int] = None
    message: str
    messages: List[dict] = []
    mode: str = "default"
    lang: str = "fr"

class QuizGenBody(BaseModel):
    student_id: int
    course_id: int
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    lang: str = "fr"

class QuizSubmitBody(BaseModel):
    student_id: int
    course_id: int
    answers: List[dict]
    lang: str = "fr"

class CreateCourseBody(BaseModel):
    title: str
    filiere: str = "IA Distribuée"

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/login")
def login(body: LoginBody):
    from backend.database import create_student, get_student_by_email
    student = get_student_by_email(body.email)
    if not student:
        create_student(body.name, body.email)
        student = get_student_by_email(body.email)
    return {"ok": True, "student": student}

# ── Courses ───────────────────────────────────────────────────────────────────

@app.get("/api/courses")
def list_courses():
    from backend.database import get_all_courses_with_files
    return get_all_courses_with_files()

@app.post("/api/courses")
def create_course_endpoint(body: CreateCourseBody):
    from backend.database import create_course
    course_id = create_course(body.title, body.filiere)
    return {"ok": True, "course_id": course_id}

@app.post("/api/courses/{course_id}/files")
async def add_file_to_course(course_id: int, file: UploadFile = File(...)):
    from backend.database import add_course_file, get_course_by_id
    from backend.course_parser import parse_course_file
    from backend.vector_store import add_file_chunks

    course = get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    upload_dir = Path(f"./data/courses/{course_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Use unique filename to avoid conflicts
    safe_name = f"{course_id}_{file.filename}"
    dest = upload_dir / safe_name
    dest.write_bytes(await file.read())

    try:
        parsed = await asyncio.to_thread(parse_course_file, str(dest))
        chunks = parsed["chunks"]
        file_id = await asyncio.to_thread(
            add_course_file, course_id, safe_name, file.filename, len(chunks)
        )
        await asyncio.to_thread(add_file_chunks, course_id, file_id, chunks)
        return {"ok": True, "file_id": file_id, "chunks": len(chunks), "original_name": file.filename}
    except Exception as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/courses/{course_id}/files/{file_id}")
def delete_file_endpoint(course_id: int, file_id: int):
    from backend.database import delete_course_file
    from backend.vector_store import remove_file_chunks
    f = delete_course_file(file_id)
    if not f:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    remove_file_chunks(course_id, file_id)
    # Remove physical file
    dest = Path(f"./data/courses/{course_id}/{f['filename']}")
    dest.unlink(missing_ok=True)
    return {"ok": True}

@app.delete("/api/courses/{course_id}")
def delete_course_endpoint(course_id: int):
    from backend.database import delete_course, get_course_files, delete_course_file
    from backend.vector_store import delete_course_index
    # Delete all files first
    for f in get_course_files(course_id):
        delete_course_file(f["id"])
        dest = Path(f"./data/courses/{course_id}/{f['filename']}")
        dest.unlink(missing_ok=True)
    delete_course_index(course_id)
    delete_course(course_id)
    return {"ok": True}

# ── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(body: ChatBody):
    from backend.ai_tutor import chat_with_tutor
    from backend.database import save_chat_session
    try:
        reply = await asyncio.to_thread(
            chat_with_tutor,
            messages=body.messages,
            course_id=body.course_id,
            user_message=body.message,
            response_mode=body.mode,
            language=body.lang,
        )
    except Exception as e:
        reply = f"⚠️ Erreur interne : {e}"
    new_msgs = body.messages + [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": reply},
    ]
    try:
        await asyncio.to_thread(save_chat_session, body.student_id, body.course_id, new_msgs)
    except Exception as e:
        print(f"[Chat] Avertissement sauvegarde session : {e}")
    return {"reply": reply, "messages": new_msgs}

@app.get("/api/chat/history/{student_id}")
def chat_history(student_id: int, course_id: Optional[int] = None):
    from backend.database import get_latest_chat_session
    session = get_latest_chat_session(student_id, course_id)
    return session or {"messages": []}

# ── Quiz ──────────────────────────────────────────────────────────────────────

@app.post("/api/quiz/generate")
async def quiz_generate(body: QuizGenBody):
    from backend.ai_tutor import generate_quiz
    return await asyncio.to_thread(
        generate_quiz,
        course_id=body.course_id,
        topic=body.topic,
        num_questions=body.num_questions,
        difficulty=body.difficulty,
        language=body.lang,
    )

@app.post("/api/quiz/submit")
async def quiz_submit(body: QuizSubmitBody):
    from backend.database import save_quiz_result
    from backend.ai_tutor import analyze_weaknesses
    wrong = []
    for a in body.answers:
        await asyncio.to_thread(
            save_quiz_result,
            body.student_id, body.course_id,
            a["concept"], a["question"],
            a["student_answer"], a["correct_answer"],
            a["is_correct"], 1.0 if a["is_correct"] else 0.0,
        )
        if not a["is_correct"]:
            wrong.append(a)
    total = len(body.answers)
    correct = sum(1 for a in body.answers if a["is_correct"])
    analysis = await asyncio.to_thread(analyze_weaknesses, wrong, body.course_id, body.lang) if wrong else None
    return {
        "correct": correct,
        "total": total,
        "pct": round(correct / total * 100) if total else 0,
        "analysis": analysis,
    }

# ── Dashboard & Progress ──────────────────────────────────────────────────────

@app.get("/api/dashboard/{student_id}")
def dashboard(student_id: int):
    from backend.database import (
        get_student_stats, get_course_progress,
        get_recent_activity, get_recommended_actions, get_weaknesses,
    )
    return {
        "stats": get_student_stats(student_id),
        "progress": get_course_progress(student_id),
        "activity": get_recent_activity(student_id, 8),
        "recommendations": get_recommended_actions(student_id),
        "weaknesses": get_weaknesses(student_id)[:5],
    }

@app.get("/api/progress/{student_id}")
def progress(student_id: int):
    from backend.database import get_student_stats, get_course_progress, get_weaknesses
    return {
        "stats": get_student_stats(student_id),
        "progress": get_course_progress(student_id),
        "weaknesses": get_weaknesses(student_id),
    }

# ── SPA serving ───────────────────────────────────────────────────────────────

_static = Path(__file__).parent / "static"
_static.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(_static)), name="static")

@app.get("/{_:path}", response_class=HTMLResponse, include_in_schema=False)
def spa(_: str = ""):
    f = _static / "index.html"
    if f.exists():
        return HTMLResponse(f.read_text("utf-8"))
    return HTMLResponse("<h1>Frontend not built yet — static/index.html missing</h1>", 404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
