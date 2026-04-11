# backend/database.py
# Gestion SQLite : étudiants, sessions, résultats quiz, lacunes

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./data/studybuddy.db")


def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise toutes les tables au premier lancement."""
    conn = get_connection()
    c = conn.cursor()

    # Table étudiants
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table cours uploadés
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

    # Table sessions de chat
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

    # Table résultats de quiz
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

    # Table lacunes détectées
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
    print("✅ Base de données initialisée.")


# ──────────────────────────────────────────────
#  Helpers étudiants
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
#  Helpers cours
# ──────────────────────────────────────────────

def save_course(title: str, filename: str, filiere: str, num_chunks: int) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO courses (title, filename, filiere, num_chunks) VALUES (?, ?, ?, ?)",
        (title, filename, filiere, num_chunks)
    )
    conn.commit()
    lid = c.lastrowid
    conn.close()
    return lid


def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses ORDER BY uploaded_at DESC")
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


# ──────────────────────────────────────────────
#  Helpers quiz & lacunes
# ──────────────────────────────────────────────

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
        WHERE student_id=? AND course_id=? AND concept=?
    """, (student_id, course_id, concept))
    row = c.fetchone()
    if row:
        c.execute("""
            UPDATE weaknesses SET fail_count = fail_count + 1, last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (row["id"],))
    else:
        c.execute("""
            INSERT INTO weaknesses (student_id, course_id, concept) VALUES (?, ?, ?)
        """, (student_id, course_id, concept))
    conn.commit()
    conn.close()


def get_weaknesses(student_id: int, course_id: int = None):
    conn = get_connection()
    c = conn.cursor()
    if course_id:
        c.execute("""
            SELECT concept, fail_count FROM weaknesses
            WHERE student_id=? AND course_id=?
            ORDER BY fail_count DESC
        """, (student_id, course_id))
    else:
        c.execute("""
            SELECT concept, SUM(fail_count) as fail_count FROM weaknesses
            WHERE student_id=?
            GROUP BY concept ORDER BY fail_count DESC
        """, (student_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_stats(student_id: int):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) as total FROM quiz_results WHERE student_id=?", (student_id,))
    total = c.fetchone()["total"]

    c.execute("SELECT COUNT(*) as correct FROM quiz_results WHERE student_id=? AND is_correct=1", (student_id,))
    correct = c.fetchone()["correct"]

    c.execute("""
        SELECT c.title, COUNT(qr.id) as attempts,
               SUM(qr.is_correct) as correct_count
        FROM quiz_results qr
        JOIN courses c ON qr.course_id = c.id
        WHERE qr.student_id=?
        GROUP BY c.id
    """, (student_id,))
    by_course = [dict(r) for r in c.fetchall()]

    conn.close()
    return {
        "total_questions": total,
        "correct_answers": correct,
        "score_global": round((correct / total * 100) if total > 0 else 0, 1),
        "by_course": by_course
    }


if __name__ == "__main__":
    init_db()
