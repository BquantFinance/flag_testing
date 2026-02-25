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
    page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed",
)

DATA = Path("anomalias")
Q_DIR = DATA / "quality"

C = {
    'bg':'#06080d','card':'#0b0e15','card2':'#0f1219','border':'#171c28','border2':'#1f2636',
    'accent':'#d94a2e','accent2':'#e8603f','blue':'#3a7bd5','blue2':'#5b9bf0','teal':'#10b981',
    'amber':'#e5a229','red':'#dc4444','purple':'#8466d4',
    'text':'#dfe5ef','text2':'#8d99af','muted':'#505c72','grid':'rgba(255,255,255,0.025)',
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

/* ── Resets & vars ── */
:root {{
    --bg: {C['bg']}; --card: {C['card']}; --card2: {C['card2']};
    --border: {C['border']}; --border2: {C['border2']};
    --accent: {C['accent']}; --accent2: {C['accent2']};
    --blue: {C['blue']}; --blue2: {C['blue2']};
    --teal: {C['teal']}; --amber: {C['amber']};
    --red: {C['red']}; --purple: {C['purple']};
    --text: {C['text']}; --text2: {C['text2']}; --muted: {C['muted']};
}}

*, *::before, *::after {{ box-sizing: border-box }}

/* ── App shell ── */
.stApp {{
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 80% 55% at 10% 0%, rgba(58,123,213,.04) 0%, transparent 55%),
        radial-gradient(ellipse 60% 45% at 90% 100%, rgba(217,74,46,.025) 0%, transparent 50%),
        radial-gradient(ellipse 40% 35% at 50% 50%, rgba(132,102,212,.012) 0%, transparent 60%);
    color: var(--text);
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}}
section[data-testid="stSidebar"] {{
    background: var(--card); border-right: 1px solid var(--border);
}}
.block-container {{
    max-width: 1180px;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px }}
::-webkit-scrollbar-track {{ background: transparent }}
::-webkit-scrollbar-thumb {{
    background: rgba(255,255,255,.08); border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(255,255,255,.14) }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0; border-bottom: 1px solid var(--border);
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent; color: var(--muted); border: none;
    padding: 14px 28px; font-family: 'DM Sans'; font-size: .82rem;
    font-weight: 600; letter-spacing: .02em;
    transition: color .3s, border-color .3s;
    border-bottom: 2px solid transparent;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--text2) }}
.stTabs [aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: .5rem }}

/* ── Metrics ── */
div[data-testid="stMetric"] {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 18px 22px; position: relative; overflow: hidden;
    transition: border-color .3s, box-shadow .3s;
}}
div[data-testid="stMetric"]:hover {{
    border-color: var(--border2);
    box-shadow: 0 4px 24px rgba(0,0,0,.15);
}}
div[data-testid="stMetric"]::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 5%, var(--blue) 50%, transparent 95%);
    opacity: .35;
}}
div[data-testid="stMetric"] label {{
    color: var(--muted) !important;
    font-family: 'IBM Plex Mono'; font-size: .58rem !important;
    letter-spacing: .1em; text-transform: uppercase;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: var(--text) !important;
    font-family: 'IBM Plex Mono'; font-size: 1.25rem !important; font-weight: 600;
}}
div[data-testid="stMetricDelta"] {{ font-family: 'IBM Plex Mono'; font-size: .7rem !important }}

/* ── Expander ── */
div[data-testid="stExpander"] {{
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; overflow: hidden;
    transition: border-color .3s;
}}
div[data-testid="stExpander"]:hover {{ border-color: var(--border2) !important }}
div[data-testid="stExpander"] details summary {{
    font-family: 'DM Sans'; font-size: .84rem; font-weight: 600; color: var(--text2);
    padding: 14px 18px;
}}
div[data-testid="stExpander"] details summary:hover {{ color: var(--text) }}
div[data-testid="stExpander"] details[open] summary {{ border-bottom: 1px solid var(--border) }}

/* ── Inputs: text, select, number ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {{
    background: var(--card2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-family: 'IBM Plex Mono'; font-size: .82rem !important;
    padding: 10px 14px !important;
    transition: border-color .3s, box-shadow .3s;
}}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {{
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,.12) !important;
    outline: none !important;
}}
div[data-testid="stTextInput"] input::placeholder {{ color: var(--muted) !important; opacity: .7 }}
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
.stSelectbox label {{
    color: var(--muted) !important;
    font-family: 'IBM Plex Mono'; font-size: .6rem !important;
    letter-spacing: .08em; text-transform: uppercase;
}}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {{
    background: var(--card2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-family: 'DM Sans'; font-size: .82rem !important;
    transition: border-color .3s;
}}
.stSelectbox [data-baseweb="select"] > div:hover {{ border-color: var(--border2) !important }}
.stSelectbox [data-baseweb="select"] > div:focus-within {{
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,.12) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul {{
    background: {C['card2']} !important; border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
}}
[data-baseweb="popover"] li {{
    color: var(--text2) !important; font-family: 'DM Sans'; font-size: .82rem !important;
    transition: background .2s, color .2s;
}}
[data-baseweb="popover"] li:hover {{
    background: rgba(58,123,213,.08) !important; color: var(--text) !important;
}}
[data-baseweb="popover"] li[aria-selected="true"] {{
    background: rgba(217,74,46,.1) !important; color: var(--accent) !important;
}}

/* ── Dataframe / table ── */
div[data-testid="stDataFrame"] {{
    border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
}}
div[data-testid="stDataFrame"] [data-testid="glideDataEditor"] {{
    border-radius: 12px !important;
}}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: var(--accent) !important }}

/* ── Caption ── */
.stCaption, div[data-testid="stCaptionContainer"] {{
    font-family: 'IBM Plex Mono' !important; font-size: .72rem !important;
    color: var(--muted) !important;
}}

/* ── Info / Warning / Error boxes ── */
div[data-testid="stAlert"] {{
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text2) !important;
    font-size: .82rem; font-family: 'DM Sans';
}}

/* ── Buttons (if any) ── */
.stButton > button {{
    background: var(--card2) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-family: 'DM Sans'; font-weight: 600; font-size: .82rem;
    padding: 8px 20px; transition: all .3s;
}}
.stButton > button:hover {{
    border-color: var(--accent) !important; color: var(--accent) !important;
    box-shadow: 0 2px 12px rgba(217,74,46,.12);
}}

/* ══════════════════════════════════
   CUSTOM CLASSES
   ══════════════════════════════════ */

/* ── Hero ── */
.hero {{
    text-align: center; padding: 3rem 0 .8rem;
    animation: fadeIn .7s ease-out;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px) }}
    to   {{ opacity: 1; transform: translateY(0) }}
}}
.hero h1 {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.6rem; font-weight: 700; color: var(--text);
    letter-spacing: -.03em; margin: 0; line-height: 1.15;
}}
.hero h1 span {{
    color: var(--accent);
    background: linear-gradient(135deg, var(--accent) 20%, var(--accent2) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero .mono {{
    font-family: 'IBM Plex Mono'; font-size: .6rem; color: var(--muted);
    letter-spacing: .2em; text-transform: uppercase; margin-top: .6rem;
}}
.hero-desc {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.05rem; font-style: italic; color: var(--text2);
    max-width: 640px; margin: 1rem auto 0; line-height: 1.7; font-weight: 400;
}}
.hero-desc b {{ color: var(--text); font-weight: 600; font-style: normal }}

/* ── Divider ── */
.divider {{
    height: 1px; margin: 1.5rem 0;
    background: linear-gradient(90deg, transparent 2%, {C['border2']} 50%, transparent 98%);
}}

/* ── Section header ── */
.sec {{
    font-family: 'IBM Plex Mono'; font-size: .64rem; font-weight: 600;
    color: var(--accent); letter-spacing: .14em; text-transform: uppercase;
    border-bottom: 1px solid var(--border); padding-bottom: 8px;
    margin: 2.2rem 0 1.1rem; position: relative;
}}
.sec::after {{
    content: ''; position: absolute; bottom: -1px; left: 0;
    width: 40px; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    border-radius: 1px;
}}

/* ── Cards ── */
.card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px; margin: 10px 0;
    font-size: .84rem; color: var(--text2); line-height: 1.7;
    transition: border-color .3s, box-shadow .3s;
}}
.card:hover {{
    border-color: var(--border2);
    box-shadow: 0 2px 16px rgba(0,0,0,.1);
}}
.card b {{ color: var(--text) }}
.card-l {{
    border-left: 3px solid; border-radius: 0 12px 12px 0;
    padding-left: 22px;
}}
.card-accent {{ border-left-color: var(--accent) }}
.card-blue  {{ border-left-color: var(--blue) }}
.card-teal  {{ border-left-color: var(--teal) }}
.card-amber {{ border-left-color: var(--amber) }}
.card-red   {{ border-left-color: var(--red) }}

/* ── Badges ── */
.badge {{
    display: inline-block; padding: 3px 11px; border-radius: 6px;
    font-family: 'IBM Plex Mono'; font-size: .58rem; font-weight: 600;
    margin: 2px 4px 2px 0; letter-spacing: .04em;
    vertical-align: middle;
}}
.b-red    {{ background: rgba(220,68,68,.1);  color: var(--red);    border: 1px solid rgba(220,68,68,.2) }}
.b-blue   {{ background: rgba(58,123,213,.1); color: var(--blue2);  border: 1px solid rgba(58,123,213,.2) }}
.b-amber  {{ background: rgba(229,162,41,.1); color: var(--amber);  border: 1px solid rgba(229,162,41,.2) }}
.b-teal   {{ background: rgba(16,185,129,.1); color: var(--teal);   border: 1px solid rgba(16,185,129,.2) }}
.b-purple {{ background: rgba(132,102,212,.1);color: var(--purple); border: 1px solid rgba(132,102,212,.2) }}

/* ── Warning box ── */
.warn-box {{
    background: rgba(229,162,41,.035); border: 1px solid rgba(229,162,41,.12);
    border-radius: 12px; padding: 18px 22px;
    font-size: .82rem; color: var(--text2); line-height: 1.7;
    margin-bottom: 1rem;
    position: relative; overflow: hidden;
}}
.warn-box::before {{
    content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px;
    background: var(--amber); border-radius: 3px 0 0 3px;
}}
.warn-box b {{ color: var(--text) }}

/* ── Example box ── */
.example-box {{
    background: rgba(58,123,213,.025);
    border: 1px solid rgba(58,123,213,.1);
    border-left: 3px solid rgba(58,123,213,.3);
    border-radius: 0 10px 10px 0;
    padding: 14px 18px; margin: 10px 0 0;
    font-size: .78rem; font-family: 'IBM Plex Mono'; color: var(--text2);
    line-height: 1.65;
}}
.example-box b {{ color: var(--blue2) }}
.example-box .ex-label {{
    font-size: .56rem; letter-spacing: .12em; text-transform: uppercase;
    color: var(--blue); margin-bottom: 5px; display: block; font-weight: 600;
}}

/* ── Pipeline steps ── */
.step {{
    display: flex; gap: 18px; margin: 10px 0; padding: 20px 24px;
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    transition: border-color .3s, box-shadow .3s;
    position: relative;
}}
.step:hover {{
    border-color: var(--border2);
    box-shadow: 0 3px 20px rgba(0,0,0,.12);
}}
.step::before {{
    content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 2px;
    background: linear-gradient(180deg, rgba(217,74,46,.3), rgba(217,74,46,.05));
    border-radius: 2px;
}}
.step-n {{
    flex-shrink: 0; width: 38px; height: 38px; line-height: 38px; text-align: center;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #fff; font-family: 'IBM Plex Mono'; font-size: .78rem; font-weight: 700;
    border-radius: 10px;
    box-shadow: 0 3px 14px rgba(217,74,46,.25), 0 0 0 3px rgba(217,74,46,.08);
}}
.step-body {{
    flex: 1; font-size: .84rem; color: var(--text2); line-height: 1.7;
}}
.step-body b {{ color: var(--text) }}
.step-body .step-title {{
    font-family: 'DM Sans'; font-size: .94rem; font-weight: 700;
    color: var(--text); margin-bottom: 6px; letter-spacing: -.01em;
}}
.step-body code {{
    background: rgba(58,123,213,.07); color: var(--blue2);
    padding: 3px 8px; border-radius: 5px;
    font-family: 'IBM Plex Mono'; font-size: .72rem;
    border: 1px solid rgba(58,123,213,.1);
}}
.step-stat {{
    display: inline-block; padding: 4px 10px; border-radius: 6px;
    background: rgba(16,185,129,.06); color: var(--teal);
    font-family: 'IBM Plex Mono'; font-size: .65rem; font-weight: 600;
    border: 1px solid rgba(16,185,129,.15); margin: 3px 2px;
    transition: background .3s;
}}
.step-stat:hover {{ background: rgba(16,185,129,.1) }}

/* ── Signal cards ── */
.signal-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px; margin: 10px 0;
    position: relative; overflow: hidden;
    transition: border-color .3s, box-shadow .3s, transform .2s;
}}
.signal-card:hover {{
    border-color: var(--border2);
    box-shadow: 0 6px 28px rgba(0,0,0,.18);
    transform: translateY(-1px);
}}
.signal-card::after {{
    content: ''; position: absolute; top: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle at 100% 0%, rgba(217,74,46,.03), transparent 70%);
    pointer-events: none;
}}
.signal-title {{
    font-family: 'DM Sans'; font-size: .94rem; font-weight: 700;
    color: var(--text); margin-bottom: 8px; letter-spacing: -.01em;
}}
.signal-body {{
    font-size: .82rem; color: var(--text2); line-height: 1.7;
}}
.signal-stats {{
    display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap;
}}
.signal-stat {{
    padding: 7px 14px; border-radius: 8px;
    background: rgba(255,255,255,.02);
    border: 1px solid var(--border);
    font-family: 'IBM Plex Mono'; font-size: .68rem; color: var(--text2);
    transition: background .3s, border-color .3s;
}}
.signal-stat:hover {{
    background: rgba(255,255,255,.04); border-color: var(--border2);
}}
.signal-stat b {{ color: var(--text); font-size: .8rem }}

/* ── Footer ── */
.ft {{
    text-align: center; color: var(--muted);
    font-family: 'IBM Plex Mono'; font-size: .58rem;
    letter-spacing: .06em;
    padding: 2rem 0 .8rem;
    border-top: 1px solid var(--border); margin-top: 2.5rem;
}}
.ft a {{
    color: var(--accent); text-decoration: none;
    transition: color .3s;
}}
.ft a:hover {{ color: var(--accent2) }}

/* ── Hide Streamlit chrome ── */
#MainMenu {{ visibility: hidden }}
footer {{ visibility: hidden }}
header {{ visibility: hidden }}

/* ── Animated fade-in for content ── */
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(12px) }}
    to   {{ opacity: 1; transform: translateY(0) }}
}}
.signal-card, .step, .card, .example-box, .warn-box {{
    animation: slideUp .4s ease-out both;
}}
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
        'what':'Empresa registrada en una CCAA que gana contratos <b>mayoritariamente en otra</b>.',
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

def discover_flags():
    found = {}
    for d, scope in [(DATA, 'Nacional'), (DATA / 'catalunya', 'Catalunya')]:
        if d.exists():
            for f in sorted(d.glob('*.parquet')):
                found[f.stem] = {'path': str(f), 'scope': scope, 'size': f.stat().st_size}
    return found

def get_meta(stem):
    return FLAGS.get(stem, {'label':stem,'short':'?','icon':'📄','badge':'b-blue','scope':'?','color':C['blue'],
        'what':'','why':'','how':'','example':'','stat_empresas':0,'stat_extra':''})

_HIDE = {'empresa_norm','adj_norm','empresa_1','empresa_2','cargo_norm','cargo_upper','cargo_w','organo_norm','same_group','is_fusion_borme'}
_SCORES = {'risk_score','score','score_max','score_sum','par_score','score_total','f6_score','f7_max_conc','cargo_weight','flag_weight','size_penalty','concentracion'}

def clean_df(df):
    return df.drop(columns=[c for c in df.columns if c in _SCORES | _HIDE], errors='ignore')

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
    stages = [('Contratos PLACSP',8_700_000),('Con adjudicatario e importe',5_800_000),('Actos mercantiles BORME',17_100_000),
              ('Empresas cruzadas BORME ∩ PLACSP',126_073),('Con señal de alerta (≥1 flag)',25_675),('Con ≥3 señales acumuladas',125)]
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
    fig = go.Figure(go.Pie(values=[52,48],labels=['Cruzadas con BORME','Sin cruzar'],hole=.65,
        textinfo='label+percent',textposition='outside',textfont=dict(size=11,family='DM Sans',color=C['text2']),
        marker=dict(colors=[C['blue'],C['border2']],line=dict(width=2,color=C['bg'])),
        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'))
    fig.update_layout(**PL,height=300,showlegend=False,
        annotations=[dict(text='<b>52%</b><br>cruzadas',x=.5,y=.5,showarrow=False,font=dict(size=16,color=C['text'],family='IBM Plex Mono'))])
    return fig

def pl_signal_summary():
    signals = [('F9 · Geo discrepancia',14832,C['purple']),('F2 · Capital mínimo',5735,C['amber']),
        ('F1 · Recién creada',5435,C['red']),('F10 · Fraccionamiento',2651,C['red']),('F6 · Red administradores',2684,C['blue']),
        ('F4 · Disolución',1294,C['red']),('F5 · Concursal',540,C['red']),('F7 · Concentración',286,C['teal']),
        ('F11 · Modificaciones',115,C['amber']),('F8 · UTEs vinculadas',97,C['amber'])]
    labels=[s[0] for s in signals]; vals=[s[1] for s in signals]; cols=[s[2] for s in signals]
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

    st.markdown('<div class="sec">De dónde partimos · El embudo de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.6;margin-bottom:12px">
        De <b style="color:{C['text']}">8.7 millones</b> de contratos en PLACSP,
        filtramos los que tienen adjudicatario e importe, cruzamos con <b style="color:{C['text']}">17 millones</b>
        de actos del Registro Mercantil, y aplicamos 11 filtros de detección.</div>""", unsafe_allow_html=True)
    st.plotly_chart(pl_funnel(), use_container_width=True)

    st.markdown('<div class="sec">Cobertura del cruce · Honestidad metodológica</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.5])
    with col_a: st.plotly_chart(pl_coverage(), use_container_width=True)
    with col_b:
        st.markdown(f"""<div style="font-size:.84rem;color:{C['text2']};line-height:1.7;padding:10px 0">
            <b style="color:{C['text']}">No vemos todo.</b> Solo el <b style="color:{C['blue']}">52%</b>
            de adjudicatarios se cruzan con BORME.<br><br>
            El <b>48% restante</b> incluye:<br>
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
                    st.dataframe(clean_df(r['sample']), use_container_width=True, hide_index=True)
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
            flag_sums = {c:int(df[c].sum()) for c in bool_cols if df[c].sum()>0}
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
    df_display = clean_df(df)
    fc1,fc2 = st.columns([1,2])
    with fc1: search_col = st.selectbox("Buscar en", ['(todas)'] + list(df_display.columns), key="exp_col")
    with fc2: search_term = st.text_input("Filtrar", key="exp_term", placeholder="Escribe para filtrar...")
    filtered = df_display.copy()
    if search_term:
        if search_col != '(todas)': filtered = filtered[filtered[search_col].astype(str).str.contains(search_term, case=False, na=False)]
        else:
            mask = pd.Series(False, index=filtered.index)
            for col in filtered.select_dtypes(include=['object']).columns: mask |= filtered[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered = filtered[mask]
        st.caption(f"🔍 {len(filtered):,} de {len(df_display):,}")
    sortable = [c for c in filtered.columns if filtered[c].dtype in ['int64','float64','int32','float32']]
    if sortable:
        sort_col = st.selectbox("Ordenar por", ['(sin ordenar)'] + sortable, key="exp_sort")
        if sort_col != '(sin ordenar)': filtered = filtered.sort_values(sort_col, ascending=False)
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
    st.markdown(f"""<div class="warn-box"><b>Nota:</b> Pipeline de filtros deterministas — no hay modelos de ML.
        Un patrón indica una situación que merece revisión humana, <b>no constituye prueba de irregularidad</b>.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 1 · Obtener los datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">1</div><div class="step-body"><div class="step-title">Descargar 64.000 PDFs del BORME</div>
        BORME-A (Sección Primera: Actos inscritos) publica un PDF diario por provincia desde 2009.
        Descargamos <b>todos</b> — 64.000 documentos, ~25 GB.<br>
        <span class="step-stat">2009–2026</span> <span class="step-stat">64.000 PDFs</span> <span class="step-stat">~25 GB</span></div></div>
    <div class="step"><div class="step-n">2</div><div class="step-body"><div class="step-title">Parsear los PDFs con regex</div>
        Parser de expresiones regulares extrae: <b>empresa, acto, persona, cargo, capital, fecha</b>. Validado contra 300 PDFs.<br>
        <span class="step-stat">17.1M filas</span> <span class="step-stat">3.8M personas</span> <span class="step-stat">2.77M empresas</span></div></div>
    <div class="step"><div class="step-n">3</div><div class="step-body"><div class="step-title">Cargar contratación pública</div>
        <b>PLACSP:</b> 8.7M registros → filtro → <b>5.8M adjudicaciones útiles</b>.
        <b>Catalunya:</b> Registre Públic (~3.4M) + menores BCN (~177K).<br>
        <span class="step-stat">5.8M nacionales</span> <span class="step-stat">3.4M Catalunya</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 2 · Cruzar los datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">4</div><div class="step-body"><div class="step-title">Normalizar nombres</div>
        Cruce por <b>nombre normalizado</b> (no por NIF — no disponible en BORME).
        Pipeline: mayúsculas → eliminar acentos (preservar Ñ) → colapsar formas societarias → limpiar puntuación.<br><br>
        <code>"Construcciones García López, S.L.U. (R.M. Madrid)"</code> → <code>"CONSTRUCCIONES GARCIA LOPEZ"</code><br>
        <span class="step-stat">~5.550 stop words</span> <span class="step-stat">203 curadas</span> <span class="step-stat">5.400 auto-generadas</span></div></div>
    <div class="step"><div class="step-n">5</div><div class="step-body"><div class="step-title">Intersección BORME ∩ Contratación</div>
        Empresas que existen en ambos datasets por nombre normalizado.<br>
        <span class="step-stat">126.073 empresas (Nacional)</span> <span class="step-stat">23.156 (Catalunya)</span> <span class="step-stat">52% de PLACSP</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 3 · Señales individuales (F1–F5)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">6</div><div class="step-body"><div class="step-title">Señales por empresa</div>
        <b>F1 · Recién creada:</b> Constitución → 1ª adjudicación < 180 días → <span class="step-stat">5.435 empresas</span><br><br>
        <b>F2 · Capital mínimo:</b> Capital < 10K€ y adjudicación > 100K€ → <span class="step-stat">5.735 empresas</span><br><br>
        <b>F4 · Disolución:</b> Acto disolución + adjudicación en 0–365 días → <span class="step-stat">1.294 empresas</span><br><br>
        <b>F5 · Concursal:</b> Acto concursal + adjudicaciones posteriores → <span class="step-stat">540 empresas</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 4 · Detectar redes (F6)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">7</div><div class="step-body"><div class="step-title">Cargos vigentes</div>
        17.1M actos → último acto por (persona, empresa, cargo). Nombramiento → vigente. Cese → inactivo.
        Filtro: solo cargos de decisión. Excluir personas jurídicas.<br>
        <span class="step-stat">618K → 232K → 212K cargos activos</span></div></div>
    <div class="step"><div class="step-n">8</div><div class="step-body"><div class="step-title">Pares sospechosos</div>
        Personas con 2–50 empresas adjudicatarias → pares con <b>≥2 órganos comunes</b>.<br>
        <span class="step-stat">7.514 personas</span> <span class="step-stat">3.970 pares</span></div></div>
    <div class="step"><div class="step-n">9</div><div class="step-body"><div class="step-title">Filtrar grupos corporativos</div>
        <b>a)</b> Nombre de marca: Jaccard ≥0.5 → grupo.
        <b>b)</b> Consejo: >40% overlap + ≥3 personas → grupo.
        <b>c)</b> Fusiones BORME → grupo.<br>
        <span class="step-stat">3.970 → 2.287 pares</span> <span class="step-stat">1.683 eliminados</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 5 · Señales adicionales (F7–F11)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">10</div><div class="step-body"><div class="step-title">F7, F8, F9 (Nacional + CAT)</div>
        <b>F7:</b> >40% adj de un órgano → <span class="step-stat">286 empresas</span>
        <b>F8:</b> UTEs con admin compartido → <span class="step-stat">127 pares</span>
        <b>F9:</b> CCAA registro ≠ CCAA contratos → <span class="step-stat">14.832 empresas</span></div></div>
    <div class="step"><div class="step-n">11</div><div class="step-body"><div class="step-title">F10, F11 (Catalunya)</div>
        <b>F10:</b> Troceo: ≥3 contratos ≤15K€ en 90 días, suma > umbral → <span class="step-stat">2.651 empresas</span><br>
        <b>F11:</b> Modificaciones ≥20% (media: 0.57%) → <span class="step-stat">115 empresas</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Paso 6 · Consolidar</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step"><div class="step-n">12</div><div class="step-body"><div class="step-title">Listado final</div>
        Unión de F1–F11 por empresa. Cada empresa recibe un vector binario de señales activas.
        No hay scoring numérico — solo <b>qué señales tiene y cuántas</b>.<br>
        <span class="step-stat">Nacional: 25.675 con ≥1</span> <span class="step-stat">125 con ≥3</span>
        <span class="step-stat">Catalunya: 4.203 con ≥1</span></div></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Diferencias Nacional vs Catalunya</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="card card-l card-blue">
        <b>Datos:</b> Nacional 5.8M adj · Catalunya 3.4M + 177K menores<br>
        <b>Matching:</b> Nacional 126K · Catalunya 23K<br>
        <b>F7:</b> Nacional umbral fijo 40% · Catalunya adaptativo 20/30/40%<br>
        <b>Solo Nacional:</b> F9 geo · <b>Solo Catalunya:</b> F10 troceo, F11 modificaciones
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Limitaciones</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="card card-l card-amber">
        <b>Cobertura:</b> 52% cruzados. Autónomos, personas físicas y extranjeras no figuran en BORME.<br><br>
        <b>Matching por nombre:</b> No por NIF. Posibles homónimos y variantes no capturadas.<br><br>
        <b>Vigencia cargos:</b> Si el cese no se publica, el cargo aparece vigente.<br><br>
        <b>Grupos corporativos:</b> Filtros heurísticos. Holdings complejos pueden escapar.<br><br>
        <b>Señal ≠ fraude.</b> Requiere investigación humana cualificada.
    </div>""", unsafe_allow_html=True)


# ═══════════════ MAIN ═══════════════
def main():
    st.markdown("""
    <div class="hero">
        <h1>🏛️ Contratación <span>Pública</span></h1>
        <p class="mono">BQUANT FINANCE · @GSNCHEZ</p>
        <div class="hero-desc">
            Cruzamos <b>8.7 millones de contratos públicos</b> con <b>17 millones de actos
            del Registro Mercantil</b> para detectar patrones que merecen atención.
        </div>
    </div><div class="divider"></div>
    """, unsafe_allow_html=True)
    flag_files = discover_flags()
    tabs = st.tabs(["📊 Resumen", "🔎 Explorar señales", "📋 Cómo funciona"])
    with tabs[0]: render_resumen(flag_files)
    with tabs[1]: render_explorar(flag_files)
    with tabs[2]: render_metodo()
    st.markdown("""<div class="ft"><a href="https://twitter.com/Gsnchez">@Gsnchez</a> · <a href="https://bquantfinance.com">bquantfinance.com</a> · <a href="https://github.com/BquantFinance">GitHub</a></div>""", unsafe_allow_html=True)

if __name__ == "__main__": main()
