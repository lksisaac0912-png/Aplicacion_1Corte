import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# Configuración inicial
# ===============================
st.set_page_config(page_title="EDA Concreto", layout="wide")
st.title("🏗️ Exploración de Datos - Resistencia del Concreto")

# ===============================
# Subida de dataset
# ===============================
uploaded_file = st.sidebar.file_uploader("📂 Sube tu dataset (.csv o .xls)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    # Detectar extensión
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("👀 Vista previa del dataset")
    st.dataframe(df.head())

    # ===============================
    # Pregunta 1: Variables que más influyen
    # ===============================
    st.markdown("## 1️⃣ Variables que influyen en la resistencia")
    if "Concrete compressive strength" in df.columns:
        corr = df.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No se encontró la columna 'Concrete compressive strength'.")

    # ===============================
    # Pregunta 2: Histograma interactivo
    # ===============================
    st.markdown("## 2️⃣ Distribución de variables (Histogramas)")
    variable = st.sidebar.selectbox("Selecciona una variable:", df.columns)
    fig, ax = plt.subplots()
    ax.hist(df[variable], bins=20, color="skyblue", edgecolor="black")
    ax.set_xlabel(variable)
    ax.set_ylabel("Frecuencia")
    ax.set_title(f"Histograma de {variable}")
    st.pyplot(fig)

    # ===============================
    # Pregunta 3: Scatter Plot interactivo
    # ===============================
    st.markdown("## 3️⃣ Relación entre dos variables (Scatter Plot)")
    x_var = st.sidebar.selectbox("Eje X:", df.columns, index=0)
    y_var = st.sidebar.selectbox("Eje Y:", df.columns, index=1)

    if x_var != y_var:
        fig, ax = plt.subplots()
        scatter = ax.scatter(df[x_var], df[y_var],
                             c=df["Concrete compressive strength"], cmap="viridis", alpha=0.7)
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        ax.set_title(f"{y_var} vs {x_var}")
        cbar = plt.colorbar(scatter)
        cbar.set_label("Resistencia")
        st.pyplot(fig)

    # ===============================
    # Pregunta 4: Relación Agua/Cemento
    # ===============================
    st.markdown("## 4️⃣ Relación Agua/Cemento vs Resistencia")
    if "Water" in df.columns and "Cement" in df.columns:
        df["Relación A/C"] = df["Water"] / df["Cement"]
        fig, ax = plt.subplots()
        ax.scatter(df["Relación A/C"], df["Concrete compressive strength"], alpha=0.7, color="orange")
        ax.set_xlabel("Relación Agua/Cemento")
        ax.set_ylabel("Resistencia")
        st.pyplot(fig)

    # ===============================
    # Pregunta 5: Valores atípicos
    # ===============================
    st.markdown("## 5️⃣ Valores atípicos")
    target = "Concrete compressive strength"
    if target in df.columns:
        fig, ax = plt.subplots()
        sns.boxplot(y=df[target], ax=ax)
        ax.set_ylabel("Resistencia")
        st.pyplot(fig)

        st.write("🔎 Valores extremos detectados:")
        st.dataframe(df[(df[target] < df[target].quantile(0.05)) |
                        (df[target] > df[target].quantile(0.95))])
