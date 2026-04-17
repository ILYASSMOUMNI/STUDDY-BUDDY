# frontend/design_system.py
# Light theme — emerald × violet × clean white

import streamlit as st

# ─── Design Tokens ────────────────────────────────────────────────────────────
C = {
    # Backgrounds
    "bg":         "#F0F4F8",
    "surface":    "#FFFFFF",
    "elevated":   "#F8FAFC",
    "overlay":    "rgba(0,0,0,0.03)",
    "sidebar_bg": "#FFFFFF",

    # Accent — Emerald (darker shade for contrast on white)
    "accent":      "#059669",
    "accent_dim":  "rgba(5,150,105,0.10)",
    "accent_glow": "rgba(5,150,105,0.20)",

    # Secondary — Violet
    "violet":     "#7C3AED",
    "violet_dim": "rgba(124,58,237,0.08)",

    # Borders
    "border":    "rgba(15,23,42,0.08)",
    "border_md": "rgba(15,23,42,0.14)",
    "border_lg": "rgba(15,23,42,0.22)",

    # Text
    "text":    "#0F172A",
    "text_2":  "#475569",
    "text_3":  "#94A3B8",
    "text_inv":"#FFFFFF",

    # Status
    "green":  "#059669",  "green_bg":  "rgba(5,150,105,0.08)",
    "orange": "#D97706",  "orange_bg": "rgba(217,119,6,0.08)",
    "red":    "#DC2626",  "red_bg":    "rgba(220,38,38,0.08)",
    "blue":   "#2563EB",  "blue_bg":   "rgba(37,99,235,0.08)",
    "purple": "#7C3AED",  "purple_bg": "rgba(124,58,237,0.08)",

    # Backward-compat aliases used by existing pages
    "indigo":       "#059669",
    "indigo_dark":  "#047857",
    "indigo_light": "rgba(5,150,105,0.10)",
    "tertiary":     "#7C3AED",
    "surface_2":    "#F8FAFC",
    "border_dark":  "rgba(15,23,42,0.16)",
    "gray":         "#64748B",
    "gray_bg":      "rgba(100,116,139,0.08)",
    "sidebar_active_bg":   "rgba(5,150,105,0.08)",
    "sidebar_active_text": "#059669",
}


def inject_global_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ─── Design Tokens ─────────────────────────────────────────────────────── */
:root {{
  --bg:           {C["bg"]};
  --surface:      {C["surface"]};
  --elevated:     {C["elevated"]};
  --accent:       {C["accent"]};
  --violet:       {C["violet"]};
  --border:       {C["border"]};
  --border-md:    {C["border_md"]};
  --text:         {C["text"]};
  --text-2:       {C["text_2"]};
  --text-3:       {C["text_3"]};
  --radius-sm:    6px;
  --radius-md:    10px;
  --radius-lg:    16px;
  --radius-xl:    22px;
  --ease-out:     cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
  --dur-fast:     120ms;
  --dur-base:     220ms;
  --dur-slow:     380ms;
}}

/* ─── Keyframes ─────────────────────────────────────────────────────────── */
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(14px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeIn {{
  from {{ opacity:0; }}
  to   {{ opacity:1; }}
}}
@keyframes scaleIn {{
  from {{ opacity:0; transform:scale(0.96); }}
  to   {{ opacity:1; transform:scale(1); }}
}}
@keyframes shimmer {{
  from {{ background-position:-200% center; }}
  to   {{ background-position: 200% center; }}
}}

/* ─── Reset ─────────────────────────────────────────────────────────────── */
*,*::before,*::after {{ box-sizing:border-box; margin:0; }}
html,body,[class*="css"] {{
  font-family:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif;
  font-size:14px;
  line-height:1.5;
  color:{C["text"]};
  -webkit-font-smoothing:antialiased;
  background:{C["bg"]};
}}

/* ─── App background ─────────────────────────────────────────────────────── */
.stApp {{
  background:{C["bg"]};
  background-image:
    radial-gradient(ellipse 70% 50% at 10%  0%,  rgba(5,150,105,0.06) 0%,transparent 60%),
    radial-gradient(ellipse 50% 40% at 90% 90%,  rgba(124,58,237,0.05) 0%,transparent 60%);
}}

/* Subtle dot-grid */
.stApp::before {{
  content:"";
  position:fixed;
  inset:0;
  background-image:radial-gradient(circle,rgba(15,23,42,0.06) 1px,transparent 1px);
  background-size:28px 28px;
  pointer-events:none;
  z-index:0;
}}

/* ─── Chrome ─────────────────────────────────────────────────────────────── */
#MainMenu,footer,header {{ visibility:hidden; height:0; overflow:hidden; }}
.block-container {{
  padding:1.5rem 2.5rem 4rem !important;
  max-width:1440px !important;
  position:relative;
  z-index:1;
}}

/* Page entrance */
.block-container > div:first-child {{
  animation:fadeUp 0.32s var(--ease-out) both;
}}

/* ─── Sidebar ────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
  background:{C["sidebar_bg"]} !important;
  border-right:1px solid {C["border"]} !important;
  box-shadow:2px 0 12px rgba(15,23,42,0.06) !important;
  width:240px !important;
  min-width:240px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{ padding:0 !important; }}
section[data-testid="stSidebar"] * {{ color:{C["text_2"]} !important; }}

/* Sidebar nav buttons — base */
section[data-testid="stSidebar"] .stButton > button {{
  width:100% !important;
  background:transparent !important;
  color:{C["text_2"]} !important;
  border:none !important;
  border-left:2px solid transparent !important;
  border-radius:0 var(--radius-md) var(--radius-md) 0 !important;
  padding:9px 14px 9px 14px !important;
  font-size:0.875rem !important;
  font-weight:500 !important;
  text-align:left !important;
  box-shadow:none !important;
  transition:background var(--dur-fast) var(--ease-out),
             color var(--dur-fast),
             border-left-color var(--dur-fast) !important;
  justify-content:flex-start !important;
  letter-spacing:-0.01em !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
  background:rgba(15,23,42,0.04) !important;
  color:{C["text"]} !important;
  transform:none !important;
  box-shadow:none !important;
}}

/* ─── Top-nav bar container ──────────────────────────────────────────────── */
.topnav-bar {{
  background:{C["surface"]};
  border:1px solid {C["border"]};
  border-radius:var(--radius-xl);
  padding:6px;
  margin-bottom:24px;
  display:flex;
  gap:4px;
  box-shadow:0 2px 8px rgba(15,23,42,0.06);
}}

/* ─── Primary buttons ────────────────────────────────────────────────────── */
.stButton > button {{
  background:{C["accent"]} !important;
  color:{C["text_inv"]} !important;
  border:none !important;
  border-radius:var(--radius-md) !important;
  padding:9px 20px !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:0.875rem !important;
  font-weight:600 !important;
  cursor:pointer !important;
  transition:all var(--dur-base) var(--ease-out) !important;
  box-shadow:0 1px 3px rgba(5,150,105,0.25), 0 4px 12px rgba(5,150,105,0.12) !important;
  letter-spacing:-0.01em !important;
}}
.stButton > button:hover {{
  background:#047857 !important;
  box-shadow:0 2px 6px rgba(5,150,105,0.35), 0 8px 20px rgba(5,150,105,0.18) !important;
  transform:translateY(-1px) !important;
}}
.stButton > button:active {{
  transform:translateY(0) scale(0.98) !important;
  transition-duration:60ms !important;
}}
.stButton > button[kind="secondary"] {{
  background:{C["surface"]} !important;
  color:{C["text_2"]} !important;
  border:1px solid {C["border"]} !important;
  box-shadow:0 1px 3px rgba(15,23,42,0.06) !important;
}}
.stButton > button[kind="secondary"]:hover {{
  background:{C["elevated"]} !important;
  border-color:{C["border_md"]} !important;
  color:{C["text"]} !important;
  box-shadow:0 2px 6px rgba(15,23,42,0.1) !important;
}}

/* ─── Inputs ─────────────────────────────────────────────────────────────── */
.stTextInput label,.stTextArea label,.stSelectbox label,
.stSlider label,.stRadio label p {{
  font-size:0.8125rem !important;
  font-weight:500 !important;
  color:{C["text_2"]} !important;
  margin-bottom:6px !important;
  letter-spacing:-0.005em !important;
}}
.stTextInput > div > div > input {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["text"]} !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:0.875rem !important;
  padding:10px 14px !important;
  height:40px !important;
  box-shadow:0 1px 3px rgba(15,23,42,0.04) !important;
  transition:border-color var(--dur-base),box-shadow var(--dur-base) !important;
}}
.stTextInput > div > div > input:focus {{
  border-color:{C["accent"]} !important;
  box-shadow:0 0 0 3px {C["accent_dim"]} !important;
  outline:none !important;
}}
.stTextInput > div > div > input::placeholder {{ color:{C["text_3"]} !important; }}
.stTextArea > div > div > textarea {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["text"]} !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:0.875rem !important;
  transition:border-color var(--dur-base),box-shadow var(--dur-base) !important;
}}
.stTextArea > div > div > textarea:focus {{
  border-color:{C["accent"]} !important;
  box-shadow:0 0 0 3px {C["accent_dim"]} !important;
}}

/* ─── Selectbox ──────────────────────────────────────────────────────────── */
.stSelectbox > div > div {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["text"]} !important;
  font-size:0.875rem !important;
  min-height:40px !important;
  box-shadow:0 1px 3px rgba(15,23,42,0.04) !important;
}}

/* ─── Radio ──────────────────────────────────────────────────────────────── */
.stRadio > div {{ gap:8px !important; }}
.stRadio > div > label {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-md) !important;
  padding:10px 14px !important;
  cursor:pointer !important;
  transition:all var(--dur-fast) !important;
  font-size:0.875rem !important;
  color:{C["text"]} !important;
  width:100% !important;
  box-shadow:0 1px 2px rgba(15,23,42,0.04) !important;
}}
.stRadio > div > label:hover {{
  border-color:{C["border_md"]} !important;
  background:{C["elevated"]} !important;
  box-shadow:0 2px 6px rgba(15,23,42,0.08) !important;
}}

/* ─── Slider ─────────────────────────────────────────────────────────────── */
.stSlider > div > div > div > div {{ background:{C["accent"]} !important; }}
.stSlider > div > div > div       {{ background:rgba(15,23,42,0.10) !important; }}

/* ─── Tabs ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  background:transparent !important;
  border-bottom:1px solid {C["border"]} !important;
  gap:0 !important;
  padding:0 !important;
}}
.stTabs [data-baseweb="tab"] {{
  background:transparent !important;
  border:none !important;
  border-bottom:2px solid transparent !important;
  padding:10px 20px !important;
  font-size:0.875rem !important;
  font-weight:500 !important;
  color:{C["text_3"]} !important;
  margin-bottom:-1px !important;
  transition:color var(--dur-base),border-color var(--dur-base) !important;
  letter-spacing:-0.01em !important;
}}
.stTabs [aria-selected="true"] {{
  color:{C["accent"]} !important;
  border-bottom-color:{C["accent"]} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding:20px 0 0 !important; }}

/* ─── Progress ───────────────────────────────────────────────────────────── */
.stProgress > div > div {{
  background:rgba(15,23,42,0.08) !important;
  border-radius:999px !important;
  height:4px !important;
}}
.stProgress > div > div > div {{
  background:linear-gradient(90deg, {C["accent"]}, {C["violet"]}) !important;
  border-radius:999px !important;
  height:4px !important;
}}

/* ─── Expander ───────────────────────────────────────────────────────────── */
details summary {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-md) !important;
  padding:10px 16px !important;
  font-size:0.875rem !important;
  font-weight:600 !important;
  color:{C["text"]} !important;
  cursor:pointer !important;
  box-shadow:0 1px 3px rgba(15,23,42,0.04) !important;
  transition:background var(--dur-fast),border-color var(--dur-fast) !important;
}}
details summary:hover {{
  border-color:{C["border_md"]} !important;
  background:{C["elevated"]} !important;
}}

/* ─── Status boxes ───────────────────────────────────────────────────────── */
.stSuccess,.element-container .stSuccess {{
  background:{C["green_bg"]} !important;
  border-color:{C["green"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["green"]} !important;
}}
.stError,.element-container .stError {{
  background:{C["red_bg"]} !important;
  border-color:{C["red"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["red"]} !important;
}}
.stWarning,.element-container .stWarning {{
  background:{C["orange_bg"]} !important;
  border-color:{C["orange"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["orange"]} !important;
}}
.stInfo,.element-container .stInfo {{
  background:{C["accent_dim"]} !important;
  border-color:{C["accent"]} !important;
  border-radius:var(--radius-md) !important;
  color:{C["accent"]} !important;
}}

/* ─── Spinner ────────────────────────────────────────────────────────────── */
.stSpinner > div {{ border-top-color:{C["accent"]} !important; }}

/* ─── Chat messages ──────────────────────────────────────────────────────── */
.stChatMessage {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-lg) !important;
  padding:4px 8px !important;
  box-shadow:0 1px 4px rgba(15,23,42,0.06) !important;
}}
[data-testid="stChatMessageContent"] p {{ color:{C["text"]} !important; }}
[data-testid="stChatMessageContent"] code {{
  background:{C["elevated"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:4px !important;
  padding:1px 6px !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.8125rem !important;
  color:{C["accent"]} !important;
}}
/* ─── Chat input — bottom sticky bar ────────────────────────────────────── */
[data-testid="stBottom"] {{
  background:{C["bg"]} !important;
  border-top:1px solid {C["border"]} !important;
}}
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottom"] > div > div > div {{
  background:{C["bg"]} !important;
}}
.stChatInput,
.stChatInput > div,
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {{
  background:{C["surface"]} !important;
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-xl) !important;
  box-shadow:0 2px 8px rgba(15,23,42,0.06) !important;
}}
.stChatInput > div:focus-within,
[data-testid="stChatInput"] > div:focus-within {{
  border-color:{C["accent"]} !important;
  box-shadow:0 0 0 3px {C["accent_dim"]} !important;
}}
.stChatInput textarea,
[data-testid="stChatInput"] textarea {{
  background:transparent !important;
  color:{C["text"]} !important;
  caret-color:{C["accent"]} !important;
}}
.stChatInput textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {{
  color:{C["text_3"]} !important;
}}
/* send button inside chat input */
[data-testid="stChatInput"] button {{
  background:{C["accent"]} !important;
  border:none !important;
  border-radius:8px !important;
  color:{C["text_inv"]} !important;
}}

/* ─── Dataframe ──────────────────────────────────────────────────────────── */
.stDataFrame {{
  border:1px solid {C["border"]} !important;
  border-radius:var(--radius-lg) !important;
  overflow:hidden !important;
}}
.stDataFrame table {{
  background:{C["surface"]} !important;
  font-size:0.875rem !important;
  color:{C["text"]} !important;
}}

/* ─── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:rgba(15,23,42,0.15); border-radius:999px; }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(15,23,42,0.28); }}

/* ─── Divider ────────────────────────────────────────────────────────────── */
hr {{
  border:none !important;
  border-top:1px solid {C["border"]} !important;
  margin:20px 0 !important;
}}

/* ─── Focus ──────────────────────────────────────────────────────────────── */
:focus-visible {{
  outline:2px solid {C["accent"]} !important;
  outline-offset:2px !important;
  border-radius:4px !important;
}}

/* ─── Selection ──────────────────────────────────────────────────────────── */
::selection {{ background:{C["accent_dim"]}; color:{C["text"]}; }}

/* ─── Reduced-motion ─────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {{
  *,*::before,*::after {{
    animation-duration:0.01ms !important;
    animation-iteration-count:1 !important;
    transition-duration:0.01ms !important;
  }}
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def page_title(title: str, subtitle: str = ""):
    sub = (f'<p style="font-size:0.9375rem;color:{C["text_2"]};margin-top:6px;'
           f'line-height:1.5;letter-spacing:-0.01em;">{subtitle}</p>') if subtitle else ""
    st.markdown(f"""
<div style="padding:20px 0 18px;animation:fadeUp 0.32s var(--ease-out) both;">
  <h1 style="font-size:clamp(1.4rem,3vw,1.85rem);font-weight:700;
             letter-spacing:-0.03em;line-height:1.1;
             color:{C["text"]};">
    {title}
  </h1>
  {sub}
</div>""", unsafe_allow_html=True)


def section_heading(text: str):
    st.markdown(f"""
<p style="font-size:0.6875rem;font-weight:600;letter-spacing:0.1em;
          text-transform:uppercase;color:{C["text_3"]};margin:24px 0 12px;">
  {text}
</p>""", unsafe_allow_html=True)


def kpi_card(value: str, label: str, delta: str = "", delta_positive: bool = True,
             accent_color: str = None):
    accent = accent_color or C["accent"]
    delta_color = C["green"] if delta_positive else C["red"]
    delta_bg    = C["green_bg"] if delta_positive else C["red_bg"]
    delta_html  = (
        f'<span style="font-size:0.6875rem;font-weight:600;letter-spacing:0.05em;'
        f'text-transform:uppercase;color:{delta_color};margin-left:8px;'
        f'background:{delta_bg};padding:2px 8px;border-radius:999px;">'
        f'{delta}</span>'
    ) if delta else ""
    st.markdown(f"""
<div style="background:{C["surface"]};
            border:1px solid {C["border"]};
            border-radius:var(--radius-lg);
            padding:22px 24px;
            position:relative;overflow:hidden;
            box-shadow:0 2px 12px rgba(15,23,42,0.06),
                       0 1px 3px rgba(15,23,42,0.04);
            animation:fadeUp 0.32s var(--ease-out) both;">
  <div style="position:absolute;top:-20px;right:-20px;width:100px;height:100px;
              border-radius:50%;
              background:radial-gradient(circle,{accent},transparent);
              opacity:0.10;pointer-events:none;"></div>
  <p style="font-size:0.6875rem;font-weight:600;letter-spacing:0.1em;
            text-transform:uppercase;color:{C["text_3"]};margin-bottom:14px;">
    {label}
  </p>
  <div style="display:flex;align-items:baseline;gap:4px;position:relative;z-index:1;">
    <span style="font-size:2.25rem;font-weight:700;color:{C["text"]};
                 letter-spacing:-0.04em;font-family:'DM Sans',sans-serif;line-height:1;">
      {value}
    </span>
    {delta_html}
  </div>
  <div style="margin-top:16px;height:2px;border-radius:999px;
              background:linear-gradient(90deg,{accent},transparent);
              opacity:0.45;"></div>
</div>""", unsafe_allow_html=True)


def badge(text: str, color: str = "gray"):
    palettes = {
        "green":  (C["green"],  C["green_bg"],  "rgba(5,150,105,0.20)"),
        "orange": (C["orange"], C["orange_bg"], "rgba(217,119,6,0.20)"),
        "red":    (C["red"],    C["red_bg"],    "rgba(220,38,38,0.20)"),
        "blue":   (C["blue"],   C["blue_bg"],   "rgba(37,99,235,0.20)"),
        "purple": (C["purple"], C["purple_bg"], "rgba(124,58,237,0.20)"),
        "indigo": (C["accent"], C["accent_dim"],"rgba(5,150,105,0.20)"),
        "gray":   (C["text_2"], "rgba(100,116,139,0.08)", "rgba(100,116,139,0.18)"),
    }
    fg, bg, border = palettes.get(color, palettes["gray"])
    return (f'<span style="display:inline-block;padding:3px 10px;'
            f'border-radius:999px;font-size:0.6875rem;font-weight:600;'
            f'letter-spacing:0.05em;text-transform:uppercase;'
            f'background:{bg};color:{fg};border:1px solid {border};">'
            f'{text}</span>')


def card(content_html: str, padding: str = "20px 24px", extra_style: str = ""):
    st.markdown(f"""
<div style="background:{C["surface"]};
            border:1px solid {C["border"]};
            border-radius:var(--radius-lg);
            padding:{padding};
            box-shadow:0 2px 12px rgba(15,23,42,0.06),
                       0 1px 3px rgba(15,23,42,0.04);
            {extra_style}">
  {content_html}
</div>""", unsafe_allow_html=True)


def inline_alert(text: str, kind: str = "info"):
    styles = {
        "info":    (C["accent"], C["accent_dim"], "rgba(5,150,105,0.15)"),
        "success": (C["green"],  C["green_bg"],   "rgba(5,150,105,0.15)"),
        "warning": (C["orange"], C["orange_bg"],  "rgba(217,119,6,0.15)"),
        "danger":  (C["red"],    C["red_bg"],     "rgba(220,38,38,0.15)"),
    }
    icons = {"info": "ℹ", "success": "✓", "warning": "⚠", "danger": "✕"}
    fg, bg, border = styles.get(kind, styles["info"])
    icon = icons.get(kind, "ℹ")
    st.markdown(f"""
<div style="background:{bg};border:1px solid {border};
            border-radius:var(--radius-md);
            padding:12px 16px;font-size:0.875rem;color:{fg};
            line-height:1.5;margin-bottom:16px;font-weight:500;
            display:flex;gap:10px;align-items:flex-start;">
  <span style="opacity:0.8;flex-shrink:0;">{icon}</span>
  <span>{text}</span>
</div>""", unsafe_allow_html=True)


def spacer(h: int = 16):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)


def divider():
    st.markdown(
        f'<hr style="border:none;border-top:1px solid {C["border"]};margin:16px 0;">',
        unsafe_allow_html=True)


def table_header(cols: list):
    cells = "".join(
        f'<div style="flex:{w};font-size:0.6875rem;font-weight:600;'
        f'letter-spacing:0.08em;text-transform:uppercase;color:{C["text_3"]};">'
        f'{lbl}</div>'
        for lbl, w in cols
    )
    st.markdown(f"""
<div style="display:flex;gap:12px;padding:8px 16px;
            border-bottom:1px solid {C["border"]};
            background:{C["elevated"]};
            border-radius:var(--radius-md) var(--radius-md) 0 0;">
  {cells}
</div>""", unsafe_allow_html=True)
