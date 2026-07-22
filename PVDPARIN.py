import math
from dataclasses import dataclass, asdict
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="PVD Studio Pro",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown(
    """
    <style>
    :root{
        --navy:#0B1220;
        --navy-2:#121C2F;
        --cyan:#22D3EE;
        --blue:#3B82F6;
        --green:#10B981;
        --amber:#F59E0B;
        --red:#EF4444;
        --muted:#94A3B8;
        --panel:#111827;
        --panel-2:#172033;
        --line:rgba(148,163,184,.18);
    }

    .stApp{
        background:
            radial-gradient(circle at 10% 0%, rgba(34,211,238,.10), transparent 28%),
            radial-gradient(circle at 95% 10%, rgba(59,130,246,.12), transparent 30%),
            linear-gradient(180deg,#07111F 0%,#0A1220 50%,#0E1728 100%);
        color:#E5EEF8;
    }

    [data-testid="stSidebar"]{
        background:linear-gradient(180deg,#0B1322 0%,#101A2D 100%);
        border-right:1px solid var(--line);
    }

    [data-testid="stSidebar"] *{
        color:#E8F1FA;
    }

    /* -------------------------------------------------
       HIGH-CONTRAST FORM CONTROLS
       ทำให้ข้อความภายในช่องสีขาวอ่านง่ายและชัดเจน
       ------------------------------------------------- */

    /* Number input / text input */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="input"] input{
        color:#0F172A !important;
        -webkit-text-fill-color:#0F172A !important;
        caret-color:#2563EB !important;
        font-weight:700 !important;
        font-size:1rem !important;
        opacity:1 !important;
    }

    /* Input container */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="base-input"]{
        background:#F8FAFC !important;
        border:1px solid #CBD5E1 !important;
        border-radius:12px !important;
        box-shadow:inset 0 1px 2px rgba(15,23,42,.08) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="input"]:focus-within,
    [data-testid="stSidebar"] [data-baseweb="base-input"]:focus-within{
        border-color:#38BDF8 !important;
        box-shadow:0 0 0 3px rgba(56,189,248,.18) !important;
    }

    /* Number input +/- buttons and units */
    [data-testid="stSidebar"] [data-testid="stNumberInput"] button,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] svg{
        color:#334155 !important;
        fill:#334155 !important;
    }

    [data-testid="stSidebar"] [data-testid="stNumberInput"] div[data-baseweb="input"] > div{
        color:#334155 !important;
    }

    /* Selectbox visible value */
    [data-testid="stSidebar"] [data-baseweb="select"] > div{
        background:#F8FAFC !important;
        border-color:#CBD5E1 !important;
        border-radius:12px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div[role="button"],
    [data-testid="stSidebar"] [data-baseweb="select"] svg{
        color:#0F172A !important;
        fill:#334155 !important;
        font-weight:700 !important;
        opacity:1 !important;
    }

    /* Dropdown menu */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"]{
        background:#FFFFFF !important;
        color:#0F172A !important;
    }

    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li{
        color:#0F172A !important;
        background:#FFFFFF !important;
        font-weight:600 !important;
    }

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover{
        background:#E0F2FE !important;
    }

    /* Segmented control: unselected and selected */
    [data-testid="stSidebar"] [data-testid="stSegmentedControl"]{
        background:#F8FAFC !important;
        border:1px solid #CBD5E1 !important;
        border-radius:12px !important;
        padding:3px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSegmentedControl"] button{
        color:#0F172A !important;
        background:transparent !important;
        font-weight:700 !important;
        border-radius:9px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSegmentedControl"] button[aria-pressed="true"]{
        color:#FFFFFF !important;
        background:linear-gradient(135deg,#0284C7,#2563EB) !important;
        box-shadow:0 4px 12px rgba(37,99,235,.30) !important;
    }

    /* Radio controls */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p{
        color:#E8F1FA !important;
        font-weight:600 !important;
    }

    /* Widget labels stay bright on dark sidebar */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] .stMarkdown p{
        color:#E8F1FA !important;
    }

    /* Placeholder text */
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder{
        color:#64748B !important;
        -webkit-text-fill-color:#64748B !important;
        opacity:1 !important;
    }

    .block-container{
        padding-top:1.4rem;
        padding-bottom:2rem;
        max-width:1500px;
    }

    .hero{
        position:relative;
        overflow:hidden;
        padding:28px 30px;
        border:1px solid rgba(34,211,238,.20);
        border-radius:28px;
        background:
            linear-gradient(135deg,rgba(15,23,42,.96),rgba(14,28,48,.92)),
            linear-gradient(135deg,rgba(34,211,238,.08),rgba(59,130,246,.06));
        box-shadow:0 24px 60px rgba(0,0,0,.28);
        margin-bottom:18px;
    }

    .hero:before{
        content:"";
        position:absolute;
        width:260px;height:260px;
        border-radius:50%;
        right:-60px;top:-100px;
        background:radial-gradient(circle,rgba(34,211,238,.25),rgba(34,211,238,0));
    }

    .hero:after{
        content:"";
        position:absolute;
        width:240px;height:240px;
        border-radius:50%;
        right:160px;bottom:-150px;
        background:radial-gradient(circle,rgba(59,130,246,.20),rgba(59,130,246,0));
    }

    .eyebrow{
        display:inline-flex;
        gap:8px;
        align-items:center;
        padding:7px 12px;
        border-radius:999px;
        background:rgba(34,211,238,.10);
        border:1px solid rgba(34,211,238,.22);
        color:#9DEBFA;
        font-size:.82rem;
        font-weight:700;
        letter-spacing:.08em;
        text-transform:uppercase;
    }

    .hero h1{
        margin:.6rem 0 .25rem;
        font-size:clamp(2rem,4vw,3.5rem);
        line-height:1.02;
        color:white;
        letter-spacing:-.04em;
    }

    .hero p{
        color:#AFC0D5;
        font-size:1.02rem;
        max-width:850px;
        margin:0;
    }

    .hero-grid{
        position:relative;
        z-index:2;
        display:grid;
        grid-template-columns:1.35fr .65fr;
        gap:24px;
        align-items:center;
    }

    @media (max-width:900px){
        .hero-grid{grid-template-columns:1fr;}
    }

    .glass-card{
        background:linear-gradient(180deg,rgba(17,24,39,.88),rgba(15,23,42,.92));
        border:1px solid var(--line);
        border-radius:22px;
        padding:18px;
        box-shadow:0 18px 35px rgba(0,0,0,.18);
        height:100%;
    }

    .section-title{
        display:flex;
        align-items:center;
        gap:10px;
        font-size:1.12rem;
        font-weight:800;
        margin-bottom:12px;
        color:#F8FAFC;
    }

    .mini-badge{
        font-size:.72rem;
        font-weight:800;
        padding:5px 9px;
        border-radius:999px;
        background:rgba(59,130,246,.14);
        border:1px solid rgba(59,130,246,.24);
        color:#AFCBFF;
    }

    .kpi-card{
        border:1px solid var(--line);
        border-radius:20px;
        padding:18px;
        background:
            linear-gradient(180deg,rgba(15,23,42,.92),rgba(17,24,39,.88));
        box-shadow:0 12px 26px rgba(0,0,0,.16);
    }

    .kpi-label{
        color:#8FA4BD;
        font-size:.80rem;
        font-weight:700;
        letter-spacing:.04em;
        text-transform:uppercase;
    }

    .kpi-value{
        color:#F8FAFC;
        font-size:1.85rem;
        font-weight:900;
        line-height:1.1;
        margin-top:8px;
    }

    .kpi-note{
        color:#98A8BC;
        font-size:.78rem;
        margin-top:6px;
    }

    .status-pass{
        color:#A7F3D0;
        background:rgba(16,185,129,.10);
        border:1px solid rgba(16,185,129,.25);
        padding:10px 14px;
        border-radius:14px;
        font-weight:800;
    }

    .status-fail{
        color:#FECACA;
        background:rgba(239,68,68,.10);
        border:1px solid rgba(239,68,68,.25);
        padding:10px 14px;
        border-radius:14px;
        font-weight:800;
    }

    .info-strip{
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:10px;
        margin-top:16px;
    }

    .info-chip{
        background:rgba(255,255,255,.035);
        border:1px solid var(--line);
        border-radius:14px;
        padding:11px 12px;
        color:#B7C5D8;
        font-size:.83rem;
    }

    @media (max-width:750px){
        .info-strip{grid-template-columns:1fr;}
    }

    .divider-soft{
        height:1px;
        background:linear-gradient(90deg,transparent,var(--line),transparent);
        margin:14px 0 20px;
    }

    .footer-note{
        padding:16px 18px;
        border-radius:16px;
        background:rgba(245,158,11,.08);
        border:1px solid rgba(245,158,11,.18);
        color:#F7D9A2;
        font-size:.86rem;
    }

    div[data-testid="stMetric"]{
        background:linear-gradient(180deg,rgba(15,23,42,.92),rgba(17,24,39,.86));
        border:1px solid var(--line);
        padding:16px;
        border-radius:18px;
    }

    div[data-testid="stMetricLabel"]{
        color:#9FB1C5;
    }

    div[data-testid="stMetricValue"]{
        color:#F8FAFC;
    }

    .stTabs [data-baseweb="tab-list"]{
        gap:8px;
        background:rgba(15,23,42,.55);
        border:1px solid var(--line);
        border-radius:16px;
        padding:6px;
    }

    .stTabs [data-baseweb="tab"]{
        border-radius:12px;
        padding:10px 14px;
        color:#AFC0D5;
    }

    .stTabs [aria-selected="true"]{
        background:linear-gradient(135deg,rgba(34,211,238,.15),rgba(59,130,246,.15));
        color:#E9FCFF;
    }

    .stButton>button, .stDownloadButton>button{
        border-radius:12px;
        border:1px solid rgba(34,211,238,.25);
        background:linear-gradient(135deg,#0EA5E9,#2563EB);
        color:white;
        font-weight:800;
    }

    .stButton>button:hover, .stDownloadButton>button:hover{
        border-color:#67E8F9;
        box-shadow:0 10px 25px rgba(37,99,235,.28);
    }

    div[data-testid="stDataFrame"]{
        border:1px solid var(--line);
        border-radius:16px;
        overflow:hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO SVG
# =========================================================
hero_svg = """
<svg viewBox="0 0 520 300" width="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8B5E3C"/>
      <stop offset="100%" stop-color="#3F2D24"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22D3EE"/>
      <stop offset="100%" stop-color="#3B82F6"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect x="10" y="18" width="500" height="264" rx="26" fill="#0A1527" stroke="#1E3A5F"/>
  <rect x="30" y="74" width="460" height="180" rx="18" fill="url(#soil)" opacity=".95"/>
  <rect x="30" y="52" width="460" height="30" rx="10" fill="#D9B56D"/>
  <rect x="30" y="44" width="460" height="12" rx="6" fill="#F2D38C"/>

  <g stroke="url(#water)" stroke-width="8" stroke-linecap="round" filter="url(#glow)">
    <line x1="112" y1="74" x2="112" y2="228"/>
    <line x1="205" y1="74" x2="205" y2="228"/>
    <line x1="298" y1="74" x2="298" y2="228"/>
    <line x1="391" y1="74" x2="391" y2="228"/>
  </g>

  <g fill="none" stroke="#67E8F9" stroke-width="2" opacity=".8">
    <path d="M75 135 C90 130,95 120,112 118"/>
    <path d="M75 168 C90 163,95 153,112 151"/>
    <path d="M168 132 C182 126,190 118,205 116"/>
    <path d="M168 177 C182 170,190 160,205 158"/>
    <path d="M261 140 C278 134,284 124,298 122"/>
    <path d="M261 183 C278 176,284 166,298 164"/>
    <path d="M354 135 C370 130,380 122,391 120"/>
    <path d="M354 180 C370 174,380 165,391 163"/>
  </g>

  <g fill="#CFFAFE">
    <circle cx="86" cy="132" r="3"/>
    <circle cx="92" cy="164" r="3"/>
    <circle cx="178" cy="128" r="3"/>
    <circle cx="178" cy="174" r="3"/>
    <circle cx="270" cy="136" r="3"/>
    <circle cx="270" cy="179" r="3"/>
    <circle cx="364" cy="132" r="3"/>
    <circle cx="364" cy="176" r="3"/>
  </g>

  <g fill="#FFFFFF">
    <text x="48" y="38" font-size="16" font-weight="800">PVD SOIL IMPROVEMENT SYSTEM</text>
  </g>
  <g fill="#93C5FD">
    <text x="54" y="276" font-size="13">Accelerated consolidation through radial drainage</text>
  </g>
</svg>
"""


# =========================================================
# DATA MODEL
# =========================================================
@dataclass
class PVDResult:
    spacing_m: float
    de_cm: float
    dw_cm: float
    n: float
    fn: float
    sand_mat_L: float
    radial_denominator: float
    cr_cm2_day: float
    tr: float
    ur: float
    tv: float
    uv: float
    uav: float


# =========================================================
# ENGINEERING FUNCTIONS
# =========================================================
def equivalent_diameter(a_cm: float, b_cm: float, method: str) -> float:
    if method == "Hansbo":
        return 2.0 * (a_cm + b_cm) / math.pi
    return (a_cm + b_cm) / 2.0


def influence_diameter(spacing_m: float, pattern: str) -> float:
    factor = 1.13 if pattern == "Square" else 1.05
    return factor * spacing_m * 100.0


def spacing_factor(n: float) -> float:
    if n <= 1:
        raise ValueError("ค่า n ต้องมากกว่า 1 โปรดตรวจสอบ S และขนาด PVD")
    n2 = n**2
    return (n2 / (n2 - 1.0)) * math.log(n) - ((3.0 * n2 - 1.0) / (4.0 * n2))


def calculate_sand_mat_L(
    n: float,
    soil_thickness_m: float,
    sand_mat_thickness_m: float,
    soil_permeability: float,
    sand_mat_permeability: float,
    sand_mat_full_width_m: float,
    dw_cm: float,
) -> float:
    """
    Drainage resistance index of sand mat:
    L = (32/pi^2)(1/n^2)(H/Hm)(kc/km)(B/dw)^2

    B is half of the full sand-mat width (full width = 2B).
    kc and km must use the same units.
    """
    if sand_mat_thickness_m <= 0:
        raise ValueError("ความหนา Sand Mat (Hm) ต้องมากกว่า 0")
    if sand_mat_permeability <= 0:
        raise ValueError("ค่า km ต้องมากกว่า 0")
    if sand_mat_full_width_m <= 0:
        raise ValueError("ความกว้าง Sand Mat ต้องมากกว่า 0")

    half_width_m = sand_mat_full_width_m / 2.0
    dw_m = dw_cm / 100.0
    return (
        (32.0 / math.pi**2)
        * (1.0 / n**2)
        * (soil_thickness_m / sand_mat_thickness_m)
        * (soil_permeability / sand_mat_permeability)
        * (half_width_m / dw_m) ** 2
    )


def calculate_pvd(
    spacing_m: float,
    pattern: str,
    a_cm: float,
    b_cm: float,
    dw_method: str,
    cv_cm2_day: float,
    kh_kv: float,
    time_day: float,
    hd_m: float,
    consider_sand_mat: bool = False,
    soil_thickness_m: float = 1.0,
    sand_mat_thickness_m: float = 0.50,
    soil_permeability: float = 1e-7,
    sand_mat_permeability: float = 1e-3,
    sand_mat_full_width_m: float = 80.0,
) -> PVDResult:
    dw = equivalent_diameter(a_cm, b_cm, dw_method)
    de = influence_diameter(spacing_m, pattern)
    n = de / dw
    fn = spacing_factor(n)

    sand_mat_L = 0.0
    if consider_sand_mat:
        sand_mat_L = calculate_sand_mat_L(
            n=n,
            soil_thickness_m=soil_thickness_m,
            sand_mat_thickness_m=sand_mat_thickness_m,
            soil_permeability=soil_permeability,
            sand_mat_permeability=sand_mat_permeability,
            sand_mat_full_width_m=sand_mat_full_width_m,
            dw_cm=dw,
        )

    radial_denominator = fn + 0.8 * sand_mat_L
    cr = kh_kv * cv_cm2_day
    tr = cr * time_day / (de**2)
    ur = 1.0 - math.exp((-8.0 * tr) / radial_denominator)

    tv = cv_cm2_day * time_day / ((hd_m * 100.0) ** 2)
    uv = min(math.sqrt(max(0.0, 4.0 * tv / math.pi)), 1.0)

    uav = 1.0 - (1.0 - ur) * (1.0 - uv)

    return PVDResult(
        spacing_m=spacing_m,
        de_cm=de,
        dw_cm=dw,
        n=n,
        fn=fn,
        sand_mat_L=sand_mat_L,
        radial_denominator=radial_denominator,
        cr_cm2_day=cr,
        tr=tr,
        ur=ur,
        tv=tv,
        uv=uv,
        uav=uav,
    )


def gauge_chart(value: float, title: str, target: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"size": 34, "color": "#F8FAFC"}},
            title={"text": title, "font": {"size": 15, "color": "#AFC0D5"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#64748B",
                    "tickfont": {"color": "#94A3B8"},
                },
                "bar": {"color": "#22D3EE"},
                "bgcolor": "rgba(15,23,42,.25)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60], "color": "rgba(239,68,68,.16)"},
                    {"range": [60, target], "color": "rgba(245,158,11,.16)"},
                    {"range": [target, 100], "color": "rgba(16,185,129,.16)"},
                ],
                "threshold": {
                    "line": {"color": "#F8FAFC", "width": 3},
                    "thickness": 0.8,
                    "value": target,
                },
            },
        )
    )
    fig.update_layout(
        height=270,
        margin=dict(l=20, r=20, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E5EEF8"},
    )
    return fig


def comparison_chart(df: pd.DataFrame, target: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["S (m)"],
            y=df["Ur (%)"],
            mode="lines+markers",
            name="Ur — Radial",
            line=dict(width=3, color="#22D3EE"),
            marker=dict(size=7),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["S (m)"],
            y=df["Uv (%)"],
            mode="lines+markers",
            name="Uv — Vertical",
            line=dict(width=3, color="#F59E0B"),
            marker=dict(size=7),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["S (m)"],
            y=df["Uav (%)"],
            mode="lines+markers",
            name="Uav — Combined",
            line=dict(width=4, color="#10B981"),
            marker=dict(size=8),
        )
    )
    fig.add_hline(
        y=target,
        line_dash="dash",
        line_color="#F8FAFC",
        annotation_text=f"Target {target:.0f}%",
        annotation_position="top left",
    )
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,.35)",
        font=dict(color="#C9D5E3"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            title="PVD Spacing, S (m)",
            gridcolor="rgba(148,163,184,.10)",
            zeroline=False,
        ),
        yaxis=dict(
            title="Degree of Consolidation (%)",
            range=[0, 102],
            gridcolor="rgba(148,163,184,.10)",
            zeroline=False,
        ),
    )
    return fig


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Design Inputs")
    st.caption("กำหนดข้อมูลเพื่อวิเคราะห์ระบบ PVD")

    st.markdown("### Geometry")
    pattern_th = st.selectbox(
        "รูปแบบการติดตั้ง",
        ["สี่เหลี่ยมจัตุรัส", "สามเหลี่ยม"],
    )
    pattern = "Square" if pattern_th == "สี่เหลี่ยมจัตุรัส" else "Triangular"

    spacing_m = st.number_input(
        "ระยะห่าง PVD, S (m)",
        min_value=0.10,
        max_value=10.00,
        value=1.00,
        step=0.05,
    )

    c1, c2 = st.columns(2)
    with c1:
        b_mm = st.number_input("ความกว้าง b (mm)", min_value=1.0, value=100.0, step=1.0)
    with c2:
        a_mm = st.number_input("ความหนา a (mm)", min_value=0.1, value=5.0, step=0.5)

    dw_method = st.segmented_control(
        "Equivalent Diameter",
        options=["Rixner", "Hansbo"],
        default="Rixner",
    )

    st.markdown("### Soil Parameters")
    cv = st.number_input(
        "Cv (cm²/day)",
        min_value=0.0001,
        value=20.0,
        step=1.0,
        format="%.4f",
    )
    kh_kv = st.number_input(
        "kh / kv",
        min_value=0.01,
        value=7.0,
        step=0.5,
    )

    st.markdown("### Time & Drainage")
    time_day = st.number_input(
        "เวลา t (day)",
        min_value=0.01,
        value=90.0,
        step=1.0,
    )
    soil_thickness_m = st.number_input(
        "ความหนาชั้นดินอ่อน H (m)",
        min_value=0.10,
        value=30.0,
        step=1.0,
    )
    drainage = st.radio(
        "Boundary drainage",
        ["ระบายสองทาง", "ระบายทางเดียว"],
    )
    target = st.slider(
        "เป้าหมาย Uav (%)",
        min_value=50,
        max_value=100,
        value=90,
        step=1,
    )

    st.markdown("### Sand Mat Resistance")
    consider_sand_mat = st.checkbox(
        "พิจารณาค่าความต้านทาน L ของ Sand Mat",
        value=True,
        help="เมื่อเปิด โปรแกรมจะใช้ Ur = 1 - exp[-8Tr/(F(n)+0.8L)]",
    )
    sand_mat_thickness_m = st.number_input(
        "ความหนา Sand Mat, Hm (m)",
        min_value=0.01,
        value=0.50,
        step=0.05,
        disabled=not consider_sand_mat,
    )
    sand_mat_full_width_m = st.number_input(
        "ความกว้าง Sand Mat ทั้งหมด, 2B (m)",
        min_value=0.10,
        value=80.0,
        step=1.0,
        disabled=not consider_sand_mat,
    )
    soil_permeability = st.number_input(
        "kc ดินเหนียว (m/s)",
        min_value=1e-12,
        value=1e-7,
        format="%.2e",
        disabled=not consider_sand_mat,
    )
    sand_mat_permeability = st.number_input(
        "km Sand Mat (m/s)",
        min_value=1e-12,
        value=1e-3,
        format="%.2e",
        disabled=not consider_sand_mat,
    )

    st.markdown("---")
    st.caption("PVD Studio Pro · Educational Edition")


# =========================================================
# CALCULATION
# =========================================================
a_cm = a_mm / 10.0
b_cm = b_mm / 10.0
hd_m = soil_thickness_m / 2.0 if drainage == "ระบายสองทาง" else soil_thickness_m

try:
    result = calculate_pvd(
        spacing_m=spacing_m,
        pattern=pattern,
        a_cm=a_cm,
        b_cm=b_cm,
        dw_method=dw_method,
        cv_cm2_day=cv,
        kh_kv=kh_kv,
        time_day=time_day,
        hd_m=hd_m,
        consider_sand_mat=consider_sand_mat,
        soil_thickness_m=soil_thickness_m,
        sand_mat_thickness_m=sand_mat_thickness_m,
        soil_permeability=soil_permeability,
        sand_mat_permeability=sand_mat_permeability,
        sand_mat_full_width_m=sand_mat_full_width_m,
    )
except ValueError as exc:
    st.error(str(exc))
    st.stop()


# =========================================================
# HERO
# =========================================================
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <div class="eyebrow">◉ Geotechnical Design Platform</div>
          <h1>PVD Studio Pro</h1>
          <p>
            Professional Prefabricated Vertical Drain calculator for
            radial, vertical and combined consolidation analysis.
          </p>
          <div class="info-strip">
            <div class="info-chip">Barron radial consolidation</div>
            <div class="info-chip">Terzaghi vertical consolidation</div>
            <div class="info-chip">Carillo combined consolidation</div>
          </div>
        </div>
        <div>{hero_svg}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SUMMARY KPIs
# =========================================================
st.markdown('<div class="section-title">Project Overview <span class="mini-badge">LIVE CALCULATION</span></div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">PVD Spacing</div>
          <div class="kpi-value">{result.spacing_m:.2f} m</div>
          <div class="kpi-note">{pattern_th} pattern</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">Influence Diameter</div>
          <div class="kpi-value">{result.de_cm:.1f} cm</div>
          <div class="kpi-note">de based on installation pattern</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">Equivalent Diameter</div>
          <div class="kpi-value">{result.dw_cm:.2f} cm</div>
          <div class="kpi-note">{dw_method} method</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    status_class = "status-pass" if result.uav * 100 >= target else "status-fail"
    status_text = "PASS" if result.uav * 100 >= target else "REVIEW"
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">Design Status</div>
          <div style="margin-top:13px"><span class="{status_class}">{status_text}</span></div>
          <div class="kpi-note">Target Uav ≥ {target:.0f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# MAIN TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "📐 Engineering Details", "🧪 Spacing Optimizer", "📘 Formula Guide"]
)

with tab1:
    st.markdown('<div class="divider-soft"></div>', unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(
            gauge_chart(result.ur * 100, "Radial Consolidation · Ur", target),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with g2:
        st.plotly_chart(
            gauge_chart(result.uv * 100, "Vertical Consolidation · Uv", target),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with g3:
        st.plotly_chart(
            gauge_chart(result.uav * 100, "Combined Consolidation · Uav", target),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    if result.uav * 100 >= target:
        st.success(
            f"✅ ระยะห่าง S = {spacing_m:.2f} m ให้ค่า Uav = {result.uav*100:.2f}% "
            f"ผ่านเป้าหมาย {target:.0f}%"
        )
    else:
        st.warning(
            f"⚠️ ระยะห่าง S = {spacing_m:.2f} m ให้ค่า Uav = {result.uav*100:.2f}% "
            f"ยังไม่ถึงเป้าหมาย {target:.0f}%"
        )

    if result.uv * 100 > 60:
        st.info(
            "Uv มากกว่า 60% ซึ่งอยู่นอกช่วงแนะนำของสมการประมาณ "
            "Uv = √(4Tv/π) ควรพิจารณาใช้สมการหรือ Time Factor ที่เหมาะสมเพิ่มเติม"
        )

    if consider_sand_mat:
        lm1, lm2, lm3 = st.columns(3)
        lm1.metric("Sand Mat resistance, L", f"{result.sand_mat_L:.4f}")
        lm2.metric("F(n)", f"{result.fn:.4f}")
        lm3.metric("F(n) + 0.8L", f"{result.radial_denominator:.4f}")
        if result.sand_mat_L > 1:
            st.warning("ค่า L ค่อนข้างสูง แสดงว่า Sand Mat มีความต้านทานต่อการระบายน้ำมากและทำให้ Ur ลดลง")

    st.markdown("### Settlement Projection")
    c1, c2 = st.columns([1, 2])
    with c1:
        s_final = st.number_input(
            "Ultimate Settlement, Sfinal (m)",
            min_value=0.0,
            value=1.0,
            step=0.05,
        )
        s_t = result.uav * s_final
        st.metric("Settlement at time t", f"{s_t:.4f} m")
        st.caption("St = Uav × Sfinal")

    with c2:
        days = list(range(1, int(max(time_day, 2)) + 1))
        curve_rows = []
        for d in days:
            r = calculate_pvd(
                spacing_m=spacing_m,
                pattern=pattern,
                a_cm=a_cm,
                b_cm=b_cm,
                dw_method=dw_method,
                cv_cm2_day=cv,
                kh_kv=kh_kv,
                time_day=d,
                hd_m=hd_m,
            )
            curve_rows.append(
                {
                    "Day": d,
                    "Settlement (m)": r.uav * s_final,
                    "Uav (%)": r.uav * 100,
                }
            )
        curve_df = pd.DataFrame(curve_rows)

        fig_settlement = go.Figure()
        fig_settlement.add_trace(
            go.Scatter(
                x=curve_df["Day"],
                y=curve_df["Settlement (m)"],
                fill="tozeroy",
                mode="lines",
                line=dict(width=4, color="#22D3EE"),
                fillcolor="rgba(34,211,238,.12)",
                name="Settlement",
            )
        )
        fig_settlement.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=25, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,.35)",
            font=dict(color="#C9D5E3"),
            xaxis=dict(title="Time (day)", gridcolor="rgba(148,163,184,.10)"),
            yaxis=dict(title="Settlement (m)", gridcolor="rgba(148,163,184,.10)"),
            showlegend=False,
        )
        st.plotly_chart(
            fig_settlement,
            use_container_width=True,
            config={"displayModeBar": False},
        )

with tab2:
    st.markdown("### Calculation Breakdown")

    details = pd.DataFrame(
        [
            ["Spacing, S", result.spacing_m, "m"],
            ["Influence diameter, de", result.de_cm, "cm"],
            ["Equivalent diameter, dw", result.dw_cm, "cm"],
            ["Diameter ratio, n", result.n, "-"],
            ["Spacing factor, F(n)", result.fn, "-"],
            ["Sand mat resistance index, L", result.sand_mat_L, "-"],
            ["Radial denominator, F(n)+0.8L", result.radial_denominator, "-"],
            ["Radial coefficient, Cr", result.cr_cm2_day, "cm²/day"],
            ["Radial time factor, Tr", result.tr, "-"],
            ["Vertical time factor, Tv", result.tv, "-"],
            ["Radial consolidation, Ur", result.ur * 100, "%"],
            ["Vertical consolidation, Uv", result.uv * 100, "%"],
            ["Combined consolidation, Uav", result.uav * 100, "%"],
            ["Maximum drainage path, Hd", hd_m, "m"],
        ],
        columns=["Parameter", "Value", "Unit"],
    )

    st.dataframe(
        details.style.format({"Value": "{:,.6f}"}),
        use_container_width=True,
        hide_index=True,
    )

    csv_detail = details.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download Calculation Report (CSV)",
        data=csv_detail,
        file_name="pvd_calculation_report.csv",
        mime="text/csv",
    )

    st.markdown("### Input Validation")
    check1, check2, check3 = st.columns(3)
    check1.metric("n = de/dw", f"{result.n:.2f}", "Valid" if result.n > 1 else "Invalid")
    check2.metric("kh/kv", f"{kh_kv:.2f}", "Typical 4–10")
    check3.metric("Hd", f"{hd_m:.2f} m", drainage)

with tab3:
    st.markdown("### Automatic Spacing Comparison")
    st.caption("ทดลองหลายระยะห่างเพื่อหาระยะสูงสุดที่ยังผ่านเกณฑ์")

    o1, o2, o3 = st.columns(3)
    with o1:
        s_min = st.number_input("S minimum (m)", min_value=0.10, value=0.60, step=0.05)
    with o2:
        s_max = st.number_input("S maximum (m)", min_value=0.10, value=1.50, step=0.05)
    with o3:
        s_step = st.number_input("Increment (m)", min_value=0.01, value=0.10, step=0.01)

    if s_max < s_min:
        st.error("S maximum ต้องมากกว่าหรือเท่ากับ S minimum")
    else:
        spacings: List[float] = []
        s = s_min
        while s <= s_max + 1e-9:
            spacings.append(round(s, 6))
            s += s_step

        rows: List[Dict[str, float]] = []
        for s in spacings:
            r = calculate_pvd(
                spacing_m=s,
                pattern=pattern,
                a_cm=a_cm,
                b_cm=b_cm,
                dw_method=dw_method,
                cv_cm2_day=cv,
                kh_kv=kh_kv,
                time_day=time_day,
                hd_m=hd_m,
            )
            rows.append(
                {
                    "S (m)": s,
                    "de (cm)": r.de_cm,
                    "n": r.n,
                    "F(n)": r.fn,
                    "L": r.sand_mat_L,
                    "F(n)+0.8L": r.radial_denominator,
                    "Tr": r.tr,
                    "Ur (%)": r.ur * 100,
                    "Uv (%)": r.uv * 100,
                    "Uav (%)": r.uav * 100,
                    "Status": "PASS" if r.uav * 100 >= target else "REVIEW",
                }
            )

        df = pd.DataFrame(rows)
        st.plotly_chart(
            comparison_chart(df, target),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        passed = df[df["Uav (%)"] >= target]
        if not passed.empty:
            best_s = passed["S (m)"].max()
            best_row = passed.loc[passed["S (m)"].idxmax()]
            st.success(
                f"ระยะห่างสูงสุดที่ยังผ่านเป้าหมายในช่วงทดลองคือ "
                f"S ≈ {best_s:.2f} m โดยมี Uav ≈ {best_row['Uav (%)']:.2f}%"
            )
        else:
            st.warning("ไม่มีระยะห่างในช่วงที่กำหนดผ่านเป้าหมาย")

        st.dataframe(
            df.style.format(
                {
                    "S (m)": "{:.2f}",
                    "de (cm)": "{:.2f}",
                    "n": "{:.3f}",
                    "F(n)": "{:.3f}",
                    "L": "{:.3f}",
                    "F(n)+0.8L": "{:.3f}",
                    "Tr": "{:.5f}",
                    "Ur (%)": "{:.2f}",
                    "Uv (%)": "{:.2f}",
                    "Uav (%)": "{:.2f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        csv_optimizer = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download Optimizer Results",
            data=csv_optimizer,
            file_name="pvd_spacing_optimizer.csv",
            mime="text/csv",
        )

with tab4:
    st.markdown("### Core Equations")

    f1, f2 = st.columns(2)
    with f1:
        st.markdown("#### Geometry")
        st.latex(r"d_e = 1.13S \quad \mathrm{(Square)}")
        st.latex(r"d_e = 1.05S \quad \mathrm{(Triangular)}")
        st.latex(r"d_w = \frac{a+b}{2} \quad \mathrm{(Rixner)}")
        st.latex(r"d_w = \frac{2(a+b)}{\pi} \quad \mathrm{(Hansbo)}")
        st.latex(r"n = \frac{d_e}{d_w}")
        st.latex(
            r"F(n)=\frac{n^2}{n^2-1}\ln(n)-\frac{3n^2-1}{4n^2}"
        )

    with f2:
        st.markdown("#### Consolidation")
        st.latex(r"C_r=\left(\frac{k_h}{k_v}\right)C_v")
        st.latex(r"T_r=\frac{C_rt}{d_e^2}")
        st.latex(r"L=\frac{32}{\pi^2}\frac{1}{n^2}\frac{H}{H_m}\frac{k_c}{k_m}\left(\frac{B}{d_w}\right)^2")
        st.caption("B คือครึ่งหนึ่งของความกว้าง Sand Mat ทั้งหมด (ความกว้างเต็ม = 2B)")
        st.latex(r"U_r=1-\exp\left(\frac{-8T_r}{F(n)+0.8L}\right)")
        st.latex(r"T_v=\frac{C_vt}{H_d^2}")
        st.latex(r"U_v=\frac{\sqrt{4T_v}}{\pi}")
        st.latex(r"U_{av}=1-(1-U_r)(1-U_v)")
        st.latex(r"S_t=U_{av}S_{final}")

    st.markdown(
        """
        <div class="footer-note">
        <b>Engineering note:</b> แบบจำลองนี้ยังไม่รวมผลของ smear zone,
        well resistance, drain discharge capacity, staged loading,
        surcharge stability และเงื่อนไขเฉพาะโครงการ จึงเหมาะสำหรับ
        การเรียนการสอนและการวิเคราะห์เบื้องต้น
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption("PVD Studio Pro · Streamlit Geotechnical Engineering Application")
