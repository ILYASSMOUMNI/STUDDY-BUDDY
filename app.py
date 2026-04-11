# app.py — Point d'entrée StudyBuddy Streamlit

import streamlit as st
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db

# ──────────────────────────────────────────────
#  Configuration Streamlit
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="StudyBuddy — IA & Data Science",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Init DB au démarrage
init_db()

# ──────────────────────────────────────────────
#  CSS Global
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

    /* Reset & base */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid #2d2d4e;
    }

    section[data-testid="stSidebar"] * {
        color: #e8e8f0 !important;
    }

    /* Main background */
    .stApp {
        background: #0a0a12;
    }

    /* Cards */
    .sb-card {
        background: linear-gradient(135deg, #12122a 0%, #1a1a35 100%);
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s ease;
    }
    .sb-card:hover {
        border-color: #5b5bff;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e3a 0%, #252545 100%);
        border: 1px solid #3a3a6a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #7b7bff;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8888aa;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #2d2d6e, #3d3d8e);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0 8px 40px;
        color: #e8e8ff;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .chat-assistant {
        background: linear-gradient(135deg, #1a2a1a, #1e321e);
        border: 1px solid #2a4a2a;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 40px 8px 0;
        color: #d0e8d0;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Quiz cards */
    .quiz-question {
        background: #16162e;
        border: 1px solid #2e2e5e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .quiz-question h4 {
        color: #b8b8ff;
        font-size: 1rem;
        margin-bottom: 12px;
    }

    /* Tags */
    .weakness-tag {
        display: inline-block;
        background: linear-gradient(135deg, #3a1a1a, #4a2020);
        border: 1px solid #6a3030;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: #ffaaaa;
        margin: 4px;
    }
    .strength-tag {
        display: inline-block;
        background: linear-gradient(135deg, #1a3a1a, #204a20);
        border: 1px solid #306a30;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.8rem;
        color: #aaffaa;
        margin: 4px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4a4aff, #6a6aff) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(100, 100, 255, 0.4) !important;
    }

    /* Title */
    .sb-title {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #7b7bff, #b8b8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sb-subtitle {
        color: #6868aa;
        font-size: 0.9rem;
        margin-top: -8px;
    }

    /* Alert banners */
    .alert-warning {
        background: linear-gradient(135deg, #2a2000, #3a2d00);
        border: 1px solid #6a5a00;
        border-radius: 10px;
        padding: 12px 16px;
        color: #ffdd88;
        font-size: 0.9rem;
    }
    .alert-success {
        background: linear-gradient(135deg, #002a00, #003a00);
        border: 1px solid #006a00;
        border-radius: 10px;
        padding: 12px 16px;
        color: #88ff88;
        font-size: 0.9rem;
    }

    /* Progress bar custom */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4a4aff, #b8b8ff) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a1a2e !important;
        border: 1px solid #2a2a4e !important;
        border-radius: 10px !important;
        color: #e8e8ff !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: #1a1a2e !important;
        border: 1px solid #2a2a4e !important;
        border-radius: 10px !important;
        color: #e8e8ff !important;
    }

    /* Divider */
    hr { border-color: #2a2a4a !important; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Session State Init
# ──────────────────────────────────────────────
def init_session():
    defaults = {
        "student_id": None,
        "student_name": None,
        "student_email": None,
        "current_page": "home",
        "selected_course_id": None,
        "chat_messages": [],    # [{role, content}] pour l'API
        "chat_display": [],     # [{role, content}] pour l'affichage
        "quiz_data": None,
        "quiz_answers": {},
        "quiz_submitted": False,
        "wrong_answers_session": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ──────────────────────────────────────────────
#  Import pages
# ──────────────────────────────────────────────
from frontend.page_login import render_login
from frontend.page_home import render_home
from frontend.page_courses import render_courses
from frontend.page_chat import render_chat
from frontend.page_quiz import render_quiz
from frontend.page_dashboard import render_dashboard


# ──────────────────────────────────────────────
#  Sidebar Navigation
# ──────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sb-title">📚 StudyBuddy</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-subtitle">IA & Data Science — EMSI</div>', unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.student_id:
            st.markdown(f"👤 **{st.session_state.student_name}**")
            st.markdown("---")

            nav_items = {
                "🏠 Accueil": "home",
                "📂 Mes Cours": "courses",
                "💬 Tuteur IA": "chat",
                "📝 Quiz": "quiz",
                "📊 Dashboard": "dashboard",
            }

            for label, page in nav_items.items():
                active = "➤ " if st.session_state.current_page == page else "  "
                if st.button(f"{active}{label}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

            st.markdown("---")
            if st.button("🚪 Déconnexion", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session()
                st.rerun()
        else:
            st.markdown("*Connecte-toi pour commencer*")


# ──────────────────────────────────────────────
#  Router principal
# ──────────────────────────────────────────────
def main():
    render_sidebar()

    if not st.session_state.student_id:
        render_login()
    else:
        page = st.session_state.current_page
        if page == "home":
            render_home()
        elif page == "courses":
            render_courses()
        elif page == "chat":
            render_chat()
        elif page == "quiz":
            render_quiz()
        elif page == "dashboard":
            render_dashboard()
        else:
            render_home()


if __name__ == "__main__":
    main()
