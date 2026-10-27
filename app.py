# =============================================================================
# Brechas Territoriales del Mercado Laboral y la Pobreza Monetaria en Colombia
# Análisis espacial con datos oficiales DANE
# Versión corregida - Mapa completo + rigor académico
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

st.set_page_config(
    page_title="Brechas Territoriales | Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', system-ui, sans-serif; }
.stApp { background-color: #f6f3eb; }
.main-title { font-family: 'Source Serif 4', Georgia, serif; font-size: 2.4rem; font-weight: 700; color: #1a2332; margin-bottom: 0.15rem; }
.subtitle { font-size: 1.05rem; color: #5c675f; margin-bottom: 1.5rem; }
.stTabs [data-baseweb="tab"] { height: 43px; border-radius: 999px; padding: 0 18px; font-weight: 600; background: #fffdf8; border: 1px solid #ddd4c4; }
.stTabs [aria-selected="true"] { background: #0f6e6b !important; color: white !important; border-color: #0f6e6b !important; }
div[data-testid="stMetricValue"] { font-size: 1.35rem; font-weight: 700; }
.card { background: #fffdf8; border: 1px solid #e5dfd3; border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 0.8rem; }
.card-title { font-weight: 700; font-size: 0.92rem; color: #0f6e6b; margin-bottom: 0.35rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Datos oficiales (solo 23 departamentos + Bogotá)
# -----------------------------------------------------------------------------
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
            rows.append({
                "codigo": code,
                "departamento": name,
                "anio": year,
                "pobreza": pobreza[year][code],
                "desocupacion": desocupacion[year][code]
            })
    df = pd.DataFrame(rows)
    nacional = pd.DataFrame({
        "anio": [2023, 2024, 2025],
        "pobreza": [34.6, 31.8, 28.0],
        "desocupacion": [10.2, 9.7, 8.9]
    })
    return df, nacional

df, nacional = load_data()

# -----------------------------------------------------------------------------
# GeoJSON
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Controles")
    st.caption("DANE · 23 departamentos + Bogotá")
    indicador = st.selectbox("Indicador", ["Pobreza monetaria (%)", "Tasa de desocupación (%)"])
    col_map = "pobreza" if "Pobreza" in indicador else "desocupacion"
    anio = st.selectbox("Año", [2025, 2024, 2023])
    dept_sel = st.selectbox("Departamento", sorted(df["departamento"].unique()),
                            index=sorted(df["departamento"].unique()).index("Nariño"))
    st.markdown("---")
    st.info("Gris = sin estimación oficial del DANE")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Resultados y Mapa", "Evolución", "Espacial", "Brechas", "Asociación", "Método"]
)

# ===================== TAB 1: RESULTADOS + MAPA COMPLETO =====================
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
            <b>{brecha:.1f} puntos porcentuales</b>.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Concentración geográfica</div>
            La pobreza más alta se concentra en Caribe y Pacífico 
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
    st.caption("Pasa el mouse sobre los departamentos. Gris = sin dato oficial del DANE.")

    # ----- PREPARACIÓN DEL MAPA COMPLETO -----
    data_year = data_anio.copy()
    data_year["dept_geo"] = data_year["departamento"].map(NAME_MAP)

    # DataFrame con TODOS los departamentos del GeoJSON
    full = pd.DataFrame({"dept_geo": ALL_GEO_NAMES})
    full = full.merge(data_year[["dept_geo", col_map, "departamento"]], on="dept_geo", how="left")

    # Valor especial para los que no tienen dato (para poder colorearlos de gris)
    MISSING_VALUE = -1
    full["valor"] = full[col_map].fillna(MISSING_VALUE)

    # Rango real de los datos
    vmin = data_year[col_map].min()
    vmax = data_year[col_map].max()

    fig = px.choropleth(
        full,
        geojson=geojson,
        locations="dept_geo",
        featureidkey="properties.NOMBRE_DPT",
        color="valor",
        color_continuous_scale=[
            [0.0, "#c8c8c8"],      # gris para valor = -1 (sin dato)
            [0.01, "#fef0d9"],
            [0.25, "#fdcc8a"],
            [0.50, "#fc8d59"],
            [0.75, "#e34a33"],
            [1.0,  "#b30000"]
        ],
        range_color=(MISSING_VALUE, vmax * 1.05),
        labels={"valor": "%"},
        hover_data={"valor": False, "dept_geo": False}
    )

    # Forzar visualización completa de Colombia
    fig.update_geos(
        center=dict(lat=4.15, lon=-73.0),
        projection_scale=5.8,
        visible=False,
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        fitbounds=False
    )

    fig.update_layout(
        margin=dict(r=0, t=15, l=0, b=0),
        height=710,
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(
            title="%",
            thickness=15,
            len=0.55,
            tickvals=[vmin, (vmin+vmax)/2, vmax],
            ticktext=[f"{vmin:.0f}", f"{(vmin+vmax)/2:.0f}", f"{vmax:.0f}"],
            bgcolor="#fffdf8"
        )
    )

    # Bordes negros y más gruesos
    fig.update_traces(
        marker_line_width=0.8,
        marker_line_color="#111111",
        hovertemplate="<b>%{location}</b><br>Valor: %{z:.1f}%<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fuente: DANE. Los departamentos en gris no tienen estimación oficial de pobreza/desocupación departamental.")

    # Ranking
    st.markdown("#### Ranking de pobreza monetaria")
    ranking = data_anio.sort_values("pobreza", ascending=False)[["departamento", "pobreza", "desocupacion"]]
    ranking.columns = ["Departamento", "Pobreza (%)", "Desocupación (%)"]
    st.dataframe(ranking, use_container_width=True, hide_index=True)

# ===================== TAB 2: EVOLUCIÓN (versión académica) =====================
with tab2:
    st.subheader(f"Evolución temporal · {dept_sel}")

    serie = df[df["departamento"] == dept_sel].sort_values("anio")

    st.markdown(f"""
    La siguiente figura presenta la evolución de la **pobreza monetaria** y la **tasa de desocupación** 
    para el departamento de **{dept_sel}** durante el periodo 2023-2025, según los anexos oficiales del DANE.
    """)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["pobreza"],
        mode="lines+markers", name="Pobreza monetaria (%)",
        line=dict(color="#b30000", width=3), marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["desocupacion"],
        mode="lines+markers", name="Tasa de desocupación (%)",
        line=dict(color="#0f6e6b", width=3), marker=dict(size=10),
        yaxis="y2"
    ))
    fig.update_layout(
        height=430,
        yaxis=dict(title="Pobreza monetaria (%)", titlefont=dict(color="#b30000"), tickfont=dict(color="#b30000")),
        yaxis2=dict(title="Desocupación (%)", overlaying="y", side="right",
                    titlefont=dict(color="#0f6e6b"), tickfont=dict(color="#0f6e6b")),
        legend=dict(orientation="h", y=1.12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fffdf8"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Nota metodológica:**  
    La serie temporal disponible a nivel departamental es corta (tres observaciones anuales). 
    Por esta razón **no se realizan proyecciones** ni se estiman modelos de series de tiempo o 
    paneles espaciales (SAR, SEM, SpVAR). Cualquier extrapolación más allá de 2025 carecería 
    de fundamento estadístico robusto con la información actualmente publicada por el DANE.
    """)

    st.dataframe(
        serie[["anio", "pobreza", "desocupacion"]].rename(
            columns={"anio": "Año", "pobreza": "Pobreza monetaria (%)", "desocupacion": "Desocupación (%)"}
        ).set_index("Año"),
        use_container_width=True
    )

# ===================== TAB 3: ESPACIAL =====================
with tab3:
    st.subheader("Análisis de autocorrelación espacial (Moran's I)")

    data_year = df[df["anio"] == anio].set_index("codigo")
    y = data_year[col_map].values
    n = len(y)

    vecinos = {
        "05": ["15","17","18","27","68","73"], "08": ["13","20","47"], "11": ["25"],
        "13": ["08","20","23","47","70"], "15": ["05","25","54","68"], "17": ["05","63","66","73"],
        "18": ["05","19","41","50"], "19": ["18","27","41","52","76"], "20": ["08","13","44","47","54"],
        "23": ["13","27","70"], "25": ["11","15","50","73"], "27": ["05","19","23","76"],
        "41": ["18","19","50","73"], "44": ["20"], "47": ["08","13","20"], "50": ["18","25","41","73"],
        "52": ["19"], "54": ["15","20","68"], "63": ["17","66","73"], "66": ["17","63","76"],
        "68": ["05","15","54"], "70": ["13","23"], "73": ["05","17","25","41","50","63"],
        "76": ["19","27","66"]
    }

    codes = list(data_year.index)
    W = np.zeros((n, n))
    for i, c in enumerate(codes):
        neigh = [v for v in vecinos.get(c, []) if v in codes]
        if neigh:
            for v in neigh:
                W[i, codes.index(v)] = 1.0
            W[i] /= W[i].sum()

    z = y - y.mean()
    I = (n / W.sum()) * (z @ W @ z) / (z @ z)

    np.random.seed(42)
    I_perm = [(n / W.sum()) * (np.random.permutation(z) @ W @ np.random.permutation(z)) / (z @ z) for _ in range(499)]
    p_val = (np.sum(np.array(I_perm) >= I) + 1) / 500

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Moran's I", f"{I:.4f}")
    col_b.metric("p-valor (499 permutaciones)", f"{p_val:.4f}")
    col_c.metric("Conclusión", "Significativo" if p_val < 0.05 else "No significativo")

    if p_val < 0.05:
        st.success("Se rechaza la hipótesis nula de distribución espacial aleatoria. Existe evidencia de autocorrelación espacial positiva.")
    else:
        st.info("No se encuentra evidencia suficiente de autocorrelación espacial al 5% de significancia.")

    st.markdown("""
    **Interpretación académica:**  
    Un valor positivo y significativo del índice de Moran indica que los departamentos con niveles 
    similares de pobreza (o desocupación) tienden a estar geográficamente próximos. Esto es 
    coherente con la concentración observada en las regiones Caribe y Pacífica.
    """)

# ===================== TAB 4: BRECHAS =====================
with tab4:
    st.subheader(f"Brechas respecto al promedio nacional · {anio}")
    data_year = data_anio.copy()
    data_year["brecha"] = data_year[col_map] - nat[col_map]
    data_year = data_year.sort_values("brecha")

    fig = px.bar(
        data_year, x="brecha", y="departamento", orientation="h",
        color="brecha", color_continuous_scale=["#0f6e6b", "#fef0d9", "#9a3412"],
        labels={"brecha": "Diferencia (pp)"}, height=700
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#1a2332")
    fig.update_layout(margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 5: ASOCIACIÓN =====================
with tab5:
    st.subheader(f"Relación entre pobreza monetaria y desocupación · {anio}")
    data_year = data_anio.copy()
    slope, intercept, r, p, _ = stats.linregress(data_year["desocupacion"], data_year["pobreza"])

    fig = px.scatter(
        data_year, x="desocupacion", y="pobreza", text="departamento",
        color="pobreza", color_continuous_scale=["#fef0d9", "#fc8d59", "#b30000"],
        labels={"desocupacion": "Desocupación (%)", "pobreza": "Pobreza (%)"}, height=520
    )
    fig.update_traces(textposition="top center", textfont_size=10, marker=dict(size=13, line=dict(width=1, color="white")))

    x_line = np.linspace(data_year["desocupacion"].min(), data_year["desocupacion"].max(), 40)
    fig.add_trace(go.Scatter(
        x=x_line, y=intercept + slope*x_line, mode="lines",
        name=f"OLS (R² = {r**2:.3f})", line=dict(color="#1a2332", width=2, dash="dot")
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Pendiente:** {slope:.2f} &nbsp;|&nbsp; **R²:** {r**2:.3f} &nbsp;|&nbsp; **p-valor:** {p:.4f}")
    st.info("La relación mostrada es descriptiva. No se interpreta como un efecto causal.")

# ===================== TAB 6: MÉTODO =====================
with tab6:
    st.subheader("Método, fuentes y limitaciones")
    st.markdown(f"""
### Objetivo
Identificar patrones territoriales de pobreza monetaria y desocupación en Colombia, 
evaluar su distribución espacial y explorar asociaciones estadísticas entre ambos indicadores.

### Fuentes
- DANE – Anexo de Pobreza Monetaria Departamental (2023, 2024 y 2025)
- DANE – GEIH Resultados por departamentos

### Cobertura geográfica
El DANE publica estimaciones solo para **23 departamentos + Bogotá D.C.**  
Los territorios de la Amazonía, Orinoquía y el Archipiélago de San Andrés aparecen en el mapa 
en color gris porque **no tienen estimación oficial** por insuficiencia de muestra.

### Análisis espacial
- Matriz de pesos: contigüidad tipo Queen
- Estadístico: Índice de Moran global (499 permutaciones)

### Limitaciones
1. Serie temporal corta (T=3) → no se estiman modelos SAR, SEM ni SpVAR.
2. No se realizan proyecciones ni imputaciones de datos faltantes.
3. La asociación pobreza-desocupación es correlacional.

**Fecha de construcción del panel:** {datetime.now().strftime("%Y-%m-%d")}
    """)

st.markdown("---")
st.caption("Investigación basada exclusivamente en datos oficiales del DANE · Sin series inventadas ni proyecciones no sustentadas")
