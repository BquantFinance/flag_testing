"""
═══════════════════════════════════════════════════════════════════════
  CONTRATACIÓN PÚBLICA × REGISTRO MERCANTIL
  Señales de alerta · Explorador de empresas · Metodología
  BQuant Finance · @Gsnchez · bquantfinance.com
═══════════════════════════════════════════════════════════════════════

Datos:
  anomalias/flag*.parquet             ← generados por explore_flags.py / explore_flags_cat.py
  anomalias/quality/placsp_profile.json
  anomalias/quality/cat_profile.json
  anomalias/quality/headline_stats.json
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
st.set_page_config(
    page_title="Señales en Contratación Pública",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA = Path("anomalias")
Q_DIR = DATA / "quality"

# ── Colors ──
C = {
    'bg':     '#07090e',
    'card':   '#0c0f16',
    'border': '#181d2a',
    'accent': '#e05a3a',
    'blue':   '#3b82f6',
    'green':  '#10b981',
    'amber':  '#f59e0b',
    'red':    '#ef4444',
    'purple': '#8b5cf6',
    'text':   '#e2e8f0',
    'text2':  '#94a3b8',
    'muted':  '#525d73',
    'grid':   'rgba(255,255,255,0.03)',
}

PL = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono, monospace', color=C['text'], size=11),
    margin=dict(l=50, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor='rgba(12,15,22,0.97)', bordercolor=C['border'],
        font=dict(color=C['text'], size=11),
    ),
)

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

.stApp {{
    background: {C['bg']};
    color: {C['text']};
    font-family: 'DM Sans', sans-serif;
}}
section[data-testid="stSidebar"] {{ background: {C['card']}; border-right: 1px solid {C['border']} }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap:0; border-bottom:1px solid {C['border']} }}
.stTabs [data-baseweb="tab"] {{
    background:transparent; color:{C['muted']}; border:none;
    padding:12px 24px; font-family:'DM Sans'; font-size:.82rem; font-weight:500;
    transition:all .25s;
}}
.stTabs [data-baseweb="tab"]:hover {{ color:{C['text2']} }}
.stTabs [aria-selected="true"] {{
    color:{C['accent']}!important;
    border-bottom:2px solid {C['accent']}!important;
}}

/* Metrics */
div[data-testid="stMetric"] {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:8px;
    padding:14px 18px;
}}
div[data-testid="stMetric"] label {{
    color:{C['muted']}!important; font-family:'JetBrains Mono'; font-size:.58rem!important;
    letter-spacing:.08em; text-transform:uppercase;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color:{C['text']}!important; font-family:'JetBrains Mono'; font-size:1.2rem!important; font-weight:600;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background:{C['card']}!important; border:1px solid {C['border']}!important; border-radius:8px!important;
}}

/* Custom classes */
.hero {{ text-align:center; padding:2rem 0 .8rem }}
.hero h1 {{
    font-family:'DM Sans'; font-size:2rem; font-weight:700; color:{C['text']};
    letter-spacing:-.03em; margin:0;
}}
.hero h1 span {{ color:{C['accent']} }}
.hero p {{ font-size:.78rem; color:{C['muted']}; font-family:'JetBrains Mono'; letter-spacing:.1em; margin:.3rem 0 0 }}
.hero-desc {{
    font-size:.88rem; color:{C['text2']}; max-width:650px; margin:.8rem auto 0; line-height:1.6;
}}
.hero-desc b {{ color:{C['text']} }}
.divider {{ height:1px; background:linear-gradient(90deg,transparent,{C['border']},transparent); margin:1.2rem 0 }}

.sec {{
    font-family:'JetBrains Mono'; font-size:.68rem; font-weight:600; color:{C['accent']};
    letter-spacing:.1em; text-transform:uppercase;
    border-bottom:1px solid {C['border']}; padding-bottom:6px; margin:1.8rem 0 1rem;
}}
.card {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:8px;
    padding:16px 20px; margin:8px 0; font-size:.84rem; color:{C['text2']}; line-height:1.65;
}}
.card b {{ color:{C['text']} }}
.card-accent {{ border-left:3px solid {C['accent']}; border-radius:0 8px 8px 0 }}
.card-blue {{ border-left:3px solid {C['blue']}; border-radius:0 8px 8px 0 }}
.card-green {{ border-left:3px solid {C['green']}; border-radius:0 8px 8px 0 }}
.card-amber {{ border-left:3px solid {C['amber']}; border-radius:0 8px 8px 0 }}

.badge {{
    display:inline-block; padding:3px 10px; border-radius:4px;
    font-family:'JetBrains Mono'; font-size:.62rem; font-weight:600; margin:2px;
}}
.badge-red {{ background:rgba(239,68,68,.1); color:{C['red']}; border:1px solid rgba(239,68,68,.2) }}
.badge-blue {{ background:rgba(59,130,246,.1); color:{C['blue']}; border:1px solid rgba(59,130,246,.2) }}
.badge-amber {{ background:rgba(245,158,11,.1); color:{C['amber']}; border:1px solid rgba(245,158,11,.2) }}
.badge-green {{ background:rgba(16,185,129,.1); color:{C['green']}; border:1px solid rgba(16,185,129,.2) }}
.badge-purple {{ background:rgba(139,92,246,.1); color:{C['purple']}; border:1px solid rgba(139,92,246,.2) }}

.warn-box {{
    background:rgba(245,158,11,.04); border:1px solid rgba(245,158,11,.12);
    border-radius:8px; padding:14px 18px; font-size:.78rem; color:{C['text2']}; line-height:1.65; margin-bottom:1rem;
}}

.ft {{
    text-align:center; color:{C['muted']}; font-family:'JetBrains Mono'; font-size:.62rem;
    padding:1.5rem 0 .5rem; border-top:1px solid {C['border']}; margin-top:2rem;
}}
.ft a {{ color:{C['accent']}; text-decoration:none }}

.formula {{
    background:rgba(139,92,246,.05); border:1px solid rgba(139,92,246,.12); border-radius:8px;
    padding:12px 16px; font-family:'JetBrains Mono'; font-size:.7rem; color:{C['purple']};
    line-height:1.7; margin:8px 0;
}}

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

@st.cache_data(show_spinner=False)
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_pq(path):
    return pd.read_parquet(path)


# ═══════════════════════════════════════════════════════════════
# FLAG REGISTRY
# ═══════════════════════════════════════════════════════════════
FLAGS = {
    'flag1_recien_creada': {
        'label': 'Empresa recién creada',
        'short': 'F1',
        'icon': '🆕',
        'badge': 'badge-red',
        'scope': 'Nacional',
        'what': 'Empresa constituida <b>menos de 6 meses antes</b> de recibir su primer contrato público.',
        'why': 'Puede indicar una sociedad instrumental creada ad hoc para una adjudicación concreta.',
        'how': 'Se busca en BORME el acto de "Constitución", se toma la primera fecha, y se compara con la fecha de adjudicación en PLACSP. Flag si <b>0–180 días</b>.',
    },
    'flag2_capital_ridiculo': {
        'label': 'Capital social mínimo',
        'short': 'F2',
        'icon': '💰',
        'badge': 'badge-amber',
        'scope': 'Nacional',
        'what': 'Empresa con <b>capital social inferior a 10.000€</b> que recibe contratos de más de 100.000€.',
        'why': 'Un capital tan bajo es inusual para empresas que manejan contratación pública relevante.',
        'how': 'Se toma el capital más reciente publicado en BORME y se compara con el importe de adjudicación.',
    },
    'flag4_disolucion': {
        'label': 'Empresa disuelta',
        'short': 'F4',
        'icon': '💀',
        'badge': 'badge-red',
        'scope': 'Nacional',
        'what': 'Empresa con acto de <b>disolución o extinción</b> publicado en BORME que sigue recibiendo contratos públicos.',
        'why': 'Una empresa disuelta no debería participar en licitaciones.',
        'how': 'Se buscan actos de "Disolución|Extinción" en BORME. Flag si la disolución ocurre entre <b>0 y 365 días después</b> de una adjudicación.',
    },
    'flag5_concursal': {
        'label': 'En concurso de acreedores',
        'short': 'F5',
        'icon': '⚖️',
        'badge': 'badge-red',
        'scope': 'Nacional',
        'what': 'Empresa en <b>situación concursal</b> (insolvencia) según BORME que recibe adjudicaciones.',
        'why': 'La legislación restringe la contratación pública a empresas en esta situación.',
        'how': 'Se buscan actos con "concurso|concursal" en BORME. Flag si la empresa recibe adjudicaciones <b>después</b> de la declaración.',
    },
    'flag6_admin_network': {
        'label': 'Red de administradores (pares)',
        'short': 'F6',
        'icon': '🕸️',
        'badge': 'badge-blue',
        'scope': 'Nacional',
        'what': 'Dos empresas comparten <b>administrador</b> (sin ser del mismo grupo corporativo) y ganan contratos ante los <b>mismos organismos públicos</b>.',
        'why': 'Sugiere posible coordinación de ofertas entre empresas aparentemente independientes.',
        'how': 'Se cruzan cargos activos de BORME con adjudicaciones de PLACSP. Se requieren ≥2 órganos comunes. Se filtran grupos corporativos legítimos.',
    },
    'flag6_pares_unicos': {
        'label': 'Pares únicos de empresas',
        'short': 'F6',
        'icon': '🔗',
        'badge': 'badge-blue',
        'scope': 'Nacional',
        'what': 'Pares de empresas agregados: cada par aparece una vez con el resumen de <b>todas las personas</b> que los conectan.',
        'why': 'Vista consolidada: un par con 3 personas compartidas es más sospechoso que uno con 1.',
        'how': 'Agrupación de F6 por par (empresa_1, empresa_2). Se muestra nº personas, órganos comunes, flags de cada empresa.',
    },
    'flag6_personas_resumen': {
        'label': 'Personas con más conexiones',
        'short': 'F6',
        'icon': '👤',
        'badge': 'badge-blue',
        'scope': 'Nacional',
        'what': 'Ranking de <b>personas físicas</b> que conectan más pares de empresas adjudicatarias.',
        'why': 'Una persona en muchos pares indica un decisor que controla varias empresas que licitan ante los mismos órganos.',
        'how': 'Agregación por persona de todos los pares F6 en los que participa.',
    },
    'flag6_admin_network_cat': {
        'label': 'Red de administradores CAT',
        'short': 'F6',
        'icon': '🕸️',
        'badge': 'badge-blue',
        'scope': 'Catalunya',
        'what': 'Igual que F6 Nacional pero para contratación catalana (Registre Públic + menores BCN).',
        'why': 'Misma lógica aplicada al dataset catalán.',
        'how': 'Cruce BORME × contratos Catalunya.',
    },
    'flag6_pares_cat': {
        'label': 'Pares únicos CAT',
        'short': 'F6',
        'icon': '🔗',
        'badge': 'badge-blue',
        'scope': 'Catalunya',
        'what': 'Pares de empresas agregados en Catalunya.',
        'why': 'Vista consolidada de pares catalanes.',
        'how': 'Agrupación de F6 CAT por par de empresas.',
    },
    'flag6_personas_cat': {
        'label': 'Personas con más conexiones CAT',
        'short': 'F6',
        'icon': '👤',
        'badge': 'badge-blue',
        'scope': 'Catalunya',
        'what': 'Ranking de personas que conectan más pares en Catalunya.',
        'why': 'Misma lógica que personas Nacional, aplicada al dataset catalán.',
        'how': 'Agregación por persona de pares F6 CAT.',
    },
    'flag7_concentracion': {
        'label': 'Empresa dominante en un órgano',
        'short': 'F7',
        'icon': '🎯',
        'badge': 'badge-green',
        'scope': 'Nacional',
        'what': 'Una empresa gana <b>más del 40%</b> de todas las adjudicaciones de un organismo contratante.',
        'why': 'Indica posible relación preferente entre la empresa y el órgano.',
        'how': 'Empresa con >40% adj del órgano, mínimo 5 adj propias y 10 totales del órgano.',
    },
    'flag7_concentracion_cat': {
        'label': 'Empresa dominante en órgano CAT',
        'short': 'F7',
        'icon': '🎯',
        'badge': 'badge-green',
        'scope': 'Catalunya',
        'what': 'Concentración de adjudicaciones en Catalunya con umbral adaptativo.',
        'why': 'Umbral adaptativo: órganos grandes (≥200 adj) → 20%, medianos → 30%, pequeños → 40%.',
        'how': 'Misma lógica que F7 Nacional con umbrales escalonados.',
    },
    'flag8_utes_sospechosas': {
        'label': 'UTEs con miembros vinculados',
        'short': 'F8',
        'icon': '🤝',
        'badge': 'badge-amber',
        'scope': 'Nacional',
        'what': '<b>UTEs</b> cuyos miembros comparten administrador en BORME.',
        'why': 'Si las dos partes de una UTE tienen el mismo decisor, la "unión temporal" puede no ser independiente.',
        'how': 'Se parsean los miembros de cada UTE del nombre del adjudicatario y se cruzan con la red F6.',
    },
    'flag8_utes_cat': {
        'label': 'UTEs vinculadas CAT',
        'short': 'F8',
        'icon': '🤝',
        'badge': 'badge-amber',
        'scope': 'Catalunya',
        'what': 'UTEs con miembros vinculados en contratación catalana.',
        'why': 'Misma lógica que F8 Nacional.',
        'how': 'Cruce UTEs catalanas con red F6.',
    },
    'flag9_geo_discrepancia': {
        'label': 'Empresa lejos de donde contrata',
        'short': 'F9',
        'icon': '📍',
        'badge': 'badge-purple',
        'scope': 'Nacional',
        'what': 'Empresa registrada en una CCAA que gana contratos <b>mayoritariamente en otra muy distinta</b>.',
        'why': 'Solo PYMEs (3–200 adj). Las grandes con sede en Madrid se excluyen por ser habitual.',
        'how': 'Provincia BORME → CCAA registro. NUTS2 del contrato → CCAA mayoritaria.',
    },
    'flag10_troceo_cat': {
        'label': 'Posible fraccionamiento',
        'short': 'F10',
        'icon': '✂️',
        'badge': 'badge-red',
        'scope': 'Catalunya',
        'what': 'Un órgano adjudica a la misma empresa <b>≥3 contratos en 90 días, todos bajo 15.000€</b>, pero cuya suma supera ese umbral.',
        'why': 'Posible división artificial para evitar la obligación de licitar.',
        'how': 'Sliding window de 90 días por par empresa×órgano. Contratos ≤15K€, cluster ≥3, suma > umbral.',
    },
    'flag11_modificaciones_cat': {
        'label': 'Modificaciones excesivas',
        'short': 'F11',
        'icon': '📝',
        'badge': 'badge-amber',
        'scope': 'Catalunya',
        'what': 'Empresa con <b>≥20% de sus contratos modificados</b> (la media catalana es ~0.6%).',
        'why': 'Puede indicar adjudicaciones inicialmente bajas que se incrementan después.',
        'how': 'Columnas nativas del registro catalán: Número/Tipus/Import de modificació.',
    },
    'risk_scoring_unificado': {
        'label': 'Empresas con señales acumuladas',
        'short': 'Resumen',
        'icon': '🚩',
        'badge': 'badge-red',
        'scope': 'Nacional',
        'what': 'Listado de <b>todas las empresas que tienen al menos 1 señal</b> de alerta activa.',
        'why': 'Vista consolidada: muestra qué señales tiene cada empresa y cuántas acumula.',
        'how': 'Unión de todas las señales F1–F9 por empresa.',
    },
    'risk_scoring_cat': {
        'label': 'Empresas con señales acumuladas CAT',
        'short': 'Resumen',
        'icon': '🚩',
        'badge': 'badge-red',
        'scope': 'Catalunya',
        'what': 'Listado de empresas catalanas con al menos 1 señal activa.',
        'why': 'Vista consolidada para Catalunya.',
        'how': 'Unión de señales F1–F11 por empresa.',
    },
    'grupos_corporativos': {
        'label': 'Grupos corporativos (filtrados)',
        'short': 'Grp',
        'icon': '🏢',
        'badge': 'badge-green',
        'scope': 'Nacional',
        'what': 'Pares <b>descartados como grupo corporativo legítimo</b>: comparten marca, consejo o fusiones.',
        'why': 'Estos no son sospechosos — son falsos positivos que el sistema ha filtrado correctamente.',
        'how': 'Nombre de marca compartido, >40% solapamiento de consejo, o actos de fusión en BORME.',
    },
    'grupos_corporativos_cat': {
        'label': 'Grupos corporativos CAT',
        'short': 'Grp',
        'icon': '🏢',
        'badge': 'badge-green',
        'scope': 'Catalunya',
        'what': 'Grupos corporativos filtrados en Catalunya.',
        'why': 'Falsos positivos descartados.',
        'how': 'Mismos criterios que Nacional.',
    },
}


def discover_flags():
    """Find all parquet files and match them to the registry."""
    found = {}
    for d, scope in [(DATA, 'Nacional'), (DATA / 'catalunya', 'Catalunya')]:
        if d.exists():
            for f in sorted(d.glob('*.parquet')):
                found[f.stem] = {'path': str(f), 'scope': scope, 'size': f.stat().st_size}
    return found

def get_meta(stem):
    return FLAGS.get(stem, {'label': stem, 'short': '?', 'icon': '📄', 'badge': 'badge-blue',
                             'scope': '?', 'what': '', 'why': '', 'how': ''})


# ═══════════════════════════════════════════════════════════════
# GEOGRAPHIC MAP for F9
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
    reg_col = next((c for c in df_geo.columns if 'ccaa_borme' in c.lower() or 'registro' in c.lower()), None)
    con_col = next((c for c in df_geo.columns if 'ccaa_contrato' in c.lower() or 'principal' in c.lower()), None)
    if not reg_col or not con_col:
        return None
    imp_col = next((c for c in df_geo.columns if 'importe' in c.lower()), None)

    flows = {}
    for _, r in df_geo.iterrows():
        orig, dest = str(r[reg_col]).strip(), str(r[con_col]).strip()
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

    top_flows = sorted(flows.items(), key=lambda x: -x[1]['count'])[:60]
    max_count = max(f[1]['count'] for f in top_flows)
    fig = go.Figure()

    for (orig, dest), info in top_flows:
        lat0, lon0 = CCAA_COORDS[orig]
        lat1, lon1 = CCAA_COORDS[dest]
        intensity = info['count'] / max_count
        mid_lat = (lat0 + lat1) / 2 + (lon1 - lon0) * 0.08
        mid_lon = (lon0 + lon1) / 2 - (lat1 - lat0) * 0.08
        fig.add_trace(go.Scattergeo(
            lat=[lat0, mid_lat, lat1], lon=[lon0, mid_lon, lon1], mode='lines',
            line=dict(width=1 + intensity * 5, color=f'rgba(245,158,11,{0.15 + intensity * 0.55})'),
            hovertext=f"<b>{orig} → {dest}</b><br>{info['count']} empresas<br>{info['importe']/1e6:.0f}M€",
            hoverinfo='text', showlegend=False))

    all_ccaa = set()
    out_count = {}
    for (o, d), info in top_flows:
        all_ccaa.update([o, d])
        out_count[o] = out_count.get(o, 0) + info['count']
        out_count[d] = out_count.get(d, 0) + info['count']

    for ccaa in all_ccaa:
        if ccaa in CCAA_COORDS:
            lat, lon = CCAA_COORDS[ccaa]
            sz = 6 + (out_count.get(ccaa, 0) / max(out_count.values())) * 18
            fig.add_trace(go.Scattergeo(
                lat=[lat], lon=[lon], mode='markers+text',
                marker=dict(size=sz, color=C['blue'], opacity=.9, line=dict(width=1, color='rgba(255,255,255,.2)')),
                text=[ccaa[:12]], textposition='top center',
                textfont=dict(size=8, color=C['text2'], family='JetBrains Mono'),
                hovertext=f"<b>{ccaa}</b><br>{out_count.get(ccaa, 0)} flujos",
                hoverinfo='text', showlegend=False))

    fig.update_geos(
        scope='europe', center=dict(lat=40.0, lon=-3.5), projection_scale=6.5,
        showland=True, landcolor='rgba(12,15,22,1)', showocean=True, oceancolor='rgba(7,9,14,1)',
        showcoastlines=True, coastlinecolor='rgba(24,29,42,.6)',
        showcountries=True, countrycolor='rgba(24,29,42,.4)',
        showlakes=False, showrivers=False, bgcolor='rgba(0,0,0,0)',
        lonaxis_range=[-10, 5], lataxis_range=[27, 44])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color=C['text'], size=11),
        margin=dict(l=0, r=0, t=40, b=0), height=500,
        title=dict(text='Registro → Contratos · Grosor ∝ nº empresas', font=dict(size=12), x=0.5),
        hoverlabel=dict(bgcolor='rgba(12,15,22,.97)', bordercolor=C['border'], font=dict(color=C['text'], size=11)))
    return fig


# ═══════════════════════════════════════════════════════════════
# F7 HEATMAP
# ═══════════════════════════════════════════════════════════════
def pl_f7_heatmap(df):
    if 'pct_adj_organo' not in df.columns:
        return None
    emp_col = 'adj_norm' if 'adj_norm' in df.columns else df.columns[0]
    org_col = 'organo_contratante' if 'organo_contratante' in df.columns else df.columns[1]
    top = df.head(100).copy()
    top['emp'] = top[emp_col].astype(str).str[:30]
    top['org'] = top[org_col].astype(str).str[:35]
    top_emps = top.groupby('emp')['pct_adj_organo'].max().nlargest(15).index.tolist()
    sub = top[top['emp'].isin(top_emps)]
    if len(sub) < 3:
        return None
    piv = sub.pivot_table(index='emp', columns='org', values='pct_adj_organo', aggfunc='max').fillna(0)
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[str(c)[:30] for c in piv.columns], y=piv.index.tolist(),
        colorscale=[[0, 'rgba(7,9,14,1)'], [.3, 'rgba(59,130,246,.35)'],
                     [.6, 'rgba(245,158,11,.55)'], [1, 'rgba(239,68,68,.85)']],
        hovertemplate='<b>%{y}</b><br>%{x}<br>%{z:.0%}<extra></extra>',
        colorbar=dict(title='%Adj', thickness=10, len=.5, tickfont=dict(size=9, color=C['muted']))))
    fig.update_layout(**PL, height=max(350, len(top_emps) * 28 + 80),
        title=dict(text='Concentración empresa × órgano (% adjudicaciones)', font=dict(size=12), x=0),
        xaxis=dict(tickfont=dict(size=8), tickangle=-45),
        yaxis=dict(tickfont=dict(size=9)))
    return fig


# ═══════════════════════════════════════════════════════════════
# SEARCH across all flags
# ═══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def search_all(q, flag_files):
    results = []
    for stem, fi in flag_files.items():
        try:
            df = load_pq(fi['path'])
            meta = get_meta(stem)
            mask = pd.Series(False, index=df.index)
            for col in df.select_dtypes(include=['object']).columns:
                mask |= df[col].astype(str).str.contains(q, case=False, na=False)
            hits = mask.sum()
            if hits > 0:
                results.append({
                    'stem': stem,
                    'label': meta['label'],
                    'icon': meta['icon'],
                    'badge': meta['badge'],
                    'scope': fi['scope'],
                    'hits': hits,
                    'sample': df[mask].head(10),
                })
        except Exception:
            pass
    return results


# ═══════════════════════════════════════════════════════════════
# COLUMN DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════
# Columns to hide from display (internal normalization keys)
_HIDE_COLS = {'empresa_norm', 'adj_norm', 'empresa_1', 'empresa_2', 'cargo_norm',
              'cargo_upper', 'cargo_w', 'organo_norm', 'same_group', 'is_fusion_borme'}

# Columns to drop scoring from display
_SCORE_COLS = {'risk_score', 'score', 'score_max', 'score_sum', 'par_score',
               'score_total', 'f6_score', 'f7_max_conc', 'cargo_weight',
               'flag_weight', 'size_penalty', 'concentracion'}

def clean_df_for_display(df):
    """Remove score columns and internal normalization columns from display."""
    drop = [c for c in df.columns if c in _SCORE_COLS or c in _HIDE_COLS]
    return df.drop(columns=drop, errors='ignore')


# ═══════════════════════════════════════════════════════════════
# TAB: RESUMEN
# ═══════════════════════════════════════════════════════════════
def render_resumen(flag_files):
    # ── What is this ──
    st.markdown("""
    <div class="card card-accent">
        <b>¿Qué es esto?</b><br><br>
        Cruzamos los datos del <b>Registro Mercantil</b> (quién dirige cada empresa, cuándo se constituyó,
        si está disuelta o en concurso) con la <b>contratación pública</b> (quién gana contratos del Estado)
        para detectar situaciones que merecen revisión. Ningún patrón es prueba de irregularidad —
        son señales estadísticas para priorizar la supervisión humana.
    </div>
    """, unsafe_allow_html=True)

    # ── Headline stats ──
    hs_path = Q_DIR / "headline_stats.json"
    if hs_path.exists():
        hs = load_json(str(hs_path))
        st.markdown('<div class="sec">Datos procesados</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Contratos analizados", "8.7M")
        with c2: st.metric("Actos mercantiles", "17.1M")
        with c3: st.metric("Empresas cruzadas", fmt(hs.get('n_empresas_red_nacional', 126_073)))
        with c4: st.metric("Señales detectadas", fmt(hs.get('n_risk_nacional', 25_675)))

    # ── The 11 signals ──
    st.markdown('<div class="sec">Las 11 señales que analizamos</div>', unsafe_allow_html=True)

    signals = [
        ('🕸️', 'Administrador compartido', 'F6', 'Dos empresas comparten persona en su consejo y ganan contratos ante los mismos organismos, sin ser del mismo grupo corporativo.', 'badge-blue'),
        ('🎯', 'Empresa dominante', 'F7', 'Una empresa gana más del 40% de las adjudicaciones de un organismo contratante.', 'badge-green'),
        ('🆕', 'Empresa recién creada', 'F1', 'Constituida menos de 6 meses antes de recibir su primer contrato público.', 'badge-red'),
        ('💰', 'Capital mínimo', 'F2', 'Capital social inferior a 10.000€ y contratos superiores a 100.000€.', 'badge-amber'),
        ('💀', 'Empresa disuelta', 'F4', 'Acto de disolución en BORME seguido de adjudicaciones.', 'badge-red'),
        ('⚖️', 'En concurso', 'F5', 'Empresa en situación concursal que sigue recibiendo contratos.', 'badge-red'),
        ('🤝', 'UTEs vinculadas', 'F8', 'UTEs cuyos miembros comparten administrador.', 'badge-amber'),
        ('📍', 'Discrepancia geográfica', 'F9', 'Empresa registrada en una CCAA que contrata mayoritariamente en otra.', 'badge-purple'),
        ('✂️', 'Fraccionamiento', 'F10', '≥3 contratos en 90 días bajo umbral cuya suma lo supera (solo Catalunya).', 'badge-red'),
        ('📝', 'Modificaciones excesivas', 'F11', '≥20% de contratos modificados vs media del 0.6% (solo Catalunya).', 'badge-amber'),
        ('🏢', 'Grupos filtrados', 'Grp', 'Pares descartados como grupo corporativo legítimo (no sospechosos).', 'badge-green'),
    ]

    for icon, name, short, desc, badge in signals:
        st.markdown(f"""<div class="card" style="padding:10px 16px">
            <span class="badge {badge}">{short}</span>
            <b>{icon} {name}</b> — <span style="color:{C['text2']}">{desc}</span>
        </div>""", unsafe_allow_html=True)

    # ── Search ──
    st.markdown('<div class="sec">Buscar empresa o persona</div>', unsafe_allow_html=True)
    q = st.text_input("🔍", key="search_main", placeholder="Escribe un nombre (mín. 3 caracteres)...",
                       label_visibility="collapsed")
    if q and len(q) >= 3:
        with st.spinner("Buscando en todos los análisis..."):
            results = search_all(q, flag_files)
        if results:
            st.markdown(f"**{len(results)}** análisis con resultados para **{q}**")
            for r in results:
                with st.expander(f"{r['icon']} {r['label']} — {r['scope']} · {r['hits']} coincidencias"):
                    st.dataframe(clean_df_for_display(r['sample']), use_container_width=True, hide_index=True)
        else:
            st.info(f"«{q}» no encontrado en ningún análisis.")

    # ── Disclaimer ──
    st.markdown(f"""
    <div class="warn-box">
        <b>⚠️ Importante:</b> Un patrón detectado NO es prueba de irregularidad. Son señales estadísticas
        derivadas del cruce automatizado de datos públicos. Requieren revisión humana cualificada.
        Datos de PLACSP, Registre Públic de Contractes, Portal de Transparència BCN y BORME.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB: EXPLORAR SEÑALES
# ═══════════════════════════════════════════════════════════════
def render_explorar(flag_files):
    if not flag_files:
        st.warning("No se encontraron análisis. Coloca los parquets en `anomalias/`.")
        return

    # ── Signal selector ──
    stems = list(flag_files.keys())
    display_names = []
    for s in stems:
        m = get_meta(s)
        display_names.append(f"{m['icon']} {m['label']} ({flag_files[s]['scope']})")

    idx = st.selectbox("Seleccionar señal", range(len(stems)), format_func=lambda i: display_names[i])
    sel = stems[idx]
    meta = get_meta(sel)
    info = flag_files[sel]

    # ── Explanation ──
    if meta['what']:
        st.markdown(f"""<div class="card card-accent">
            <span class="badge {meta['badge']}">{meta['short']}</span>
            <b>{meta['icon']} {meta['label']}</b><br><br>
            <b>Qué detecta:</b> {meta['what']}<br>
            <b>Por qué importa:</b> {meta['why']}<br>
            <b>Cómo se calcula:</b> {meta['how']}
        </div>""", unsafe_allow_html=True)

    # ── Load data ──
    with st.spinner("Cargando..."):
        df = load_pq(info['path'])

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Registros", f"{len(df):,}")
    with c2: st.metric("Columnas", len(df.columns))
    with c3: st.metric("Ámbito", info['scope'])

    # ── Specialized visualizations (only the useful ones) ──
    if 'flag7' in sel:
        fig = pl_f7_heatmap(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    if 'flag9' in sel or 'geo_dis' in sel:
        fig = pl_geo_map(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    if 'flag10' in sel and 'n_contratos_cluster' in df.columns:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Histogram(x=df['n_contratos_cluster'], nbinsx=30,
                marker=dict(color=C['accent'], opacity=.85)))
            fig.update_layout(**PL, height=280,
                title=dict(text='Contratos por cluster de troceo', font=dict(size=12)),
                xaxis=dict(title='Nº contratos', gridcolor=C['grid']),
                yaxis=dict(title='Frecuencia', gridcolor=C['grid']), bargap=.03)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'ratio_sobre_umbral' in df.columns:
                fig = go.Figure(go.Histogram(x=df['ratio_sobre_umbral'], nbinsx=30,
                    marker=dict(color=C['amber'], opacity=.85)))
                fig.update_layout(**PL, height=280,
                    title=dict(text='Ratio suma / umbral (1x = justo en límite)', font=dict(size=12)),
                    xaxis=dict(title='Ratio', gridcolor=C['grid']),
                    yaxis=dict(title='Frecuencia', gridcolor=C['grid']), bargap=.03)
                st.plotly_chart(fig, use_container_width=True)

    if 'risk_scoring' in sel:
        # Show flag composition without scores
        bool_cols = [c for c in df.columns if df[c].dtype == bool]
        if bool_cols:
            flag_sums = {c: int(df[c].sum()) for c in bool_cols if df[c].sum() > 0}
            if flag_sums:
                fs_df = pd.DataFrame({'Señal': list(flag_sums.keys()),
                                      'Empresas': list(flag_sums.values())}).sort_values('Empresas', ascending=True)
                fig = go.Figure(go.Bar(
                    y=fs_df['Señal'], x=fs_df['Empresas'], orientation='h',
                    marker=dict(color=C['blue'], opacity=.85),
                    hovertemplate='<b>%{y}</b><br>%{x:,} empresas<extra></extra>'))
                fig.update_layout(**PL, height=max(220, len(fs_df) * 30),
                    title=dict(text='Nº empresas por señal activa', font=dict(size=12)),
                    xaxis=dict(gridcolor=C['grid']),
                    yaxis=dict(tickfont=dict(size=9)))
                st.plotly_chart(fig, use_container_width=True)

        # Nº flags distribution
        nf_col = next((c for c in df.columns if 'n_flags' in c.lower()), None)
        if nf_col:
            dist = df[nf_col].value_counts().sort_index()
            fig = go.Figure(go.Bar(
                x=[f"{int(k)} señal{'es' if k > 1 else ''}" for k in dist.index],
                y=dist.values,
                marker=dict(color=[C['blue'] if k <= 1 else C['amber'] if k <= 2 else C['red']
                                   for k in dist.index], opacity=.85),
                hovertemplate='<b>%{x}</b><br>%{y:,} empresas<extra></extra>'))
            fig.update_layout(**PL, height=280,
                title=dict(text='Distribución: cuántas señales acumula cada empresa', font=dict(size=12)),
                xaxis=dict(gridcolor=C['grid']),
                yaxis=dict(title='Empresas', gridcolor=C['grid']), bargap=.15)
            st.plotly_chart(fig, use_container_width=True)

    # ── Filter & search ──
    st.markdown('<div class="sec">Explorar datos</div>', unsafe_allow_html=True)
    df_display = clean_df_for_display(df)

    fc1, fc2 = st.columns([1, 2])
    with fc1:
        search_col = st.selectbox("Buscar en columna", ['(todas)'] + list(df_display.columns), key="exp_col")
    with fc2:
        search_term = st.text_input("Filtrar por texto", key="exp_term",
                                     placeholder="Escribe para filtrar...")

    filtered = df_display.copy()
    if search_term:
        if search_col != '(todas)':
            filtered = filtered[filtered[search_col].astype(str).str.contains(search_term, case=False, na=False)]
        else:
            mask = pd.Series(False, index=filtered.index)
            for col in filtered.select_dtypes(include=['object']).columns:
                mask |= filtered[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered = filtered[mask]
        st.caption(f"🔍 {len(filtered):,} de {len(df_display):,} registros")

    # Sorting
    sortable = [c for c in filtered.columns if filtered[c].dtype in ['int64', 'float64', 'int32', 'float32']]
    if sortable:
        sort_col = st.selectbox("Ordenar por", ['(sin ordenar)'] + sortable, key="exp_sort")
        if sort_col != '(sin ordenar)':
            filtered = filtered.sort_values(sort_col, ascending=False)

    st.dataframe(filtered.head(1000), use_container_width=True, height=500, hide_index=True)

    # ── Cross-search ──
    with st.expander("🔎 Buscar esta empresa en TODAS las señales"):
        xq = st.text_input("Nombre de empresa", key="xsearch")
        if xq and len(xq) >= 3:
            xresults = []
            for s, fi in flag_files.items():
                try:
                    df_tmp = load_pq(fi['path'])
                    for col in df_tmp.select_dtypes(include=['object']).columns:
                        n = df_tmp[col].astype(str).str.contains(xq, case=False, na=False).sum()
                        if n > 0:
                            m = get_meta(s)
                            xresults.append({'Señal': f"{m['icon']} {m['label']}", 'Ámbito': fi['scope'],
                                             'Coincidencias': n})
                            break
                except Exception:
                    pass
            if xresults:
                st.dataframe(pd.DataFrame(xresults), use_container_width=True, hide_index=True)
            else:
                st.info(f"«{xq}» no aparece en ningún análisis.")


# ═══════════════════════════════════════════════════════════════
# TAB: METODOLOGÍA (simplified)
# ═══════════════════════════════════════════════════════════════
def render_metodo():
    st.markdown("""
    <div class="warn-box">
        <b>Nota:</b> Este pipeline usa filtros deterministas — no es un modelo de machine learning.
        Un patrón detectado indica una situación que merece revisión humana,
        <b>no constituye prueba de irregularidad</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">1. Fuentes de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-blue">
        <b>BORME — Boletín Oficial del Registro Mercantil</b><br>
        17.1M filas parseadas de PDFs (2009–2026). Incluye nombramientos, ceses, constituciones,
        fusiones, disoluciones, concursos, capitales.
    </div>
    <div class="card card-blue">
        <b>PLACSP — Plataforma de Contratación del Sector Público</b><br>
        8.7M registros (2012–2026). Filtrado a 5.8M adjudicaciones con importe > 0 y adjudicatario identificado.
    </div>
    <div class="card card-blue">
        <b>Contratación Catalunya</b><br>
        Registre Públic de Contractes (~3.4M) + contratos menores Barcelona (~177K).
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">2. Cómo se cruzan los datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-accent">
        <b>Normalización de nombres</b><br><br>
        El cruce se hace por <b>nombre de empresa normalizado</b> (no por NIF, que no está disponible en BORME).
        Proceso: mayúsculas → eliminar acentos (preservar Ñ) → colapsar formas societarias
        (S.L., S.A., SOCIEDAD LIMITADA, etc.) → eliminar puntuación.<br><br>
        Ejemplo: <code>"Construcciones García López, S.L.U. (R.M. Madrid)"</code>
        → <code>"CONSTRUCCIONES GARCIA LOPEZ"</code><br><br>
        Nacional: <b>126.073 empresas</b> cruzadas entre BORME y PLACSP.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">3. Cómo funciona cada señal</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card card-blue">
        <b>🕸️ F6 — Red de administradores</b> (la señal principal)<br><br>
        <b>Paso 1:</b> De los 17.1M actos BORME, se toma el último acto por persona×empresa×cargo.
        Si es nombramiento → vigente. Si es cese → inactivo. Se retienen solo cargos de decisión
        (administradores, consejeros, presidentes — no apoderados).<br><br>
        <b>Paso 2:</b> Para cada persona con 2–50 empresas adjudicatarias, se buscan pares de sus empresas
        que comparten ≥2 órganos contratantes.<br><br>
        <b>Paso 3:</b> Se filtran grupos corporativos legítimos: nombre de marca compartido, >40% solapamiento
        de consejo con ≥3 personas, o actos de fusión en BORME.<br><br>
        Resultado Nacional: <b>2.287 pares</b> persona×empresa (1.878 pares únicos, 1.416 personas, 2.684 empresas).
    </div>

    <div class="card">
        <b>🆕 F1 — Recién creada:</b> Acto de "Constitución" en BORME con fecha < 6 meses antes de la primera adjudicación.
    </div>
    <div class="card">
        <b>💰 F2 — Capital ridículo:</b> Capital social < 10.000€ (el más reciente en BORME) y adjudicación > 100.000€.
    </div>
    <div class="card">
        <b>💀 F4 — Disolución:</b> Acto de "Disolución|Extinción" en BORME entre 0 y 365 días después de una adjudicación.
    </div>
    <div class="card">
        <b>⚖️ F5 — Concursal:</b> Acto de "concurso|concursal" en BORME, con adjudicaciones posteriores a la fecha del concurso.
    </div>
    <div class="card">
        <b>🎯 F7 — Concentración:</b> Empresa gana >40% de adjudicaciones de un órgano (≥5 adj propias, ≥10 totales del órgano).
        En Catalunya: umbral adaptativo 20/30/40% según tamaño del órgano.
    </div>
    <div class="card">
        <b>🤝 F8 — UTEs:</b> Se parsean los miembros de cada UTE del nombre del adjudicatario y se cruzan con la red F6.
    </div>
    <div class="card">
        <b>📍 F9 — Geo:</b> CCAA de registro (provincia BORME) ≠ CCAA mayoritaria de contratos (NUTS2). Solo PYMEs (3–200 adj).
    </div>
    <div class="card">
        <b>✂️ F10 — Troceo (Catalunya):</b> Sliding window 90 días, ≥3 contratos ≤15K€ cuya suma > 15K€.
    </div>
    <div class="card">
        <b>📝 F11 — Modificaciones (Catalunya):</b> Empresas con ≥3 modificaciones y ≥20% de contratos modificados (media: 0.6%).
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">4. Filtro de grupos corporativos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-green">
        Muchos pares de empresas con administrador compartido son legítimos (filiales, fusiones, M&A).
        Se filtran automáticamente por tres vías:<br><br>
        <b>a) Nombre de marca:</b> Tokenizar nombres, calcular similitud Jaccard en tokens significativos.
        Si Jaccard ≥0.5 → grupo corporativo.<br>
        <b>b) Solapamiento de consejo:</b> >40% de personas compartidas con ≥3 en común → grupo.<br>
        <b>c) Fusiones BORME:</b> Ambas empresas con actos de fusión/absorción/escisión → grupo.<br><br>
        Nacional: 1.683 pares eliminados (953 nombre, 902 consejo, 287 fusiones).
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec">5. Limitaciones</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-amber">
        <b>Cobertura:</b> ~52% de adjudicatarios PLACSP cruzados con BORME.
        Autónomos, personas físicas y empresas extranjeras no figuran en BORME.<br><br>
        <b>Matching:</b> Por nombre normalizado, no por NIF. Posibles homónimos (falsos positivos)
        y variantes no capturadas (falsos negativos).<br><br>
        <b>Vigencia de cargos:</b> Depende de que el cese se publique en BORME. Cargos no cesados
        explícitamente aparecen como vigentes aunque hayan terminado de facto.<br><br>
        <b>Señal ≠ fraude.</b> Cada patrón detectado requiere revisión humana cualificada.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    st.markdown("""
    <div class="hero">
        <h1>🏛️ Contratación <span>Pública</span></h1>
        <p>BQUANT FINANCE · @GSNCHEZ</p>
        <div class="hero-desc">
            Cruzamos <b>8.7 millones de contratos públicos</b> con <b>17 millones de actos
            del Registro Mercantil</b> para detectar patrones que merecen atención.
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    flag_files = discover_flags()

    tabs = st.tabs(["📊 Resumen", "🔎 Explorar señales", "📋 Cómo funciona"])

    with tabs[0]:
        render_resumen(flag_files)

    with tabs[1]:
        render_explorar(flag_files)

    with tabs[2]:
        render_metodo()

    st.markdown("""
    <div class="ft">
        <a href="https://twitter.com/Gsnchez">@Gsnchez</a> ·
        <a href="https://bquantfinance.com">bquantfinance.com</a> ·
        <a href="https://github.com/BquantFinance">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
