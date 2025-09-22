import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
st.set_page_config(
    page_title="Análisis de Resistencia del Concreto",
    page_icon="🏗️",
    layout="wide"
)
@st.cache_data
def load_data():
    """
    Genera datos simulados basados en el dataset de resistencia del concreto de UCI
    En un caso real, usarías: pd.read_csv('concrete_data.csv')
    """
    np.random.seed(42)
    n_samples = 1030
    cement = np.random.normal(280, 104, n_samples)
    blast_furnace_slag = np.random.exponential(73, n_samples)
    fly_ash = np.random.exponential(54, n_samples)
    water = np.random.normal(182, 21, n_samples)
    superplasticizer = np.random.exponential(6.2, n_samples)
    coarse_aggregate = np.random.normal(972, 77, n_samples)
    fine_aggregate = np.random.normal(773, 80, n_samples)
    age = np.random.exponential(45, n_samples)
