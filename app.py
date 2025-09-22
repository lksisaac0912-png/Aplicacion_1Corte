# app.py
"""
Streamlit app - Optimización de mezclas de concreto
Objetivo: permitir que un ingeniero de materiales explore cómo la variación
en los componentes de la mezcla afecta la resistencia a compresión.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO, BytesIO

sns.set_theme()  # estilo por defecto de seaborn

st.set_page_config(page_title="Optimización Mezclas - Concreto", layout="wide")
st.title("🏗️ Optimización de mezclas — Resistencia a compresión del concreto")
st.write(
    "Sube un CSV del dataset (ej: *Concrete Compressive Strength* - UCI). "
    "La app permite explorar relaciones, filtrar por edad, crear razón agua/cemento y descargar datos filtrados."
)

# --------------------------
# CARGA DE DATOS
# --------------------------
st.sidebar.header("1) Cargar datos")
uploaded = st.sidebar.file_uploader("Sube tu archivo CSV (ej: concrete.csv)", type=["csv"])
use_local = st.sidebar.checkbox("Cargar 'concrete.csv' desde carpeta (si existe)", value=False)

df = None
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.sidebar.error("Error leyendo CSV: " + str(e))
elif use_local:
    try:
        df = pd.read_csv("concrete.csv")
        st.sidebar.success("Se cargó concrete.csv desde la carpeta.")
    except Exception as e:
        st.sidebar.error("No se encontró 'concrete.csv' en la carpeta: " + str(e))

if df is None:
    st.info("Sube un CSV para comenzar. Si descargaste el dataset UCI, conviértelo a CSV y súbelo aquí.")
    st.stop()

# --------------------------
# PREPARACIONES y DETECCIÓN DE COLUMNAS
# --------------------------
# Mapear nombres originales (preservamos nombres originales)
cols_map = {c.lower().strip(): c for c in df.columns}
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Crear columna water/cement si existen water y cement (nombres detectados por minúsculas)
if "water" in cols_map and "cement" in cols_map:
    w_col = cols_map["water"]
    c_col = cols_map["cement"]
    # evitar dividir por cero
    df["water_cement_ratio"] = df[w_col] / df[c_col].replace({0: np.nan})
    if "water_cement_ratio" not in numeric_cols:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Si hay columna 'age' normalizamos el nombre
age_col = cols_map.get("age", None)

# --------------------------
# PANEL PRINCIPAL: VISTA RÁPIDA
# --------------------------
st.header("Vista rápida de datos")
st.markdown("Primeras 10 filas:")
st.dataframe(df.head(10))

with st.expander("Mostrar `info()` (tipos y nulos)"):
    buf = StringIO()
    df.info(buf=buf)
    st.text(buf.getvalue())

st.subheader("Resumen estadístico")
st.dataframe(df.describe().T)

st.subheader("Conteo de valores nulos por columna")
nulls = df.isnull().sum()
st.dataframe(nulls[nulls > 0] if nulls.sum() > 0 else ("No se detectaron valores nulos."))

# --------------------------
# FILTRADO INTERACTIVO (sidebar)
# --------------------------
st.sidebar.header("2) Filtrar / Transformar datos")
# filtro por edad si existe
if age_col:
    min_age = int(df[age_col].min())
    max_age = int(df[age_col].max())
    age_range = st.sidebar.slider("Rango de edad (días) a incluir", min_age, max_age, (min_age, max_age))
    df_filtered = df[(df[age_col] >= age_range[0]) & (df[age_col] <= age_range[1])]
else:
    df_filtered = df.copy()

# opción de eliminar filas con nulos
drop_nans = st.sidebar.checkbox("Eliminar filas con cualquier nulo (solo para análisis)", value=False)
if drop_nans:
    before = df_filtered.shape[0]
    df_filtered = df_filtered.dropna()
    st.sidebar.write(f"Filas: {before} → {df_filtered.shape[0]} tras eliminar nulos")

# opción para log-transformar la variable Y (se aplicará solo en la gráfica si elige)
log_transform = st.sidebar.checkbox("Aplicar log a la variable Y (para gráficos)", value=False)

# --------------------------
# SELECCIÓN DE VARIABLES PARA GRAFICAR
# --------------------------
st.sidebar.header("3) Selección de variables")
if not numeric_cols:
    st.error("No se detectaron columnas numéricas en el dataset. La app necesita variables numéricas.")
    st.stop()

x_var = st.sidebar.selectbox("Componente (Eje X)", numeric_cols, index=0)
y_var = st.sidebar.selectbox("Variable objetivo (Eje Y)", numeric_cols, index=len(numeric_cols) - 1)

st.header("Visualizaciones")
st.markdown(f"**{y_var}** vs **{x_var}** (datos filtrados: {df_filtered.shape[0]} filas)")

# Preparar datos para graficar (si log requested, verificamos >0)
df_plot = df_filtered[[x_var, y_var]].dropna()
if log_transform:
    # mantener solo valores positivos para log
    df_plot = df_plot[df_plot[y_var] > 0]
    df_plot = df_plot.copy()
    df_plot[y_var] = np.log(df_plot[y_var])
    st.caption("Se está graphando ln(Y). Ten en cuenta que se excluyeron Y ≤ 0 para la transformación.")

# Scatter + línea de regresión simple
fig1, ax1 = plt.subplots(figsize=(7, 4))
sns.scatterplot(data=df_plot, x=x_var, y=y_var, ax=ax1, alpha=0.6)
# línea de tendencia (regresión 1er orden)
if len(df_plot) > 1:
    m, b = np.polyfit(df_plot[x_var], df_plot[y_var], 1)
    x_vals = np.linspace(df_plot[x_var].min(), df_plot[x_var].max(), 100)
    ax1.plot(x_vals, m * x_vals + b, linestyle="--", linewidth=1)
    ax1.text(0.02, 0.95, f"y = {m:.3f} x + {b:.3f}", transform=ax1.transAxes, fontsize=9, verticalalignment="top")
ax1.set_title(f"{y_var} vs {x_var}")
ax1.set_ylabel(f"{'ln('+y_var+')' if log_transform else y_var}")
st.pyplot(fig1)

# Histograma del X seleccionado
st.subheader(f"Distribución de {x_var}")
fig2, ax2 = plt.subplots(figsize=(6, 3))
ax2.hist(df_filtered[x_var].dropna(), bins=25, edgecolor="black")
ax2.set_xlabel(x_var)
ax2.set_ylabel("Frecuencia")
st.pyplot(fig2)

# Boxplot de Y
st.subheader(f"Boxplot de {y_var}")
fig3, ax3 = plt.subplots(figsize=(6, 2))
sns.boxplot(x=df_filtered[y_var].dropna(), ax=ax3)
st.pyplot(fig3)

# Heatmap de correlación
st.subheader("Mapa de calor de correlaciones (variables numéricas)")
corr_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
fig4, ax4 = plt.subplots(figsize=(9, 7))
corr = df_filtered[corr_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", vmin=-1, vmax=1, ax=ax4)
st.pyplot(fig4)

# Mostrar variables más correlacionadas con y_var
if y_var in corr.columns:
    st.subheader(f"Variables más correlacionadas con {y_var}")
    corr_with_y = corr[y_var].drop(labels=[y_var]).abs().sort_values(ascending=False)
    st.table(pd.DataFrame({"variable": corr_with_y.index, "abs_corr_with_"+y_var: corr_with_y.values}).reset_index(drop=True).head(10))

# --------------------------
# EXPORTAR DATOS FILTRADOS
# --------------------------
st.header("Exportar datos filtrados")
to_download = BytesIO()
df_filtered.to_csv(to_download, index=False)
to_download.seek(0)
st.download_button("Descargar CSV de datos filtrados", data=to_download, file_name="concrete_filtered.csv", mime="text/csv")

# --------------------------
# Sugerencias rápidas para interpretar la salida
# --------------------------
st.sidebar.header("Interpretación rápida")
st.sidebar.markdown(
    "- Observa la pendiente y el spread en el scatter: pendiente positiva indica que al aumentar X aumenta Y.\n"
    "- Revisa el heatmap: correlaciones altas (±0.6/0.7) son señales fuertes.\n"
    "- Si la distribución de Y está sesgada, prueba `ln(Y)` (casilla log en la barra lateral).\n"
    "- Los outliers en boxplot pueden ser errores de medida o mezclas experimentales especiales: investigarlos.\n"
)

st.caption("App generada para análisis exploratorio. Ajusta nombres de columnas si tu CSV usa etiquetas distintas (ej. 'Cement' en vez de 'cement').")
import streamlit as st
import pandas as pd

st.markdown("## 🧹 Manejo de valores nulos")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Mostrar cantidad de nulos
    st.write("### Valores nulos por columna:")
    st.dataframe(df.isnull().sum())

    # Opción de tratamiento
    opcion = st.radio(
        "Selecciona una estrategia para manejar nulos:",
        ("No hacer nada", "Eliminar filas con nulos", "Rellenar con media", "Rellenar con mediana", "Rellenar con moda")
    )

    if opcion == "Eliminar filas con nulos":
        df = df.dropna()
        st.success("✅ Se eliminaron las filas con valores nulos.")

    elif opcion == "Rellenar con media":
        df = df.fillna(df.mean(numeric_only=True))
        st.success("✅ Los valores nulos fueron reemplazados con la media.")

    elif opcion == "Rellenar con mediana":
        df = df.fillna(df.median(numeric_only=True))
        st.success("✅ Los valores nulos fueron reemplazados con la mediana.")

    elif opcion == "Rellenar con moda":
        df = df.fillna(df.mode().iloc[0])
        st.success("✅ Los valores nulos fueron reemplazados con la moda.")

    # Mostrar DataFrame limpio
    st.write("### DataFrame después del tratamiento de nulos:")
    st.dataframe(df.head())
