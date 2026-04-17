# frontend/page_chat.py

import streamlit as st
from backend.database import get_all_courses
from backend.ai_tutor import chat_with_tutor, explain_concept_step_by_step
from frontend.design_system import C, spacer
from frontend.i18n import t


_RESPONSE_MODES = [
    ("default",      {"fr": "Expliquer",  "en": "Explain"},    "💬"),
    ("step_by_step", {"fr": "Pas à pas",  "en": "Step-by-step"},"🪜"),
    ("example",      {"fr": "Exemple",    "en": "Example"},    "💡"),
    ("summary",      {"fr": "Résumé",     "en": "Summary"},    "📋"),
]

_SUGGESTIONS = {
    "fr": [
        ("📖", "Explique les concepts",      "Vue d'ensemble du cours"),
        ("📝", "Résume ce chapitre",          "Points clés en quelques lignes"),
        ("💡", "Donne un exemple concret",    "Un cas réel pour mieux comprendre"),
        ("🔍", "Quels sont les termes clés ?","Glossaire et définitions"),
        ("⚖️", "Compare ces notions",         "Similitudes et différences"),
        ("🎯", "Conseils d'apprentissage",    "Méthodes pour mieux retenir"),
    ],
    "en": [
        ("📖", "Explain the concepts",   "Course overview"),
        ("📝", "Summarize this chapter", "Key points in a few lines"),
        ("💡", "Give a concrete example","A real case to understand better"),
        ("🔍", "What are the key terms?","Glossary and definitions"),
        ("⚖️", "Compare these notions",  "Similarities and differences"),
        ("🎯", "Study tips",             "Methods to retain better"),
    ],
}


def render_chat():
    lang    = st.session_state.get("language", "fr")
    courses = get_all_courses()

    if not courses:
        _empty_no_courses(lang)
        return

    # ── CSS overrides for this page ───────────────────────────
    st.markdown(f"""
<style>
/* Compact chat messages */
.stChatMessage {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:14px !important;
  padding:4px 8px !important;
  box-shadow:0 1px 4px rgba(15,23,42,0.05) !important;
  margin-bottom:6px !important;
}}
/* User bubble accent */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
  border-left:3px solid {C["accent"]} !important;
  background:{C["accent_dim"]} !important;
}}
/* Fix chat input */
.stChatInput textarea {{
  font-size:0.9rem !important;
  padding:12px 16px !important;
}}
</style>""", unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────
    course_map  = {c["title"]: c["id"] for c in courses}
    default_idx = 0
    if st.session_state.selected_course_id:
        for i, c in enumerate(courses):
            if c["id"] == st.session_state.selected_course_id:
                default_idx = i; break

    col_left, col_right = st.columns([3, 1])
    with col_left:
        st.markdown(f"""
<div style="padding:20px 0 6px;">
  <h1 style="font-size:1.5rem;font-weight:700;color:{C["text"]};
             letter-spacing:-0.03em;line-height:1;margin-bottom:4px;">
    {"Tuteur IA" if lang == "fr" else "AI Tutor"}
  </h1>
  <p style="font-size:0.8125rem;color:{C["text_3"]};margin:0;">
    {t("chat.subtitle", lang)}
  </p>
</div>""", unsafe_allow_html=True)

    with col_right:
        spacer(22)
        if st.button("🗑 " + t("common.clear", lang),
                     type="secondary", use_container_width=True, key="chat_clear"):
            st.session_state.chat_messages = []
            st.session_state.chat_display  = []
            st.rerun()

    # ── Course + Mode bar ─────────────────────────────────────
    st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:14px;padding:12px 16px;margin-bottom:18px;
            display:flex;align-items:center;gap:12px;flex-wrap:wrap;
            box-shadow:0 1px 4px rgba(15,23,42,0.05);">
  <span style="font-size:0.75rem;font-weight:600;color:{C["text_3"]};
               text-transform:uppercase;letter-spacing:0.08em;white-space:nowrap;">
    {"Cours actif" if lang == "fr" else "Active course"}
  </span>
</div>""", unsafe_allow_html=True)

    # Course selector sits right after (we use st.selectbox float trick via columns)
    cs_col, mode_cols_area = st.columns([1.6, 2.4])
    with cs_col:
        sel = st.selectbox(
            "course_sel",
            list(course_map.keys()),
            index=default_idx,
            label_visibility="collapsed",
            key="chat_course_sel",
        )
        st.session_state.selected_course_id = course_map[sel]

    # Mode pills
    current_mode = st.session_state.get("chat_mode", "default")
    with mode_cols_area:
        m_cols = st.columns(len(_RESPONSE_MODES))
        for col, (mode_key, mode_names, mode_icon) in zip(m_cols, _RESPONSE_MODES):
            label     = f"{mode_icon} {mode_names[lang]}"
            is_active = current_mode == mode_key
            if is_active:
                st.markdown(f"""<style>
#msel-{mode_key} button {{
  background:{C["accent"]} !important;
  color:{C["text_inv"]} !important;
  border:none !important;
  box-shadow:0 2px 8px {C["accent_glow"]} !important;
  font-weight:700 !important;
}}</style>""", unsafe_allow_html=True)
            with col:
                st.markdown(f'<div id="msel-{mode_key}">', unsafe_allow_html=True)
                if st.button(label, key=f"msel_{mode_key}",
                             use_container_width=True, type="secondary"):
                    st.session_state.chat_mode = mode_key
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Auto-send preset ──────────────────────────────────────
    preset = st.session_state.get("chat_preset")
    if preset:
        st.session_state.chat_preset = None
        _send(preset, st.session_state.selected_course_id)
        return

    # ── Empty state — suggestion cards ────────────────────────
    if not st.session_state.chat_display:
        focus = st.session_state.get("focus_concept")
        name  = st.session_state.get("student_name", "").split()[0] if st.session_state.get("student_name") else ""

        greeting = f"Bonjour{', ' + name if name else ''} 👋" if lang == "fr" else f"Hello{', ' + name if name else ''} 👋"
        sub      = "Comment puis-je t'aider avec ce cours ?" if lang == "fr" else "How can I help you with this course?"

        st.markdown(f"""
<div style="text-align:center;padding:32px 0 24px;">
  <div style="display:inline-flex;align-items:center;justify-content:center;
              width:48px;height:48px;border-radius:14px;margin-bottom:14px;
              background:linear-gradient(135deg,{C["accent"]},{C["violet"]});
              box-shadow:0 4px 16px {C["accent_glow"]};">
    <span style="font-size:1.4rem;">🤖</span>
  </div>
  <h2 style="font-size:1.25rem;font-weight:700;color:{C["text"]};
             letter-spacing:-0.02em;margin-bottom:6px;">{greeting}</h2>
  <p style="font-size:0.9rem;color:{C["text_2"]};margin:0;">{sub}</p>
</div>""", unsafe_allow_html=True)

        suggestions = list(_SUGGESTIONS.get(lang, _SUGGESTIONS["fr"]))
        if focus:
            prefix = "Explique : " if lang == "fr" else "Explain: "
            suggestions.insert(0, ("🎯", f"{prefix}{focus}", "Concept ciblé" if lang == "fr" else "Targeted concept"))
            suggestions = suggestions[:6]

        c1, c2, c3 = st.columns(3)
        for idx, (icon, title, desc) in enumerate(suggestions):
            with [c1, c2, c3][idx % 3]:
                # card background on hover handled by button CSS
                st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:14px 16px;margin-bottom:10px;
            box-shadow:0 1px 4px rgba(15,23,42,0.05);cursor:pointer;">
  <div style="font-size:1.3rem;margin-bottom:8px;">{icon}</div>
  <div style="font-size:0.875rem;font-weight:600;color:{C["text"]};
              margin-bottom:3px;line-height:1.3;">{title}</div>
  <div style="font-size:0.75rem;color:{C["text_3"]};line-height:1.4;">{desc}</div>
</div>""", unsafe_allow_html=True)
                if st.button(title, key=f"sug_{idx}",
                             use_container_width=True, type="secondary"):
                    st.session_state.focus_concept = None
                    _send(title, st.session_state.selected_course_id)

        spacer(8)
        st.markdown(f"""
<p style="text-align:center;font-size:0.75rem;color:{C["text_3"]};">
  {"ou écrivez votre question ci-dessous ↓" if lang == "fr" else "or type your question below ↓"}
</p>""", unsafe_allow_html=True)

    else:
        # ── Message thread ────────────────────────────────────
        for msg in st.session_state.chat_display:
            role   = msg["role"]
            avatar = "👤" if role == "user" else "🤖"
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg["content"])

    # ── Chat input ────────────────────────────────────────────
    placeholder = t("chat.placeholder", lang)
    user_input  = st.chat_input(placeholder)
    if user_input and user_input.strip():
        _send(user_input.strip(), st.session_state.selected_course_id)

    # ── Deep-dive expander ────────────────────────────────────
    spacer(4)
    with st.expander("📚 " + t("chat.deep_explanation", lang)):
        focus_default = st.session_state.get("focus_concept") or ""
        c_concept, c_level = st.columns(2)
        with c_concept:
            concept = st.text_input(
                "Concept",
                value=focus_default,
                placeholder=t("chat.deep_placeholder", lang),
                key="deep_c",
                label_visibility="collapsed")
        with c_level:
            level = st.select_slider(
                t("chat.level", lang),
                options=["beginner", "intermediate", "advanced"],
                value="intermediate")
        if st.button(t("chat.generate_explanation", lang), type="primary"):
            if concept.strip():
                with st.spinner(t("chat.generating", lang)):
                    res = explain_concept_step_by_step(
                        st.session_state.selected_course_id,
                        concept.strip(), student_level=level,
                        language=lang)
                st.markdown(res)


def _empty_no_courses(lang: str):
    st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;
            justify-content:center;padding:80px 24px;text-align:center;">
  <div style="font-size:2.5rem;margin-bottom:16px;">📭</div>
  <h2 style="font-size:1.125rem;font-weight:600;color:{C["text"]};margin-bottom:8px;">
    {t("chat.no_courses", lang)}
  </h2>
</div>""", unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        if st.button("📤 " + t("common.upload_course", lang),
                     type="primary", use_container_width=True):
            st.session_state.current_page = "courses"
            st.rerun()


def _send(msg: str, course_id: int):
    lang = st.session_state.get("language", "fr")
    mode = st.session_state.get("chat_mode", "default")
    st.session_state.chat_display.append({"role": "user", "content": msg})
    st.session_state.chat_messages.append({"role": "user", "content": msg})
    with st.spinner(""):
        try:
            resp = chat_with_tutor(
                messages=st.session_state.chat_messages[:-1],
                course_id=course_id,
                user_message=msg,
                response_mode=mode,
                language=lang)
            st.session_state.chat_display.append({"role": "assistant", "content": resp})
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
        except Exception as e:
            st.session_state.chat_display.append(
                {"role": "assistant", "content": t("chat.error", lang, error=str(e))})
    st.rerun()
