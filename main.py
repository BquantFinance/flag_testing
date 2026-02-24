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
    letter-spacing:.2em; text-transform:uppercase;
}}
.hero-line {{ height:1px; background:linear-gradient(90deg,transparent,{C['border2']},transparent); margin:1.5rem auto; max-width:500px }}

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
    'flag1_recien_creada':     {'label':'F1 Recién creada',       'icon':'🆕', 'css':'fb-r',  'short':'F1'},
    'flag2_capital_ridiculo':  {'label':'F2 Capital ridículo',    'icon':'💰', 'css':'fb-w',  'short':'F2'},
    'flag3_multi_admin':       {'label':'F3 Multi-admin',         'icon':'👥', 'css':'fb-p',  'short':'F3'},
    'flag4_disolucion':        {'label':'F4 Disolución',          'icon':'💀', 'css':'fb-r',  'short':'F4'},
    'flag5_concursal':         {'label':'F5 Concursal',           'icon':'⚖️', 'css':'fb-r',  'short':'F5'},
    # F6 network
    'flag6_admin_network':     {'label':'F6 Red admin (detalle)', 'icon':'🕸️', 'css':'fb-b',  'short':'F6'},
    'flag6_admin_network_cat': {'label':'F6 Red admin CAT',       'icon':'🕸️', 'css':'fb-b',  'short':'F6'},
    'flag6_pares_unicos':      {'label':'F6 Pares empresas',      'icon':'🔗', 'css':'fb-b',  'short':'F6'},
    'flag6_pares_cat':         {'label':'F6 Pares CAT',           'icon':'🔗', 'css':'fb-b',  'short':'F6'},
    'flag6_personas_resumen':  {'label':'F6 Personas ranking',    'icon':'👤', 'css':'fb-b',  'short':'F6'},
    'flag6_personas_cat':      {'label':'F6 Personas CAT',        'icon':'👤', 'css':'fb-b',  'short':'F6'},
    # F7–F11
    'flag7_concentracion':     {'label':'F7 Concentración',       'icon':'🎯', 'css':'fb-g',  'short':'F7'},
    'flag7_concentracion_cat': {'label':'F7 Concentración CAT',   'icon':'🎯', 'css':'fb-g',  'short':'F7'},
    'flag8_utes_sospechosas':  {'label':'F8 UTEs sospechosas',    'icon':'🤝', 'css':'fb-w',  'short':'F8'},
    'flag8_utes_cat':          {'label':'F8 UTEs CAT',            'icon':'🤝', 'css':'fb-w',  'short':'F8'},
    'flag9_geo_discrepancia':  {'label':'F9 Discrepancia geo',    'icon':'📍', 'css':'fb-p',  'short':'F9'},
    'flag10_troceo_cat':       {'label':'F10 Troceo CAT',         'icon':'✂️', 'css':'fb-r',  'short':'F10'},
    'flag11_modificaciones_cat':{'label':'F11 Modificaciones CAT','icon':'📝', 'css':'fb-w',  'short':'F11'},
    # Scoring & grupos
    'risk_scoring_unificado':  {'label':'Scoring unificado',      'icon':'📊', 'css':'fb-r',  'short':'Risk'},
    'risk_scoring_cat':        {'label':'Scoring CAT',            'icon':'📊', 'css':'fb-r',  'short':'Risk'},
    'grupos_corporativos':     {'label':'Grupos corporativos',    'icon':'🏢', 'css':'fb-b',  'short':'Grp'},
    'grupos_corporativos_cat': {'label':'Grupos corp. CAT',       'icon':'🏢', 'css':'fb-b',  'short':'Grp'},
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
# 3D NETWORK GRAPH — neon glow effects
# ═══════════════════════════════════════════════════════════════
def pl_network_3d(df_pares, max_nodes=60):
    """3D force-directed network with neon glow layers."""
    if 'empresa_1' not in df_pares.columns:
        return None

    top = df_pares.head(max_nodes)
    nodes = set(); edges = []
    for _, r in top.iterrows():
        e1 = str(r['empresa_1'])[:30]; e2 = str(r['empresa_2'])[:30]
        nodes.add(e1); nodes.add(e2)
        sc = r.get('par_score', r.get('score_max', 1))
        nf = r.get('n_flags', 0)
        edges.append((e1, e2, sc, nf))
    nodes = list(nodes)
    if len(nodes) < 3: return None

    # ── 3D Force-directed layout ──
    np.random.seed(42)
    pos = {n: np.random.randn(3) * 4 for n in nodes}
    for iteration in range(120):
        forces = {n: np.zeros(3) for n in nodes}
        for i, n1 in enumerate(nodes):
            for n2 in nodes[i+1:]:
                diff = pos[n1] - pos[n2]
                d = max(0.15, np.linalg.norm(diff))
                direction = diff / d
                forces[n1] += direction * (3.0 / d**2)
                forces[n2] -= direction * (3.0 / d**2)
        for e1, e2, sc, _ in edges:
            if e1 in pos and e2 in pos:
                diff = pos[e2] - pos[e1]
                d = max(0.15, np.linalg.norm(diff))
                direction = diff / d
                forces[e1] += direction * d * 0.04
                forces[e2] -= direction * d * 0.04
        for n in nodes:
            d_c = np.linalg.norm(pos[n])
            if d_c > 0.1: forces[n] -= pos[n] / d_c * 0.02
        damping = 0.15 * max(0.3, 1.0 - iteration / 120)
        for n in nodes: pos[n] = pos[n] + forces[n] * damping

    # ── Node metrics ──
    deg = {n: 0 for n in nodes}; flag_count = {n: 0 for n in nodes}; max_score = {n: 0 for n in nodes}
    for e1, e2, sc, nf in edges:
        deg[e1] += 1; deg[e2] += 1
        flag_count[e1] = max(flag_count[e1], nf); flag_count[e2] = max(flag_count[e2], nf)
        max_score[e1] = max(max_score[e1], sc); max_score[e2] = max(max_score[e2], sc)
    max_deg = max(deg.values()) if deg else 1

    fig = go.Figure()

    # ── Edges with intensity color ──
    max_edge_sc = max(sc for _, _, sc, _ in edges) if edges else 1
    for e1, e2, sc, nf in edges:
        intensity = sc / max_edge_sc
        alpha = 0.08 + intensity * 0.35
        width = 1 + intensity * 3
        if nf >= 2:   edge_color = f'rgba(239,68,68,{alpha})'
        elif nf == 1: edge_color = f'rgba(245,158,11,{alpha})'
        else:         edge_color = f'rgba(59,130,246,{alpha})'
        fig.add_trace(go.Scatter3d(
            x=[pos[e1][0], pos[e2][0]], y=[pos[e1][1], pos[e2][1]], z=[pos[e1][2], pos[e2][2]],
            mode='lines', line=dict(width=width, color=edge_color),
            hoverinfo='none', showlegend=False))

    # ── Outer glow (large soft halo) ──
    gx = [pos[n][0] for n in nodes]; gy = [pos[n][1] for n in nodes]; gz = [pos[n][2] for n in nodes]
    glow2_sz = [max(28, min(70, 20 + deg[n]/max_deg*55)) for n in nodes]
    glow2_c = []
    for n in nodes:
        fc = flag_count.get(n, 0)
        if fc >= 2:   glow2_c.append('rgba(239,68,68,.06)')
        elif fc == 1: glow2_c.append('rgba(245,158,11,.05)')
        else:         glow2_c.append('rgba(59,130,246,.04)')
    fig.add_trace(go.Scatter3d(x=gx, y=gy, z=gz, mode='markers',
        marker=dict(size=glow2_sz, color=glow2_c, line=dict(width=0), opacity=1),
        hoverinfo='none', showlegend=False))

    # ── Inner glow ──
    glow1_sz = [max(16, min(48, 14 + deg[n]/max_deg*38)) for n in nodes]
    glow1_c = []
    for n in nodes:
        fc = flag_count.get(n, 0)
        if fc >= 2:   glow1_c.append('rgba(239,68,68,.18)')
        elif fc == 1: glow1_c.append('rgba(245,158,11,.15)')
        else:         glow1_c.append('rgba(59,130,246,.12)')
    fig.add_trace(go.Scatter3d(x=gx, y=gy, z=gz, mode='markers',
        marker=dict(size=glow1_sz, color=glow1_c, line=dict(width=0), opacity=1),
        hoverinfo='none', showlegend=False))

    # ── Main nodes ──
    node_sz = [max(5, min(18, 4 + deg[n]/max_deg*16)) for n in nodes]
    node_c = ['#ef4444' if flag_count.get(n,0)>=2 else '#f59e0b' if flag_count.get(n,0)==1 else '#3b82f6' for n in nodes]
    hover = [f"<b>{n}</b><br>Conexiones: {deg[n]}<br>Max score: {max_score.get(n,0):.0f}<br>Flags: {flag_count.get(n,0)}" for n in nodes]
    fig.add_trace(go.Scatter3d(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], z=[pos[n][2] for n in nodes],
        mode='markers+text', text=[n[:16] for n in nodes],
        textfont=dict(size=7, color=C['text2'], family='JetBrains Mono'), textposition='top center',
        marker=dict(size=node_sz, color=node_c, line=dict(width=1, color='rgba(255,255,255,.2)'), opacity=0.95),
        hovertext=hover, hoverinfo='text', showlegend=False))

    # ── Bright core ──
    core_sz = [max(2, s*0.35) for s in node_sz]
    fig.add_trace(go.Scatter3d(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], z=[pos[n][2] for n in nodes],
        mode='markers', marker=dict(size=core_sz, color='rgba(255,255,255,.7)', line=dict(width=0)),
        hoverinfo='none', showlegend=False))

    ax = dict(showbackground=True, backgroundcolor='rgba(5,6,9,.8)', gridcolor='rgba(255,255,255,.03)',
              zerolinecolor='rgba(255,255,255,.05)', showticklabels=False, title='', showspikes=False)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono, monospace', color=C['text'], size=11),
        margin=dict(l=0, r=0, t=40, b=0), height=620, showlegend=False,
        title=dict(text='<b>Red de Administradores</b> · Grafo 3D interactivo',
                   font=dict(size=14, color=C['text'], family='JetBrains Mono'), x=0.5, xanchor='center'),
        scene=dict(xaxis=ax, yaxis=ax, zaxis=ax, bgcolor='rgba(5,6,9,0.0)',
                   camera=dict(eye=dict(x=1.8, y=1.8, z=1.2), up=dict(x=0, y=0, z=1)),
                   aspectmode='cube'),
        hoverlabel=dict(bgcolor='rgba(13,16,23,0.97)', bordercolor=C['border2'],
                        font=dict(color=C['text'], size=11, family='JetBrains Mono')),
        annotations=[dict(text="<b style='color:#3b82f6'>●</b> Sin flags  "
                               "<b style='color:#f59e0b'>●</b> 1 flag  "
                               "<b style='color:#ef4444'>●</b> 2+ flags",
                          xref="paper", yref="paper", x=0.5, y=-0.02, showarrow=False,
                          font=dict(size=10, color=C['text2'], family='JetBrains Mono'))])
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
                            titlefont=dict(color=C['accent']),
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
        st.warning("No se encontraron flags en `data/nacional/` o `data/catalunya/`."); return
    st.markdown('<div class="sec">Inventario</div>', unsafe_allow_html=True)
    badges = ''.join(f'<span class="fb {get_flag_meta(s)["css"]}">{get_flag_meta(s)["icon"]} {get_flag_meta(s)["label"]} · {flags[s]["scope"]}</span> ' for s in flags)
    st.markdown(f"<div style='margin-bottom:1rem'>{badges}</div>", unsafe_allow_html=True)

    stems = list(flags.keys())
    display = [f"{get_flag_meta(s)['icon']} {s} ({flags[s]['scope']})" for s in stems]
    idx = st.selectbox("Seleccionar flag", range(len(stems)), format_func=lambda i: display[i])
    sel = stems[idx]; info = flags[sel]; meta = get_flag_meta(sel)
    with st.spinner(f"Cargando {sel}..."): df = load_pq(info['path'])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Registros", fmt(len(df)))
    with c2: st.metric("Columnas", len(df.columns))
    with c3: st.metric("Ámbito", info['scope'])
    with c4: st.metric("Tamaño", f"{info['size']/1024:.0f} KB")

    # ── Specialized views ──
    if 'pares' in sel or 'admin_network' in sel:
        st.markdown('<div class="sec">Red de administradores — Grafo 3D</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-caption">Arrastra para rotar · Scroll para zoom · Hover para detalles · <span>Nodos = empresas, aristas = admin compartido</span></div>', unsafe_allow_html=True)
        fig_3d = pl_network_3d(df, max_nodes=60)
        if fig_3d: st.plotly_chart(fig_3d, use_container_width=True)
        st.markdown('<div class="sec">Score vs Concentración</div>', unsafe_allow_html=True)
        fig_bub = pl_f6_bubble(df)
        if fig_bub: st.plotly_chart(fig_bub, use_container_width=True)

    elif 'personas' in sel:
        sc_col = next((c for c in ['score_total','score_sum','score'] if c in df.columns), None)
        if sc_col:
            st.markdown('<div class="sec">Top personas por score</div>', unsafe_allow_html=True)
            top = df.nlargest(30, sc_col)
            fig = go.Figure(go.Bar(y=top.index.astype(str).str[:30][::-1], x=top[sc_col].values[::-1], orientation='h',
                marker=dict(color=top[sc_col].values[::-1],
                    colorscale=[[0,'rgba(59,130,246,.7)'],[1,'rgba(239,68,68,.9)']], line=dict(width=0))))
            fig.update_layout(**PL, height=max(350, len(top)*20),
                title=dict(text='<b>Top 30</b> · Score acumulado', font=dict(size=13), x=0))
            st.plotly_chart(fig, use_container_width=True)

    elif 'flag7' in sel:
        st.markdown('<div class="sec">Concentración empresa × órgano</div>', unsafe_allow_html=True)
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

    elif 'flag10' in sel or 'troceo' in sel:
        st.markdown('<div class="sec">Troceo — fraccionamiento de contratos</div>', unsafe_allow_html=True)
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

    with st.expander("🔎 Buscar empresa en todos los flags"):
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
            else: st.info(f"'{q}' no encontrado en ningún flag.")


# ═══════════════════════════════════════════════════════════════
# TAB 3: METODOLOGÍA
# ═══════════════════════════════════════════════════════════════
def render_meth():
    st.markdown(f"""
    <div class="disc"><strong>Nota:</strong> Esta pestaña documenta el pipeline de <strong>cruce
    BORME × Contratación Pública</strong>. Consiste en filtros deterministas — no es un modelo
    estadístico ni de machine learning. Un score alto indica un patrón que merece revisión humana,
    <strong>no constituye prueba de irregularidad</strong>.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">1. Fuentes de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc"><strong>BORME — Boletín Oficial del Registro Mercantil</strong><br><br>
    126.073 PDFs del BORME-A (2009–2026) parseados:<br>
    <code>borme_cargos.parquet</code> — acto (nombramiento, cese, reelección, revocación)
    vinculado a persona × empresa × cargo × fecha.<br>
    <code>borme_empresas.parquet</code> — datos societarios: fusiones, absorciones, escisiones,
    disoluciones, concursos, capital, domicilio.</div>
    <div class="mc"><strong>PLACSP — Plataforma de Contratación del Sector Público</strong><br><br>
    <code>licitaciones_espana.parquet</code> — 8.7M registros (2012–2026). Se filtran adjudicaciones
    con importe &gt; 0 y adjudicatario identificado.</div>
    <div class="mc"><strong>Contratación Catalunya</strong><br><br>
    <code>contratos_registro.parquet</code> (~3.4M) + <code>contratos_menores_bcn.parquet</code> (~177K) unificados.</div>
    <div class="mc"><strong>Flags pre-computados (F1–F5)</strong><br><br>
    <code>F1</code> Empresa constituida &lt;6 meses antes de su primer contrato ·
    <code>F2</code> Capital social &lt;3.000€ para contratos significativos ·
    <code>F4</code> Acto de disolución publicado ·
    <code>F5</code> Concurso de acreedores publicado</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">2. Normalización</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc"><strong>Empresas:</strong> Mayúsculas → eliminar acentos (preservando Ñ)
    → limpiar sufijos R.M. → colapsar formas societarias (S.L., S.A., S.L.U., S.C.P., S.C.C.L.)
    → eliminar sufijos (EN LIQUIDACION, EN DISOLUCION…) → strip puntuación.<br>
    Ejemplo: <code>"Construcciones García, S.L.U. (R.M. Madrid)"</code> → <code>"CONSTRUCCIONES GARCIA"</code><br><br>
    <strong>Stop words:</strong> Data-driven — tokens en &gt;0.5% de empresas BORME (~5.500 auto) + 203 curadas (ES/CAT/EN trilingüe).<br>
    <strong>Pesos de cargo:</strong> Regex-based (10 niveles: Adm.Único=10, Liquidador=9, …, Apoderado=1).</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">3. Pipeline de detección</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc mc-acc"><span class="step-num">1</span> <strong>Intersección BORME ∩ Contratación</strong><br><br>
    Cruce por nombre normalizado. Solo empresas en <strong>ambos</strong> datasets con ≥3 adjudicaciones.</div>
    <div class="mc mc-acc"><span class="step-num">2</span> <strong>Cargos vigentes</strong><br><br>
    Último acto por terna (persona, empresa, cargo). Filtro: solo cargos de decisión. Exclusión de personas jurídicas.</div>
    <div class="mc mc-acc"><span class="step-num">3</span> <strong>Detectar pares sospechosos</strong><br><br>
    Persona con 2–50 empresas → combinaciones de pares → retener si ≥2 órganos contratantes comunes.
    Análisis temporal: % órganos con actividad concurrente (±365 días).</div>
    <div class="mc mc-grn"><span class="step-num">4</span> <strong>Filtrar grupos corporativos</strong><br><br>
    <strong>a)</strong> Nombre de marca: Jaccard ≥0.5 en tokens no-genéricos<br>
    <strong>b)</strong> Solapamiento consejo: &gt;40% overlap + ≥3 personas<br>
    <strong>c)</strong> Multinacional: &gt;60% overlap + ≥4 personas<br>
    <strong>d)</strong> Fusiones BORME: ambas con actos de fusión/absorción/escisión</div>
    <div class="mc mc-acc"><span class="step-num">5</span> <strong>Enriquecer pares</strong><br><br>
    Peso del cargo (1–10), Flags F1–F5, stats contratación, concentración.</div>
    <div class="mc mc-wrn"><span class="step-num">6</span> <strong>Scoring de pares</strong></div>
    <div class="formula">
    score = concentración × √(n_órganos_comunes) × flag_weight × (cargo_weight / 5)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;× 1/log(1 + max_adj/5) × √(importe_par / 10K)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;× solo_admin_bonus × temporal_bonus<br><br>
    <span style="color:{C['text2']}">Flag weights: F1 ×4.0 · F5 ×3.0 · F4 ×2.5 · F2 ×2.0 (multiplicativos)</span><br>
    <span style="color:{C['text2']}">Agregación: par_score = score_max × log(1 + n_personas)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">4. Flags adicionales (F7–F11)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc"><strong>F7 — Concentración</strong>: % adj del órgano ganadas por una empresa.
    Nacional: &gt;40% fijo. Catalunya: adaptativo (≥200 adj → 20%, ≥50 → 30%, &lt;50 → 40%).</div>
    <div class="mc"><strong>F8 — UTEs sospechosas</strong>: UTEs cuyos miembros comparten administrador (detectados en F6).</div>
    <div class="mc"><strong>F9 — Discrepancia geo</strong> <span class="qg qg-wn">Nacional</span>:
    Provincia BORME ≠ CCAA mayoritaria de contratos (NUTS2). Solo PYMEs (3–200 adj).</div>
    <div class="mc"><strong>F10 — Troceo</strong> <span class="qg qg-wn">Catalunya</span>:
    ≥3 contratos misma empresa→órgano en 90d, todos bajo 15.000€, suma &gt; umbral.</div>
    <div class="mc"><strong>F11 — Modificaciones excesivas</strong> <span class="qg qg-wn">Catalunya</span>:
    ≥3 modificaciones y ≥20% de contratos modificados (promedio ~0.4%).</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">5. Scoring unificado por empresa</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="formula">
    risk_score = F1×3.0 + F2×0.5 + F4×2.0 + F5×2.0 + min(f6/50, 10) + f7×5.0 + F8×3.0 + F9×1.0
    </div>
    <div class="mc">Solo empresas con ≥1 flag. Salida: <code>risk_scoring_unificado.parquet</code>.<br><br>
    <strong>Catalunya (v4):</strong> risk_score = F1×3.0 + F2×0.5 + F4×2.0 + F5×2.0 + min(f6/50, 10) + f7×5.0 + F8×3.0 + F10×2.5 + F11×1.5</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">6. Diferencias Nacional vs Catalunya</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc">
    <strong>Datos:</strong> Nacional = PLACSP 8.7M · Catalunya = Registro 3.4M + Menores BCN 177K<br>
    <strong>F7:</strong> Nacional umbral fijo 40% · Catalunya adaptativo 20/30/40%<br>
    <strong>Exclusivo Nacional:</strong> F9 geo · <strong>Exclusivo Catalunya:</strong> F10 troceo, F11 modificaciones<br>
    <strong>Ambos:</strong> F1–F8, scoring unificado</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">7. Limitaciones</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mc">
    <strong>Cobertura:</strong> ~52% de adjudicatarios PLACSP en BORME. Autónomos y extranjeras no figuran.<br>
    <strong>Matching:</strong> Por nombre normalizado, no por NIF. Posibles falsos positivos/negativos.<br>
    <strong>Score ≠ fraude.</strong> Patrón estadístico que requiere investigación humana.</div>
    <div class="disc"><strong>Descargo de responsabilidad</strong><br><br>
    Datos públicos de PLACSP, Transparència Catalunya y BORME. <strong>No vinculado</strong> a estos organismos.
    <strong>Un score alto NO es prueba de irregularidad.</strong></div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">🏛️ Contratación <span>Pública</span> España</div>
        <div class="hero-sub">Calidad de datos · Red flags BORME × Contratación · Metodología</div>
        <div class="hero-line"></div>
    </div>
    """, unsafe_allow_html=True)

    placsp_prof = load_json(str(Q_DIR/"placsp_profile.json")) if (Q_DIR/"placsp_profile.json").exists() else None
    cat_prof = load_json(str(Q_DIR/"cat_profile.json")) if (Q_DIR/"cat_profile.json").exists() else None
    flags = discover_flags()

    tab_names = ["📊 Visión General"]
    if placsp_prof: tab_names.append("🏛️ PLACSP")
    if cat_prof: tab_names.append("🏴 Catalunya")
    tab_names += ["🚩 Flags", "📋 Metodología"]
    tabs = st.tabs(tab_names)
    ti = 0

    with tabs[ti]:
        ti += 1
        if not placsp_prof and not cat_prof and not flags:
            st.markdown("<div class='mc'>Sin datos. Ejecuta <code>precompute_quality.py</code> y coloca parquets en <code>data/</code>.</div>", unsafe_allow_html=True)
        else:
            for p in [placsp_prof, cat_prof]:
                if p:
                    st.markdown(f"<div class='fcard'><div style='font-family:\"Outfit\",sans-serif;font-size:.95rem;font-weight:700;color:{C['text']};margin-bottom:6px'>{p['name']}</div>"
                        f"<div style='font-size:.8rem;color:{C['text2']}'><b style='color:{C['text']};font-size:1.1rem'>{p['n']:,}</b> registros · {p['nc']} cols · {qb(p['completitud'])} · Dupes: {p['dupe_pct']:.2f}%</div></div>", unsafe_allow_html=True)
            if flags:
                badges = ' '.join(f'<span class="fb {get_flag_meta(s)["css"]}">{get_flag_meta(s)["icon"]} {get_flag_meta(s)["label"]}</span>' for s in flags)
                st.markdown(f"<div class='fcard'><div style='font-family:\"Outfit\",sans-serif;font-size:.95rem;font-weight:700;color:{C['accent']};margin-bottom:8px'>🚩 Flags — {len(flags)} archivos</div><div style='margin-top:8px'>{badges}</div></div>", unsafe_allow_html=True)
            if placsp_prof and cat_prof:
                st.markdown('<div class="sec">Comparativa</div>', unsafe_allow_html=True)
                comp = pd.DataFrame({
                    'Métrica': ['Registros','Columnas','Completitud (%)','Duplicados (%)','100% completas','>90% vacías'],
                    'PLACSP': [f"{placsp_prof['n']:,}", placsp_prof['nc'], f"{placsp_prof['completitud']:.1f}", f"{placsp_prof['dupe_pct']:.2f}", placsp_prof['n_complete'], placsp_prof['n_hi_miss']],
                    'Catalunya': [f"{cat_prof['n']:,}", cat_prof['nc'], f"{cat_prof['completitud']:.1f}", f"{cat_prof['dupe_pct']:.2f}", cat_prof['n_complete'], cat_prof['n_hi_miss']]})
                st.dataframe(comp, use_container_width=True, hide_index=True)

    if placsp_prof:
        with tabs[ti]: ti += 1; render_quality(placsp_prof, "PLACSP")
    if cat_prof:
        with tabs[ti]: ti += 1; render_quality(cat_prof, "Catalunya")

    with tabs[ti]: ti += 1; render_flags(flags)
    with tabs[ti]: render_meth()

    st.markdown(f"<div class='ft'><a href='https://twitter.com/Gsnchez'>@Gsnchez</a> · <a href='https://bquantfinance.com'>bquantfinance.com</a> · <a href='https://github.com/BquantFinance'>GitHub</a></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
