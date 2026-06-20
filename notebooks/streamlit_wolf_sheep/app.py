# -*- coding: utf-8 -*-
"""
Wolf Sheep Simple 3 — Modelo Integrado
Dashboard Streamlit com visualização espacial estilo NetLogo.

Execute com:
    streamlit run 03_07_01_streamlit_wolf_sheep_integrado.py
"""

import copy
import json
import math
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# Plotly pode falhar em alguns ambientes/proxies do Streamlit.
# Para garantir que a visualização apareça, o dashboard usa Matplotlib como renderização principal.
try:
    import plotly.graph_objects as go  # opcional, não é necessário para a visualização principal
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Wolf Sheep Integrado — NetLogo View",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }
        .hero-card {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(3, 43, 38, .96), rgba(7, 25, 31, .96));
            border: 1px solid rgba(102, 255, 178, .22);
            box-shadow: 0 10px 30px rgba(0,0,0,.22);
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            margin: 0;
            color: #f3fff8;
        }
        .hero-subtitle {
            font-size: 1.02rem;
            margin-top: .4rem;
            color: #b8d9cf;
        }
        .section-note {
            color: #b8d9cf;
            font-size: .95rem;
            margin-top: -.35rem;
        }
        .small-caption {
            color: #9bbab1;
            font-size: .86rem;
        }
        .metric-card {
            background: rgba(9, 48, 44, .72);
            border: 1px solid rgba(133, 218, 170, .22);
            border-radius: 16px;
            padding: .9rem 1rem;
            min-height: 108px;
        }
        .metric-label {
            font-size: .82rem;
            color: #a9cfc4;
            margin-bottom: .35rem;
        }
        .metric-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #ffffff;
        }
        .metric-help {
            font-size: .78rem;
            color: #86a99f;
            margin-top: .15rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <p class="hero-title">🐺🐑 Wolf Sheep Simple 3 — Modelo Integrado</p>
        <p class="hero-subtitle">
            Simulação baseada em agentes com visualização espacial estilo NetLogo, parâmetros ajustáveis,
            genética mendeliana, estações, doenças, migração, obstáculos e dashboard analítico.<br>
            Tem como objetivo ser um laboratório para mostrar a complexidade de forma visual, experimental e acessível.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# GENÉTICA E PARÂMETROS
SHEEP_GENES = ["V", "S", "R", "F"]
WOLF_GENES = ["V", "H", "R", "F"]

ALLELES = {
    "V": ("V", "v"),  # visão
    "S": ("S", "s"),  # fuga/velocidade — ovelhas
    "H": ("H", "h"),  # caça — lobos
    "R": ("R", "r"),  # resistência
    "F": ("F", "f"),  # fertilidade
}

GENE_NAMES = {
    "V": "visão",
    "S": "fuga/velocidade",
    "H": "caça",
    "R": "resistência à doença",
    "F": "fertilidade",
}

params_base = {
    # Ambiente
    "width": 50,
    "height": 50,
    "grass_max": 10.0,
    "grass_regrowth_base": 0.45,
    "obstacle_density": 0.06,

    # Populações iniciais
    "initial_sheep": 160,
    "initial_wolves": 45,

    # Energia
    "initial_sheep_energy": 24.0,
    "initial_wolf_energy": 36.0,
    "sheep_movement_cost": 1.0,
    "wolf_movement_cost": 1.2,
    "energy_gain_from_grass": 4.0,
    "energy_gain_from_sheep": 22.0,

    # Fome e idade
    "max_hunger_sheep": 18,
    "max_hunger_wolf": 24,
    "max_age_sheep": 90,
    "max_age_wolf": 120,

    # Visão
    "default_sheep_vision": 4,
    "default_wolf_vision": 5,

    # Reprodução
    "sheep_reproduction_energy_threshold": 34.0,
    "wolf_reproduction_energy_threshold": 48.0,
    "base_sheep_reproduction_prob": 0.045,
    "base_wolf_reproduction_prob": 0.025,
    "offspring_energy_fraction": 0.45,

    # Doença
    "initial_disease_prob": 0.02,
    "disease_spread_prob": 0.06,
    "disease_energy_cost": 1.2,
    "disease_death_prob": 0.01,
    "disease_recovery_prob": 0.015,

    # Migração
    "migration_prob": 0.01,
    "migration_edge_bias": 0.75,

    # Estações
    "season_length": 50,
    "season_growth_multipliers": {
        "primavera": 1.25,
        "verao": 1.00,
        "outono": 0.70,
        "inverno": 0.35,
    },

    # Genética
    "mutation_rate": 0.01,

    # Ativadores
    "use_obstacles": True,
    "use_seasons": True,
    "use_disease": True,
    "use_migration": True,
    "use_genetics": True,

    # Execução e visualização
    "n_steps": 300,
    "random_seed": 42,
    "frame_interval": 5,
    "agent_marker_size": 9,
    "show_grid_lines": True,
    "live_preview": True,
    "live_update_interval": 5,
    "stop_on_extinction": False,
}


def scenario_params(name: str) -> Dict:
    p = copy.deepcopy(params_base)
    if name == "base":
        p.update(
            {
                "use_obstacles": False,
                "use_seasons": False,
                "use_disease": False,
                "use_migration": False,
                "use_genetics": False,
                "obstacle_density": 0.0,
            }
        )
    elif name == "ampliado":
        p.update(
            {
                "use_obstacles": True,
                "use_seasons": True,
                "use_disease": True,
                "use_migration": True,
                "use_genetics": False,
            }
        )
    elif name == "evolutivo":
        p.update(
            {
                "use_obstacles": True,
                "use_seasons": True,
                "use_disease": True,
                "use_migration": True,
                "use_genetics": True,
            }
        )
    return p


# FUNÇÕES AUXILIARES DO MODELO
def get_season(tick: int, params: Dict) -> str:
    if not params.get("use_seasons", True):
        return "sem estação"
    seasons = ["primavera", "verao", "outono", "inverno"]
    # tick começa em 1; usamos tick-1 para cada estação ter exatamente season_length passos
    idx = ((max(1, int(tick)) - 1) // max(1, int(params["season_length"]))) % len(seasons)
    return seasons[idx]


def current_grass_growth_rate(tick: int, params: Dict) -> float:
    if not params.get("use_seasons", True):
        return float(params["grass_regrowth_base"])
    season = get_season(tick, params)
    multiplier = params["season_growth_multipliers"].get(season, 1.0)
    return float(params["grass_regrowth_base"]) * float(multiplier)


def toroidal_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int], width: int, height: int) -> float:
    dx = abs(pos_a[0] - pos_b[0])
    dy = abs(pos_a[1] - pos_b[1])
    dx = min(dx, width - dx)
    dy = min(dy, height - dy)
    return math.sqrt(dx * dx + dy * dy)


def make_random_genome(genes: List[str], dominant_prob: float = 0.5) -> Dict[str, Tuple[str, str]]:
    genome = {}
    for gene in genes:
        dom, rec = ALLELES[gene]
        a1 = dom if random.random() < dominant_prob else rec
        a2 = dom if random.random() < dominant_prob else rec
        genome[gene] = (a1, a2)
    return genome


def inherit_genome(parent_a: Dict, parent_b: Dict, mutation_rate: float = 0.01) -> Dict[str, Tuple[str, str]]:
    child = {}
    for gene in parent_a.keys():
        allele_a = random.choice(parent_a[gene])
        allele_b = random.choice(parent_b[gene])

        if random.random() < mutation_rate:
            allele_a = ALLELES[gene][1] if allele_a == ALLELES[gene][0] else ALLELES[gene][0]
        if random.random() < mutation_rate:
            allele_b = ALLELES[gene][1] if allele_b == ALLELES[gene][0] else ALLELES[gene][0]

        child[gene] = (allele_a, allele_b)
    return child


def dominant_count(genome: Dict, gene: str) -> int:
    dom = ALLELES[gene][0]
    return sum(1 for a in genome[gene] if a == dom)


def allele_frequency(agents: List, gene: str, dominant: bool = True) -> float:
    if not agents:
        return 0.0
    target = ALLELES[gene][0] if dominant else ALLELES[gene][1]
    total = 0
    count = 0
    for a in agents:
        if hasattr(a, "genome") and gene in a.genome:
            total += 2
            count += sum(1 for allele in a.genome[gene] if allele == target)
    return count / total if total > 0 else 0.0


def random_free_position(obstacles: np.ndarray, prefer_edge: bool = False, edge_bias: float = 0.75) -> Tuple[int, int]:
    height, width = obstacles.shape
    for _ in range(2000):
        if prefer_edge and random.random() < edge_bias:
            side = random.choice(["left", "right", "bottom", "top"])
            if side == "left":
                x, y = 0, random.randrange(height)
            elif side == "right":
                x, y = width - 1, random.randrange(height)
            elif side == "bottom":
                x, y = random.randrange(width), 0
            else:
                x, y = random.randrange(width), height - 1
        else:
            x, y = random.randrange(width), random.randrange(height)

        if not obstacles[y, x]:
            return x, y

    free_y, free_x = np.where(~obstacles)
    idx = random.randrange(len(free_x))
    return int(free_x[idx]), int(free_y[idx])


def candidate_moves(x: int, y: int, width: int, height: int, obstacles: np.ndarray) -> List[Tuple[int, int]]:
    candidates = [(x, y)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % width
            ny = (y + dy) % height
            if not obstacles[ny, nx]:
                candidates.append((nx, ny))
    return candidates


def step_toward(src: Tuple[int, int], dst: Tuple[int, int], width: int, height: int) -> Tuple[int, int]:
    sx, sy = src
    dx_raw = dst[0] - sx
    dy_raw = dst[1] - sy

    if abs(dx_raw) > width / 2:
        dx_raw = -math.copysign(width - abs(dx_raw), dx_raw)
    if abs(dy_raw) > height / 2:
        dy_raw = -math.copysign(height - abs(dy_raw), dy_raw)

    step_x = 0 if dx_raw == 0 else int(math.copysign(1, dx_raw))
    step_y = 0 if dy_raw == 0 else int(math.copysign(1, dy_raw))

    return (sx + step_x) % width, (sy + step_y) % height


# AGENTES
@dataclass
class Sheep:
    unique_id: int
    x: int
    y: int
    energy: float
    genome: Dict[str, Tuple[str, str]]
    params: Dict
    age: int = 0
    hunger: int = 0
    sick: bool = False
    kind: str = "sheep"

    def phenotype(self) -> Dict[str, float]:
        if not self.params.get("use_genetics", True):
            return {"vision": self.params["default_sheep_vision"], "escape": 0.5, "resistance": 0.5, "fertility": 0.5}

        vision = 3 + dominant_count(self.genome, "V") * 0.8
        escape = 0.25 + dominant_count(self.genome, "S") * 0.35
        resistance = 0.25 + dominant_count(self.genome, "R") * 0.35
        fertility = 0.25 + dominant_count(self.genome, "F") * 0.35
        return {"vision": vision, "escape": escape, "resistance": resistance, "fertility": fertility}


@dataclass
class Wolf:
    unique_id: int
    x: int
    y: int
    energy: float
    genome: Dict[str, Tuple[str, str]]
    params: Dict
    age: int = 0
    hunger: int = 0
    sick: bool = False
    kind: str = "wolf"

    def phenotype(self) -> Dict[str, float]:
        if not self.params.get("use_genetics", True):
            return {"vision": self.params["default_wolf_vision"], "hunting": 0.5, "resistance": 0.5, "fertility": 0.5}

        vision = 4 + dominant_count(self.genome, "V") * 0.8
        hunting = 0.25 + dominant_count(self.genome, "H") * 0.35
        resistance = 0.25 + dominant_count(self.genome, "R") * 0.35
        fertility = 0.25 + dominant_count(self.genome, "F") * 0.35
        return {"vision": vision, "hunting": hunting, "resistance": resistance, "fertility": fertility}


# MOTOR DA SIMULAÇÃO ESPACIAL
def make_snapshot(tick: int, grass: np.ndarray, obstacles: np.ndarray, sheep: List[Sheep], wolves: List[Wolf], params: Dict) -> Dict:
    return {
        "tick": int(tick),
        "season": get_season(tick, params),
        "grass": grass.astype(np.float32).copy(),
        "obstacles": obstacles.copy(),
        "sheep": [(int(s.x), int(s.y), bool(s.sick), float(s.energy)) for s in sheep],
        "wolves": [(int(w.x), int(w.y), bool(w.sick), float(w.energy)) for w in wolves],
    }


def run_simulation(params: Dict) -> Tuple[pd.DataFrame, List[Dict]]:
    """Executa a simulação espacial e retorna histórico + quadros para visualização NetLogo."""

    random.seed(int(params["random_seed"]))
    np.random.seed(int(params["random_seed"]))

    width = int(params["width"])
    height = int(params["height"])

    # Obstáculos como patches bloqueados.
    if params.get("use_obstacles", True):
        obstacles = np.random.random((height, width)) < float(params["obstacle_density"])
    else:
        obstacles = np.zeros((height, width), dtype=bool)

    # Garante pelo menos algumas células livres.
    if np.mean(~obstacles) < 0.2:
        obstacles[:] = False

    grass = np.random.uniform(0.20 * params["grass_max"], params["grass_max"], size=(height, width)).astype(float)
    grass[obstacles] = 0.0

    next_id = 1
    sheep: List[Sheep] = []
    wolves: List[Wolf] = []

    for _ in range(int(params["initial_sheep"])):
        x, y = random_free_position(obstacles)
        agent = Sheep(
            next_id,
            x,
            y,
            float(params["initial_sheep_energy"]),
            make_random_genome(SHEEP_GENES),
            params,
            sick=params.get("use_disease", True) and random.random() < float(params["initial_disease_prob"]),
        )
        sheep.append(agent)
        next_id += 1

    for _ in range(int(params["initial_wolves"])):
        x, y = random_free_position(obstacles)
        agent = Wolf(
            next_id,
            x,
            y,
            float(params["initial_wolf_energy"]),
            make_random_genome(WOLF_GENES),
            params,
            sick=params.get("use_disease", True) and random.random() < float(params["initial_disease_prob"]),
        )
        wolves.append(agent)
        next_id += 1

    history = []
    frames = [make_snapshot(0, grass, obstacles, sheep, wolves, params)]

    progress_bar = st.progress(0)
    status_text = st.empty()

    live_enabled = bool(params.get("live_preview", True))
    live_world_placeholder = None
    live_chart_placeholder = None
    live_info_placeholder = None
    if live_enabled:
        st.markdown("### 🎥 Visualização ao vivo da simulação")
        st.caption("A cada atualização, o mapa espacial e o gráfico populacional são redesenhados enquanto a simulação roda.")
        live_col1, live_col2 = st.columns([1.15, 1])
        with live_col1:
            live_world_placeholder = st.empty()
        with live_col2:
            live_chart_placeholder = st.empty()
            live_info_placeholder = st.empty()
        initial_fig = netlogo_world_figure(frames[0], params)
        live_world_placeholder.pyplot(initial_fig, clear_figure=True)
        plt.close(initial_fig)

    for tick in range(1, int(params["n_steps"]) + 1):
        progress_bar.progress(tick / max(1, int(params["n_steps"])))
        status_text.markdown(f"**Simulando...** passo {tick}/{params['n_steps']} · estação: `{get_season(tick, params)}`")

        # Crescimento da grama.
        growth_rate = current_grass_growth_rate(tick, params)
        grass = np.minimum(grass + growth_rate, float(params["grass_max"]))
        grass[obstacles] = 0.0

        # Movimento e alimentação das ovelhas.
        random.shuffle(sheep)
        for s in sheep:
            ph = s.phenotype()
            vision = ph["vision"]
            pos = (s.x, s.y)
            nearby_wolves = [w for w in wolves if toroidal_distance(pos, (w.x, w.y), width, height) <= vision]
            moves = candidate_moves(s.x, s.y, width, height, obstacles)

            if nearby_wolves:
                # Fuga: escolhe o patch que maximiza a distância dos lobos próximos.
                def sheep_score(move):
                    min_d = min(toroidal_distance(move, (w.x, w.y), width, height) for w in nearby_wolves)
                    return min_d * (1 + ph["escape"]) + 0.08 * grass[move[1], move[0]] + random.random() * 0.02

                s.x, s.y = max(moves, key=sheep_score)
            else:
                # Sem predador visível: busca grama local.
                s.x, s.y = max(moves, key=lambda m: grass[m[1], m[0]] + random.random() * 0.05)

            available_grass = grass[s.y, s.x]
            if available_grass > 0.5:
                eaten = min(available_grass, 1.0 + ph["fertility"] * 0.35)
                s.energy += float(params["energy_gain_from_grass"]) * (eaten / max(0.1, float(params["grass_max"]))) * 2.0
                grass[s.y, s.x] = max(0.0, available_grass - eaten)
                s.hunger = 0
            else:
                s.hunger += 1

            s.energy -= float(params["sheep_movement_cost"])
            s.age += 1

        # Movimento e caça dos lobos.
        random.shuffle(wolves)
        eaten_ids = set()
        eaten_count = 0
        for w in wolves:
            ph = w.phenotype()
            pos = (w.x, w.y)
            visible_sheep = [s for s in sheep if s.unique_id not in eaten_ids and toroidal_distance(pos, (s.x, s.y), width, height) <= ph["vision"]]
            moves = candidate_moves(w.x, w.y, width, height, obstacles)

            if visible_sheep:
                target = min(visible_sheep, key=lambda s: toroidal_distance(pos, (s.x, s.y), width, height))
                preferred = step_toward((w.x, w.y), (target.x, target.y), width, height)
                if preferred in moves:
                    w.x, w.y = preferred
                else:
                    w.x, w.y = min(moves, key=lambda m: toroidal_distance(m, (target.x, target.y), width, height))
            else:
                w.x, w.y = random.choice(moves)

            # Caça no mesmo patch.
            local_sheep = [s for s in sheep if s.unique_id not in eaten_ids and s.x == w.x and s.y == w.y]
            if local_sheep:
                hunt_prob = min(0.95, 0.35 + 0.55 * ph["hunting"])
                victim = random.choice(local_sheep)
                victim_escape = victim.phenotype().get("escape", 0.5)
                effective_prob = max(0.05, hunt_prob - 0.22 * victim_escape)
                if random.random() < effective_prob:
                    eaten_ids.add(victim.unique_id)
                    w.energy += float(params["energy_gain_from_sheep"])
                    w.hunger = 0
                    eaten_count += 1
                else:
                    w.hunger += 1
            else:
                w.hunger += 1

            w.energy -= float(params["wolf_movement_cost"])
            w.age += 1

        if eaten_ids:
            sheep = [s for s in sheep if s.unique_id not in eaten_ids]

        # Doenças: custo, recuperação, morte e contágio por vizinhança.
        disease_deaths = 0
        if params.get("use_disease", True):
            all_agents = sheep + wolves
            sick_agents = [a for a in all_agents if a.sick]

            for a in all_agents:
                ph = a.phenotype()
                resistance = ph.get("resistance", 0.5)

                if a.sick:
                    a.energy -= float(params["disease_energy_cost"]) * (1.0 - 0.45 * resistance)
                    if random.random() < float(params["disease_recovery_prob"]) * (0.75 + resistance):
                        a.sick = False
                    elif random.random() < float(params["disease_death_prob"]) * (1.1 - resistance):
                        a.energy = -999.0
                        disease_deaths += 1
                elif sick_agents:
                    close_sick = any(
                        toroidal_distance((a.x, a.y), (b.x, b.y), width, height) <= 1.5 for b in sick_agents if b is not a
                    )
                    if close_sick:
                        infection_prob = float(params["disease_spread_prob"]) * (1.05 - resistance)
                        if random.random() < infection_prob:
                            a.sick = True
        else:
            disease_deaths = 0

        # Mortalidade por energia, fome e idade.
        sheep = [
            s
            for s in sheep
            if s.energy > 0 and s.age <= int(params["max_age_sheep"]) and s.hunger <= int(params["max_hunger_sheep"])
        ]
        wolves = [
            w
            for w in wolves
            if w.energy > 0 and w.age <= int(params["max_age_wolf"]) and w.hunger <= int(params["max_hunger_wolf"])
        ]

        # Reprodução por energia e proximidade.
        sheep_births = 0
        new_sheep: List[Sheep] = []
        if len(sheep) > 1:
            fertile_sheep = [s for s in sheep if s.energy > float(params["sheep_reproduction_energy_threshold"])]
            for s in fertile_sheep:
                if len(sheep) + len(new_sheep) >= 900:
                    break
                ph = s.phenotype()
                repro_prob = float(params["base_sheep_reproduction_prob"]) * (0.65 + ph["fertility"])
                if random.random() < repro_prob:
                    partners = [p for p in sheep if p.unique_id != s.unique_id and toroidal_distance((s.x, s.y), (p.x, p.y), width, height) <= 2.0]
                    if partners:
                        parent2 = random.choice(partners)
                        genome = inherit_genome(s.genome, parent2.genome, float(params["mutation_rate"]))
                        x, y = random.choice(candidate_moves(s.x, s.y, width, height, obstacles))
                        child_energy = float(params["offspring_energy_fraction"]) * s.energy
                        s.energy *= 1 - float(params["offspring_energy_fraction"])
                        new_sheep.append(Sheep(next_id, x, y, child_energy, genome, params, sick=False))
                        next_id += 1
                        sheep_births += 1
            sheep.extend(new_sheep)

        wolf_births = 0
        new_wolves: List[Wolf] = []
        if len(wolves) > 1:
            fertile_wolves = [w for w in wolves if w.energy > float(params["wolf_reproduction_energy_threshold"])]
            for w in fertile_wolves:
                if len(wolves) + len(new_wolves) >= 300:
                    break
                ph = w.phenotype()
                repro_prob = float(params["base_wolf_reproduction_prob"]) * (0.65 + ph["fertility"])
                if random.random() < repro_prob:
                    partners = [p for p in wolves if p.unique_id != w.unique_id and toroidal_distance((w.x, w.y), (p.x, p.y), width, height) <= 2.5]
                    if partners:
                        parent2 = random.choice(partners)
                        genome = inherit_genome(w.genome, parent2.genome, float(params["mutation_rate"]))
                        x, y = random.choice(candidate_moves(w.x, w.y, width, height, obstacles))
                        child_energy = float(params["offspring_energy_fraction"]) * w.energy
                        w.energy *= 1 - float(params["offspring_energy_fraction"])
                        new_wolves.append(Wolf(next_id, x, y, child_energy, genome, params, sick=False))
                        next_id += 1
                        wolf_births += 1
            wolves.extend(new_wolves)

        # Migração: entrada de agentes pelas bordas.
        migrants = 0
        if params.get("use_migration", True) and random.random() < float(params["migration_prob"]):
            if random.random() < 0.65 and len(sheep) < 900:
                x, y = random_free_position(obstacles, prefer_edge=True, edge_bias=float(params["migration_edge_bias"]))
                sheep.append(
                    Sheep(
                        next_id,
                        x,
                        y,
                        float(params["initial_sheep_energy"]),
                        make_random_genome(SHEEP_GENES),
                        params,
                        sick=params.get("use_disease", True) and random.random() < float(params["initial_disease_prob"]),
                    )
                )
                next_id += 1
                migrants += 1
            elif len(wolves) < 300:
                x, y = random_free_position(obstacles, prefer_edge=True, edge_bias=float(params["migration_edge_bias"]))
                wolves.append(
                    Wolf(
                        next_id,
                        x,
                        y,
                        float(params["initial_wolf_energy"]),
                        make_random_genome(WOLF_GENES),
                        params,
                        sick=params.get("use_disease", True) and random.random() < float(params["initial_disease_prob"]),
                    )
                )
                next_id += 1
                migrants += 1

        mean_sheep_energy = float(np.mean([s.energy for s in sheep])) if sheep else 0.0
        mean_wolf_energy = float(np.mean([w.energy for w in wolves])) if wolves else 0.0
        sick_sheep = sum(1 for s in sheep if s.sick)
        sick_wolves = sum(1 for w in wolves if w.sick)

        record = {
            "tick": tick,
            "season": get_season(tick, params),
            "sheep": len(sheep),
            "wolves": len(wolves),
            "sick_sheep": sick_sheep,
            "sick_wolves": sick_wolves,
            "eaten_sheep": eaten_count,
            "sheep_births": sheep_births,
            "wolf_births": wolf_births,
            "disease_deaths": disease_deaths,
            "migrants": migrants,
            "mean_grass": float(np.mean(grass[~obstacles])) if np.any(~obstacles) else 0.0,
            "grass_growth_rate": growth_rate,
            "mean_sheep_energy": mean_sheep_energy,
            "mean_wolf_energy": mean_wolf_energy,
            "sheep_freq_S": allele_frequency(sheep, "S", dominant=True) if sheep else 0.0,
            "sheep_freq_R": allele_frequency(sheep, "R", dominant=True) if sheep else 0.0,
            "wolf_freq_H": allele_frequency(wolves, "H", dominant=True) if wolves else 0.0,
            "wolf_freq_R": allele_frequency(wolves, "R", dominant=True) if wolves else 0.0,
        }
        history.append(record)

        saved_snapshot = None
        if tick % int(params["frame_interval"]) == 0 or tick == int(params["n_steps"]):
            saved_snapshot = make_snapshot(tick, grass, obstacles, sheep, wolves, params)
            frames.append(saved_snapshot)

        update_interval = max(1, int(params.get("live_update_interval", params.get("frame_interval", 5))))
        if live_enabled and (tick == 1 or tick % update_interval == 0 or tick == int(params["n_steps"])):
            preview_snapshot = saved_snapshot if saved_snapshot is not None else make_snapshot(tick, grass, obstacles, sheep, wolves, params)
            fig_world = netlogo_world_figure(preview_snapshot, params)
            live_world_placeholder.pyplot(fig_world, clear_figure=True)
            plt.close(fig_world)

            live_df = pd.DataFrame(history)
            fig_pop = timeseries_figure(live_df, ["sheep", "wolves"], "População durante a execução", "Agentes")
            live_chart_placeholder.pyplot(fig_pop, clear_figure=True)
            plt.close(fig_pop)

            if live_info_placeholder is not None:
                live_info_placeholder.markdown(
                    f"**Passo:** {tick}  |  **Ovelhas:** {len(sheep)}  |  **Lobos:** {len(wolves)}  |  **Estação:** `{get_season(tick, params)}`"
                )

        if (len(sheep) == 0 or len(wolves) == 0) and bool(params.get("stop_on_extinction", False)):
            frames.append(make_snapshot(tick, grass, obstacles, sheep, wolves, params))
            break

    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(history), frames


# VISUALIZAÇÃO
def netlogo_world_figure(snapshot: Dict, params: Dict):
    """Renderiza o mundo espacial em Matplotlib, no estilo NetLogo.

    Esta função usa imagem estática para evitar falhas de renderização Plotly em alguns
    proxies/JupyterHub/Streamlit. O resultado aparece como figura normal do Streamlit.
    """
    grass = snapshot["grass"]
    obstacles = snapshot["obstacles"]
    height, width = grass.shape
    marker_size = int(params.get("agent_marker_size", 9))

    # Colormap escuro -> verde claro para parecer patches do NetLogo.
    cmap = LinearSegmentedColormap.from_list(
        "netlogo_grass",
        ["#06110c", "#0d2618", "#184c25", "#3d8d38", "#8bd94d"],
        N=256,
    )

    fig_w = 9.2
    fig_h = 9.2 * (height / max(width, 1))
    fig_h = min(8.5, max(5.2, fig_h))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=130)
    fig.patch.set_facecolor("#061817")
    ax.set_facecolor("#061817")

    ax.imshow(
        grass,
        origin="lower",
        vmin=0,
        vmax=float(params["grass_max"]),
        cmap=cmap,
        interpolation="nearest",
    )

    oy, ox = np.where(obstacles)
    if len(ox) > 0:
        ax.scatter(
            ox,
            oy,
            marker="s",
            s=(marker_size + 2) ** 2,
            c="#242832",
            edgecolors="#666f7a",
            linewidths=0.45,
            label="Obstáculos",
            zorder=3,
        )

    sheep = snapshot["sheep"]
    sheep_ok = [(x, y, e) for x, y, sick, e in sheep if not sick]
    sheep_sick = [(x, y, e) for x, y, sick, e in sheep if sick]
    wolves = snapshot["wolves"]
    wolves_ok = [(x, y, e) for x, y, sick, e in wolves if not sick]
    wolves_sick = [(x, y, e) for x, y, sick, e in wolves if sick]

    if sheep_ok:
        ax.scatter(
            [a[0] for a in sheep_ok],
            [a[1] for a in sheep_ok],
            s=(marker_size * 1.15) ** 2,
            c="#f8f7ed",
            edgecolors="#173a26",
            linewidths=0.55,
            marker="o",
            label="Ovelhas",
            zorder=5,
        )
    if sheep_sick:
        ax.scatter(
            [a[0] for a in sheep_sick],
            [a[1] for a in sheep_sick],
            s=(marker_size * 1.25) ** 2,
            c="#fff0a8",
            edgecolors="#ffb000",
            linewidths=0.85,
            marker="o",
            label="Ovelhas doentes",
            zorder=6,
        )
    if wolves_ok:
        ax.scatter(
            [a[0] for a in wolves_ok],
            [a[1] for a in wolves_ok],
            s=(marker_size * 1.45) ** 2,
            c="#ff4d4d",
            edgecolors="#260707",
            linewidths=0.65,
            marker="^",
            label="Lobos",
            zorder=7,
        )
    if wolves_sick:
        ax.scatter(
            [a[0] for a in wolves_sick],
            [a[1] for a in wolves_sick],
            s=(marker_size * 1.55) ** 2,
            c="#ff9b54",
            edgecolors="#ffdc73",
            linewidths=0.85,
            marker="^",
            label="Lobos doentes",
            zorder=8,
        )

    if params.get("show_grid_lines", True) and width <= 70 and height <= 70:
        ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
        ax.grid(which="minor", color="white", alpha=0.08, linewidth=0.35)

    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#1c4941")
        spine.set_linewidth(1.2)

    title = f"Mundo espacial estilo NetLogo — tick {snapshot['tick']} · {snapshot['season']}"
    ax.set_title(title, color="#f3fff8", fontsize=14, fontweight="bold", pad=10)
    if ax.get_legend_handles_labels()[0]:
        leg = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.035),
            ncol=4,
            fontsize=9,
            frameon=True,
            facecolor="#08211f",
            edgecolor="#2d6f65",
        )
        for text in leg.get_texts():
            text.set_color("#f3fff8")

    plt.tight_layout()
    return fig


def timeseries_figure(df: pd.DataFrame, y_cols: List[str], title: str, y_title: str):
    labels = {
        "sheep": "Ovelhas",
        "wolves": "Lobos",
        "mean_grass": "Grama média",
        "mean_sheep_energy": "Energia média das ovelhas",
        "mean_wolf_energy": "Energia média dos lobos",
        "sheep_freq_S": "Fuga S — ovelhas",
        "sheep_freq_R": "Resistência R — ovelhas",
        "wolf_freq_H": "Caça H — lobos",
        "wolf_freq_R": "Resistência R — lobos",
        "eaten_sheep": "Ovelhas predadas",
        "sheep_births": "Nascimentos de ovelhas",
        "wolf_births": "Nascimentos de lobos",
        "sick_sheep": "Ovelhas doentes",
        "sick_wolves": "Lobos doentes",
        "grass_growth_rate": "Crescimento da grama",
        "migrants": "Migrantes",
        "disease_deaths": "Mortes por doença",
    }
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=130)
    fig.patch.set_facecolor("#061817")
    ax.set_facecolor("#061817")
    for col in y_cols:
        if col in df.columns:
            ax.plot(df["tick"], df[col], linewidth=2.3, label=labels.get(col, col))
    ax.set_title(title, color="#f3fff8", fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Tick", color="#d7eee7")
    ax.set_ylabel(y_title, color="#d7eee7")
    ax.tick_params(colors="#d7eee7", labelsize=9)
    ax.grid(True, alpha=0.18, color="white", linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_color("#1c4941")
    if len(y_cols) > 1:
        leg = ax.legend(frameon=True, facecolor="#08211f", edgecolor="#2d6f65", fontsize=9)
        for text in leg.get_texts():
            text.set_color("#f3fff8")
    plt.tight_layout()
    return fig


def line_chart(df: pd.DataFrame, y_cols: List[str], title: str, y_title: str):
    fig = timeseries_figure(df, y_cols, title, y_title)
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def bar_chart_last_values(df: pd.DataFrame):
    last = df.iloc[-1]
    values = pd.DataFrame(
        {
            "Indicador": ["Ovelhas", "Lobos", "Ovelhas doentes", "Lobos doentes", "Grama média"],
            "Valor": [last["sheep"], last["wolves"], last["sick_sheep"], last["sick_wolves"], last["mean_grass"]],
        }
    )
    fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=130)
    fig.patch.set_facecolor("#061817")
    ax.set_facecolor("#061817")
    bars = ax.bar(values["Indicador"], values["Valor"])
    ax.set_title("Estado final da simulação", color="#f3fff8", fontsize=13, fontweight="bold", pad=10)
    ax.tick_params(axis="x", colors="#d7eee7", rotation=12, labelsize=9)
    ax.tick_params(axis="y", colors="#d7eee7", labelsize=9)
    ax.grid(True, axis="y", alpha=0.18, color="white", linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_color("#1c4941")
    for bar, value in zip(bars, values["Valor"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.1f}", ha="center", va="bottom", color="#f3fff8", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def metric_card(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# SIDEBAR — PARÂMETROS AJUSTÁVEIS
st.sidebar.header("⚙️ Parâmetros ajustáveis")

scenario_choice = st.sidebar.selectbox(
    "Cenário predefinido",
    ["Personalizado", "Base (sem recursos)", "Ampliado (com estações e obstáculos)", "Evolutivo (completo)"],
    help="Escolha um cenário inicial e depois ajuste os controles livremente.",
)

scenario_key = {
    "Base (sem recursos)": "base",
    "Ampliado (com estações e obstáculos)": "ampliado",
    "Evolutivo (completo)": "evolutivo",
}.get(scenario_choice, "personalizado")

if "params" not in st.session_state:
    st.session_state.params = scenario_params("evolutivo")
    st.session_state.last_scenario_key = "evolutivo"

if scenario_key != "personalizado" and scenario_key != st.session_state.get("last_scenario_key"):
    st.session_state.params = scenario_params(scenario_key)
    st.session_state.last_scenario_key = scenario_key
elif scenario_key == "personalizado":
    st.session_state.last_scenario_key = "personalizado"

params = st.session_state.params

with st.sidebar.expander("🌍 Ambiente espacial", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        params["width"] = st.slider("Largura", 25, 80, int(params["width"]), 5)
        params["grass_max"] = st.slider("Máx. grama", 5.0, 20.0, float(params["grass_max"]), 0.5)
    with col2:
        params["height"] = st.slider("Altura", 25, 80, int(params["height"]), 5)
        params["grass_regrowth_base"] = st.slider("Crescimento", 0.05, 1.20, float(params["grass_regrowth_base"]), 0.05)

with st.sidebar.expander("👥 Populações", expanded=True):
    params["initial_sheep"] = st.slider("Ovelhas iniciais", 20, 500, int(params["initial_sheep"]), 10)
    params["initial_wolves"] = st.slider("Lobos iniciais", 5, 160, int(params["initial_wolves"]), 5)

with st.sidebar.expander("⚡ Energia e sobrevivência", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["initial_sheep_energy"] = st.slider("Energia inicial ovelha", 5.0, 70.0, float(params["initial_sheep_energy"]), 1.0)
        params["sheep_movement_cost"] = st.slider("Custo mov. ovelha", 0.1, 4.0, float(params["sheep_movement_cost"]), 0.1)
        params["max_hunger_sheep"] = st.slider("Fome máx. ovelha", 5, 50, int(params["max_hunger_sheep"]), 1)
        params["max_age_sheep"] = st.slider("Idade máx. ovelha", 30, 200, int(params["max_age_sheep"]), 5)
    with col2:
        params["initial_wolf_energy"] = st.slider("Energia inicial lobo", 10.0, 90.0, float(params["initial_wolf_energy"]), 1.0)
        params["wolf_movement_cost"] = st.slider("Custo mov. lobo", 0.1, 4.0, float(params["wolf_movement_cost"]), 0.1)
        params["max_hunger_wolf"] = st.slider("Fome máx. lobo", 5, 60, int(params["max_hunger_wolf"]), 1)
        params["max_age_wolf"] = st.slider("Idade máx. lobo", 40, 250, int(params["max_age_wolf"]), 5)

with st.sidebar.expander("🔄 Reprodução", expanded=False):
    params["base_sheep_reproduction_prob"] = st.slider("Prob. reprodução ovelha", 0.0, 0.20, float(params["base_sheep_reproduction_prob"]), 0.005)
    params["base_wolf_reproduction_prob"] = st.slider("Prob. reprodução lobo", 0.0, 0.15, float(params["base_wolf_reproduction_prob"]), 0.005)
    params["sheep_reproduction_energy_threshold"] = st.slider("Energia mínima ovelha", 10.0, 90.0, float(params["sheep_reproduction_energy_threshold"]), 1.0)
    params["wolf_reproduction_energy_threshold"] = st.slider("Energia mínima lobo", 15.0, 110.0, float(params["wolf_reproduction_energy_threshold"]), 1.0)
    params["offspring_energy_fraction"] = st.slider("Energia passada ao filhote", 0.10, 0.80, float(params["offspring_energy_fraction"]), 0.05)

with st.sidebar.expander("🧬 Genética e migração", expanded=False):
    params["use_genetics"] = st.checkbox("Ativar genética mendeliana", bool(params["use_genetics"]))
    params["mutation_rate"] = st.slider("Taxa de mutação", 0.0, 0.15, float(params["mutation_rate"]), 0.005)
    params["use_migration"] = st.checkbox("Ativar migração", bool(params["use_migration"]))
    params["migration_prob"] = st.slider("Prob. migração por tick", 0.0, 0.10, float(params["migration_prob"]), 0.005)

with st.sidebar.expander("🌦️ Estações, obstáculos e doença", expanded=False):
    params["use_seasons"] = st.checkbox("Ativar estações", bool(params["use_seasons"]))
    params["season_length"] = st.slider("Duração da estação", 10, 120, int(params["season_length"]), 5)
    params["use_obstacles"] = st.checkbox("Ativar obstáculos", bool(params["use_obstacles"]))
    params["obstacle_density"] = st.slider("Densidade de obstáculos", 0.0, 0.30, float(params["obstacle_density"]), 0.01)
    params["use_disease"] = st.checkbox("Ativar doenças", bool(params["use_disease"]))
    params["initial_disease_prob"] = st.slider("Doença inicial", 0.0, 0.20, float(params["initial_disease_prob"]), 0.005)
    params["disease_spread_prob"] = st.slider("Contágio", 0.0, 0.30, float(params["disease_spread_prob"]), 0.005)
    params["disease_death_prob"] = st.slider("Morte por doença", 0.0, 0.10, float(params["disease_death_prob"]), 0.005)

with st.sidebar.expander("🎬 Execução e visualização", expanded=True):
    params["n_steps"] = st.slider("Número de passos", 20, 700, int(params["n_steps"]), 20)
    passos_4_estacoes = int(params.get("season_length", 50)) * 4
    if bool(params.get("use_seasons", True)):
        st.caption(f"Para passar pelas 4 estações: use pelo menos {passos_4_estacoes} passos.")
        if int(params["n_steps"]) < passos_4_estacoes:
            st.warning(f"Com a duração atual, {params['n_steps']} passos não completam as 4 estações. Use {passos_4_estacoes} ou reduza a duração da estação.")
    params["stop_on_extinction"] = st.checkbox("Parar se ovelhas ou lobos forem extintos", bool(params.get("stop_on_extinction", False)))
    params["frame_interval"] = st.slider("Salvar quadro a cada N passos", 1, 25, int(params["frame_interval"]), 1)
    params["agent_marker_size"] = st.slider("Tamanho dos agentes", 5, 18, int(params["agent_marker_size"]), 1)
    params["show_grid_lines"] = st.checkbox("Mostrar grade dos patches", bool(params["show_grid_lines"]))
    params["live_preview"] = st.checkbox("Mostrar simulação ao vivo durante execução", bool(params.get("live_preview", True)))
    params["live_update_interval"] = st.slider("Atualizar tela a cada N passos", 1, 25, int(params.get("live_update_interval", 5)), 1)
    params["random_seed"] = int(st.number_input("Semente da simulação", 0, 999999, int(params["random_seed"])))

st.sidebar.markdown("---")
run_clicked = st.sidebar.button("🚀 EXECUTAR SIMULAÇÃO", use_container_width=True, type="primary")
clear_clicked = st.sidebar.button("🧹 Limpar resultados", use_container_width=True)

if clear_clicked:
    st.session_state.pop("df_result", None)
    st.session_state.pop("frames", None)
    st.session_state.pop("last_params", None)
    st.rerun()

if run_clicked:
    df_result, frames = run_simulation(copy.deepcopy(params))
    st.session_state.df_result = df_result
    st.session_state.frames = frames
    st.session_state.last_params = copy.deepcopy(params)


# PAINEL PRINCIPAL
if "df_result" not in st.session_state or st.session_state.df_result.empty:
    st.info("👈 Ajuste os parâmetros na barra lateral e clique em **EXECUTAR SIMULAÇÃO**.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🟩 Patches")
        st.write("Cada célula representa uma porção do ambiente. A cor verde indica a quantidade de grama disponível.")
    with c2:
        st.markdown("### 🐑🐺 Agentes")
        st.write("Ovelhas fogem, comem grama e reproduzem. Lobos perseguem, caçam e também reproduzem.")
    with c3:
        st.markdown("### 🧬 Evolução")
        st.write("Genes alteram visão, fuga, caça, resistência e fertilidade. Mutação e seleção mudam frequências alélicas.")
    st.info("Este painel representa um **ecossistema evolutivo artificial**")
    st.markdown(
        """           
        - **Patches espaciais:** cada célula contém grama e pode conter obstáculos.
        - **Ovelhas:** comem grama, fogem de lobos, gastam energia e reproduzem.
        - **Lobos:** procuram ovelhas, caçam, gastam energia e reproduzem.
        - **Mundo toroidal:** sair por uma borda equivale a entrar pela borda oposta.
        - **Genética:** genes controlam visão, fuga, caça, resistência e fertilidade.
        - **Ambiente dinâmico:** estações alteram crescimento da grama; doenças e migração mudam a composição populacional.
    
        Relações científicas incorporadas:
    
        - **Lotka-Volterra:** dinâmica predador-presa.
        - **Mendel:** herança e recombinação genética.
        - **Darwin:** seleção natural por sobrevivência e reprodução diferencial.
        - **Sistemas complexos:** emergência, auto-organização, feedback e coevolução.
        
        #### Relação com os autores da literatura de sistemas complexos

        - **Joshua M. Epstein e Robert Axtell** ajudam a interpretar o modelo como uma sociedade artificial construída de baixo para cima (bottom-up), na qual padrões globais emergem das regras locais dos agentes. No Wolf Sheep, não há um controlador central: o comportamento coletivo surge das interações entre grama, ovelhas e lobos.
       
        - **W. Brian Arthu** contribui com a ideia de feedback positivo, dependência histórica (path dependence) e trajetórias que se reforçam ao longo do tempo. No modelo, uma sequência inicial de abundância ou escassez pode direcionar todo o futuro do sistema, favorecendo estabilidade, crescimento ou colapso.
       
        - **Stuart A. Kauffman** aparece na ideia de auto-organização e ordem emergente em sistemas vivos. Mesmo sem planejamento global, o ecossistema pode formar padrões relativamente estáveis, ciclos populacionais ou reorganizações após perturbações.
       
        - **Melanie Mitchell** ajuda a compreender a complexidade como resultado da interação entre adaptação, emergência, evolução e múltiplos níveis de organização. No modelo, regras individuais simples produzem comportamentos coletivos complexos ao longo do tempo.
        
        - **Ilya Prigogine e Grégoire Nicolis** se relacionam com o fato de o ecossistema estar fora do equilíbrio. O sistema se reorganiza continuamente diante de fluxos de energia, escassez, morte, reprodução, doença, migração e perturbações ambientais.
       
        - **Albert-László Barabási e Steven H. Strogatz** ajudam a ler o modelo como uma rede dinâmica de interações: quem caça quem, quem compete por recurso, quem transmite doença, quem se reproduz com quem e como os agentes se distribuem no espaço.
        
        """
    )
else:
    df = st.session_state.df_result
    frames = st.session_state.frames
    last_params = st.session_state.last_params
    last = df.iloc[-1]

    st.markdown("---")
    st.subheader("📊 Resumo executivo")
    st.markdown('<p class="section-note">Indicadores finais e máximos observados durante a execução.</p>', unsafe_allow_html=True)

    if "season" in df.columns:
        ordem_estacoes = ["primavera", "verao", "outono", "inverno"]
        estacoes_visitadas = [e for e in ordem_estacoes if e in set(df["season"].astype(str))]
        if bool(last_params.get("use_seasons", True)) and len(estacoes_visitadas) < 4:
            st.warning("A simulação ainda não visitou as quatro estações. Aumente o número de passos, reduza a duração da estação ou desmarque 'Parar se ovelhas ou lobos forem extintos'.")
        st.caption("Estações visitadas: " + " → ".join(estacoes_visitadas if estacoes_visitadas else ["sem estação"]))

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        metric_card("Passos", f"{int(last['tick'])}", "tempo simulado")
    with m2:
        metric_card("Ovelhas finais", f"{int(last['sheep'])}", f"máx.: {int(df['sheep'].max())}")
    with m3:
        metric_card("Lobos finais", f"{int(last['wolves'])}", f"máx.: {int(df['wolves'].max())}")
    with m4:
        metric_card("Predações", f"{int(df['eaten_sheep'].sum())}", "ovelhas caçadas")
    with m5:
        metric_card("Nascimentos", f"{int(df['sheep_births'].sum() + df['wolf_births'].sum())}", "ovelhas + lobos")
    with m6:
        metric_card("Grama média", f"{last['mean_grass']:.1f}", f"estação: {last['season']}")

    tab_world, tab_dynamics, tab_genetics, tab_environment, tab_data, tab_model = st.tabs(
        ["🌍 Simulação NetLogo", "📈 Dinâmica", "🧬 Genética", "🌿 Ambiente", "📋 Dados", "📚 Modelo"]
    )

    with tab_world:
        st.subheader("🌍 Visualização espacial estilo NetLogo")
        st.markdown(
            '<p class="section-note">Verde = grama; quadrados escuros = obstáculos; círculos claros = ovelhas; triângulos vermelhos = lobos.</p>',
            unsafe_allow_html=True,
        )

        frame_ticks = [f["tick"] for f in frames]
        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
        with col_a:
            frame_idx = st.slider(
                "Passo visualizado",
                min_value=0,
                max_value=len(frames) - 1,
                value=len(frames) - 1,
                format="quadro %d",
                help="Use este controle como o slider temporal do NetLogo.",
            )
        snapshot = frames[frame_idx]
        with col_b:
            st.metric("Tick", snapshot["tick"])
        with col_c:
            st.metric("Ovelhas", len(snapshot["sheep"]))
        with col_d:
            st.metric("Lobos", len(snapshot["wolves"]))

        view_col1, view_col2 = st.columns([1.15, 1])
        with view_col1:
            fig_world = netlogo_world_figure(snapshot, last_params)
            st.pyplot(fig_world, clear_figure=True)
            plt.close(fig_world)
        with view_col2:
            line_chart(df, ["sheep", "wolves"], "Dinâmica populacional", "Agentes")
            line_chart(df, ["mean_grass"], "Grama média", "Recurso")

        with st.expander("▶️ Reproduzir animação dentro do Streamlit", expanded=False):
            speed = st.slider("Velocidade da animação", 0.02, 0.50, 0.10, 0.02)
            if st.button("Reproduzir quadros salvos", use_container_width=True):
                placeholder = st.empty()
                for f in frames:
                    fig_anim = netlogo_world_figure(f, last_params)
                    placeholder.pyplot(fig_anim, clear_figure=True)
                    plt.close(fig_anim)
                    time.sleep(speed)

        st.markdown(
            """
            **Leitura do mapa:** quando a grama diminui, as ovelhas perdem energia. Quando as ovelhas se concentram,
            os lobos encontram presas com mais facilidade. Obstáculos criam barreiras locais e podem formar ilhas de sobrevivência.
            """
        )

    with tab_dynamics:
        st.subheader("📈 Dinâmica predador-presa")
        c1, c2 = st.columns(2)
        with c1:
            line_chart(df, ["sheep", "wolves"], "Populações ao longo do tempo", "Quantidade de agentes")
        with c2:
            line_chart(df, ["mean_sheep_energy", "mean_wolf_energy"], "Energia média", "Energia")

        c3, c4 = st.columns(2)
        with c3:
            line_chart(df, ["eaten_sheep"], "Predação por tick", "Ovelhas predadas")
        with c4:
            line_chart(df, ["sheep_births", "wolf_births"], "Nascimentos por tick", "Nascimentos")

        bar_chart_last_values(df)

    with tab_genetics:
        st.subheader("🧬 Evolução genética")
        if not last_params.get("use_genetics", True):
            st.warning("A genética está desativada neste cenário. Ative em **Genética e migração** para acompanhar frequências alélicas.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                line_chart(df, ["sheep_freq_S", "sheep_freq_R"], "Ovelhas: fuga e resistência", "Frequência alélica dominante")
            with c2:
                line_chart(df, ["wolf_freq_H", "wolf_freq_R"], "Lobos: caça e resistência", "Frequência alélica dominante")

            st.markdown(
                """
                **Interpretação:** se a frequência de **S** aumenta nas ovelhas, a fuga está sendo favorecida.
                Se **H** aumenta nos lobos, a caça está sendo favorecida. O gene **R** indica pressão seletiva causada por doenças.
                """
            )

    with tab_environment:
        st.subheader("🌿 Recursos, estações, doença e migração")
        c1, c2 = st.columns(2)
        with c1:
            line_chart(df, ["mean_grass"], "Disponibilidade média de grama", "Grama média")
        with c2:
            line_chart(df, ["sick_sheep", "sick_wolves"], "Agentes doentes", "Quantidade")

        c3, c4 = st.columns(2)
        with c3:
            line_chart(df, ["grass_growth_rate"], "Taxa de crescimento da grama", "Taxa")
        with c4:
            line_chart(df, ["migrants", "disease_deaths"], "Migração e mortes por doença", "Eventos")

        if last_params.get("use_seasons", True):
            st.info(
                "As estações modulam a grama: primavera aumenta o crescimento; inverno reduz o recurso e pode gerar gargalos populacionais."
            )

    with tab_data:
        st.subheader("📋 Dados completos e exportação")
        st.dataframe(df, use_container_width=True, height=440)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Baixar histórico CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="wolf_sheep_historico_netlogo_view.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "⚙️ Baixar parâmetros JSON",
                data=json.dumps(last_params, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="wolf_sheep_parametros.json",
                mime="application/json",
                use_container_width=True,
            )

    with tab_model:
        st.subheader("📚 Sobre o modelo")
        st.markdown(
            """
            Este painel representa um **ecossistema evolutivo artificial**:

            - **Patches espaciais:** cada célula contém grama e pode conter obstáculos.
            - **Ovelhas:** comem grama, fogem de lobos, gastam energia e reproduzem.
            - **Lobos:** procuram ovelhas, caçam, gastam energia e reproduzem.
            - **Mundo toroidal:** sair por uma borda equivale a entrar pela borda oposta.
            - **Genética:** genes controlam visão, fuga, caça, resistência e fertilidade.
            - **Ambiente dinâmico:** estações alteram crescimento da grama; doenças e migração mudam a composição populacional.

            Relações científicas incorporadas:

            - **Lotka-Volterra:** dinâmica predador-presa.
            - **Mendel:** herança e recombinação genética.
            - **Darwin:** seleção natural por sobrevivência e reprodução diferencial.
            - **Sistemas complexos:** emergência, auto-organização, feedback e coevolução.
            """
        )

        st.markdown("#### Parâmetros usados nesta execução")
        st.json(last_params)
