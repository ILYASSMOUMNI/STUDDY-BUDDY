# frontend/page_dashboard.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from backend.database import (get_student_stats, get_weaknesses,
                               get_all_courses, get_connection)


def render_dashboard():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div class="sb-title">📊 Dashboard</div>
        <div class="sb-subtitle">Visualise ta progression et tes lacunes</div>
    </div>
    """, unsafe_allow_html=True)

    student_id = st.session_state.student_id
    stats = get_student_stats(student_id)
    weaknesses = get_weaknesses(student_id)
    courses = get_all_courses()

    # ── KPIs ──
    c1, c2, c3, c4 = st.columns(4)

    score_color = "#7bff7b" if stats['score_global'] >= 70 else "#ffbb7b" if stats['score_global'] >= 50 else "#ff7b7b"

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{stats['total_questions']}</div>
            <div class="metric-label">Questions répondues</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{stats['correct_answers']}</div>
            <div class="metric-label">Bonnes réponses</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{score_color};">{stats['score_global']}%</div>
            <div class="metric-label">Score global</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#ff7bbb;">{len(weaknesses)}</div>
            <div class="metric-label">Lacunes actives</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # ── Graphe 1 : Score par cours ──
    with col_left:
        st.markdown("#### 📚 Performance par cours")
        if stats['by_course']:
            df_courses = pd.DataFrame(stats['by_course'])
            df_courses['score_pct'] = (df_courses['correct_count'] / df_courses['attempts'] * 100).round(1)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_courses['title'],
                y=df_courses['score_pct'],
                marker_color=[
                    '#7bff7b' if s >= 70 else '#ffbb7b' if s >= 50 else '#ff7b7b'
                    for s in df_courses['score_pct']
                ],
                text=df_courses['score_pct'].astype(str) + '%',
                textposition='outside'
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c8c8e8',
                xaxis=dict(gridcolor='#2a2a4a', tickangle=-20),
                yaxis=dict(gridcolor='#2a2a4a', range=[0, 115]),
                margin=dict(l=20, r=20, t=20, b=80),
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""<div style="text-align:center; color:#4a4a6a; padding:60px 0;">
                Aucune donnée quiz pour l'instant
            </div>""", unsafe_allow_html=True)

    # ── Graphe 2 : Lacunes (radar ou bar) ──
    with col_right:
        st.markdown("#### ⚠️ Top Lacunes")
        if weaknesses:
            top_w = weaknesses[:8]
            df_w = pd.DataFrame(top_w)

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_w['fail_count'],
                y=df_w['concept'],
                orientation='h',
                marker=dict(
                    color=df_w['fail_count'],
                    colorscale=[[0, '#ff9944'], [0.5, '#ff5544'], [1, '#ff1111']],
                ),
                text=df_w['fail_count'].astype(str) + ' erreurs',
                textposition='outside'
            ))
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c8c8e8',
                xaxis=dict(gridcolor='#2a2a4a'),
                yaxis=dict(gridcolor='#2a2a4a'),
                margin=dict(l=20, r=80, t=20, b=20),
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown("""<div style="text-align:center; color:#4a4a6a; padding:60px 0;">
                🎉 Aucune lacune détectée !
            </div>""", unsafe_allow_html=True)

    # ── Historique des quiz ──
    st.markdown("---")
    st.markdown("#### 🕐 Historique des quiz")

    conn = get_connection()
    df_history = pd.read_sql_query("""
        SELECT qr.taken_at, c.title as cours, qr.concept,
               qr.question, qr.is_correct, qr.student_answer, qr.correct_answer
        FROM quiz_results qr
        LEFT JOIN courses c ON qr.course_id = c.id
        WHERE qr.student_id = ?
        ORDER BY qr.taken_at DESC
        LIMIT 50
    """, conn, params=(student_id,))
    conn.close()

    if df_history.empty:
        st.markdown("""<div class="alert-warning">
            Pas encore de quiz complété. Va dans l'onglet Quiz pour commencer !
        </div>""", unsafe_allow_html=True)
    else:
        # Courbe de progression dans le temps
        df_history['taken_at'] = pd.to_datetime(df_history['taken_at'])
        df_history['date'] = df_history['taken_at'].dt.date

        df_daily = df_history.groupby('date').agg(
            total=('is_correct', 'count'),
            correct=('is_correct', 'sum')
        ).reset_index()
        df_daily['score_pct'] = (df_daily['correct'] / df_daily['total'] * 100).round(1)

        if len(df_daily) > 1:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['score_pct'],
                mode='lines+markers',
                line=dict(color='#7b7bff', width=2),
                marker=dict(size=8, color='#b8b8ff'),
                fill='tozeroy',
                fillcolor='rgba(123, 123, 255, 0.1)'
            ))
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#c8c8e8',
                xaxis=dict(gridcolor='#2a2a4a'),
                yaxis=dict(gridcolor='#2a2a4a', range=[0, 115]),
                margin=dict(l=20, r=20, t=20, b=20),
                height=220,
                showlegend=False,
                title=dict(text="Évolution du score dans le temps", font_color='#8888aa', font_size=13)
            )
            st.plotly_chart(fig3, use_container_width=True)

        # Table
        df_display = df_history[['taken_at', 'cours', 'concept', 'is_correct']].copy()
        df_display['is_correct'] = df_display['is_correct'].map({1: '✅', 0: '❌'})
        df_display.columns = ['Date', 'Cours', 'Concept', 'Résultat']
        df_display['Date'] = df_display['Date'].dt.strftime('%d/%m %H:%M')

        st.dataframe(
            df_display,
            use_container_width=True,
            height=300,
            hide_index=True
        )

    # ── Recommandations ──
    st.markdown("---")
    st.markdown("#### 💡 Recommandations personnalisées")

    if weaknesses:
        top3 = weaknesses[:3]
        cols = st.columns(len(top3))
        for i, w in enumerate(top3):
            with cols[i]:
                urgence = "🔴 Urgent" if w['fail_count'] >= 3 else "🟡 À retravailler"
                st.markdown(f"""
                <div class="sb-card" style="text-align:center; padding:16px;">
                    <div style="color:#ffaaaa; font-size:0.75rem; text-transform:uppercase;
                                letter-spacing:0.1em; margin-bottom:8px;">{urgence}</div>
                    <div style="color:#e8e8ff; font-weight:600; margin-bottom:8px;">{w['concept']}</div>
                    <div style="color:#6868aa; font-size:0.8rem;">{w['fail_count']} erreur(s) enregistrée(s)</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🎯 Quiz sur ce concept", key=f"reco_{i}", use_container_width=True):
                    st.session_state.current_page = "quiz"
                    st.rerun()
    else:
        st.markdown("""
        <div class="alert-success">
            ✅ Aucune lacune détectée ! Continue comme ça et essaie des quiz plus difficiles.
        </div>
        """, unsafe_allow_html=True)
