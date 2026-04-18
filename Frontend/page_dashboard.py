# frontend/page_dashboard.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from backend.database import (get_student_stats, get_weaknesses,
                               get_all_courses, get_connection)
from backend.ai_tutor import generate_study_plan, generate_progress_report
from backend.email_service import send_weekly_summary, is_configured as email_configured
from frontend.design_system import C, page_title, kpi_card, badge, spacer, divider


_LAYOUT = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family="Inter, sans-serif",
                         color=C["text_2"], size=12),
    margin        = dict(l=0, r=8, t=8, b=0),
    showlegend    = False,
)


def render_dashboard():
    lang  = st.session_state.get("language", "fr")
    title = "📊 Analytiques" if lang == "fr" else "📊 Analytics"
    sub   = ("Suivez votre progression et identifiez vos points faibles."
             if lang == "fr"
             else "Track your learning progress and identify areas for improvement.")
    page_title(title, sub)

    sid   = st.session_state.student_id
    stats = get_student_stats(sid)
    weak  = get_weaknesses(sid)
    score = stats["score_global"]
    s_color = C["green"] if score >= 70 else C["orange"] if score >= 50 else C["red"]

    # ── KPIs ─────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card(str(stats["total_questions"]), "Total questions", accent_color=C["blue"])
    with k2: kpi_card(str(stats["correct_answers"]), "Correct answers",
                      accent_color=C["green"])
    with k3: kpi_card(f"{score}%", "Success rate", accent_color=s_color)
    with k4: kpi_card(str(len(weak)), "Weak concepts",
                      accent_color=C["red"] if weak else C["green"])

    spacer(28)

    # ── Charts ───────────────────────────────────────────────
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:22px 24px;
            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <p style="font-size:0.85rem;font-weight:700;color:{C["text"]};
              margin-bottom:18px;">📈 Score by course</p>
""", unsafe_allow_html=True)

        if stats["by_course"]:
            df = pd.DataFrame(stats["by_course"])
            df["pct"] = (df["correct_count"] / df["attempts"].replace(0, float("nan")) * 100).fillna(0).round(1)
            colors = [C["green"] if p >= 70 else C["orange"] if p >= 50
                      else C["red"] for p in df["pct"]]
            fig = go.Figure(go.Bar(
                x=df["pct"], y=df["title"], orientation="h",
                marker=dict(color=colors, line=dict(width=0)),
                text=df["pct"].astype(str) + "%",
                textposition="outside", textfont=dict(size=11)
            ))
            fig.update_layout(**_LAYOUT, height=220,
                xaxis=dict(range=[0,120], gridcolor=C["border"], zeroline=False),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"""
<p style="font-size:0.9rem;color:{C["text_3"]};padding:24px 0;text-align:center;">
    📭 No quiz data yet.
</p>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:22px 24px;
            box-shadow:0 4px 12px rgba(0,0,0,0.3);">
    <p style="font-size:0.85rem;font-weight:700;color:{C["text"]};
              margin-bottom:18px;">⚠️ Weak concepts</p>
""", unsafe_allow_html=True)

        if weak:
            df_w = pd.DataFrame(weak[:8])
            opacity = [min(0.35 + i * 0.09, 1.0) for i in range(len(df_w))]
            fig2 = go.Figure(go.Bar(
                x=df_w["fail_count"], y=df_w["concept"],
                orientation="h",
                marker=dict(color=C["red"], opacity=opacity,
                            line=dict(width=0)),
                text=df_w["fail_count"].astype(str) + "x",
                textposition="outside", textfont=dict(size=11)
            ))
            fig2.update_layout(**_LAYOUT, height=220,
                xaxis=dict(gridcolor=C["border"], zeroline=False),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(f"""
<p style="font-size:0.875rem;color:{C["text_3"]};padding:20px 0;text-align:center;">
    No weak concepts detected.
</p>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    spacer(24)

    # ── Progress over time ────────────────────────────────────
    conn = get_connection()
    df_h = pd.read_sql_query("""
        SELECT qr.taken_at, c.title as course,
               qr.concept, qr.is_correct
        FROM quiz_results qr
        LEFT JOIN courses c ON qr.course_id = c.id
        WHERE qr.student_id = ?
        ORDER BY qr.taken_at DESC LIMIT 200
    """, conn, params=(sid,))
    conn.close()

    st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;padding:20px 22px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04);">
    <p style="font-size:0.8125rem;font-weight:600;color:{C["text"]};
              margin-bottom:16px;">Progress over time</p>
""", unsafe_allow_html=True)

    if not df_h.empty:
        df_h["taken_at"] = pd.to_datetime(df_h["taken_at"])
        df_h["date"]     = df_h["taken_at"].dt.date
        df_d = df_h.groupby("date").agg(
            total=("is_correct","count"),
            ok=("is_correct","sum")
        ).reset_index()
        df_d["pct"] = (df_d["ok"] / df_d["total"] * 100).round(1)

        if len(df_d) > 1:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_d["date"], y=df_d["pct"],
                mode="lines+markers",
                line=dict(color=C["indigo"], width=2),
                marker=dict(size=5, color=C["indigo"],
                            line=dict(color="#fff", width=1.5)),
                fill="tozeroy",
                fillcolor=f"rgba(75,78,222,0.05)"
            ))
            fig3.update_layout(**_LAYOUT, height=180,
                xaxis=dict(gridcolor=C["border"], zeroline=False),
                yaxis=dict(gridcolor=C["border"], zeroline=False,
                           range=[0,110]))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.markdown(f"""
<p style="font-size:0.875rem;color:{C["text_3"]};padding:8px 0;">
    Complete more quizzes to see your progress curve.
</p>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<p style="font-size:0.875rem;color:{C["text_3"]};padding:8px 0;">
    No quiz history yet.
</p>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    spacer(24)

    # ── Recent activity table ─────────────────────────────────
    if not df_h.empty:
        rows_html = ""
        for i, row in df_h.head(12).iterrows():
            ok           = int(row["is_correct"]) == 1
            bg           = C["surface"] if i % 2 == 0 else C["surface_2"]
            result_badge = badge("Correct", "green") if ok else badge("Incorrect", "red")
            date_fmt     = row["taken_at"].strftime("%d %b %H:%M")
            course_name  = (row["course"] or "—")[:28]
            concept_name = (row["concept"] or "—")[:28]
            rows_html += f"""
<div style="background:{bg};border-bottom:1px solid {C["border"]};
            display:grid;grid-template-columns:1fr 1.5fr 1.2fr 80px;
            gap:12px;padding:10px 20px;align-items:center;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                 color:{C["text_3"]};">{date_fmt}</span>
    <span style="font-size:0.8125rem;color:{C["text"]};font-weight:500;
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {course_name}
    </span>
    <span style="font-size:0.8125rem;color:{C["text_2"]};
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {concept_name}
    </span>
    <span>{result_badge}</span>
</div>"""

        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:12px;overflow:hidden;
            box-shadow:0 2px 12px rgba(15,23,42,0.06);">
    <div style="padding:16px 20px;border-bottom:1px solid {C["border"]};">
        <span style="font-size:0.8125rem;font-weight:600;color:{C["text"]};">
            Recent activity
        </span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1.5fr 1.2fr 80px;
                gap:12px;padding:8px 20px;
                background:{C["surface_2"]};
                border-bottom:1px solid {C["border"]};">
        <span style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
                     text-transform:uppercase;color:{C["text_3"]};">Date</span>
        <span style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
                     text-transform:uppercase;color:{C["text_3"]};">Course</span>
        <span style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
                     text-transform:uppercase;color:{C["text_3"]};">Concept</span>
        <span style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
                     text-transform:uppercase;color:{C["text_3"]};">Result</span>
    </div>
    {rows_html}
</div>""", unsafe_allow_html=True)

    # ── Recommendations ───────────────────────────────────────
    if weak:
        spacer(24)
        rec_label = "Pratique recommandée" if lang == "fr" else "Recommended practice"
        st.markdown(f"""
<p style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:12px;">
    {rec_label}
</p>""", unsafe_allow_html=True)

        cols = st.columns(min(len(weak[:3]), 3))
        for i, w in enumerate(weak[:3]):
            with cols[i]:
                urgency = ("Priorité haute" if lang == "fr" else "High priority") if w["fail_count"] >= 3 else ("À revoir" if lang == "fr" else "Review")
                bc = "red" if w["fail_count"] >= 3 else "orange"
                mistakes_txt = f"{w['fail_count']} erreur(s)" if lang == "fr" else f"{w['fail_count']} mistake(s)"
                st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};
            border-radius:10px;padding:16px 18px;height:100px;">
    <div style="margin-bottom:8px;">{badge(urgency, bc)}</div>
    <div style="font-weight:600;font-size:0.875rem;color:{C["text"]};
                margin-bottom:3px;">{w['concept']}</div>
    <div style="font-size:0.75rem;color:{C["text_3"]};">{mistakes_txt}</div>
</div>""", unsafe_allow_html=True)
                prac_btn = "Pratiquer" if lang == "fr" else "Practice"
                if st.button(prac_btn, key=f"rec_{i}",
                             use_container_width=True, type="secondary"):
                    st.session_state.current_page = "quiz"
                    st.rerun()

    # ── Plan d'étude IA personnalisé ──────────────────────────
    spacer(28)
    plan_header = "Plan d'Étude Personnalisé" if lang == "fr" else "Personalized Study Plan"
    plan_sub    = ("Généré par l'IA selon vos lacunes et votre niveau."
                   if lang == "fr" else "AI-generated based on your weaknesses and level.")
    st.markdown(f"""
<p style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
          text-transform:uppercase;color:{C["text_3"]};margin-bottom:4px;">{plan_header}</p>
<p style="font-size:0.8125rem;color:{C["text_3"]};margin-bottom:12px;">{plan_sub}</p>
""", unsafe_allow_html=True)

    plan_btn_label = "🤖 Générer mon plan d'étude" if lang == "fr" else "🤖 Generate my study plan"
    if st.button(plan_btn_label, key="dash_gen_plan", type="secondary"):
        with st.spinner("Analyse de votre profil…" if lang == "fr" else "Analysing your profile…"):
            plan = generate_study_plan(weak, stats, language=lang)
        st.session_state["_dash_study_plan"] = plan

    if st.session_state.get("_dash_study_plan"):
        plan = st.session_state["_dash_study_plan"]
        st.markdown(f"""
<div style="background:{C["surface"]};border:1px solid {C["border"]};border-radius:12px;
            padding:20px 24px;margin-top:8px;">
  <div style="font-weight:700;color:{C["text"]};margin-bottom:4px;">
    🎯 {plan.get('objectif', '')}
  </div>
  <div style="font-size:0.85rem;color:{C["text_2"]};margin-bottom:14px;">
    {plan.get('conseil_general', '')}
  </div>""", unsafe_allow_html=True)
        for sess in plan.get("sessions", [])[:5]:
            prio = sess.get("priorite", "")
            pcolor = C["red"] if prio == "haute" else C["orange"] if prio == "moyenne" else C["text_3"]
            st.markdown(f"""
  <div style="display:flex;align-items:center;gap:12px;padding:9px 0;
              border-bottom:1px solid {C["border"]};">
    <span style="color:{pcolor};font-size:0.72rem;font-weight:700;
                 min-width:60px;text-transform:uppercase;">{prio}</span>
    <span style="flex:1;font-size:0.875rem;color:{C["text"]};">{sess.get('titre','')}</span>
    <span style="font-size:0.75rem;color:{C["text_3"]};white-space:nowrap;">
      {sess.get('duree_min',30)} min · {sess.get('activite','')}
    </span>
  </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Email du rapport de progression ───────────────────────
    if email_configured():
        spacer(16)
        email_lbl = "📧 Recevoir mon rapport par email" if lang == "fr" else "📧 Email my progress report"
        if st.button(email_lbl, key="dash_email_report"):
            with st.spinner("Génération du rapport…" if lang == "fr" else "Generating report…"):
                report = generate_progress_report(
                    student_name=st.session_state.get("student_name", "Étudiant"),
                    stats=stats,
                    weaknesses=weak,
                    language=lang,
                )
                result = send_weekly_summary(
                    student_email=st.session_state.get("student_email", ""),
                    student_name=st.session_state.get("student_name", "Étudiant"),
                    stats=stats,
                    weaknesses=weak,
                    progress_report=report,
                )
            if result.get("success"):
                ok_msg = f"✅ Rapport envoyé à {st.session_state.get('student_email','')}"
                st.success(ok_msg if lang == "fr" else ok_msg.replace("Rapport envoyé", "Report sent"))
            else:
                st.error(f"❌ {result.get('error', 'Erreur')}")
