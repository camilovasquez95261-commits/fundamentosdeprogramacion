import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard Cruces por Programa - Univ. Colegio Mayor de Cundinamarca",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores solicitada
PALETTE = ["#362F4F", "#5B23FF", "#008BFF", "#E4FF30"]

# 2. Estilos CSS personalizados
st.markdown(f"""
    <style>
        /* Fondo del panel lateral (Sidebar) */
        [data-testid="stSidebar"] {{
            background-color: {PALETTE[0]};
        }}
        [data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}
        /* Ajuste de color para las opciones dentro de los desplegables */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
            color: #111111 !important;
        }}
        /* Títulos principales */
        h1, h2, h3 {{
            color: {PALETTE[0]};
            font-weight: 700;
        }}
        /* Estilo de las pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: #F4F5F7;
            border-radius: 8px 8px 0px 0px;
            padding: 10px 20px;
            color: {PALETTE[0]};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {PALETTE[1]} !important;
            color: #FFFFFF !important;
        }}
        /* Tarjetas de reseña debajo de cada gráfico */
        .resena-box {{
            background-color: #F8F9FA;
            border-left: 6px solid {PALETTE[1]};
            padding: 16px 20px;
            border-radius: 6px;
            margin-top: 15px;
            color: #1E1E1E;
            font-size: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .resena-title {{
            color: {PALETTE[0]};
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
        }}
    </style>
""", unsafe_allow_html=True)

# 3. Función de carga y limpieza de datos
@st.cache_data
def cargar_datos():
    ruta = os.path.join("database", "Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv")
    
    try:
        df = pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    except Exception:
        df = pd.read_csv(ruta, sep=None, engine="python", encoding="latin-1")
    
    df.columns = df.columns.str.strip()
    
    def limpiar_numero(val):
        if pd.isna(val):
            return 0.0
        s = str(val).replace("$", "").replace(" ", "").strip()
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            s = s.replace(",", ".")
        elif s.count(".") > 1:
            s = s.replace(".", "")
        try:
            return float(s)
        except ValueError:
            return 0.0

    if "VALOR DE MATRICULA" in df.columns:
        df["MATRICULA_NUM"] = df["VALOR DE MATRICULA"].apply(limpiar_numero)
    if "Valor en SMLMV" in df.columns:
        df["SMLMV_NUM"] = df["Valor en SMLMV"].apply(limpiar_numero)
    if "NIVEL DE INGRESO MAXIMO" in df.columns:
        df["INGRESO_MAX_NUM"] = df["NIVEL DE INGRESO MAXIMO"].apply(limpiar_numero)
        
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("❌ No se encontró el archivo en `database\\Valor_de_Matricula_-_Programas_Universidad_Colegio_Mayor_de_Cundinamarca_20261126.csv`.")
    st.stop()

# 4. Panel Izquierdo: Filtros Encadenados
st.sidebar.title("🎛️ Filtros Encadenados")
st.sidebar.markdown("Selecciona en orden para filtrar dinámicamente:")

categorias = [
    "PROGRAMA",
    "NIVEL DE INGRESOS",
    "NIVEL DE INGRESO MAXIMO",
    "VALOR DE MATRICULA",
    "Valor en SMLMV"
]

faltantes = [col for col in categorias if col not in df.columns]
if faltantes:
    st.error(f"Las siguientes columnas no coinciden con el CSV: {faltantes}. Disponibles: {list(df.columns)}")
    st.stop()

df_filtrado = df.copy()

for idx, col in enumerate(categorias):
    opciones_disponibles = ["Todos"] + sorted(df_filtrado[col].dropna().astype(str).unique().tolist())
    seleccion = st.sidebar.selectbox(
        label=f"📌 {col}",
        options=opciones_disponibles,
        key=f"filtro_cascada_{idx}_{col}"
    )
    if seleccion != "Todos":
        df_filtrado = df_filtrado[df_filtrado[col].astype(str) == seleccion]

st.sidebar.markdown("---")
st.sidebar.metric("Registros seleccionados", f"{len(df_filtrado)} de {len(df)}")

# 5. Encabezado y Única Tabla Oculta por Defecto
st.title("🎓 Análisis Cruzado por Programa Académico")
st.markdown("**Universidad Colegio Mayor de Cundinamarca** — Relación de programas frente a niveles de ingreso, matrícula y SMLMV.")

with st.expander("📋 Ver Tabla de Datos Filtrados (Clic para desplegar)", expanded=False):
    columnas_mostrar = [c for c in df_filtrado.columns if not c.endswith("_NUM")]
    st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True, hide_index=True)

st.markdown("---")

def estilizar_grafico(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE[0], family="sans-serif"),
        title_font=dict(size=18, color=PALETTE[0]),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=False, linecolor="#CCCCCC")
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")
    return fig

# 6. Pestañas para los 4 Grupos de Categorías Cruzadas
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 PROGRAMA vs NIVEL DE INGRESOS",
    "📈 PROGRAMA vs INGRESO MÁXIMO",
    "💳 PROGRAMA vs VALOR DE MATRÍCULA",
    "⚖️ PROGRAMA vs VALOR EN SMLMV"
])

# --- PESTAÑA 1: PROGRAMA Y NIVEL DE INGRESOS ---
with tab1:
    st.subheader("Cruce: Programa Académico y Nivel de Ingresos")
    if not df_filtrado.empty:
        g1 = df_filtrado.groupby(["PROGRAMA", "NIVEL DE INGRESOS"], as_index=False).size()
        g1.rename(columns={"size": "Cantidad_Tarifas"}, inplace=True)
        
        fig1 = px.bar(
            g1,
            x="Cantidad_Tarifas",
            y="PROGRAMA",
            color="NIVEL DE INGRESOS",
            orientation="h",
            barmode="stack",
            text_auto=True,
            color_discrete_sequence=PALETTE,
            labels={
                "PROGRAMA": "Programa Académico",
                "Cantidad_Tarifas": "Cantidad de Rangos Tarifarios",
                "NIVEL DE INGRESOS": "Nivel de Ingresos"
            },
            title="Distribución de Niveles de Ingresos por cada Programa"
        )
        fig1.update_layout(height=max(450, len(g1["PROGRAMA"].unique()) * 28))
        st.plotly_chart(estilizar_grafico(fig1), use_container_width=True)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    st.markdown("""
        <div class="resena-box">
            <div class="resena-title">Reseña: PROGRAMA y NIVEL DE INGRESOS</div>
            Este cruce muestra cómo se segmenta cada programa académico según los distintos niveles socioeconómicos 
            del núcleo familiar. Permite verificar si todos los programas cuentan con la misma estructura de 
            clasificación de ingresos o si existen esquemas diferenciales por carrera.
        </div>
    """, unsafe_allow_html=True)

# --- PESTAÑA 2: PROGRAMA Y NIVEL DE INGRESO MAXIMO ---
with tab2:
    st.subheader("Cruce: Programa Académico y Nivel de Ingreso Máximo")
    if not df_filtrado.empty:
        g2 = df_filtrado.groupby(["PROGRAMA", "NIVEL DE INGRESO MAXIMO"], as_index=False).agg(
            Ingreso_Max_Num=("INGRESO_MAX_NUM", "max")
        )
        
        fig2 = px.scatter(
            g2,
            x="Ingreso_Max_Num",
            y="PROGRAMA",
            color="NIVEL DE INGRESO MAXIMO",
            size="Ingreso_Max_Num",
            color_discrete_sequence=PALETTE,
            labels={
                "PROGRAMA": "Programa Académico",
                "Ingreso_Max_Num": "Tope de Ingreso Máximo ($)",
                "NIVEL DE INGRESO MAXIMO": "Categoría Tope"
            },
            title="Umbrales de Ingreso Máximo Aplicados por Programa"
        )
        fig2.update_layout(height=max(450, len(g2["PROGRAMA"].unique()) * 28))
        st.plotly_chart(estilizar_grafico(fig2), use_container_width=True)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    st.markdown("""
        <div class="resena-box">
            <div class="resena-title">Reseña: PROGRAMA y NIVEL DE INGRESO MAXIMO</div>
            Compara los techos o topes máximos de ingresos establecidos dentro de cada programa académico. 
            Permite visualizar el alcance económico superior de cada rango tarifario y detectar variaciones 
            en los límites de capacidad de pago exigidos según la carrera.
        </div>
    """, unsafe_allow_html=True)

# --- PESTAÑA 3: PROGRAMA Y VALOR DE MATRICULA ---
with tab3:
    st.subheader("Cruce: Programa Académico y Valor de Matrícula")
    if not df_filtrado.empty:
        g3 = df_filtrado.groupby("PROGRAMA", as_index=False).agg(
            Minimo=("MATRICULA_NUM", "min"),
            Promedio=("MATRICULA_NUM", "mean"),
            Maximo=("MATRICULA_NUM", "max")
        ).sort_values(by="Promedio", ascending=True)
        
        g3_melt = g3.melt(
            id_vars="PROGRAMA",
            value_vars=["Minimo", "Promedio", "Maximo"],
            var_name="Metrica",
            value_name="Valor_COP"
        )
        
        fig3 = px.bar(
            g3_melt,
            x="Valor_COP",
            y="PROGRAMA",
            color="Metrica",
            barmode="group",
            orientation="h",
            color_discrete_map={
                "Minimo": PALETTE[2],
                "Promedio": PALETTE[1],
                "Maximo": PALETTE[0]
            },
            labels={
                "PROGRAMA": "Programa Académico",
                "Valor_COP": "Valor de Matrícula ($ COP)",
                "Metrica": "Indicador"
            },
            title="Comparativa de Matrícula Mínima, Promedio y Máxima por Programa"
        )
        fig3.update_layout(height=max(500, len(g3["PROGRAMA"].unique()) * 32))
        st.plotly_chart(estilizar_grafico(fig3), use_container_width=True)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    st.markdown("""
        <div class="resena-box">
            <div class="resena-title">Reseña: PROGRAMA y VALOR DE MATRÍCULA</div>
            Analiza la amplitud tarifaria en pesos colombianos dentro de cada programa, contrastando el valor mínimo, 
            el promedio y el techo máximo de liquidación. Facilita identificar qué carreras tienen mayor dispersión 
            de costos entre sus estudiantes.
        </div>
    """, unsafe_allow_html=True)

# --- PESTAÑA 4: PROGRAMA Y VALOR EN SMLMV ---
with tab4:
    st.subheader("Cruce: Programa Académico y Valor en SMLMV")
    if not df_filtrado.empty:
        fig4 = px.box(
            df_filtrado,
            x="SMLMV_NUM",
            y="PROGRAMA",
            color="NIVEL DE INGRESOS",
            points="all",
            color_discrete_sequence=PALETTE,
            labels={
                "PROGRAMA": "Programa Académico",
                "SMLMV_NUM": "Valor en SMLMV",
                "NIVEL DE INGRESOS": "Nivel de Ingresos"
            },
            title="Distribución y Dispersión en SMLMV por Programa Académico"
        )
        fig4.update_layout(height=max(500, len(df_filtrado["PROGRAMA"].unique()) * 32))
        st.plotly_chart(estilizar_grafico(fig4), use_container_width=True)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    st.markdown("""
        <div class="resena-box">
            <div class="resena-title">Reseña: PROGRAMA y VALOR EN SMLMV</div>
            Evalúa el peso relativo de cada programa académico medido en Salarios Mínimos Legales Mensuales Vigentes. 
            Permite observar la concentración, mediana y dispersión de tarifas estandarizadas, mostrando cuántos 
            salarios mínimos representa estudiar cada carrera según el nivel socioeconómico.
        </div>
    """, unsafe_allow_html=True)