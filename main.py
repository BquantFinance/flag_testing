"""
Contratación Pública × Registro Mercantil
BQuant Finance · @Gsnchez · bquantfinance.com
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Señales en Contratación Pública · BQuant",
    page_icon="📊", layout="wide", initial_sidebar_state="collapsed",
)

DATA = Path("anomalias")
Q_DIR = DATA / "quality"

C = {
    'bg':'#080b12','card':'#0d1117','card2':'#131921','border':'#1e2636','border2':'#2a3348',
    'accent':'#e05a3a','accent2':'#f06e52','blue':'#4a8fe7','blue2':'#6baaff','teal':'#22d3a0',
    'amber':'#f0b030','red':'#ef5555','purple':'#9b7dea',
    'text':'#e8edf5','text2':'#9dafc8','muted':'#5e6f88','grid':'rgba(255,255,255,0.03)',
}

PL = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='IBM Plex Mono, JetBrains Mono, monospace', color=C['text'], size=11),
    margin=dict(l=50, r=30, t=50, b=40),
    hoverlabel=dict(bgcolor='rgba(11,14,21,0.97)', bordercolor=C['border2'],
                    font=dict(color=C['text'], size=11)),
)

# ═══════════════ CSS ═══════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

:root {{
    --bg:{C['bg']}; --card:{C['card']}; --card2:{C['card2']};
    --border:{C['border']}; --border2:{C['border2']};
    --accent:{C['accent']}; --accent2:{C['accent2']};
    --blue:{C['blue']}; --blue2:{C['blue2']};
    --teal:{C['teal']}; --amber:{C['amber']};
    --red:{C['red']}; --purple:{C['purple']};
    --text:{C['text']}; --text2:{C['text2']}; --muted:{C['muted']};
    --glow-accent: 0 0 20px rgba(224,90,58,.15), 0 0 60px rgba(224,90,58,.06);
    --glow-blue:   0 0 20px rgba(74,143,231,.15), 0 0 60px rgba(74,143,231,.06);
    --glow-teal:   0 0 20px rgba(34,211,160,.12), 0 0 60px rgba(34,211,160,.05);
    --glow-amber:  0 0 20px rgba(240,176,48,.12), 0 0 60px rgba(240,176,48,.05);
    --glow-purple: 0 0 20px rgba(155,125,234,.12),0 0 60px rgba(155,125,234,.05);
    --glow-red:    0 0 20px rgba(239,85,85,.12),  0 0 60px rgba(239,85,85,.05);
}}

/* ── App shell ── */
.stApp {{
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 80% 50% at 8% 0%, rgba(74,143,231,.05) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 92% 100%, rgba(224,90,58,.04) 0%, transparent 50%),
        radial-gradient(ellipse 50% 30% at 50% 40%, rgba(155,125,234,.02) 0%, transparent 60%);
    color: var(--text); font-family: 'DM Sans', -apple-system, sans-serif;
}}
section[data-testid="stSidebar"] {{ background: var(--card); border-right:1px solid var(--border) }}
.block-container {{ max-width:1180px; padding-top:1rem!important; padding-bottom:2rem!important }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width:6px; height:6px }}
::-webkit-scrollbar-track {{ background:transparent }}
::-webkit-scrollbar-thumb {{ background:rgba(255,255,255,.1); border-radius:4px }}
::-webkit-scrollbar-thumb:hover {{ background:rgba(255,255,255,.18) }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{ gap:0; border-bottom:1px solid var(--border); background:transparent }}
.stTabs [data-baseweb="tab"] {{
    background:transparent; color:var(--muted); border:none; padding:14px 28px;
    font-family:'DM Sans'; font-size:.82rem; font-weight:600; letter-spacing:.02em;
    transition:color .3s; border-bottom:2px solid transparent;
}}
.stTabs [data-baseweb="tab"]:hover {{ color:var(--text2) }}
.stTabs [aria-selected="true"] {{
    color:var(--accent)!important; border-bottom:2px solid var(--accent)!important;
    background:transparent!important; text-shadow:0 0 20px rgba(224,90,58,.3);
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:.5rem }}

/* ── Metrics ── */
div[data-testid="stMetric"] {{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:18px 22px; position:relative; overflow:hidden;
    transition:border-color .3s, box-shadow .3s;
}}
div[data-testid="stMetric"]:hover {{
    border-color:var(--border2); box-shadow:var(--glow-blue);
}}
div[data-testid="stMetric"]::before {{
    content:''; position:absolute; top:0;left:0;right:0; height:2px;
    background:linear-gradient(90deg,transparent 10%,var(--blue) 50%,transparent 90%); opacity:.4;
}}
div[data-testid="stMetric"] label {{
    color:var(--muted)!important; font-family:'IBM Plex Mono'; font-size:.58rem!important;
    letter-spacing:.1em; text-transform:uppercase;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color:var(--text)!important; font-family:'IBM Plex Mono'; font-size:1.25rem!important; font-weight:600;
}}

/* ── Expander ── */
div[data-testid="stExpander"] {{
    background:var(--card)!important; border:1px solid var(--border)!important;
    border-radius:14px!important; overflow:hidden; transition:border-color .3s;
}}
div[data-testid="stExpander"]:hover {{ border-color:var(--border2)!important }}
div[data-testid="stExpander"] details summary {{
    font-family:'DM Sans'; font-size:.84rem; font-weight:600; color:var(--text2); padding:14px 18px;
}}
div[data-testid="stExpander"] details[open] summary {{ border-bottom:1px solid var(--border) }}

/* ── Inputs ── */
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {{
    background:var(--card2)!important; color:var(--text)!important;
    border:1px solid var(--border)!important; border-radius:12px!important;
    font-family:'IBM Plex Mono'; font-size:.82rem!important; padding:10px 14px!important;
    transition:border-color .3s, box-shadow .3s;
}}
div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {{
    border-color:var(--blue)!important; box-shadow:0 0 0 3px rgba(74,143,231,.15), var(--glow-blue)!important;
}}
div[data-testid="stTextInput"] input::placeholder {{ color:var(--muted)!important; opacity:.7 }}
div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, .stSelectbox label, .stMultiSelect label {{
    color:var(--muted)!important; font-family:'IBM Plex Mono'; font-size:.6rem!important;
    letter-spacing:.08em; text-transform:uppercase;
}}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {{
    background:var(--card2)!important; color:var(--text)!important;
    border:1px solid var(--border)!important; border-radius:12px!important;
    font-family:'DM Sans'; font-size:.82rem!important; transition:border-color .3s;
}}
.stSelectbox [data-baseweb="select"] > div:hover {{ border-color:var(--border2)!important }}
.stSelectbox [data-baseweb="select"] > div:focus-within {{
    border-color:var(--blue)!important; box-shadow:0 0 0 3px rgba(74,143,231,.15)!important;
}}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {{
    background:{C['card2']}!important; border:1px solid var(--border2)!important; border-radius:12px!important;
}}
[data-baseweb="popover"] li {{
    color:var(--text2)!important; font-family:'DM Sans'; font-size:.82rem!important; transition:background .2s;
}}
[data-baseweb="popover"] li:hover {{ background:rgba(74,143,231,.1)!important; color:var(--text)!important }}
[data-baseweb="popover"] li[aria-selected="true"] {{ background:rgba(224,90,58,.12)!important; color:var(--accent)!important }}

/* ── Multiselect ── */
.stMultiSelect [data-baseweb="select"] > div {{
    background:var(--card2)!important; color:var(--text)!important;
    border:1px solid var(--border)!important; border-radius:12px!important;
    font-family:'DM Sans'; font-size:.82rem!important; min-height:44px; transition:border-color .3s;
}}
.stMultiSelect [data-baseweb="select"] > div:hover {{ border-color:var(--border2)!important }}
.stMultiSelect [data-baseweb="select"] > div:focus-within {{
    border-color:var(--blue)!important; box-shadow:0 0 0 3px rgba(74,143,231,.15)!important;
}}
.stMultiSelect [data-baseweb="tag"] {{
    background:rgba(224,90,58,.12)!important; border:1px solid rgba(224,90,58,.3)!important;
    border-radius:8px!important; color:var(--accent2)!important;
    font-family:'DM Sans'; font-size:.78rem!important; font-weight:600;
    box-shadow:0 0 10px rgba(224,90,58,.08);
}}
.stMultiSelect [data-baseweb="tag"] span {{ color:var(--accent2)!important }}

/* ── Radio ── */
.stRadio > div {{ gap:0!important }}
.stRadio [data-baseweb="radio"] {{
    background:var(--card)!important; border:1px solid var(--border)!important;
    border-radius:12px!important; padding:10px 18px!important; margin:0 6px 6px 0!important;
    transition:all .3s;
}}
.stRadio [data-baseweb="radio"]:hover {{ border-color:var(--border2)!important; background:var(--card2)!important }}
.stRadio [data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {{
    font-family:'DM Sans'!important; font-size:.8rem!important; color:var(--text2)!important; font-weight:500;
}}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {{ border:1px solid var(--border); border-radius:14px; overflow:hidden }}

/* ── Buttons ── */
.stButton > button {{
    background:var(--card2)!important; color:var(--text)!important;
    border:1px solid var(--border)!important; border-radius:12px!important;
    font-family:'DM Sans'; font-weight:600; font-size:.82rem; padding:8px 20px; transition:all .3s;
}}
.stButton > button:hover {{
    border-color:var(--accent)!important; color:var(--accent)!important;
    box-shadow:var(--glow-accent);
}}

/* ── Alert ── */
div[data-testid="stAlert"] {{
    background:var(--card)!important; border:1px solid var(--border)!important;
    border-radius:12px!important; color:var(--text2)!important; font-size:.82rem; font-family:'DM Sans';
}}

/* ── Caption ── */
.stCaption, div[data-testid="stCaptionContainer"] {{
    font-family:'IBM Plex Mono'!important; font-size:.72rem!important; color:var(--muted)!important;
}}

/* ══════════════════════════════════
   CUSTOM CLASSES
   ══════════════════════════════════ */

/* ── Hero ── */
.hero {{ text-align:center; padding:3rem 0 .8rem; animation:fadeIn .7s ease-out }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px) }} to {{ opacity:1; transform:translateY(0) }} }}
.hero h1 {{
    font-family:'Newsreader',Georgia,serif; font-size:2.6rem; font-weight:700;
    color:var(--text); letter-spacing:-.03em; margin:0; line-height:1.15;
}}
.hero h1 span {{
    color:var(--accent);
    background:linear-gradient(135deg,var(--accent) 20%,var(--accent2) 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    filter:drop-shadow(0 0 12px rgba(224,90,58,.25));
}}
.hero .mono {{
    font-family:'IBM Plex Mono'; font-size:.6rem; color:var(--muted);
    letter-spacing:.2em; text-transform:uppercase; margin-top:.6rem;
}}
.hero-desc {{
    font-family:'Newsreader',Georgia,serif; font-size:1.05rem; font-style:italic;
    color:var(--text2); max-width:640px; margin:1rem auto 0; line-height:1.7;
}}
.hero-desc b {{ color:var(--text); font-weight:600; font-style:normal }}

/* ── Divider ── */
.divider {{
    height:1px; margin:1.5rem 0;
    background:linear-gradient(90deg,transparent 2%,{C['border2']} 50%,transparent 98%);
}}

/* ── Section header ── */
.sec {{
    font-family:'IBM Plex Mono'; font-size:.64rem; font-weight:600;
    color:var(--accent); letter-spacing:.14em; text-transform:uppercase;
    border-bottom:1px solid var(--border); padding-bottom:8px;
    margin:2.2rem 0 1.1rem; position:relative;
    text-shadow:0 0 18px rgba(224,90,58,.2);
}}
.sec::after {{
    content:''; position:absolute; bottom:-1px; left:0; width:42px; height:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
    border-radius:1px; box-shadow:0 0 8px rgba(224,90,58,.3);
}}

/* ── Cards ── */
.card {{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:20px 24px; margin:10px 0; font-size:.84rem; color:var(--text2); line-height:1.7;
    transition:border-color .3s, box-shadow .3s;
}}
.card:hover {{ border-color:var(--border2); box-shadow:0 4px 24px rgba(0,0,0,.15) }}
.card b {{ color:var(--text) }}
.card-l {{ border-left:3px solid; border-radius:0 14px 14px 0; padding-left:22px }}
.card-accent {{ border-left-color:var(--accent); box-shadow:inset 3px 0 12px -6px rgba(224,90,58,.15) }}
.card-blue  {{ border-left-color:var(--blue);   box-shadow:inset 3px 0 12px -6px rgba(74,143,231,.15) }}
.card-teal  {{ border-left-color:var(--teal);   box-shadow:inset 3px 0 12px -6px rgba(34,211,160,.12) }}
.card-amber {{ border-left-color:var(--amber);  box-shadow:inset 3px 0 12px -6px rgba(240,176,48,.12) }}
.card-red   {{ border-left-color:var(--red);    box-shadow:inset 3px 0 12px -6px rgba(239,85,85,.12) }}

/* ── Badges ── */
.badge {{
    display:inline-block; padding:3px 11px; border-radius:7px;
    font-family:'IBM Plex Mono'; font-size:.58rem; font-weight:600;
    margin:2px 4px 2px 0; letter-spacing:.04em; vertical-align:middle;
}}
.b-red    {{ background:rgba(239,85,85,.12);  color:var(--red);    border:1px solid rgba(239,85,85,.22);  box-shadow:0 0 10px rgba(239,85,85,.06) }}
.b-blue   {{ background:rgba(74,143,231,.12); color:var(--blue2);  border:1px solid rgba(74,143,231,.22); box-shadow:0 0 10px rgba(74,143,231,.06) }}
.b-amber  {{ background:rgba(240,176,48,.12); color:var(--amber);  border:1px solid rgba(240,176,48,.22); box-shadow:0 0 10px rgba(240,176,48,.06) }}
.b-teal   {{ background:rgba(34,211,160,.12); color:var(--teal);   border:1px solid rgba(34,211,160,.22); box-shadow:0 0 10px rgba(34,211,160,.06) }}
.b-purple {{ background:rgba(155,125,234,.12);color:var(--purple); border:1px solid rgba(155,125,234,.22);box-shadow:0 0 10px rgba(155,125,234,.06) }}

/* ── Warning box ── */
.warn-box {{
    background:rgba(240,176,48,.04); border:1px solid rgba(240,176,48,.15);
    border-radius:14px; padding:18px 22px; font-size:.82rem; color:var(--text2); line-height:1.7;
    margin-bottom:1rem; position:relative; overflow:hidden;
    box-shadow:0 0 30px rgba(240,176,48,.04);
}}
.warn-box::before {{
    content:''; position:absolute; top:0;left:0;bottom:0; width:3px;
    background:var(--amber); border-radius:3px 0 0 3px; box-shadow:0 0 10px rgba(240,176,48,.3);
}}
.warn-box b {{ color:var(--text) }}

/* ── Example box ── */
.example-box {{
    background:rgba(74,143,231,.03); border:1px solid rgba(74,143,231,.12);
    border-left:3px solid rgba(74,143,231,.35); border-radius:0 12px 12px 0;
    padding:14px 18px; margin:10px 0 0; font-size:.78rem; font-family:'IBM Plex Mono';
    color:var(--text2); line-height:1.65;
    box-shadow:inset 3px 0 12px -6px rgba(74,143,231,.1);
}}
.example-box b {{ color:var(--blue2) }}
.example-box .ex-label {{
    font-size:.56rem; letter-spacing:.12em; text-transform:uppercase;
    color:var(--blue); margin-bottom:5px; display:block; font-weight:600;
    text-shadow:0 0 12px rgba(74,143,231,.3);
}}

/* ── Pipeline steps ── */
.step {{
    display:flex; gap:18px; margin:10px 0; padding:20px 24px;
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    transition:border-color .3s, box-shadow .3s; position:relative;
}}
.step:hover {{ border-color:var(--border2); box-shadow:0 4px 24px rgba(0,0,0,.15) }}
.step::before {{
    content:''; position:absolute; top:0;left:0;bottom:0; width:2px;
    background:linear-gradient(180deg,rgba(224,90,58,.3),rgba(224,90,58,.05)); border-radius:2px;
}}
.step-n {{
    flex-shrink:0; width:38px; height:38px; line-height:38px; text-align:center;
    background:linear-gradient(135deg,var(--accent),var(--accent2)); color:#fff;
    font-family:'IBM Plex Mono'; font-size:.78rem; font-weight:700; border-radius:10px;
    box-shadow:0 3px 16px rgba(224,90,58,.3), 0 0 0 3px rgba(224,90,58,.1);
}}
.step-body {{ flex:1; font-size:.84rem; color:var(--text2); line-height:1.7 }}
.step-body b {{ color:var(--text) }}
.step-body .step-title {{
    font-family:'DM Sans'; font-size:.94rem; font-weight:700; color:var(--text);
    margin-bottom:6px; letter-spacing:-.01em;
}}
.step-body code {{
    background:rgba(74,143,231,.08); color:var(--blue2);
    padding:3px 8px; border-radius:6px; font-family:'IBM Plex Mono'; font-size:.72rem;
    border:1px solid rgba(74,143,231,.12);
}}
.step-stat {{
    display:inline-block; padding:4px 10px; border-radius:7px;
    background:rgba(34,211,160,.07); color:var(--teal);
    font-family:'IBM Plex Mono'; font-size:.65rem; font-weight:600;
    border:1px solid rgba(34,211,160,.18); margin:3px 2px;
    box-shadow:0 0 8px rgba(34,211,160,.06); transition:all .3s;
}}
.step-stat:hover {{ background:rgba(34,211,160,.12); box-shadow:0 0 14px rgba(34,211,160,.1) }}

/* ── Signal cards ── */
.signal-card {{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:20px 24px; margin:10px 0; position:relative; overflow:hidden;
    transition:border-color .3s, box-shadow .3s, transform .2s;
}}
.signal-card:hover {{
    border-color:var(--border2); box-shadow:0 8px 32px rgba(0,0,0,.2); transform:translateY(-1px);
}}
.signal-card::after {{
    content:''; position:absolute; top:0;right:0; width:100px; height:100px;
    background:radial-gradient(circle at 100% 0%,rgba(224,90,58,.04),transparent 70%); pointer-events:none;
}}
.signal-title {{
    font-family:'DM Sans'; font-size:.94rem; font-weight:700; color:var(--text);
    margin-bottom:8px; letter-spacing:-.01em;
}}
.signal-body {{ font-size:.82rem; color:var(--text2); line-height:1.7 }}
.signal-stats {{ display:flex; gap:10px; margin-top:12px; flex-wrap:wrap }}
.signal-stat {{
    padding:7px 14px; border-radius:8px; background:rgba(255,255,255,.025);
    border:1px solid var(--border); font-family:'IBM Plex Mono'; font-size:.68rem; color:var(--text2);
    transition:all .3s;
}}
.signal-stat:hover {{ background:rgba(255,255,255,.05); border-color:var(--border2); box-shadow:0 2px 12px rgba(0,0,0,.1) }}
.signal-stat b {{ color:var(--text); font-size:.8rem }}

/* ── Dataset cards ── */
.ds-card {{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:22px 24px; position:relative; overflow:hidden;
    transition:border-color .3s, box-shadow .3s, transform .2s;
    animation:slideUp .4s ease-out both;
}}
.ds-card:hover {{
    border-color:var(--border2); transform:translateY(-1px);
}}
.ds-card::before {{
    content:''; position:absolute; top:0;left:0;right:0; height:2px; border-radius:14px 14px 0 0;
}}
.ds-card.ds-blue::before  {{ background:linear-gradient(90deg,var(--blue),rgba(74,143,231,.3)) }}
.ds-card.ds-teal::before  {{ background:linear-gradient(90deg,var(--teal),rgba(34,211,160,.3)) }}
.ds-card.ds-amber::before {{ background:linear-gradient(90deg,var(--amber),rgba(240,176,48,.3)) }}
.ds-card.ds-purple::before{{ background:linear-gradient(90deg,var(--purple),rgba(155,125,234,.3)) }}
.ds-card.ds-blue:hover  {{ box-shadow:var(--glow-blue) }}
.ds-card.ds-teal:hover  {{ box-shadow:var(--glow-teal) }}
.ds-card.ds-amber:hover {{ box-shadow:var(--glow-amber) }}
.ds-card.ds-purple:hover{{ box-shadow:var(--glow-purple) }}
.ds-icon {{ font-size:1.4rem; margin-bottom:8px; display:block }}
.ds-name {{ font-family:'DM Sans'; font-size:1rem; font-weight:700; color:var(--text); margin-bottom:4px }}
.ds-full {{ font-family:'IBM Plex Mono'; font-size:.6rem; color:var(--muted); letter-spacing:.04em; margin-bottom:10px; display:block }}
.ds-desc {{ font-size:.82rem; color:var(--text2); line-height:1.65; margin-bottom:12px }}
.ds-desc b {{ color:var(--text) }}
.ds-metrics {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px }}
.ds-metric {{
    padding:5px 12px; border-radius:7px; background:rgba(255,255,255,.025);
    border:1px solid var(--border); font-family:'IBM Plex Mono'; font-size:.66rem; color:var(--text2);
    transition:all .3s;
}}
.ds-metric:hover {{ background:rgba(255,255,255,.045); border-color:var(--border2) }}
.ds-metric b {{ color:var(--text); font-size:.76rem }}
.ds-quality {{
    margin-top:12px; padding-top:12px; border-top:1px solid var(--border);
    font-size:.74rem; color:var(--muted); line-height:1.6; font-family:'IBM Plex Mono';
}}
.ds-quality b {{ color:var(--text2) }}
.ds-quality .q-good {{ color:var(--teal); text-shadow:0 0 8px rgba(34,211,160,.3) }}
.ds-quality .q-warn {{ color:var(--amber); text-shadow:0 0 8px rgba(240,176,48,.3) }}
.ds-quality .q-bad  {{ color:var(--red); text-shadow:0 0 8px rgba(239,85,85,.3) }}

/* ── Screener ── */
.scr-header {{ font-family:'Newsreader',Georgia,serif; font-size:1.2rem; font-weight:600; color:var(--text); margin-bottom:4px }}
.scr-sub {{ font-size:.82rem; color:var(--text2); line-height:1.6; margin-bottom:16px }}
.scr-results {{
    background:var(--card); border:1px solid var(--border); border-radius:14px;
    padding:22px 26px; margin-top:12px;
    box-shadow:0 0 40px rgba(0,0,0,.1);
}}
.scr-count {{ font-family:'IBM Plex Mono'; font-size:1.8rem; font-weight:700; color:var(--text); line-height:1; text-shadow:0 0 20px rgba(74,143,231,.15) }}
.scr-count-label {{ font-family:'IBM Plex Mono'; font-size:.62rem; color:var(--muted); letter-spacing:.1em; text-transform:uppercase; margin-top:4px }}
.scr-active-flags {{ display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 6px }}
.scr-pill {{
    display:inline-flex; align-items:center; gap:6px; padding:6px 14px; border-radius:8px;
    font-family:'DM Sans'; font-size:.78rem; font-weight:600; border:1px solid; transition:all .3s;
}}
.scr-pill-red    {{ background:rgba(239,85,85,.08);  color:var(--red);    border-color:rgba(239,85,85,.22);  box-shadow:0 0 10px rgba(239,85,85,.05) }}
.scr-pill-blue   {{ background:rgba(74,143,231,.08); color:var(--blue2);  border-color:rgba(74,143,231,.22); box-shadow:0 0 10px rgba(74,143,231,.05) }}
.scr-pill-amber  {{ background:rgba(240,176,48,.08); color:var(--amber);  border-color:rgba(240,176,48,.22); box-shadow:0 0 10px rgba(240,176,48,.05) }}
.scr-pill-teal   {{ background:rgba(34,211,160,.08); color:var(--teal);   border-color:rgba(34,211,160,.22); box-shadow:0 0 10px rgba(34,211,160,.05) }}
.scr-pill-purple {{ background:rgba(155,125,234,.08);color:var(--purple); border-color:rgba(155,125,234,.22);box-shadow:0 0 10px rgba(155,125,234,.05) }}
.scr-logic {{
    display:inline-block; padding:3px 10px; border-radius:7px;
    font-family:'IBM Plex Mono'; font-size:.6rem; font-weight:700; letter-spacing:.08em;
}}
.scr-logic-and {{ background:rgba(34,211,160,.1); color:var(--teal); border:1px solid rgba(34,211,160,.22) }}
.scr-logic-or  {{ background:rgba(74,143,231,.1); color:var(--blue2); border:1px solid rgba(74,143,231,.22) }}
.scr-empty {{ text-align:center; padding:40px 20px; color:var(--muted); font-family:'DM Sans'; font-size:.9rem }}
.scr-empty-icon {{ font-size:2rem; margin-bottom:8px; display:block; opacity:.5 }}

/* ── Footer ── */
.ft {{
    text-align:center; color:var(--muted); font-family:'IBM Plex Mono'; font-size:.58rem;
    letter-spacing:.06em; padding:2rem 0 .8rem; border-top:1px solid var(--border); margin-top:2.5rem;
}}
.ft a {{ color:var(--accent); text-decoration:none; transition:color .3s }}
.ft a:hover {{ color:var(--accent2); text-shadow:0 0 10px rgba(224,90,58,.3) }}

/* ── Hide chrome ── */
#MainMenu {{ visibility:hidden }} footer {{ visibility:hidden }} header {{ visibility:hidden }}

/* ── Animations ── */
@keyframes slideUp {{ from {{ opacity:0; transform:translateY(12px) }} to {{ opacity:1; transform:translateY(0) }} }}
.signal-card, .step, .card, .example-box, .warn-box {{ animation:slideUp .4s ease-out both }}
</style>
""", unsafe_allow_html=True)

# ═══════════════ HELPERS ═══════════════
def fmt(n):
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.0f}K"
    return f"{int(n):,}"

@st.cache_data(show_spinner=False)
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

@st.cache_data(show_spinner=False)
def load_pq(path):
    return pd.read_parquet(path)

# ═══════════════ FLAG REGISTRY ═══════════════
FLAGS = {
    'flag1_recien_creada': {'label':'Empresa recién creada','short':'F1','icon':'🆕','badge':'b-red','scope':'Nacional','color':C['red'],
        'what':'Empresa constituida <b>menos de 6 meses antes</b> de recibir su primer contrato público.',
        'why':'Puede indicar una sociedad instrumental creada ad hoc para una adjudicación concreta.',
        'how':'Acto "Constitución" en BORME → primera fecha → comparar con adjudicación. Flag si <b>0–180 días</b>.',
        'example':'Empresa constituida el 15/03/2022, primera adjudicación el 28/07/2022 — 135 días. Contrato de 287.000€.','stat_empresas':5435,'stat_extra':'890M€ en contratos'},
    'flag2_capital_ridiculo': {'label':'Capital social mínimo','short':'F2','icon':'💰','badge':'b-amber','scope':'Nacional','color':C['amber'],
        'what':'Capital social <b>inferior a 10.000€</b> y contratos superiores a 100.000€.',
        'why':'Un capital tan bajo es inusual para empresas en contratación pública relevante.',
        'how':'Capital más reciente en BORME. Flag si capital < 10K€ y adjudicación > 100K€.',
        'example':'Capital social de 3.006€. Adjudicación de 425.000€ en consultoría — ratio 141:1.','stat_empresas':5735,'stat_extra':'Ratio medio: 85x'},
    'flag4_disolucion': {'label':'Empresa disuelta','short':'F4','icon':'💀','badge':'b-red','scope':'Nacional','color':C['red'],
        'what':'Acto de <b>disolución/extinción</b> en BORME con adjudicaciones en los 365 días posteriores.',
        'why':'Una empresa disuelta no debería participar en licitaciones.',
        'how':'Actos "Disolución|Extinción". Flag si adjudicación entre 0–365 días después.',
        'example':'Disolución el 04/11/2021. Adjudicación de 89.000€ el 22/02/2022 — 110 días después.','stat_empresas':1294,'stat_extra':'210M€ post-disolución'},
    'flag5_concursal': {'label':'En concurso de acreedores','short':'F5','icon':'⚖️','badge':'b-red','scope':'Nacional','color':C['red'],
        'what':'Empresa en <b>situación concursal</b> según BORME que sigue recibiendo adjudicaciones.',
        'why':'La legislación restringe la contratación pública a empresas en insolvencia.',
        'how':'Acto "concurso|concursal" en BORME. Flag si adjudicaciones posteriores.',
        'example':'Concurso voluntario 12/06/2020. 3 adjudicaciones por 156.000€ entre 2021–2022.','stat_empresas':540,'stat_extra':'95M€ post-concurso'},
    'flag6_admin_network': {'label':'Red de administradores (detalle)','short':'F6','icon':'🕸️','badge':'b-blue','scope':'Nacional','color':C['blue'],
        'what':'Dos empresas comparten <b>administrador</b>, no son del mismo grupo, y ganan contratos ante los <b>mismos organismos</b>.',
        'why':'Sugiere posible coordinación de ofertas entre empresas aparentemente independientes.',
        'how':'Cargos activos BORME × adjudicaciones PLACSP. ≥2 órganos comunes. Filtro grupos corporativos.',
        'example':'Persona X es Adm. Único de Empresa A y Cons. Delegado de Empresa B. Ambas ganan en 7 órganos comunes.','stat_empresas':2684,'stat_extra':'2.287 pares · 1.416 personas'},
    'flag6_pares_unicos': {'label':'Pares únicos de empresas','short':'F6','icon':'🔗','badge':'b-blue','scope':'Nacional','color':C['blue'],
        'what':'Pares agregados: cada par aparece una vez con <b>todas las personas que los conectan</b>.',
        'why':'Un par con 3 personas compartidas es más significativo que uno con 1.','how':'Agrupación de F6 por par.',
        'example':'Empresa A y B conectadas por 3 personas, coinciden en 12 órganos.','stat_empresas':1878,'stat_extra':'1.878 pares únicos'},
    'flag6_personas_resumen': {'label':'Personas con más conexiones','short':'F6','icon':'👤','badge':'b-blue','scope':'Nacional','color':C['blue'],
        'what':'Ranking de <b>personas</b> que conectan más pares de empresas adjudicatarias.','why':'','how':'Agregación por persona.',
        'example':'','stat_empresas':1416,'stat_extra':'Máx: 47 pares/persona'},
    'flag6_admin_network_cat': {'label':'Red administradores CAT','short':'F6','icon':'🕸️','badge':'b-blue','scope':'Catalunya','color':C['blue'],
        'what':'Misma lógica F6 para contratación catalana.','why':'','how':'','example':'','stat_empresas':571,'stat_extra':'439 pares'},
    'flag6_pares_cat': {'label':'Pares únicos CAT','short':'F6','icon':'🔗','badge':'b-blue','scope':'Catalunya','color':C['blue'],
        'what':'Pares agregados en Catalunya.','why':'','how':'','example':'','stat_empresas':353,'stat_extra':''},
    'flag6_personas_cat': {'label':'Personas conexiones CAT','short':'F6','icon':'👤','badge':'b-blue','scope':'Catalunya','color':C['blue'],
        'what':'Personas que conectan más pares en Catalunya.','why':'','how':'','example':'','stat_empresas':0,'stat_extra':''},
    'flag7_concentracion': {'label':'Empresa dominante en un órgano','short':'F7','icon':'🎯','badge':'b-teal','scope':'Nacional','color':C['teal'],
        'what':'Una empresa gana <b>más del 40%</b> de las adjudicaciones de un organismo.',
        'why':'Indica posible relación preferente.','how':'>40% adj del órgano, mín. 5 propias y 10 totales.',
        'example':'Empresa gana 87 de 142 adj (61%) de un órgano municipal — 4.2M€.','stat_empresas':286,'stat_extra':'358 pares empresa-órgano'},
    'flag7_concentracion_cat': {'label':'Empresa dominante CAT','short':'F7','icon':'🎯','badge':'b-teal','scope':'Catalunya','color':C['teal'],
        'what':'Umbral adaptativo: ≥200 adj→20%, ≥50→30%, <50→40%.','why':'','how':'','example':'','stat_empresas':10,'stat_extra':''},
    'flag8_utes_sospechosas': {'label':'UTEs con miembros vinculados','short':'F8','icon':'🤝','badge':'b-amber','scope':'Nacional','color':C['amber'],
        'what':'<b>UTEs</b> cuyos miembros comparten administrador según BORME.',
        'why':'Si los dos miembros de una UTE tienen el mismo decisor, la unión no es independiente.',
        'how':'Se parsean miembros del nombre UTE y se cruzan con F6.',
        'example':'UTE: Empresa A + B. Ambas tienen a Persona X como Adm. Solidario.','stat_empresas':97,'stat_extra':'127 pares'},
    'flag8_utes_cat': {'label':'UTEs CAT','short':'F8','icon':'🤝','badge':'b-amber','scope':'Catalunya','color':C['amber'],
        'what':'UTEs vinculadas en Catalunya.','why':'','how':'','example':'','stat_empresas':0,'stat_extra':''},
    'flag9_geo_discrepancia': {'label':'Empresa lejos de donde contrata','short':'F9','icon':'📍','badge':'b-purple','scope':'Nacional','color':C['purple'],
        'what':'Empresa registrada en una CCAA que gana contratos <b>mayoritariamente en otra</b>. <span style="color:#6b7280;font-size:.78rem">Señal débil — alta tasa de falsos positivos. Cobra sentido combinada con otras señales.</span>',
        'why':'Solo PYMEs (3–200 adj). Las grandes con sede en Madrid se excluyen.',
        'how':'Provincia BORME → CCAA registro. NUTS2 → CCAA contratos.',
        'example':'Empresa de Murcia que gana 28 de 31 contratos en Andalucía — 1.8M€.','stat_empresas':14832,'stat_extra':'De 27.465 con CCAA mapeada'},
    'flag10_troceo_cat': {'label':'Posible fraccionamiento','short':'F10','icon':'✂️','badge':'b-red','scope':'Catalunya','color':C['red'],
        'what':'≥3 contratos en 90 días, todos bajo 15K€, pero cuya <b>suma supera el umbral</b>.',
        'why':'Posible división artificial para evitar licitar públicamente.',
        'how':'Sliding window 90 días por par empresa×órgano.',
        'example':'5 contratos de 12.8K, 14.2K, 11.5K, 13.9K, 14.7K€ en 67 días. Suma: 67.1K€ (4.5× umbral).','stat_empresas':2651,'stat_extra':'4.331 clusters · 33K€ media'},
    'flag11_modificaciones_cat': {'label':'Modificaciones excesivas','short':'F11','icon':'📝','badge':'b-amber','scope':'Catalunya','color':C['amber'],
        'what':'≥20% de contratos modificados (media: ~0.6%).',
        'why':'Puede indicar adjudicaciones inicialmente bajas que se incrementan después.',
        'how':'Columnas nativas registro catalán. ≥3 modificaciones y ≥20%.',
        'example':'14 contratos, 5 modificados (36%). Incremento medio: +42%.','stat_empresas':115,'stat_extra':'36× la media'},
    'risk_scoring_unificado': {'label':'Empresas con señales acumuladas','short':'Resumen','icon':'🚩','badge':'b-red','scope':'Nacional','color':C['accent'],
        'what':'Todas las empresas con <b>al menos 1 señal</b>. Muestra qué señales tiene cada una.','why':'','how':'Unión F1–F9.',
        'example':'','stat_empresas':25675,'stat_extra':'125 con ≥3 señales'},
    'risk_scoring_cat': {'label':'Empresas señales CAT','short':'Resumen','icon':'🚩','badge':'b-red','scope':'Catalunya','color':C['accent'],
        'what':'Empresas catalanas con ≥1 señal.','why':'','how':'','example':'','stat_empresas':4203,'stat_extra':''},
    'grupos_corporativos': {'label':'Grupos corporativos (filtrados)','short':'Grp','icon':'🏢','badge':'b-teal','scope':'Nacional','color':C['teal'],
        'what':'Pares <b>descartados como grupo corporativo</b> legítimo.','why':'No son sospechosos.','how':'',
        'example':'','stat_empresas':1683,'stat_extra':'Pares eliminados'},
    'grupos_corporativos_cat': {'label':'Grupos corporativos CAT','short':'Grp','icon':'🏢','badge':'b-teal','scope':'Catalunya','color':C['teal'],
        'what':'Grupos filtrados en Catalunya.','why':'','how':'','example':'','stat_empresas':295,'stat_extra':''},
}

# ── Pipeline-level metadata (source stats not derivable from output parquets) ──
# Update these if you re-run the pipeline with new data.
PIPELINE = {
    'borme_pdfs': 126_065, 'borme_actos': 17_100_000, 'borme_empresas': 2_770_000, 'borme_personas': 3_800_000,
    'placsp_total': 8_700_000, 'placsp_useful': 5_800_000,
    'cat_total': 3_400_000, 'cat_menores': 177_000,
    'stop_words': 5_550, 'manual_rules': 203, 'auto_rules': 5_400,
    'matched_nac': 126_073, 'matched_cat': 23_156, 'coverage_pct': 52,
    'f6_cargos_total': 618_000, 'f6_cargos_decision': 232_000, 'f6_cargos_activos': 212_000,
    'f6_personas_multi': 7_514, 'f6_pares_iniciales': 3_970,
}

# Parquets to silently ignore (superseded or too noisy to display)
_EXCLUDE_STEMS = {'flag3_multi_admin'}

def discover_flags():
    found = {}
    for d, scope in [(DATA, 'Nacional'), (DATA / 'catalunya', 'Catalunya')]:
        if d.exists():
            for f in sorted(d.glob('*.parquet')):
                if f.stem not in _EXCLUDE_STEMS:
                    found[f.stem] = {'path': str(f), 'scope': scope, 'size': f.stat().st_size}
    return found

@st.cache_data(show_spinner=False)
def _dynamic_stats():
    """Compute stats from parquets dynamically — empresas, rows, importe."""
    ff = discover_flags(); out = {}
    for stem, fi in ff.items():
        try:
            df = load_pq(fi['path'])
            emp_col = next((c for c in ['empresa_norm','adj_norm'] if c in df.columns), None)
            n_emp = int(df[emp_col].nunique()) if emp_col else len(df)
            imp_col = next((c for c in df.columns if 'importe' in c.lower() and pd.api.types.is_numeric_dtype(df[c])), None)
            imp_sum = float(df[imp_col].sum()) if imp_col else 0
            out[stem] = {'n_empresas': n_emp, 'n_rows': len(df), 'importe': imp_sum}
        except Exception:
            out[stem] = {'n_empresas': 0, 'n_rows': 0, 'importe': 0}
    # Risk scoring: count empresas with ≥3 flags
    for k in ['risk_scoring_unificado', 'risk_scoring_cat']:
        if k in out:
            try:
                df = load_pq(ff[k]['path'])
                if 'n_flags' in df.columns:
                    out[k]['n_ge3'] = int((df['n_flags'] >= 3).sum())
            except Exception:
                pass
    return out

def _ds(stem, field='n_empresas'):
    """Get a dynamic stat for a flag stem. Returns 0 if not found."""
    return _dynamic_stats().get(stem, {}).get(field, 0)

def _ds_fmt(stem, field='n_empresas'):
    """Get a formatted dynamic stat (e.g. '5.435')."""
    v = _ds(stem, field)
    if isinstance(v, float) and v >= 1e6:
        return f"{v/1e6:.0f}M€"
    return f"{v:,.0f}".replace(',', '.')

def get_meta(stem):
    base = FLAGS.get(stem, {'label':stem,'short':'?','icon':'📄','badge':'b-blue','scope':'?','color':C['blue'],
        'what':'','why':'','how':'','example':'','stat_empresas':0,'stat_extra':''})
    # Override stat_empresas with dynamic count if parquet exists
    dyn = _dynamic_stats().get(stem)
    if dyn:
        base = {**base, 'stat_empresas': dyn['n_empresas']}
    return base

_HIDE = {'cargo_norm','cargo_upper','cargo_w','organo_norm','same_group','is_fusion_borme',
         'size_penalty','flag_weight',
         'risk_score','score','score_max','score_sum','par_score','score_total',
         'f6_score','f7_max_conc','cargo_weight','concentracion'}

def clean_df(df):
    return df.drop(columns=[c for c in df.columns if c in _HIDE], errors='ignore')

@st.cache_data(show_spinner=False)
def search_all(q, flag_files):
    results = []
    for stem, fi in flag_files.items():
        try:
            df = load_pq(fi['path']); meta = get_meta(stem)
            mask = pd.Series(False, index=df.index)
            for col in df.select_dtypes(include=['object']).columns:
                mask |= df[col].astype(str).str.contains(q, case=False, na=False)
            hits = mask.sum()
            if hits > 0:
                results.append({'stem':stem,'label':meta['label'],'icon':meta['icon'],'badge':meta['badge'],'scope':fi['scope'],'hits':hits,'sample':df[mask].head(10)})
        except Exception: pass
    return results


# ═══════════════ PLOTS ═══════════════
def pl_funnel():
    n_risk = _ds('risk_scoring_unificado')
    n_ge3 = _dynamic_stats().get('risk_scoring_unificado', {}).get('n_ge3', 0)
    stages = [('Contratos PLACSP', PIPELINE['placsp_total']),
              ('Con adjudicatario e importe', PIPELINE['placsp_useful']),
              ('Actos mercantiles BORME', PIPELINE['borme_actos']),
              ('Empresas cruzadas BORME ∩ PLACSP', PIPELINE['matched_nac']),
              ('Con señal de alerta (≥1 flag)', n_risk or 25_675),
              ('Con ≥3 señales acumuladas', n_ge3 or 125)]
    labels = [s[0] for s in stages]; values = [s[1] for s in stages]
    colors = [C['blue'],C['blue'],C['teal'],C['amber'],C['accent'],C['red']]
    fig = go.Figure(go.Bar(y=labels[::-1],x=values[::-1],orientation='h',
        marker=dict(color=colors[::-1],line=dict(width=0),opacity=.85),
        text=[fmt(v) for v in values[::-1]],textposition='auto',textfont=dict(size=11,color='white',family='IBM Plex Mono'),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>'))
    fig.update_layout(**PL,height=320,xaxis=dict(gridcolor=C['grid'],type='log',tickvals=[100,1000,10000,100000,1000000,10000000],
        ticktext=['100','1K','10K','100K','1M','10M']),yaxis=dict(tickfont=dict(size=10,family='DM Sans')),bargap=.25)
    return fig

def pl_coverage():
    pct = PIPELINE['coverage_pct']
    fig = go.Figure(go.Pie(values=[pct, 100-pct],labels=['Cruzadas con BORME','Sin cruzar'],hole=.65,
        textinfo='label+percent',textposition='outside',textfont=dict(size=11,family='DM Sans',color=C['text2']),
        marker=dict(colors=[C['blue'],C['border2']],line=dict(width=2,color=C['bg'])),
        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'))
    fig.update_layout(**PL,height=300,showlegend=False,
        annotations=[dict(text=f'<b>{pct}%</b><br>cruzadas',x=.5,y=.5,showarrow=False,font=dict(size=16,color=C['text'],family='IBM Plex Mono'))])
    return fig

def pl_signal_summary():
    signals = [('F9 · Geo discrepancia','flag9_geo_discrepancia',C['purple']),
        ('F2 · Capital mínimo','flag2_capital_ridiculo',C['amber']),
        ('F1 · Recién creada','flag1_recien_creada',C['red']),
        ('F10 · Fraccionamiento','flag10_troceo_cat',C['red']),
        ('F6 · Red administradores','flag6_admin_network',C['blue']),
        ('F4 · Disolución','flag4_disolucion',C['red']),
        ('F5 · Concursal','flag5_concursal',C['red']),
        ('F7 · Concentración','flag7_concentracion',C['teal']),
        ('F11 · Modificaciones','flag11_modificaciones_cat',C['amber']),
        ('F8 · UTEs vinculadas','flag8_utes_sospechosas',C['amber'])]
    labels=[s[0] for s in signals]; vals=[_ds(s[1]) for s in signals]; cols=[s[2] for s in signals]
    # Sort by value for display
    combined = sorted(zip(labels, vals, cols), key=lambda x: x[1])
    labels = [c[0] for c in combined]; vals = [c[1] for c in combined]; cols = [c[2] for c in combined]
    fig = go.Figure(go.Bar(y=labels[::-1],x=vals[::-1],orientation='h',
        marker=dict(color=cols[::-1],opacity=.85,line=dict(width=0)),
        text=[fmt(v) for v in vals[::-1]],textposition='auto',textfont=dict(size=10,color='white',family='IBM Plex Mono'),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} empresas<extra></extra>'))
    fig.update_layout(**PL,height=380,xaxis=dict(gridcolor=C['grid'],title='Empresas afectadas'),
        yaxis=dict(tickfont=dict(size=10,family='DM Sans')),bargap=.2)
    return fig

# ── Geo map F9 ──
CCAA_COORDS = {'Andalucía':(37.38,-4.77),'Aragón':(41.60,-0.88),'Asturias':(43.36,-5.85),'Canarias':(28.12,-15.43),'Cantabria':(43.18,-3.99),'Castilla y León':(41.65,-4.73),'Castilla-La Mancha':(39.28,-2.88),'Cataluña':(41.82,1.47),'Ceuta':(35.89,-5.32),'Comunidad Valenciana':(39.48,-0.75),'Extremadura':(39.16,-6.17),'Galicia':(42.57,-8.17),'Islas Baleares':(39.57,2.65),'La Rioja':(42.29,-2.52),'Madrid':(40.42,-3.70),'Melilla':(35.29,-2.94),'Murcia':(37.99,-1.13),'Navarra':(42.70,-1.68),'País Vasco':(43.00,-2.62)}

def pl_geo_map(df_geo):
    reg_col = next((c for c in df_geo.columns if 'ccaa_borme' in c.lower() or 'registro' in c.lower()), None)
    con_col = next((c for c in df_geo.columns if 'ccaa_contrato' in c.lower() or 'principal' in c.lower()), None)
    if not reg_col or not con_col: return None
    imp_col = next((c for c in df_geo.columns if 'importe' in c.lower()), None)
    flows = {}
    for _, r in df_geo.iterrows():
        orig, dest = str(r[reg_col]).strip(), str(r[con_col]).strip()
        if orig == dest or orig not in CCAA_COORDS or dest not in CCAA_COORDS: continue
        key = (orig, dest)
        if key not in flows: flows[key] = {'count':0,'importe':0}
        flows[key]['count'] += 1
        if imp_col and pd.notna(r.get(imp_col)): flows[key]['importe'] += float(r[imp_col])
    if not flows: return None
    top_flows = sorted(flows.items(), key=lambda x: -x[1]['count'])[:60]; max_count = max(f[1]['count'] for f in top_flows)
    fig = go.Figure()
    for (orig,dest),info in top_flows:
        lat0,lon0=CCAA_COORDS[orig]; lat1,lon1=CCAA_COORDS[dest]; intensity=info['count']/max_count
        mid_lat=(lat0+lat1)/2+(lon1-lon0)*.08; mid_lon=(lon0+lon1)/2-(lat1-lat0)*.08
        fig.add_trace(go.Scattergeo(lat=[lat0,mid_lat,lat1],lon=[lon0,mid_lon,lon1],mode='lines',
            line=dict(width=1+intensity*5,color=f'rgba(229,162,41,{.15+intensity*.55})'),
            hovertext=f"<b>{orig} → {dest}</b><br>{info['count']} empresas<br>{info['importe']/1e6:.0f}M€",hoverinfo='text',showlegend=False))
    all_ccaa,out_count=set(),{}
    for (o,d),info in top_flows: all_ccaa.update([o,d]); out_count[o]=out_count.get(o,0)+info['count']; out_count[d]=out_count.get(d,0)+info['count']
    for ccaa in all_ccaa:
        if ccaa in CCAA_COORDS:
            lat,lon=CCAA_COORDS[ccaa]; sz=6+(out_count.get(ccaa,0)/max(out_count.values()))*18
            fig.add_trace(go.Scattergeo(lat=[lat],lon=[lon],mode='markers+text',marker=dict(size=sz,color=C['blue'],opacity=.9,line=dict(width=1,color='rgba(255,255,255,.2)')),
                text=[ccaa[:12]],textposition='top center',textfont=dict(size=8,color=C['text2'],family='IBM Plex Mono'),
                hovertext=f"<b>{ccaa}</b><br>{out_count.get(ccaa,0)} flujos",hoverinfo='text',showlegend=False))
    fig.update_geos(scope='europe',center=dict(lat=40.0,lon=-3.5),projection_scale=6.5,showland=True,landcolor='rgba(11,14,21,1)',
        showocean=True,oceancolor='rgba(6,8,13,1)',showcoastlines=True,coastlinecolor='rgba(23,28,40,.6)',
        showcountries=True,countrycolor='rgba(23,28,40,.4)',showlakes=False,showrivers=False,bgcolor='rgba(0,0,0,0)',lonaxis_range=[-10,5],lataxis_range=[27,44])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='IBM Plex Mono',color=C['text'],size=11),
        margin=dict(l=0,r=0,t=40,b=0),height=500,title=dict(text='Registro → Contratos · Grosor ∝ nº empresas',font=dict(size=12),x=.5),
        hoverlabel=dict(bgcolor='rgba(11,14,21,.97)',bordercolor=C['border2'],font=dict(color=C['text'],size=11)))
    return fig

def pl_f7_heatmap(df):
    if 'pct_adj_organo' not in df.columns: return None
    emp_col = 'adj_norm' if 'adj_norm' in df.columns else df.columns[0]
    org_col = 'organo_contratante' if 'organo_contratante' in df.columns else df.columns[1]
    top = df.head(100).copy(); top['emp']=top[emp_col].astype(str).str[:30]; top['org']=top[org_col].astype(str).str[:35]
    top_emps = top.groupby('emp')['pct_adj_organo'].max().nlargest(15).index.tolist()
    sub = top[top['emp'].isin(top_emps)]
    if len(sub) < 3: return None
    piv = sub.pivot_table(index='emp',columns='org',values='pct_adj_organo',aggfunc='max').fillna(0)
    fig = go.Figure(go.Heatmap(z=piv.values,x=[str(c)[:30] for c in piv.columns],y=piv.index.tolist(),
        colorscale=[[0,'rgba(6,8,13,1)'],[.3,'rgba(58,123,213,.35)'],[.6,'rgba(229,162,41,.55)'],[1,'rgba(220,68,68,.85)']],
        hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.0%}<extra></extra>',colorbar=dict(title='%Adj',thickness=10,len=.5,tickfont=dict(size=9,color=C['muted']))))
    fig.update_layout(**PL,height=max(350,len(top_emps)*28+80),title=dict(text='Concentración empresa × órgano',font=dict(size=12),x=0),
        xaxis=dict(tickfont=dict(size=8),tickangle=-45),yaxis=dict(tickfont=dict(size=9)))
    return fig


# ═══════════════ TAB 1: RESUMEN ═══════════════
def render_resumen(flag_files):
    st.markdown(f"""<div class="card card-l card-accent">
        <b>¿Qué es esto?</b><br><br>
        Cruzamos los datos del <b>Registro Mercantil</b> (quién dirige cada empresa, cuándo se constituyó,
        si está disuelta o en concurso) con la <b>contratación pública española</b> (quién gana contratos
        del Estado) para detectar situaciones que merecen revisión. Ningún patrón es prueba de irregularidad —
        son señales estadísticas para priorizar la supervisión humana.
    </div>""", unsafe_allow_html=True)

    # ── DATASETS ──
    st.markdown('<div class="sec">Los datos · 4 fuentes públicas</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        Todo parte de datos abiertos publicados por organismos oficiales. No accedemos a nada privado.
        Cada fuente tiene sus fortalezas y limitaciones.
    </div>""", unsafe_allow_html=True)

    # Load quality stats if available
    q_stats = {}
    if Q_DIR.exists():
        for qf in Q_DIR.glob('*.json'):
            try: q_stats[qf.stem] = load_json(str(qf))
            except Exception: pass

    ds_col1, ds_col2 = st.columns(2)
    with ds_col1:
        st.markdown(f"""<div class="ds-card ds-blue">
            <span class="ds-icon">🏛️</span>
            <div class="ds-name">PLACSP</div>
            <span class="ds-full">Plataforma de Contratación del Sector Público</span>
            <div class="ds-desc">
                Base de datos oficial de contratación pública. Contiene <b>todas las licitaciones
                y adjudicaciones</b> publicadas por administraciones del Estado, CCAA, diputaciones,
                ayuntamientos y entidades públicas.
            </div>
            <div class="ds-metrics">
                <span class="ds-metric"><b>{fmt(PIPELINE['placsp_total'])}</b> registros</span>
                <span class="ds-metric"><b>{fmt(PIPELINE['placsp_useful'])}</b> con adj. e importe</span>
                <span class="ds-metric"><b>2012–2026</b></span>
            </div>
            <div class="ds-quality">
                <b>Calidad:</b>
                <span class="q-good">✓</span> Obligatoria por ley ·
                <span class="q-warn">△</span> 33% sin importe/adj. ·
                <span class="q-bad">✗</span> Sin NIF/CIF abierto
            </div>
        </div>""", unsafe_allow_html=True)

    with ds_col2:
        st.markdown(f"""<div class="ds-card ds-teal">
            <span class="ds-icon">📜</span>
            <div class="ds-name">BORME</div>
            <span class="ds-full">Boletín Oficial del Registro Mercantil</span>
            <div class="ds-desc">
                Publicación diaria con <b>todos los actos inscritos</b> en los Registros
                Mercantiles provinciales. Un PDF por provincia y día.
                Nuestro parser extrae empresa, acto, persona, cargo, capital y fecha.
            </div>
            <div class="ds-metrics">
                <span class="ds-metric"><b>{fmt(PIPELINE['borme_actos'])}</b> actos</span>
                <span class="ds-metric"><b>{fmt(PIPELINE['borme_empresas'])}</b> empresas</span>
                <span class="ds-metric"><b>{fmt(PIPELINE['borme_personas'])}</b> personas</span>
                <span class="ds-metric"><b>{fmt(PIPELINE['borme_pdfs'])}</b> PDFs</span>
            </div>
            <div class="ds-quality">
                <b>Calidad:</b>
                <span class="q-good">✓</span> Inscripción obligatoria ·
                <span class="q-warn">△</span> Parsing regex (validado) ·
                <span class="q-bad">✗</span> Sin NIF — cruce por nombre
            </div>
        </div>""", unsafe_allow_html=True)

    ds_col3, ds_col4 = st.columns(2)
    with ds_col3:
        st.markdown(f"""<div class="ds-card ds-amber">
            <span class="ds-icon">🏗️</span>
            <div class="ds-name">Registre Públic</div>
            <span class="ds-full">Generalitat de Catalunya · PSCP</span>
            <div class="ds-desc">
                Contratación catalana con <b>datos más ricos</b> que PLACSP: columnas nativas
                de modificaciones contractuales que permiten detectar F11.
            </div>
            <div class="ds-metrics">
                <span class="ds-metric"><b>{fmt(PIPELINE['cat_total'])}</b> registros</span>
                <span class="ds-metric"><b>2014–2026</b></span>
                <span class="ds-metric">Modificaciones nativas</span>
            </div>
            <div class="ds-quality">
                <b>Calidad:</b>
                <span class="q-good">✓</span> Modificaciones únicas ·
                <span class="q-warn">△</span> Solapamiento parcial con PLACSP
            </div>
        </div>""", unsafe_allow_html=True)

    with ds_col4:
        st.markdown(f"""<div class="ds-card ds-purple">
            <span class="ds-icon">📋</span>
            <div class="ds-name">Menores BCN</div>
            <span class="ds-full">Portal de Transparència · Ajuntament de Barcelona</span>
            <div class="ds-desc">
                <b>Contratos menores</b> (≤15K€) del Ayuntamiento de Barcelona.
                No aparecen en PLACSP. Pieza clave para detectar <b>fraccionamiento</b> (F10).
            </div>
            <div class="ds-metrics">
                <span class="ds-metric"><b>{fmt(PIPELINE['cat_menores'])}</b> registros</span>
                <span class="ds-metric"><b>Solo BCN</b></span>
                <span class="ds-metric">Contratos ≤15K€</span>
            </div>
            <div class="ds-quality">
                <b>Calidad:</b>
                <span class="q-good">✓</span> Granular ·
                <span class="q-warn">△</span> Solo Barcelona ·
                <span class="q-bad">✗</span> Sin equivalente nacional
            </div>
        </div>""", unsafe_allow_html=True)

    # Show quality JSON stats if they exist
    if q_stats:
        with st.expander("📊 Radiografía de calidad de los datos"):
            for name, data in q_stats.items():
                st.markdown(f'<div class="sec">{name.replace("_", " ").upper()}</div>', unsafe_allow_html=True)
                if not isinstance(data, dict):
                    continue

                # ── Completeness: bar chart ──
                completeness = data.get('completeness', {})
                if not completeness:
                    # Try top-level simple numeric values as completeness
                    completeness = {k: v for k, v in data.items()
                                    if isinstance(v, (int, float)) and 0 < v <= 100}
                if completeness:
                    cols_sorted = sorted(completeness.items(), key=lambda x: -x[1])
                    labels = [c[0].replace('_', ' ') for c in cols_sorted]
                    vals = [c[1] for c in cols_sorted]
                    bar_colors = [C['teal'] if v >= 90 else C['amber'] if v >= 60 else C['red'] for v in vals]
                    fig = go.Figure(go.Bar(
                        y=labels[::-1], x=vals[::-1], orientation='h',
                        marker=dict(color=bar_colors[::-1], opacity=.85, line=dict(width=0)),
                        text=[f"{v:.1f}%" for v in vals[::-1]], textposition='auto',
                        textfont=dict(size=9, color='white', family='IBM Plex Mono'),
                        hovertemplate='<b>%{y}</b><br>%{x:.1f}%<extra></extra>'))
                    fig.update_layout(**PL, height=max(200, len(labels)*24+60),
                        title=dict(text='Completitud por columna (%)', font=dict(size=11)),
                        xaxis=dict(range=[0, 105], gridcolor=C['grid'], dtick=25),
                        yaxis=dict(tickfont=dict(size=9, family='IBM Plex Mono')), bargap=.2)
                    st.plotly_chart(fig, use_container_width=True)

                # ── Coverage: horizontal metrics ──
                coverage = data.get('coverage', {})
                if coverage and isinstance(coverage, dict):
                    st.markdown(f"<div style='font-family:IBM Plex Mono;font-size:.6rem;color:{C['muted']};"
                        "letter-spacing:.1em;text-transform:uppercase;margin:12px 0 6px'>Cobertura de campos clave</div>",
                        unsafe_allow_html=True)
                    cov_cols = st.columns(min(len(coverage), 5))
                    for i, (k, v) in enumerate(coverage.items()):
                        with cov_cols[i % len(cov_cols)]:
                            color = C['teal'] if v >= 90 else C['amber'] if v >= 60 else C['red']
                            st.markdown(f"""<div style="background:{C['card']};border:1px solid {C['border']};
                                border-radius:10px;padding:12px 14px;text-align:center">
                                <div style="font-family:IBM Plex Mono;font-size:1.1rem;font-weight:700;color:{color}">
                                    {v:.1f}%</div>
                                <div style="font-family:IBM Plex Mono;font-size:.58rem;color:{C['muted']};
                                    letter-spacing:.06em;margin-top:2px">{k.replace('_', ' ')}</div>
                            </div>""", unsafe_allow_html=True)

                # ── Top adjudicatarios ──
                top_adj = data.get('top_adjudicatarios', data.get('top_adj', {}))
                if top_adj and isinstance(top_adj, dict):
                    names = top_adj.get('names', top_adj.get('name', []))
                    amounts = top_adj.get('importes', top_adj.get('importe', []))
                    if names and isinstance(names, list):
                        st.markdown(f"<div style='font-family:IBM Plex Mono;font-size:.6rem;color:{C['muted']};"
                            "letter-spacing:.1em;text-transform:uppercase;margin:16px 0 8px'>Top adjudicatarios por importe</div>",
                            unsafe_allow_html=True)
                        top_n = min(10, len(names))
                        rows = []
                        for j in range(top_n):
                            nm = str(names[j])[:50] if j < len(names) else '—'
                            amt = amounts[j] if isinstance(amounts, list) and j < len(amounts) else 0
                            amt_str = f"{amt/1e6:,.1f}M€" if isinstance(amt, (int,float)) and amt > 1e6 else f"{amt:,.0f}€" if isinstance(amt, (int,float)) else str(amt)
                            rows.append({'#': j+1, 'Adjudicatario': nm, 'Importe total': amt_str})
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(400, top_n*40+40))

                # ── Top órganos ──
                top_org = data.get('top_organos', data.get('top_org', {}))
                if top_org and isinstance(top_org, dict):
                    names = top_org.get('names', top_org.get('name', []))
                    amounts = top_org.get('importes', top_org.get('importe', []))
                    if names and isinstance(names, list):
                        st.markdown(f"<div style='font-family:IBM Plex Mono;font-size:.6rem;color:{C['muted']};"
                            "letter-spacing:.1em;text-transform:uppercase;margin:16px 0 8px'>Top órganos contratantes</div>",
                            unsafe_allow_html=True)
                        top_n = min(10, len(names))
                        rows = []
                        for j in range(top_n):
                            nm = str(names[j])[:60] if j < len(names) else '—'
                            amt = amounts[j] if isinstance(amounts, list) and j < len(amounts) else 0
                            amt_str = f"{amt/1e6:,.1f}M€" if isinstance(amt, (int,float)) and amt > 1e6 else f"{amt:,.0f}€" if isinstance(amt, (int,float)) else str(amt)
                            rows.append({'#': j+1, 'Órgano': nm, 'Importe total': amt_str})
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(400, top_n*40+40))

                # ── Categories: compact pills ──
                categories = data.get('categories', {})
                if categories and isinstance(categories, dict):
                    for cat_name, cat_data in categories.items():
                        if isinstance(cat_data, dict) and 'counts' in cat_data:
                            counts = cat_data['counts']
                            if isinstance(counts, list) and len(counts) > 0:
                                labels_cat = cat_data.get('labels', cat_data.get('values',
                                    [f"Cat {i+1}" for i in range(len(counts))]))
                                if isinstance(labels_cat, list):
                                    top_n = min(8, len(counts))
                                    fig = go.Figure(go.Bar(
                                        y=[str(l)[:30] for l in labels_cat[:top_n]][::-1],
                                        x=counts[:top_n][::-1], orientation='h',
                                        marker=dict(color=C['blue'], opacity=.8),
                                        text=[fmt(c) for c in counts[:top_n]][::-1], textposition='auto',
                                        textfont=dict(size=9, color='white', family='IBM Plex Mono')))
                                    fig.update_layout(**PL, height=max(180, top_n*28+60),
                                        title=dict(text=cat_name.replace('_', ' ').title(), font=dict(size=11)),
                                        xaxis=dict(gridcolor=C['grid']),
                                        yaxis=dict(tickfont=dict(size=9)), bargap=.2)
                                    st.plotly_chart(fig, use_container_width=True)

                # ── CPV top ──
                cpv = data.get('cpv_top', data.get('cpv', {}))
                if cpv and isinstance(cpv, dict):
                    codes = cpv.get('codes', [])
                    labels_cpv = cpv.get('labels', [])
                    if codes and labels_cpv and isinstance(codes, list) and isinstance(labels_cpv, list):
                        st.markdown(f"<div style='font-family:IBM Plex Mono;font-size:.6rem;color:{C['muted']};"
                            "letter-spacing:.1em;text-transform:uppercase;margin:16px 0 8px'>CPV más frecuentes</div>",
                            unsafe_allow_html=True)
                        cpv_items = []
                        for j in range(min(10, len(codes))):
                            code = str(codes[j]) if j < len(codes) else ''
                            label = str(labels_cpv[j])[:50] if j < len(labels_cpv) else ''
                            cpv_items.append({'CPV': code, 'Descripción': label})
                        st.dataframe(pd.DataFrame(cpv_items), use_container_width=True, hide_index=True)

                # ── Amounts distribution ──
                amounts_data = data.get('amounts', {})
                if amounts_data and isinstance(amounts_data, dict):
                    for amt_name, amt_info in amounts_data.items():
                        if isinstance(amt_info, dict) and 'brackets' in amt_info:
                            brackets = amt_info.get('brackets', {})
                            counts = brackets.get('counts', [])
                            labels_b = brackets.get('labels',
                                [f"Tramo {i+1}" for i in range(len(counts))])
                            if counts and isinstance(counts, list) and isinstance(labels_b, list):
                                top_n = min(len(counts), len(labels_b))
                                fig = go.Figure(go.Bar(
                                    x=[str(l)[:20] for l in labels_b[:top_n]],
                                    y=counts[:top_n],
                                    marker=dict(color=C['amber'], opacity=.8),
                                    hovertemplate='<b>%{x}</b><br>%{y:,.0f}<extra></extra>'))
                                fig.update_layout(**PL, height=260,
                                    title=dict(text=amt_name.replace('_', ' ').title(), font=dict(size=11)),
                                    xaxis=dict(tickangle=-45, tickfont=dict(size=8), gridcolor=C['grid']),
                                    yaxis=dict(title='Registros', gridcolor=C['grid']), bargap=.15)
                                st.plotly_chart(fig, use_container_width=True)

                # ── Fallback: any remaining simple key-value pairs not yet shown ──
                shown_keys = {'completeness','coverage','top_adjudicatarios','top_adj',
                    'top_organos','top_org','categories','cpv_top','cpv','amounts',
                    'temporal','comparador'}
                remaining = {k: v for k, v in data.items()
                             if k not in shown_keys and isinstance(v, (int, float, str))}
                if remaining:
                    rem_cols = st.columns(min(len(remaining), 4))
                    for i, (k, v) in enumerate(remaining.items()):
                        with rem_cols[i % len(rem_cols)]:
                            display_v = f"{v:,.0f}" if isinstance(v, (int, float)) and abs(v) > 100 else str(v)
                            st.metric(k.replace('_', ' ').title(), display_v)

                st.markdown(f'<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""<div style="font-size:.78rem;color:{C['muted']};line-height:1.6;margin:8px 0 4px">
        <b style="color:{C['text2']}">Nota sobre el cruce:</b>
        BORME no incluye NIF/CIF. El cruce con PLACSP se hace por <b>nombre de empresa normalizado</b>.
        Esto implica posibles <b>falsos positivos</b> (homónimos) y <b>falsos negativos</b> (variantes de nombre
        no capturadas). Las {PIPELINE['stop_words']:,} stop words y {PIPELINE['manual_rules']} reglas curadas manualmente mitigan el problema, pero no lo eliminan.
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">De dónde partimos · El embudo de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.6;margin-bottom:12px">
        De <b style="color:{C['text']}">{fmt(PIPELINE['placsp_total'])}</b> de contratos en PLACSP,
        filtramos los que tienen adjudicatario e importe, cruzamos con <b style="color:{C['text']}">{fmt(PIPELINE['borme_actos'])}</b>
        de actos del Registro Mercantil, y aplicamos 11 filtros de detección.</div>""", unsafe_allow_html=True)
    st.plotly_chart(pl_funnel(), use_container_width=True)

    st.markdown('<div class="sec">Cobertura del cruce · Honestidad metodológica</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.5])
    with col_a: st.plotly_chart(pl_coverage(), use_container_width=True)
    with col_b:
        st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.7;padding:10px 0">
            <b style="color:{C['text']}">No vemos todo.</b> Solo el <b style="color:{C['blue']}">{PIPELINE['coverage_pct']}%</b>
            de adjudicatarios se cruzan con BORME.<br><br>
            El <b>{100 - PIPELINE['coverage_pct']}% restante</b> incluye:<br>
            · <b>Autónomos y personas físicas</b> — no figuran en el Registro Mercantil<br>
            · <b>Empresas extranjeras</b> — registradas fuera de España<br>
            · <b>Variantes de nombre no capturadas</b> — cruce por nombre, no por NIF<br><br>
            Nuestras señales son un <b>límite inferior</b>: hay patrones que no podemos ver.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Las 11 señales · Cuántas empresas afecta cada una</div>', unsafe_allow_html=True)
    st.plotly_chart(pl_signal_summary(), use_container_width=True)

    SIGNAL_ORDER = [('flag6_admin_network','La señal principal'),('flag7_concentracion',None),('flag1_recien_creada',None),
        ('flag2_capital_ridiculo',None),('flag4_disolucion',None),('flag5_concursal',None),
        ('flag8_utes_sospechosas',None),('flag9_geo_discrepancia',None),('flag10_troceo_cat','Solo Catalunya'),('flag11_modificaciones_cat','Solo Catalunya')]
    for stem, subtitle in SIGNAL_ORDER:
        m = FLAGS.get(stem, {}); 
        if not m: continue
        sub_html = f" <span style='font-size:.68rem;color:{C['muted']}'>{subtitle}</span>" if subtitle else ""
        stats_html = ""
        if m.get('stat_empresas'): stats_html += f'<span class="signal-stat"><b>{fmt(m["stat_empresas"])}</b> empresas</span>'
        if m.get('stat_extra'): stats_html += f'<span class="signal-stat">{m["stat_extra"]}</span>'
        example_html = f"""<div class="example-box"><span class="ex-label">Ejemplo ilustrativo</span>{m['example']}</div>""" if m.get('example') else ""
        st.markdown(f"""<div class="signal-card">
            <div class="signal-title"><span class="badge {m['badge']}">{m['short']}</span> {m['icon']} {m['label']}{sub_html}</div>
            <div class="signal-body">{m['what']}</div>
            <div class="signal-stats">{stats_html}</div>{example_html}</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Buscar empresa o persona</div>', unsafe_allow_html=True)
    q = st.text_input("🔍", key="search_main", placeholder="Ej: IBERDROLA, MARTI SOLER, AENA...", label_visibility="collapsed")
    if q and len(q) >= 3:
        with st.spinner("Buscando..."): results = search_all(q, flag_files)
        if results:
            st.markdown(f"**{len(results)}** análisis con resultados para **{q}**")
            for r in results:
                with st.expander(f"{r['icon']} {r['label']} — {r['scope']} · {r['hits']} coincidencias"):
                    st.dataframe(_rename_columns(clean_df(r['sample'])), use_container_width=True, hide_index=True)
        else: st.info(f"«{q}» no encontrado.")

    st.markdown(f"""<div class="warn-box"><b>⚠️ Importante:</b> Un patrón detectado NO es prueba de irregularidad.
        Son señales estadísticas de datos públicos (PLACSP, Registre Públic, Portal Transparència BCN, BORME).
        Requieren revisión humana cualificada.</div>""", unsafe_allow_html=True)


# ═══════════════ TAB 2: EXPLORAR ═══════════════
def render_explorar(flag_files):
    if not flag_files: st.warning("No se encontraron análisis."); return
    stems = list(flag_files.keys())
    display_names = [f"{get_meta(s)['icon']} {get_meta(s)['label']} ({flag_files[s]['scope']})" for s in stems]
    idx = st.selectbox("Seleccionar señal", range(len(stems)), format_func=lambda i: display_names[i])
    sel = stems[idx]; meta = get_meta(sel); info = flag_files[sel]

    parts = []
    if meta['what']: parts.append(f"<b>Qué detecta:</b> {meta['what']}")
    if meta['why']: parts.append(f"<b>Por qué importa:</b> {meta['why']}")
    if meta['how']: parts.append(f"<b>Cómo se calcula:</b> {meta['how']}")
    if parts:
        st.markdown(f"""<div class="card card-l card-accent"><span class="badge {meta['badge']}">{meta['short']}</span>
            <b>{meta['icon']} {meta['label']}</b><br><br>{'<br>'.join(parts)}</div>""", unsafe_allow_html=True)
    if meta.get('example'):
        st.markdown(f"""<div class="example-box" style="margin-top:0"><span class="ex-label">Ejemplo</span>{meta['example']}</div>""", unsafe_allow_html=True)

    with st.spinner("Cargando..."): df = load_pq(info['path'])
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Registros", f"{len(df):,}")
    with c2: st.metric("Columnas", len(df.columns))
    with c3: st.metric("Ámbito", info['scope'])

    if 'flag7' in sel:
        fig = pl_f7_heatmap(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
    if 'flag9' in sel or 'geo_dis' in sel:
        fig = pl_geo_map(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
    if 'flag10' in sel and 'n_contratos_cluster' in df.columns:
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Histogram(x=df['n_contratos_cluster'],nbinsx=30,marker=dict(color=C['accent'],opacity=.85)))
            fig.update_layout(**PL,height=280,title=dict(text='Contratos por cluster',font=dict(size=12)),xaxis=dict(title='Nº contratos',gridcolor=C['grid']),yaxis=dict(title='Freq',gridcolor=C['grid']),bargap=.03)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'ratio_sobre_umbral' in df.columns:
                fig = go.Figure(go.Histogram(x=df['ratio_sobre_umbral'],nbinsx=30,marker=dict(color=C['amber'],opacity=.85)))
                fig.update_layout(**PL,height=280,title=dict(text='Ratio suma/umbral',font=dict(size=12)),xaxis=dict(title='Ratio',gridcolor=C['grid']),yaxis=dict(title='Freq',gridcolor=C['grid']),bargap=.03)
                st.plotly_chart(fig, use_container_width=True)
    if 'flag11' in sel and 'pct_modificados' in df.columns:
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Histogram(x=df['pct_modificados']*100,nbinsx=30,marker=dict(color=C['purple'],opacity=.85)))
            fig.update_layout(**PL,height=280,title=dict(text='% contratos modificados',font=dict(size=12)),xaxis=dict(title='%',gridcolor=C['grid']),yaxis=dict(title='Freq',gridcolor=C['grid']),bargap=.03)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'n_modificaciones' in df.columns:
                fig = go.Figure(go.Histogram(x=df['n_modificaciones'],nbinsx=30,marker=dict(color=C['blue'],opacity=.85)))
                fig.update_layout(**PL,height=280,title=dict(text='Nº modificaciones',font=dict(size=12)),xaxis=dict(title='Mod.',gridcolor=C['grid']),yaxis=dict(title='Freq',gridcolor=C['grid']),bargap=.03)
                st.plotly_chart(fig, use_container_width=True)
    if 'risk_scoring' in sel:
        bool_cols = [c for c in df.columns if df[c].dtype == bool]
        if bool_cols:
            flag_sums = {}
            for c in bool_cols:
                if df[c].sum() > 0:
                    lbl = COL_RENAME.get(c, _flag_label(c))
                    flag_sums[lbl] = int(df[c].sum())
            if flag_sums:
                fs_df = pd.DataFrame({'Señal':list(flag_sums.keys()),'Empresas':list(flag_sums.values())}).sort_values('Empresas',ascending=True)
                fig = go.Figure(go.Bar(y=fs_df['Señal'],x=fs_df['Empresas'],orientation='h',marker=dict(color=C['blue'],opacity=.85),hovertemplate='<b>%{y}</b><br>%{x:,}<extra></extra>'))
                fig.update_layout(**PL,height=max(220,len(fs_df)*30),title=dict(text='Empresas por señal',font=dict(size=12)),xaxis=dict(gridcolor=C['grid']),yaxis=dict(tickfont=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True)
        nf_col = next((c for c in df.columns if 'n_flags' in c.lower()), None)
        if nf_col:
            dist = df[nf_col].value_counts().sort_index()
            fig = go.Figure(go.Bar(x=[f"{int(k)} señal{'es' if k>1 else ''}" for k in dist.index],y=dist.values,
                marker=dict(color=[C['blue'] if k<=1 else C['amber'] if k<=2 else C['red'] for k in dist.index],opacity=.85),
                hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'))
            fig.update_layout(**PL,height=280,title=dict(text='Señales acumuladas por empresa',font=dict(size=12)),
                xaxis=dict(gridcolor=C['grid']),yaxis=dict(title='Empresas',gridcolor=C['grid']),bargap=.15)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec">Explorar datos</div>', unsafe_allow_html=True)
    df_display = _rename_columns(clean_df(df))
    df_display = _format_pct_col(df_display)

    # Dedup option
    n_total = len(df_display)
    n_dedup = len(df_display.drop_duplicates())
    has_dupes = n_dedup < n_total
    if has_dupes:
        dedup = st.checkbox(f"Eliminar filas duplicadas ({n_total:,} → {n_dedup:,})", value=True, key="exp_dedup")
        if dedup:
            df_display = df_display.drop_duplicates()

    fc1,fc2 = st.columns([1,2])
    with fc1: search_col = st.selectbox("Buscar en", ['(todas las columnas)'] + list(df_display.columns), key="exp_col")
    _placeholders = {'Empresa':'Ej: IBERDROLA, ACCIONA...','Adjudicatario':'Ej: IBERDROLA ENERGIA SA',
        'Persona':'Ej: GARCIA LOPEZ','Órgano contratante':'Ej: Ayuntamiento de Madrid',
        'Objeto del contrato':'Ej: limpieza, consultoría...','CCAA registro':'Ej: Andalucía',
        'Nombre UTE':'Ej: UTE AUTOPISTA','Miembro 1':'Ej: CONSTRUCCIONES GARCIA',
        '(todas las columnas)':'Busca en cualquier columna — ej: ACCIONA, Madrid...'}
    ph = _placeholders.get(search_col, f"Filtrar por {search_col}...")
    with fc2: search_term = st.text_input("Filtrar", key="exp_term", placeholder=ph)
    filtered = df_display.copy()
    if search_term:
        if search_col != '(todas las columnas)': filtered = filtered[filtered[search_col].astype(str).str.contains(search_term, case=False, na=False)]
        else:
            mask = pd.Series(False, index=filtered.index)
            for col in filtered.select_dtypes(include=['object']).columns: mask |= filtered[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered = filtered[mask]
        st.caption(f"🔍 {len(filtered):,} de {len(df_display):,}")
    sortable = [c for c in filtered.columns if filtered[c].dtype in ['int64','float64','int32','float32','Int64','Float64']]
    if sortable:
        sort_col = st.selectbox("Ordenar por", ['(sin ordenar)'] + sortable, key="exp_sort")
        if sort_col != '(sin ordenar)': filtered = filtered.sort_values(sort_col, ascending=False)
    # Format importe after sort
    filtered = _format_importe_col(filtered)
    st.dataframe(filtered.head(1000), use_container_width=True, height=500, hide_index=True)

    with st.expander("🔎 Buscar en TODAS las señales"):
        xq = st.text_input("Nombre", key="xsearch")
        if xq and len(xq) >= 3:
            xr = []
            for s,fi in flag_files.items():
                try:
                    dt = load_pq(fi['path'])
                    for col in dt.select_dtypes(include=['object']).columns:
                        n = dt[col].astype(str).str.contains(xq,case=False,na=False).sum()
                        if n>0: m=get_meta(s); xr.append({'Señal':f"{m['icon']} {m['label']}",'Ámbito':fi['scope'],'Coincidencias':n}); break
                except: pass
            if xr: st.dataframe(pd.DataFrame(xr), use_container_width=True, hide_index=True)
            else: st.info(f"«{xq}» no aparece.")


# ═══════════════ TAB 3: METODOLOGÍA ═══════════════
def render_metodo():
    st.markdown(f"""<div class="warn-box"><b>Nota:</b> Este análisis usa filtros deterministas sobre datos públicos — no hay modelos de ML ni puntuaciones.
        Un patrón detectado indica una situación que merece revisión humana, <b>no constituye prueba de irregularidad</b>.</div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Obtener los datos</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        Todo parte de cuatro fuentes públicas. No accedemos a datos privados ni protegidos.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">1</div><div class="step-body"><div class="step-title">Descargar y parsear el BORME (2009–2026)</div>
        El Boletín Oficial del Registro Mercantil publica un PDF diario por provincia con todos los actos
        inscritos: constituciones, nombramientos, ceses, disoluciones, concursos, etc.
        Descargamos los <b>~{PIPELINE['borme_pdfs']:,} PDFs</b> (~25 GB) y los procesamos con un parser de expresiones regulares
        que extrae empresa, acto, persona, cargo, capital y fecha. Validado contra 300 documentos.<br>
        <span class="step-stat">{fmt(PIPELINE['borme_actos'])} actos extraídos</span> <span class="step-stat">{fmt(PIPELINE['borme_empresas'])} empresas</span> <span class="step-stat">{fmt(PIPELINE['borme_personas'])} personas</span></div></div>

    <div class="step"><div class="step-n">2</div><div class="step-body"><div class="step-title">Cargar la contratación pública</div>
        <b>Nacional (PLACSP):</b> {fmt(PIPELINE['placsp_total'])} registros de la Plataforma de Contratación del Sector Público.
        Tras filtrar los que tienen adjudicatario e importe, quedan <b>{fmt(PIPELINE['placsp_useful'])} adjudicaciones útiles</b>.<br>
        <b>Catalunya:</b> {fmt(PIPELINE['cat_total'])} del Registre Públic de Contractes + {fmt(PIPELINE['cat_menores'])} contratos menores del Ayuntamiento de Barcelona.<br>
        <span class="step-stat">{fmt(PIPELINE['placsp_useful'])} nacionales</span> <span class="step-stat">{fmt(PIPELINE['cat_total'])} Catalunya</span> <span class="step-stat">{fmt(PIPELINE['cat_menores'])} menores BCN</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Cruzar BORME con contratación</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        El BORME no publica NIF/CIF en abierto. El cruce se hace por <b>nombre de empresa normalizado</b>,
        lo que implica posibles falsos positivos (homónimos) y falsos negativos (variantes no capturadas).
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">3</div><div class="step-body"><div class="step-title">Normalizar nombres de empresa</div>
        Cada nombre pasa por un pipeline: mayúsculas → eliminar acentos (preservar Ñ) →
        colapsar formas societarias (SL, SA, SLU…) → limpiar puntuación.<br><br>
        <code>"Construcciones García López, S.L.U. (R.M. Madrid)"</code> → <code>"CONSTRUCCIONES GARCIA LOPEZ"</code><br>
        <span class="step-stat">~{PIPELINE['stop_words']:,} stop words</span> <span class="step-stat">{PIPELINE['manual_rules']} reglas manuales</span> <span class="step-stat">{fmt(PIPELINE['auto_rules'])} auto-generadas</span></div></div>

    <div class="step"><div class="step-n">4</div><div class="step-body"><div class="step-title">Intersección BORME ∩ Contratación</div>
        Buscamos qué empresas aparecen en ambos datasets (mismo nombre normalizado).
        Esto nos da el universo sobre el que podemos aplicar señales.<br>
        <span class="step-stat">{PIPELINE['matched_nac']:,} empresas cruzadas (Nacional)</span> <span class="step-stat">{PIPELINE['matched_cat']:,} (Catalunya)</span>
        <span class="step-stat">{PIPELINE['coverage_pct']}% de adjudicatarios PLACSP</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Señales sobre la empresa (F1, F2, F4, F5)</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        Las primeras señales cruzan datos del BORME sobre la propia empresa con sus adjudicaciones.
        No hay F3 — se descartó durante el desarrollo por tener demasiados falsos positivos.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">5</div><div class="step-body"><div class="step-title">F1 · Empresa recién creada</div>
        Si una empresa se constituyó <b>menos de 180 días</b> antes de su primera adjudicación,
        puede indicar una sociedad instrumental creada para un contrato concreto.
        Se usa la fecha de constitución publicada en BORME.<br>
        <span class="step-stat">{_ds_fmt('flag1_recien_creada')} empresas</span></div></div>

    <div class="step"><div class="step-n">6</div><div class="step-body"><div class="step-title">F2 · Capital social mínimo</div>
        Capital social inscrito <b>menor de 10.000€</b> y al menos una adjudicación <b>superior a 100.000€</b>.
        Un capital tan bajo es inusual para empresas con contratos de esa magnitud.<br>
        <span class="step-stat">{_ds_fmt('flag2_capital_ridiculo')} empresas</span></div></div>

    <div class="step"><div class="step-n">7</div><div class="step-body"><div class="step-title">F4 · Empresa disuelta</div>
        Acto de disolución o extinción en BORME con adjudicaciones en los <b>365 días posteriores</b>.
        Una empresa en proceso de cierre no debería estar participando activamente en licitaciones.<br>
        <span class="step-stat">{_ds_fmt('flag4_disolucion')} empresas</span></div></div>

    <div class="step"><div class="step-n">8</div><div class="step-body"><div class="step-title">F5 · Situación concursal</div>
        La empresa tiene un acto concursal publicado en BORME y sigue recibiendo adjudicaciones
        posteriores. La legislación restringe la contratación pública a empresas en insolvencia.<br>
        <span class="step-stat">{_ds_fmt('flag5_concursal')} empresas</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Redes de administradores (F6)</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        La señal más compleja. Buscamos personas que dirigen dos empresas distintas que ganan
        contratos ante los mismos organismos públicos — y que no pertenecen al mismo grupo corporativo.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">9</div><div class="step-body"><div class="step-title">Determinar cargos vigentes</div>
        Partimos de {fmt(PIPELINE['borme_actos'])} de actos del BORME. Para cada combinación (persona, empresa, cargo),
        tomamos el <b>último acto publicado</b>: si es un nombramiento, el cargo está vigente;
        si es un cese, está inactivo. Filtramos solo cargos de decisión (administradores, consejeros delegados,
        apoderados generales…) y excluimos personas jurídicas.<br>
        <span class="step-stat">{fmt(PIPELINE['f6_cargos_total'])} cargos → {fmt(PIPELINE['f6_cargos_decision'])} de decisión → {fmt(PIPELINE['f6_cargos_activos'])} activos</span></div></div>

    <div class="step"><div class="step-n">10</div><div class="step-body"><div class="step-title">Buscar pares de empresas sospechosos</div>
        Identificamos personas que dirigen entre 2 y 50 empresas adjudicatarias. Para cada par
        de empresas que comparten una persona, contamos en cuántos <b>órganos contratantes coinciden</b>.
        Solo retenemos pares con <b>≥2 órganos comunes</b>.<br>
        <span class="step-stat">{PIPELINE['f6_personas_multi']:,} personas con ≥2 empresas</span> <span class="step-stat">{PIPELINE['f6_pares_iniciales']:,} pares iniciales</span></div></div>

    <div class="step"><div class="step-n">11</div><div class="step-body"><div class="step-title">Filtrar grupos corporativos legítimos</div>
        Muchos pares son empresas del mismo grupo (filiales, marcas). Los descartamos con tres filtros:<br>
        <b>a)</b> <b>Nombre de marca:</b> similitud Jaccard ≥0.5 entre nombres normalizados → mismo grupo.<br>
        <b>b)</b> <b>Consejo compartido:</b> >40% de overlap en el consejo + ≥3 consejeros → grupo.<br>
        <b>c)</b> <b>Fusiones BORME:</b> actos de fusión/absorción/escisión entre las dos empresas → grupo.<br>
        <span class="step-stat">{PIPELINE['f6_pares_iniciales']:,} → {_ds_fmt('flag6_pares_unicos', 'n_rows')} pares sospechosos</span> <span class="step-stat">{_ds_fmt('grupos_corporativos', 'n_rows')} descartados como grupo</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Señales adicionales (F7 – F9)</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        Estas señales no dependen de redes de personas. Analizan patrones en las propias adjudicaciones.
        F7 y F8 se calculan tanto para Nacional como para Catalunya. F9 solo para Nacional.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">12</div><div class="step-body"><div class="step-title">F7 · Concentración en un órgano</div>
        Una empresa gana <b>más del 40%</b> de las adjudicaciones de un organismo concreto
        (mínimo 5 propias y 10 totales del órgano). En Catalunya el umbral es adaptativo: 20% si ≥200 adj, 30% si ≥50, 40% si <50.<br>
        <span style="color:{C['muted']};font-size:.78rem">⚠ El umbral del 40% en Nacional es fijo y arbitrario. Organismos pequeños con pocos contratos
        pueden disparar esta señal sin que haya nada anómalo. El umbral adaptativo de Catalunya es más robusto.</span><br>
        <span class="step-stat">{_ds_fmt('flag7_concentracion')} empresas (Nacional)</span> <span class="step-stat">{_ds_fmt('flag7_concentracion', 'n_rows')} pares empresa-órgano</span></div></div>

    <div class="step"><div class="step-n">13</div><div class="step-body"><div class="step-title">F8 · UTEs con miembros vinculados</div>
        UTEs (Uniones Temporales de Empresas) cuyos miembros comparten administrador según BORME.
        Si los dos miembros de una UTE tienen el mismo decisor, la unión no aporta independencia real.<br>
        <span class="step-stat">{_ds_fmt('flag8_utes_sospechosas')} pares de empresas</span></div></div>

    <div class="step"><div class="step-n">14</div><div class="step-body"><div class="step-title">F9 · Discrepancia geográfica <span style="font-size:.7rem;color:{C['muted']}">(solo Nacional)</span></div>
        Empresa registrada en una CCAA que gana contratos <b>mayoritariamente en otra</b>.
        Solo para PYMEs (3–200 adjudicaciones). Las grandes con sede en Madrid se excluyen
        porque es normal que operen en todo el territorio.<br>
        <span style="color:{C['muted']};font-size:.78rem">⚠ Señal débil — la más ruidosa del análisis. Muchas empresas operan legítimamente fuera de su comunidad
        (ej: constructora de Sevilla con obra en Huelva). Por sí sola tiene poco valor; cobra sentido combinada con otras señales.</span><br>
        <span class="step-stat">{_ds_fmt('flag9_geo_discrepancia')} empresas</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Señales específicas de Catalunya (F10 – F11)</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.65;margin-bottom:14px">
        Estas señales solo se pueden calcular con datos catalanes, que incluyen contratos menores
        y columnas nativas de modificaciones contractuales que no existen en PLACSP.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">15</div><div class="step-body"><div class="step-title">F10 · Posible fraccionamiento <span style="font-size:.7rem;color:{C['muted']}">(solo Catalunya)</span></div>
        Un mismo par empresa×órgano tiene <b>≥3 contratos menores (≤15K€) en 90 días</b> cuya suma
        supera el umbral de 15K€. Esto podría indicar que se divide un contrato mayor en partes
        para evitar el procedimiento de licitación pública.<br>
        <span class="step-stat">{_ds_fmt('flag10_troceo_cat')} empresas</span> <span class="step-stat">{_ds_fmt('flag10_troceo_cat', 'n_rows')} clusters detectados</span></div></div>

    <div class="step"><div class="step-n">16</div><div class="step-body"><div class="step-title">F11 · Modificaciones excesivas <span style="font-size:.7rem;color:{C['muted']}">(solo Catalunya)</span></div>
        Empresas con <b>≥20% de sus contratos modificados</b> (la media es ~0.6%).
        Puede indicar adjudicaciones inicialmente bajas que se incrementan después de ganadas,
        aprovechando que las modificaciones tienen menos escrutinio.<br>
        <span style="color:{C['muted']};font-size:.78rem">⚠ La media del 0.6% incluye todos los tipos de contrato. Sectores como obras o servicios técnicos
        tienen tasas de modificación naturalmente más altas. Una comparación por tipo de contrato sería más justa.</span><br>
        <span class="step-stat">{_ds_fmt('flag11_modificaciones_cat')} empresas</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Consolidar resultados</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="step"><div class="step-n">17</div><div class="step-body"><div class="step-title">Listado final</div>
        Unión de todas las señales (F1–F11) por empresa. Cada empresa recibe un <b>vector binario</b>
        que indica qué señales tiene activas y cuántas son en total.
        La app no muestra puntuaciones numéricas — solo <b>qué señales tiene cada empresa y cuántas</b>.<br>
        <span class="step-stat">Nacional: {_ds_fmt('risk_scoring_unificado')} con ≥1 señal</span> <span class="step-stat">{_ds_fmt('risk_scoring_unificado', 'n_ge3')} con ≥3</span>
        <span class="step-stat">Catalunya: {_ds_fmt('risk_scoring_cat')} con ≥1 señal</span></div></div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Diferencias Nacional vs Catalunya</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="card card-l card-blue">
        <b>Datos:</b> Nacional usa {fmt(PIPELINE['placsp_useful'])} adj. de PLACSP · Catalunya usa {fmt(PIPELINE['cat_total'])} del Registre Públic + {fmt(PIPELINE['cat_menores'])} menores BCN<br><br>
        <b>Matching:</b> Nacional cruza {fmt(PIPELINE['matched_nac'])} empresas con BORME · Catalunya {fmt(PIPELINE['matched_cat'])}<br><br>
        <b>F7 Concentración:</b> Nacional usa umbral fijo (40%) · Catalunya usa umbral adaptativo (20/30/40% según volumen)<br><br>
        <b>Señales exclusivas:</b> F9 (geográfica) solo Nacional · F10 (fraccionamiento) y F11 (modificaciones) solo Catalunya
    </div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────
    st.markdown('<div class="sec">Limitaciones</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="card card-l card-amber">
        <b>Cobertura parcial:</b> Solo el {PIPELINE['coverage_pct']}% de adjudicatarios se cruzan con BORME.
        Autónomos, personas físicas y empresas extranjeras no figuran en el Registro Mercantil.<br><br>
        <b>Cruce por nombre, no por NIF:</b> Posibles homónimos (falsos positivos) y variantes de nombre
        no capturadas (falsos negativos). Las {PIPELINE['stop_words']:,} stop words y {PIPELINE['manual_rules']} reglas manuales mitigan el problema,
        pero no lo eliminan.<br><br>
        <b>Vigencia de cargos:</b> Si el cese de un cargo no se publica en BORME, aparece como vigente.
        El BORME no registra cargos de hecho.<br><br>
        <b>Grupos corporativos:</b> Los filtros son heurísticos (nombre, consejo, fusiones BORME).
        Holdings complejos con estructuras opacas pueden escapar al filtro.<br><br>
        <b>F10 — ventana limitada:</b> Solo detecta fraccionamiento en ventanas de 90 días con umbral de 15K€.
        Patrones más sofisticados (distintos órganos, periodos más largos) no se capturan.<br><br>
        <b>F9 — señal ruidosa:</b> La discrepancia geográfica es la señal con más falsos positivos.
        Muchas empresas operan legítimamente fuera de su comunidad. Por sí sola tiene poco valor diagnóstico.<br><br>
        <b>F7 — umbral arbitrario:</b> El 40% fijo en Nacional no distingue organismos grandes de pequeños.
        El umbral adaptativo de Catalunya (20/30/40% según volumen) es más robusto.<br><br>
        <b>F11 — media global:</b> Comparar contra la media general de modificaciones (0.6%) penaliza sectores
        como obras o servicios técnicos donde las modificaciones son más habituales.<br><br>
        <b>Señal ≠ fraude.</b> Cada señal tiene una explicación inocente plausible. Este análisis
        sirve para priorizar la supervisión humana, no para acusar.
    </div>""", unsafe_allow_html=True)


# ═══════════════ TAB 4: SCREENER ═══════════════

# Friendly names — keys are distinctive substrings to match any column naming convention
FLAG_LABELS = {
    'recien_cread':    {'label': 'Recién creada',          'short': 'F1', 'pill': 'scr-pill-red',    'color_key': 'red'},
    'capital_ridic':   {'label': 'Capital mínimo',         'short': 'F2', 'pill': 'scr-pill-amber',  'color_key': 'amber'},
    'disolucion':      {'label': 'Disuelta',               'short': 'F4', 'pill': 'scr-pill-red',    'color_key': 'red'},
    'concursal':       {'label': 'Concursal',              'short': 'F5', 'pill': 'scr-pill-red',    'color_key': 'red'},
    'red_admin':       {'label': 'Red administradores',    'short': 'F6', 'pill': 'scr-pill-blue',   'color_key': 'blue2'},
    'concentracion':   {'label': 'Concentración',          'short': 'F7', 'pill': 'scr-pill-teal',   'color_key': 'teal'},
    'ute_sospech':     {'label': 'UTEs vinculadas',        'short': 'F8', 'pill': 'scr-pill-amber',  'color_key': 'amber'},
    'geo_discrep':     {'label': 'Discrepancia geográfica','short': 'F9', 'pill': 'scr-pill-purple', 'color_key': 'purple'},
    'troceo':          {'label': 'Fraccionamiento',        'short': 'F10','pill': 'scr-pill-red',    'color_key': 'red'},
    'modificacion':    {'label': 'Modificaciones',         'short': 'F11','pill': 'scr-pill-amber',  'color_key': 'amber'},
}

# Column rename — covers ALL parquets
COL_RENAME = {
    # ── Company / person identifiers ──
    'empresa_norm':'Empresa', 'adj_norm':'Empresa', 'adjudicatario':'Adjudicatario',
    'persona':'Persona', 'empresa_1':'Empresa 1', 'empresa_2':'Empresa 2',
    'ute_name':'Nombre UTE', 'member_1':'Miembro 1', 'member_2':'Miembro 2',
    'personas':'Personas vinculadas',
    # ── Amounts ──
    'n_adj':'Nº adjudicaciones', 'importe':'Importe total', 'importe_total':'Importe total',
    'importe_adjudicacion':'Importe adj.', 'importe_par':'Importe par',
    'importe_e1':'Importe emp. 1', 'importe_e2':'Importe emp. 2',
    'importe_ute':'Importe UTE', 'importe_cluster':'Importe cluster',
    'importe_medio_cluster':'Importe medio cluster', 'importe_total_par':'Importe total par',
    'importe_total_empresa':'Importe total empresa', 'importe_mods':'Importe modificaciones',
    'capital_euros':'Capital social (€)',
    'n_adj_e1':'Adj. emp. 1', 'n_adj_e2':'Adj. emp. 2', 'n_adj_ute':'Adj. UTE',
    'n_adj_empresa':'Adj. empresa', 'max_adj':'Máx. adj.',
    # ── Flag counts ──
    'n_flags_total':'Nº señales', 'n_flags':'Nº señales',
    # ── Dates ──
    'fecha_adjudicacion':'Fecha adj.', 'fecha_constitucion':'Fecha constitución',
    'fecha_disolucion':'Fecha disolución', 'fecha_concursal':'Fecha concursal',
    # ── F1 ──
    'dias_desde_constitucion':'Días desde constitución',
    # ── F2 ──
    'ratio_importe_capital':'Ratio importe/capital',
    # ── F4 ──
    'dias_hasta_disolucion':'Días hasta disolución',
    # ── F6 network ──
    'n_organos_comunes':'Órganos comunes', 'organos_comunes':'Lista órganos comunes',
    'n_empresas_persona':'Empresas por persona', 'n_organos_concurrent':'Órganos concurrentes',
    'pct_concurrent':'% concurrencia', 'board_overlap':'Overlap consejo',
    'n_shared_board':'Consejeros compartidos', 'board_e1':'Consejo emp. 1', 'board_e2':'Consejo emp. 2',
    'n_personas':'Nº personas', 'n_personas_par':'Personas en par',
    'n_pares':'Nº pares', 'n_empresas':'Nº empresas', 'max_organos':'Máx. órganos',
    'total_flags':'Total señales', 'max_cargo_weight':'Peso máx. cargo', 'cargo_weight':'Peso cargo',
    'f6_score':'Score red (F6)',
    # ── F7 ──
    'organo_contratante':'Órgano contratante', 'total_adj_organo':'Total adj. órgano',
    'total_importe_organo':'Importe total órgano', 'pct_adj_organo':'% adj. en órgano',
    'pct_importe_organo':'% importe en órgano', 'f7_max_conc':'Máx. concentración (F7)',
    'threshold':'Umbral',
    # ── F8 ──
    'organos':'Órganos',
    # ── F9 ──
    'provincia_borme':'Provincia registro', 'ccaa_borme':'CCAA registro',
    'ccaa_contrato_principal':'CCAA contratos',
    # ── F10 ──
    'n_contratos_cluster':'Contratos en cluster', 'supera_umbral':'Supera umbral',
    'ratio_sobre_umbral':'Ratio sobre umbral', 'n_contratos_total':'Contratos totales par',
    'ventana_dias':'Ventana (días)', 'umbral':'Umbral (€)',
    # ── F11 ──
    'n_contratos':'Nº contratos', 'n_modificaciones':'Nº modificaciones',
    'pct_modificados':'% modificados',
    # ── Contract details ──
    'objeto':'Objeto del contrato', 'id':'ID contrato',
    # ── Grupos corporativos ──
    'grupo_reason':'Razón agrupación',
    # ── Scoring (useful info — no longer hidden) ──
    'risk_score':'Score riesgo', 'score':'Score', 'score_max':'Score máx.',
    'score_sum':'Score suma', 'par_score':'Score par', 'score_total':'Score total',
    'min_organos':'Mín. órganos', 'concentracion':'Concentración',
    # ── Bool flags ──
    'F1_recien_creada':'F1 · Recién creada', 'F2_capital_ridiculo':'F2 · Capital mínimo',
    'F4_disolucion':'F4 · Disuelta', 'F5_concursal':'F5 · Concursal',
    'F6_red_admin':'F6 · Red admin.', 'F7_concentracion':'F7 · Concentración',
    'F8_ute_sospechosa':'F8 · UTE vinculada', 'F9_geo_discrepancia':'F9 · Geo discrepancia',
    'F10_troceo':'F10 · Fraccionamiento', 'F11_modificaciones':'F11 · Modificaciones',
    # ── F6 detail bools ──
    'F1_recien_creada_e1':'F1 emp.1', 'F1_recien_creada_e2':'F1 emp.2', 'F1_recien_creada_any':'F1 alguna',
    'F2_capital_ridiculo_e1':'F2 emp.1', 'F2_capital_ridiculo_e2':'F2 emp.2', 'F2_capital_ridiculo_any':'F2 alguna',
    'F4_disolucion_e1':'F4 emp.1', 'F4_disolucion_e2':'F4 emp.2', 'F4_disolucion_any':'F4 alguna',
    'F5_concursal_e1':'F5 emp.1', 'F5_concursal_e2':'F5 emp.2', 'F5_concursal_any':'F5 alguna',
    'F1_any':'F1 alguna', 'F2_any':'F2 alguna', 'F4_any':'F4 alguna', 'F5_any':'F5 alguna',
}

def _flag_info(col):
    """Get full info dict for a flag column, matching by substring."""
    col_l = col.lower()
    for key, info in FLAG_LABELS.items():
        if key in col_l:
            return info
    return None

def _flag_label(col):
    info = _flag_info(col)
    if info: return f"{info['short']} · {info['label']}"
    return col

def _flag_short(col):
    info = _flag_info(col)
    return info['short'] if info else col[:6]

def _flag_pill_class(col):
    info = _flag_info(col)
    return info['pill'] if info else 'scr-pill-blue'

def _flag_color(col):
    info = _flag_info(col)
    return C.get(info['color_key'], C['blue2']) if info else C['blue2']

def _rename_columns(df):
    """Rename raw column names to human-readable ones."""
    rmap = {}
    for c in df.columns:
        # Exact match first (case-sensitive for bool flags like F1_recien_creada)
        if c in COL_RENAME:
            rmap[c] = COL_RENAME[c]
            continue
        # Case-insensitive exact match
        cl = c.lower()
        for k, v in COL_RENAME.items():
            if cl == k.lower():
                rmap[c] = v
                break
    if rmap:
        df = df.rename(columns=rmap)
    return df

def _format_importe_col(df):
    """Format any importe/capital columns to readable currency strings."""
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in ['importe','capital']):
            if df[c].dtype in ('float64','Float64','int64','Int64'):
                df[c] = df[c].apply(lambda v: f"{v/1e6:,.2f}M€" if pd.notna(v) and abs(v) >= 1e6
                    else f"{v:,.0f}€" if pd.notna(v) else "")
    return df

def _format_pct_col(df):
    """Format percentage columns."""
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in ['pct_','% ']) and 'modificados' not in cl:
            if df[c].dtype in ('float64','Float64'):
                df[c] = df[c].apply(lambda v: f"{v:.1%}" if pd.notna(v) else "")
        elif 'modificados' in cl and df[c].dtype in ('float64','Float64'):
            df[c] = df[c].apply(lambda v: f"{v:.1%}" if pd.notna(v) else "")
    return df

def render_screener(flag_files):

    # ── Find scoring files ──
    scoring_files = {}
    for stem, fi in flag_files.items():
        if 'risk_scoring' in stem:
            scoring_files[stem] = fi

    if not scoring_files:
        st.markdown("""<div class="scr-empty">
            <span class="scr-empty-icon">📭</span>
            No se encontró <code>risk_scoring_unificado.parquet</code>.
        </div>""", unsafe_allow_html=True)
        return

    # ── Scope selector ──
    scope_names = {}
    for s, fi in scoring_files.items():
        scope_names[s] = '🇪🇸 Nacional' if 'cat' not in s else '🏗️ Catalunya'
    if len(scoring_files) > 1:
        sel_scope = st.radio("Ámbito", list(scoring_files.keys()),
            format_func=lambda x: scope_names[x], horizontal=True, key="scr_scope",
            label_visibility="collapsed")
    else:
        sel_scope = list(scoring_files.keys())[0]

    with st.spinner("Cargando…"):
        df_raw = load_pq(scoring_files[sel_scope]['path'])

    bool_cols = [c for c in df_raw.columns if df_raw[c].dtype == bool and df_raw[c].sum() > 0]
    if not bool_cols:
        st.info("No se detectaron columnas de señales booleanas.")
        return
    bool_cols = sorted(bool_cols, key=lambda c: -int(df_raw[c].sum()))
    nf_col = next((c for c in df_raw.columns if 'n_flags' in c.lower()), None)

    # ══════════════════════════════════════════════
    # PANORAMA — clean horizontal bar chart of all flags
    # ══════════════════════════════════════════════
    chart_labels = []
    chart_counts = []
    chart_colors = []
    for fc in reversed(bool_cols):
        info = _flag_info(fc)
        if info:
            chart_labels.append(f"{info['short']}  {info['label']}")
        else:
            chart_labels.append(fc)
        chart_counts.append(int(df_raw[fc].sum()))
        chart_colors.append(_flag_color(fc))

    fig_overview = go.Figure(go.Bar(
        y=chart_labels, x=chart_counts, orientation='h',
        marker=dict(color=chart_colors, opacity=.88, line=dict(width=0)),
        text=[f"  {c:,}" for c in chart_counts],
        textposition='outside',
        textfont=dict(family='IBM Plex Mono', size=11, color=C['text2']),
        hovertemplate='<b>%{y}</b><br>%{x:,} empresas<extra></extra>'))
    pl2 = {k: v for k, v in PL.items() if k != 'margin'}
    fig_overview.update_layout(
        **pl2, height=max(220, len(bool_cols) * 36 + 50),
        margin=dict(l=0, r=80, t=36, b=0),
        xaxis=dict(gridcolor=C['grid'], showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=11, family='DM Sans', color=C['text2']),
            automargin=True),
        title=dict(
            text=f"<b>{len(df_raw):,}</b> empresas  ·  <b>{len(bool_cols)}</b> señales detectadas",
            font=dict(size=12, color=C['text2'], family='DM Sans'),
            x=0, xanchor='left'),
        bargap=.25)
    st.plotly_chart(fig_overview, use_container_width=True)

    # ══════════════════════════════════════════════
    # FILTER CONTROLS
    # ══════════════════════════════════════════════
    st.markdown(f"""<div style="height:1px;background:linear-gradient(90deg,{C['border']},{C['bg']});
        margin:4px 0 20px"></div>""", unsafe_allow_html=True)

    # Build rich option labels
    flag_opts = {}
    for c in bool_cols:
        info = _flag_info(c)
        if info:
            flag_opts[c] = f"{info['short']} · {info['label']}  —  {int(df_raw[c].sum()):,}"
        else:
            flag_opts[c] = f"{c}  —  {int(df_raw[c].sum()):,}"

    fc1, fc2 = st.columns([4, 1])
    with fc1:
        selected_flags = st.multiselect(
            "Filtrar por señales",
            options=bool_cols,
            format_func=lambda c: flag_opts[c],
            key="scr_flags",
            placeholder="Elige señales para filtrar empresas…",
        )
    with fc2:
        if len(selected_flags) >= 2:
            logic = st.radio("Lógica",
                ["AND — Todas", "OR — Al menos 1"],
                key="scr_logic", label_visibility="collapsed")
            is_and = logic.startswith("AND")
        else:
            is_and = True
            st.markdown(f"""<div style="background:{C['card']};border:1px solid {C['border']};
                border-radius:10px;padding:10px 12px;text-align:center;margin-top:25px">
                <span style="font-family:IBM Plex Mono;font-size:.6rem;color:{C['muted']};
                    letter-spacing:.06em">{'SELECCIONA ≥2' if len(selected_flags)<2 else 'FILTRO DIRECTO'}</span>
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # EMPTY STATE
    # ══════════════════════════════════════════════
    if not selected_flags:
        if nf_col:
            dist = df_raw[nf_col].value_counts().sort_index()
            fig_dist = go.Figure(go.Bar(
                x=[f"{int(k)}" for k in dist.index], y=dist.values,
                marker=dict(
                    color=[C['blue'] if k <= 1 else C['amber'] if k <= 2 else C['red'] for k in dist.index],
                    opacity=.85, line=dict(width=0)),
                text=[f"{v:,}" for v in dist.values],
                textposition='outside',
                textfont=dict(family='IBM Plex Mono', size=10, color=C['muted']),
                hovertemplate='%{x} señales<br>%{y:,} empresas<extra></extra>'))
            fig_dist.update_layout(**PL, height=200,
                title=dict(text='Señales acumuladas por empresa',
                    font=dict(size=11, color=C['text2']), x=0),
                xaxis=dict(title='Nº señales', gridcolor=C['grid']),
                yaxis=dict(gridcolor=C['grid'], showticklabels=False), bargap=.2)
            st.plotly_chart(fig_dist, use_container_width=True)
        return

    # ══════════════════════════════════════════════
    # APPLY FILTER
    # ══════════════════════════════════════════════
    if is_and:
        mask = pd.Series(True, index=df_raw.index)
        for c in selected_flags:
            mask &= df_raw[c]
    else:
        mask = pd.Series(False, index=df_raw.index)
        for c in selected_flags:
            mask |= df_raw[c]
    df_filtered = df_raw[mask].copy()
    pct = len(df_filtered) / len(df_raw) * 100 if len(df_raw) > 0 else 0

    # ══════════════════════════════════════════════
    # RESULTS BANNER
    # ══════════════════════════════════════════════
    # Build pills as simple CSS-class spans (no inline styles to avoid f-string quote issues)
    pills_parts = []
    for c in selected_flags:
        info = _flag_info(c)
        pcls = _flag_pill_class(c)
        lbl = _flag_label(c) if info else c
        pills_parts.append('<span class="scr-pill ' + pcls + '">' + lbl + '</span>')
    pills_html = "".join(pills_parts)

    logic_html = ""
    if len(selected_flags) >= 2:
        if is_and:
            logic_html = '<span class="scr-logic scr-logic-and">AND</span>'
        else:
            logic_html = '<span class="scr-logic scr-logic-or">OR</span>'

    banner = (
        '<div class="scr-results">'
        '<div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap">'
        '<div style="flex-shrink:0;min-width:110px">'
        '<div class="scr-count">' + f"{len(df_filtered):,}" + '</div>'
        '<div class="scr-count-label">'
        + f"empresas · {pct:.1f}% del total" +
        '</div></div>'
        '<div style="width:1px;height:48px;background:' + C['border'] + '"></div>'
        '<div style="flex:1;min-width:200px">'
        + ('<div style="margin-bottom:8px">' + logic_html + '</div>' if logic_html else '') +
        '<div class="scr-active-flags">' + pills_html + '</div>'
        '</div></div></div>'
    )
    st.markdown(banner, unsafe_allow_html=True)

    if len(df_filtered) == 0:
        msg = 'todas' if is_and else 'ninguna de'
        alt = 'OR' if is_and else 'AND'
        st.markdown(
            '<div style="text-align:center;padding:40px;color:' + C['muted'] + '">'
            '<div style="font-size:1.2rem;margin-bottom:6px;opacity:.35">Sin resultados</div>'
            '<span style="font-size:.84rem">Ninguna empresa cumple ' + msg + ' las señales.</span><br>'
            '<span style="font-size:.76rem">Cambia señales o prueba modo ' + alt + '.</span>'
            '</div>', unsafe_allow_html=True)
        return

    # ── Metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        imp_col = next((c for c in df_filtered.columns if 'importe' in c.lower() and 'total' in c.lower()), None)
        if not imp_col:
            imp_col = next((c for c in df_filtered.columns if 'importe' in c.lower()), None)
        if imp_col and df_filtered[imp_col].notna().any():
            st.metric("Importe total", f"{df_filtered[imp_col].sum()/1e6:,.0f}M€")
        else:
            st.metric("Empresas", f"{len(df_filtered):,}")
    with m2:
        if nf_col and nf_col in df_filtered.columns:
            st.metric("Media señales", f"{df_filtered[nf_col].mean():.1f}")
    with m3:
        adj_col = next((c for c in df_filtered.columns if 'n_adj' in c.lower() or 'n_contratos' in c.lower()), None)
        if adj_col:
            st.metric("Contratos", f"{int(df_filtered[adj_col].sum()):,}")
    with m4:
        st.metric("Señales activas", f"{sum(int(df_filtered[c].sum()) for c in bool_cols):,}")

    # ── Prepare display table ──
    df_show = _rename_columns(clean_df(df_filtered))

    # Reorder: Empresa first, then numeric, then flags, then Nº señales last
    col_order = []
    empresa_col = next((c for c in df_show.columns if c == 'Empresa'), None)
    if empresa_col:
        col_order.append(empresa_col)
    for c in df_show.columns:
        if c not in col_order and c != 'Nº señales' and df_show[c].dtype != bool:
            col_order.append(c)
    for c in df_show.columns:
        if df_show[c].dtype == bool:
            col_order.append(c)
    if 'Nº señales' in df_show.columns:
        col_order.append('Nº señales')
    df_show = df_show[[c for c in col_order if c in df_show.columns]]

    # Sortable columns (before formatting)
    sortable = [c for c in df_show.columns if df_show[c].dtype in ('int64','float64','int32','float32','Int64','Float64')]

    # ── Search + Sort ──
    sf1, sf2 = st.columns([2.5, 1])
    with sf1:
        search_q = st.text_input("🔍 Buscar", key="scr_search",
            placeholder="Nombre de empresa, órgano, persona…")
    with sf2:
        sort_col = '(sin ordenar)'
        if sortable:
            sort_col = st.selectbox("Ordenar", ['(sin ordenar)'] + sortable, key="scr_sort")

    if search_q and len(search_q) >= 2:
        smask = pd.Series(False, index=df_show.index)
        for col in df_show.select_dtypes(include=['object']).columns:
            smask |= df_show[col].astype(str).str.contains(search_q, case=False, na=False)
        df_show = df_show[smask]
        st.caption(f"🔍 {len(df_show):,} resultados para «{search_q}»")
    if sort_col != '(sin ordenar)' and sort_col in df_show.columns:
        df_show = df_show.sort_values(sort_col, ascending=False)

    # Format after sort (so numeric sort works)
    df_show = _format_importe_col(df_show)
    df_show = _format_pct_col(df_show)

    st.dataframe(df_show.head(2000), use_container_width=True, height=520, hide_index=True)
    st.caption(f"Mostrando {min(len(df_show), 2000):,} de {len(df_show):,}")

    # ── Breakdown chart ──
    with st.expander("📊 Desglose de señales en estos resultados"):
        bd_labels = []
        bd_counts = []
        bd_colors = []
        for fc in reversed(bool_cols):
            n = int(df_filtered[fc].sum())
            if n > 0:
                info = _flag_info(fc)
                bd_labels.append(f"{info['short']}  {info['label']}" if info else fc)
                bd_counts.append(n)
                bd_colors.append(_flag_color(fc))
        if bd_labels:
            fig_bd = go.Figure(go.Bar(
                y=bd_labels, x=bd_counts, orientation='h',
                marker=dict(color=bd_colors, opacity=.85),
                text=[f"  {v:,}" for v in bd_counts],
                textposition='outside',
                textfont=dict(family='IBM Plex Mono', size=10, color=C['text2']),
                hovertemplate='<b>%{y}</b><br>%{x:,}<extra></extra>'))
            fig_bd.update_layout(**PL, height=max(180, len(bd_labels) * 32),
                xaxis=dict(gridcolor=C['grid'], showticklabels=False),
                yaxis=dict(tickfont=dict(size=10, family='DM Sans'), automargin=True),
                bargap=.22)
            st.plotly_chart(fig_bd, use_container_width=True)


# ═══════════════ MAIN ═══════════════
def main():
    st.markdown(f"""
    <div class="hero">
        <h1>Contratación <span>Pública</span></h1>
        <p class="mono">BQUANT FINANCE · @GSNCHEZ</p>
        <div class="hero-desc">
            Cruzamos <b>{fmt(PIPELINE['placsp_total'])} de contratos públicos</b> con <b>{fmt(PIPELINE['borme_actos'])} de actos
            del Registro Mercantil</b> para detectar patrones que merecen atención.
        </div>
    </div><div class="divider"></div>
    """, unsafe_allow_html=True)
    flag_files = discover_flags()
    tabs = st.tabs(["📊 Resumen", "🔬 Screener", "🔎 Explorar señales", "📋 Cómo funciona"])
    with tabs[0]: render_resumen(flag_files)
    with tabs[1]: render_screener(flag_files)
    with tabs[2]: render_explorar(flag_files)
    with tabs[3]: render_metodo()
    st.markdown("""<div class="ft"><a href="https://twitter.com/Gsnchez">@Gsnchez</a> · <a href="https://bquantfinance.com">bquantfinance.com</a> · <a href="https://github.com/BquantFinance">GitHub</a></div>""", unsafe_allow_html=True)

if __name__ == "__main__": main()
