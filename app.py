
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Mapa de Stakeholders – Senior Market", layout="wide")

st.title("Mapa de Stakeholders – Senior Market")
st.caption("Tamaño = Importancia (1–10) · Distancia = Cercanía al núcleo (0–10) · Colores = Categoría")

with st.sidebar:
    st.header("Datos de entrada")
    st.write("Usa una URL de CSV (por ejemplo, Google Sheets → **Archivo > Publicar en la web** → CSV) o sube un CSV.")
    csv_url = st.text_input("URL CSV pública (opcional)")
    uploaded = st.file_uploader("O sube un CSV", type=["csv"])
    st.markdown("---")
    st.header("Opciones de visualización")
    size_scale = st.slider("Escala de tamaño", 1.0, 6.0, 3.0, 0.5)
    show_labels = st.checkbox("Mostrar etiquetas", value=True)
    ring_step = st.selectbox("Separación de anillos", [1, 2], index=1)  # 2 por defecto
    st.markdown("---")
    st.caption("Formato esperado de columnas: **Categoría, Grupo de interés, Importancia (1-10), Distancia (0-10), Nivel de categoría (1=Externo, 2=Conectado, 3=Interno)**")

# Cargar datos
df = None
error = None

try:
    if csv_url:
        df = pd.read_csv(csv_url)
    elif uploaded is not None:
        df = pd.read_csv(uploaded)
except Exception as e:
    error = str(e)

if df is None:
    st.info("👉 Proporciona una URL de CSV pública o sube un archivo CSV para ver el mapa.")
    st.stop()

# Validaciones mínimas
required_cols = ["Categoría", "Grupo de interés", "Importancia (1-10)", "Distancia (0-10)"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Faltan columnas requeridas: {missing}")
    st.stop()

# Si no existe 'Nivel de categoría', la creamos automáticamente
if "Nivel de categoría" not in df.columns:
    mapping = {"Interno": 3, "Conectado": 2, "Externo": 1}
    if "Categoría" in df.columns:
        df["Nivel de categoría"] = df["Categoría"].map(mapping).fillna(2)
    else:
        df["Nivel de categoría"] = 2

# Asegurar tipos numéricos
for col in ["Importancia (1-10)", "Distancia (0-10)", "Nivel de categoría"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Importancia (1-10)", "Distancia (0-10)", "Nivel de categoría"]).copy()

# Paleta
palette = {"Interno": "#6A5ACD", "Conectado": "#20B2AA", "Externo": "#FF8C00"}
df["color"] = df["Categoría"].map(palette).fillna("#999999")

# Crear figura Plotly con anillos concéntricos
fig = go.Figure()

# Anillos 0..10
for r in range(0, 11, ring_step):
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=-r, y0=-r, x1=r, y1=r,
        line=dict(color="lightgray", width=1),
    )
    # Etiqueta de radio
    if r > 0:
        fig.add_annotation(x=r, y=0, text=str(r), showarrow=False, font=dict(size=10, color="gray"))

# Dispersión
sizes = df["Importancia (1-10)"].astype(float) * size_scale

fig.add_trace(go.Scatter(
    x=df["Distancia (0-10)"] * np.cos(np.linspace(0, 2*np.pi, len(df), endpoint=False)),
    y=df["Distancia (0-10)"] * np.sin(np.linspace(0, 2*np.pi, len(df), endpoint=False)),
    mode="markers+text" if show_labels else "markers",
    text=df["Grupo de interés"] if show_labels else None,
    textposition="top center",
    marker=dict(
        size=sizes,
        color=df["color"],
        line=dict(color="white", width=1)
    ),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"  # Grupo
        "Categoría: %{customdata[1]}<br>"
        "Importancia: %{customdata[2]}<br>"
        "Distancia: %{customdata[3]}<br>"
        "Nivel de categoría: %{customdata[4]}<extra></extra>"
    ),
    customdata=np.stack([
        df["Grupo de interés"],
        df["Categoría"],
        df["Importancia (1-10)"],
        df["Distancia (0-10)"],
        df["Nivel de categoría"]
    ], axis=1)
))

fig.update_layout(
    width=1100, height=700,
    xaxis=dict(range=[-10.5, 10.5], zeroline=False, visible=False),
    yaxis=dict(range=[-10.5, 10.5], scaleanchor="x", scaleratio=1, zeroline=False, visible=False),
    plot_bgcolor="white",
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver / editar datos (tabla)"):
    st.dataframe(df)
    st.caption("Edita el CSV en tu Google Sheets y recarga la página para actualizar el mapa.")
