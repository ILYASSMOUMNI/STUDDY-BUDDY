# frontend/page_chat.py

import streamlit as st
from backend.database import get_all_courses, get_course_by_id
from backend.ai_tutor import chat_with_tutor


def render_chat():
    st.markdown("""
    <div style="margin-bottom:16px;">
        <div class="sb-title">💬 Tuteur IA</div>
        <div class="sb-subtitle">Pose toutes tes questions — je m'appuie sur tes cours</div>
    </div>
    """, unsafe_allow_html=True)

    courses = get_all_courses()

    if not courses:
        st.markdown("""
        <div class="alert-warning">
            ⚠️ Aucun cours disponible. <a href="#" style="color:#7b7bff;">Upload un cours d'abord.</a>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📂 Aller à Mes Cours"):
            st.session_state.current_page = "courses"
            st.rerun()
        return

    # ── Sélection du cours ──
    col_select, col_reset = st.columns([4, 1])

    with col_select:
        course_options = {c['title']: c['id'] for c in courses}
        course_options_list = list(course_options.keys())

        # Pré-sélectionner si venu depuis home/courses
        default_idx = 0
        if st.session_state.selected_course_id:
            for i, c in enumerate(courses):
                if c['id'] == st.session_state.selected_course_id:
                    default_idx = i
                    break

        selected_title = st.selectbox(
            "📚 Cours actif",
            course_options_list,
            index=default_idx,
            help="Le tuteur répondra en se basant sur ce cours"
        )
        selected_course_id = course_options[selected_title]
        st.session_state.selected_course_id = selected_course_id

    with col_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset", help="Effacer la conversation"):
            st.session_state.chat_messages = []
            st.session_state.chat_display = []
            st.rerun()

    # ── Suggestions de questions ──
    if not st.session_state.chat_display:
        st.markdown("#### 💡 Questions suggérées")
        suggestions = [
            "Explique-moi les réseaux de neurones step by step",
            "C'est quoi la différence entre supervised et unsupervised learning ?",
            "Comment fonctionne la backpropagation ?",
            "Explique le gradient descent avec un exemple simple",
            "Qu'est-ce qu'un transformer en NLP ?",
        ]
        cols = st.columns(3)
        for i, suggestion in enumerate(suggestions[:6]):
            with cols[i % 3]:
                if st.button(f"💬 {suggestion[:45]}...", key=f"sugg_{i}",
                             use_container_width=True):
                    _send_message(suggestion, selected_course_id)

        st.markdown("---")

    # ── Historique du chat ──
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_display:
            st.markdown("""
            <div style="text-align:center; color:#4a4a6a; padding:40px 0; font-size:0.9rem;">
                👆 Clique sur une suggestion ou pose ta propre question ci-dessous
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_display:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-user">
                        <b>Toi</b><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Formater le markdown dans la bulle assistant
                    content_html = msg['content'].replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="chat-assistant">
                        <b>🤖 StudyBuddy</b><br>
                    </div>
                    """, unsafe_allow_html=True)
                    # Utiliser st.markdown pour rendre le markdown correctement
                    with st.container():
                        st.markdown(msg['content'])
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Input utilisateur ──
    st.markdown("---")
    col_input, col_send = st.columns([5, 1])

    with col_input:
        user_input = st.text_input(
            "Ta question",
            placeholder="Ex: Je ne comprends pas le overfitting, tu peux m'expliquer ?",
            label_visibility="collapsed",
            key="chat_input"
        )

    with col_send:
        send_clicked = st.button("Envoyer ➤", use_container_width=True)

    if send_clicked and user_input.strip():
        _send_message(user_input.strip(), selected_course_id)

    # ── Mode explication pas à pas ──
    with st.expander("🔍 Explication approfondie d'un concept"):
        concept_input = st.text_input("Concept à approfondir", placeholder="Ex: Convolution, LSTM, K-means...")
        level = st.select_slider("Ton niveau", options=["débutant", "intermédiaire", "avancé"], value="intermédiaire")
        if st.button("🧠 Explication pas à pas"):
            if concept_input.strip():
                with st.spinner("Le tuteur prépare une explication détaillée..."):
                    from backend.ai_tutor import explain_concept_step_by_step
                    explanation = explain_concept_step_by_step(
                        selected_course_id,
                        concept_input.strip(),
                        student_level=level
                    )
                    st.markdown(explanation)


def _send_message(user_message: str, course_id: int):
    """Envoie un message et récupère la réponse du tuteur."""
    # Ajouter le message user à l'historique d'affichage
    st.session_state.chat_display.append({"role": "user", "content": user_message})

    # Ajouter à l'historique API (sans le contexte RAG — il est ajouté dans ai_tutor)
    st.session_state.chat_messages.append({"role": "user", "content": user_message})

    with st.spinner("🤔 Le tuteur réfléchit..."):
        try:
            # Appel au tuteur avec RAG
            response = chat_with_tutor(
                messages=st.session_state.chat_messages[:-1],  # historique sans le dernier
                course_id=course_id,
                user_message=user_message
            )

            # Ajouter la réponse à l'historique
            st.session_state.chat_display.append({"role": "assistant", "content": response})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

        except Exception as e:
            error_msg = f"❌ Erreur : {str(e)}"
            st.session_state.chat_display.append({"role": "assistant", "content": error_msg})

    st.rerun()
