# frontend/page_quiz.py

import streamlit as st
from backend.database import get_all_courses, save_quiz_result, get_weaknesses
from backend.ai_tutor import generate_quiz, generate_targeted_quiz, analyze_weaknesses
from frontend.design_system import C, page_title, badge, spacer, divider, inline_alert
from frontend.i18n import t


def render_quiz():
    lang    = st.session_state.get("language", "fr")
    courses = get_all_courses()
    if not courses:
        page_title(t("quiz.title", lang))
        inline_alert(t("quiz.no_courses", lang), "info")
        if st.button(t("common.upload_course", lang), type="primary"):
            st.session_state.current_page = "courses"
            st.rerun()
        return

    # ── Auto-launch quick quiz from navigation helper ─────────
    if st.session_state.quiz_data is None and st.session_state.get("quick_quiz_mode"):
        st.session_state.quick_quiz_mode = False
        cid   = st.session_state.selected_course_id or courses[0]["id"]
        topic = st.session_state.get("focus_concept") or courses[0]["title"]
        with st.spinner(t("quiz.generating", lang, count=3, topic=topic)):
            quiz = generate_quiz(cid, topic, 3, "medium", language=lang)
        if quiz.get("questions"):
            _start(quiz, cid)
        else:
            inline_alert(t("quiz.no_questions", lang), "danger")
        return

    if st.session_state.quiz_data is None:
        _setup(courses, lang)
    elif not st.session_state.quiz_submitted:
        _questions(lang)
    else:
        _results(lang)


# ─── SETUP ───────────────────────────────────────────────────

def _setup(courses, lang: str = "fr"):
    col_t, col_b = st.columns([4, 1])
    with col_t:
        page_title(t("quiz.title", lang), t("quiz.subtitle", lang))

    tab1, tab2 = st.tabs([
        f"📝 {t('quiz.tab.standard', lang)}",
        f"🎯 {t('quiz.tab.targeted', lang)}",
    ])

    with tab1:
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:24px;margin-bottom:16px;
            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cmap = {c["title"]: c["id"] for c in courses}
            default_idx = 0
            if st.session_state.get("selected_course_id"):
                for i, c in enumerate(courses):
                    if c["id"] == st.session_state.selected_course_id:
                        default_idx = i; break
            sel       = st.selectbox(t("common.course", lang), list(cmap.keys()), index=default_idx)
            cid       = cmap[sel]
            focus_default = st.session_state.get("focus_concept") or ""
            topic = st.text_input(
                t("common.topic", lang),
                value=focus_default,
                placeholder="E.g. Neural networks, K-means…")
        with c2:
            num_q = st.slider(t("quiz.number", lang), 3, 10, 5)
            diff  = st.select_slider(t("common.difficulty", lang),
                       options=["easy","medium","hard"], value="medium")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(f"▶️ {t('quiz.generate', lang)}", type="primary", use_container_width=True):
            topic_f = topic.strip() or sel
            st.session_state.focus_concept = None
            with st.spinner(t("quiz.generating", lang, count=num_q, topic=topic_f)):
                quiz = generate_quiz(cid, topic_f, num_q, diff, language=lang)
            if quiz.get("questions"):
                _start(quiz, cid)
            else:
                inline_alert(f"{t('quiz.no_questions', lang)} {quiz.get('error','')}", "danger")

    with tab2:
        weak = get_weaknesses(st.session_state.student_id)
        if not weak:
            inline_alert(t("quiz.targeted_empty", lang), "info")
        else:
            st.markdown(f"""
<p style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:12px;">
    {t("quiz.targeted_weaknesses", lang)}
</p>""", unsafe_allow_html=True)
            for w in weak[:6]:
                color = "red" if w["fail_count"] >= 3 else "orange"
                st.markdown(
                    f'{badge(w["concept"], color)}&nbsp;'
                    f'<span style="font-size:0.8rem;color:{C["text_3"]};font-weight:600;">{w["fail_count"]}x</span>',
                    unsafe_allow_html=True)
            spacer(18)

            cw1, cw2 = st.columns(2)
            with cw1:
                cmw = {c["title"]: c["id"] for c in courses}
                sel_w = st.selectbox(t("quiz.reference_course", lang), list(cmw.keys()), key="tw_c")
                cid_w = cmw[sel_w]
            with cw2:
                nq_w = st.slider(t("quiz.questions_per_concept", lang), 2, 5, 3, key="tw_n")
            spacer(10)

            if st.button(f"🎯 {t('quiz.start_targeted', lang)}", type="primary", use_container_width=True):
                concepts = [w["concept"] for w in weak[:3]]
                with st.spinner(t("quiz.building_targeted", lang)):
                    quizzes = generate_targeted_quiz(cid_w, concepts, nq_w, language=lang)
                if quizzes:
                    all_q = []
                    for qz in quizzes:
                        for q in qz.get("questions", []):
                            q["concept"] = qz.get("concept", "")
                            all_q.append(q)
                    _start({"concept": t("quiz.tab.targeted", lang),
                             "questions": all_q, "is_targeted": True}, cid_w)
                else:
                    inline_alert(t("quiz.no_questions", lang), "danger")


def _start(quiz, cid):
    st.session_state.quiz_data              = quiz
    st.session_state.quiz_data["course_id"] = cid
    st.session_state.quiz_answers           = {}
    st.session_state.quiz_submitted         = False
    st.session_state.wrong_answers_session  = []
    st.rerun()


# ─── QUESTIONS ───────────────────────────────────────────────

def _questions(lang: str = "fr"):
    quiz      = st.session_state.quiz_data
    questions = quiz.get("questions", [])
    if not questions:
        st.session_state.quiz_data = None; st.rerun(); return

    total    = len(questions)
    answered = len(st.session_state.quiz_answers)
    is_tgt   = quiz.get("is_targeted", False)

    # Header
    badge_label = t("quiz.badge.targeted", lang) if is_tgt else t("quiz.badge.standard", lang)
    col_info, col_prog = st.columns([2, 1])
    with col_info:
        page_title("Quiz", f"{quiz.get('concept','')} — {badge_label}")
    with col_prog:
        spacer(28)
        st.progress(answered / total if total else 0,
                    text=f"📊 {t('quiz.answered', lang, done=answered, total=total)}")

    # Questions
    for idx, q in enumerate(questions):
        choices = q.get("choices", [])
        concept = q.get("concept", quiz.get("concept", ""))
        current = st.session_state.quiz_answers.get(idx)

        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:22px 24px;margin-bottom:12px;
            box-shadow:0 4px 12px rgba(0,0,0,0.2);
            transition:all 0.2s ease;">
    <div style="display:flex;justify-content:space-between;
                align-items:baseline;margin-bottom:14px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                     color:{C["indigo"]};font-weight:700;letter-spacing:0.05em;">
            Q{idx+1:02d}
        </span>
        {badge(concept, "indigo") if concept else ""}
    </div>
    <p style="font-size:0.95rem;font-weight:500;color:{C["text"]};
              line-height:1.6;margin-bottom:16px;">
        {q['question']}
    </p>
</div>""", unsafe_allow_html=True)

        sel = st.radio(
            f"q{idx}",
            choices,
            index=None if current is None
                  else (choices.index(current) if current in choices else None),
            key=f"r_{idx}",
            label_visibility="collapsed"
        )
        if sel is not None:
            st.session_state.quiz_answers[idx] = sel
        spacer(6)

    divider()
    remaining = total - len(st.session_state.quiz_answers)
    c_msg, c_cancel, c_submit = st.columns([3, 1, 1])
    with c_msg:
        if remaining > 0:
            st.markdown(f"""
<span style="font-size:0.85rem;color:{C["orange"]};font-weight:600;">
    ⚠️ {t("quiz.unanswered", lang, count=remaining)}
</span>""", unsafe_allow_html=True)
    with c_cancel:
        if st.button(f"❌ {t('common.cancel', lang)}", type="secondary", use_container_width=True):
            st.session_state.quiz_data    = None
            st.session_state.quiz_answers = {}
            st.rerun()
    with c_submit:
        lbl = f"✓ {t('quiz.submit', lang)}" if remaining == 0 else f"→ {t('quiz.submit_anyway', lang)}"
        if st.button(lbl, type="primary", use_container_width=True):
            _submit()


# ─── SUBMIT ──────────────────────────────────────────────────

def _submit():
    quiz      = st.session_state.quiz_data
    questions = quiz.get("questions", [])
    wrong     = []
    for idx, q in enumerate(questions):
        sel = st.session_state.quiz_answers.get(idx, "—")
        ok  = sel == q.get("correct_answer", "")
        save_quiz_result(
            student_id=st.session_state.student_id,
            course_id=quiz.get("course_id"),
            concept=q.get("concept", quiz.get("concept","")),
            question=q["question"],
            student_answer=sel,
            correct_answer=q.get("correct_answer",""),
            is_correct=ok,
            score=1.0 if ok else 0.0
        )
        if not ok:
            wrong.append({"question":q["question"],
                          "concept":q.get("concept",""),
                          "student_answer":sel,
                          "correct":q.get("correct_answer",""),
                          "explanation":q.get("explanation","")})
    st.session_state.quiz_submitted        = True
    st.session_state.wrong_answers_session = wrong
    st.rerun()


# ─── RESULTS ─────────────────────────────────────────────────

def _results(lang: str = "fr"):
    quiz      = st.session_state.quiz_data
    questions = quiz.get("questions", [])
    answers   = st.session_state.quiz_answers
    wrong     = st.session_state.wrong_answers_session
    total     = len(questions)
    correct   = total - len(wrong)
    pct       = round(correct / total * 100) if total else 0

    if pct >= 80:
        sc, sb, sv = C["green"], "green", t("quiz.result.excellent", lang)
    elif pct >= 60:
        sc, sb, sv = C["orange"], "orange", t("quiz.result.good", lang)
    elif pct >= 40:
        sc, sb, sv = "#EA580C", "orange", t("quiz.result.keep", lang)
    else:
        sc, sb, sv = C["red"], "red", t("quiz.result.review", lang)

    # Score banner
    st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:24px 28px;
            display:flex;align-items:center;gap:28px;margin-bottom:24px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04);">
    <div style="font-family:'JetBrains Mono',monospace;font-size:3rem;
                font-weight:700;color:{sc};line-height:1;">{pct}%</div>
    <div>
        <div style="font-size:1.125rem;font-weight:600;color:{C["text"]};
                    margin-bottom:4px;">{sv}</div>
        <div style="font-size:0.875rem;color:{C["text_2"]};">
            {t("quiz.result.summary", lang, correct=correct, total=total)}
        </div>
        <div style="margin-top:12px;height:4px;width:240px;
                    background:{C["border"]};border-radius:100px;overflow:hidden;">
            <div style="width:{pct}%;height:4px;background:{sc};
                        border-radius:100px;"></div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

    # Full correction
    st.markdown(f"""
<p style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:12px;">
    {t("quiz.correction", lang)}
</p>""", unsafe_allow_html=True)

    for idx, q in enumerate(questions):
        sel       = answers.get(idx, "—")
        correct_a = q.get("correct_answer", "")
        ok        = sel == correct_a
        choices   = q.get("choices", [])
        expl      = q.get("explanation", "")
        concept   = q.get("concept", "")

        border_l = C["green"] if ok else C["red"]
        status   = badge(t("quiz.correct", lang), "green") if ok else badge(t("quiz.incorrect", lang), "red")

        # build choices HTML
        choices_html = ""
        for choice in choices:
            if choice == correct_a:
                row_bg, row_border, row_color, marker = C["green_bg"], "#A7F3D0", C["green"], "+"
            elif choice == sel and not ok:
                row_bg, row_border, row_color, marker = C["red_bg"], "#FCA5A5", C["red"], "✕"
            else:
                row_bg, row_border, row_color, marker = C["surface_2"], C["border"], C["text_2"], "·"
            choices_html += f"""
<div style="background:{row_bg};border:1px solid {row_border};
            border-radius:7px;padding:8px 14px;margin-bottom:5px;
            display:flex;align-items:center;gap:10px;
            font-size:0.8125rem;color:{row_color};">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                 font-weight:700;min-width:14px;">{marker}</span>
    <span>{choice}</span>
</div>"""

        expl_html = ""
        if not ok and expl:
            expl_html = f"""
<div style="margin-top:10px;padding:10px 14px;
            background:{C["indigo_light"]};border-radius:8px;
            font-size:0.8125rem;color:{C["indigo"]};line-height:1.5;">
    <strong>{t("quiz.note", lang)}:</strong> {expl}
</div>"""

        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-left:3px solid {border_l};border-radius:10px;
            padding:16px 20px;margin-bottom:10px;
            box-shadow:0 1px 4px rgba(15,23,42,0.05);">
    <div style="display:flex;justify-content:space-between;
                align-items:baseline;margin-bottom:10px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                     color:{C["text_3"]};">
            Q{idx+1:02d}{f" — {concept}" if concept else ""}
        </span>
        {status}
    </div>
    <p style="font-size:0.9rem;font-weight:500;color:{C["text"]};
              margin-bottom:12px;line-height:1.5;">{q['question']}</p>
    {choices_html}
    {expl_html}
</div>""", unsafe_allow_html=True)

    # AI analysis
    if wrong:
        divider()
        st.markdown(f"""
<p style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:12px;">
    {t("quiz.analysis", lang)}
</p>""", unsafe_allow_html=True)
        with st.spinner("…"):
            analysis = analyze_weaknesses(wrong, quiz.get("course_id"), language=lang)
        if analysis.get("concepts_faibles"):
            for c in analysis["concepts_faibles"]:
                st.markdown(badge(c, "red") + "&nbsp;", unsafe_allow_html=True)
            spacer(8)
        if analysis.get("priorite"):
            st.markdown(f"""
<div style="background:{C["orange_bg"]};border:1px solid #FDE68A;
            border-radius:8px;padding:10px 14px;font-size:0.875rem;
            color:{C["orange"]};margin-bottom:12px;">
    <strong>{t("quiz.priority", lang)}:</strong> <em>{analysis['priorite']}</em>
</div>""", unsafe_allow_html=True)
        if analysis.get("analyse"):
            with st.expander(t("quiz.full_analysis", lang)):
                st.markdown(analysis["analyse"])

    divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(t("quiz.new", lang), type="primary", use_container_width=True):
            st.session_state.quiz_data      = None
            st.session_state.quiz_answers   = {}
            st.session_state.quiz_submitted = False
            st.rerun()
    with c2:
        if wrong and st.button(t("quiz.retry_targeted", lang), type="secondary", use_container_width=True):
            st.session_state.quiz_data      = None
            st.session_state.quiz_submitted = False
            st.rerun()
    with c3:
        if st.button(t("quiz.ask_tutor", lang), type="secondary", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
