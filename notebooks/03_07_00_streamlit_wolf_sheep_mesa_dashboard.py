
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Wolf Sheep Mesa", layout="wide")
st.title("Wolf Sheep Simple 3 com Mesa")

csv_path = Path("wolf_sheep_mesa_outputs/wolf_sheep_mesa_historico.csv")
if not csv_path.exists():
    st.error("CSV não encontrado. Rode primeiro o notebook.")
    st.stop()

df = pd.read_csv(csv_path)
col1, col2, col3 = st.columns(3)
col1.metric("Ticks", int(df["tick"].max()))
col2.metric("Ovelhas finais", int(df["sheep"].iloc[-1]))
col3.metric("Lobos finais", int(df["wolves"].iloc[-1]))

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df["tick"], df["sheep"], label="Ovelhas")
ax.plot(df["tick"], df["wolves"], label="Lobos")
ax.grid(True); ax.legend(); st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df["tick"], df["mean_grass"], label="Grama média")
ax.plot(df["tick"], df["grass_growth_rate"], label="Taxa crescimento")
ax.grid(True); ax.legend(); st.pyplot(fig)

st.dataframe(df)
