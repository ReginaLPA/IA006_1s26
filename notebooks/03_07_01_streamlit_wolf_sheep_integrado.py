
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Wolf Sheep Integrado", layout="wide")

st.title("Wolf Sheep Simple 3 — Modelo Integrado")
st.write("Dashboard para análise dos cenários base, ampliado e evolutivo.")

base_dir = Path("wolf_sheep_integrado_outputs")
csv_path = base_dir / "comparacao_todos_cenarios.csv"

if not csv_path.exists():
    st.error("CSV não encontrado. Rode primeiro o notebook.")
    st.stop()

df = pd.read_csv(csv_path)

st.subheader("Cenários disponíveis")
st.write(df["cenario"].unique())

cenario = st.selectbox("Escolha o cenário", sorted(df["cenario"].unique()))
dff = df[df["cenario"] == cenario]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Ticks", int(dff["tick"].max()))
    st.metric("Ovelhas finais", int(dff["sheep"].iloc[-1]))

with col2:
    st.metric("Lobos finais", int(dff["wolves"].iloc[-1]))
    st.metric("Máximo de ovelhas", int(dff["sheep"].max()))

with col3:
    st.metric("Máximo de lobos", int(dff["wolves"].max()))
    st.metric("Total predado", int(dff["eaten_sheep"].sum()))

st.subheader("Populações")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(dff["tick"], dff["sheep"], label="Ovelhas")
ax.plot(dff["tick"], dff["wolves"], label="Lobos")
ax.set_xlabel("Tick")
ax.set_ylabel("População")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.subheader("Genética")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(dff["tick"], dff["sheep_freq_S"], label="Ovelhas S — fuga")
ax.plot(dff["tick"], dff["sheep_freq_R"], label="Ovelhas R — resistência")
ax.plot(dff["tick"], dff["wolf_freq_H"], label="Lobos H — caça")
ax.plot(dff["tick"], dff["wolf_freq_R"], label="Lobos R — resistência")
ax.set_ylim(0, 1)
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.subheader("Dados")
st.dataframe(dff)
