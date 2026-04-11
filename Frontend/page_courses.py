# frontend/page_courses.py

import streamlit as st
import os
import shutil
from pathlib import Path
from backend.database import save_course, get_all_courses, get_connection
from backend.course_parser import parse_course_file
from backend.vector_store import index_course, delete_course_index, course_is_indexed
from dotenv import load_dotenv

load_dotenv()
COURSES_DIR = os.getenv("COURSES_DIR", "./data/courses")
FILIERE = os.getenv("FILIERE", "IA & Data Science")


def render_courses():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div class="sb-title">📂 Mes Cours</div>
        <div class="sb-subtitle">Upload tes cours PDF/DOCX pour les indexer</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ──
    st.markdown("### ⬆️ Uploader un nouveau cours")

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Glisse ton fichier ici",
                type=["pdf", "docx", "txt"],
                help="Format supportés : PDF, DOCX, TXT"
            )

        with col2:
            custom_title = st.text_input("Titre du cours (optionnel)", placeholder="Ex: Deep Learning Chapitre 3")
            chunk_size = st.slider("Taille des chunks", 400, 1200, 800, 100,
                                   help="Plus grand = plus de contexte mais moins précis")

        if uploaded_file and st.button("🚀 Indexer ce cours", use_container_width=True):
            _process_upload(uploaded_file, custom_title, chunk_size)

    st.markdown("---")

    # ── Liste des cours ──
    st.markdown("### 📚 Cours indexés")
    courses = get_all_courses()

    if not courses:
        st.markdown("""
        <div class="alert-warning">
            📭 Aucun cours indexé. Upload ton premier cours ci-dessus !
        </div>
        """, unsafe_allow_html=True)
        return

    for course in courses:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

            indexed = course_is_indexed(course['id'])
            status_icon = "🟢" if indexed else "🔴"

            with col1:
                st.markdown(f"""
                <div style="padding:8px 0;">
                    <div style="color:#c8c8ff; font-weight:500;">{status_icon} {course['title']}</div>
                    <div style="color:#5a5a8a; font-size:0.78rem;">
                        {course['filename']} · {course['num_chunks']} chunks · {course['uploaded_at'][:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("💬 Chat", key=f"c_chat_{course['id']}"):
                    st.session_state.selected_course_id = course['id']
                    st.session_state.current_page = "chat"
                    st.session_state.chat_messages = []
                    st.session_state.chat_display = []
                    st.rerun()

            with col3:
                if st.button("📝 Quiz", key=f"c_quiz_{course['id']}"):
                    st.session_state.selected_course_id = course['id']
                    st.session_state.current_page = "quiz"
                    st.rerun()

            with col4:
                if st.button("🔄 Ré-indexer", key=f"c_reindex_{course['id']}"):
                    filepath = os.path.join(COURSES_DIR, course['filename'])
                    if os.path.exists(filepath):
                        with st.spinner("Ré-indexation..."):
                            parsed = parse_course_file(filepath, chunk_size=800)
                            index_course(course['id'], parsed['chunks'])
                            # Update num_chunks in DB
                            conn = get_connection()
                            conn.execute("UPDATE courses SET num_chunks=? WHERE id=?",
                                         (parsed['num_chunks'], course['id']))
                            conn.commit()
                            conn.close()
                        st.success("✅ Ré-indexé !")
                        st.rerun()
                    else:
                        st.error("Fichier introuvable")

            with col5:
                if st.button("🗑️", key=f"c_del_{course['id']}"):
                    delete_course_index(course['id'])
                    conn = get_connection()
                    conn.execute("DELETE FROM courses WHERE id=?", (course['id'],))
                    conn.commit()
                    conn.close()
                    st.success("Cours supprimé")
                    st.rerun()

        st.markdown("<hr style='border-color:#1e1e3a; margin:4px 0;'>", unsafe_allow_html=True)

    # ── Cours exemple ──
    st.markdown("---")
    st.markdown("### 📖 Cours exemple disponibles")
    st.markdown("""
    <div class="sb-card">
        <div style="color:#8888aa; font-size:0.9rem;">
            💡 <b>Conseil :</b> Pour tester rapidement, tu peux uploader n'importe quel cours PDF
            de ta filière IA & Data Science (Machine Learning, Deep Learning, NLP, Python, etc.)
        </div>
    </div>
    """, unsafe_allow_html=True)


def _process_upload(uploaded_file, custom_title: str, chunk_size: int):
    """Traite l'upload : sauvegarde fichier, parse, indexe, enregistre en DB."""
    Path(COURSES_DIR).mkdir(parents=True, exist_ok=True)

    filename = uploaded_file.name
    filepath = os.path.join(COURSES_DIR, filename)

    # Sauvegarder le fichier
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    progress_bar = st.progress(0, text="Extraction du texte...")

    try:
        # Parser
        progress_bar.progress(25, text="Extraction et chunking...")
        parsed = parse_course_file(filepath, chunk_size=chunk_size)

        title = custom_title.strip() if custom_title.strip() else parsed['title']

        progress_bar.progress(50, text="Création des embeddings...")

        # Sauvegarder en DB
        course_id = save_course(title, filename, FILIERE, parsed['num_chunks'])

        progress_bar.progress(75, text="Indexation vectorielle...")

        # Indexer
        index_course(course_id, parsed['chunks'])

        progress_bar.progress(100, text="Terminé !")

        st.markdown(f"""
        <div class="alert-success">
            ✅ <b>"{title}"</b> indexé avec succès !<br>
            {parsed['num_chunks']} chunks créés et prêts pour le tuteur IA.
        </div>
        """, unsafe_allow_html=True)

        st.balloons()
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Erreur lors de l'indexation : {str(e)}")
        # Nettoyer le fichier en cas d'erreur
        if os.path.exists(filepath):
            os.remove(filepath)
