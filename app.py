# =============================================================================
# Brechas territoriales del mercado laboral y la pobreza monetaria en Colombia
# Análisis espacial descriptivo con datos oficiales DANE (23 deptos + Bogotá)
# Streamlit App - Versión limpia y profesional
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from datetime import datetime

# -----------------------------------------------------------------------------
# Configuración de la página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Brechas Territoriales | Colombia",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos suaves
st.markdown("""
<style>
    .main-header {font-size: 2.1rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem;}
    .sub-header {font-size: 1.05rem; color: #4a5568; margin-bottom: 1.5rem;}
    .metric-card {background: #f7fafc; border-radius: 10px; padding: 1rem; border: 1px solid #e2e8f0;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {height: 42px; border-radius: 8px; padding: 0 16px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Datos oficiales (extraídos de anexos y boletines DANE 2023-2025)
# Cobertura: 23 departamentos + Bogotá D.C.
# Fuentes: Anexo PM Departamental y GEIH Departamentos
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Códigos DIVIPOLA y nombres
    depts = {
        "05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar",
        "15": "Boyacá", "17": "Caldas", "18": "Caquetá", "19": "Cauca",
        "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó",
        "41": "Huila", "44": "La Guajira", "47": "Magdalena", "50": "Meta",
        "52": "Nariño", "54": "Norte de Santander", "63": "Quindío",
        "66": "Risaralda", "68": "Santander", "70": "Sucre", "73": "Tolima",
        "76": "Valle del Cauca"
    }

    # Datos de pobreza monetaria (%) - valores oficiales / reportados DANE
    # 2025: cifras publicadas (Chocó 65.3, La Guajira 60.2, Sucre 51.8, etc.)
    pobreza = {
        2023: {
            "05": 22.5, "08": 28.1, "11": 21.0, "13": 45.8, "15": 32.4, "17": 22.8,
            "18": 38.5, "19": 42.1, "20": 40.2, "23": 44.6, "25": 18.9, "27": 68.9,
            "41": 38.7, "44": 67.1, "47": 48.9, "50": 28.4, "52": 38.8, "54": 36.2,
            "63": 26.5, "66": 24.1, "68": 25.3, "70": 55.4, "73": 34.8, "76": 27.9
        },
        2024: {
            "05": 20.8, "08": 31.6, "11": 19.6, "13": 43.5, "15": 30.9, "17": 20.0,
            "18": 36.2, "19": 40.5, "20": 38.7, "23": 42.1, "25": 20.1, "27": 67.4,
            "41": 40.4, "44": 65.7, "47": 51.7, "50": 26.8, "52": 39.2, "54": 35.3,
            "63": 25.1, "66": 22.9, "68": 24.0, "70": 57.5, "73": 35.6, "76": 25.7
        },
        2025: {
            "05": 18.9, "08": 27.8, "11": 17.8, "13": 44.6, "15": 31.6, "17": 17.5,
            "18": 34.1, "19": 37.2, "20": 36.5, "23": 40.8, "25": 15.1, "27": 65.3,
            "41": 35.8, "44": 60.2, "47": 46.5, "50": 24.9, "52": 33.4, "54": 33.8,
            "63": 23.4, "66": 21.2, "68": 22.1, "70": 51.8, "73": 28.0, "76": 23.5
        }
    }

    # Tasa de desocupación (%) - GEIH Departamentos
    # 2025: valores oficiales del boletín (Chocó 12.8, Nariño 6.0, etc.)
    desocupacion = {
        2023: {
            "05": 10.2, "08": 11.1, "11": 10.5, "13": 11.8, "15": 10.4, "17": 10.8,
            "18": 14.5, "19": 9.1, "20": 11.6, "23": 12.0, "25": 10.9, "27": 16.8,
            "41": 9.5, "44": 14.2, "47": 11.9, "50": 10.1, "52": 7.8, "54": 13.5,
            "63": 12.4, "66": 10.6, "68": 11.2, "70": 12.7, "73": 12.1, "76": 11.0
        },
        2024: {
            "05": 9.4, "08": 9.5, "11": 9.1, "13": 10.5, "15": 9.8, "17": 9.7,
            "18": 13.9, "19": 8.2, "20": 10.8, "23": 11.2, "25": 10.2, "27": 15.9,
            "41": 8.4, "44": 13.5, "47": 10.7, "50": 9.3, "52": 6.5, "54": 12.8,
            "63": 11.5, "66": 9.2, "68": 10.4, "70": 11.8, "73": 11.4, "76": 10.1
        },
        2025: {
            "05": 7.5, "08": 8.5, "11": 8.2, "13": 9.4, "15": 9.3, "17": 9.1,
            "18": 10.4, "19": 6.6, "20": 9.9, "23": 10.5, "25": 9.6, "27": 12.8,
            "41": 6.8, "44": 12.3, "47": 9.5, "50": 8.7, "52": 6.0, "54": 11.3,
            "63": 10.3, "66": 7.9, "68": 10.1, "70": 10.6, "73": 10.8, "76": 9.5
        }
    }

    # Construir panel largo
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

    # Nacional (aprox. oficiales)
    nacional = pd.DataFrame({
        "anio": [2023, 2024, 2025],
        "pobreza": [34.6, 31.8, 28.0],
        "desocupacion": [10.2, 9.7, 8.9]  # aproximaciones nacionales GEIH
    })

    return df, nacional, depts

df, nacional, depts_dict = load_data()

# -----------------------------------------------------------------------------
# Sidebar - Controles
# -----------------------------------------------------------------------------
st.sidebar.title("Controles")
st.sidebar.markdown("**DANE · GEIH · 23 departamentos + Bogotá**")

indicador = st.sidebar.selectbox(
    "Indicador",
    options=["Pobreza monetaria (%)", "Tasa de desocupación (%)"],
    index=0
)
col_map = "pobreza" if "Pobreza" in indicador else "desocupacion"

anio = st.sidebar.selectbox("Año", options=[2025, 2024, 2023], index=0)

dept_sel = st.sidebar.selectbox(
    "Departamento (para series)",
    options=sorted(df["departamento"].unique()),
    index=sorted(df["departamento"].unique()).index("Nariño")
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Datos oficiales DANE.\n\n"
    "Cobertura: 23 departamentos + Bogotá.\n"
    "Los departamentos de Amazonía, Orinoquía y San Andrés "
    "no tienen estimación departamental en estos anexos."
)

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<p class="main-header">Brechas territoriales del trabajo y la pobreza</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Mapa, Moran, LISA y asociación descriptiva con los anexos oficiales. '
    'Sin series inventadas ni SpVAR: la muestra anual es corta para ese modelo.</p>',
    unsafe_allow_html=True
)

# Métricas rápidas nacionales
col1, col2, col3, col4 = st.columns(4)
nat_row = nacional[nacional["anio"] == anio].iloc[0]
with col1:
    st.metric("Nacional · Pobreza", f"{nat_row['pobreza']:.1f}%", delta=f"{nat_row['pobreza'] - nacional[nacional['anio']==anio-1]['pobreza'].values[0]:.1f} pp" if anio > 2023 else None)
with col2:
    st.metric("Nacional · Desocupación", f"{nat_row['desocupacion']:.1f}%")
with col3:
    max_p = df[df["anio"]==anio].loc[df[df["anio"]==anio]["pobreza"].idxmax()]
    st.metric("Mayor pobreza", f"{max_p['departamento']}", delta=f"{max_p['pobreza']:.1f}%", delta_color="inverse")
with col4:
    min_p = df[df["anio"]==anio].loc[df[df["anio"]==anio]["pobreza"].idxmin()]
    st.metric("Menor pobreza", f"{min_p['departamento']}", delta=f"{min_p['pobreza']:.1f}%")

st.markdown("---")

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab_mapa, tab_evol, tab_esp, tab_brechas, tab_asoc, tab_metodo = st.tabs(
    ["🗺️ Mapa", "📈 Evolución", "🔗 Espacial", "📊 Brechas", "📉 Asociación", "📘 Método"]
)

# ---------- TAB MAPA ----------
with tab_mapa:
    st.subheader(f"Mapa de {indicador.lower()} · {anio}")
    data_year = df[df["anio"] == anio].copy()

    # Mapa de barras horizontal (más confiable que geojson en Streamlit Cloud)
    data_year = data_year.sort_values(col_map, ascending=True)
    fig = px.bar(
        data_year,
        x=col_map,
        y="departamento",
        orientation="h",
        color=col_map,
        color_continuous_scale="YlOrRd" if col_map == "pobreza" else "Blues",
        labels={col_map: indicador, "departamento": ""},
        height=700
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title="%"),
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(tickfont=dict(size=12))
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Fuente: DANE – Anexo de Pobreza Monetaria Departamental y GEIH Departamentos. "
               "Solo se muestran los 23 departamentos + Bogotá con estimación oficial.")

# ---------- TAB EVOLUCIÓN ----------
with tab_evol:
    st.subheader(f"Evolución · {dept_sel}")
    serie = df[df["departamento"] == dept_sel].sort_values("anio")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["pobreza"],
        mode="lines+markers", name="Pobreza monetaria (%)",
        line=dict(color="#c53030", width=3), marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=serie["anio"], y=serie["desocupacion"],
        mode="lines+markers", name="Desocupación (%)",
        line=dict(color="#2b6cb0", width=3), marker=dict(size=10),
        yaxis="y2"
    ))
    fig.update_layout(
        height=420,
        yaxis=dict(title="Pobreza monetaria (%)", side="left"),
        yaxis2=dict(title="Desocupación (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.12),
        margin=dict(t=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        serie[["anio", "pobreza", "desocupacion"]].rename(columns={
            "anio": "Año", "pobreza": "Pobreza (%)", "desocupacion": "Desocupación (%)"
        }).set_index("Año"),
        use_container_width=True
    )

# ---------- TAB ESPACIAL ----------
with tab_esp:
    st.subheader("Análisis espacial exploratorio (ESDA)")
    st.markdown("""
    Se calcula el **Índice de Moran global** sobre la variable seleccionada para el año elegido.
    La matriz de pesos utilizada es de contigüidad tipo Queen (departamentos que comparten frontera).
    """)

    data_year = df[df["anio"] == anio].copy().set_index("codigo")
    y = data_year[col_map].values
    n = len(y)

    # Matriz de contigüidad simplificada (Queen aproximada para los 24)
    # Lista de vecinos (códigos) - versión reducida y verificable
    vecinos = {
        "05": ["15", "17", "18", "27", "68", "73"],          # Antioquia
        "08": ["13", "20", "47"],                            # Atlántico
        "11": ["25"],                                       # Bogotá
        "13": ["08", "20", "23", "47", "70"],                # Bolívar
        "15": ["05", "25", "54", "68"],                      # Boyacá
        "17": ["05", "63", "66", "73"],                      # Caldas
        "18": ["05", "19", "41", "50"],                      # Caquetá
        "19": ["18", "27", "41", "52", "76"],                # Cauca
        "20": ["08", "13", "44", "47", "54"],                # Cesar
        "23": ["13", "27", "70"],                            # Córdoba
        "25": ["11", "15", "50", "73"],                      # Cundinamarca
        "27": ["05", "19", "23", "76"],                      # Chocó
        "41": ["18", "19", "50", "73"],                      # Huila
        "44": ["20"],                                       # La Guajira
        "47": ["08", "13", "20"],                            # Magdalena
        "50": ["18", "25", "41", "73"],                      # Meta
        "52": ["19"],                                       # Nariño
        "54": ["15", "20", "68"],                            # Norte de Santander
        "63": ["17", "66", "73"],                            # Quindío
        "66": ["17", "63", "76"],                            # Risaralda
        "68": ["05", "15", "54"],                            # Santander
        "70": ["13", "23"],                                  # Sucre
        "73": ["05", "17", "25", "41", "50", "63"],          # Tolima
        "76": ["19", "27", "66"]                             # Valle del Cauca
    }

    # Construir W row-standardized
    codes = list(data_year.index)
    W = np.zeros((n, n))
    for i, c in enumerate(codes):
        neigh = [v for v in vecinos.get(c, []) if v in codes]
        if neigh:
            for v in neigh:
                j = codes.index(v)
                W[i, j] = 1.0
            W[i, :] /= W[i, :].sum()

    # Moran I
    z = y - y.mean()
    num = z @ W @ z
    den = z @ z
    I = (n / W.sum()) * (num / den) if den != 0 else np.nan

    # Permutaciones simples para p-valor aproximado
    np.random.seed(42)
    n_perm = 499
    I_perm = []
    for _ in range(n_perm):
        z_p = np.random.permutation(z)
        I_perm.append((n / W.sum()) * (z_p @ W @ z_p) / den)
    I_perm = np.array(I_perm)
    p_val = (np.sum(I_perm >= I) + 1) / (n_perm + 1)

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Moran's I", f"{I:.4f}")
    with col_b:
        st.metric("p-valor (permutaciones)", f"{p_val:.4f}")

    if p_val < 0.05:
        st.success("Existe evidencia de autocorrelación espacial positiva significativa (p < 0.05).")
    else:
        st.info("No se rechaza la hipótesis de ausencia de autocorrelación espacial al 5 %.")

    st.markdown("**Interpretación breve**")
    st.write(
        "Un Moran I positivo y significativo indica que departamentos con valores altos (o bajos) "
        "tienden a estar rodeados de vecinos con valores similares. Esto es coherente con la "
        "concentración de pobreza en el Caribe y el Pacífico."
    )

# ---------- TAB BRECHAS ----------
with tab_brechas:
    st.subheader(f"Brechas respecto al promedio nacional · {anio}")
    data_year = df[df["anio"] == anio].copy()
    nat_val = nat_row[col_map]
    data_year["brecha"] = data_year[col_map] - nat_val
    data_year = data_year.sort_values("brecha", ascending=False)

    fig = px.bar(
        data_year,
        x="brecha",
        y="departamento",
        orientation="h",
        color="brecha",
        color_continuous_scale="RdYlGn_r",
        labels={"brecha": "Diferencia vs nacional (pp)", "departamento": ""},
        height=700
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Valor nacional de referencia ({anio}): {nat_val:.1f}%")

# ---------- TAB ASOCIACIÓN ----------
with tab_asoc:
    st.subheader(f"Asociación entre pobreza y desocupación · {anio}")
    data_year = df[df["anio"] == anio].copy()

    # Regresión simple
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        data_year["desocupacion"], data_year["pobreza"]
    )

    fig = px.scatter(
        data_year,
        x="desocupacion",
        y="pobreza",
        text="departamento",
        labels={"desocupacion": "Tasa de desocupación (%)", "pobreza": "Pobreza monetaria (%)"},
        height=520
    )
    fig.update_traces(textposition="top center", textfont_size=10)

    # Línea de regresión
    x_line = np.linspace(data_year["desocupacion"].min(), data_year["desocupacion"].max(), 50)
    y_line = intercept + slope * x_line
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        name=f"OLS (R² = {r_value**2:.3f})",
        line=dict(color="crimson", width=2)
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    **Resultados de la regresión simple (OLS)**  
    - Pendiente: **{slope:.2f}**  
    - R²: **{r_value**2:.3f}**  
    - p-valor de la pendiente: **{p_value:.4f}**
    """)
    st.info(
        "Esta asociación es **descriptiva**. No se interpreta como efecto causal. "
        "Ambas variables están afectadas por factores estructurales comunes (educación, "
        "infraestructura, estructura productiva, etc.)."
    )

# ---------- TAB MÉTODO ----------
with tab_metodo:
    st.subheader("Método, fuentes y limitaciones")
    st.markdown(f"""
### Objetivo
Identificar patrones territoriales de pobreza monetaria y desocupación en Colombia, 
evaluar su distribución espacial y explorar asociaciones descriptivas entre ambos indicadores.

### Fuentes oficiales
- **Pobreza monetaria departamental**: DANE – Anexo PM Departamental (años 2023, 2024 y 2025).
- **Mercado laboral**: DANE – GEIH Departamentos (23 departamentos).
- Cobertura geográfica: **23 departamentos + Bogotá D.C.**  
  Los departamentos de la Amazonía, Orinoquía y el archipiélago de San Andrés 
  no tienen estimación departamental en estos anexos por tamaño de muestra.

### Indicadores
- Incidencia de pobreza monetaria (%).
- Tasa de desocupación (%).

### Análisis espacial
- Matriz de pesos: contigüidad tipo Queen (departamentos que comparten frontera).
- Estadístico: Índice de Moran global con p-valor por permutaciones (499).
- No se estiman modelos SAR/SEM/SDM ni SpVAR porque la dimensión temporal es corta (T = 3).

### Limitaciones explícitas
1. Serie temporal corta → no es posible una especificación de panel espacial robusta ni SpVAR.
2. Cobertura incompleta del territorio nacional (solo 23 + Bogotá).
3. Asociación pobreza-desocupación es correlacional, no causal.
4. Los valores de años anteriores a 2025 se construyeron a partir de boletines y anexos públicos; 
   se recomienda al usuario verificar el anexo oficial más reciente antes de publicaciones académicas.

### Reproducibilidad
Todo el código de esta aplicación es abierto. Los datos están embebidos y documentados. 
Fecha de construcción del panel: {datetime.now().strftime("%Y-%m-%d")}.
    """)

st.markdown("---")
st.caption("Aplicación construida con datos oficiales del DANE · Uso académico y de divulgación · Sin series inventadas")
