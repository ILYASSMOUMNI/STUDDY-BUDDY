# app.py

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db
from frontend.design_system import inject_global_css, C
from frontend.i18n import t

st.set_page_config(
    page_title="StudyBuddy",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def _startup():
    """Initialisation unique au démarrage : DB + cours exemples."""
    init_db()
    try:
        from backend.sample_courses import init_sample_courses
        titles = init_sample_courses()
        if titles:
            print(f"[App] Cours exemples indexés : {titles}")
    except Exception as e:
        print(f"[App] Avertissement init cours exemples : {e}")


_startup()
inject_global_css()

_DEFAULTS = {
    "student_id":               None,
    "student_name":             None,
    "student_email":            None,
    "current_page":             "home",
    "selected_course_id":       None,
    "chat_messages":            [],
    "chat_display":             [],
    "quiz_data":                None,
    "quiz_answers":             {},
    "quiz_submitted":           False,
    "wrong_answers_session":    [],
    # extended navigation state
    "language":                 "fr",
    "active_chat_session_id":   None,
    "focus_concept":            None,
    "chat_preset":              None,
    "chat_mode":                "default",
    "quick_quiz_mode":          False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# (id, i18n_key, icon)
NAV_ITEMS = [
    ("home",      "nav.home",      "▦"),
    ("courses",   "nav.courses",   "◻"),
    ("chat",      "nav.chat",      "◎"),
    ("quiz",      "nav.quiz",      "◇"),
    ("dashboard", "nav.dashboard", "◑"),
]


def _sidebar():
    with st.sidebar:
        # ── Brand ──────────────────────────────────────────────
        st.markdown(f"""
<div style="padding:28px 20px 20px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:36px;height:36px;flex-shrink:0;
                background:linear-gradient(135deg,{C["accent"]},{C["violet"]});
                border-radius:10px;display:flex;align-items:center;
                justify-content:center;
                box-shadow:0 4px 16px rgba(110,231,183,0.3);">
      <span style="color:{C["text_inv"]};font-size:0.9rem;font-weight:800;
                   font-family:'DM Sans',sans-serif;letter-spacing:-0.05em;">S</span>
    </div>
    <div>
      <div style="font-size:0.9375rem;font-weight:700;color:{C["text"]};
                  letter-spacing:-0.02em;">StudyBuddy</div>
      <div style="font-size:0.6875rem;color:{C["text_3"]};margin-top:1px;
                  letter-spacing:0.02em;">IA & Data Science</div>
    </div>
  </div>
</div>
<div style="height:1px;background:linear-gradient(90deg,transparent,{C["border"]},transparent);
            margin:0 12px 8px;"></div>
""", unsafe_allow_html=True)

        if not st.session_state.student_id:
            return

        lang = st.session_state.get("language", "fr")

        # ── Nav label ──────────────────────────────────────────
        st.markdown(f"""
<p style="font-size:0.625rem;font-weight:600;letter-spacing:0.12em;
          text-transform:uppercase;color:{C["text_3"]};
          padding:8px 20px 6px;">{t("nav.section", lang)}</p>
""", unsafe_allow_html=True)

        # ── Nav items ──────────────────────────────────────────
        for page_id, label_key, icon in NAV_ITEMS:
            label     = t(label_key, lang)
            is_active = st.session_state.current_page == page_id

            if is_active:
                st.markdown(f"""
<style>
#nav-wrap-{page_id} button {{
  background: rgba(110,231,183,0.08) !important;
  color: {C["accent"]} !important;
  border-left-color: {C["accent"]} !important;
  font-weight: 600 !important;
}}
</style>""", unsafe_allow_html=True)

            st.markdown(f'<div id="nav-wrap-{page_id}" style="padding:1px 10px;">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Divider ────────────────────────────────────────────
        st.markdown(f"""
<div style="height:1px;background:{C["border"]};margin:14px 20px;"></div>
""", unsafe_allow_html=True)

        # ── User section ───────────────────────────────────────
        name  = st.session_state.student_name or "User"
        email = st.session_state.student_email or ""
        initials = "".join(p[0].upper() for p in name.split()[:2])

        st.markdown(f"""
<div style="padding:8px 20px 12px;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
    <div style="width:32px;height:32px;flex-shrink:0;
                background:linear-gradient(135deg,{C["accent"]},{C["violet"]});
                border-radius:8px;display:flex;align-items:center;justify-content:center;">
      <span style="color:{C["text_inv"]};font-size:0.75rem;font-weight:700;
                   font-family:'DM Sans',sans-serif;">{initials}</span>
    </div>
    <div style="min-width:0;">
      <div style="font-size:0.8125rem;font-weight:600;color:{C["text"]};
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {name}
      </div>
      <div style="font-size:0.6875rem;color:{C["text_3"]};margin-top:1px;
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {email}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Language toggle ────────────────────────────────────
        st.markdown(f'<div style="padding:0 20px 8px;">', unsafe_allow_html=True)
        lang_label = t("sidebar.language", lang)
        st.markdown(f"""
<p style="font-size:0.625rem;font-weight:600;letter-spacing:0.1em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:6px;">
  {lang_label}
</p>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)
        with lc1:
            if st.button("FR", key="lang_fr", use_container_width=True,
                         type="primary" if lang == "fr" else "secondary"):
                st.session_state.language = "fr"
                st.rerun()
        with lc2:
            if st.button("EN", key="lang_en", use_container_width=True,
                         type="primary" if lang == "en" else "secondary"):
                st.session_state.language = "en"
                st.rerun()

        st.markdown('<div style="padding:0 10px 16px;">', unsafe_allow_html=True)
        if st.button(t("nav.sign_out", lang), key="signout", use_container_width=True, type="secondary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            for k, v in _DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Version ────────────────────────────────────────────
        st.markdown(f"""
<div style="padding:0 20px 20px;">
  <span style="font-size:0.625rem;color:{C["text_3"]};letter-spacing:0.08em;">
    STUDYBUDDY v1.0 · EMSI
  </span>
</div>
""", unsafe_allow_html=True)


_NAV_ICONS = {
    "home":      "🏠",
    "courses":   "📚",
    "chat":      "💬",
    "quiz":      "📝",
    "dashboard": "📊",
}


def _topnav():
    lang    = st.session_state.get("language", "fr")
    current = st.session_state.current_page

    # Pill container
    st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:999px;padding:5px 6px;margin-bottom:20px;
            display:inline-flex;gap:4px;
            box-shadow:0 2px 8px rgba(15,23,42,0.07),
                       0 1px 2px rgba(15,23,42,0.04);">
""", unsafe_allow_html=True)

    cols = st.columns(len(NAV_ITEMS))
    for col, (page_id, label_key, _icon) in zip(cols, NAV_ITEMS):
        label     = t(label_key, lang)
        icon      = _NAV_ICONS[page_id]
        is_active = current == page_id

        if is_active:
            st.markdown(f"""
<style>
#tnav-{page_id} button {{
  background: {C["accent"]} !important;
  color: {C["text_inv"]} !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(5,150,105,0.30) !important;
  font-weight: 700 !important;
}}
#tnav-{page_id} button:hover {{
  background: #047857 !important;
  transform: none !important;
}}
</style>""", unsafe_allow_html=True)

        with col:
            st.markdown(f'<div id="tnav-{page_id}">', unsafe_allow_html=True)
            if st.button(f"{icon} {label}", key=f"tnav_{page_id}",
                         use_container_width=True,
                         type="secondary"):
                st.session_state.current_page = page_id
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    _sidebar()

    if not st.session_state.student_id:
        from frontend.page_login import render_login
        render_login()
        return

    _topnav()

    page = st.session_state.current_page
    if page == "home":
        from frontend.page_home import render_home; render_home()
    elif page == "courses":
        from frontend.page_courses import render_courses; render_courses()
    elif page == "chat":
        from frontend.page_chat import render_chat; render_chat()
    elif page == "quiz":
        from frontend.page_quiz import render_quiz; render_quiz()
    elif page == "dashboard":
        from frontend.page_dashboard import render_dashboard; render_dashboard()
    else:
        from frontend.page_home import render_home; render_home()


if __name__ == "__main__":
    main()
