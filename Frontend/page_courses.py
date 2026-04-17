# frontend/page_courses.py

import streamlit as st, os
from pathlib import Path
from backend.database import save_course, get_all_courses, get_connection
from backend.course_parser import parse_course_file
from backend.vector_store import index_course, delete_course_index, course_is_indexed
from frontend.design_system import C, page_title, badge, spacer, divider, inline_alert
from dotenv import load_dotenv

load_dotenv()
COURSES_DIR = os.getenv("COURSES_DIR", "./data/courses")
FILIERE     = os.getenv("FILIERE", "IA & Data Science")


def render_courses():
    col_t, col_b = st.columns([4, 1])
    with col_t:
        page_title("Courses", "Upload and manage your course materials.")
    with col_b:
        spacer(28)
        if st.button("📤 Upload new", type="primary", use_container_width=True):
            st.session_state["show_upload"] = not st.session_state.get("show_upload", False)

    # ── Upload panel (toggle) ────────────────────────────────
    if st.session_state.get("show_upload", False):
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:24px;margin-bottom:20px;
            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <p style="font-size:0.75rem;font-weight:700;color:{C["text_2"]};
              margin-bottom:16px;text-transform:uppercase;letter-spacing:0.1em;">
        📁 Upload course
    </p>
""", unsafe_allow_html=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            uploaded    = st.file_uploader("File", type=["pdf","docx","txt"],
                                           label_visibility="collapsed")
        with c2:
            custom_title = st.text_input("Title (optional)", placeholder="E.g. ML Chapter 3")
            chunk_size   = st.slider("Chunk size", 400, 1200, 800, 100)

        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded and st.button("🚀 Index course", type="primary"):
            _upload(uploaded, custom_title, chunk_size)
            st.session_state["show_upload"] = False

    # ── Table ────────────────────────────────────────────────
    courses = get_all_courses()

    if not courses:
        inline_alert("No courses indexed yet. Upload your first course above.", "info")
        return

    # Table header
    st.markdown(f"""
<div style="background:{C["surface_2"]};border:1px solid {C["border"]};
            border-radius:12px 12px 0 0;
            display:grid;
            grid-template-columns:2.5fr 90px 90px 160px;
            gap:12px;padding:12px 18px;">
    <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:{C["text_3"]};">Course name</div>
    <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:{C["text_3"]};text-align:center;">
        Chunks</div>
    <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:{C["text_3"]};text-align:center;">
        Status</div>
    <div style="font-size:0.75rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:{C["text_3"]};text-align:center;">
        Actions</div>
</div>""", unsafe_allow_html=True)

    for i, c in enumerate(courses):
        indexed = course_is_indexed(c["id"])
        status_badge = badge("✓ Indexed", "green") if indexed else badge("pending", "gray")
        radius = "0 0 12px 12px" if i == len(courses) - 1 else "0"
        bg = C["surface"] if i % 2 == 0 else C["surface_2"]

        st.markdown(f"""
<div style="background:{bg};border:1px solid {C["border"]};
            border-top:none;border-radius:{radius};
            display:grid;grid-template-columns:2.5fr 90px 90px 160px;
            gap:12px;padding:14px 18px;align-items:center;
            transition:background 0.2s ease;">
    <div>
        <div style="font-weight:600;font-size:0.9rem;color:{C["text"]};">
            {c['title']}
        </div>
        <div style="font-size:0.75rem;color:{C["text_3"]};margin-top:4px;
                    font-family:'JetBrains Mono',monospace;">
            {c['filename']} · {c['uploaded_at'][:10]}
        </div>
    </div>
    <div style="text-align:center;font-family:'JetBrains Mono',monospace;
                font-size:0.85rem;font-weight:600;color:{C["indigo"]};">{c['num_chunks']}</div>
    <div style="text-align:center;">{status_badge}</div>
</div>""", unsafe_allow_html=True)

        _, ca, cb, cc, cd = st.columns([3.5, 0.8, 0.8, 0.9, 0.7])
        with ca:
            if st.button("Chat", key=f"cc_{c['id']}", use_container_width=True, type="secondary"):
                st.session_state.selected_course_id = c["id"]
                st.session_state.current_page = "chat"
                st.session_state.chat_messages = []
                st.session_state.chat_display  = []
                st.rerun()
        with cb:
            if st.button("Quiz", key=f"cq_{c['id']}", use_container_width=True, type="secondary"):
                st.session_state.selected_course_id = c["id"]
                st.session_state.current_page = "quiz"
                st.rerun()
        with cc:
            if st.button("Re-index", key=f"cr_{c['id']}", use_container_width=True, type="secondary"):
                fp = os.path.join(COURSES_DIR, c["filename"])
                if os.path.exists(fp):
                    with st.spinner("Re-indexing…"):
                        p = parse_course_file(fp, chunk_size=800)
                        index_course(c["id"], p["chunks"])
                        conn = get_connection()
                        conn.execute("UPDATE courses SET num_chunks=? WHERE id=?",
                                     (p["num_chunks"], c["id"]))
                        conn.commit(); conn.close()
                    st.rerun()
        with cd:
            if st.button("Del", key=f"cd_{c['id']}", use_container_width=True, type="secondary"):
                st.session_state[f"confirm_del_{c['id']}"] = True

        if st.session_state.get(f"confirm_del_{c['id']}", False):
            st.warning(f"Delete **{c['title']}**? This cannot be undone.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Confirm", key=f"yes_{c['id']}", type="primary",
                             use_container_width=True):
                    delete_course_index(c["id"])
                    conn = get_connection()
                    conn.execute("DELETE FROM courses WHERE id=?", (c["id"],))
                    conn.commit(); conn.close()
                    del st.session_state[f"confirm_del_{c['id']}"]
                    st.rerun()
            with col_no:
                if st.button("Cancel", key=f"no_{c['id']}", use_container_width=True):
                    del st.session_state[f"confirm_del_{c['id']}"]
                    st.rerun()
        spacer(2)

    st.markdown(f"""
<p style="font-size:0.8rem;color:{C["text_3"]};margin-top:12px;">
    Showing {len(courses)} course(s) total
</p>""", unsafe_allow_html=True)


def _upload(uploaded_file, custom_title, chunk_size):
    Path(COURSES_DIR).mkdir(parents=True, exist_ok=True)
    fp = os.path.join(COURSES_DIR, uploaded_file.name)
    with open(fp, "wb") as f:
        f.write(uploaded_file.getbuffer())
    bar = st.progress(0, text="Extracting text…")
    try:
        bar.progress(30, text="Chunking…")
        parsed = parse_course_file(fp, chunk_size=chunk_size)
        title  = custom_title.strip() or parsed["title"]
        bar.progress(60, text="Embedding…")
        cid = save_course(title, uploaded_file.name, FILIERE, parsed["num_chunks"])
        bar.progress(85, text="Indexing…")
        index_course(cid, parsed["chunks"])
        bar.progress(100, text="Done.")
        st.success(f'"{title}" — {parsed["num_chunks"]} chunks indexed.')
        st.rerun()
    except Exception as e:
        bar.empty()
        st.error(f"Error: {e}")
        if os.path.exists(fp): os.remove(fp)
