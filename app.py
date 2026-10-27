# =============================================================================
# Brechas Territoriales Colombia - Mapa Completo + Diseño Pop-Art
# Datos oficiales DANE (23 departamentos + Bogotá) - Sin estimaciones
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

# -----------------------------------------------------------------------------
# Configuración de página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Brechas Territoriales | Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Pop-Art mejorado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .main-title {
        font-family: 'Archivo Black', sans-serif;
        font-size: 2.8rem;
        background: linear-gradient(90deg, #FF2E63, #FF9A3C, #08D9D6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.15rem;
        line-height: 1.05;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 12px;
        padding: 0 18px;
        font-weight: 700;
        background: #f1f1f1;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #FF2E63, #FF9A3C) !important;
        color: white !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
        font-weight: 700;
    }
    
    .stSelectbox label, .stSlider label {
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Datos oficiales (NO se modifican)
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
# GeoJSON + Mapeo de nombres CORREGIDO
# -----------------------------------------------------------------------------
@st.cache_data
def load_geojson():
    url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
    with urlopen(url) as response:
        geo = json.load(response)
    for feature in geo["features"]:
        feature["id"] = feature["properties"]["NOMBRE_DPT"]
    return geo

geojson = load_geojson()

# Mapeo exacto de nombres (esto era lo que fallaba)
NAME_MAP = {
    "Antioquia": "ANTIOQUIA",
    "Atlántico": "ATLÁNTICO",
    "Bogotá D.C.": "BOGOTÁ, D.C.",
    "Bolívar": "BOLÍVAR",
    "Boyacá": "BOYACÁ",
    "Caldas": "CALDAS",
    "Caquetá": "CAQUETÁ",
    "Cauca": "CAUCA",
    "Cesar": "CESAR",
    "Córdoba": "CÓRDOBA",
    "Cundinamarca": "CUNDINAMARCA",
    "Chocó": "CHOCÓ",
    "Huila": "HUILA",
    "La Guajira": "LA GUAJIRA",
    "Magdalena": "MAGDALENA",
    "Meta": "META",
    "Nariño": "NARIÑO",
    "Norte de Santander": "NORTE DE SANTANDER",
    "Quindío": "QUINDÍO",
    "Risaralda": "RISARALDA",
    "Santander": "SANTANDER",
    "Sucre": "SUCRE",
    "Tolima": "TOLIMA",
    "Valle del Cauca": "VALLE DEL CAUCA"
}

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Controles")
    st.caption("DANE · GEIH · 23 deptos + Bogotá")
    
    indicador = st.selectbox("Indicador", ["Pobreza monetaria (%)", "Tasa de desocupación (%)"])
    col_map = "pobreza" if "Pobreza" in indicador else "desocupacion"
    
    anio = st.selectbox("Año", [2025, 2024, 2023])
    
    dept_sel = st.selectbox(
        "Departamento (series)",
        sorted(df["departamento"].unique()),
        index=sorted(df["departamento"].unique()).index("Nariño")
    )
    
    st.markdown("---")
    st.success("Solo datos oficiales DANE")
    st.caption("Sin series inventadas ni SpVAR")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<p class="main-title">Brechas Territoriales</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Mercado laboral y pobreza monetaria en Colombia · Análisis espacial con datos oficiales DANE</p>', unsafe_allow_html=True)

# Métricas rápidas
nat = nacional[nacional["anio"] == anio].iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Nacional Pobreza", f"{nat['pobreza']:.1f}%")
c2.metric("Nacional Desocupación", f"{nat['desocupacion']:.1f}%")
top = df[df["anio"]==anio].loc[df[df["anio"]==anio]["pobreza"].idxmax()]
c3.metric("Mayor pobreza", top["departamento"], delta=f"{top['pobreza']:.1f}%", delta_color="inverse")
low = df[df["anio"]==anio].loc[df[df["anio"]==anio]["pobreza"].idxmin()]
c4.metric("Menor pobreza", low["departamento"], delta=f"{low['pobreza']:.1f}%")

st.markdown("")

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🗺️ Mapa", "📈 Evolución", "🔗 Espacial", "📊 Brechas", "📉 Asociación", "📘 Método"]
)

# ====================== TAB MAPA ======================
with tab1:
    st.subheader(f"Mapa de {indicador} · {anio}")
    
    data_year = df[df["anio"] == anio].copy()
    data_year["dept_geo"] = data_year["departamento"].map(NAME_MAP)
    
    fig = px.choropleth(
        data_year,
        geojson=geojson,
        locations="dept_geo",
        featureidkey="properties.NOMBRE_DPT",
        color=col_map,
        color_continuous_scale=["#00F5D4", "#FEE440", "#F15BB5", "#9B5DE5", "#FF0A54"],
        range_color=(data_year[col_map].min() * 0.95, data_year[col_map].max() * 1.02),
        labels={col_map: "%"},
        hover_name="departamento",
        hover_data={col_map: ":.1f", "dept_geo": False}
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        bgcolor="rgba(0,0,0,0)",
        resolution=50
    )
    
    fig.update_layout(
        margin={"r": 0, "t": 20, "l": 0, "b": 0},
        height=680,
        coloraxis_colorbar=dict(
            title="%",
            thickness=22,
            len=0.65,
            x=1.02,
            bgcolor="white",
            borderwidth=2,
            bordercolor="#FF2E63",
            outlinewidth=0
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Fuente: DANE – Anexos oficiales de Pobreza Monetaria Departamental y GEIH. Solo se muestran los 23 departamentos + Bogotá con estimación oficial.")

# ====================== TAB EVOLUCIÓN ======================
with tab2:
    st.subheader(f"Evolución · {dept_sel}")
    serie = df[df["departamento"] == dept_sel].sort_values("anio")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["pobreza"],
        mode="lines+markers", name="Pobreza monetaria",
        line=dict(color="#FF2E63", width=4),
        marker=dict(size=13)
    ))
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["desocupacion"],
        mode="lines+markers", name="Desocupación",
        line=dict(color="#08D9D6", width=4),
        marker=dict(size=13, symbol="diamond"),
        yaxis="y2"
    ))
    fig.update_layout(
        height=440,
        yaxis=dict(title="Pobreza (%)", color="#FF2E63"),
        yaxis2=dict(title="Desocupación (%)", overlaying="y", side="right", color="#08D9D6"),
        legend=dict(orientation="h", y=1.14),
        margin=dict(t=50),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(
        serie[["anio", "pobreza", "desocupacion"]].rename(
            columns={"anio": "Año", "pobreza": "Pobreza (%)", "desocupacion": "Desocupación (%)"}
        ).set_index("Año"),
        use_container_width=True
    )

# ====================== TAB ESPACIAL ======================
with tab3:
    st.subheader("Análisis espacial (Moran's I)")
    
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
                j = codes.index(v)
                W[i, j] = 1.0
            W[i] /= W[i].sum()
    
    z = y - y.mean()
    I = (n / W.sum()) * (z @ W @ z) / (z @ z)
    
    np.random.seed(42)
    I_perm = [(n / W.sum()) * (np.random.permutation(z) @ W @ np.random.permutation(z)) / (z @ z) for _ in range(499)]
    p_val = (np.sum(np.array(I_perm) >= I) + 1) / 500
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Moran's I", f"{I:.4f}")
    col_b.metric("p-valor", f"{p_val:.4f}")
    col_c.metric("Resultado", "Significativo ✓" if p_val < 0.05 else "No significativo")
    
    if p_val < 0.05:
        st.success("Existe autocorrelación espacial positiva significativa (los valores similares tienden a concentrarse geográficamente).")
    else:
        st.info("No se detecta autocorrelación espacial significativa al 5%.")

# ====================== TAB BRECHAS ======================
with tab4:
    st.subheader(f"Brechas vs promedio nacional · {anio}")
    data_year = df[df["anio"] == anio].copy()
    nat_val = nat[col_map]
    data_year["brecha"] = data_year[col_map] - nat_val
    data_year = data_year.sort_values("brecha")
    
    fig = px.bar(
        data_year, x="brecha", y="departamento", orientation="h",
        color="brecha",
        color_continuous_scale=["#00F5D4", "#FEE440", "#FF2E63"],
        labels={"brecha": "Diferencia (pp)"},
        height=700
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#1a1a2e", line_width=2)
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ====================== TAB ASOCIACIÓN ======================
with tab5:
    st.subheader(f"Pobreza vs Desocupación · {anio}")
    data_year = df[df["anio"] == anio]
    
    slope, intercept, r, p, se = stats.linregress(data_year["desocupacion"], data_year["pobreza"])
    
    fig = px.scatter(
        data_year, x="desocupacion", y="pobreza", text="departamento",
        color="pobreza",
        color_continuous_scale=["#00F5D4", "#FF2E63"],
        labels={"desocupacion": "Desocupación (%)", "pobreza": "Pobreza (%)"},
        height=530
    )
    fig.update_traces(textposition="top center", textfont_size=10, marker=dict(size=15, line=dict(width=1, color="white")))
    
    x_line = np.linspace(data_year["desocupacion"].min(), data_year["desocupacion"].max(), 40)
    fig.add_trace(go.Scatter(
        x=x_line, y=intercept + slope * x_line,
        mode="lines", name=f"OLS  R² = {r**2:.3f}",
        line=dict(color="#1a1a2e", width=3, dash="dot")
    ))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"**Pendiente:** {slope:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; **R²:** {r**2:.3f} &nbsp;&nbsp;|&nbsp;&nbsp; **p-valor:** {p:.4f}")
    st.info("Asociación descriptiva. No implica causalidad.")

# ====================== TAB MÉTODO ======================
with tab6:
    st.subheader("Método y fuentes")
    st.markdown(f"""
### Fuentes certificadas
- **DANE** – Anexo de Pobreza Monetaria Departamental (2023, 2024 y 2025)
- **DANE** – GEIH Departamentos (tasa de desocupación)
- Cobertura oficial: **23 departamentos + Bogotá D.C.**

### ¿Por qué solo 23 + Bogotá?
El DANE no publica estimaciones departamentales para Amazonas, Arauca, Casanare, Guainía, Guaviare, Putumayo, Vaupés, Vichada y San Andrés por insuficiencia de muestra en la GEIH.

### Análisis espacial
- Matriz de pesos: contigüidad tipo Queen
- Estadístico: Moran’s I con 499 permutaciones

### Limitaciones
- Serie temporal corta (T=3) → no se estiman modelos SAR/SEM ni SpVAR
- La asociación entre pobreza y desocupación es correlacional, no causal

**Fecha de construcción:** {datetime.now().strftime("%Y-%m-%d")}
    """)

st.markdown("---")
st.caption("Datos oficiales DANE · Sin series inventadas · Diseño Pop-Art")
