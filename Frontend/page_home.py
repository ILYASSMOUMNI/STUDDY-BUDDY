# frontend/page_home.py

import streamlit as st
from backend.database import get_student_stats, get_weaknesses, get_course_progress
from frontend.design_system import C, page_title, kpi_card, badge, spacer


def render_home():
    sid             = st.session_state.student_id
    stats           = get_student_stats(sid)
    weak            = get_weaknesses(sid)
    course_progress = get_course_progress(sid)
    name            = st.session_state.student_name

    # ── Page title ────────────────────────────────────────────
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        page_title("Dashboard", f"Welcome back, {name}. Here's your learning summary.")
    with col_btn:
        spacer(28)
        if st.button("+ Upload course", type="primary"):
            st.session_state.current_page = "courses"
            st.rerun()

    # ── KPI row ───────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    score = stats["score_global"]

    with k1: kpi_card(str(len(course_progress)), "Total courses", accent_color=C["indigo"])
    with k2: kpi_card(str(stats["total_questions"]), "Questions answered", accent_color=C["blue"])
    with k3: kpi_card(f"{score}%", "Global score",
                      delta=("+good" if score >= 70 else "needs work"),
                      delta_positive=(score >= 70),
                      accent_color=C["green"] if score >= 70 else C["orange"] if score >= 50 else C["red"])
    with k4: kpi_card(str(len(weak)), "Weak concepts",
                      accent_color=C["red"] if weak else C["green"])

    spacer(24)

    # ── Main content + right panel ────────────────────────────
    col_main, col_right = st.columns([2.4, 1], gap="large")

    with col_main:
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;overflow:hidden;
            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:18px 24px;border-bottom:1px solid {C["border"]};
                background:linear-gradient(135deg, rgba(125,211,252,0.05), rgba(200,160,240,0.05));">
        <span style="font-size:1rem;font-weight:700;color:{C["text"]};">📚 Active courses</span>
    </div>
""", unsafe_allow_html=True)

        if not course_progress:
            st.markdown(f"""
<div style="padding:40px 24px;text-align:center;color:{C["text_3"]};font-size:0.9rem;">
    <p style="margin-bottom:8px;">📦 No courses indexed yet</p>
    <p>Upload your first course to get started.</p>
</div>""", unsafe_allow_html=True)
        else:
            for i, course in enumerate(course_progress[:5]):
                sep      = f"border-top:1px solid {C['border']};" if i > 0 else ""
                pct      = course.get("score_pct", 0)
                attempts = course.get("attempts", 0)
                bar_color = (C["green"] if pct >= 70
                             else C["orange"] if pct >= 40 and attempts > 0
                             else C["red"] if attempts > 0
                             else C["border_dark"])
                label = f"{attempts} attempt(s) · {pct}%" if attempts > 0 else "Not started yet"

                st.markdown(f"""
<div style="padding:16px 24px;{sep}display:flex;align-items:center;gap:16px;">
    <div style="flex:1;min-width:0;">
        <div style="font-weight:600;font-size:0.9rem;color:{C["text"]};margin-bottom:4px;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            {course['title']}
        </div>
        <div style="font-size:0.8rem;color:{C["text_3"]};margin-bottom:8px;">{label}</div>
        <div style="height:4px;border-radius:100px;background:{C["border"]};overflow:hidden;">
            <div style="height:4px;width:{pct}%;background:{bar_color};
                        border-radius:100px;transition:width 0.3s ease;"></div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

                ca, cb = st.columns(2)
                with ca:
                    if st.button("💬 Chat", key=f"hc_{course['id']}",
                                 use_container_width=True, type="secondary"):
                        st.session_state.selected_course_id = course["id"]
                        st.session_state.current_page = "chat"
                        st.session_state.chat_messages = []
                        st.session_state.chat_display  = []
                        st.rerun()
                with cb:
                    if st.button("❓ Quiz", key=f"hq_{course['id']}",
                                 use_container_width=True, type="secondary"):
                        st.session_state.selected_course_id = course["id"]
                        st.session_state.current_page = "quiz"
                        st.rerun()
                spacer(2)

        st.markdown("</div>", unsafe_allow_html=True)
        spacer(28)

        # How it works
        st.markdown(f"""
<p style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:14px;">
    ✨ How it works
</p>""", unsafe_allow_html=True)

        steps = [
            ("01", "Upload", "PDF or DOCX courses"),
            ("02", "Chat",   "Ask the AI tutor"),
            ("03", "Quiz",   "Test yourself"),
            ("04", "Review", "Improve weak areas"),
        ]
        for col, (num, title, desc) in zip(st.columns(4), steps):
            with col:
                st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:18px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                color:{C["indigo"]};margin-bottom:8px;font-weight:700;">{num}</div>
    <div style="font-weight:700;font-size:0.85rem;color:{C["text"]};margin-bottom:6px;">{title}</div>
    <div style="font-size:0.8rem;color:{C["text_3"]};line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

    with col_right:
        # Weak concepts panel
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <div style="padding:18px 20px;border-bottom:1px solid {C["border"]};
                background:linear-gradient(135deg, rgba(248,113,113,0.05), rgba(251,191,36,0.05));">
        <span style="font-size:1rem;font-weight:700;color:{C["text"]};">⚠️ Weak concepts</span>
    </div>
""", unsafe_allow_html=True)

        if not weak:
            st.markdown(f"""
<div style="padding:32px 20px;text-align:center;">
    {badge("✓ All good", "green")}
    <p style="font-size:0.85rem;color:{C["text_3"]};margin-top:12px;line-height:1.6;">
        No weak concepts detected.<br>Complete a quiz to get feedback.
    </p>
</div>""", unsafe_allow_html=True)
        else:
            for w in weak[:7]:
                color = "red" if w["fail_count"] >= 3 else "orange" if w["fail_count"] >= 2 else "gray"
                st.markdown(f"""
<div style="padding:12px 20px;border-bottom:1px solid {C["border"]};
            display:flex;align-items:center;justify-content:space-between;">
    <span style="font-size:0.85rem;color:{C["text"]};font-weight:500;">{w["concept"]}</span>
    {badge(f'{w["fail_count"]}x failed', color)}
</div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        spacer(18)

        if weak:
            if st.button("🎯 Targeted quiz", use_container_width=True, type="primary"):
                st.session_state.current_page = "quiz"
                st.rerun()
        spacer(18)

        # Overall score card
        verdict = "Strong" if score >= 70 else "Developing" if score >= 50 else "Needs work"
        st.markdown(f"""
<div style="background:linear-gradient(135deg, {C["indigo"]}, {C["tertiary"]});
            border-radius:12px;padding:22px 20px;color:{C["text_inv"]};
            box-shadow:0 8px 16px rgba(125,211,252,0.2);">
    <p style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;
              text-transform:uppercase;opacity:0.8;margin-bottom:10px;">📊 Overall</p>
    <p style="font-size:1.75rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">
        {verdict}</p>
    <p style="font-size:0.85rem;opacity:0.85;margin-bottom:14px;">
        {stats['correct_answers']} / {stats['total_questions']} correct</p>
    <div style="height:4px;border-radius:100px;background:rgba(255,255,255,0.2);">
        <div style="width:{score}%;height:4px;border-radius:100px;
                    background:#fff;box-shadow:0 0 8px rgba(255,255,255,0.4);"></div>
    </div>
    <p style="font-size:0.75rem;opacity:0.7;margin-top:8px;">{score}% success rate</p>
</div>""", unsafe_allow_html=True)
