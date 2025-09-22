import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ===============================
# 1. Configuración inicial
# ===============================
st.set_page_config(page_title="Análisis EDA Concreto", layout="wide")
st.title("🏗️ Exploración de Datos - Resistencia del Concreto")

# Cargar dataset
uploaded_file = st.file_uploader("📂 Sube el archivo Concrete_Data.xls", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("👀 Vista previa del dataset")
    st.dataframe(df.head())

    # ===============================
    # Pregunta 1: Variables que más influyen
    # ===============================
    st.markdown("## 1️⃣ ¿Qué variables influyen más en la resistencia?")
    corr = df.corr()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

    # ===============================
    # Pregunta 2: Resistencia vs Tiempo de curado
    # ===============================
    st.markdown("## 2️⃣ ¿Cómo varía la resistencia con el tiempo de curado?")
    if "Age" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(x="Age", y="Concrete compressive strength", data=df, ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("⚠️ No se encontró la columna 'Age' en el dataset.")

    # ===============================
    # Pregunta 3: Combinaciones de materiales
    # ===============================
    st.markdown("## 3️⃣ ¿Qué combinaciones de materiales producen más o menos resistencia?")
    x_var = st.selectbox("📊 Selecciona un material para eje X", df.columns)
    y_var = st.selectbox("📊 Selecciona otro material para eje Y", df.columns)

    if x_var != y_var:
        fig, ax = plt.subplots(figsize=(7, 5))
        scatter = ax.scatter(df[x_var], df[y_var],
                             c=df["Concrete compressive strength"], cmap="viridis")
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        cbar = plt.colorbar(scatter)
        cbar.set_label("Resistencia")
        st.pyplot(fig)

    # ===============================
    # Pregunta 4: Relación agua/cemento
    # ===============================
    st.markdown("## 4️⃣ ¿Cuál es el impacto de la relación Agua/Cemento?")
    if "Water" in df.columns and "Cement" in df.columns:
        df["Relación A/C"] = df["Water"] / df["Cement"]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(df["Relación A/C"], df["Concrete compressive strength"], alpha=0.7)
        ax.set_xlabel("Relación Agua/Cemento")
        ax.set_ylabel("Resistencia")
        st.pyplot(fig)
    else:
        st.warning("⚠️ No se encontraron columnas 'Water' y 'Cement' en el dataset.")

    # ===============================
    # Pregunta 5: Valores atípicos
    # ===============================
    st.markdown("## 5️⃣ ¿Existen valores atípicos o inconsistencias?")
    target = "Concrete compressive strength"
    if target in df.columns:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(y=df[target], ax=ax)
        ax.set_ylabel("Resistencia")
        st.pyplot(fig)

        st.write("🔎 Valores extremos detectados:")
        st.dataframe(df[(df[target] < df[target].quantile(0.05)) |
                        (df[target] > df[target].quantile(0.95))])
    else:
        st.warning("⚠️ No se encontró la columna 'Concrete compressive strength' en el dataset.")
else:
    st.info("👆 Sube tu archivo de datos para comenzar el análisis.")

