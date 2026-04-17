"""SQLite helpers for StudyBuddy."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./data/studybuddy.db")


def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialise toutes les tables au premier lancement."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            filiere TEXT NOT NULL,
            num_chunks INTEGER DEFAULT 0,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            messages TEXT DEFAULT '[]',
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            concept TEXT NOT NULL,
            question TEXT NOT NULL,
            student_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            score REAL DEFAULT 0.0,
            taken_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS weaknesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            concept TEXT NOT NULL,
            fail_count INTEGER DEFAULT 1,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    conn.commit()
    conn.close()


def _json_dumps(value):
    return json.dumps(value, ensure_ascii=False)


def _json_loads(raw):
    try:
        return json.loads(raw or "[]")
    except Exception:
        return []


def create_student(name: str, email: str) -> int:
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO students (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        c.execute("SELECT id FROM students WHERE email = ?", (email,))
        row = c.fetchone()
        return row["id"] if row else -1
    finally:
        conn.close()


def get_student_by_email(email: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_course(title: str, filename: str, filiere: str, num_chunks: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO courses (title, filename, filiere, num_chunks) VALUES (?, ?, ?, ?)",
        (title, filename, filiere, num_chunks),
    )
    conn.commit()
    course_id = c.lastrowid
    conn.close()
    return course_id


def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses ORDER BY uploaded_at DESC, id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_course_by_id(course_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_chat_session(student_id: int, course_id: int | None, messages):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id
        FROM chat_sessions
        WHERE student_id = ?
          AND ((course_id = ?) OR (course_id IS NULL AND ? IS NULL))
        ORDER BY started_at DESC, id DESC
        LIMIT 1
    """, (student_id, course_id, course_id))
    row = c.fetchone()
    payload = _json_dumps(messages)

    if row:
        c.execute("UPDATE chat_sessions SET messages = ? WHERE id = ?", (payload, row["id"]))
        session_id = row["id"]
    else:
        c.execute("""
            INSERT INTO chat_sessions (student_id, course_id, messages)
            VALUES (?, ?, ?)
        """, (student_id, course_id, payload))
        session_id = c.lastrowid

    conn.commit()
    conn.close()
    return session_id


def get_latest_chat_session(student_id: int, course_id: int = None):
    conn = get_connection()
    c = conn.cursor()

    if course_id is None:
        c.execute("""
            SELECT cs.*, c.title AS course_title
            FROM chat_sessions cs
            LEFT JOIN courses c ON cs.course_id = c.id
            WHERE cs.student_id = ?
            ORDER BY cs.started_at DESC, cs.id DESC
            LIMIT 1
        """, (student_id,))
    else:
        c.execute("""
            SELECT cs.*, c.title AS course_title
            FROM chat_sessions cs
            LEFT JOIN courses c ON cs.course_id = c.id
            WHERE cs.student_id = ? AND cs.course_id = ?
            ORDER BY cs.started_at DESC, cs.id DESC
            LIMIT 1
        """, (student_id, course_id))

    row = c.fetchone()
    conn.close()
    if not row:
        return None

    result = dict(row)
    result["messages"] = _json_loads(result.get("messages"))
    return result


def save_quiz_result(student_id, course_id, concept, question, student_answer, correct_answer, is_correct, score):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO quiz_results
        (student_id, course_id, concept, question, student_answer, correct_answer, is_correct, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, course_id, concept, question, student_answer, correct_answer, int(is_correct), score))
    conn.commit()
    conn.close()

    if not is_correct:
        _increment_weakness(student_id, course_id, concept)


def _increment_weakness(student_id, course_id, concept):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id FROM weaknesses
        WHERE student_id = ? AND course_id = ? AND concept = ?
    """, (student_id, course_id, concept))
    row = c.fetchone()

    if row:
        c.execute("""
            UPDATE weaknesses
            SET fail_count = fail_count + 1, last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (row["id"],))
    else:
        c.execute("""
            INSERT INTO weaknesses (student_id, course_id, concept)
            VALUES (?, ?, ?)
        """, (student_id, course_id, concept))

    conn.commit()
    conn.close()


def get_weaknesses(student_id: int, course_id: int = None):
    conn = get_connection()
    c = conn.cursor()
    if course_id:
        c.execute("""
            SELECT concept, fail_count, course_id, last_seen
            FROM weaknesses
            WHERE student_id = ? AND course_id = ?
            ORDER BY fail_count DESC, last_seen DESC
        """, (student_id, course_id))
    else:
        c.execute("""
            SELECT concept, SUM(fail_count) AS fail_count, MAX(last_seen) AS last_seen
            FROM weaknesses
            WHERE student_id = ?
            GROUP BY concept
            ORDER BY fail_count DESC, last_seen DESC
        """, (student_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_stats(student_id: int):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS total FROM quiz_results WHERE student_id = ?", (student_id,))
    total = c.fetchone()["total"]

    c.execute("SELECT COUNT(*) AS correct FROM quiz_results WHERE student_id = ? AND is_correct = 1", (student_id,))
    correct = c.fetchone()["correct"]

    c.execute("""
        SELECT c.title, COUNT(qr.id) AS attempts, SUM(qr.is_correct) AS correct_count
        FROM quiz_results qr
        JOIN courses c ON qr.course_id = c.id
        WHERE qr.student_id = ?
        GROUP BY c.id
    """, (student_id,))
    by_course = [dict(r) for r in c.fetchall()]

    conn.close()
    return {
        "total_questions": total,
        "correct_answers": correct,
        "score_global": round((correct / total * 100) if total > 0 else 0, 1),
        "by_course": by_course,
    }


def _get_last_course_score(conn, student_id: int, course_id: int):
    c = conn.cursor()
    c.execute("""
        SELECT ROUND(SUM(is_correct) * 100.0 / COUNT(*), 1) AS score_pct
        FROM quiz_results
        WHERE student_id = ? AND course_id = ? AND taken_at = (
            SELECT MAX(taken_at)
            FROM quiz_results
            WHERE student_id = ? AND course_id = ?
        )
    """, (student_id, course_id, student_id, course_id))
    row = c.fetchone()
    return row["score_pct"] if row and row["score_pct"] is not None else None


def get_course_progress(student_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT
            c.id,
            c.title,
            c.filename,
            c.num_chunks,
            c.uploaded_at,
            COUNT(qr.id) AS attempts,
            COALESCE(SUM(qr.is_correct), 0) AS correct_count,
            MAX(qr.taken_at) AS last_taken_at,
            COALESCE((
                SELECT COUNT(*)
                FROM weaknesses w
                WHERE w.student_id = ? AND w.course_id = c.id
            ), 0) AS weakness_count
        FROM courses c
        LEFT JOIN quiz_results qr
            ON qr.course_id = c.id AND qr.student_id = ?
        GROUP BY c.id
        ORDER BY c.uploaded_at DESC, c.id DESC
    """, (student_id, student_id))
    rows = [dict(r) for r in c.fetchall()]

    for row in rows:
        attempts = row["attempts"] or 0
        correct = row["correct_count"] or 0
        row["score_pct"] = round((correct / attempts * 100) if attempts else 0, 1)
        row["last_score"] = _get_last_course_score(conn, student_id, row["id"])

    conn.close()
    return rows


def get_recent_activity(student_id: int, limit: int = 10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT *
        FROM (
            SELECT
                'quiz' AS activity_type,
                qr.taken_at AS created_at,
                qr.course_id,
                c.title AS course_title,
                qr.concept,
                qr.is_correct,
                NULL AS session_id
            FROM quiz_results qr
            LEFT JOIN courses c ON qr.course_id = c.id
            WHERE qr.student_id = ?

            UNION ALL

            SELECT
                'chat' AS activity_type,
                cs.started_at AS created_at,
                cs.course_id,
                c.title AS course_title,
                NULL AS concept,
                NULL AS is_correct,
                cs.id AS session_id
            FROM chat_sessions cs
            LEFT JOIN courses c ON cs.course_id = c.id
            WHERE cs.student_id = ?
        )
        ORDER BY created_at DESC
        LIMIT ?
    """, (student_id, student_id, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_recommended_actions(student_id: int):
    actions = []

    latest_chat = get_latest_chat_session(student_id)
    if latest_chat and latest_chat.get("course_id"):
        actions.append({
            "type": "resume_chat",
            "course_id": latest_chat["course_id"],
            "course_title": latest_chat.get("course_title"),
            "session_id": latest_chat["id"],
        })

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT w.course_id, c.title AS course_title, w.concept, w.fail_count
        FROM weaknesses w
        LEFT JOIN courses c ON w.course_id = c.id
        WHERE w.student_id = ?
        ORDER BY w.fail_count DESC, w.last_seen DESC
        LIMIT 1
    """, (student_id,))
    weakness = c.fetchone()
    conn.close()

    if weakness:
        actions.append({
            "type": "targeted_quiz",
            "course_id": weakness["course_id"],
            "course_title": weakness["course_title"],
            "concept": weakness["concept"],
            "fail_count": weakness["fail_count"],
        })
        actions.append({
            "type": "review_concept",
            "course_id": weakness["course_id"],
            "course_title": weakness["course_title"],
            "concept": weakness["concept"],
            "fail_count": weakness["fail_count"],
        })

    progress = get_course_progress(student_id)
    least_started = next((row for row in progress if row["attempts"] == 0), None)
    if least_started:
        actions.append({
            "type": "start_quiz",
            "course_id": least_started["id"],
            "course_title": least_started["title"],
        })

    return actions


if __name__ == "__main__":
    init_db()
