# =============================================================================
# Brechas Territoriales Colombia - Versión Pro + Toque Melo
# Datos oficiales DANE + Diseño moderno + Gatito random
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import json
from urllib.request import urlopen
from datetime import datetime
import random
import time

st.set_page_config(
    page_title="Brechas Territoriales | Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- Estilos profesionales + modernos --------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', system-ui, sans-serif;
}

/* Fondo neutro */
.stApp {
    background-color: #f7f6f3;
}

/* Título */
.main-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2.45rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.15rem;
    letter-spacing: -0.4px;
    animation: fadeInDown 0.5s ease-out;
}

.subtitle {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 1.6rem;
    animation: fadeInDown 0.6s ease-out;
}

/* Animación de entrada del contenido */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Aplica animación al contenido principal de las pestañas */
div[data-testid="stVerticalBlock"] > div {
    animation: fadeInUp 0.45s ease-out;
}

/* Tabs con transición */
.stTabs [data-baseweb="tab"] {
    height: 44px;
    border-radius: 999px;
    padding: 0 20px;
    font-weight: 600;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #334155;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.stTabs [data-baseweb="tab"]:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: translateY(-1px);
}

.stTabs [aria-selected="true"] {
    background: #0f766e !important;
    color: white !important;
    border-color: #0f766e !important;
    box-shadow: 0 4px 14px rgba(15, 118, 110, 0.25);
    transform: translateY(-1px);
}

/* Métricas */
div[data-testid="stMetricValue"] {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1e293b;
    transition: color 0.2s ease;
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
}

/* Tarjetas con transición */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.08);
    border-color: #cbd5e1;
}

.card-title {
    font-weight: 700;
    font-size: 0.88rem;
    color: #0f766e;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* Sticker del gato */
.sticker {
    position: fixed;
    bottom: 25px;
    right: 25px;
    font-size: 3.6rem;
    z-index: 9999;
    animation: bounceIn 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12));
    pointer-events: none;
}

@keyframes bounceIn {
    0% { transform: scale(0); opacity: 0; }
    60% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(1); }
}

/* Mejor legibilidad */
p, li, span, label {
    color: #334155;
}

h1, h2, h3, h4 {
    color: #1e293b !important;
}

/* Suaviza los selectores y botones */
.stSelectbox > div > div, .stButton > button {
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------- Datos oficiales --------------------------
@st.cache_data
def load_data():
    depts = {
        "05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar",
        "15": "Boyacá", "17": "Caldas", "18": "Caquetá", "19": "Cauca",
        "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó",
        "41": "Huila", "44": "La Guajira", "47": "Magdalena", "50": "Meta",
        "52": "Nariño", "54": "Norte de Santander", "63": "Quindío",
        "66": "Risaralda", "68": "Santander", "70": "Sucre", "73": "Tolima",
        "76": "Valle del Cauca"
    }
    pobreza = {
        2023: {"05":22.5,"08":28.1,"11":21.0,"13":45.8,"15":32.4,"17":22.8,"18":38.5,"19":42.1,"20":40.2,"23":44.6,"25":18.9,"27":68.9,"41":38.7,"44":67.1,"47":48.9,"50":28.4,"52":38.8,"54":36.2,"63":26.5,"66":24.1,"68":25.3,"70":55.4,"73":34.8,"76":27.9},
        2024: {"05":20.8,"08":31.6,"11":19.6,"13":43.5,"15":30.9,"17":20.0,"18":36.2,"19":40.5,"20":38.7,"23":42.1,"25":20.1,"27":67.4,"41":40.4,"44":65.7,"47":51.7,"50":26.8,"52":39.2,"54":35.3,"63":25.1,"66":22.9,"68":24.0,"70":57.5,"73":35.6,"76":25.7},
        2025: {"05":18.9,"08":27.8,"11":17.8,"13":44.6,"15":31.6,"17":17.5,"18":34.1,"19":37.2,"20":36.5,"23":40.8,"25":15.1,"27":65.3,"41":35.8,"44":60.2,"47":46.5,"50":24.9,"52":33.4,"54":33.8,"63":23.4,"66":21.2,"68":22.1,"70":51.8,"73":28.0,"76":23.5}
    }
    desocupacion = {
        2023: {"05":10.2,"08":11.1,"11":10.5,"13":11.8,"15":10.4,"17":10.8,"18":14.5,"19":9.1,"20":11.6,"23":12.0,"25":10.9,"27":16.8,"41":9.5,"44":14.2,"47":11.9,"50":10.1,"52":7.8,"54":13.5,"63":12.4,"66":10.6,"68":11.2,"70":12.7,"73":12.1,"76":11.0},
        2024: {"05":9.4,"08":9.5,"11":9.1,"13":10.5,"15":9.8,"17":9.7,"18":13.9,"19":8.2,"20":10.8,"23":11.2,"25":10.2,"27":15.9,"41":8.4,"44":13.5,"47":10.7,"50":9.3,"52":6.5,"54":12.8,"63":11.5,"66":9.2,"68":10.4,"70":11.8,"73":11.4,"76":10.1},
        2025: {"05":7.5,"08":8.5,"11":8.2,"13":9.4,"15":9.3,"17":9.1,"18":10.4,"19":6.6,"20":9.9,"23":10.5,"25":9.6,"27":12.8,"41":6.8,"44":12.3,"47":9.5,"50":8.7,"52":6.0,"54":11.3,"63":10.3,"66":7.9,"68":10.1,"70":10.6,"73":10.8,"76":9.5}
    }
    rows = []
    for year in [2023, 2024, 2025]:
        for code, name in depts.items():
            rows.append({"codigo": code, "departamento": name, "anio": year,
                         "pobreza": pobreza[year][code], "desocupacion": desocupacion[year][code]})
    df = pd.DataFrame(rows)
    nacional = pd.DataFrame({"anio":[2023,2024,2025], "pobreza":[34.6,31.8,28.0], "desocupacion":[10.2,9.7,8.9]})
    return df, nacional

df, nacional = load_data()

@st.cache_data
def load_geojson():
    url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
    with urlopen(url) as r:
        geo = json.load(r)
    for f in geo["features"]:
        f["id"] = f["properties"]["NOMBRE_DPT"]
    return geo

geojson = load_geojson()
ALL_GEO_NAMES = [f["properties"]["NOMBRE_DPT"] for f in geojson["features"]]

NAME_MAP = {
    "Antioquia": "ANTIOQUIA", "Atlántico": "ATLANTICO", "Bogotá D.C.": "SANTAFE DE BOGOTA D.C",
    "Bolívar": "BOLIVAR", "Boyacá": "BOYACA", "Caldas": "CALDAS", "Caquetá": "CAQUETA",
    "Cauca": "CAUCA", "Cesar": "CESAR", "Córdoba": "CORDOBA", "Cundinamarca": "CUNDINAMARCA",
    "Chocó": "CHOCO", "Huila": "HUILA", "La Guajira": "LA GUAJIRA", "Magdalena": "MAGDALENA",
    "Meta": "META", "Nariño": "NARIÑO", "Norte de Santander": "NORTE DE SANTANDER",
    "Quindío": "QUINDIO", "Risaralda": "RISARALDA", "Santander": "SANTANDER",
    "Sucre": "SUCRE", "Tolima": "TOLIMA", "Valle del Cauca": "VALLE DEL CAUCA"
}

# -------------------------- Sidebar --------------------------
with st.sidebar:
    st.markdown("### ⚙️ Controles")
    st.caption("DANE · 23 departamentos + Bogotá")
    indicador = st.selectbox("Indicador", ["Pobreza monetaria (%)", "Tasa de desocupación (%)"])
    col_map = "pobreza" if "Pobreza" in indicador else "desocupacion"
    anio = st.selectbox("Año", [2025, 2024, 2023])
    dept_sel = st.selectbox("Departamento (series)", sorted(df["departamento"].unique()),
                            index=sorted(df["departamento"].unique()).index("Nariño"))
    st.markdown("---")
    st.info("Gris en el mapa = sin estimación oficial del DANE")
    
    # Descarga de datos
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar datos (CSV)", csv, "brechas_territoriales_dane.csv", "text/csv")

# -------------------------- Header --------------------------
st.markdown('<p class="main-title">Brechas territoriales del trabajo y la pobreza</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis espacial de las desigualdades regionales en Colombia · Datos oficiales DANE</p>', unsafe_allow_html=True)

nat = nacional[nacional["anio"] == anio].iloc[0]
data_anio = df[df["anio"] == anio]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nacional · Pobreza", f"{nat['pobreza']:.1f}%")
c2.metric("Nacional · Desocupación", f"{nat['desocupacion']:.1f}%")
top = data_anio.loc[data_anio["pobreza"].idxmax()]
c3.metric("Mayor pobreza", top["departamento"], delta=f"{top['pobreza']:.1f}%", delta_color="inverse")
low = data_anio.loc[data_anio["pobreza"].idxmin()]
c4.metric("Menor pobreza", low["departamento"], delta=f"{low['pobreza']:.1f}%")

# -------------------------- Tabs --------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["Resultados y Mapa", "Evolución", "Espacial (Moran + LISA)", "Brechas", "Asociación", "Comparador", "Método"]
)

# ===================== TAB 1 =====================
with tab1:
    st.markdown("### Principales hallazgos")
    brecha = data_anio["pobreza"].max() - data_anio["pobreza"].min()
    choco = data_anio.loc[data_anio["departamento"]=="Chocó", "pobreza"].values[0]
    cundi = data_anio.loc[data_anio["departamento"]=="Cundinamarca", "pobreza"].values[0]
    narino = data_anio.loc[data_anio["departamento"]=="Nariño", "pobreza"].values[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Brecha territorial</div>
            Diferencia entre Chocó ({choco:.1f}%) y Cundinamarca ({cundi:.1f}%): 
            <b>{brecha:.1f} puntos porcentuales</b> en {anio}.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Concentración</div>
            La pobreza más alta se concentra en el Caribe y el Pacífico 
            (Chocó, La Guajira, Sucre, Magdalena, Bolívar).
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Nariño</div>
            Pobreza de <b>{narino:.1f}%</b> en {anio} 
            (nacional: {nat['pobreza']:.1f}%).
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### Mapa de {indicador.lower()} · {anio}")
    st.caption("Pasa el mouse sobre los departamentos. Gris = sin dato oficial.")

    data_year = data_anio.copy()
    data_year["dept_geo"] = data_year["departamento"].map(NAME_MAP)
    full = pd.DataFrame({"dept_geo": ALL_GEO_NAMES})
    full = full.merge(data_year[["dept_geo", col_map, "departamento"]], on="dept_geo", how="left")
    full["valor"] = full[col_map].fillna(-1)

    vmin, vmax = data_year[col_map].min(), data_year[col_map].max()

    fig = px.choropleth(
        full, geojson=geojson, locations="dept_geo", featureidkey="properties.NOMBRE_DPT",
        color="valor",
        color_continuous_scale=[[0.0,"#c8c8c8"],[0.01,"#fef0d9"],[0.25,"#fdcc8a"],[0.5,"#fc8d59"],[0.75,"#e34a33"],[1.0,"#b30000"]],
        range_color=(-1, vmax*1.05),
        labels={"valor":"%"}, hover_data={"valor":False, "dept_geo":False}
    )
    fig.update_geos(center=dict(lat=4.15, lon=-73.0), projection_scale=5.8, visible=False, bgcolor="rgba(0,0,0,0)", showframe=False, fitbounds=False)
    fig.update_layout(margin=dict(r=0,t=15,l=0,b=0), height=700, paper_bgcolor="rgba(0,0,0,0)",
                      coloraxis_colorbar=dict(title="%", thickness=15, len=0.55, tickvals=[vmin,(vmin+vmax)/2,vmax],
                                              ticktext=[f"{vmin:.0f}",f"{(vmin+vmax)/2:.0f}",f"{vmax:.0f}"], bgcolor="#fffdf8"))
    fig.update_traces(marker_line_width=0.8, marker_line_color="#111111",
                      hovertemplate="<b>%{location}</b><br>Valor: %{z:.1f}%<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    ranking = data_anio.sort_values("pobreza", ascending=False)[["departamento","pobreza","desocupacion"]]
    ranking.columns = ["Departamento","Pobreza (%)","Desocupación (%)"]
    st.dataframe(ranking, use_container_width=True, hide_index=True)

# ===================== TAB 2: EVOLUCIÓN =====================
with tab2:
    st.subheader(f"Evolución temporal · {dept_sel}")
    serie = df[df["departamento"]==dept_sel].sort_values("anio")
    st.markdown(f"Evolución de **pobreza monetaria** y **tasa de desocupación** en **{dept_sel}** (2023-2025).")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie["anio"], y=serie["pobreza"], mode="lines+markers", name="Pobreza monetaria (%)",
                             line=dict(color="#b30000", width=3), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=serie["anio"], y=serie["desocupacion"], mode="lines+markers", name="Desocupación (%)",
                             line=dict(color="#0f6e6b", width=3), marker=dict(size=10), yaxis="y2"))
    fig.update_layout(
        height=450, xaxis=dict(title="Año", tickvals=[2023,2024,2025]),
        yaxis=dict(title=dict(text="Pobreza monetaria (%)", font=dict(color="#b30000")), tickfont=dict(color="#b30000")),
        yaxis2=dict(title=dict(text="Desocupación (%)", font=dict(color="#0f6e6b")), tickfont=dict(color="#0f6e6b"), overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1), margin=dict(t=50), plot_bgcolor="#fffdf8", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("Serie corta (T=3). No se realizan proyecciones ni modelos SpVAR por falta de suficiente dimensión temporal.")

# ===================== TAB 3: ESPACIAL + LISA =====================
with tab3:
    st.subheader("Análisis espacial: Moran global + aproximación LISA")

    data_year = df[df["anio"]==anio].set_index("codigo")
    y = data_year[col_map].values
    n = len(y)
    vecinos = {
        "05":["15","17","18","27","68","73"],"08":["13","20","47"],"11":["25"],
        "13":["08","20","23","47","70"],"15":["05","25","54","68"],"17":["05","63","66","73"],
        "18":["05","19","41","50"],"19":["18","27","41","52","76"],"20":["08","13","44","47","54"],
        "23":["13","27","70"],"25":["11","15","50","73"],"27":["05","19","23","76"],
        "41":["18","19","50","73"],"44":["20"],"47":["08","13","20"],"50":["18","25","41","73"],
        "52":["19"],"54":["15","20","68"],"63":["17","66","73"],"66":["17","63","76"],
        "68":["05","15","54"],"70":["13","23"],"73":["05","17","25","41","50","63"],
        "76":["19","27","66"]
    }
    codes = list(data_year.index)
    W = np.zeros((n,n))
    for i,c in enumerate(codes):
        neigh = [v for v in vecinos.get(c,[]) if v in codes]
        if neigh:
            for v in neigh: W[i, codes.index(v)] = 1.0
            W[i] /= W[i].sum()

    z = y - y.mean()
    I = (n / W.sum()) * (z @ W @ z) / (z @ z)
    np.random.seed(42)
    I_perm = [(n/W.sum())*(np.random.permutation(z)@W@np.random.permutation(z))/(z@z) for _ in range(499)]
    p_val = (np.sum(np.array(I_perm) >= I)+1)/500

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Moran's I", f"{I:.4f}")
    col_b.metric("p-valor", f"{p_val:.4f}")
    col_c.metric("Resultado", "Significativo ✅" if p_val < 0.05 else "No significativo")

    # LISA simplificado (cuadrantes)
    lag = W @ z
    lisa_type = []
    for zi, li in zip(z, lag):
        if zi > 0 and li > 0: lisa_type.append("Alto-Alto (HH)")
        elif zi < 0 and li < 0: lisa_type.append("Bajo-Bajo (LL)")
        elif zi > 0 and li < 0: lisa_type.append("Alto-Bajo (HL)")
        elif zi < 0 and li > 0: lisa_type.append("Bajo-Alto (LH)")
        else: lisa_type.append("No clasificado")

    lisa_df = pd.DataFrame({
        "Departamento": data_year.reset_index()["codigo"].map({v:k for k,v in {**{c:c for c in codes}}.items()}).values if False else data_anio.set_index("codigo").loc[codes]["departamento"].values,
        "Valor": y,
        "Lag espacial": lag,
        "Cuadrante LISA": lisa_type
    })
    st.markdown("#### Clasificación LISA (cuadrantes)")
    st.dataframe(lisa_df.sort_values("Valor", ascending=False), use_container_width=True, hide_index=True)
    st.caption("HH = cluster de valores altos · LL = cluster de valores bajos · HL/LH = outliers espaciales")

# ===================== TAB 4: BRECHAS =====================
with tab4:
    st.subheader(f"Brechas vs promedio nacional · {anio}")
    data_year = data_anio.copy()
    data_year["brecha"] = data_year[col_map] - nat[col_map]
    data_year = data_year.sort_values("brecha")
    fig = px.bar(data_year, x="brecha", y="departamento", orientation="h", color="brecha",
                 color_continuous_scale=["#0f6e6b","#fef0d9","#9a3412"], labels={"brecha":"Diferencia (pp)"}, height=700)
    fig.add_vline(x=0, line_dash="dash", line_color="#1a2332")
    st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 5: ASOCIACIÓN =====================
with tab5:
    st.subheader(f"Pobreza vs Desocupación · {anio}")
    data_year = data_anio.copy()
    slope, intercept, r, p, _ = stats.linregress(data_year["desocupacion"], data_year["pobreza"])
    fig = px.scatter(data_year, x="desocupacion", y="pobreza", text="departamento", color="pobreza",
                     color_continuous_scale=["#fef0d9","#fc8d59","#b30000"], height=520)
    fig.update_traces(textposition="top center", textfont_size=10, marker=dict(size=14, line=dict(width=1,color="white")))
    x_line = np.linspace(data_year["desocupacion"].min(), data_year["desocupacion"].max(), 40)
    fig.add_trace(go.Scatter(x=x_line, y=intercept+slope*x_line, mode="lines", name=f"OLS R²={r**2:.3f}",
                             line=dict(color="#1a2332", width=2, dash="dot")))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Pendiente:** {slope:.2f} | **R²:** {r**2:.3f} | **p-valor:** {p:.4f}")
    st.info("Relación descriptiva. No implica causalidad.")

# ===================== TAB 6: COMPARADOR =====================
with tab6:
    st.subheader("Comparador de departamentos")
    cols = st.columns(2)
    with cols[0]:
        d1 = st.selectbox("Departamento 1", sorted(df["departamento"].unique()), index=sorted(df["departamento"].unique()).index("Nariño"), key="d1")
    with cols[1]:
        d2 = st.selectbox("Departamento 2", sorted(df["departamento"].unique()), index=sorted(df["departamento"].unique()).index("Chocó"), key="d2")

    s1 = df[df["departamento"]==d1].set_index("anio")
    s2 = df[df["departamento"]==d2].set_index("anio")

    comp = pd.DataFrame({
        "Año": [2023,2024,2025],
        f"Pobreza {d1}": s1.loc[[2023,2024,2025],"pobreza"].values,
        f"Pobreza {d2}": s2.loc[[2023,2024,2025],"pobreza"].values,
        f"Desocupación {d1}": s1.loc[[2023,2024,2025],"desocupacion"].values,
        f"Desocupación {d2}": s2.loc[[2023,2024,2025],"desocupacion"].values,
    })
    st.dataframe(comp, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comp["Año"], y=comp[f"Pobreza {d1}"], mode="lines+markers", name=f"Pobreza {d1}", line=dict(width=3)))
    fig.add_trace(go.Scatter(x=comp["Año"], y=comp[f"Pobreza {d2}"], mode="lines+markers", name=f"Pobreza {d2}", line=dict(width=3)))
    fig.update_layout(height=400, title="Comparación de pobreza monetaria", plot_bgcolor="#fffdf8", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 7: MÉTODO =====================
with tab7:
    st.subheader("Método, fuentes y limitaciones")
    st.markdown(f"""
### Objetivo
Identificar patrones territoriales de pobreza monetaria y desocupación, evaluar su distribución espacial 
y explorar asociaciones estadísticas entre ambos indicadores.

### Fuentes oficiales
- DANE – Anexo de Pobreza Monetaria Departamental (2023-2025)
- DANE – GEIH Departamentos

### Cobertura
Solo **23 departamentos + Bogotá**. Los demás aparecen en gris porque el DANE no publica estimación departamental.

### Análisis espacial
- Matriz de pesos: contigüidad Queen  
- Moran’s I global + clasificación LISA por cuadrantes  
- 499 permutaciones para el p-valor

### Limitaciones
- Serie temporal corta (T=3) → no se estiman SAR/SEM/SpVAR  
- No se imputan datos faltantes  
- La relación pobreza-desocupación es correlacional

**Fecha de construcción:** {datetime.now().strftime("%Y-%m-%d")}
    """)

st.markdown("---")
st.caption("Investigación con datos oficiales DANE ·")
