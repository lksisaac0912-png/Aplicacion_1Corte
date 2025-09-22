# app_histograma.py (plantilla mínima)
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Histograma interactivo — Mezclas de Concreto 🏗️")

# Cargar CSV desde uploader (o intentar 'datos.csv' si existe)
uploaded = st.sidebar.file_uploader("Sube tu archivo CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
else:
    try:
        df = pd.read_csv("datos.csv")
    except FileNotFoundError:
        st.error("No encontré 'datos.csv'. Sube un archivo CSV para continuar.")
        st.stop()

# Detectar columnas numéricas
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
if not numeric_cols:
    st.error("No hay columnas numéricas detectadas en tu CSV.")
    st.stop()

# Selector en la sidebar
var = st.sidebar.selectbox("Selecciona variable para el histograma", numeric_cols)

# Mostrar histograma
fig, ax = plt.subplots()
sns.histplot(df[var].dropna(), kde=True, ax=ax)
ax.set_title(f"Histograma de {var}")
ax.set_xlabel(var)
ax.set_ylabel("Frecuencia")
st.pyplot(fig)
