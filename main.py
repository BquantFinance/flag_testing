"""
═══════════════════════════════════════════════════════════════════════
  CONTRATACIÓN PÚBLICA ESPAÑA
  Calidad de datos · Red flags BORME × Contratación · Metodología
  BQuant Finance · @Gsnchez · bquantfinance.com
═══════════════════════════════════════════════════════════════════════

Repo: github.com/BquantFinance/contratacion-flags
Deploy: Streamlit Cloud

Datos:
  data/quality/placsp_profile.json    ← precomputado con precompute_quality.py
  data/quality/cat_profile.json       ← precomputado con precompute_quality.py
  data/nacional/*.parquet             ← flags generados por explore_flags.py
  data/catalunya/*.parquet            ← flags generados por explore_flags_cat.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')
import streamlit.components.v1 as components

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Contratación Pública · BQuant", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="collapsed")

DATA = Path("anomalias")
Q_DIR = DATA / "quality"
NAC_DIR = DATA
CAT_DIR = DATA / "catalunya"

# ── Color System ──
C = {
    'bg':       '#050609',
    'bg2':      '#0a0c12',
    'card':     '#0d1017',
    'card2':    '#11151e',
    'border':   '#1a1f2e',
    'border2':  '#252b3d',
    'accent':   '#ff4d35',
    'accent2':  '#3b82f6',
    'accent3':  '#10b981',
    'accent4':  '#f59e0b',
    'accent5':  '#8b5cf6',
    'accent6':  '#ec4899',
    'text':     '#e2e8f0',
    'text2':    '#94a3b8',
    'muted':    '#64748b',
    'grid':     'rgba(255,255,255,0.03)',
    'good':     '#10b981',
    'warn':     '#f59e0b',
    'bad':      '#ef4444',
    'glow_red': 'rgba(255,77,53,.35)',
    'glow_blue':'rgba(59,130,246,.35)',
}

PL = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono, Fira Code, monospace', color=C['text'], size=11),
    margin=dict(l=50, r=30, t=50, b=40),
    hoverlabel=dict(bgcolor='rgba(13,16,23,0.97)', bordercolor=C['border2'],
                    font=dict(color=C['text'], size=11))
)

# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after {{ scrollbar-width: thin; scrollbar-color: {C['border']} transparent }}
.stApp {{
    background: {C['bg']};
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 0%, rgba(59,130,246,.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 100%, rgba(255,77,53,.03) 0%, transparent 60%);
    color: {C['text']};
    font-family: 'Outfit', sans-serif;
}}
section[data-testid="stSidebar"] {{ background: {C['card']}; border-right: 1px solid {C['border']} }}

.stTabs [data-baseweb="tab-list"] {{ gap:0; border-bottom:1px solid {C['border']} }}
.stTabs [data-baseweb="tab"] {{
    background:transparent; color:{C['muted']}; border:none; padding:12px 22px;
    font-family:'JetBrains Mono',monospace; font-size:.7rem; letter-spacing:.1em;
    text-transform:uppercase; transition:all .3s cubic-bezier(.4,0,.2,1);
}}
.stTabs [data-baseweb="tab"]:hover {{ color:{C['text2']} }}
.stTabs [aria-selected="true"] {{
    color:{C['accent']}!important; border-bottom:2px solid {C['accent']}!important;
    text-shadow:0 0 20px {C['glow_red']};
}}

div[data-testid="stMetric"] {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:8px;
    padding:14px 18px; transition:all .3s; position:relative; overflow:hidden;
}}
div[data-testid="stMetric"]::before {{
    content:''; position:absolute; top:0;left:0;right:0; height:1px;
    background:linear-gradient(90deg,transparent,{C['accent2']},transparent); opacity:.4;
}}
div[data-testid="stMetric"]:hover {{ border-color:{C['border2']}; box-shadow:0 4px 20px rgba(0,0,0,.3) }}
div[data-testid="stMetric"] label {{
    color:{C['muted']}!important; font-family:'JetBrains Mono',monospace;
    font-size:.6rem!important; letter-spacing:.1em; text-transform:uppercase;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color:{C['text']}!important; font-family:'JetBrains Mono',monospace;
    font-size:1.25rem!important; font-weight:600;
}}

div[data-testid="stExpander"] {{ background:{C['card']}!important; border:1px solid {C['border']}!important; border-radius:8px!important }}

.hero {{ text-align:center; padding:2.5rem 0 1rem; position:relative }}
.hero-title {{
    font-family:'Outfit',sans-serif; font-size:2.2rem; font-weight:800;
    color:{C['text']}; letter-spacing:-.04em; line-height:1.1; margin-bottom:.4rem;
}}
.hero-title span {{
    background:linear-gradient(135deg,{C['accent']},{C['accent4']});
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.hero-sub {{
    font-family:'JetBrains Mono',monospace; font-size:.65rem; color:{C['muted']};
    letter-spacing:.2em; text-transform:uppercase; margin-bottom:.4rem;
}}
.hero-context {{
    font-family:'Outfit',sans-serif; font-size:.92rem; color:{C['text2']};
    max-width:700px; margin:0 auto; line-height:1.6; padding:0 1rem;
}}
.hero-context b {{ color:{C['text']} }}
.hero-line {{ height:1px; background:linear-gradient(90deg,transparent,{C['border2']},transparent); margin:1.5rem auto; max-width:500px }}

.intro-q {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:10px;
    padding:20px 24px; margin:8px 0; font-size:.84rem; color:{C['text']};
    line-height:1.7; position:relative; overflow:hidden;
}}
.intro-q::before {{
    content:''; position:absolute; top:0;left:0;bottom:0; width:3px;
    background:linear-gradient(180deg,{C['accent']},{C['accent4']});
}}
.intro-q b {{ color:{C['accent']} }}
.intro-q .iq-icon {{ font-size:1.1rem; margin-right:8px }}

.sec {{
    font-family:'JetBrains Mono',monospace; font-size:.72rem; font-weight:600; color:{C['accent']};
    letter-spacing:.1em; text-transform:uppercase; border-bottom:1px solid {C['border']};
    padding-bottom:8px; margin:2rem 0 1.2rem; position:relative;
}}
.sec::after {{ content:''; position:absolute; bottom:-1px; left:0; width:40px; height:1px; background:{C['accent']} }}

.mc {{
    background:{C['card']}; border:1px solid {C['border']}; border-left:3px solid {C['accent2']};
    border-radius:0 8px 8px 0; padding:18px 22px; margin:10px 0; font-size:.82rem;
    line-height:1.75; color:{C['text']}; transition:border-color .3s;
}}
.mc:hover {{ border-left-color:{C['accent']} }}
.mc code {{ background:rgba(59,130,246,.1); color:{C['accent2']}; padding:2px 7px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:.74rem }}
.mc strong {{ color:#f1f5f9 }}
.mc-acc {{ border-left-color:{C['accent']} }}
.mc-grn {{ border-left-color:{C['good']} }}
.mc-wrn {{ border-left-color:{C['warn']} }}

.qg {{ display:inline-block; padding:3px 10px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:.64rem; font-weight:600; letter-spacing:.05em }}
.qg-ok {{ background:rgba(16,185,129,.1); color:{C['good']}; border:1px solid rgba(16,185,129,.2) }}
.qg-wn {{ background:rgba(245,158,11,.1); color:{C['warn']}; border:1px solid rgba(245,158,11,.2) }}
.qg-bd {{ background:rgba(239,68,68,.1); color:{C['bad']}; border:1px solid rgba(239,68,68,.2) }}

.disc {{ background:rgba(245,158,11,.04); border:1px solid rgba(245,158,11,.12); border-radius:8px; padding:16px 20px; font-size:.78rem; color:{C['text2']}; line-height:1.7; margin-bottom:1.5rem }}
.fcard {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:8px;
    padding:18px 22px; margin:8px 0; transition:all .3s; position:relative; overflow:hidden;
}}
.fcard:hover {{ border-color:{C['border2']}; box-shadow:0 8px 30px rgba(0,0,0,.25) }}
.fcard::after {{ content:''; position:absolute; top:0;right:0; width:80px;height:80px; background:radial-gradient(circle,rgba(59,130,246,.05),transparent 70%) }}

.ft {{ text-align:center; color:{C['muted']}; font-family:'JetBrains Mono',monospace; font-size:.64rem; letter-spacing:.05em; padding:2rem 0 1rem; border-top:1px solid {C['border']}; margin-top:3rem }}
.ft a {{ color:{C['accent']}; text-decoration:none; transition:color .2s }}
.ft a:hover {{ color:{C['accent4']} }}

.step-num {{
    display:inline-block; background:linear-gradient(135deg,{C['accent']},{C['accent4']}); color:#fff;
    font-family:'JetBrains Mono',monospace; font-size:.72rem; font-weight:700;
    width:26px;height:26px;line-height:26px; text-align:center; border-radius:6px;
    margin-right:10px; box-shadow:0 2px 10px {C['glow_red']};
}}
.formula {{
    background:rgba(139,92,246,.05); border:1px solid rgba(139,92,246,.12); border-radius:8px;
    padding:14px 18px; font-family:'JetBrains Mono',monospace; font-size:.72rem;
    color:{C['accent5']}; line-height:1.8; margin:10px 0;
}}
.fb {{
    display:inline-block; padding:3px 10px; border-radius:4px; font-family:'JetBrains Mono',monospace;
    font-size:.62rem; font-weight:600; margin:2px 3px; letter-spacing:.03em; transition:all .2s;
}}
.fb:hover {{ transform:translateY(-1px) }}
.fb-r {{ background:rgba(239,68,68,.1); color:{C['bad']}; border:1px solid rgba(239,68,68,.2) }}
.fb-w {{ background:rgba(245,158,11,.1); color:{C['warn']}; border:1px solid rgba(245,158,11,.2) }}
.fb-b {{ background:rgba(59,130,246,.1); color:{C['accent2']}; border:1px solid rgba(59,130,246,.2) }}
.fb-g {{ background:rgba(16,185,129,.1); color:{C['good']}; border:1px solid rgba(16,185,129,.2) }}
.fb-p {{ background:rgba(139,92,246,.1); color:{C['accent5']}; border:1px solid rgba(139,92,246,.2) }}

.graph-caption {{
    text-align:center; font-family:'JetBrains Mono',monospace; font-size:.6rem;
    color:{C['muted']}; letter-spacing:.1em; text-transform:uppercase; margin-top:-8px; padding-bottom:8px;
}}
.graph-caption span {{ color:{C['accent']} }}

#MainMenu {{ visibility:hidden }} footer {{ visibility:hidden }} header {{ visibility:hidden }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def fmt(n):
    if n >= 1e9: return f"{n/1e9:.1f}B"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.0f}K"
    return str(int(n))

def qb(p):
    if p >= 90: return f'<span class="qg qg-ok">{p:.1f}%</span>'
    if p >= 60: return f'<span class="qg qg-wn">{p:.1f}%</span>'
    return f'<span class="qg qg-bd">{p:.1f}%</span>'

@st.cache_data(show_spinner=False)
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

@st.cache_data(show_spinner=False)
def load_pq(path):
    return pd.read_parquet(path)

def discover_flags():
    flags = {}
    for d, scope in [(NAC_DIR, 'Nacional'), (CAT_DIR, 'Catalunya')]:
        if d.exists():
            for f in sorted(d.glob('*.parquet')):
                flags[f.stem] = {'path': str(f), 'scope': scope, 'size': f.stat().st_size}
    return flags

FLAG_INFO = {
    # F1–F5 individual flags
    'flag1_recien_creada':     {'label':'Empresa recién creada',              'icon':'🆕', 'css':'fb-r',  'short':'F1'},
    'flag2_capital_ridiculo':  {'label':'Capital social mínimo',              'icon':'💰', 'css':'fb-w',  'short':'F2'},
    'flag3_multi_admin':       {'label':'Cambios frecuentes de administrador','icon':'👥', 'css':'fb-p',  'short':'F3'},
    'flag4_disolucion':        {'label':'Empresa en disolución',              'icon':'💀', 'css':'fb-r',  'short':'F4'},
    'flag5_concursal':         {'label':'Empresa en concurso de acreedores',  'icon':'⚖️', 'css':'fb-r',  'short':'F5'},
    # F6 network
    'flag6_admin_network':     {'label':'Administrador compartido (detalle)', 'icon':'🕸️', 'css':'fb-b',  'short':'F6'},
    'flag6_admin_network_cat': {'label':'Administrador compartido CAT',       'icon':'🕸️', 'css':'fb-b',  'short':'F6'},
    'flag6_pares_unicos':      {'label':'Pares de empresas sospechosos',      'icon':'🔗', 'css':'fb-b',  'short':'F6'},
    'flag6_pares_cat':         {'label':'Pares sospechosos CAT',              'icon':'🔗', 'css':'fb-b',  'short':'F6'},
    'flag6_personas_resumen':  {'label':'Personas con más conexiones',        'icon':'👤', 'css':'fb-b',  'short':'F6'},
    'flag6_personas_cat':      {'label':'Personas con más conexiones CAT',    'icon':'👤', 'css':'fb-b',  'short':'F6'},
    # F7–F11
    'flag7_concentracion':     {'label':'Empresa dominante en un órgano',     'icon':'🎯', 'css':'fb-g',  'short':'F7'},
    'flag7_concentracion_cat': {'label':'Empresa dominante en órgano CAT',    'icon':'🎯', 'css':'fb-g',  'short':'F7'},
    'flag8_utes_sospechosas':  {'label':'UTEs con miembros vinculados',       'icon':'🤝', 'css':'fb-w',  'short':'F8'},
    'flag8_utes_cat':          {'label':'UTEs con miembros vinculados CAT',   'icon':'🤝', 'css':'fb-w',  'short':'F8'},
    'flag9_geo_discrepancia':  {'label':'Empresa lejos de donde contrata',    'icon':'📍', 'css':'fb-p',  'short':'F9'},
    'flag10_troceo_cat':       {'label':'Posible fraccionamiento de contratos','icon':'✂️','css':'fb-r',  'short':'F10'},
    'flag11_modificaciones_cat':{'label':'Modificaciones contractuales excesivas','icon':'📝','css':'fb-w','short':'F11'},
    # Scoring & grupos
    'risk_scoring_unificado':  {'label':'Scoring de riesgo unificado',        'icon':'📊', 'css':'fb-r',  'short':'Risk'},
    'risk_scoring_cat':        {'label':'Scoring de riesgo CAT',              'icon':'📊', 'css':'fb-r',  'short':'Risk'},
    'grupos_corporativos':     {'label':'Grupos corporativos (filtrados)',     'icon':'🏢', 'css':'fb-b',  'short':'Grp'},
    'grupos_corporativos_cat': {'label':'Grupos corporativos CAT',            'icon':'🏢', 'css':'fb-b',  'short':'Grp'},
}

def get_flag_meta(stem):
    return FLAG_INFO.get(stem, {'label':stem, 'icon':'📄', 'css':'fb-b', 'short':'?'})


# ═══════════════════════════════════════════════════════════════
# PLOTS — precomputed JSON
# ═══════════════════════════════════════════════════════════════
def pl_missing_from_json(missing_dict, mx=40):
    mp = pd.Series(missing_dict).sort_values(ascending=True)
    mp = mp[mp > 0]
    if len(mp) == 0: return None
    if len(mp) > mx: mp = mp.tail(mx)
    cols = [C['good'] if v < 5 else C['warn'] if v < 50 else C['bad'] for v in mp.values]
    fig = go.Figure(go.Bar(y=mp.index, x=mp.values, orientation='h',
        marker=dict(color=cols, line=dict(width=0)),
        hovertemplate='<b>%{y}</b><br>%{x:.1f}%<extra></extra>'))
    fig.update_layout(**PL, height=max(250, len(mp)*22),
        title=dict(text='<b>% Missing por columna</b>', font=dict(size=13), x=0),
        xaxis=dict(gridcolor=C['grid'], range=[0, 100]), yaxis=dict(tickfont=dict(size=9)))
    return fig

def pl_radar_from_json(radar_dict):
    if len(radar_dict) < 3: return None
    labs = [k[:22] for k in radar_dict.keys()]; vals = list(radar_dict.values())
    fig = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=labs+[labs[0]], fill='toself',
        fillcolor='rgba(59,130,246,.08)', line=dict(color=C['accent2'], width=2), marker=dict(size=4)))
    fig.update_layout(**PL, height=380,
        title=dict(text='<b>Completitud campos clave</b>', font=dict(size=13), x=0),
        polar=dict(bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor=C['grid'], tickfont=dict(size=8, color=C['muted'])),
            angularaxis=dict(gridcolor=C['grid'], tickfont=dict(size=9, color=C['muted']))))
    return fig

def pl_temporal_from_json(temp_data, col):
    if col not in temp_data: return None
    d = temp_data[col]
    months = pd.to_datetime([m.replace('-','') if '-' not in m else m for m in d['months']], format='mixed', errors='coerce')
    fig = go.Figure(go.Bar(x=months, y=d['counts'],
        marker=dict(color=C['accent2'], opacity=.85, line=dict(width=0)),
        hovertemplate='<b>%{x|%Y-%m}</b><br>%{y:,.0f}<extra></extra>'))
    fig.update_layout(**PL, height=300,
        title=dict(text=f'<b>Temporal</b> · {col}', font=dict(size=13), x=0),
        xaxis=dict(gridcolor=C['grid']), yaxis=dict(title='Registros', gridcolor=C['grid']), bargap=.05)
    return fig

def pl_amounts_from_json(amt_data, col):
    if col not in amt_data or 'hist_counts' not in amt_data[col]: return None
    d = amt_data[col]; edges = d['hist_edges']
    centers = [(edges[i]+edges[i+1])/2 for i in range(len(edges)-1)]
    fig = go.Figure(go.Bar(x=centers, y=d['hist_counts'],
        marker=dict(color=C['accent3'], opacity=.85, line=dict(width=0)), width=(edges[1]-edges[0])*0.95))
    for val, lab in [(3,'1K€'),(4,'10K€'),(5,'100K€'),(6,'1M€'),(7,'10M€')]:
        if edges[0] <= val <= edges[-1]:
            fig.add_vline(x=val, line=dict(color=C['muted'], width=1, dash='dot'),
                annotation=dict(text=lab, font=dict(size=9, color=C['muted']), yshift=10))
    fig.update_layout(**PL, height=300,
        title=dict(text=f'<b>Importes</b> · {col} (log₁₀)', font=dict(size=13), x=0),
        xaxis=dict(title='log₁₀(€)', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.02)
    return fig

def pl_category_from_json(cat_data, col):
    if col not in cat_data: return None
    d = cat_data[col]; vals = d['values'][:15]; counts = d['counts'][:15]
    fig = go.Figure(go.Bar(y=[str(v)[:50] for v in reversed(vals)], x=list(reversed(counts)), orientation='h',
        marker=dict(color=C['accent2'], opacity=.85, line=dict(width=0)),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>'))
    fig.update_layout(**PL, height=max(280, len(vals)*26),
        title=dict(text=f'<b>{col}</b> · Top {len(vals)}', font=dict(size=13), x=0),
        xaxis=dict(gridcolor=C['grid']), yaxis=dict(tickfont=dict(size=9)))
    return fig


# ═══════════════════════════════════════════════════════════════
# PLOTS — DataFrames (flags)
# ═══════════════════════════════════════════════════════════════
def pl_score(df, sc, title, clr=None):
    v = df[sc].dropna()
    if len(v) == 0: return None
    fig = go.Figure(go.Histogram(x=v, nbinsx=50,
        marker=dict(color=clr or C['accent'], opacity=.85, line=dict(width=0)),
        hovertemplate='Score %{x:.2f}<br>%{y:,.0f}<extra></extra>'))
    fig.update_layout(**PL, height=280,
        title=dict(text=f'<b>{title}</b>', font=dict(size=13), x=0),
        xaxis=dict(title='Score', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
    return fig

def pl_amt_df(df, col, color=None):
    v = df[col].dropna(); v = v[v > 0]
    if len(v) == 0: return None
    lv = np.log10(v.clip(lower=1))
    fig = go.Figure(go.Histogram(x=lv, nbinsx=80,
        marker=dict(color=color or C['accent3'], opacity=.85, line=dict(width=0))))
    for val, lab in [(3,'1K€'),(4,'10K€'),(5,'100K€'),(6,'1M€'),(7,'10M€')]:
        if lv.min() <= val <= lv.max():
            fig.add_vline(x=val, line=dict(color=C['muted'], width=1, dash='dot'),
                annotation=dict(text=lab, font=dict(size=9, color=C['muted']), yshift=10))
    fig.update_layout(**PL, height=300,
        title=dict(text=f'<b>Importes</b> · {col} (log₁₀)', font=dict(size=13), x=0),
        xaxis=dict(title='log₁₀(€)', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.02)
    return fig

def pl_f6_bubble(df):
    sc = next((c for c in ['par_score','score_max','score'] if c in df.columns), None)
    conc = 'concentracion' if 'concentracion' in df.columns else None
    imp = next((c for c in ['importe_par','importe_e1'] if c in df.columns), None)
    nfl = 'n_flags' if 'n_flags' in df.columns else None
    if not sc or not conc: return None
    dv = df.head(500).copy()
    size_vals = np.sqrt(dv[imp]/1e3).clip(lower=3, upper=50) if imp else 8
    color_vals = dv[nfl] if nfl else 0
    hover = [f"{str(r.get('empresa_1',''))[:35]}<br>× {str(r.get('empresa_2',''))[:35]}<br>Score: {r[sc]:.1f}" for _, r in dv.iterrows()]
    fig = go.Figure(go.Scatter(x=dv[conc], y=dv[sc], mode='markers',
        marker=dict(size=size_vals, color=color_vals,
            colorscale=[[0,'rgba(59,130,246,.7)'],[0.5,'rgba(245,158,11,.8)'],[1,'rgba(239,68,68,.9)']],
            showscale=True, colorbar=dict(title='Flags', thickness=12, len=.5, tickfont=dict(size=9, color=C['muted'])),
            line=dict(width=.5, color='rgba(255,255,255,.08)')),
        hovertext=hover, hoverinfo='text'))
    fig.update_layout(**PL, height=450,
        title=dict(text='<b>Pares F6</b> · Concentración vs Score', font=dict(size=13), x=0),
        xaxis=dict(title='Concentración', gridcolor=C['grid']), yaxis=dict(title='ParScore', gridcolor=C['grid']))
    return fig


# ═══════════════════════════════════════════════════════════════
# EGO-NETWORK — D3.js interactive radial graph
# ═══════════════════════════════════════════════════════════════
def _fcol(df, *hints):
    """Find first column matching any hint substring."""
    for h in hints:
        for c in df.columns:
            if h in c.lower(): return c
    return None

def build_ego_data(df_pares, persona_name):
    """Build ego-network graph data for a person."""
    e1c = _fcol(df_pares, 'empresa_1'); e2c = _fcol(df_pares, 'empresa_2')
    if not e1c or not e2c: return None
    # Find rows involving this person
    mask = pd.Series(False, index=df_pares.index)
    safe = persona_name.replace('(','\\(').replace(')','\\)')
    for col in df_pares.select_dtypes(include=['object']).columns:
        mask |= df_pares[col].astype(str).str.contains(safe, case=False, na=False, regex=True)
    ego = df_pares[mask]
    if len(ego) == 0: return None

    companies = {}
    for _, r in ego.iterrows():
        for ec, ac, ic in [(e1c,'adj_e1','importe_e1'),(e2c,'adj_e2','importe_e2')]:
            nm = str(r[ec])[:35]
            if nm not in companies:
                ac_c = _fcol(df_pares, ac); ic_c = _fcol(df_pares, ic)
                nf_c = _fcol(df_pares, 'n_flags')
                companies[nm] = {
                    'adj': int(r[ac_c]) if ac_c and pd.notna(r.get(ac_c)) else 0,
                    'imp': float(r[ic_c]) if ic_c and pd.notna(r.get(ic_c)) else 0,
                    'flags': int(r[nf_c]) if nf_c and pd.notna(r.get(nf_c)) else 0,
                }
    nodes = [{'id': persona_name[:30], 'type': 'person', 'flags': 0, 'adj': 0, 'imp': 0}]
    for nm, info in companies.items():
        nodes.append({'id': nm, 'type': 'company', **info})
    links = []
    for nm in companies:
        links.append({'source': persona_name[:30], 'target': nm, 'type': 'admin', 'score': 0, 'organos': 0, 'flags': 0})
    sc_c = _fcol(df_pares, 'par_score','score_max'); org_c = _fcol(df_pares, 'n_organos','organos_comunes')
    nf_c2 = _fcol(df_pares, 'n_flags')
    for _, r in ego.iterrows():
        links.append({
            'source': str(r[e1c])[:35], 'target': str(r[e2c])[:35], 'type': 'overlap',
            'score': float(r[sc_c]) if sc_c and pd.notna(r.get(sc_c)) else 0,
            'organos': int(r[org_c]) if org_c and pd.notna(r.get(org_c)) else 1,
            'flags': int(r[nf_c2]) if nf_c2 and pd.notna(r.get(nf_c2)) else 0,
        })
    return {'nodes': nodes, 'links': links, 'persona': persona_name}

def ego_d3_html(data, width=920, height=600):
    """Generate D3.js HTML for ego-network with SVG glows."""
    data_json = json.dumps(data, ensure_ascii=False)
    persona_disp = data.get('persona','')[:40]
    n_co = len(data['nodes']) - 1
    html = _EGO_HTML_TEMPLATE
    html = html.replace('__DATA__', data_json)
    html = html.replace('__W__', str(width)).replace('__H__', str(height))
    html = html.replace('__PERSONA__', persona_disp)
    html = html.replace('__NCO__', str(n_co))
    return html

_EGO_HTML_TEMPLATE = r"""<!DOCTYPE html><html><head><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:transparent;overflow:hidden;font-family:'JetBrains Mono',monospace}
.tt{position:absolute;background:rgba(13,16,23,.96);border:1px solid rgba(37,43,61,.8);border-radius:8px;
  padding:10px 14px;font-size:11px;color:#e2e8f0;pointer-events:none;opacity:0;transition:opacity .2s;
  max-width:280px;backdrop-filter:blur(10px);box-shadow:0 8px 32px rgba(0,0,0,.5)}
.tt b{color:#fbbf24} .tt .m{color:#3b82f6}
.lg{position:absolute;bottom:10px;right:14px;font-size:9px;color:#64748b;letter-spacing:.05em}
.li{display:flex;align-items:center;gap:6px;margin:3px 0}
.ld{width:8px;height:8px;border-radius:50%}
.hd{position:absolute;top:10px;left:16px;font-size:13px;font-weight:600;color:#e2e8f0;letter-spacing:-.01em}
.hd span{color:#fbbf24;text-shadow:0 0 20px rgba(245,158,11,.3)}
.sd{position:absolute;top:30px;left:16px;font-size:9px;color:#64748b;letter-spacing:.08em;text-transform:uppercase}
</style></head><body>
<div class="hd"><span>●</span> __PERSONA__</div>
<div class="sd">__NCO__ empresas · Drag para mover · Hover para detalles</div>
<div id="g"></div>
<div class="lg">
<div class="li"><div class="ld" style="background:#fbbf24;box-shadow:0 0 8px rgba(245,158,11,.5)"></div>Persona</div>
<div class="li"><div class="ld" style="background:#3b82f6;box-shadow:0 0 6px rgba(59,130,246,.4)"></div>Sin flags</div>
<div class="li"><div class="ld" style="background:#f59e0b"></div>1 flag</div>
<div class="li"><div class="ld" style="background:#ef4444;box-shadow:0 0 6px rgba(239,68,68,.4)"></div>2+ flags</div>
<div class="li" style="margin-top:5px;border-top:1px solid rgba(255,255,255,.05);padding-top:4px">
<div style="width:18px;height:1px;background:rgba(245,158,11,.5);border-top:1px dashed rgba(245,158,11,.5)"></div>Admin</div>
<div class="li"><div style="width:18px;height:2px;background:rgba(59,130,246,.5)"></div>Órganos comunes</div>
</div>
<div class="tt" id="tt"></div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data=__DATA__,W=__W__,H=__H__;
const svg=d3.select("#g").append("svg").attr("width",W).attr("height",H);
const defs=svg.append("defs");
[{id:'gb',c:'59,130,246',s:4},{id:'gr',c:'239,68,68',s:5},{id:'gg',c:'245,158,11',s:8},{id:'gl',c:'245,158,11',s:18}]
.forEach(g=>{const f=defs.append("filter").attr("id",g.id).attr("x","-80%").attr("y","-80%").attr("width","260%").attr("height","260%");
f.append("feGaussianBlur").attr("in","SourceGraphic").attr("stdDeviation",g.s).attr("result","b");
const m=f.append("feMerge");m.append("feMergeNode").attr("in","b");m.append("feMergeNode").attr("in","SourceGraphic")});
const rg=defs.append("radialGradient").attr("id","pg");
rg.append("stop").attr("offset","0%").attr("stop-color","#fbbf24");
rg.append("stop").attr("offset","100%").attr("stop-color","#b45309");
const nodes=data.nodes.map(d=>({...d})),links=data.links.map(d=>({...d}));
const pn=nodes.find(n=>n.type==='person');if(pn){pn.fx=W/2;pn.fy=H/2}
const sim=d3.forceSimulation(nodes)
.force("link",d3.forceLink(links).id(d=>d.id).distance(d=>d.type==='admin'?150:200))
.force("charge",d3.forceManyBody().strength(-500))
.force("center",d3.forceCenter(W/2,H/2))
.force("collision",d3.forceCollide().radius(40))
.force("x",d3.forceX(W/2).strength(.04)).force("y",d3.forceY(H/2).strength(.04));
const lk=svg.append("g").selectAll("line").data(links).join("line")
.attr("stroke",d=>d.type==='admin'?'rgba(245,158,11,.22)':d.flags>=2?'rgba(239,68,68,.35)':'rgba(59,130,246,.28)')
.attr("stroke-width",d=>d.type==='admin'?1:Math.max(1.5,Math.min(5,(d.organos||1)/2)))
.attr("stroke-dasharray",d=>d.type==='admin'?'5,5':'none');
const gl2=svg.append("g").selectAll("circle").data(nodes).join("circle")
.attr("r",d=>d.type==='person'?42:20)
.attr("fill",d=>d.type==='person'?'rgba(245,158,11,.06)':d.flags>=2?'rgba(239,68,68,.05)':'rgba(59,130,246,.04)')
.attr("filter",d=>d.type==='person'?'url(#gl)':d.flags>=2?'url(#gr)':'url(#gb)');
const gl1=svg.append("g").selectAll("circle").data(nodes).join("circle")
.attr("r",d=>d.type==='person'?28:14)
.attr("fill",d=>d.type==='person'?'rgba(245,158,11,.15)':d.flags>=2?'rgba(239,68,68,.12)':'rgba(59,130,246,.1)')
.attr("filter",d=>d.type==='person'?'url(#gg)':d.flags>=2?'url(#gr)':'url(#gb)');
const nd=svg.append("g").selectAll("circle").data(nodes).join("circle")
.attr("r",d=>d.type==='person'?20:Math.max(8,Math.min(16,6+Math.sqrt(d.adj||1)*.7)))
.attr("fill",d=>d.type==='person'?'url(#pg)':d.flags>=2?'#ef4444':d.flags===1?'#f59e0b':'#3b82f6')
.attr("stroke",d=>d.type==='person'?'#fbbf24':'rgba(255,255,255,.12)')
.attr("stroke-width",d=>d.type==='person'?2:1)
.attr("filter",d=>d.type==='person'?'url(#gg)':d.flags>=2?'url(#gr)':'url(#gb)')
.style("cursor","grab")
.call(d3.drag()
.on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y})
.on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y})
.on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);if(d.type!=='person'){d.fx=null;d.fy=null}}));
const cr=svg.append("g").selectAll("circle").data(nodes).join("circle")
.attr("r",d=>d.type==='person'?5:2.5).attr("fill","rgba(255,255,255,.6)").attr("pointer-events","none");
const lb=svg.append("g").selectAll("text").data(nodes).join("text")
.text(d=>d.id.substring(0,d.type==='person'?25:20))
.attr("font-size",d=>d.type==='person'?11:8)
.attr("fill",d=>d.type==='person'?'#fbbf24':'#94a3b8')
.attr("text-anchor","middle").attr("dy",d=>d.type==='person'?-28:-20)
.attr("font-family","'JetBrains Mono',monospace").attr("font-weight",d=>d.type==='person'?600:400)
.attr("pointer-events","none");
const tt=d3.select("#tt");
nd.on("mouseover",(e,d)=>{tt.style("opacity",1);
let h=`<b>${d.id}</b><br>`;
if(d.type==='person')h+=`Tipo: <span class="m">Decisor</span>`;
else h+=`Adj: <span class="m">${d.adj}</span><br>Importe: <span class="m">${(d.imp/1e6).toFixed(1)}M€</span><br>Flags: <span class="m">${d.flags}</span>`;
tt.html(h)}).on("mousemove",e=>{tt.style("left",(e.pageX+15)+"px").style("top",(e.pageY-10)+"px")})
.on("mouseout",()=>tt.style("opacity",0));
sim.on("tick",()=>{
lk.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
gl2.attr("cx",d=>d.x).attr("cy",d=>d.y);gl1.attr("cx",d=>d.x).attr("cy",d=>d.y);
nd.attr("cx",d=>d.x).attr("cy",d=>d.y);cr.attr("cx",d=>d.x).attr("cy",d=>d.y);
lb.attr("x",d=>d.x).attr("y",d=>d.y)});
nd.attr("r",0).transition().duration(800).delay((_,i)=>i*60)
.attr("r",d=>d.type==='person'?20:Math.max(8,Math.min(16,6+Math.sqrt(d.adj||1)*.7)));
lk.attr("opacity",0).transition().duration(500).delay(300).attr("opacity",1);
lb.attr("opacity",0).transition().duration(700).delay(600).attr("opacity",1);
</script></body></html>"""


# ═══════════════════════════════════════════════════════════════
# CLUSTER ANALYSIS — connected components
# ═══════════════════════════════════════════════════════════════
def find_clusters(df_pares):
    """Union-Find connected components from pairs."""
    e1c = _fcol(df_pares, 'empresa_1'); e2c = _fcol(df_pares, 'empresa_2')
    if not e1c or not e2c: return pd.DataFrame()
    parent = {}
    def find(x):
        while parent.get(x, x) != x: parent[x] = parent.get(parent[x], parent[x]); x = parent[x]
        return x
    def union(a, b): ra, rb = find(a), find(b); parent[ra] = rb if ra != rb else ra

    for _, r in df_pares.iterrows(): union(str(r[e1c]), str(r[e2c]))
    clusters = {}
    for _, r in df_pares.iterrows():
        root = find(str(r[e1c]))
        if root not in clusters: clusters[root] = {'empresas': set(), 'pares': 0, 'max_score': 0, 'flags_sum': 0}
        cl = clusters[root]
        cl['empresas'].add(str(r[e1c])); cl['empresas'].add(str(r[e2c]))
        cl['pares'] += 1
        sc_c = _fcol(df_pares, 'par_score','score_max')
        nf_c = _fcol(df_pares, 'n_flags')
        if sc_c: cl['max_score'] = max(cl['max_score'], float(r.get(sc_c, 0) or 0))
        if nf_c: cl['flags_sum'] += int(r.get(nf_c, 0) or 0)

    rows = []
    for i, (root, cl) in enumerate(sorted(clusters.items(), key=lambda x: -x[1]['max_score'])):
        rows.append({
            'cluster': i+1, 'n_empresas': len(cl['empresas']), 'n_pares': cl['pares'],
            'max_score': round(cl['max_score'], 1), 'flags_total': cl['flags_sum'],
            'empresas': ', '.join(sorted(cl['empresas'])[:5]) + ('...' if len(cl['empresas']) > 5 else '')
        })
    return pd.DataFrame(rows)

def pl_clusters_bubble(cl_df):
    """Bubble chart of clusters: x=n_empresas, y=max_score, size=n_pares."""
    if len(cl_df) == 0: return None
    fig = go.Figure(go.Scatter(
        x=cl_df['n_empresas'], y=cl_df['max_score'],
        mode='markers+text', text=[f"C{r['cluster']}" for _, r in cl_df.head(20).iterrows()],
        textfont=dict(size=7, color=C['text2'], family='JetBrains Mono'),
        textposition='top center',
        marker=dict(
            size=np.sqrt(cl_df['n_pares'].head(20))*8+8,
            color=cl_df['flags_total'].head(20),
            colorscale=[[0,'rgba(59,130,246,.7)'],[0.5,'rgba(245,158,11,.8)'],[1,'rgba(239,68,68,.9)']],
            showscale=True, colorbar=dict(title='Flags', thickness=10, len=.5,
                                          tickfont=dict(size=9, color=C['muted'])),
            line=dict(width=1, color='rgba(255,255,255,.1)')),
        hovertext=[f"<b>Cluster {r['cluster']}</b><br>{r['n_empresas']} empresas<br>"
                   f"{r['n_pares']} pares<br>Max score: {r['max_score']}<br>{r['empresas'][:80]}"
                   for _, r in cl_df.head(20).iterrows()],
        hoverinfo='text'))
    fig.update_layout(**PL, height=420,
        title=dict(text='<b>Clusters</b> · Componentes conexas', font=dict(size=13), x=0),
        xaxis=dict(title='Empresas en cluster', gridcolor=C['grid']),
        yaxis=dict(title='Max score', gridcolor=C['grid']))
    return fig


# ═══════════════════════════════════════════════════════════════
# ADJACENCY MATRIX — persona × empresa heatmap
# ═══════════════════════════════════════════════════════════════
def pl_adjacency(df_pares, max_personas=25):
    """Interactive heatmap of top personas × empresas they connect."""
    e1c = _fcol(df_pares, 'empresa_1'); e2c = _fcol(df_pares, 'empresa_2')
    pc = _fcol(df_pares, 'persona','decisor')
    sc_c = _fcol(df_pares, 'par_score','score_max')
    if not e1c or not e2c or not pc: return None

    # Build persona → empresa connections
    pairs = {}
    for _, r in df_pares.iterrows():
        p = str(r[pc])[:30]
        if p not in pairs: pairs[p] = {}
        for ec in [e1c, e2c]:
            e = str(r[ec])[:30]
            sc = float(r[sc_c]) if sc_c and pd.notna(r.get(sc_c)) else 1
            pairs[p][e] = max(pairs[p].get(e, 0), sc)

    # Top personas by number of companies
    top_p = sorted(pairs.keys(), key=lambda p: -len(pairs[p]))[:max_personas]
    all_e = set()
    for p in top_p: all_e.update(pairs[p].keys())
    top_e = sorted(all_e, key=lambda e: -sum(pairs.get(p, {}).get(e, 0) for p in top_p))[:40]

    z = [[pairs.get(p, {}).get(e, 0) for e in top_e] for p in top_p]
    fig = go.Figure(go.Heatmap(
        z=z, x=[e[:25] for e in top_e], y=[p[:25] for p in top_p],
        colorscale=[[0,'rgba(5,6,9,1)'],[0.15,'rgba(59,130,246,.2)'],
                     [0.4,'rgba(59,130,246,.5)'],[0.7,'rgba(245,158,11,.7)'],[1,'rgba(239,68,68,.9)']],
        hovertemplate='<b>%{y}</b><br>%{x}<br>Score: %{z:.0f}<extra></extra>',
        colorbar=dict(title='Score', thickness=10, len=.6, tickfont=dict(size=9, color=C['muted']))))
    fig.update_layout(**PL, height=max(400, len(top_p)*24+100),
        title=dict(text='<b>Adjacency</b> · Persona × Empresa (score)', font=dict(size=13), x=0),
        xaxis=dict(tickfont=dict(size=7), tickangle=-45, side='bottom'),
        yaxis=dict(tickfont=dict(size=8), autorange='reversed'))
    return fig


def pl_f7_heatmap(df):
    if 'pct_adj_organo' not in df.columns: return None
    emp_col = 'adj_norm' if 'adj_norm' in df.columns else df.columns[0]
    org_col = 'organo_contratante' if 'organo_contratante' in df.columns else df.columns[1]
    top = df.head(100).copy()
    top['emp'] = top[emp_col].astype(str).str[:30]; top['org'] = top[org_col].astype(str).str[:35]
    top_emps = top.groupby('emp')['pct_adj_organo'].max().nlargest(15).index.tolist()
    sub = top[top['emp'].isin(top_emps)]
    if len(sub) < 3: return None
    piv = sub.pivot_table(index='emp', columns='org', values='pct_adj_organo', aggfunc='max').fillna(0)
    fig = go.Figure(go.Heatmap(z=piv.values, x=[str(c)[:30] for c in piv.columns], y=piv.index.tolist(),
        colorscale=[[0,'rgba(5,6,9,1)'],[.3,'rgba(59,130,246,.35)'],[.6,'rgba(245,158,11,.55)'],[1,'rgba(239,68,68,.85)']],
        hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.0%}<extra></extra>',
        colorbar=dict(title='%Adj', thickness=12, len=.6, tickfont=dict(size=9, color=C['muted']))))
    fig.update_layout(**PL, height=max(350, len(top_emps)*28+80),
        title=dict(text='<b>F7</b> · Concentración empresa × órgano', font=dict(size=13), x=0),
        xaxis=dict(tickfont=dict(size=8), tickangle=-45), yaxis=dict(tickfont=dict(size=9)))
    return fig


# ═══════════════════════════════════════════════════════════════
# UNIVERSAL SEARCH — scan all parquets
# ═══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def search_all_flags(q, flags):
    """Search a term across all flag parquets. Returns summary per flag."""
    results = []
    for stem, fi in flags.items():
        try:
            df = load_pq(fi['path'])
            meta = get_flag_meta(stem)
            # Search in object columns
            hit_cols = []
            total_hits = 0
            for col in df.select_dtypes(include=['object']).columns:
                n = df[col].astype(str).str.contains(q, case=False, na=False).sum()
                if n > 0:
                    hit_cols.append(col)
                    total_hits += n
            if total_hits > 0:
                # Get sample rows
                mask = pd.Series(False, index=df.index)
                for col in hit_cols:
                    mask |= df[col].astype(str).str.contains(q, case=False, na=False)
                sample = df[mask].head(5)
                # Get score if available
                sc_col = next((c for c in df.columns if any(k in c.lower()
                    for k in ['risk_score','par_score','score_max','score'])), None)
                max_sc = float(sample[sc_col].max()) if sc_col and sc_col in sample.columns else None
                results.append({
                    'stem': stem, 'label': meta['label'], 'icon': meta['icon'],
                    'css': meta['css'], 'scope': fi['scope'],
                    'hits': total_hits, 'cols': hit_cols,
                    'max_score': max_sc, 'sample': sample,
                })
        except Exception:
            pass
    return results

@st.cache_data(show_spinner=False)
def build_company_profile(empresa_q, flags):
    """Aggregate all info about a company across flags."""
    profile = {'nombre': empresa_q, 'flags_active': [], 'connections': [],
               'organos': set(), 'scores': {}, 'details': {}}

    for stem, fi in flags.items():
        try:
            df = load_pq(fi['path'])
            meta = get_flag_meta(stem)
            # Search company
            mask = pd.Series(False, index=df.index)
            for col in df.select_dtypes(include=['object']).columns:
                mask |= df[col].astype(str).str.contains(empresa_q, case=False, na=False)
            hits = df[mask]
            if len(hits) == 0:
                continue

            profile['flags_active'].append({
                'flag': meta['label'], 'icon': meta['icon'], 'stem': stem,
                'scope': fi['scope'], 'n_hits': len(hits)})

            # Scores
            for sc_col in ['risk_score','par_score','score_max','score','pct_adj_organo']:
                if sc_col in hits.columns:
                    val = hits[sc_col].max()
                    if pd.notna(val):
                        profile['scores'][f"{meta['short']}_{sc_col}"] = round(float(val), 2)

            # Connections (from F6)
            if 'empresa_1' in hits.columns and 'empresa_2' in hits.columns:
                for _, r in hits.iterrows():
                    e1, e2 = str(r.get('empresa_1','')), str(r.get('empresa_2',''))
                    other = e2 if empresa_q.lower() in e1.lower() else e1
                    pc = _fcol(hits, 'persona', 'decisor')
                    persona = str(r[pc])[:40] if pc else '?'
                    profile['connections'].append({
                        'empresa': other[:40], 'persona': persona,
                        'score': float(r.get('par_score', r.get('score_max', 0)) or 0),
                        'organos': int(r.get('n_organos_comunes', r.get('organos_comunes', 0)) or 0),
                        'flags': int(r.get('n_flags', 0) or 0),
                    })

            # Órganos (from F7)
            if 'organo_contratante' in hits.columns:
                for o in hits['organo_contratante'].dropna().unique():
                    profile['organos'].add(str(o)[:60])

            # Details per flag
            profile['details'][stem] = hits.head(10)

        except Exception:
            pass

    profile['organos'] = sorted(profile['organos'])
    return profile


# ═══════════════════════════════════════════════════════════════
# F9 GEOGRAPHIC MAP — arcs between CCAA
# ═══════════════════════════════════════════════════════════════
CCAA_COORDS = {
    'Andalucía': (37.38, -4.77), 'Aragón': (41.60, -0.88), 'Asturias': (43.36, -5.85),
    'Canarias': (28.12, -15.43), 'Cantabria': (43.18, -3.99), 'Castilla y León': (41.65, -4.73),
    'Castilla-La Mancha': (39.28, -2.88), 'Cataluña': (41.82, 1.47), 'Ceuta': (35.89, -5.32),
    'Comunidad Valenciana': (39.48, -0.75), 'Extremadura': (39.16, -6.17), 'Galicia': (42.57, -8.17),
    'Islas Baleares': (39.57, 2.65), 'La Rioja': (42.29, -2.52), 'Madrid': (40.42, -3.70),
    'Melilla': (35.29, -2.94), 'Murcia': (37.99, -1.13), 'Navarra': (42.70, -1.68),
    'País Vasco': (43.00, -2.62),
}

def pl_geo_map(df_geo):
    """Map of Spain with arcs showing geographic discrepancy."""
    reg_col = next((c for c in df_geo.columns if 'registro' in c.lower() or 'ccaa_borme' in c.lower()
                    or 'ccaa_registro' in c.lower()), None)
    con_col = next((c for c in df_geo.columns if 'contrato' in c.lower() or 'ccaa_contrato' in c.lower()
                    or 'ccaa_principal' in c.lower()), None)
    if not reg_col or not con_col:
        return None

    # Aggregate flows: (origin, dest) → count, total_importe
    imp_col = _fcol(df_geo, 'importe', 'volumen', 'amount')
    flows = {}
    for _, r in df_geo.iterrows():
        orig = str(r[reg_col]).strip()
        dest = str(r[con_col]).strip()
        if orig == dest or orig not in CCAA_COORDS or dest not in CCAA_COORDS:
            continue
        key = (orig, dest)
        if key not in flows:
            flows[key] = {'count': 0, 'importe': 0}
        flows[key]['count'] += 1
        if imp_col and pd.notna(r.get(imp_col)):
            flows[key]['importe'] += float(r[imp_col])

    if not flows:
        return None

    # Sort by count
    top_flows = sorted(flows.items(), key=lambda x: -x[1]['count'])[:60]
    max_count = max(f[1]['count'] for f in top_flows)

    fig = go.Figure()

    # ── Arcs ──
    for (orig, dest), info in top_flows:
        lat0, lon0 = CCAA_COORDS[orig]
        lat1, lon1 = CCAA_COORDS[dest]
        intensity = info['count'] / max_count
        width = 1 + intensity * 5
        alpha = 0.15 + intensity * 0.55
        # Curved arc via midpoint
        mid_lat = (lat0 + lat1) / 2 + (lon1 - lon0) * 0.08
        mid_lon = (lon0 + lon1) / 2 - (lat1 - lat0) * 0.08
        lats = [lat0, mid_lat, lat1]
        lons = [lon0, mid_lon, lon1]

        fig.add_trace(go.Scattergeo(
            lat=lats, lon=lons, mode='lines',
            line=dict(width=width, color=f'rgba(245,158,11,{alpha})'),
            hoverinfo='text',
            hovertext=f"<b>{orig} → {dest}</b><br>{info['count']} empresas<br>"
                      f"{info['importe']/1e6:.0f}M€",
            showlegend=False))

    # ── CCAA dots ──
    all_ccaa = set()
    for (o, d), _ in top_flows:
        all_ccaa.add(o); all_ccaa.add(d)
    # Count outgoing per CCAA
    out_count = {}
    for (o, d), info in top_flows:
        out_count[o] = out_count.get(o, 0) + info['count']
        out_count[d] = out_count.get(d, 0) + info['count']

    for ccaa in all_ccaa:
        if ccaa in CCAA_COORDS:
            lat, lon = CCAA_COORDS[ccaa]
            sz = 6 + (out_count.get(ccaa, 0) / max(out_count.values())) * 20
            fig.add_trace(go.Scattergeo(
                lat=[lat], lon=[lon], mode='markers+text',
                marker=dict(size=sz, color='#3b82f6',
                            line=dict(width=1, color='rgba(255,255,255,.2)'),
                            opacity=0.9),
                text=[ccaa[:12]], textposition='top center',
                textfont=dict(size=8, color=C['text2'], family='JetBrains Mono'),
                hovertext=f"<b>{ccaa}</b><br>{out_count.get(ccaa, 0)} flujos",
                hoverinfo='text', showlegend=False))

    fig.update_geos(
        scope='europe', center=dict(lat=40.0, lon=-3.5),
        projection_scale=6.5,
        showland=True, landcolor='rgba(13,16,23,1)',
        showocean=True, oceancolor='rgba(5,6,9,1)',
        showcoastlines=True, coastlinecolor='rgba(37,43,61,.6)',
        showcountries=True, countrycolor='rgba(37,43,61,.4)',
        showlakes=False, showrivers=False,
        bgcolor='rgba(0,0,0,0)',
        lonaxis_range=[-10, 5], lataxis_range=[27, 44])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono, monospace', color=C['text'], size=11),
        margin=dict(l=0, r=0, t=50, b=0), height=550,
        title=dict(text='<b>F9</b> · Discrepancia geográfica — Registro ≠ Contratos',
                   font=dict(size=14, color=C['text'], family='JetBrains Mono'),
                   x=0.5, xanchor='center'),
        hoverlabel=dict(bgcolor='rgba(13,16,23,0.97)', bordercolor=C['border2'],
                        font=dict(color=C['text'], size=11, family='JetBrains Mono')),
        annotations=[dict(
            text="<b style='color:#f59e0b'>→</b> Arcos: CCAA registro → CCAA mayoritaria de contratos · Grosor ∝ nº empresas",
            xref="paper", yref="paper", x=0.5, y=-0.02, showarrow=False,
            font=dict(size=9, color=C['text2'], family='JetBrains Mono'))])
    return fig


# ═══════════════════════════════════════════════════════════════
# TEMPORAL EVOLUTION — network by year
# ═══════════════════════════════════════════════════════════════
def pl_temporal_evolution(df_pares):
    """Show how the network evolves over time."""
    date_cols = [c for c in df_pares.columns if df_pares[c].dtype in ['datetime64[ns]','datetime64[ns, UTC]']]
    if not date_cols:
        for c in df_pares.columns:
            if any(k in c.lower() for k in ['fecha','date','año','year','first_','last_']):
                try:
                    parsed = pd.to_datetime(df_pares[c], errors='coerce')
                    if parsed.notna().sum() > len(df_pares) * 0.3:
                        df_pares = df_pares.copy()
                        df_pares[c] = parsed
                        date_cols.append(c)
                except Exception:
                    pass
    if not date_cols:
        return None, None
    dc = date_cols[0]
    df_t = df_pares.dropna(subset=[dc]).copy()
    if len(df_t) < 10:
        return None, None
    df_t['_year'] = df_t[dc].dt.year
    years = sorted(int(y) for y in df_t['_year'].dropna().unique() if 2005 <= y <= 2026)
    if len(years) < 2:
        return None, None

    sc_col = next((c for c in ['par_score','score_max','score'] if c in df_t.columns), None)
    yearly = []
    for y in years:
        sub = df_t[df_t['_year'] <= y]
        row = {'year': y, 'pares': len(sub)}
        emps = set()
        for ec in ['empresa_1','empresa_2']:
            if ec in sub.columns:
                emps.update(sub[ec].dropna().unique())
        row['empresas'] = len(emps)
        if sc_col:
            row['max_score'] = float(sub[sc_col].max()) if len(sub) else 0
        yearly.append(row)

    ydf = pd.DataFrame(yearly)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ydf['year'], y=ydf['pares'], name='Pares (acum.)',
        mode='lines+markers', line=dict(color=C['accent'], width=2.5),
        marker=dict(size=7, color=C['accent'])))
    if 'empresas' in ydf.columns:
        fig.add_trace(go.Scatter(x=ydf['year'], y=ydf['empresas'], name='Empresas',
            mode='lines+markers', line=dict(color=C['accent2'], width=2, dash='dot'),
            marker=dict(size=5, color=C['accent2'])))
    if 'max_score' in ydf.columns:
        fig.add_trace(go.Scatter(x=ydf['year'], y=ydf['max_score'], name='Max score',
            mode='lines+markers', line=dict(color=C['warn'], width=2),
            marker=dict(size=5, color=C['warn']), yaxis='y2'))

    fig.update_layout(**PL, height=340,
        title=dict(text='<b>Evolución temporal</b> · Red acumulada por año', font=dict(size=13), x=0),
        xaxis=dict(title='Año', gridcolor=C['grid'], dtick=2),
        yaxis=dict(title='Pares / Empresas', gridcolor=C['grid']),
        yaxis2=dict(title='Max score', overlaying='y', side='right', showgrid=False,
                    title_font=dict(color=C['warn'], size=11),
                    tickfont=dict(color=C['warn'], size=9)),
        legend=dict(orientation='h', y=1.12, x=0, font=dict(size=10)))
    return fig, ydf


def filter_pares_by_year(df_pares, year_range):
    """Filter pares to a year range using first date column found."""
    date_cols = [c for c in df_pares.columns if df_pares[c].dtype in ['datetime64[ns]','datetime64[ns, UTC]']]
    if not date_cols:
        for c in df_pares.columns:
            if any(k in c.lower() for k in ['fecha','date','año','year']):
                try:
                    parsed = pd.to_datetime(df_pares[c], errors='coerce')
                    if parsed.notna().sum() > len(df_pares) * 0.3:
                        df_pares = df_pares.copy()
                        df_pares[c] = parsed
                        date_cols.append(c)
                        break
                except Exception:
                    pass
    if not date_cols:
        return df_pares
    dc = date_cols[0]
    mask = df_pares[dc].dt.year.between(year_range[0], year_range[1])
    return df_pares[mask | df_pares[dc].isna()]




def pl_comparador_scatter(cdf):
    """Heatmap: Nacional flags × Catalunya flags for common companies."""
    if len(cdf) < 3: return None

    # Build crosstab: which Nacional flags co-occur with which Catalunya flags
    rows = []
    for _, r in cdf.iterrows():
        nac_flags = [f.strip() for f in str(r.get('flags_nac','')).split(',') if f.strip()]
        cat_flags = [f.strip() for f in str(r.get('flags_cat','')).split(',') if f.strip()]
        for nf in nac_flags:
            for cf in cat_flags:
                rows.append({'nacional': nf, 'catalunya': cf})
    if not rows:
        return None

    cross = pd.DataFrame(rows)
    piv = cross.groupby(['nacional','catalunya']).size().reset_index(name='n')
    piv_wide = piv.pivot(index='nacional', columns='catalunya', values='n').fillna(0)

    # Sort by total
    piv_wide = piv_wide.loc[piv_wide.sum(axis=1).sort_values(ascending=True).index]
    piv_wide = piv_wide[piv_wide.sum(axis=0).sort_values(ascending=False).index]

    fig = go.Figure(go.Heatmap(
        z=piv_wide.values, x=piv_wide.columns.tolist(), y=piv_wide.index.tolist(),
        colorscale=[[0,'rgba(5,6,9,1)'],[.15,'rgba(59,130,246,.25)'],[.4,'rgba(245,158,11,.5)'],[1,'rgba(239,68,68,.85)']],
        hovertemplate='<b>Nacional:</b> %{y}<br><b>Catalunya:</b> %{x}<br><b>Empresas:</b> %{z}<extra></extra>',
        colorbar=dict(title='Empresas', thickness=12, len=.6, tickfont=dict(size=9, color=C['muted'])),
        xgap=2, ygap=2))
    fig.update_layout(**PL, height=max(300, len(piv_wide)*32+80),
        title=dict(text='<b>Señales cruzadas</b> · Nacional × Catalunya', font=dict(size=13), x=0),
        xaxis=dict(title='Señales Catalunya', tickfont=dict(size=9), tickangle=-35, side='bottom'),
        yaxis=dict(title='Señales Nacional', tickfont=dict(size=9)))
    return fig


# ═══════════════════════════════════════════════════════════════
# TAB 1: CALIDAD DE DATOS
# ═══════════════════════════════════════════════════════════════
def render_quality(prof, label):
    # ── 1. Resumen general ──
    st.markdown('<div class="sec">Resumen del dataset</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.metric("Registros", fmt(prof['n']))
    with c2: st.metric("Columnas", prof['nc'])
    with c3: st.metric("Numéricas", prof['n_num'])
    with c4: st.metric("Categóricas", prof['n_cat'])
    with c5: st.metric("Fechas", prof.get('n_dt', 0))
    with c6: st.metric("Duplicados", f"{prof['dupe_pct']:.2f}%")

    mem = prof.get('memory_mb', 0)
    st.markdown(
        f"<div style='margin:.5rem 0;font-size:.8rem;color:{C['text2']}'>"
        f"Completitud media: {qb(prof['completitud'])} · "
        f"100% completas: <b style='color:{C['text']}'>{prof['n_complete']}</b>/{prof['nc']} · "
        f">90% vacías: <b style='color:{C['bad'] if prof['n_hi_miss'] else C['good']}'>{prof['n_hi_miss']}</b>"
        f"{f' · Memoria: <b>{mem:,.0f} MB</b>' if mem else ''}</div>",
        unsafe_allow_html=True)

    # ── 2. Coverage scores (barras horizontales) ──
    coverage = prof.get('coverage', {})
    if coverage:
        st.markdown('<div class="sec">Cobertura de campos clave</div>', unsafe_allow_html=True)
        cov_names = list(coverage.keys())
        cov_vals = list(coverage.values())
        cov_colors = [C['good'] if v >= 90 else C['warn'] if v >= 60 else C['bad'] for v in cov_vals]
        fig = go.Figure(go.Bar(
            y=cov_names[::-1], x=cov_vals[::-1], orientation='h',
            marker=dict(color=cov_colors[::-1], line=dict(width=0)),
            text=[f'{v:.0f}%' for v in cov_vals[::-1]], textposition='auto',
            textfont=dict(size=10, color='white', family='JetBrains Mono'),
            hovertemplate='<b>%{y}</b>: %{x:.1f}%<extra></extra>'))
        fig.update_layout(**PL, height=max(250, len(cov_names)*28),
            title=dict(text='<b>% registros con valor</b> por campo clave', font=dict(size=13), x=0),
            xaxis=dict(range=[0, 105], gridcolor=C['grid']),
            yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

    # ── 3. Quality Rules ──
    rules = prof.get('rules', [])
    if rules:
        st.markdown('<div class="sec">Reglas de calidad</div>', unsafe_allow_html=True)
        for r in rules:
            sev = r.get('severity', 'ok')
            if sev == 'bad':   icon, css = '❌', f'color:{C["bad"]}'
            elif sev == 'warn': icon, css = '⚠️', f'color:{C["warn"]}'
            elif sev == 'info': icon, css = 'ℹ️', f'color:{C["accent2"]}'
            else:               icon, css = '✅', f'color:{C["good"]}'
            base_txt = f" (de {r['base']:,} con ambos campos)" if 'base' in r else ''
            st.markdown(
                f"<div class='fcard' style='padding:10px 16px;margin:4px 0'>"
                f"<span style='font-size:.85rem'>{icon}</span> "
                f"<b style='{css};font-size:.8rem'>{r['id']}: {r['name']}</b> — "
                f"<span style='font-size:.78rem;color:{C['text2']}'>{r['description']}</span>"
                f"<span style='float:right;font-family:\"JetBrains Mono\",monospace;font-size:.78rem;"
                f"{css}'>{r['count']:,} ({r['pct']:.2f}%){base_txt}</span></div>",
                unsafe_allow_html=True)

    # ── 4. Missing data + Radar ──
    st.markdown('<div class="sec">Completitud por columna</div>', unsafe_allow_html=True)
    ca, cb = st.columns([2, 1])
    with ca:
        fig = pl_missing_from_json(prof['missing'])
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.success("✅ Sin valores faltantes significativos")
    with cb:
        fig = pl_radar_from_json(prof.get('radar', {}))
        if fig: st.plotly_chart(fig, use_container_width=True)

    # ── 5. Temporal ──
    temp = prof.get('temporal', {})
    if temp:
        st.markdown('<div class="sec">Cobertura temporal</div>', unsafe_allow_html=True)
        dc = st.selectbox("Campo de fecha", list(temp.keys()), key=f"dt_{label}")
        d = temp[dc]
        fig = pl_temporal_from_json(temp, dc)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Rango: **{d['min']}** → **{d['max']}** · "
                       f"Válidos: {d.get('n_valid',0):,} · Nulos: {d['n_null']:,}")

        # Year-over-year
        yoy = d.get('yoy', {})
        if yoy and len(yoy) > 1:
            years = sorted(yoy.keys())
            vals = [yoy[y] for y in years]
            # YoY growth
            growths = [None] + [round((vals[i]/vals[i-1]-1)*100, 1) if vals[i-1] > 0 else None
                                for i in range(1, len(vals))]
            fig_yoy = go.Figure()
            fig_yoy.add_trace(go.Bar(
                x=[str(y) for y in years], y=vals, name='Registros',
                marker=dict(color=C['accent2'], opacity=.8, line=dict(width=0)),
                hovertemplate='<b>%{x}</b><br>%{y:,.0f} registros<extra></extra>'))
            # Growth line on secondary axis
            valid_g = [(str(years[i]), growths[i]) for i in range(len(years)) if growths[i] is not None]
            if valid_g:
                fig_yoy.add_trace(go.Scatter(
                    x=[g[0] for g in valid_g], y=[g[1] for g in valid_g],
                    mode='lines+markers', name='Crecimiento %', yaxis='y2',
                    line=dict(color=C['accent'], width=2),
                    marker=dict(size=6, color=C['accent']),
                    hovertemplate='<b>%{x}</b><br>%{y:+.1f}%<extra></extra>'))
            fig_yoy.update_layout(**PL, height=300,
                title=dict(text='<b>Evolución anual</b>', font=dict(size=13), x=0),
                xaxis=dict(gridcolor=C['grid']),
                yaxis=dict(title='Registros', gridcolor=C['grid']),
                yaxis2=dict(title='Crecimiento %', overlaying='y', side='right',
                            gridcolor='rgba(0,0,0,0)', ticksuffix='%',
                            title_font=dict(color=C['accent']),
                            tickfont=dict(color=C['accent'])),
                legend=dict(orientation='h', y=-0.15),
                bargap=.15)
            st.plotly_chart(fig_yoy, use_container_width=True)

    # ── 6. Importes ──
    amts = prof.get('amounts', {})
    if amts:
        st.markdown('<div class="sec">Análisis de importes</div>', unsafe_allow_html=True)
        ac = st.selectbox("Campo de importe", list(amts.keys()), key=f"am_{label}")
        d = amts[ac]

        # Metrics row
        s1, s2, s3, s4, s5, s6 = st.columns(6)
        with s1: st.metric("Válidos", fmt(d.get('n_valid', 0)))
        with s2: st.metric("Media", f"{d.get('mean',0):,.0f}€")
        with s3: st.metric("Mediana", f"{d.get('median',0):,.0f}€")
        with s4: st.metric("P95", f"{d.get('p95',0):,.0f}€")
        with s5: st.metric("Max", f"{d.get('max',0):,.0f}€")
        with s6: st.metric("Neg/Ceros", f"{d.get('n_neg',0):,}/{d.get('n_zero',0):,}")

        # Histogram
        fig = pl_amounts_from_json(amts, ac)
        if fig: st.plotly_chart(fig, use_container_width=True)

        # Percentiles table
        pcts = d.get('percentiles', {})
        if pcts:
            with st.expander("📊 Tabla de percentiles"):
                pct_data = {k: v for k, v in pcts.items() if k.startswith('p') and v is not None}
                pct_df = pd.DataFrame([{
                    'Percentil': k.upper(),
                    'Valor': f"{v:,.2f}€" if v else '—'
                } for k, v in pct_data.items()])
                extras = []
                for k in ['mean','std','skew','kurtosis']:
                    if k in pcts and pcts[k] is not None:
                        extras.append({'Percentil': k.capitalize(), 'Valor': f"{pcts[k]:,.2f}"})
                if extras:
                    pct_df = pd.concat([pct_df, pd.DataFrame(extras)], ignore_index=True)
                st.dataframe(pct_df, use_container_width=True, hide_index=True)

        # Amount brackets (treemap-style bar chart)
        brackets = d.get('brackets')
        if brackets:
            bl = brackets['labels']
            bc = brackets['counts']
            bt = brackets['totals']
            total_c = brackets['total_count']
            total_a = brackets['total_amount']
            br_pcts = [round(c/total_c*100, 1) if total_c else 0 for c in bc]
            ba_pcts = [round(t/total_a*100, 1) if total_a else 0 for t in bt]

            fig_br = go.Figure()
            fig_br.add_trace(go.Bar(
                x=bl, y=br_pcts, name='% contratos',
                marker=dict(color=C['accent2'], opacity=.8),
                hovertemplate='<b>%{x}</b><br>%{y:.1f}% contratos<extra></extra>'))
            fig_br.add_trace(go.Bar(
                x=bl, y=ba_pcts, name='% importe',
                marker=dict(color=C['accent'], opacity=.8),
                hovertemplate='<b>%{x}</b><br>%{y:.1f}% importe<extra></extra>'))
            fig_br.update_layout(**PL, height=320, barmode='group',
                title=dict(text='<b>Distribución por tramos</b> · % contratos vs % importe', font=dict(size=13), x=0),
                xaxis=dict(gridcolor=C['grid'], tickangle=-30, tickfont=dict(size=9)),
                yaxis=dict(title='%', gridcolor=C['grid']),
                legend=dict(orientation='h', y=-0.22), bargap=.2)
            st.plotly_chart(fig_br, use_container_width=True)

    # ── 7. Categorías ──
    cats = prof.get('categories', {})
    if cats:
        st.markdown('<div class="sec">Análisis de categorías</div>', unsafe_allow_html=True)
        cc = st.selectbox("Campo categórico", list(cats.keys()), key=f"cc_{label}")
        d = cats[cc]

        # Metrics
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("Valores únicos", fmt(d.get('n_unique', 0)))
        with mc2: st.metric("Top 1", f"{d.get('top1_pct', 0):.1f}%")
        with mc3: st.metric("Top 5 acumulado", f"{d.get('top5_pct', 0):.1f}%")
        with mc4: st.metric("HHI (concentración)", f"{d.get('hhi_approx', 0):.0f}")

        fig = pl_category_from_json(cats, cc)
        if fig: st.plotly_chart(fig, use_container_width=True)

    # ── 8. CPV ──
    cpv = prof.get('cpv_top')
    if cpv:
        st.markdown('<div class="sec">Distribución CPV (nivel 1)</div>', unsafe_allow_html=True)
        cpv_labels = [f"{c}: {l}" for c, l in zip(cpv['codes'], cpv['labels'])]
        fig = go.Figure(go.Bar(
            y=cpv_labels[::-1], x=cpv['counts'][::-1], orientation='h',
            marker=dict(color=C['accent3'], opacity=.85, line=dict(width=0)),
            hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>'))
        fig.update_layout(**PL, height=max(300, len(cpv_labels)*24),
            title=dict(text='<b>Top 15 familias CPV</b>', font=dict(size=13), x=0),
            xaxis=dict(gridcolor=C['grid']), yaxis=dict(tickfont=dict(size=9)))
        st.plotly_chart(fig, use_container_width=True)

    # ── 9. Top adjudicatarios ──
    top_adj = prof.get('top_adjudicatarios')
    if top_adj:
        st.markdown('<div class="sec">Top 20 adjudicatarios por importe</div>', unsafe_allow_html=True)
        names = top_adj['names']; importes = top_adj['importes']; ncontr = top_adj['n_contratos']
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=[n[:45] for n in names[::-1]],
            x=[i/1e6 for i in importes[::-1]],
            orientation='h',
            marker=dict(color=C['accent2'], opacity=.85, line=dict(width=0)),
            hovertext=[f"<b>{n[:50]}</b><br>{i/1e6:,.1f}M€<br>{c:,} contratos"
                       for n, i, c in zip(names[::-1], importes[::-1], ncontr[::-1])],
            hoverinfo='text'))
        fig.update_layout(**PL, height=max(400, len(names)*22),
            title=dict(text='<b>Top adjudicatarios</b> · Importe acumulado (M€)', font=dict(size=13), x=0),
            xaxis=dict(title='M€', gridcolor=C['grid']),
            yaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig, use_container_width=True)

    # ── 10. Top órganos ──
    top_org = prof.get('top_organos')
    if top_org:
        with st.expander("🏛️ Top 20 órganos contratantes por importe"):
            names = top_org['names']; importes = top_org['importes']; ncontr = top_org['n_contratos']
            fig = go.Figure(go.Bar(
                y=[n[:50] for n in names[::-1]],
                x=[i/1e6 for i in importes[::-1]],
                orientation='h',
                marker=dict(color=C['accent5'], opacity=.85, line=dict(width=0)),
                hovertext=[f"<b>{n[:55]}</b><br>{i/1e6:,.1f}M€<br>{c:,} contratos"
                           for n, i, c in zip(names[::-1], importes[::-1], ncontr[::-1])],
                hoverinfo='text'))
            fig.update_layout(**PL, height=max(400, len(names)*22),
                title=dict(text='<b>Top órganos contratantes</b> · M€', font=dict(size=13), x=0),
                xaxis=dict(title='M€', gridcolor=C['grid']),
                yaxis=dict(tickfont=dict(size=8)))
            st.plotly_chart(fig, use_container_width=True)

    # ── 11. Catálogo de columnas ──
    with st.expander("📋 Catálogo completo de columnas"):
        st.dataframe(pd.DataFrame(prof['catalog']), use_container_width=True, height=500, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2: FLAGS
# ═══════════════════════════════════════════════════════════════
def render_flags(flags):
    if not flags:
        st.warning("No se encontraron análisis. Coloca los parquets en `anomalias/`."); return
    st.markdown('<div class="sec">Análisis disponibles</div>', unsafe_allow_html=True)
    badges = ''.join(f'<span class="fb {get_flag_meta(s)["css"]}">{get_flag_meta(s)["icon"]} {get_flag_meta(s)["label"]}</span> ' for s in flags)
    st.markdown(f"<div style='margin-bottom:1rem'>{badges}</div>", unsafe_allow_html=True)

    stems = list(flags.keys())
    display = [f"{get_flag_meta(s)['icon']} {get_flag_meta(s)['label']} ({flags[s]['scope']})" for s in stems]
    idx = st.selectbox("Seleccionar análisis", range(len(stems)), format_func=lambda i: display[i])
    sel = stems[idx]; info = flags[sel]; meta = get_flag_meta(sel)

    # ── Explanation card per analysis type ──
    _EX = {
        'flag10': ('✂️ ¿Qué es?', 'Un órgano adjudica a la misma empresa <b>≥3 contratos en 90 días, todos bajo 15.000€</b> '
                   '(umbral de contrato menor), pero cuya suma supera ese umbral. Posible fraccionamiento para evitar licitación pública.'),
        'flag11': ('📝 ¿Qué es?', 'Empresas con <b>≥20% de sus contratos modificados</b> (la media catalana es ~0.57%). '
                   'Las modificaciones frecuentes pueden indicar adjudicaciones inicialmente bajas que se incrementan después.'),
        'flag1': ('🆕 ¿Qué es?', 'Empresas constituidas <b>menos de 6 meses antes</b> de recibir su primer contrato público. '
                  'Puede indicar sociedades instrumentales creadas ad hoc para adjudicaciones concretas.'),
        'flag2': ('💰 ¿Qué es?', 'Empresas con <b>capital social inferior a 3.000€</b> que reciben contratos significativos (>50K€). '
                  'Un capital tan bajo es inusual para empresas que manejan contratación pública relevante.'),
        'flag3': ('👥 ¿Qué es?', 'Empresas con <b>cambios frecuentes de administrador</b> en el Registro Mercantil. '
                  'La rotación rápida de cargos de decisión puede indicar testaferros o cambios para evadir responsabilidades.'),
        'flag4': ('💀 ¿Qué es?', 'Empresas con <b>acto de disolución publicado</b> en BORME que siguen recibiendo contratos públicos. '
                  'Una empresa disuelta no debería participar en licitaciones.'),
        'flag5': ('⚖️ ¿Qué es?', 'Empresas en <b>concurso de acreedores</b> (situación de insolvencia) según BORME. '
                  'La legislación restringe la contratación pública a empresas en esta situación.'),
        'persona': ('👤 ¿Qué es?', 'Ranking de <b>personas con más conexiones</b> entre empresas que licitan ante los mismos órganos. '
                    'El score acumula las puntuaciones de todos los pares en los que participa.'),
        'pares': ('🔗 ¿Qué es?', 'Cada fila es un <b>par de empresas</b> que comparten administrador y coinciden en ≥2 órganos contratantes. '
                  'Ya se han filtrado los grupos corporativos legítimos. El score combina concentración, cargo, flags e importe.'),
        'flag6': ('🕸️ ¿Qué es?', '<b>Dos empresas que comparten administrador</b> (sin ser del mismo grupo corporativo) ganan contratos '
                  'ante los mismos órganos contratantes. Sugiere posible coordinación de ofertas. '
                  'Se filtran grupos corporativos por nombre, solapamiento de consejo y fusiones BORME.'),
        'flag7': ('🎯 ¿Qué es?', 'Una empresa gana un <b>porcentaje anormalmente alto</b> de las adjudicaciones de un órgano contratante '
                  '(>40% en Nacional, adaptativo en Catalunya). Indica posible relación preferente.'),
        'flag8': ('🤝 ¿Qué es?', '<b>UTEs (Uniones Temporales de Empresas)</b> cuyos miembros comparten administrador. '
                  'Si dos empresas de una UTE tienen el mismo decisor, la "unión temporal" puede no ser independiente.'),
        'flag9': ('📍 ¿Qué es?', 'Empresas registradas en una comunidad autónoma que ganan contratos <b>mayoritariamente en otra</b> muy distinta. '
                  'Solo PYMEs (3–200 adj) — las grandes corporaciones con sede en Madrid se excluyen por ser habitual.'),
        'risk': ('📊 ¿Qué es?', 'Puntuación unificada que <b>combina todas las señales</b> con pesos ponderados. '
                 'A mayor score, más señales acumula una empresa. No es prueba de irregularidad — es una priorización para revisión humana.'),
        'grupo': ('🏢 ¿Qué es?', 'Pares de empresas <b>filtrados como grupo corporativo legítimo</b>: comparten nombre de marca, '
                  'tienen >40% solapamiento de consejo, o figuran en actos de fusión/absorción en BORME. Son falsos positivos descartados.'),
    }
    _exp = None
    for _k, _v in _EX.items():
        if _k in sel.lower():
            _exp = _v; break
    if _exp:
        st.markdown(f"<div class='intro-q' style='margin:12px 0 16px'>"
            f"<b style='color:{C['accent']}'>{_exp[0]}</b><br>"
            f"<span style='font-size:.82rem;color:{C['text2']};line-height:1.7'>{_exp[1]}</span></div>",
            unsafe_allow_html=True)

    with st.spinner("Cargando..."): df = load_pq(info['path'])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Registros", fmt(len(df)))
    with c2: st.metric("Columnas", len(df.columns))
    with c3: st.metric("Ámbito", info['scope'])
    with c4: st.metric("Tamaño", f"{info['size']/1024:.0f} KB")

    # ── Specialized views ──
    if 'pares' in sel or 'admin_network' in sel:
        # ── Temporal evolution ──
        fig_temp, ydf_temp = pl_temporal_evolution(df)
        if fig_temp:
            st.markdown('<div class="sec">Evolución temporal · Red por año</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="graph-caption">Muestra cómo crece la red de pares sospechosos año a año (acumulado). Línea roja = nº de pares, azul punteada = empresas únicas, amarilla = score máximo detectado ese año. Permite ver si los patrones se concentran en ciertos períodos.</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_temp, use_container_width=True)
            # Year filter slider
            date_cols = [c for c in df.columns if df[c].dtype in ['datetime64[ns]','datetime64[ns, UTC]']]
            if not date_cols:
                for c in df.columns:
                    if any(k in c.lower() for k in ['fecha','date','año','year']):
                        try:
                            parsed = pd.to_datetime(df[c], errors='coerce')
                            if parsed.notna().sum() > len(df) * 0.3:
                                df[c] = parsed
                                date_cols.append(c)
                        except Exception:
                            pass
            if date_cols:
                dc = date_cols[0]
                ymin = int(df[dc].dt.year.min())
                ymax = int(df[dc].dt.year.max())
                if ymax > ymin:
                    yr = st.slider("Filtrar por rango de años", ymin, ymax, (ymin, ymax), key="yr_slider")
                    if yr != (ymin, ymax):
                        df = filter_pares_by_year(df, yr)
                        st.caption(f"Mostrando {len(df)} pares en rango {yr[0]}–{yr[1]}")

        # ── Ego-network ──
        st.markdown('<div class="sec">Ego-Network · Explorar persona</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Grafo radial centrado en una persona. Nodos = empresas donde tiene cargo de decisión. Líneas doradas = vínculo persona→empresa. Líneas entre empresas = comparten órganos contratantes (grosor ∝ órganos comunes). Color del nodo: <span>azul</span> sin flags, naranja con 1 flag, rojo con 2+. Tamaño ∝ nº adjudicaciones. Arrastra nodos para explorar.</div>', unsafe_allow_html=True)
        pc = _fcol(df, 'persona','decisor','personas')
        if pc:
            personas_list = sorted(df[pc].dropna().unique().tolist())
        else:
            personas_list = []
            for col in df.select_dtypes(include=['object']).columns:
                if 'persona' in col.lower() or 'decisor' in col.lower():
                    personas_list = sorted(df[col].dropna().unique().tolist()); break
        if personas_list:
            sel_persona = st.selectbox("🔍 Buscar persona", [''] + personas_list[:1000], key="ego_p",
                                       format_func=lambda x: x if x else "Seleccionar...")
            if sel_persona:
                ego_data = build_ego_data(df, sel_persona)
                if ego_data and len(ego_data['nodes']) > 1:
                    html = ego_d3_html(ego_data)
                    components.html(html, height=620, scrolling=False)
                else:
                    st.info("No se encontraron conexiones para esta persona.")
        else:
            st.caption("No se detectó columna de personas en este dataset.")

        # ── Clusters ──
        st.markdown('<div class="sec">Clusters · Componentes conexas</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Algoritmo Union-Find agrupa empresas conectadas (comparten persona con cargo). Cada burbuja = un cluster. Eje X = nº empresas en el cluster, Y = score máximo, tamaño ∝ nº pares, color = total de flags. Clusters grandes con score alto son los más sospechosos.</div>', unsafe_allow_html=True)
        cl_df = find_clusters(df)
        if len(cl_df) > 0:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Clusters", len(cl_df))
            with c2: st.metric("Más grande", f"{cl_df['n_empresas'].max()} empr.")
            with c3: st.metric("Max score", f"{cl_df['max_score'].max():.0f}")
            with c4: st.metric("Con flags", int((cl_df['flags_total'] > 0).sum()))
            fig_cl = pl_clusters_bubble(cl_df)
            if fig_cl: st.plotly_chart(fig_cl, use_container_width=True)
            with st.expander("📋 Detalle de clusters"):
                st.dataframe(cl_df.head(50), use_container_width=True, hide_index=True)

        # ── Adjacency matrix ──
        st.markdown('<div class="sec">Adjacency Matrix · Persona × Empresa</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Heatmap de las 25 personas con más conexiones × las 40 empresas más frecuentes. Cada celda = score máximo de ese par persona-empresa. Permite detectar personas que aparecen en muchas empresas simultáneamente (filas densas) o empresas con múltiples personas vinculadas (columnas densas).</div>', unsafe_allow_html=True)
        fig_adj = pl_adjacency(df)
        if fig_adj: st.plotly_chart(fig_adj, use_container_width=True)
        else: st.caption("No se detectó columna de persona para construir la matriz.")

        # ── Bubble chart ──
        st.markdown('<div class="sec">Score vs Concentración</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Cada burbuja = un par de empresas. Eje X = concentración (órganos comunes / mín. órganos totales), Y = score del par. Tamaño ∝ importe total. Esquina superior derecha = máxima sospecha: alta concentración + alto score.</div>', unsafe_allow_html=True)
        fig_bub = pl_f6_bubble(df)
        if fig_bub: st.plotly_chart(fig_bub, use_container_width=True)

    elif 'personas' in sel:
        sc_col = next((c for c in ['score_total','score_sum','score'] if c in df.columns), None)
        if sc_col:
            st.markdown('<div class="sec">Top personas por score</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="graph-caption">Ranking de las 30 personas con mayor score acumulado. El score suma las puntuaciones de todos los pares en los que participa esa persona. Una persona con muchas empresas en órganos comunes y flags activos tendrá un score más alto.</div>', unsafe_allow_html=True)
            top = df.nlargest(30, sc_col)
            fig = go.Figure(go.Bar(y=top.index.astype(str).str[:30][::-1], x=top[sc_col].values[::-1], orientation='h',
                marker=dict(color=top[sc_col].values[::-1],
                    colorscale=[[0,'rgba(59,130,246,.7)'],[1,'rgba(239,68,68,.9)']], line=dict(width=0))))
            fig.update_layout(**PL, height=max(350, len(top)*20),
                title=dict(text='<b>Top 30</b> · Score acumulado', font=dict(size=13), x=0))
            st.plotly_chart(fig, use_container_width=True)

    elif 'flag7' in sel:
        st.markdown('<div class="sec">Concentración empresa × órgano</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Heatmap: cada celda = % de adjudicaciones de un órgano ganadas por una empresa. Se muestran las 15 empresas con mayor concentración. Colores cálidos = dominancia alta. El histograma inferior muestra la distribución general de concentración.</div>', unsafe_allow_html=True)
        fig = pl_f7_heatmap(df)
        if fig: st.plotly_chart(fig, use_container_width=True)
        if 'pct_adj_organo' in df.columns:
            fig = go.Figure(go.Histogram(x=df['pct_adj_organo']*100, nbinsx=40, marker=dict(color=C['good'], opacity=.85)))
            fig.update_layout(**PL, height=280,
                title=dict(text='<b>Distribución</b> · % adjudicaciones capturadas', font=dict(size=13), x=0),
                xaxis=dict(title='%', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
            st.plotly_chart(fig, use_container_width=True)

    elif 'risk_scoring' in sel:
        sc_col = next((c for c in ['risk_score','score'] if c in df.columns), None)
        if sc_col:
            st.markdown('<div class="sec">Scoring unificado</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="graph-caption">Distribución del risk_score unificado por empresa. Combina todos los flags (F1–F11) con pesos ponderados. El histograma muestra cuántas empresas hay en cada rango de score. La barra horizontal inferior desglosa cuántas empresas tienen cada flag activo.</div>', unsafe_allow_html=True)
            fig = pl_score(df, sc_col, f'Distribución: {sc_col}', C['accent'])
            if fig: st.plotly_chart(fig, use_container_width=True)
        bool_cols = [c for c in df.columns if df[c].dtype == bool]
        if bool_cols:
            flag_sums = {c: int(df[c].sum()) for c in bool_cols if df[c].sum() > 0}
            if flag_sums:
                fs_df = pd.DataFrame({'Flag': list(flag_sums.keys()), 'Empresas': list(flag_sums.values())}).sort_values('Empresas', ascending=True)
                fig = go.Figure(go.Bar(y=fs_df['Flag'], x=fs_df['Empresas'], orientation='h', marker=dict(color=C['accent'], opacity=.85)))
                fig.update_layout(**PL, height=max(220, len(fs_df)*30),
                    title=dict(text='<b>Composición</b> · Flags por empresa', font=dict(size=13), x=0))
                st.plotly_chart(fig, use_container_width=True)

    elif 'flag9' in sel or 'geo_dis' in sel:
        st.markdown('<div class="sec">Discrepancia geográfica — Mapa de flujos</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Arcos sobre el mapa de España. Cada arco = empresas registradas en una CCAA (origen, según domicilio BORME) que ganan contratos mayoritariamente en otra CCAA (destino). Grosor ∝ nº empresas con esa discrepancia. Solo PYMEs (3–200 adj) para evitar falsos positivos de grandes corporaciones con sede en Madrid.</div>', unsafe_allow_html=True)
        fig_map = pl_geo_map(df)
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.caption("No se detectaron columnas de CCAA registro/contratos para generar el mapa.")

    elif 'flag10' in sel or 'troceo' in sel:
        st.markdown('<div class="sec">Troceo — fraccionamiento de contratos</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Detecta posible fraccionamiento: empresa que recibe ≥3 contratos del mismo órgano en 90 días, todos ≤15.000€ (umbral de contrato menor), pero cuya suma supera el umbral. Histograma izquierdo = contratos por cluster. Derecho = ratio sobre umbral (2x = suma doble del límite).</div>', unsafe_allow_html=True)
        if 'n_contratos_cluster' in df.columns and 'importe_cluster' in df.columns:
            t1, t2 = st.columns(2)
            with t1:
                fig = go.Figure(go.Histogram(x=df['n_contratos_cluster'], nbinsx=30, marker=dict(color=C['accent'], opacity=.85)))
                fig.update_layout(**PL, height=280, title=dict(text='<b>Contratos por cluster</b>', font=dict(size=13), x=0),
                    xaxis=dict(title='Nº contratos', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
                st.plotly_chart(fig, use_container_width=True)
            with t2:
                fig = go.Figure(go.Histogram(x=df['ratio_sobre_umbral'], nbinsx=30, marker=dict(color=C['warn'], opacity=.85)))
                fig.update_layout(**PL, height=280, title=dict(text='<b>Ratio sobre umbral</b> (1x = justo en umbral)', font=dict(size=13), x=0),
                    xaxis=dict(title='Ratio', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
                st.plotly_chart(fig, use_container_width=True)

    elif 'flag11' in sel or 'modificacion' in sel:
        st.markdown('<div class="sec">Modificaciones contractuales excesivas</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="graph-caption">Empresas con ≥3 modificaciones contractuales y ≥20% de sus contratos modificados (promedio catalán: ~0.57%). Histograma izquierdo = % de contratos modificados por empresa. Derecho = nº absoluto de modificaciones. Modificaciones frecuentes pueden indicar adjudicaciones inicialmente bajas que se incrementan después.</div>', unsafe_allow_html=True)
        if 'pct_modificados' in df.columns:
            t1, t2 = st.columns(2)
            with t1:
                fig = go.Figure(go.Histogram(x=df['pct_modificados']*100, nbinsx=30, marker=dict(color=C['accent5'], opacity=.85)))
                fig.update_layout(**PL, height=280, title=dict(text='<b>% contratos modificados</b> por empresa', font=dict(size=13), x=0),
                    xaxis=dict(title='%', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
                st.plotly_chart(fig, use_container_width=True)
            with t2:
                fig = go.Figure(go.Histogram(x=df['n_modificaciones'], nbinsx=30, marker=dict(color=C['accent2'], opacity=.85)))
                fig.update_layout(**PL, height=280, title=dict(text='<b>Nº modificaciones</b> por empresa', font=dict(size=13), x=0),
                    xaxis=dict(title='Modificaciones', gridcolor=C['grid']), yaxis=dict(title='Freq', gridcolor=C['grid']), bargap=.03)
                st.plotly_chart(fig, use_container_width=True)

    # ── Generic ──
    sc_cols = [c for c in df.columns if any(k in c.lower() for k in ['score','parscore','par_score','risk_score','pct_adj','pct_concurrent','board_overlap','cargo_weight','concentracion'])]
    am_cols = [c for c in df.columns if any(k in c.lower() for k in ['importe','amount','pressupost','volumen','imp_'])]
    with st.expander("📈 Distribuciones detalladas"):
        if sc_cols:
            sc = st.selectbox("Score/métrica", sc_cols, key="sc_det")
            fig = pl_score(df, sc, f"Distribución: {sc}")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                v = df[sc].dropna()
                s1, s2, s3, s4 = st.columns(4)
                with s1: st.metric("Media", f"{v.mean():.2f}")
                with s2: st.metric("Mediana", f"{v.median():.2f}")
                with s3: st.metric("P90", f"{v.quantile(.9):.2f}")
                with s4: st.metric("Max", f"{v.max():.2f}")
        if am_cols:
            ac = st.selectbox("Importe", am_cols, key="am_det")
            fig = pl_amt_df(df, ac)
            if fig: st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="sec">Explorar datos</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1: scol = st.selectbox("Buscar en", ['(todo)'] + list(df.columns), key="sr_c")
    with fc2: sterm = st.text_input("Término", key="sr_t")
    with fc3: sort_sel = st.selectbox("Ordenar por", ['(original)'] + sc_cols + am_cols, key="sr_s")
    ddf = df.copy()
    if scol != '(todo)' and sterm:
        ddf = ddf[ddf[scol].astype(str).str.contains(sterm, case=False, na=False)]
    elif sterm:
        mask = pd.Series(False, index=ddf.index)
        for col in ddf.select_dtypes(include=['object']).columns:
            mask |= ddf[col].astype(str).str.contains(sterm, case=False, na=False)
        ddf = ddf[mask]
    if sterm: st.caption(f"🔍 {len(ddf):,} de {len(df):,}")
    if sort_sel != '(original)' and sort_sel in ddf.columns: ddf = ddf.sort_values(sort_sel, ascending=False)
    st.dataframe(ddf.head(500), use_container_width=True, height=500, hide_index=True)

    with st.expander("🔎 Buscar empresa en todos los análisis"):
        q = st.text_input("Nombre de empresa (parcial)", key="xf_q")
        if q:
            results = []
            for s, fi in flags.items():
                try:
                    df_tmp = load_pq(fi['path'])
                    for col in df_tmp.select_dtypes(include=['object']).columns:
                        n = df_tmp[col].astype(str).str.contains(q, case=False, na=False).sum()
                        if n > 0:
                            results.append({'Flag': get_flag_meta(s)['label'], 'Archivo': s, 'Coincidencias': n, 'Campo': col, 'Ámbito': fi['scope']})
                            break
                except Exception: pass
            if results: st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
            else: st.info(f"'{q}' no encontrado en ningún análisis.")


# ═══════════════════════════════════════════════════════════════
# TAB: METODOLOGÍA (expanded)
# ═══════════════════════════════════════════════════════════════
def render_meth():
    st.markdown(f"""
    <div class="disc"><strong>Nota:</strong> Esta pestaña documenta el pipeline completo de <strong>cruce
    BORME × Contratación Pública</strong>. Consiste en filtros deterministas — no es un modelo
    estadístico ni de machine learning. Un score alto indica un patrón que merece revisión humana,
    <strong>no constituye prueba de irregularidad</strong>.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">1. Fuentes de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc"><strong>BORME — Boletín Oficial del Registro Mercantil</strong><br><br>
    17.1M filas parseadas de PDFs del BORME-A (2009–2026):<br>
    <code>borme_cargos.parquet</code> — 3.8M personas únicas. Cada fila es un acto (nombramiento, cese,
    reelección, revocación, cancelación) vinculado a persona × empresa × cargo × fecha.<br>
    <code>borme_empresas.parquet</code> — 9.2M filas de actos societarios: constitución, fusión, absorción,
    escisión, disolución, concurso de acreedores, cambio de domicilio, ampliación/reducción de capital.</div>
    <div class="mc"><strong>PLACSP — Plataforma de Contratación del Sector Público</strong><br><br>
    <code>licitaciones_espana.parquet</code> — 8.7M registros (2012–2026), 48 columnas.
    Se filtran adjudicaciones con importe &gt; 0 y adjudicatario identificado → 5.8M registros útiles.
    23.931 órganos contratantes, colapsados a 23.304 tras normalización (627 duplicados detectados).</div>
    <div class="mc"><strong>Contratación Catalunya</strong><br><br>
    <code>contratos_registro.parquet</code> (~3.4M registros, 50 columnas) del Registre Públic de Contractes.<br>
    <code>contratos_menores_bcn.parquet</code> (~177K) del Portal de Transparència de Barcelona.<br>
    Se unifican con mapeo de columnas: catalán → castellano normalizado.</div>
    <div class="mc"><strong>Flags pre-computados (F1–F5) — BORME</strong><br><br>
    <code>F1</code> Empresa constituida &lt;6 meses antes de su primer contrato público<br>
    <code>F2</code> Capital social &lt;3.000€ y contrato significativo (&gt;50K€)<br>
    <code>F3</code> Empresa con múltiples administradores en períodos cortos<br>
    <code>F4</code> Acto de disolución publicado en BORME<br>
    <code>F5</code> Declaración de concurso de acreedores publicada</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">2. Normalización de nombres</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc mc-acc"><strong>2.1 normalize_empresa()</strong> — Función central de matching<br><br>
    Pipeline secuencial aplicado a todos los nombres de empresa (BORME y contratación):<br><br>
    <span class="step-num">1</span> <strong>Mayúsculas + Unicode NFC</strong><br>
    <code>"Construcciones García, S.L."</code> → <code>"CONSTRUCCIONES GARCIA, S.L."</code><br><br>
    <span class="step-num">2</span> <strong>Eliminar acentos</strong> (preservando Ñ)<br>
    <code>"GARCÍA"</code> → <code>"GARCIA"</code> · <code>"MUÑOZ"</code> → <code>"MUÑOZ"</code><br><br>
    <span class="step-num">3</span> <strong>Limpiar sufijos R.M.</strong> (Registro Mercantil)<br>
    regex: <code>\\(R\\.M\\.?[^)]*\\)</code> → eliminado<br>
    <code>"EMPRESA SL (R.M. PALMA DE MALLORCA)"</code> → <code>"EMPRESA SL"</code><br><br>
    <span class="step-num">4</span> <strong>Colapsar formas societarias</strong><br>
    <code>S.L., S.L.U., SOC. LIMITADA, SOCIEDAD LIMITADA</code> → eliminados<br>
    <code>S.A., S.A.U., SOCIEDAD ANONIMA</code> → eliminados<br>
    Catalán: <code>S.C.P., S.C.C.L., SOCIETAT COOPERATIVA</code> → eliminados<br>
    Otros: <code>S.COM., S.COOP., S.R.L., A.I.E.</code> → eliminados<br><br>
    <span class="step-num">5</span> <strong>Eliminar sufijos adicionales</strong><br>
    <code>EN LIQUIDACION, EN DISOLUCION, EN CONCURSO, SUCURSAL EN ESPAÑA</code><br><br>
    <span class="step-num">6</span> <strong>Strip puntuación y espacios</strong><br>
    Comas, puntos, guiones → espacios → colapsar múltiples espacios → strip<br><br>
    Ejemplo completo:<br>
    <code>"Construcciones García López, S.L.U. (R.M. Madrid)"</code><br>
    → <code>"CONSTRUCCIONES GARCIA LOPEZ"</code></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="mc mc-grn"><strong>2.2 Stop Words — Data-driven</strong><br><br>
    Función <code>build_stop_words(cargos_df, threshold=0.005)</code>:<br><br>
    <span class="step-num">A</span> <strong>Auto-generadas:</strong> Tokeniza las 2.77M empresas únicas del BORME.
    Tokens que aparecen en &gt;0.5% de empresas → genérico → stop word. Resultado: ~5.400 tokens auto-detectados.
    Incluye tokens ≤2 caracteres y números puros.<br><br>
    <span class="step-num">B</span> <strong>Curadas manualmente:</strong> 203 términos trilingües (ES/CAT/EN):<br>
    · <em>Legal:</em> SA, SL, SLU, SAU, SICAV, SOCIMI, AIE, SCR, SGIIC...<br>
    · <em>Sector:</em> SERVICIOS, SOLUCIONES, PROYECTOS, GESTION, CONSTRUCCIONES, INGENIERIA, CONSULTING...<br>
    · <em>Geográfico:</em> ESPAÑA, IBERIA, EUROPEA, INTERNACIONAL, GLOBAL, PENINSULAR, MEDITERRANEO...<br>
    · <em>Corporativo:</em> GRUPO, HOLDING, CORPORACION, EMPRESA, ASOCIADOS, PARTICIPACIONES...<br>
    · <em>Inglés:</em> SYSTEMS, SOLUTIONS, MANAGEMENT, ENERGY, CAPITAL, SERVICES, TECHNOLOGIES...<br>
    · <em>Catalán:</em> SERVEIS, OBRES, CATALANES, CATALANA, VALENCIANA...<br><br>
    <span class="step-num">C</span> <strong>Unión:</strong> 5.400 auto ∪ 203 curadas = ~5.550 stop words totales (42 overlap).<br>
    Se usan en F6 para evitar que tokens como "SERVICIOS" vinculen empresas no relacionadas.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="mc mc-wrn"><strong>2.3 Pesos de cargo — Regex-based</strong><br><br>
    Reemplazo del diccionario hardcoded por reglas regex. Primera coincidencia gana:<br><br>
    <div class="formula" style="font-size:.68rem">
    10: <code>ADM.*UNIC</code> → Administrador Único, Adm. Unico, ADM.UNICO...<br>
    &nbsp;9: <code>LIQUIDADOR</code><br>
    &nbsp;8: <code>ADM.*SOLID|ADM.*MANCOM</code> → Solidario, Mancomunado<br>
    &nbsp;7: <code>CONS.*DELEG|CONSEJERO.*DELEGAD</code><br>
    &nbsp;6: <code>PRESIDENTE</code><br>
    &nbsp;5: <code>VICEPRESID|GERENTE|DIRECTOR.*GEN</code><br>
    &nbsp;4: <code>SOCIO\\s*UNIC</code><br>
    &nbsp;3: <code>CONSEJERO|VOCAL</code><br>
    &nbsp;2: <code>SOCIO|SOC\\.\\s*PROF|MIEMBR</code><br>
    &nbsp;1: <code>SECRETARI|APODERAD|REPRESENTANT</code><br>
    &nbsp;0: Sin coincidencia (default)
    </div>
    Esto captura variantes como <code>"Adm. Unico"</code>, <code>"ADM.UNICO"</code>,
    <code>"ADMINISTRADOR UNICO"</code>, <code>"Apo.Sol."</code>, <code>"APOD.MANCOMU"</code>, etc.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">3. Pipeline de detección F6 — Red de administradores</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc mc-acc"><span class="step-num">1</span> <strong>Intersección BORME ∩ Contratación</strong><br><br>
    Cruce por nombre normalizado. Nacional: 126.073 empresas en ambos datasets.<br>
    Catalunya: 23.156 empresas matched. Solo empresas con ≥3 adjudicaciones.</div>

    <div class="mc mc-acc"><span class="step-num">2</span> <strong>Cargos vigentes</strong><br><br>
    17.1M actos BORME → unificados: 11.0M nombramientos + 6.1M ceses. Para cada terna (persona, empresa, cargo)
    se toma el <strong>último acto</strong>. Si es nombramiento/reelección → vigente. Si es cese/revocación → inactivo.<br>
    Nacional: 618.577 cargos activos → filtro de decisión (eliminar apoderados/representantes) → 232.493.<br>
    Filtro personas jurídicas (S.L., GMBH, LTD en el nombre) → 211.843 cargos finales.</div>

    <div class="mc mc-acc"><span class="step-num">3</span> <strong>Detectar pares sospechosos</strong><br><br>
    Personas con 2–50 empresas (excluir &gt;50 para evitar consejeros profesionales masivos).<br>
    Para cada persona: combinaciones de pares de sus empresas → retener si comparten ≥2 órganos contratantes.<br>
    Nacional: 7.514 personas multi-empresa → 3.970 pares con ≥2 órganos comunes.<br>
    Análisis temporal: para cada par, % de órganos con adjudicaciones concurrentes (±365 días).</div>

    <div class="mc mc-grn"><span class="step-num">4</span> <strong>Filtrar grupos corporativos</strong> (falsos positivos legítimos)<br><br>
    <strong>a) Nombre de marca:</strong> Tokenizar ambos nombres, calcular Jaccard similarity en tokens
    no-stop-word. Si Jaccard ≥0.5 → grupo corporativo. Incluye check de "primera palabra de marca" y
    containment (PAVASAL ⊂ PAVASAL EMPRESA CONSTRUCTORA).<br>
    <strong>b) Solapamiento consejo:</strong> Para cada par de empresas, calcular % de personas compartidas
    en el consejo. Si &gt;40% overlap Y ≥3 personas compartidas → grupo corporativo.<br>
    <strong>c) Fusiones BORME:</strong> Si ambas empresas tienen actos de fusión/absorción/escisión → grupo.<br>
    Nacional: 3.970 → 2.287 pares (1.683 eliminados: 953 por nombre, 902 por consejo, 287 por fusiones).</div>

    <div class="mc mc-acc"><span class="step-num">5</span> <strong>Enriquecer pares</strong><br><br>
    Cada par recibe: peso del cargo (1–10 regex), flags F1–F5, nº adjudicaciones por empresa,
    importe total, concentración (órganos comunes / min órganos), % temporal concurrente.</div>

    <div class="mc mc-wrn"><span class="step-num">6</span> <strong>Scoring de pares</strong></div>
    <div class="formula">
    score = concentración × √(n_órganos_comunes) × flag_weight × (cargo_weight / 5)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;× 1/log(1 + max_adj/5) × √(importe_par / 10K)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;× solo_admin_bonus × temporal_bonus<br><br>
    <span style="color:{C['text2']}">Flag weights (multiplicativos): F1 ×4.0 · F5 ×3.0 · F4 ×2.5 · F2 ×2.0</span><br>
    <span style="color:{C['text2']}">Solo_admin_bonus: ×1.5 si la persona es el único decisor en ambas empresas</span><br>
    <span style="color:{C['text2']}">Temporal_bonus: 1 + 0.5 × pct_concurrent (hasta ×1.5 si 100% concurrente)</span><br>
    <span style="color:{C['text2']}">Agregación persona: par_score = score_max × log₂(1 + n_personas)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">4. Flags adicionales (F7–F11)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc"><strong>F7 — Concentración de adjudicaciones</strong><br><br>
    Para cada par empresa×órgano: % de adjudicaciones del órgano ganadas por esa empresa.<br>
    · Nacional: umbral fijo &gt;40%, mínimo 5 adj propias y 10 del órgano. Resultado: 358 pares, 286 empresas.<br>
    · Catalunya: adaptativo según tamaño — ≥200 adj → 20%, ≥50 → 30%, &lt;50 → 40%.</div>

    <div class="mc"><strong>F8 — UTEs sospechosas</strong><br><br>
    Detección de UTEs (Uniones Temporales de Empresas) cuyos miembros comparten administrador:<br>
    1. Regex: <code>U\\.?T\\.?E\\.?|UNIÓN TEMPORAL|AGRUPACIÓN TEMPORAL</code><br>
    2. Parseo de miembros del nombre de la UTE (separadores: <code>- / y &amp;</code>)<br>
    3. Normalización de cada miembro → cruce con red F6<br>
    Nacional: 69.520 adj a UTEs → 13.684 parseables → 127 pares con admin compartido.<br>
    Catalunya: 17.292 adj a UTEs → 4.025 parseables → 0 matches (nombres UTE no normalizan a BORME).</div>

    <div class="mc"><strong>F9 — Discrepancia geográfica</strong> <span class="qg qg-wn">Nacional</span><br><br>
    Provincia BORME → CCAA de registro. NUTS2 del contrato → CCAA mayoritaria de contratos.<br>
    Flag si CCAA registro ≠ CCAA principal de contratos. Solo PYMEs (3–200 adj).<br>
    Resultado: 14.832 empresas con discrepancia geográfica de 27.465 con CCAA mapeada.</div>

    <div class="mc"><strong>F10 — Troceo</strong> <span class="qg qg-wn">Catalunya</span><br><br>
    Fraccionamiento de contratos para evadir umbrales de procedimiento:<br>
    Sliding window de 90 días → empresa×órgano con ≥3 contratos, todos ≤15.000€ (umbral contrato menor),
    cuya suma supera el umbral.<br>
    81.348 pares empresa×órgano analizados → 4.331 clusters de troceo, 2.651 empresas flaggeadas.<br>
    Media cluster: 33K€ (2.2× sobre el umbral).</div>

    <div class="mc"><strong>F11 — Modificaciones excesivas</strong> <span class="qg qg-wn">Catalunya</span><br><br>
    Usa columnas nativas del registro catalán: Número/Tipus/Import de modificació.<br>
    Flag si empresa tiene ≥3 modificaciones Y ≥20% de sus contratos modificados.<br>
    (Promedio catalán: ~0.57% de contratos con modificación.)<br>
    Resultado: 115 empresas flaggeadas.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">5. Scoring unificado por empresa</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="formula">
    <strong>Nacional:</strong><br>
    risk_score = F1×3.0 + F2×0.5 + F4×2.0 + F5×2.0 + min(f6_par_score/50, 10) + F7×5.0 + F8×3.0 + F9×1.0<br><br>
    <strong>Catalunya:</strong><br>
    risk_score = F1×3.0 + F2×0.5 + F4×2.0 + F5×2.0 + min(f6_par_score/50, 10) + F7×5.0 + F8×3.0 + F10×2.5 + F11×1.5
    </div>
    <div class="mc">
    Solo empresas con ≥1 flag. Nacional: 25.675 empresas (125 con ≥3 flags). Catalunya: 4.203 empresas.<br><br>
    <strong>Distribución Nacional:</strong> F9 geo (14.832) &gt; F2 capital (5.735) &gt; F1 recién creada (5.435)
    &gt; F4 disolución (1.294) &gt; F5 concursal (540) &gt; F7 concentración (286) &gt; F8 UTEs (97).<br>
    <strong>Distribución Catalunya:</strong> F10 troceo (2.651) &gt; F2 (1.032) &gt; F6 red (571) &gt; F4 (174)
    &gt; F1 (163) &gt; F11 modificaciones (115) &gt; F5 (22) &gt; F7 (10).</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">6. Diferencias Nacional vs Catalunya</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc">
    <strong>Datos:</strong> Nacional = PLACSP 5.8M adj con importe · Catalunya = Registro 3.4M + Menores BCN 177K<br>
    <strong>Matching:</strong> Nacional 126.073 empresas cruzadas · Catalunya 23.156<br>
    <strong>F7:</strong> Nacional umbral fijo 40% · Catalunya adaptativo 20/30/40%<br>
    <strong>Normalización:</strong> Catalunya incluye formas catalanas (S.C.P., S.C.C.L., SOCIETAT COOPERATIVA…)<br>
    <strong>Exclusivo Nacional:</strong> F9 discrepancia geográfica<br>
    <strong>Exclusivo Catalunya:</strong> F10 troceo (datos de contratos menores), F11 modificaciones (columnas nativas)<br>
    <strong>Ambos:</strong> F1–F8, scoring unificado, filtro grupos corporativos</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">7. Resultados clave</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc">
    <strong>Nacional:</strong> 2.287 pares persona×empresa sospechosos (1.878 pares únicos de empresas,
    1.416 personas únicas, 2.684 empresas). 677 pares con ≥1 flag adicional. Top score: 8.758 (CURENERGIA × IBERDROLA).<br><br>
    <strong>Catalunya:</strong> 439 pares (353 únicos). Top score: 7.5 (SILUJ ILUMINACION, F1+F4+F10).
    F10 troceo es el flag dominante (63% de flaggeadas).<br><br>
    <strong>Grupos corporativos filtrados:</strong> Nacional 1.683 pares legítimos eliminados. Catalunya 295.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">8. Limitaciones</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc">
    <strong>Cobertura:</strong> ~52% de adjudicatarios PLACSP cruzados con BORME. Autónomos, personas físicas y
    empresas extranjeras no figuran en BORME.<br>
    <strong>Matching:</strong> Por nombre normalizado, no por NIF (no disponible en BORME). Posibles falsos
    positivos (homónimos) y falsos negativos (variantes no capturadas).<br>
    <strong>Vigencia cargos:</strong> Depende de que el cese se publique en BORME. Cargos no cesados
    explícitamente aparecen como vigentes aunque hayan terminado de facto.<br>
    <strong>Grupos corporativos:</strong> Filtros heurísticos. Grupos complejos con holdings intermedios
    pueden no detectarse.<br>
    <strong>F10 troceo:</strong> Solo ventana de 90 días y umbral 15K€. Troceo más sofisticado
    (diferentes órganos, plazos más largos) no se detecta.<br>
    <strong>Score ≠ fraude.</strong> Un patrón estadístico que requiere investigación humana cualificada.</div>

    <div class="disc"><strong>Descargo de responsabilidad</strong><br><br>
    Datos públicos de PLACSP, Registre Públic de Contractes de Catalunya, Portal de Transparència de Barcelona
    y BORME. <strong>No vinculado</strong> a estos organismos.
    Puede contener errores derivados del parsing automático de documentos.
    <strong>Un score alto NO es prueba de irregularidad.</strong> Este es un ejercicio de análisis de datos
    con fines educativos y de transparencia.</div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# RENDER: Company Profile
# ═══════════════════════════════════════════════════════════════
def render_company_profile(flags):
    """Full company investigation page."""
    st.markdown('<div class="sec">Investigar empresa</div>', unsafe_allow_html=True)
    q = st.text_input("🔍 Buscar empresa", key="cp_q", placeholder="Escribe el nombre de una empresa...")
    if not q or len(q) < 3:
        st.markdown(f"<div class='mc'>Introduce al menos 3 caracteres. La búsqueda cruza el nombre en todos los análisis y muestra un resumen completo: señales activas, conexiones, órganos donde licita y detalle por cada señal.</div>",
                    unsafe_allow_html=True)
        return

    with st.spinner("Buscando..."):
        prof = build_company_profile(q, flags)

    if not prof['flags_active']:
        st.info(f"'{q}' no encontrado en ningún análisis.")
        return

    # ── Header ──
    n_flags = len(prof['flags_active'])
    max_sc = max(prof['scores'].values()) if prof['scores'] else 0
    total_hits = sum(f['n_hits'] for f in prof['flags_active'])

    st.markdown(f"""
    <div class="fcard">
        <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:700;color:{C['text']};margin-bottom:4px">
            {prof['nombre'][:60]}</div>
        <div style="font-size:.8rem;color:{C['text2']}">
            Aparece en <b style="color:{C['accent']}">{n_flags}</b> análisis ·
            <b style="color:{C['text']}">{total_hits}</b> coincidencias ·
            Max score: <b style="color:{C['accent']}">{max_sc:.1f}</b></div>
    </div>""", unsafe_allow_html=True)

    # ── Flag badges ──
    badges = ''.join(f'<span class="fb {f["icon"]}">{f["icon"]} {f["flag"]} · {f["scope"]} ({f["n_hits"]})</span> '
                     for f in prof['flags_active'])
    st.markdown(f"<div style='margin:10px 0'>{badges}</div>", unsafe_allow_html=True)

    # ── Scores ──
    if prof['scores']:
        st.markdown('<div class="sec">Scores</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(prof['scores']), 6))
        for i, (k, v) in enumerate(prof['scores'].items()):
            with cols[i % len(cols)]:
                st.metric(k, f"{v:.2f}")

    # ── Connections (F6) ──
    if prof['connections']:
        st.markdown('<div class="sec">Empresas conectadas por administrador</div>', unsafe_allow_html=True)
        conn_df = pd.DataFrame(prof['connections']).sort_values('score', ascending=False)
        st.dataframe(conn_df.head(20), use_container_width=True, hide_index=True)

    # ── Órganos ──
    if prof['organos']:
        with st.expander(f"📍 Órganos contratantes ({len(prof['organos'])})"):
            for o in prof['organos'][:50]:
                st.caption(f"· {o}")

    # ── Detail per flag ──
    if prof['details']:
        st.markdown('<div class="sec">Detalle por análisis</div>', unsafe_allow_html=True)
        for stem, detail_df in prof['details'].items():
            meta = get_flag_meta(stem)
            with st.expander(f"{meta['icon']} {meta['label']} — {len(detail_df)} registros"):
                st.dataframe(detail_df, use_container_width=True, hide_index=True, height=250)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🏛️ Contratación <span>Pública</span> España</div>
        <div class="hero-sub">BQuant Finance · @Gsnchez</div>
        <div class="hero-context">
            Cruzamos <b>8.7 millones de contratos públicos</b> con <b>17 millones de actos
            del Registro Mercantil</b> para detectar patrones que merecen atención.
        </div>
        <div class="hero-line"></div>
    </div>
    """, unsafe_allow_html=True)

    placsp_prof = load_json(str(Q_DIR/"placsp_profile.json")) if (Q_DIR/"placsp_profile.json").exists() else None
    cat_prof = load_json(str(Q_DIR/"cat_profile.json")) if (Q_DIR/"cat_profile.json").exists() else None
    flags = discover_flags()

    tabs = st.tabs(["📊 Resumen", "🔎 Explorar", "📋 Cómo funciona"])

    # ══════════════════════════════════════════════════════════
    # TAB 1: RESUMEN — narrative flow
    # ══════════════════════════════════════════════════════════
    with tabs[0]:
        if not placsp_prof and not cat_prof and not flags:
            st.markdown("<div class='mc'>Sin datos. Ejecuta <code>precompute_quality.py</code> y coloca parquets en <code>anomalias/</code>.</div>", unsafe_allow_html=True)
        else:
            # ── 1. ¿Qué es esto? ──
            st.markdown(f"""
            <div class="intro-q">
                <span class="iq-icon">🔍</span> <b>¿Qué tipo de patrones buscamos?</b><br><br>
                <span class="iq-icon">🕸️</span> Dos empresas que comparten administrador ganan contratos
                en los mismos organismos públicos — y no son del mismo grupo empresarial.<br>
                <span class="iq-icon">🆕</span> Una empresa se constituye 3 meses antes de recibir
                su primer contrato público.<br>
                <span class="iq-icon">✂️</span> Un organismo divide un contrato grande en varios pequeños
                para evadir el umbral de licitación pública.<br>
                <span class="iq-icon">📍</span> Una empresa registrada en Málaga solo gana contratos
                en el País Vasco.<br><br>
                <span style="font-size:.75rem;color:{C['muted']}">Ninguno de estos patrones es prueba de
                irregularidad. Son señales estadísticas que merecen revisión humana.</span>
            </div>
            """, unsafe_allow_html=True)

            # ── 2. La historia en números ──
            hs_path = Q_DIR / "headline_stats.json"
            if hs_path.exists():
                hs = load_json(str(hs_path))

                st.markdown('<div class="sec">Lo que hemos encontrado</div>', unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Pares sospechosos", fmt(hs.get('n_pares_nacional', 0)))
                with c2: st.metric("Empresas implicadas", fmt(hs.get('n_empresas_red_nacional', 0)))
                with c3: st.metric("Empresas con señal de alerta", fmt(hs.get('n_risk_nacional', 0)))
                with c4: st.metric("Discrepancia geográfica", fmt(hs.get('n_geo', 0)))

                # Narrative facts
                facts = []
                imp_nac = hs.get('importe_pares_nacional', 0)
                if imp_nac > 0:
                    facts.append(f"💰 <b>{imp_nac/1e6:,.0f}M€</b> en contratos adjudicados a empresas que comparten administrador sin ser del mismo grupo corporativo.")
                tp = hs.get('top_persona_nacional')
                if tp:
                    facts.append(f"👤 La persona con más conexiones vincula <b>{tp[1]} pares</b> de empresas que licitan ante los mismos organismos.")
                mo = hs.get('max_organos_nacional')
                if mo:
                    facts.append(f"🏛️ Hay pares de empresas con administrador común que coinciden en hasta <b>{mo} órganos contratantes</b>.")
                tc = hs.get('top_concentracion_nacional')
                if tc:
                    facts.append(f"🎯 <b>{tc[0]}</b> acumula el <b>{tc[1]:.0f}%</b> de las adjudicaciones de un órgano contratante.")
                mf = hs.get('multi_flag_nacional', 0)
                if mf:
                    facts.append(f"🚩 <b>{mf} empresas</b> acumulan 3 o más señales de alerta simultáneamente.")
                ti_val = hs.get('troceo_importe', 0)
                tc_val = hs.get('troceo_clusters', 0)
                if ti_val > 0:
                    facts.append(f"✂️ En Catalunya se detectan <b>{tc_val:,} posibles fraccionamientos</b> de contratos por un total de <b>{ti_val/1e6:,.1f}M€</b> — todos los contratos individuales están bajo el umbral de 15.000€.")

                for f in facts:
                    st.markdown(f"<div class='fcard' style='padding:12px 18px;font-size:.84rem;color:{C['text2']};line-height:1.6'>{f}</div>",
                                unsafe_allow_html=True)

            # ── 3. Comparador ──
            comp_path = Q_DIR / "comparador.json"
            if comp_path.exists():
                comp_data = load_json(str(comp_path))
                if comp_data and comp_data.get('n_common', 0) > 0:
                    st.markdown('<div class="sec">¿Coinciden en Nacional y Catalunya?</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="graph-caption">De las {comp_data["n_common"]:,} empresas que aparecen en ambos ámbitos, el heatmap muestra qué combinaciones de señales Nacional × Catalunya son más frecuentes. Celdas más cálidas = más empresas con esa combinación.</div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("En señales Nacional", fmt(comp_data['n_nac']))
                    with c2: st.metric("En señales Catalunya", fmt(comp_data['n_cat']))
                    with c3: st.metric("En ambos ámbitos", fmt(comp_data['n_common']))

                    cdf = pd.DataFrame(comp_data['empresas'])
                    if len(cdf) > 2:
                        fig_comp = pl_comparador_scatter(cdf)
                        if fig_comp:
                            st.plotly_chart(fig_comp, use_container_width=True)
                    with st.expander(f"📋 Ver listado ({comp_data['n_common']} empresas)"):
                        show_cols = ['empresa','flags_nac','flags_cat','score_nac','score_cat','total_flags']
                        avail = [c for c in show_cols if c in cdf.columns]
                        st.dataframe(cdf[avail].head(50), use_container_width=True, hide_index=True)

            # ── 4. Buscar ──
            st.markdown('<div class="sec">Buscar empresa o persona</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:.8rem;color:{C['text2']};margin-bottom:8px'>Busca en todos los análisis a la vez. Escribe un nombre y verás en qué señales aparece.</div>", unsafe_allow_html=True)
            q = st.text_input("🔍", key="univ_q", placeholder="Ej: IBERDROLA, MARTI SOLER, AENA...", label_visibility="collapsed")
            if q and len(q) >= 3:
                with st.spinner("Buscando..."):
                    results = search_all_flags(q, flags)
                if results:
                    st.markdown(f"<div style='margin:8px 0;font-size:.82rem;color:{C['text2']}'>"
                        f"<b style='color:{C['text']}'>{len(results)}</b> análisis con coincidencias para "
                        f"<b style='color:{C['accent']}'>{q}</b></div>", unsafe_allow_html=True)
                    for r in results:
                        sc_str = f" · Score: <b style='color:{C['accent']}'>{r['max_score']:.1f}</b>" if r['max_score'] else ""
                        st.markdown(f"<div class='fcard'><span class='fb {r['css']}'>{r['icon']} {r['label']}</span> "
                            f"<span style='color:{C['text2']};font-size:.78rem'>{r['scope']} · "
                            f"{r['hits']} coincidencias{sc_str}</span></div>", unsafe_allow_html=True)
                        with st.expander(f"Ver datos ({r['stem']})"):
                            st.dataframe(r['sample'], use_container_width=True, hide_index=True)
                else:
                    st.info(f"'{q}' no encontrado en ningún análisis.")

            # ── 5. Datasets (compact) ──
            with st.expander("📂 Datos utilizados"):
                for p in [placsp_prof, cat_prof]:
                    if p:
                        st.markdown(f"<div class='fcard'><div style='font-family:\"Outfit\",sans-serif;font-size:.9rem;font-weight:700;color:{C['text']};margin-bottom:4px'>{p['name']}</div>"
                            f"<div style='font-size:.78rem;color:{C['text2']}'><b style='color:{C['text']}'>{p['n']:,}</b> registros · {p['nc']} columnas · Completitud: {qb(p['completitud'])} · Duplicados: {p['dupe_pct']:.2f}%</div></div>", unsafe_allow_html=True)
                if placsp_prof and cat_prof:
                    comp = pd.DataFrame({
                        'Métrica': ['Registros','Columnas','Completitud (%)','Duplicados (%)'],
                        'PLACSP': [f"{placsp_prof['n']:,}", placsp_prof['nc'], f"{placsp_prof['completitud']:.1f}", f"{placsp_prof['dupe_pct']:.2f}"],
                        'Catalunya': [f"{cat_prof['n']:,}", cat_prof['nc'], f"{cat_prof['completitud']:.1f}", f"{cat_prof['dupe_pct']:.2f}"]})
                    st.dataframe(comp, use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════
    # TAB 2: EXPLORAR — flags + ficha empresa + quality
    # ══════════════════════════════════════════════════════════
    with tabs[1]:
        explore_section = st.radio("", ["🚩 Señales de alerta", "🔎 Ficha de empresa", "📊 Calidad de datos"],
                                   horizontal=True, label_visibility="collapsed")

        if explore_section == "🚩 Señales de alerta":
            render_flags(flags)

        elif explore_section == "🔎 Ficha de empresa":
            render_company_profile(flags)

        elif explore_section == "📊 Calidad de datos":
            if placsp_prof or cat_prof:
                if placsp_prof and cat_prof:
                    ds_tab = st.radio("Dataset", ["PLACSP — Nacional", "Catalunya"], horizontal=True, label_visibility="collapsed")
                    if "PLACSP" in ds_tab:
                        render_quality(placsp_prof, "PLACSP")
                    else:
                        render_quality(cat_prof, "Catalunya")
                elif placsp_prof:
                    render_quality(placsp_prof, "PLACSP")
                else:
                    render_quality(cat_prof, "Catalunya")
            else:
                st.info("No hay perfiles de calidad. Ejecuta precompute_quality.py.")

    # ══════════════════════════════════════════════════════════
    # TAB 3: CÓMO FUNCIONA — methodology
    # ══════════════════════════════════════════════════════════
    with tabs[2]:
        render_meth()

    st.markdown(f"<div class='ft'><a href='https://twitter.com/Gsnchez'>@Gsnchez</a> · <a href='https://bquantfinance.com'>bquantfinance.com</a> · <a href='https://github.com/BquantFinance'>GitHub</a></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
