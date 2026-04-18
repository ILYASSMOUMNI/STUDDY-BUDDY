"""
Service Email Gmail — Couche 4 : Interfaçage Cloud.
Envoie des rapports de quiz et des résumés hebdomadaires aux étudiants via SMTP Gmail.
"""

from __future__ import annotations

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

_GMAIL_USER     = os.getenv("GMAIL_USER", "")
_GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
_FROM_NAME      = "StudyBuddy EMSI"


def is_configured() -> bool:
    """Vérifie si les credentials Gmail sont configurés."""
    return bool(_GMAIL_USER and _GMAIL_PASSWORD)


# ── Envoi bas niveau ──────────────────────────────────────────────────────────

def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str = "",
) -> Dict:
    """
    Envoie un email via SMTP Gmail SSL.
    Retourne {"success": bool, "error": str|None}.
    """
    if not is_configured():
        return {
            "success": False,
            "error": "Gmail non configuré — ajoutez GMAIL_USER et GMAIL_APP_PASSWORD dans .env",
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{_FROM_NAME} <{_GMAIL_USER}>"
        msg["To"]      = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(_GMAIL_USER, _GMAIL_PASSWORD)
            server.sendmail(_GMAIL_USER, to_email, msg.as_string())

        print(f"[Email] ✅ Envoyé à {to_email} — {subject}")
        return {"success": True, "to": to_email}

    except smtplib.SMTPAuthenticationError:
        err = "Authentification Gmail échouée — vérifiez GMAIL_APP_PASSWORD"
        print(f"[Email] ❌ {err}")
        return {"success": False, "error": err}
    except Exception as e:
        print(f"[Email] ❌ Erreur : {e}")
        return {"success": False, "error": str(e)}


# ── Templates HTML ────────────────────────────────────────────────────────────

def _quiz_report_html(
    student_name: str,
    course_title: str,
    score: float,
    total: int,
    correct: int,
    weak_concepts: List[str],
) -> str:
    color   = "#059669" if score >= 70 else "#d97706" if score >= 50 else "#dc2626"
    verdict = "Excellent !" if score >= 70 else "En progression" if score >= 50 else "À améliorer"

    concepts_html = (
        "".join(f'<li style="color:#7c2d12;">{c}</li>' for c in weak_concepts)
        if weak_concepts
        else '<li style="color:#15803d;">Aucun point faible détecté — bravo !</li>'
    )

    weak_block = f"""
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:16px;margin:20px 0;">
      <p style="margin:0 0 8px;font-weight:700;color:#9a3412;">📚 Concepts à revoir :</p>
      <ul style="margin:0;padding-left:20px;">{concepts_html}</ul>
    </div>""" if weak_concepts else ""

    date_str = datetime.now().strftime("%d/%m/%Y")

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rapport Quiz — StudyBuddy</title></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;margin:0;padding:24px;">
<div style="max-width:600px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;
            box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <div style="background:linear-gradient(135deg,#059669,#7C3AED);padding:36px;text-align:center;">
    <div style="width:48px;height:48px;background:rgba(255,255,255,0.2);border-radius:12px;
                display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">
      <span style="color:#fff;font-size:1.5rem;font-weight:800;">S</span>
    </div>
    <h1 style="color:#fff;margin:0;font-size:1.6rem;font-weight:800;">StudyBuddy</h1>
    <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;font-size:0.9rem;">Rapport de Quiz</p>
  </div>

  <div style="padding:36px;">
    <p style="font-size:1rem;color:#334155;">Bonjour <strong>{student_name}</strong>,</p>
    <p style="color:#64748b;">Voici ton résultat pour le quiz sur <strong>{course_title}</strong> :</p>

    <div style="text-align:center;background:#f8fafc;border-radius:14px;padding:28px;margin:24px 0;">
      <div style="font-size:3.5rem;font-weight:900;color:{color};letter-spacing:-2px;">{score:.0f}%</div>
      <div style="color:#64748b;margin-top:6px;font-size:0.95rem;">
        {correct} / {total} réponses correctes · <strong style="color:{color};">{verdict}</strong>
      </div>
    </div>

    {weak_block}

    <p style="color:#64748b;font-size:0.875rem;text-align:center;margin-top:28px;">
      Connecte-toi sur StudyBuddy pour continuer à apprendre et améliorer ton score !
    </p>
  </div>

  <div style="background:#f8fafc;padding:16px;text-align:center;
              color:#94a3b8;font-size:0.75rem;border-top:1px solid #e2e8f0;">
    StudyBuddy EMSI · {date_str} · Généré automatiquement
  </div>
</div>
</body></html>"""


def _weekly_summary_html(
    student_name: str,
    score: float,
    total: int,
    correct: int,
    weaknesses: List[Dict],
    progress_report: str,
) -> str:
    color = "#059669" if score >= 70 else "#d97706" if score >= 50 else "#dc2626"
    weak_items = "".join(
        f'<li><strong>{w.get("concept","?")}</strong> — {w.get("fail_count",1)}× raté</li>'
        for w in weaknesses[:5]
    )
    date_str = datetime.now().strftime("%d/%m/%Y")

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;padding:24px;">
<div style="max-width:600px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;
            box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <div style="background:linear-gradient(135deg,#059669,#7C3AED);padding:36px;text-align:center;">
    <h1 style="color:#fff;margin:0;font-size:1.5rem;">📊 Rapport Hebdomadaire</h1>
    <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;">StudyBuddy EMSI</p>
  </div>

  <div style="padding:36px;">
    <p>Bonjour <strong>{student_name}</strong>,</p>
    <p style="color:#64748b;">Voici ton résumé d'apprentissage de la semaine :</p>

    <div style="display:flex;gap:12px;margin:24px 0;">
      <div style="flex:1;text-align:center;background:#f0fdf4;border-radius:12px;padding:20px;">
        <div style="font-size:2.2rem;font-weight:800;color:#059669;">{total}</div>
        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">Questions répondues</div>
      </div>
      <div style="flex:1;text-align:center;background:#f0fdf4;border-radius:12px;padding:20px;">
        <div style="font-size:2.2rem;font-weight:800;color:{color};">{score}%</div>
        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">Score global</div>
      </div>
      <div style="flex:1;text-align:center;background:#f0fdf4;border-radius:12px;padding:20px;">
        <div style="font-size:2.2rem;font-weight:800;color:#059669;">{correct}</div>
        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">Réponses correctes</div>
      </div>
    </div>

    {f'<div style="background:#fff7ed;border-radius:10px;padding:16px;margin:16px 0;"><p style="font-weight:700;margin:0 0 8px;color:#9a3412;">⚠️ À revoir :</p><ul style="margin:0;color:#7c2d12;">{weak_items}</ul></div>' if weak_items else ''}

    <div style="background:#f8fafc;border-radius:10px;padding:16px;margin-top:16px;">
      <pre style="font-family:monospace;font-size:0.8rem;white-space:pre-wrap;margin:0;color:#475569;">{progress_report}</pre>
    </div>
  </div>

  <div style="background:#f8fafc;padding:16px;text-align:center;color:#94a3b8;font-size:0.75rem;border-top:1px solid #e2e8f0;">
    StudyBuddy EMSI · {date_str}
  </div>
</div>
</body></html>"""


# ── API publique ──────────────────────────────────────────────────────────────

def send_quiz_report(
    student_email: str,
    student_name: str,
    course_title: str,
    score: float,
    total: int,
    correct: int,
    weak_concepts: Optional[List[str]] = None,
) -> Dict:
    """Envoie un rapport de résultat de quiz par email."""
    if not is_configured():
        return {"success": False, "error": "Gmail non configuré"}

    weak_concepts = weak_concepts or []
    verdict = "Excellent" if score >= 70 else "En progression" if score >= 50 else "À améliorer"
    subject = f"[StudyBuddy] Résultat quiz — {course_title} : {score:.0f}% ({verdict})"
    html = _quiz_report_html(student_name, course_title, score, total, correct, weak_concepts)
    text = (
        f"Bonjour {student_name},\n\n"
        f"Quiz : {course_title}\n"
        f"Score : {score:.0f}% ({correct}/{total})\n"
        f"Verdict : {verdict}\n\n"
        "Connecte-toi sur StudyBuddy pour continuer."
    )
    return send_email(student_email, subject, html, text)


def send_weekly_summary(
    student_email: str,
    student_name: str,
    stats: Dict,
    weaknesses: List[Dict],
    progress_report: str,
) -> Dict:
    """Envoie un résumé hebdomadaire de progression."""
    if not is_configured():
        return {"success": False, "error": "Gmail non configuré"}

    score   = stats.get("score_global", 0)
    total   = stats.get("total_questions", 0)
    correct = stats.get("correct_answers", 0)

    subject = f"[StudyBuddy] Ton rapport hebdomadaire — Score : {score}%"
    html = _weekly_summary_html(student_name, score, total, correct, weaknesses, progress_report)
    text = (
        f"Bonjour {student_name},\n\n"
        f"Score global : {score}%\n"
        f"Questions répondues : {total}\n\n"
        f"{progress_report}"
    )
    return send_email(student_email, subject, html, text)
