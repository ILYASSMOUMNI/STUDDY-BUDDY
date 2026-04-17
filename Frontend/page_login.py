# frontend/page_login.py

import streamlit as st
from backend.database import create_student
from frontend.design_system import C, spacer


def render_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        spacer(56)

        st.markdown(f"""
<div style="text-align:center;margin-bottom:32px;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
                width:44px;height:44px;background:{C["indigo"]};
                border-radius:12px;margin-bottom:16px;">
        <span style="color:#fff;font-size:1.2rem;font-weight:700;">S</span>
    </div>
    <h1 style="font-size:1.25rem;font-weight:600;color:{C["text"]};
               letter-spacing:-0.02em;margin-bottom:6px;">
        Welcome to StudyBuddy
    </h1>
    <p style="font-size:0.875rem;color:{C["text_2"]};">
        Your AI-powered tutor for IA & Data Science
    </p>
</div>

<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:16px;padding:32px;
            box-shadow:0 4px 24px rgba(0,0,0,0.06);">
    <p style="font-size:0.8125rem;font-weight:600;color:{C["text_2"]};
              margin-bottom:20px;text-transform:uppercase;letter-spacing:0.06em;">
        Sign in or create account
    </p>
""", unsafe_allow_html=True)

        name  = st.text_input("Full name", placeholder="Your name")
        email = st.text_input("Email address", placeholder="you@emsi.ma")
        spacer(8)

        if st.button("Continue", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("Please enter your name.")
            elif "@" not in email:
                st.error("Please enter a valid email.")
            else:
                sid = create_student(name.strip(), email.strip().lower())
                if sid > 0:
                    st.session_state.student_id    = sid
                    st.session_state.student_name  = name.strip()
                    st.session_state.student_email = email.strip().lower()
                    st.session_state.current_page  = "home"
                    st.rerun()
                else:
                    st.error("Could not sign in. Try again.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
<p style="text-align:center;font-size:0.75rem;color:{C["text_3"]};margin-top:16px;">
    EMSI Morocco — Distributed AI project
</p>""", unsafe_allow_html=True)
