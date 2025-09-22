# app_scatter.py (plantilla mínima)
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Scatter interactivo — Mezclas de Concreto 🏗️")

uploaded = st.sidebar.file_uploader("Sube tu CSV", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
else:
    try:
        df = pd.read_csv("datos.csv")
    except FileNotFoundError:
        st.error("Sube 'datos.csv' o usa el uploader.")
        st.stop()

numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
if len(numeric_cols) < 2:
    st.error("Se necesitan al menos 2 columnas numéricas para el scatter.")
    st.stop()

x = st.sidebar.selectbox("Eje X", numeric_cols, index=0)
y = st.sidebar.selectbox("Eje Y", numeric_cols, index=1)

# Botón opcional para mostrar
if st.sidebar.button("Mostrar scatter con línea de tendencia"):
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, ax=ax)
    sns.regplot(data=df, x=x, y=y, scatter=False, ax=ax, ci=95)  # línea de tendencia
    ax.set_title(f"{y} vs {x}")
    st.pyplot(fig)
