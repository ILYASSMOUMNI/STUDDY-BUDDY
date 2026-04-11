# frontend/page_login.py

import streamlit as st
from backend.database import create_student, get_student_by_email


def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin-bottom:32px;">
            <div style="font-family:'Space Mono',monospace; font-size:3rem; font-weight:700;
                        background:linear-gradient(135deg,#7b7bff,#b8b8ff);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text;">
                📚 StudyBuddy
            </div>
            <div style="color:#6868aa; font-size:1rem; margin-top:8px;">
                Ton tuteur IA pour l'IA & Data Science
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-card" style="max-width:480px; margin:auto;">
            <div style="color:#b8b8ff; font-size:1.1rem; font-weight:600; margin-bottom:20px; text-align:center;">
                Connexion / Inscription
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="sb-card">', unsafe_allow_html=True)

            name = st.text_input("👤 Ton prénom", placeholder="Ex: Iliass")
            email = st.text_input("📧 Ton email", placeholder="Ex: iliass@emsi.ma")

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚀 Commencer à apprendre", use_container_width=True):
                if not name.strip():
                    st.error("Entre ton prénom svp")
                elif not email.strip() or "@" not in email:
                    st.error("Entre un email valide svp")
                else:
                    student_id = create_student(name.strip(), email.strip().lower())
                    if student_id > 0:
                        st.session_state.student_id = student_id
                        st.session_state.student_name = name.strip()
                        st.session_state.student_email = email.strip().lower()
                        st.session_state.current_page = "home"
                        st.success(f"Bienvenue {name} ! 🎉")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la connexion. Réessaie.")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; color:#4a4a6a; font-size:0.8rem; margin-top:24px;">
            Filière : IA & Data Science · EMSI Morocco
        </div>
        """, unsafe_allow_html=True)
