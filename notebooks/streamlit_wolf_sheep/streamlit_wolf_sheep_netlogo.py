"""
Simulador Wolf Sheep Predation em Streamlit
Inspirado no modelo Wolf Sheep Predation do NetLogo.

Como executar:
    streamlit run streamlit_wolf_sheep_netlogo.py

Dependências:
    pip install streamlit numpy pandas matplotlib

O modelo usa uma grade toroidal: quando um agente sai por uma borda,
ele reaparece do outro lado, como no NetLogo.
"""

import os
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

# Evita erro de permissão do cache do Matplotlib em ambientes JupyterHub/Docker.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


# Estruturas do modelo
@dataclass
class Agent:
    """Representa uma ovelha ou um lobo."""
    id: int
    species: str  # "sheep" ou "wolf"
    x: int
    y: int
    energy: float


@dataclass
class ModelParams:
    width: int
    height: int
    initial_sheep: int
    initial_wolves: int
    sheep_gain_from_food: float
    wolf_gain_from_food: float
    sheep_reproduce: float
    wolf_reproduce: float
    sheep_initial_energy_min: float
    sheep_initial_energy_max: float
    wolf_initial_energy_min: float
    wolf_initial_energy_max: float
    grass_regrowth_time: int
    enable_grass: bool
    seed: int


# Funções auxiliares
def random_position(width: int, height: int) -> Tuple[int, int]:
    return random.randrange(width), random.randrange(height)


def torus_move(x: int, y: int, width: int, height: int) -> Tuple[int, int]:
    """Move para uma das 8 direções, com bordas toroidais."""
    dx, dy = random.choice([
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1),
    ])
    return (x + dx) % width, (y + dy) % height


def new_agent_id() -> int:
    st.session_state.next_id += 1
    return st.session_state.next_id


def make_agent(species: str, params: ModelParams) -> Agent:
    x, y = random_position(params.width, params.height)
    if species == "sheep":
        energy = random.uniform(
            params.sheep_initial_energy_min,
            params.sheep_initial_energy_max,
        )
    else:
        energy = random.uniform(
            params.wolf_initial_energy_min,
            params.wolf_initial_energy_max,
        )
    return Agent(id=new_agent_id(), species=species, x=x, y=y, energy=energy)


def reset_model(params: ModelParams) -> None:
    """Inicializa o estado do modelo."""
    random.seed(params.seed)
    np.random.seed(params.seed)

    st.session_state.next_id = 0
    st.session_state.tick = 0

    st.session_state.sheep = [make_agent("sheep", params) for _ in range(params.initial_sheep)]
    st.session_state.wolves = [make_agent("wolf", params) for _ in range(params.initial_wolves)]

    # grass_available=True significa patch com grama disponível.
    st.session_state.grass_available = np.ones((params.height, params.width), dtype=bool)
    st.session_state.grass_countdown = np.zeros((params.height, params.width), dtype=int)

    # Começa com alguns patches sem grama, para dar dinâmica visual.
    if params.enable_grass:
        mask = np.random.random((params.height, params.width)) < 0.25
        st.session_state.grass_available[mask] = False
        st.session_state.grass_countdown[mask] = np.random.randint(
            1, params.grass_regrowth_time + 1, size=mask.sum()
        )

    st.session_state.history = []
    save_history(params)


def save_history(params: ModelParams) -> None:
    sheep_count = len(st.session_state.sheep)
    wolf_count = len(st.session_state.wolves)
    grass_count = int(st.session_state.grass_available.sum()) if params.enable_grass else np.nan

    sheep_energy = np.mean([a.energy for a in st.session_state.sheep]) if sheep_count else 0
    wolf_energy = np.mean([a.energy for a in st.session_state.wolves]) if wolf_count else 0

    st.session_state.history.append({
        "tick": st.session_state.tick,
        "ovelhas": sheep_count,
        "lobos": wolf_count,
        "grama": grass_count,
        "energia_media_ovelhas": sheep_energy,
        "energia_media_lobos": wolf_energy,
    })


def regrow_grass(params: ModelParams) -> None:
    if not params.enable_grass:
        return

    unavailable = ~st.session_state.grass_available
    st.session_state.grass_countdown[unavailable] -= 1

    regrown = unavailable & (st.session_state.grass_countdown <= 0)
    st.session_state.grass_available[regrown] = True
    st.session_state.grass_countdown[regrown] = 0


def move_and_feed_sheep(params: ModelParams) -> List[Agent]:
    survivors: List[Agent] = []
    babies: List[Agent] = []

    random.shuffle(st.session_state.sheep)

    for sheep in st.session_state.sheep:
        sheep.x, sheep.y = torus_move(sheep.x, sheep.y, params.width, params.height)
        sheep.energy -= 1

        if params.enable_grass and st.session_state.grass_available[sheep.y, sheep.x]:
            sheep.energy += params.sheep_gain_from_food
            st.session_state.grass_available[sheep.y, sheep.x] = False
            st.session_state.grass_countdown[sheep.y, sheep.x] = params.grass_regrowth_time

        if sheep.energy > 0 and random.random() < params.sheep_reproduce / 100:
            # Reprodução no estilo NetLogo: cria filhote e divide energia.
            sheep.energy /= 2
            baby = Agent(
                id=new_agent_id(),
                species="sheep",
                x=sheep.x,
                y=sheep.y,
                energy=sheep.energy,
            )
            babies.append(baby)

        if sheep.energy > 0:
            survivors.append(sheep)

    return survivors + babies


def sheep_index_by_position(sheep_list: List[Agent]) -> Dict[Tuple[int, int], List[Agent]]:
    index: Dict[Tuple[int, int], List[Agent]] = {}
    for sheep in sheep_list:
        index.setdefault((sheep.x, sheep.y), []).append(sheep)
    return index


def move_hunt_and_reproduce_wolves(params: ModelParams) -> Tuple[List[Agent], List[Agent]]:
    survivors: List[Agent] = []
    babies: List[Agent] = []

    random.shuffle(st.session_state.wolves)
    sheep_by_pos = sheep_index_by_position(st.session_state.sheep)
    eaten_sheep_ids = set()

    for wolf in st.session_state.wolves:
        wolf.x, wolf.y = torus_move(wolf.x, wolf.y, params.width, params.height)
        wolf.energy -= 1

        prey_list = sheep_by_pos.get((wolf.x, wolf.y), [])
        prey = None
        while prey_list:
            candidate = prey_list.pop()
            if candidate.id not in eaten_sheep_ids:
                prey = candidate
                break

        if prey is not None:
            eaten_sheep_ids.add(prey.id)
            wolf.energy += params.wolf_gain_from_food

        if wolf.energy > 0 and random.random() < params.wolf_reproduce / 100:
            wolf.energy /= 2
            baby = Agent(
                id=new_agent_id(),
                species="wolf",
                x=wolf.x,
                y=wolf.y,
                energy=wolf.energy,
            )
            babies.append(baby)

        if wolf.energy > 0:
            survivors.append(wolf)

    remaining_sheep = [s for s in st.session_state.sheep if s.id not in eaten_sheep_ids]
    return survivors + babies, remaining_sheep


def step_model(params: ModelParams) -> None:
    """Executa um tick da simulação."""
    if len(st.session_state.sheep) == 0 and len(st.session_state.wolves) == 0:
        return

    st.session_state.tick += 1

    regrow_grass(params)
    st.session_state.sheep = move_and_feed_sheep(params)
    st.session_state.wolves, st.session_state.sheep = move_hunt_and_reproduce_wolves(params)

    save_history(params)


def run_steps(params: ModelParams, n: int) -> None:
    for _ in range(n):
        if st.session_state.tick >= 2000:
            break
        step_model(params)
        # Para quando há extinção completa.
        if len(st.session_state.sheep) == 0 and len(st.session_state.wolves) == 0:
            break


# Visualizações
def plot_world(params: ModelParams):
    fig, ax = plt.subplots(figsize=(7, 7))

    if params.enable_grass:
        # 0 = sem grama, 1 = grama
        background = st.session_state.grass_available.astype(int)
        ax.imshow(background, origin="lower", extent=(-0.5, params.width - 0.5, -0.5, params.height - 0.5), alpha=0.55)
    else:
        ax.set_facecolor("#e8e8e8")

    if st.session_state.sheep:
        sx = [s.x for s in st.session_state.sheep]
        sy = [s.y for s in st.session_state.sheep]
        ax.scatter(sx, sy, marker="o", s=45, label="Ovelhas", edgecolors="black", linewidths=0.4)

    if st.session_state.wolves:
        wx = [w.x for w in st.session_state.wolves]
        wy = [w.y for w in st.session_state.wolves]
        ax.scatter(wx, wy, marker="^", s=65, label="Lobos", edgecolors="black", linewidths=0.4)

    ax.set_xlim(-0.5, params.width - 0.5)
    ax.set_ylim(-0.5, params.height - 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Mundo — tick {st.session_state.tick}")
    ax.legend(loc="upper right")
    fig.tight_layout()
    return fig


def history_dataframe() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.history)


def plot_population_history(params: ModelParams) -> None:
    df = history_dataframe()
    if df.empty:
        return

    pop_cols = ["ovelhas", "lobos"]
    if params.enable_grass:
        pop_cols.append("grama")

    st.line_chart(df.set_index("tick")[pop_cols])


def show_summary_metrics(params: ModelParams) -> None:
    df = history_dataframe()
    last = df.iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tick", int(last["tick"]))
    c2.metric("Ovelhas", int(last["ovelhas"]))
    c3.metric("Lobos", int(last["lobos"]))
    if params.enable_grass:
        c4.metric("Patches com grama", int(last["grama"]))
    else:
        c4.metric("Grama", "desativada")


# Interface Streamlit
st.set_page_config(
    page_title="Wolf Sheep Predation — Streamlit",
    page_icon="🐺",
    layout="wide",
)

st.title("🐺🐑 Wolf Sheep Predation em Streamlit")
st.caption("Simulação inspirada no modelo Wolf Sheep Predation do NetLogo.")

with st.sidebar:
    st.header("Parâmetros do modelo")

    seed = st.number_input("Semente aleatória", min_value=0, max_value=999999, value=42, step=1)

    st.subheader("Mundo")
    width = st.slider("Largura da grade", 10, 80, 35, 1)
    height = st.slider("Altura da grade", 10, 80, 35, 1)
    enable_grass = st.checkbox("Ativar grama", value=True)
    grass_regrowth_time = st.slider("Tempo de rebrota da grama", 1, 100, 30, 1)

    st.subheader("População inicial")
    initial_sheep = st.slider("Ovelhas iniciais", 0, 500, 100, 1)
    initial_wolves = st.slider("Lobos iniciais", 0, 300, 50, 1)

    st.subheader("Energia")
    sheep_gain_from_food = st.slider("Energia da ovelha ao comer grama", 1.0, 20.0, 4.0, 0.5)
    wolf_gain_from_food = st.slider("Energia do lobo ao comer ovelha", 1.0, 50.0, 20.0, 0.5)

    sheep_initial_energy_min = st.slider("Energia inicial mínima das ovelhas", 1.0, 20.0, 2.0, 0.5)
    sheep_initial_energy_max = st.slider("Energia inicial máxima das ovelhas", 1.0, 40.0, 8.0, 0.5)
    wolf_initial_energy_min = st.slider("Energia inicial mínima dos lobos", 1.0, 40.0, 5.0, 0.5)
    wolf_initial_energy_max = st.slider("Energia inicial máxima dos lobos", 1.0, 80.0, 20.0, 0.5)

    st.subheader("Reprodução")
    sheep_reproduce = st.slider("Reprodução das ovelhas (%)", 0.0, 30.0, 4.0, 0.5)
    wolf_reproduce = st.slider("Reprodução dos lobos (%)", 0.0, 30.0, 5.0, 0.5)

    params = ModelParams(
        width=width,
        height=height,
        initial_sheep=initial_sheep,
        initial_wolves=initial_wolves,
        sheep_gain_from_food=sheep_gain_from_food,
        wolf_gain_from_food=wolf_gain_from_food,
        sheep_reproduce=sheep_reproduce,
        wolf_reproduce=wolf_reproduce,
        sheep_initial_energy_min=min(sheep_initial_energy_min, sheep_initial_energy_max),
        sheep_initial_energy_max=max(sheep_initial_energy_min, sheep_initial_energy_max),
        wolf_initial_energy_min=min(wolf_initial_energy_min, wolf_initial_energy_max),
        wolf_initial_energy_max=max(wolf_initial_energy_min, wolf_initial_energy_max),
        grass_regrowth_time=grass_regrowth_time,
        enable_grass=enable_grass,
        seed=int(seed),
    )

    st.divider()
    st.subheader("Execução")
    steps_per_click = st.slider("Passos por clique", 1, 300, 20, 1)


# Inicialização do estado
if "history" not in st.session_state:
    reset_model(params)

# Se os parâmetros estruturais mudarem muito, o usuário pode resetar manualmente.
# Mantemos o estado para não apagar a simulação a cada interação.

col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 2])

with col_a:
    if st.button("▶️ Rodar 1 passo", use_container_width=True):
        run_steps(params, 1)

with col_b:
    if st.button(f"⏩ Rodar {steps_per_click} passos", use_container_width=True):
        run_steps(params, steps_per_click)

with col_c:
    if st.button("🔄 Resetar", use_container_width=True):
        reset_model(params)

with col_d:
    st.info("A simulação usa bordas toroidais: os agentes atravessam uma borda e reaparecem na outra.")

show_summary_metrics(params)

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Mundo da simulação")
    fig = plot_world(params)
    st.pyplot(fig, clear_figure=True)

with right:
    st.subheader("Histórico das populações")
    plot_population_history(params)

    st.subheader("Interpretação rápida")
    sheep_now = len(st.session_state.sheep)
    wolves_now = len(st.session_state.wolves)

    if sheep_now == 0 and wolves_now == 0:
        st.error("Extinção completa: não restaram lobos nem ovelhas.")
    elif sheep_now == 0:
        st.warning("As ovelhas foram extintas. Sem alimento, os lobos tendem a desaparecer em seguida.")
    elif wolves_now == 0:
        st.warning("Os lobos foram extintos. As ovelhas podem crescer até serem limitadas pela grama.")
    else:
        st.success("Lobos, ovelhas e recursos ainda coexistem no sistema.")

st.divider()

with st.expander("Ver dados da simulação"):
    df_hist = history_dataframe()
    st.dataframe(df_hist, use_container_width=True)
    st.download_button(
        "Baixar histórico em CSV",
        data=df_hist.to_csv(index=False).encode("utf-8"),
        file_name="historico_wolf_sheep.csv",
        mime="text/csv",
    )

with st.expander("Como o modelo funciona"):
    st.markdown(
        """
        Em cada tick:

        1. A grama rebrota quando o contador do patch chega a zero.
        2. Cada ovelha se move aleatoriamente, perde energia e come grama quando há grama no patch.
        3. Ovelhas com energia positiva podem se reproduzir; a energia é dividida com o filhote.
        4. Cada lobo se move aleatoriamente, perde energia e come uma ovelha quando encontra uma no mesmo patch.
        5. Lobos com energia positiva podem se reproduzir; a energia é dividida com o filhote.
        6. Agentes com energia menor ou igual a zero morrem.

        Esse comportamento reproduz a lógica central do Wolf Sheep Predation do NetLogo, mas foi escrito em Python puro para facilitar estudo, alteração e publicação com Streamlit.
        """
    )

with st.expander("Sugestões de experimentos"):
    st.markdown(
        """
        - Aumente a reprodução das ovelhas e observe se há explosão populacional.
        - Aumente a energia dos lobos ao comer ovelhas e veja se os lobos dominam o sistema.
        - Aumente o tempo de rebrota da grama e observe se as ovelhas entram em colapso.
        - Desative a grama para estudar apenas a relação predador-presa.
        - Rode vários cenários com sementes diferentes para comparar estabilidade e extinção.
        """
    )
