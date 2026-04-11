# frontend/page_quiz.py

import streamlit as st
from backend.database import (get_all_courses, save_quiz_result,
                               get_weaknesses, get_student_stats)
from backend.ai_tutor import generate_quiz, generate_targeted_quiz, analyze_weaknesses


def render_quiz():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div class="sb-title">📝 Quiz Adaptatif</div>
        <div class="sb-subtitle">Teste tes connaissances — les lacunes sont détectées automatiquement</div>
    </div>
    """, unsafe_allow_html=True)

    courses = get_all_courses()
    if not courses:
        st.warning("⚠️ Upload un cours avant de faire le quiz.")
        if st.button("📂 Uploader un cours"):
            st.session_state.current_page = "courses"
            st.rerun()
        return

    # ── Mode sélection ou affichage quiz ──
    if st.session_state.quiz_data is None:
        _render_quiz_setup(courses)
    elif st.session_state.quiz_submitted:
        _render_quiz_results()
    else:
        _render_quiz_questions()


def _render_quiz_setup(courses):
    """Interface de configuration du quiz."""
    tab1, tab2 = st.tabs(["📝 Quiz sur un cours", "🎯 Quiz ciblé sur mes lacunes"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            course_options = {c['title']: c['id'] for c in courses}

            default_idx = 0
            if st.session_state.selected_course_id:
                for i, c in enumerate(courses):
                    if c['id'] == st.session_state.selected_course_id:
                        default_idx = i
                        break

            selected_title = st.selectbox("📚 Cours", list(course_options.keys()), index=default_idx)
            selected_course_id = course_options[selected_title]

            topic = st.text_input(
                "🎯 Sujet précis (optionnel)",
                placeholder="Ex: Réseaux de neurones convolutifs, Overfitting..."
            )

        with col2:
            num_questions = st.slider("Nombre de questions", 3, 10, 5)
            difficulty = st.select_slider(
                "Difficulté",
                options=["facile", "moyen", "difficile"],
                value="moyen"
            )

        if st.button("🚀 Générer le quiz", use_container_width=True):
            topic_final = topic.strip() if topic.strip() else selected_title
            with st.spinner(f"Génération de {num_questions} questions sur '{topic_final}'..."):
                quiz = generate_quiz(
                    course_id=selected_course_id,
                    topic=topic_final,
                    num_questions=num_questions,
                    difficulty=difficulty
                )

                if quiz.get("questions"):
                    st.session_state.quiz_data = quiz
                    st.session_state.quiz_data["course_id"] = selected_course_id
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.wrong_answers_session = []
                    st.rerun()
                else:
                    st.error(f"❌ Impossible de générer le quiz. {quiz.get('error', '')}")

    with tab2:
        weaknesses = get_weaknesses(st.session_state.student_id)

        if not weaknesses:
            st.markdown("""
            <div class="alert-success">
                ✅ Aucune lacune détectée. Fais d'abord un quiz normal pour que je puisse identifier tes points faibles !
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("#### Tes lacunes détectées :")
            for w in weaknesses[:8]:
                icon = "🔴" if w['fail_count'] >= 3 else "🟡"
                st.markdown(f'<span class="weakness-tag">{icon} {w["concept"]} ({w["fail_count"]}x)</span>',
                            unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_course, col_num = st.columns(2)
            with col_course:
                course_options_w = {c['title']: c['id'] for c in courses}
                selected_title_w = st.selectbox("Cours de référence", list(course_options_w.keys()), key="weakness_course")
                selected_course_id_w = course_options_w[selected_title_w]
            with col_num:
                num_q_w = st.slider("Questions par concept", 2, 5, 3, key="weakness_num")

            if st.button("🎯 Lancer le quiz ciblé", use_container_width=True):
                weak_concepts = [w['concept'] for w in weaknesses[:3]]
                with st.spinner("Génération du quiz adaptatif sur tes lacunes..."):
                    quizzes = generate_targeted_quiz(selected_course_id_w, weak_concepts, num_q_w)

                    if quizzes:
                        # Fusionner tous les quiz en un seul
                        all_questions = []
                        for q in quizzes:
                            for question in q.get("questions", []):
                                question["concept"] = q.get("concept", "?")
                                all_questions.append(question)

                        merged_quiz = {
                            "concept": "Quiz ciblé — Lacunes",
                            "questions": all_questions,
                            "course_id": selected_course_id_w,
                            "is_targeted": True
                        }
                        st.session_state.quiz_data = merged_quiz
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.wrong_answers_session = []
                        st.rerun()
                    else:
                        st.error("Impossible de générer le quiz ciblé.")


def _render_quiz_questions():
    """Affiche les questions du quiz."""
    quiz = st.session_state.quiz_data
    questions = quiz.get("questions", [])

    if not questions:
        st.error("Aucune question disponible.")
        st.session_state.quiz_data = None
        st.rerun()
        return

    # Header
    is_targeted = quiz.get("is_targeted", False)
    badge = "🎯 Quiz Ciblé" if is_targeted else "📝 Quiz Standard"
    st.markdown(f"""
    <div class="sb-card" style="margin-bottom:20px;">
        <span style="color:#b8b8ff; font-weight:600;">{badge}</span>
        <span style="color:#6868aa; font-size:0.9rem; margin-left:12px;">{quiz.get('concept', '')}</span>
        <span style="color:#5a5a8a; font-size:0.8rem; float:right;">{len(questions)} questions</span>
    </div>
    """, unsafe_allow_html=True)

    # Questions
    all_answered = True
    for i, q in enumerate(questions):
        q_id = str(q.get("id", i))
        concept = q.get("concept", quiz.get("concept", "?"))

        st.markdown(f"""
        <div class="quiz-question">
            <h4>Question {i+1} · <span style="color:#7878cc; font-size:0.85rem;">{concept}</span></h4>
            <div style="color:#d8d8ff; font-size:1rem; margin-bottom:12px;">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        choices = q.get("choices", [])
        answer = st.radio(
            f"Choix pour Q{i+1}",
            choices,
            key=f"quiz_q_{q_id}_{i}",
            label_visibility="collapsed"
        )
        st.session_state.quiz_answers[q_id] = {
            "selected": answer,
            "correct": q.get("correct_answer", ""),
            "correct_index": q.get("correct_index", 0),
            "explanation": q.get("explanation", ""),
            "question": q['question'],
            "concept": concept,
            "choices": choices
        }

        if answer is None:
            all_answered = False

        st.markdown("<br>", unsafe_allow_html=True)

    # Bouton soumettre
    col1, col2 = st.columns([3, 1])
    with col1:
        progress = len([a for a in st.session_state.quiz_answers.values() if a.get("selected")]) / len(questions)
        st.progress(progress, text=f"{int(progress*100)}% complété")

    with col2:
        if st.button("✅ Soumettre le quiz", use_container_width=True):
            _submit_quiz()


def _submit_quiz():
    """Calcule les résultats et sauvegarde."""
    quiz = st.session_state.quiz_data
    wrong_answers = []

    for q_id, answer_data in st.session_state.quiz_answers.items():
        selected = answer_data.get("selected", "")
        correct = answer_data.get("correct", "")
        is_correct = selected == correct

        if not is_correct:
            wrong_answers.append({
                "question": answer_data["question"],
                "concept": answer_data["concept"],
                "student_answer": selected,
                "correct": correct
            })

        save_quiz_result(
            student_id=st.session_state.student_id,
            course_id=quiz.get("course_id"),
            concept=answer_data["concept"],
            question=answer_data["question"],
            student_answer=selected,
            correct_answer=correct,
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0
        )

    st.session_state.quiz_submitted = True
    st.session_state.wrong_answers_session = wrong_answers
    st.rerun()


def _render_quiz_results():
    """Affiche les résultats du quiz."""
    quiz = st.session_state.quiz_data
    answers = st.session_state.quiz_answers
    wrong = st.session_state.wrong_answers_session
    total = len(answers)
    correct_count = total - len(wrong)
    score_pct = round((correct_count / total * 100) if total > 0 else 0)

    # Score header
    score_color = "#7bff7b" if score_pct >= 70 else "#ffbb7b" if score_pct >= 50 else "#ff7b7b"
    st.markdown(f"""
    <div style="text-align:center; padding:32px 0;">
        <div style="font-family:'Space Mono',monospace; font-size:3.5rem; font-weight:700; color:{score_color};">
            {score_pct}%
        </div>
        <div style="color:#8888aa; font-size:1rem; margin-top:8px;">
            {correct_count} / {total} bonnes réponses
        </div>
        <div style="color:#6868aa; font-size:0.85rem; margin-top:4px;">
            {"🎉 Excellent !" if score_pct >= 80 else "👍 Bien !" if score_pct >= 60 else "💪 Continue !" if score_pct >= 40 else "📚 Relis le cours !"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(score_pct / 100)

    # Analyse des lacunes
    if wrong:
        st.markdown("---")
        st.markdown("### ⚠️ Analyse de tes erreurs")
        with st.spinner("Analyse des lacunes en cours..."):
            analysis = analyze_weaknesses(wrong, quiz.get("course_id"))

        if analysis.get("concepts_faibles"):
            st.markdown("**Concepts à retravailler :**")
            for c in analysis["concepts_faibles"]:
                st.markdown(f'<span class="weakness-tag">⚠️ {c}</span>', unsafe_allow_html=True)

        if analysis.get("analyse"):
            st.markdown(f"""
            <div class="sb-card" style="margin-top:16px;">
                <div style="color:#8888aa; font-size:0.85rem; margin-bottom:8px;">📊 Analyse IA</div>
                <div style="color:#c8c8e8; font-size:0.95rem;">{analysis['analyse']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Détail des réponses
    st.markdown("---")
    st.markdown("### 📋 Détail des réponses")

    for i, (q_id, answer_data) in enumerate(answers.items()):
        is_correct = answer_data["selected"] == answer_data["correct"]
        icon = "✅" if is_correct else "❌"
        bg_color = "#0a2a0a" if is_correct else "#2a0a0a"
        border_color = "#1a6a1a" if is_correct else "#6a1a1a"

        st.markdown(f"""
        <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:10px;
                    padding:16px; margin-bottom:12px;">
            <div style="color:#d8d8ff; font-weight:500; margin-bottom:8px;">
                {icon} Q{i+1}: {answer_data['question']}
            </div>
            <div style="font-size:0.85rem; color:#888899;">
                Ta réponse : <span style="color:{'#88ff88' if is_correct else '#ff8888'};">
                    {answer_data['selected']}
                </span>
            </div>
            {"" if is_correct else f'<div style="font-size:0.85rem; color:#888899; margin-top:4px;">Correcte : <span style="color:#88ff88;">{answer_data["correct"]}</span></div>'}
            {"" if is_correct else f'<div style="font-size:0.82rem; color:#6a8a6a; margin-top:8px; font-style:italic;">💡 {answer_data.get("explanation", "")}</div>'}
        </div>
        """, unsafe_allow_html=True)

    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Nouveau quiz", use_container_width=True):
            st.session_state.quiz_data = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

    with col2:
        if wrong and st.button("🎯 Quiz sur mes lacunes", use_container_width=True):
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
            st.rerun()

    with col3:
        if st.button("💬 Demander une explication", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
