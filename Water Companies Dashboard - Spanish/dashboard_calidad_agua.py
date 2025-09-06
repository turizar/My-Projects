# =============================
# Dashboard Calidad Agua Chile: Limpieza + Visualización + Clustering + Predicción
# =============================
# 
# Este dashboard analiza la calidad del agua potable en Chile entre 2012-2017
# y utiliza técnicas de machine learning para agrupar empresas y predecir rankings futuros.
#
# AUTOR: [Tu nombre]
# FECHA: [Fecha de creación]
# DESCRIPCIÓN: Análisis completo de calidad de agua potable con visualizaciones interactivas

# Importamos las librerías necesarias para el análisis
import pandas as pd          # Para manipulación y análisis de datos
import numpy as np           # Para operaciones matemáticas
import plotly.express as px  # Para gráficos interactivos
import matplotlib.pyplot as plt  # Para gráficos estáticos
import seaborn as sns        # Para gráficos estadísticos
from sklearn.cluster import KMeans  # Para agrupar empresas similares
from sklearn.preprocessing import StandardScaler  # Para normalizar datos
from sklearn.linear_model import LinearRegression  # Para predicciones
import streamlit as st       # Para crear la interfaz web

# -----------------------------
# Configuración de Streamlit - Interfaz del Dashboard
# -----------------------------
st.set_page_config(layout="wide")  # Usar todo el ancho de la pantalla

# CSS personalizado para mejorar la apariencia visual
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        border-left: 4px solid #3498db;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💧 Dashboard: Calidad del Agua Potable en Chile (2012-2017)</h1>', unsafe_allow_html=True)

# -----------------------------
# PASO 1: Cargar y limpiar los datos
# -----------------------------
# En este paso cargamos el archivo Excel y limpiamos los datos para que sean útiles

# Cargar el archivo Excel con los datos de calidad de agua
file_path = "cuadro-45-ranking-de-calidad-del-agua-potable.xlsx"
df_raw = pd.read_excel(file_path, sheet_name='Ranking Calidad AP', skiprows=4)

# Limpiar columnas vacías (que no tienen datos)
df_raw.dropna(axis=1, how='all', inplace=True)

# Renombrar las columnas para que sean más fáciles de usar
df_raw.columns = ['Ranking Actual', 'Empresa', '2012', '2013', '2014', '2015', '2016', '2017']

# Eliminar filas que están completamente vacías
df_raw.dropna(how='all', inplace=True)

# Convertir los rankings de texto a números para poder hacer cálculos
# 'coerce' significa que si no puede convertir un valor, lo convierte en NaN
for year in ['2012', '2013', '2014', '2015', '2016', '2017']:
    df_raw[year] = pd.to_numeric(df_raw[year], errors='coerce')

# Calcular el ranking promedio de cada empresa durante los 6 años
# Esto nos da una idea general de qué tan bien le fue a cada empresa
df_raw['Ranking Promedio'] = df_raw[['2012', '2013', '2014', '2015', '2016', '2017']].mean(axis=1)

# Función para limpiar datos de empresas (eliminar filas que no son empresas reales)
def limpiar_empresas(df):
    """Elimina filas que contienen texto informativo en lugar de nombres de empresas"""
    df_limpio = df.copy()
    df_limpio = df_limpio[df_limpio["Empresa"] != "Sector"]
    df_limpio = df_limpio[~df_limpio["Empresa"].str.contains("Nota:", na=False)]  # Captura "Nota" sin dos puntos
    df_limpio = df_limpio[~df_limpio["Empresa"].str.contains("no se calcula indicador", na=False)]
    df_limpio = df_limpio[~df_limpio["Empresa"].str.contains("En este año", na=False)]
    df_limpio = df_limpio[~df_limpio["Empresa"].str.contains("En el año 2015, no se calcula el indicador", na=False)]
    df_limpio = df_limpio[~df_limpio["Empresa"].str.contains("aluviones que afectaron la región de Atacama", na=False)]
    

    
    return df_limpio

# Aplicar limpieza a los datos
df_clean = limpiar_empresas(df_raw)

# Ordenar las empresas por su ranking promedio (de mejor a peor)
df_sorted = df_clean.sort_values(by='Ranking Promedio')

# Mostrar los datos limpios en la interfaz
st.markdown('<h2 class="section-header">📊 Datos Limpios</h2>', unsafe_allow_html=True)
st.dataframe(df_sorted[['Empresa', 'Ranking Promedio'] + [str(y) for y in range(2012, 2018)]])

# -----------------------------
# PASO 2: Visualización - Top 5 Empresas
# -----------------------------
# Creamos gráficos para mostrar las mejores empresas

# Seleccionar las 5 empresas con mejor ranking promedio
top5 = df_sorted.head(5)

# Crear un gráfico de barras con las mejores empresas
fig_top = px.bar(top5, x="Empresa", y="Ranking Promedio",
                 title="Top 5 Empresas con Mejor Ranking Promedio (2012-2017)",
                 color="Empresa", text="Ranking Promedio")
fig_top.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig_top.update_layout(
    xaxis_title="Empresa", 
    yaxis_title="Ranking Promedio", 
    showlegend=False,
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_top)

# -----------------------------
# PASO 3: Visualización - Evolución temporal
# -----------------------------
# Mostramos cómo ha cambiado el ranking de las empresas a lo largo del tiempo

# Convertir los datos de formato ancho a largo para poder graficar la evolución
# Esto significa que cada fila tendrá: Empresa, Año, Ranking
df_melted = df_clean.melt(id_vars=["Empresa"], value_vars=[str(y) for y in range(2012, 2018)],
                        var_name="Año", value_name="Ranking")
df_melted["Año"] = df_melted["Año"].astype(str)

# Crear gráfico de líneas para mostrar la evolución de las top 5 empresas
fig_line = px.line(df_melted[df_melted['Empresa'].isin(top5['Empresa'])],
                   x="Año", y="Ranking", color="Empresa",
                   title="Evolución del Ranking de Calidad de Agua - Top 5 Empresas",
                   markers=True)
fig_line.update_layout(
    yaxis=dict(autorange="reversed"), 
    width=1200,
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)  # Invertir eje Y para que ranking 1 esté arriba
st.plotly_chart(fig_line)

# -----------------------------
# PASO 4: Mapa de Calor - Vista general
# -----------------------------
# Un mapa de calor nos permite ver todos los rankings de todas las empresas de un vistazo

st.markdown('<h2 class="section-header">📊 Mapa de Calor: Ranking por Año</h2>', unsafe_allow_html=True)

# Preparar datos para el mapa de calor (usar datos ya limpios)
heatmap_data = df_clean.set_index("Empresa")[[str(y) for y in range(2012, 2018)]]

# Crear el mapa de calor con Plotly para consistencia
fig_heatmap = px.imshow(
    heatmap_data,
    title="Ranking de Calidad de Agua por Empresa (2012-2017)",
    color_continuous_scale="YlGnBu",
    aspect="auto"
)
fig_heatmap.update_layout(
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5,
    width=1200
)
st.plotly_chart(fig_heatmap)

# -----------------------------
# PASO 5: Clustering con KMeans - Agrupamiento inteligente
# -----------------------------
# 
# ¿QUÉ ES CLUSTERING?
# El clustering es como organizar una fiesta donde agrupas a las personas por similitud.
# En nuestro caso, agrupamos empresas que tienen comportamientos similares en sus rankings.
#
# ¿CÓMO FUNCIONA KMEANS?
# 1. Elige 3 puntos aleatorios (centros iniciales)
# 2. Asigna cada empresa al centro más cercano
# 3. Mueve los centros al promedio de las empresas asignadas
# 4. Repite hasta que los grupos no cambien
# 5. Resultado: 3 grupos de empresas con comportamientos similares

st.markdown('<h2 class="section-header">🧩 Agrupamiento de Empresas (KMeans)</h2>', unsafe_allow_html=True)

# Usar datos ya limpios para el clustering
df_clustering = df_clean.copy()

# Preparar datos para el clustering
# Usamos los rankings de los 6 años como características para agrupar
X = df_clustering[[str(y) for y in range(2012, 2018)]].copy()
X = X.fillna(X.mean())  # Llenar valores faltantes con el promedio

# ESCALADO DE DATOS - ¿Por qué es importante?
# Imagina que tienes dos medidas: peso (en kg) y altura (en cm)
# El peso puede variar de 50-100 kg, pero la altura de 150-200 cm
# Sin escalar, la altura "dominaría" el análisis porque sus números son más grandes
# El escalado hace que todas las características tengan la misma importancia
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Aplicar KMeans para crear 3 grupos
kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
clusters = kmeans.fit_predict(X_scaled)
df_clustering["Cluster"] = clusters

# Asignar nombres descriptivos a cada grupo
cluster_labels = {
    0: "Desempeño Bajo",
    1: "Desempeño Medio", 
    2: "Desempeño Alto"
}
df_clustering["Cluster Label"] = df_clustering["Cluster"].map(cluster_labels)

# Visualizar los grupos en un gráfico de dispersión con colores personalizados
fig_cluster = px.scatter(
    df_clustering, x="2016", y="2017",
    color="Cluster Label",
    title="Clustering por Ranking 2016 vs 2017",
    hover_data=["Empresa"],
    labels={"Cluster Label": "Grupo"},
    color_discrete_map={
        "Desempeño Bajo": "#FF6B6B",    # Rojo
        "Desempeño Medio": "#FFA500",   # Naranja  
        "Desempeño Alto": "#1E90FF"     # Azul (Dodger Blue)
    }
)
fig_cluster.update_layout(
    yaxis=dict(autorange="reversed"), 
    xaxis=dict(autorange="reversed"),
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_cluster)

# Explicación del clustering para el usuario
st.markdown("""
### ¿Qué significa este gráfico?

Este gráfico agrupa **empresas sanitarias** según su desempeño en los rankings de calidad de agua en **2016 y 2017**:

- 🔴 **Desempeño Bajo** (rojo): Ranking más bajo (peor posición).
- 🟠 **Desempeño Medio** (naranja): Calidad intermedia.
- 🔵 **Desempeño Alto** (azul): Mejores rankings (más cercanos a 1).

Esta agrupación permite visualizar qué empresas mantienen patrones de calidad consistentes o no.
""")

# -----------------------------
# PASO 6: Análisis de Estabilidad y Volatilidad
# -----------------------------
# 
# ¿QUÉ ES LA ESTABILIDAD?
# La estabilidad mide qué tan consistentes son los rankings de una empresa.
# Una empresa estable mantiene rankings similares año tras año.
# Una empresa volátil tiene rankings que varían mucho.
#
# ¿CÓMO SE CALCULA?
# Usamos la desviación estándar: cuanto más alta, más volátil es la empresa.

st.markdown('<h2 class="section-header">🎯 Análisis de Estabilidad y Volatilidad</h2>', unsafe_allow_html=True)

# Calcular desviación estándar de rankings para cada empresa (usar datos ya limpios)
df_stability = df_clean.copy()

# Calcular desviación estándar de rankings
df_stability['Desviación Estándar'] = df_stability[[str(y) for y in range(2012, 2018)]].std(axis=1)
df_stability['Estabilidad'] = 1 / (1 + df_stability['Desviación Estándar'])  # Invertir para que mayor = más estable

# Ordenar por estabilidad
df_stability_sorted = df_stability.sort_values('Estabilidad', ascending=False)

# Gráfico de las 10 empresas más estables
fig_stability = px.bar(
    df_stability_sorted.head(10),
    x="Empresa", y="Estabilidad",
    title="Top 10 Empresas Más Estables (Rankings Consistentes)",
    color="Estabilidad",
    color_continuous_scale="Greens"
)
fig_stability.update_layout(
    xaxis_title="Empresa", 
    yaxis_title="Índice de Estabilidad",
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_stability)

# Gráfico de las 10 empresas más volátiles
fig_volatility = px.bar(
    df_stability_sorted.tail(10),
    x="Empresa", y="Desviación Estándar",
    title="Top 10 Empresas Más Volátiles (Rankings Variables)",
    color="Desviación Estándar",
    color_continuous_scale="Reds"
)
fig_volatility.update_layout(
    xaxis_title="Empresa", 
    yaxis_title="Desviación Estándar",
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_volatility)

# -----------------------------
# PASO 7: Análisis de Mejoras y Deterioros
# -----------------------------
#
# ¿QUÉ MIDE ESTE ANÁLISIS?
# Compara el ranking inicial (2012) con el final (2017) para ver qué empresas
# mejoraron o empeoraron su posición en el ranking.
#
# ¿CÓMO SE INTERPRETA?
# Valor positivo = mejoró (ranking más bajo = mejor posición)
# Valor negativo = empeoró (ranking más alto = peor posición)

st.markdown('<h2 class="section-header">🔄 Análisis de Mejoras y Deterioros (2012 vs 2017)</h2>', unsafe_allow_html=True)

# Calcular cambio de ranking
df_improvement = df_stability.copy()
df_improvement['Cambio Ranking'] = df_improvement['2012'] - df_improvement['2017']
df_improvement['Tipo Cambio'] = df_improvement['Cambio Ranking'].apply(
    lambda x: 'Mejoró' if x > 0 else 'Empeoró' if x < 0 else 'Sin Cambio'
)

# Ordenar por mejora
df_improvement_sorted = df_improvement.sort_values('Cambio Ranking', ascending=False)

# Gráfico de las 10 empresas que más mejoraron
fig_improvement = px.bar(
    df_improvement_sorted.head(10),
    x="Empresa", y="Cambio Ranking",
    title="Top 10 Empresas que Más Mejoraron (2012 → 2017)",
    color="Cambio Ranking",
    color_continuous_scale="Greens"
)
fig_improvement.update_layout(
    xaxis_title="Empresa", 
    yaxis_title="Mejora en Ranking",
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_improvement)

# Gráfico de las 10 empresas que más empeoraron
fig_deterioration = px.bar(
    df_improvement_sorted.tail(10),
    x="Empresa", y="Cambio Ranking",
    title="Top 10 Empresas que Más Empeoraron (2012 → 2017)",
    color="Cambio Ranking",
    color_continuous_scale="Reds"
)
fig_deterioration.update_layout(
    xaxis_title="Empresa", 
    yaxis_title="Deterioro en Ranking",
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_deterioration)

# -----------------------------
# PASO 9: Predicción con Regresión Lineal - Mirando al futuro
# -----------------------------
#
# ¿QUÉ ES LA REGRESIÓN LINEAL?
# Es como dibujar una línea recta que mejor se ajuste a los puntos de datos.
# Si tienes datos de los últimos 6 años, puedes "extender" esa línea para predecir el año 7.
#
# ¿CÓMO FUNCIONA?
# 1. Toma los rankings de una empresa durante 2012-2017
# 2. Encuentra la línea recta que mejor se ajuste a esos 6 puntos
# 3. Extiende esa línea hasta 2018 para predecir el ranking
# 4. Repite para cada empresa
#
# LIMITACIONES:
# - Asume que la tendencia es lineal (línea recta)
# - No considera eventos especiales o cambios de política
# - Es una predicción simplificada

st.markdown('<h2 class="section-header">🔮 Predicción: Ranking 2018 usando Regresión Lineal</h2>', unsafe_allow_html=True)

# Preparar los años como variable independiente (X)
X_train = np.array([2012, 2013, 2014, 2015, 2016, 2017]).reshape(-1, 1)
predicciones = []

# Usar datos ya limpios para las predicciones
df_pred = df_clean.copy()
max_ranking = len(df_pred)

# Para cada empresa, crear un modelo de predicción
for _, row in df_pred.iterrows():
    # Obtener los rankings históricos de la empresa (variable dependiente Y)
    y_train = row[[str(y) for y in range(2012, 2018)]].values.astype(np.float64)

    # Si hay datos faltantes, saltar esta empresa
    if pd.isnull(y_train).any():
        predicciones.append(np.nan)
        continue

    # Crear y entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X_train, y_train)  # Entrenar el modelo con datos históricos
    
    # Predecir el ranking para 2018
    y_pred = model.predict([[2018]])[0]

    # Limitar la predicción entre 1 y el total de empresas
    # (no puede haber ranking 0 o mayor al número total de empresas)
    y_pred_clipped = np.clip(y_pred, 1, max_ranking)
    predicciones.append(y_pred_clipped)

# Agregar las predicciones al dataframe
df_pred["Ranking Predicho 2018"] = predicciones

# Mostrar resultados ordenados por predicción
st.dataframe(
    df_pred[["Empresa", "Ranking Promedio", "Ranking Predicho 2018"]]
    .sort_values("Ranking Predicho 2018")
    .reset_index(drop=True)
)

# Gráfico de las top 10 empresas según predicción
fig_pred = px.bar(
    df_pred.sort_values("Ranking Predicho 2018").head(10),
    x="Empresa", y="Ranking Predicho 2018", color="Empresa",
    title="Predicción: Top 10 Empresas con Mejor Ranking en 2018"
)
fig_pred.update_layout(
    yaxis=dict(autorange="reversed"),
    title_font_size=20,
    title_font_family="Arial, sans-serif",
    title_x=0.5
)
st.plotly_chart(fig_pred)

# Explicación final sobre las predicciones
st.markdown("""
### 📝 Nota importante sobre las predicciones

**¿Qué significa este análisis?**
- Las predicciones se basan en tendencias históricas de 2012-2017
- Se asume que los patrones del pasado continuarán en el futuro
- Es una herramienta de planificación, no una certeza absoluta

**Limitaciones del modelo:**
- No considera cambios regulatorios o de infraestructura
- Asume tendencias lineales (línea recta)
- Los rankings reales pueden variar por factores externos

**Uso recomendado:**
- Como herramienta de monitoreo y alerta temprana
- Para identificar empresas que podrían necesitar apoyo
- Como base para análisis más profundos
""")
