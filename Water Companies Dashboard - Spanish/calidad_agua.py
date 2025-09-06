# =============================
# Ranking Calidad de Agua Potable - Dashboard
# =============================

import pandas as pd              # Para análisis de datos
import plotly.express as px      # Para visualización interactiva
import matplotlib.pyplot as plt  # Para visualización opcional tradicional
import seaborn as sns            # Para mapas de calor (opcional)
import numpy as np               # Para manejo numérico

# -----------------------------
# Cargar y limpiar los datos
# -----------------------------

# Ruta al archivo Excel
file_path = "cuadro-45-ranking-de-calidad-del-agua-potable.xlsx"

# Cargar hoja con datos, omitiendo primeras 4 filas de encabezado innecesarias
df_raw = pd.read_excel(file_path, sheet_name='Ranking Calidad AP', skiprows=4)

# Eliminar columnas totalmente vacías
df_raw.dropna(axis=1, how='all', inplace=True)

# Renombrar columnas para facilitar análisis
df_raw.columns = ['Ranking Actual', 'Empresa', '2012', '2013', '2014', '2015', '2016', '2017']

# Eliminar filas completamente vacías (por si hay al final del archivo)
df_raw.dropna(how='all', inplace=True)

# Mostrar primeras filas
print("Datos cargados:")
print(df_raw.head())

# -----------------------------
# Preprocesamiento adicional
# -----------------------------

# Convertir columnas de año a tipo numérico
for year in ['2012', '2013', '2014', '2015', '2016', '2017']:
    df_raw[year] = pd.to_numeric(df_raw[year], errors='coerce')

# Calcular promedio de ranking por empresa (omitirá NaNs)
df_raw['Ranking Promedio'] = df_raw[['2012', '2013', '2014', '2015', '2016', '2017']].mean(axis=1)

# Ordenar por mejor ranking promedio (menor es mejor)
df_sorted = df_raw.sort_values(by='Ranking Promedio')

# -----------------------------
# Visualización - Top 5 Empresas
# -----------------------------

# Seleccionar top 5 con mejor promedio
top5 = df_sorted.head(5)

# Gráfico de barras interactivo
fig_top = px.bar(
    top5,
    x="Empresa",
    y="Ranking Promedio",
    title="🏆 Top 5 Empresas con Mejor Ranking Promedio de Calidad de Agua (2012-2017)",
    color="Empresa",
    text="Ranking Promedio"
)
fig_top.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig_top.update_layout(xaxis_title="Empresa", yaxis_title="Ranking Promedio", showlegend=False)
fig_top.show()

# -----------------------------
# Visualización - Evolución por Empresa
# -----------------------------

# Reorganizar (melt) para graficar la evolución temporal
df_melted = df_raw.melt(id_vars=["Empresa"], value_vars=['2012', '2013', '2014', '2015', '2016', '2017'],
                        var_name="Año", value_name="Ranking")

# Convertir año a tipo string o categórico ordenado
df_melted["Año"] = df_melted["Año"].astype(str)

# Gráfico de líneas de evolución por empresa (solo top 5)
fig_line = px.line(
    df_melted[df_melted['Empresa'].isin(top5['Empresa'])],
    x="Año",
    y="Ranking",
    color="Empresa",
    title="📈 Evolución del Ranking de Calidad de Agua - Top 5 Empresas",
    markers=True
)
fig_line.update_layout(yaxis=dict(autorange="reversed"))  # Porque menor ranking es mejor
fig_line.show()

# -----------------------------
# Mapa de calor de rankings
# -----------------------------

# Crear matriz para heatmap
heatmap_data = df_raw.set_index("Empresa")[['2012', '2013', '2014', '2015', '2016', '2017']]

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", linewidths=0.5)
plt.title("🔍 Ranking de Calidad de Agua por Empresa (2012-2017)")
plt.xlabel("Año")
plt.ylabel("Empresa")
plt.tight_layout()
plt.show()
