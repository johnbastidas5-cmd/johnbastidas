
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# --------------------------
# CONFIGURACIÓN
# --------------------------
st.set_page_config(
    page_title="Pasto Economic Intelligence 🐱",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo oscuro moderno
st.markdown("""
<style>
    .stApp { background-color: #0B1020; color: #E2E8F0; }
    h1, h2, h3, h4 { color: #F8FAFC !important; }
    div[data-testid="stSidebar"] { background-color: #111827; }
    .stMetric { background: #1E293B; padding: 14px 18px; border-radius: 12px; border: 1px solid #334155; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --------------------------
# CARGA DE DATOS
# --------------------------
@st.cache_data
def cargar_datos():
    # Obtiene la ruta de la carpeta donde está guardado este archivo .py actual
    directorio_actual = Path(__file__).parent if "__file__" in locals() else Path(".")
    
    # Define las rutas posibles relativas a la ubicación del script
    posibles_rutas = [
        directorio_actual / "data",
        directorio_actual / "ENTREGABLES_PASTO" / "data",
        Path("data"),
        Path("ENTREGABLES_PASTO/data"),
    ]
    
    for ruta in posibles_rutas:
        archivo1 = ruta / "serie_completa_pasto.csv"
        archivo2 = ruta / "resumen_anual_pasto.csv"
        if archivo1.exists() and archivo2.exists():
            pasto = pd.read_csv(archivo1, parse_dates=["date"])
            anual = pd.read_csv(archivo2)
            pasto = pasto[pasto["year"] <= 2025].copy()
            anual = anual[anual["year"] <= 2025].copy()
            return pasto, anual
    
    st.error("No se encontraron los archivos CSV. Verifica que la carpeta 'data' esté en el mismo directorio que tu script con los archivos 'serie_completa_pasto.csv' y 'resumen_anual_pasto.csv'.")
    st.stop()

pasto, anual = cargar_datos()

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.title("🐱 Menú del Gato Economista")
st.sidebar.markdown("Elige tu aventura económica:")

pagina = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "📈 Inflación en Pasto",
        "💰 Poder Adquisitivo",
        "🔮 Proyecciones",
        "📚 ¿Qué significa todo esto?",
        "😹 Zona de memes",
        "ℹ️ Fuentes y metodología"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Datos actualizados: {datetime.now().strftime('%Y-%m-%d')}")
st.sidebar.info("Datos oficiales del DANE + humor para que no te duermas estudiando.")

# --------------------------
# PÁGINAS
# --------------------------

if pagina == "🏠 Inicio":
    st.title("📊 Pasto Economic Intelligence")
    st.markdown("### La app que analiza la inflación en Pasto... con estilo 🐱")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Observaciones", f"{len(pasto)}")
    with col2:
        st.metric("Periodo", "2017–2025")
    with col3:
        st.metric("Última var. mensual", f"{pasto['var_mensual'].iloc[-1]:.2f}%")
    with col4:
        st.metric("Fuente", "DANE oficial")

    st.success("¡Bienvenido! Aquí no solo hay números. También hay explicaciones claras, proyecciones y un gato que juzga tus decisiones económicas.")

    st.markdown("""
    **¿Qué puedes hacer en esta app?**
    - Ver la evolución real de la inflación en San Juan de Pasto
    - Entender el poder adquisitivo del salario mínimo (proxy)
    - Hacer proyecciones simples
    - Leer explicaciones sin lenguaje de robot
    - Reírte un poco (porque la inflación ya es suficiente drama)
    """)

    st.markdown("---")
    st.subheader("Resumen rápido del periodo")
    fig = px.line(pasto, x="date", y="var_mensual", title="Variación mensual del IPC en Pasto")
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(template="plotly_dark", height=420, margin=dict(t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)


elif pagina == "📈 Inflación en Pasto":
    st.header("📈 ¿Cómo se ha movido la inflación en Pasto?")

    st.markdown("""
    **Explicación rápida:**  
    La variación mensual del IPC nos dice cuánto subieron (o bajaron) los precios en promedio en un mes.  
    Cuando está alta, tu plata alcanza para menos cosas.
    """)

    fig1 = px.line(pasto, x="date", y="var_mensual",
                   title="Variación mensual del IPC — San Juan de Pasto (2017-2025)",
                   labels={"var_mensual": "Variación mensual (%)", "date": "Fecha"})
    fig1.add_hline(y=0, line_dash="dash", line_color="gray")
    fig1.update_layout(template="plotly_dark", height=480)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Inflación anual aproximada")
    st.caption("Calculada por compounding de las variaciones mensuales oficiales del DANE.")
    fig2 = px.bar(anual[anual["n_meses"] >= 11], x="year", y="inflacion_comp",
                  title="Inflación anual aproximada — Pasto",
                  text_auto=".1f", color_discrete_sequence=["#3B82F6"])
    fig2.update_layout(template="plotly_dark", height=430)
    st.plotly_chart(fig2, use_container_width=True)


elif pagina == "💰 Poder Adquisitivo":
    st.header("💰 ¿Cuánto alcanza realmente el salario mínimo?")

    st.warning("""
    **Importante (léelo):** Esto es un **proxy**.  
    Usamos el Salario Mínimo deflactado por el IPC de Pasto.  
    No es el ingreso real de todos los hogares. Para eso se necesitan microdatos de la GEIH.
    Existe una relación mecánica porque usamos el mismo IPC como deflactor.
    """)

    fig = px.line(pasto, x="date", y="poder_adquisitivo",
                  title="Poder adquisitivo del SMMLV (proxy) — pesos de dic-2018",
                  labels={"poder_adquisitivo": "Poder adquisitivo"})
    fig.update_layout(template="plotly_dark", height=480)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **¿Qué significa esta gráfica?**  
    - Cuando la línea **sube** → el salario mínimo alcanza para más cosas (en precios de Pasto).  
    - Cuando **baja** → la inflación se está comiendo el aumento del mínimo.
    """)


elif pagina == "🔮 Proyecciones":
    st.header("🔮 Proyecciones simples (no somos adivinos)")

    st.info("Estas son proyecciones **muy simples** basadas en el promedio reciente. No son modelos complejos ni predicciones oficiales del Banco de la República.")

    ultimos_12 = pasto.tail(12)["var_mensual"].mean()
    st.metric("Promedio de los últimos 12 meses", f"{ultimos_12:.2f}%")

    meses = st.slider("¿Cuántos meses quieres proyectar?", 3, 18, 6)

    ultima_fecha = pasto["date"].max()
    fechas_futuras = pd.date_range(start=ultima_fecha + pd.offsets.MonthBegin(1), periods=meses, freq="MS")
    proyeccion = pd.DataFrame({
        "date": fechas_futuras,
        "var_mensual": ultimos_12
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pasto["date"], y=pasto["var_mensual"], name="Histórico", line=dict(color="#3B82F6", width=2)))
    fig.add_trace(go.Scatter(x=proyeccion["date"], y=proyeccion["var_mensual"], name="Proyección simple", line=dict(color="#F59E0B", width=2, dash="dot")))
    fig.update_layout(title="Proyección ingenua de la variación mensual", template="plotly_dark", height=460)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("⚠️ Esto asume que el promedio de los últimos 12 meses se mantiene constante. La realidad suele ser más complicada.")


elif pagina == "📚 ¿Qué significa todo esto?":
    st.header("📚 Diccionario anti-aburrido")

    with st.expander("¿Qué es el IPC?"):
        st.write("Es el Índice de Precios al Consumidor. Mide cómo cambian los precios de una canasta de bienes y servicios que compran los hogares. Lo calcula el DANE cada mes.")

    with st.expander("¿Qué es el poder adquisitivo?"):
        st.write("Es la cantidad de cosas que puedes comprar con tu dinero. Si los precios suben más rápido que tu ingreso, tu poder adquisitivo cae.")

    with st.expander("¿Por qué usamos el salario mínimo como proxy?"):
        st.write("Porque es un dato oficial, público y fácil de conseguir. No representa a todos los hogares, pero sirve para ver la tendencia general. Idealmente se deberían usar microdatos de la GEIH.")

    with st.expander("¿Por qué hay una 'relación mecánica'?"):
        st.write("Porque construimos el poder adquisitivo dividiendo el salario mínimo por el IPC. Luego si comparamos ese poder adquisitivo con el mismo IPC, parte de la relación es matemática, no necesariamente causal.")

    with st.expander("¿Puedo decir que la inflación 'impactó' el poder adquisitivo?"):
        st.write("Con estos datos solo puedes hablar de **asociación** o **evolución conjunta**. No de impacto causal. Para hablar de impacto se necesita un diseño de identificación más fuerte.")


elif pagina == "😹 Zona de memes":
    st.header("😹 Zona de memes y verdades incómodas")
    st.markdown("""
    - La inflación es como ese amigo que llega a la fiesta y se come toda la pizza sin avisar.
    - El salario mínimo sube... y los precios también. Spoiler: a veces los precios corren más rápido.
    - Estudiar economía regional en Pasto es elite. La mayoría solo mira el dato nacional y ya.
    - Si esta app te sirvió, dale crédito a los autores y al DANE (ellos ponen los datos, nosotros el drama).
    - El gato economista te observa. No gastes de más este mes.
    """)
    st.balloons()


elif pagina == "ℹ️ Fuentes y metodología":
    st.header("ℹ️ Fuentes y metodología")

    st.markdown("""
    **Fuente principal de datos**  
    DANE – Anexo de variación mensual del IPC según ciudades.

    **Proxy utilizado**  
    Salario Mínimo Mensual Legal Vigente deflactado por el IPC de Pasto.

    **Periodo de análisis principal**  
    2017 – 2025

    **Limitaciones importantes**  
    - No se utilizan microdatos de ingresos de hogares (GEIH).  
    - Existe relación mecánica en el proxy de poder adquisitivo.  
    - Las proyecciones son simples y no constituyen pronósticos oficiales.  
    - No se dispone de IPC por divisiones de gasto para Pasto en esta versión.

    **Autores**  
    John Alexander Bastidas Morales · Jhonatan Stiven Melo Yela  
    Universidad de Nariño – Seminario de Investigación Regional 2
    """)

st.markdown("---")
st.caption("Hecho con datos del DANE + cafeína + un poco de humor · No somos el Banco de la República")
