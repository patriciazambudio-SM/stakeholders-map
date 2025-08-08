
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mapa de Stakeholders – Senior Market", layout="wide")

st.title("Mapa de Stakeholders – Senior Market")
st.caption("Tamaño = Importancia (1-5) · Distancia = Cercanía al núcleo (0-10) · Colores = Categoría")

# --- Entrada de datos
st.sidebar.header("Datos de entrada")
csv_url = st.sidebar.text_input("URL CSV pública (opcional)")
uploaded_file = st.sidebar.file_uploader("O sube un CSV", type="csv")

if csv_url:
    df = pd.read_csv(csv_url)
elif uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("➡ Proporciona una URL de CSV pública o sube un archivo CSV para ver el mapa.")
    st.stop()

# --- Opciones de visualización
st.sidebar.header("Opciones de visualización")
size_scale = st.sidebar.slider("Escala de tamaño", 1.0, 6.0, 3.0, 0.1)
show_labels = st.sidebar.checkbox("Mostrar etiquetas", True)

# --- Mapeo de colores
color_map = {
    1: "#f7ac6f",  # Externo
    2: "#e1f0ec",  # Conectado
    3: "#1f9e6f",  # Interno
}
df["color"] = df["Nivel de categoría"].map(color_map)

# --- Gráfico
fig = px.scatter(
    df,
    x="Distancia (0-10)",
    y="Importancia (1-5)",
    size="Importancia (1-5)",
    color="Nivel de categoría",
    hover_name="Grupo de interés",
    color_discrete_map=color_map,
    size_max=size_scale * 15,
)

fig.update_traces(text=df["Grupo de interés"] if show_labels else None)

fig.update_layout(
    xaxis_title="Distancia al núcleo (0=Centro, 10=Lejano)",
    yaxis_title="Importancia",
    xaxis=dict(range=[-0.5, 10.5], zeroline=False),
    yaxis=dict(range=[0, 5.5], zeroline=False),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# --- Mostrar tabla de datos
with st.expander("Ver / editar datos (tabla)"):
    st.dataframe(df)
