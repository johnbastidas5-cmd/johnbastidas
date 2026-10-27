# =============================================================================
# Brechas Territoriales del Mercado Laboral y la Pobreza Monetaria en Colombia
# Análisis espacial con datos oficiales DANE
# Versión profesional - Proyecto de investigación
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

# -------------------------- Configuración --------------------------
st.set_page_config(
    page_title="Brechas Territoriales | Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', system-ui, sans-serif; }
.stApp { background-color: #f7f4ec; }

.main-title {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a2332;
    margin-bottom: 0.15rem;
    line-height: 1.15;
}
.subtitle {
    font-size: 1.08rem;
    color: #5c675f;
    margin-bottom: 1.8rem;
}
.stTabs [data-baseweb="tab"] {
    height: 43px;
    border-radius: 999px;
    padding: 0 20px;
    font-weight: 600;
    background: #fffdf8;
    border: 1px solid #ddd4c4;
}
.stTabs [aria-selected="true"] {
    background: #0f6e6b !important;
    color: white !important;
    border-color: #0f6e6b !important;
}
div[data-testid="stMetricValue"] { font-size: 1.45rem; font-weight: 700; color: #1a2332; }
div[data-testid="stMetricLabel"] { color: #5c675f; }
.highlight-box {
    background: #fffdf8;
    border-left: 5px solid #0f6e6b;
    padding: 1rem 1.3rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 1rem;
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

@st.cache_data
def load_geojson():
    url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
    with urlopen(url) as r:
        geo = json.load(r)
    for f in geo["features"]:
        f["id"] = f["properties"]["NOMBRE_DPT"]
    return geo

geojson = load_geojson()

NAME_MAP = {
    "Antioquia": "ANTIOQUIA", "Atlántico": "ATLANTICO", "Bogotá D.C.": "SANTAFE DE BOGOTA D.C",
    "Bolívar": "BOLIVAR", "Boyacá": "BOYACA", "Caldas": "CALDAS", "Caquetá": "CAQUETA",
    "Cauca": "CAUCA", "Cesar": "CESAR", "Córdoba": "CORDOBA", "Cundinamarca": "CUNDINAMARCA",
    "Chocó": "CHOCO", "Huila": "HUILA", "La Guajira": "LA GUAJIRA", "Magdalena": "MAGDALENA",
    "Meta": "META", "Nariño": "NARIÑO", "Norte de Santander": "NORTE DE SANTANDER",
    "Quindío": "QUINDIO", "Risaralda": "RISARALDA", "Santander": "SANTANDER",
    "Sucre": "SUCRE", "Tolima": "TOLIMA", "Valle del Cauca": "VALLE DEL CAUCA"
}

ALL_GEO_NAMES = [f["properties"]["NOMBRE_DPT"] for f in geojson["features"]]

# -------------------------- Sidebar --------------------------
with st.sidebar:
    st.markdown("### Controles")
    st.caption("DANE · GEIH · 23 deptos + Bogotá")
    indicador = st.selectbox("Indicador", ["Pobreza monetaria (%)", "Tasa de desocupación (%)"])
    col_map = "pobreza" if "Pobreza" in indicador else "desocupacion"
    anio = st.selectbox("Año", [2025, 2024, 2023])
    dept_sel = st.selectbox("Departamento", sorted(df["departamento"].unique()),
                            index=sorted(df["departamento"].unique()).index("Nariño"))
    st.markdown("---")
    st.info("Departamentos en gris: sin estimación oficial del DANE.")

# -------------------------- Header --------------------------
st.markdown('<p class="main-title">Brechas territoriales del trabajo y la pobreza</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Análisis espacial de las desigualdades regionales en Colombia · Datos oficiales DANE</p>', unsafe_allow_html=True)

# Métricas
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Resultados + Mapa", "Evolución", "Espacial", "Brechas", "Asociación", "Método"]
)

# ===================== TAB 1: RESULTADOS + MAPA =====================
with tab1:
    st.markdown("### Principales hallazgos")

    # Cálculos de hallazgos
    brecha_max = data_anio["pobreza"].max() - data_anio["pobreza"].min()
    choco = data_anio[data_anio["departamento"]=="Chocó"]["pobreza"].values[0]
    cundinamarca = data_anio[data_anio["departamento"]=="Cundinamarca"]["pobreza"].values[0]
    nariño_val = data_anio[data_anio["departamento"]=="Nariño"]["pobreza"].values[0]

    col_a, col_b = st.columns([1.1, 1])

    with col_a:
        st.markdown(f"""
        <div class="highlight-box">
        <b>Brecha territorial extrema</b><br>
        En {anio} la diferencia entre el departamento con mayor pobreza (Chocó: <b>{choco:.1f}%</b>) 
        y el de menor pobreza (Cundinamarca: <b>{cundinamarca:.1f}%</b>) fue de 
        <b>{brecha_max:.1f} puntos porcentuales</b>.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="highlight-box">
        <b>Concentración geográfica</b><br>
        Los niveles más altos de pobreza monetaria se concentran en la región Caribe y el Pacífico 
        (Chocó, La Guajira, Sucre, Magdalena y Bolívar).
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="highlight-box">
        <b>Nariño</b><br>
        En {anio} registró una pobreza monetaria de <b>{nariño_val:.1f}%</b>, 
        por encima del promedio nacional ({nat['pobreza']:.1f}%).
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="highlight-box">
        <b>Cobertura de datos</b><br>
        El DANE publica estimaciones departamentales solo para 23 departamentos + Bogotá. 
        Los territorios de la Amazonía, Orinoquía y San Andrés aparecen en gris porque no tienen dato oficial.
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        # Ranking top 5
        ranking = data_anio.sort_values("pobreza", ascending=False)[["departamento", "pobreza", "desocupacion"]].head(8)
        ranking = ranking.rename(columns={"departamento": "Departamento", "pobreza": "Pobreza (%)", "desocupacion": "Desocupación (%)"})
        st.markdown("**Departamentos con mayor pobreza monetaria**")
        st.dataframe(ranking, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"### Mapa de {indicador.lower()} · {anio}")

    # ---------- MAPA DE CALOR CORRECTO ----------
    data_year = data_anio.copy()
    data_year["dept_geo"] = data_year["departamento"].map(NAME_MAP)

    # DataFrame completo
    full = pd.DataFrame({"dept_geo": ALL_GEO_NAMES})
    full = full.merge(data_year[["dept_geo", col_map, "departamento"]], on="dept_geo", how="left")

    # Solo usamos los que tienen valor real para el color
    full_plot = full.copy()
    full_plot["valor_plot"] = full_plot[col_map]  # NaN se quedan como NaN

    fig = px.choropleth(
        full_plot,
        geojson=geojson,
        locations="dept_geo",
        featureidkey="properties.NOMBRE_DPT",
        color="valor_plot",
        color_continuous_scale=["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"],
        range_color=(data_year[col_map].min() * 0.92, data_year[col_map].max() * 1.03),
        labels={"valor_plot": "%"},
        hover_name="departamento",
        hover_data={"valor_plot": ":.1f", "dept_geo": False}
    )

    # Configuración geográfica para ver TODO Colombia
    fig.update_geos(
        center=dict(lat=4.1, lon=-73.0),
        projection_scale=5.9,
        visible=False,
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        fitbounds=False
    )

    fig.update_layout(
        margin=dict(r=0, t=20, l=0, b=0),
        height=680,
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(
            title="%",
            thickness=16,
            len=0.55,
            bgcolor="#fffdf8",
            borderwidth=1,
            bordercolor="#ddd4c4"
        )
    )

    # Los NaN se ven grises por defecto en Plotly cuando no tienen valor
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="#555555",
        colorscale=["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Escala de color solo aplica a los 23 departamentos + Bogotá. Gris = sin dato oficial del DANE.")

# ===================== TAB 2: EVOLUCIÓN =====================
with tab2:
    st.subheader(f"Evolución · {dept_sel}")
    serie = df[df["departamento"] == dept_sel].sort_values("anio")

    years = serie["anio"].values
    y_pob = serie["pobreza"].values
    slope, intercept, r_value, _, _ = stats.linregress(years, y_pob)
    future_years = np.arange(2026, 2036)
    future_pob = np.clip(intercept + slope * future_years, 5, 75)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=y_pob, mode="lines+markers", name="Observado (DANE)",
        line=dict(color="#0f6e6b", width=3), marker=dict(size=11)
    ))
    fig.add_trace(go.Scatter(
        x=future_years, y=future_pob, mode="lines+markers", name="Proyección ilustrativa (lineal)",
        line=dict(color="#9a3412", width=2, dash="dot"), marker=dict(size=7)
    ))
    fig.update_layout(
        height=430, yaxis_title="Pobreza monetaria (%)",
        legend=dict(orientation="h", y=1.12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fffdf8"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning("La línea punteada es una **extrapolación lineal simple** de solo 3 observaciones. No constituye un pronóstico oficial ni un modelo SpVAR.")

    st.dataframe(
        serie[["anio", "pobreza", "desocupacion"]].rename(
            columns={"anio": "Año", "pobreza": "Pobreza (%)", "desocupacion": "Desocupación (%)"}
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
        st.success("Se rechaza la hipótesis de distribución espacial aleatoria. Existe autocorrelación espacial positiva (los valores similares tienden a agruparse geográficamente).")
    else:
        st.info("No se encuentra evidencia suficiente de autocorrelación espacial al nivel de significancia del 5%.")

    st.markdown("""
    **Interpretación:** Un Moran’s I positivo y significativo indica que departamentos con alta (o baja) 
    pobreza/desocupación tienden a tener vecinos con valores similares. Esto es coherente con la 
    concentración de pobreza en el Caribe y el Pacífico.
    """)

# ===================== TAB 4: BRECHAS =====================
with tab4:
    st.subheader(f"Brechas respecto al promedio nacional · {anio}")
    data_year = df[df["anio"] == anio].copy()
    data_year["brecha"] = data_year[col_map] - nat[col_map]
    data_year = data_year.sort_values("brecha")

    fig = px.bar(
        data_year, x="brecha", y="departamento", orientation="h",
        color="brecha",
        color_continuous_scale=["#0f6e6b", "#fef0d9", "#9a3412"],
        labels={"brecha": "Diferencia vs nacional (pp)"},
        height=700
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#1a2332", line_width=1.5)
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ===================== TAB 5: ASOCIACIÓN =====================
with tab5:
    st.subheader(f"Relación entre pobreza y desocupación · {anio}")
    data_year = df[df["anio"] == anio]

    slope, intercept, r, p, se = stats.linregress(data_year["desocupacion"], data_year["pobreza"])

    fig = px.scatter(
        data_year, x="desocupacion", y="pobreza", text="departamento",
        color="pobreza",
        color_continuous_scale=["#fef0d9", "#fc8d59", "#b30000"],
        labels={"desocupacion": "Tasa de desocupación (%)", "pobreza": "Pobreza monetaria (%)"},
        height=530
    )
    fig.update_traces(textposition="top center", textfont_size=10, marker=dict(size=14, line=dict(width=1, color="white")))

    x_line = np.linspace(data_year["desocupacion"].min(), data_year["desocupacion"].max(), 50)
    fig.add_trace(go.Scatter(
        x=x_line, y=intercept + slope * x_line, mode="lines",
        name=f"Regresión OLS (R² = {r**2:.3f})",
        line=dict(color="#1a2332", width=2, dash="dot")
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    **Resultados de la regresión lineal simple**  
    - Pendiente: **{slope:.2f}**  
    - R²: **{r**2:.3f}**  
    - p-valor: **{p:.4f}**
    """)
    st.info("Esta relación es **descriptiva**. No se interpreta como efecto causal. Ambas variables están influenciadas por factores estructurales comunes.")

# ===================== TAB 6: MÉTODO =====================
with tab6:
    st.subheader("Método, fuentes y limitaciones")
    st.markdown(f"""
### Objetivo de la investigación
Identificar patrones territoriales de pobreza monetaria y desocupación en Colombia, 
evaluar su distribución espacial y explorar asociaciones estadísticas entre ambos indicadores.

### Fuentes de datos (oficiales)
- **DANE** – Anexo de Pobreza Monetaria Departamental (años 2023, 2024 y 2025)
- **DANE** – Gran Encuesta Integrada de Hogares (GEIH) – Resultados por departamentos

### Cobertura geográfica
Solo **23 departamentos + Bogotá D.C.** tienen estimación oficial.  
Los departamentos de Amazonas, Arauca, Casanare, Guainía, Guaviare, Putumayo, Vaupés, Vichada 
y el Archipiélago de San Andrés **no tienen dato** por insuficiencia de muestra en la GEIH.  
En el mapa aparecen en color gris neutro.

### Análisis espacial
- Matriz de pesos espaciales: contigüidad tipo **Queen**
- Estadístico: **Índice de Moran global** con p-valor calculado por 499 permutaciones aleatorias

### Limitaciones (transparencia metodológica)
1. La serie temporal es corta (T = 3 años) → no es posible estimar modelos SAR, SEM, SDM o SpVAR de forma robusta.
2. La asociación entre pobreza y desocupación es correlacional, no causal.
3. No se imputaron ni inventaron valores para los departamentos sin cobertura oficial.

**Fecha de construcción del panel:** {datetime.now().strftime("%Y-%m-%d")}
    """)

st.markdown("---")
st.caption("Investigación basada exclusivamente en datos oficiales del DANE · Sin series inventadas ni modelos sobre-especificados")
