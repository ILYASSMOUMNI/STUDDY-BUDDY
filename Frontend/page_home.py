# frontend/page_home.py

import streamlit as st
from backend.database import get_student_stats, get_weaknesses, get_all_courses


def render_home():
    name = st.session_state.student_name
    stats = get_student_stats(st.session_state.student_id)
    weaknesses = get_weaknesses(st.session_state.student_id)
    courses = get_all_courses()

    # Header
    st.markdown(f"""
    <div style="margin-bottom:32px;">
        <div style="font-family:'Space Mono',monospace; font-size:1.8rem; font-weight:700;
                    background:linear-gradient(135deg,#7b7bff,#b8b8ff);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
            Bonjour, {name} 👋
        </div>
        <div style="color:#6868aa; font-size:0.95rem; margin-top:4px;">
            Prêt à apprendre quelque chose aujourd'hui ?
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Métriques ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(courses)}</div>
            <div class="metric-label">Cours disponibles</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['total_questions']}</div>
            <div class="metric-label">Questions répondues</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        score_color = "#7bff7b" if stats['score_global'] >= 70 else "#ffbb7b" if stats['score_global'] >= 50 else "#ff7b7b"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{score_color};">{stats['score_global']}%</div>
            <div class="metric-label">Score global</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#ff7bbb;">{len(weaknesses)}</div>
            <div class="metric-label">Lacunes détectées</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 🎯 Démarrage rapide")

        # Si pas de cours uploadés
        if not courses:
            st.markdown("""
            <div class="alert-warning">
                ⚠️ Aucun cours chargé. Va dans <b>Mes Cours</b> pour uploader un PDF ou DOCX.
            </div>
            """, unsafe_allow_html=True)
        else:
            for course in courses[:3]:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"""
                    <div style="color:#c8c8ff; font-weight:500;">{course['title']}</div>
                    <div style="color:#5a5a8a; font-size:0.8rem;">{course['num_chunks']} segments indexés</div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("💬 Chat", key=f"chat_{course['id']}"):
                        st.session_state.selected_course_id = course['id']
                        st.session_state.current_page = "chat"
                        st.rerun()
                with col_c:
                    if st.button("📝 Quiz", key=f"quiz_{course['id']}"):
                        st.session_state.selected_course_id = course['id']
                        st.session_state.current_page = "quiz"
                        st.rerun()
                st.markdown("<hr style='border-color:#2a2a4a;margin:8px 0;'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📂 Uploader un cours", use_container_width=True):
                st.session_state.current_page = "courses"
                st.rerun()
        with col_btn2:
            if st.button("📊 Voir mon dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()

    with col_right:
        st.markdown("### ⚠️ Concepts à retravailler")
        if weaknesses:
            for w in weaknesses[:5]:
                fail_emoji = "🔴" if w['fail_count'] >= 3 else "🟡" if w['fail_count'] >= 2 else "🟠"
                st.markdown(f"""
                <div class="weakness-tag">{fail_emoji} {w['concept']} ({w['fail_count']}x)</div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎯 Quiz ciblé sur mes lacunes", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.rerun()
        else:
            st.markdown("""
            <div class="alert-success">
                ✅ Aucune lacune détectée pour l'instant.<br>
                Fais des quiz pour que je puisse t'aider !
            </div>
            """, unsafe_allow_html=True)

    # ── Tips du jour ──
    st.markdown("---")
    st.markdown("### 💡 Comment bien utiliser StudyBuddy")
    tips = [
        ("1. Upload tes cours", "Va dans **Mes Cours** → uploader PDF ou DOCX de tes cours IA/Data Science"),
        ("2. Discute avec le tuteur", "Pose n'importe quelle question sur le cours → le tuteur explique pas à pas"),
        ("3. Fais le quiz", "Après chaque cours, teste-toi → le système détecte automatiquement tes lacunes"),
        ("4. Quiz ciblé", "StudyBuddy génère des questions spécialement sur ce que tu n'as pas compris"),
    ]
    cols = st.columns(4)
    for i, (title, desc) in enumerate(tips):
        with cols[i]:
            st.markdown(f"""
            <div class="sb-card" style="padding:16px; height:120px;">
                <div style="color:#b8b8ff; font-weight:600; font-size:0.9rem; margin-bottom:8px;">{title}</div>
                <div style="color:#7878aa; font-size:0.8rem; line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
