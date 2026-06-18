import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import random
import math

# CONFIGURAÇÃO STREAMLIT
st.set_page_config(
    page_title="Wolf Sheep Integrado",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐺🐑 Wolf Sheep Simple 3 — Modelo Integrado")
st.markdown("**Dashboard interativo para simular e analisar um ecossistema evolutivo artificial**")

# VARIÁVEIS GLOBAIS E FUNÇÕES AUXILIARES
SHEEP_GENES = ["V", "S", "R", "F"]
WOLF_GENES = ["V", "H", "R", "F"]

ALLELES = {
    "V": ("V", "v"),
    "S": ("S", "s"),
    "H": ("H", "h"),
    "R": ("R", "r"),
    "F": ("F", "f"),
}

GENE_NAMES = {
    "V": "visão",
    "S": "fuga/velocidade",
    "H": "caça",
    "R": "resistência à doença",
    "F": "fertilidade",
}


def get_season(tick, params):
    if not params.get("use_seasons", True):
        return "sem estação"
    seasons = ["primavera", "verao", "outono", "inverno"]
    idx = (tick // params["season_length"]) % len(seasons)
    return seasons[idx]


def current_grass_growth_rate(tick, params):
    if not params.get("use_seasons", True):
        return params["grass_regrowth_base"]
    season = get_season(tick, params)
    return params["grass_regrowth_base"] * params["season_growth_multipliers"][season]


def toroidal_distance(pos_a, pos_b, width, height):
    dx = abs(pos_a[0] - pos_b[0])
    dy = abs(pos_a[1] - pos_b[1])
    dx = min(dx, width - dx)
    dy = min(dy, height - dy)
    return math.sqrt(dx * dx + dy * dy)


def make_random_genome(genes, dominant_prob=0.5):
    genome = {}
    for gene in genes:
        dom, rec = ALLELES[gene]
        a1 = dom if random.random() < dominant_prob else rec
        a2 = dom if random.random() < dominant_prob else rec
        genome[gene] = (a1, a2)
    return genome


def inherit_genome(parent_a, parent_b, mutation_rate=0.01):
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


def dominant_count(genome, gene):
    dom = ALLELES[gene][0]
    return sum(1 for a in genome[gene] if a == dom)


def allele_frequency(agents, gene, dominant=True):
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


# PARÂMETROS PADRÃO
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

    # Visão e comportamento
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

    # Ativadores por cenário
    "use_obstacles": True,
    "use_seasons": True,
    "use_disease": True,
    "use_migration": True,
    "use_genetics": True,

    # Execução
    "n_steps": 300,
    "random_seed": 42,
}


def scenario_params(name):
    p = params_base.copy()
    if name == "base":
        p.update({
            "use_obstacles": False,
            "use_seasons": False,
            "use_disease": False,
            "use_migration": False,
            "use_genetics": False,
            "obstacle_density": 0.0,
        })
    elif name == "ampliado":
        p.update({
            "use_obstacles": True,
            "use_seasons": True,
            "use_disease": True,
            "use_migration": True,
            "use_genetics": False,
        })
    elif name == "evolutivo":
        p.update({
            "use_obstacles": True,
            "use_seasons": True,
            "use_disease": True,
            "use_migration": True,
            "use_genetics": True,
        })
    return p


# SIMULAÇÃO (VERSÃO SIMPLIFICADA PARA STREAMLIT)
class Sheep:
    def __init__(self, unique_id, energy, genome, params):
        self.unique_id = unique_id
        self.kind = "sheep"
        self.energy = energy
        self.age = 0
        self.sick = False
        self.genome = genome
        self.params = params

    def phenotype(self):
        if not self.params.get("use_genetics", True):
            return {"vision": 4, "escape": 0.5, "resistance": 0.5, "fertility": 0.5}
        
        vision = 3 + dominant_count(self.genome, "V") * 0.5
        escape = 0.3 + dominant_count(self.genome, "S") * 0.35
        resistance = 0.3 + dominant_count(self.genome, "R") * 0.35
        fertility = 0.3 + dominant_count(self.genome, "F") * 0.35
        
        return {"vision": vision, "escape": escape, "resistance": resistance, "fertility": fertility}


class Wolf:
    def __init__(self, unique_id, energy, genome, params):
        self.unique_id = unique_id
        self.kind = "wolf"
        self.energy = energy
        self.age = 0
        self.sick = False
        self.genome = genome
        self.params = params

    def phenotype(self):
        if not self.params.get("use_genetics", True):
            return {"vision": 5, "hunting": 0.5, "resistance": 0.5, "fertility": 0.5}
        
        vision = 4 + dominant_count(self.genome, "V") * 0.5
        hunting = 0.3 + dominant_count(self.genome, "H") * 0.35
        resistance = 0.3 + dominant_count(self.genome, "R") * 0.35
        fertility = 0.3 + dominant_count(self.genome, "F") * 0.35
        
        return {"vision": vision, "hunting": hunting, "resistance": resistance, "fertility": fertility}


def run_simulation(params):
    """Executa simulação simplificada do modelo Wolf Sheep"""
    
    random.seed(params["random_seed"])
    np.random.seed(params["random_seed"])
    
    # Inicializar agentes
    sheep = [
        Sheep(i, params["initial_sheep_energy"], make_random_genome(SHEEP_GENES), params)
        for i in range(params["initial_sheep"])
    ]
    
    wolves = [
        Wolf(i + 1000, params["initial_wolf_energy"], make_random_genome(WOLF_GENES), params)
        for i in range(params["initial_wolves"])
    ]
    
    # Inicializar grama
    grass = np.full((params["width"], params["height"]), params["grass_max"] / 2)
    
    # Histórico
    history = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for tick in range(params["n_steps"]):
        # Atualizar progress
        progress_bar.progress((tick + 1) / params["n_steps"])
        status_text.text(f"Simulando... tick {tick + 1}/{params['n_steps']}")
        
        # Crescimento de grama
        growth_rate = current_grass_growth_rate(tick, params)
        grass = np.minimum(grass + params["grass_regrowth_base"] * growth_rate, params["grass_max"])
        
        # Sheep comem grama
        sheep_alive = []
        for s in sheep:
            if random.random() < 0.7:  # Probabilidade de encontrar grama
                energy_gain = params["energy_gain_from_grass"]
                s.energy += energy_gain
                grass[min(49, max(0, int(random.random() * 50))), 
                      min(49, max(0, int(random.random() * 50)))] -= 0.5
            
            s.energy -= params["sheep_movement_cost"]
            s.age += 1
            
            # Verificar morte
            if s.energy > 0 and s.age < params["max_age_sheep"]:
                sheep_alive.append(s)
        
        sheep = sheep_alive
        
        # Wolves caçam sheep
        wolf_alive = []
        eaten_count = 0
        
        for w in wolves:
            if len(sheep) > 0 and random.random() < 0.5 + 0.2 * w.phenotype()["hunting"]:
                victim = random.choice(sheep)
                w.energy += params["energy_gain_from_sheep"]
                sheep.remove(victim)
                eaten_count += 1
            
            w.energy -= params["wolf_movement_cost"]
            w.age += 1
            
            # Verificar morte
            if w.energy > 0 and w.age < params["max_age_wolf"]:
                wolf_alive.append(w)
        
        wolves = wolf_alive
        
        # Reprodução sheep
        new_sheep = []
        for s in sheep:
            if len(sheep) > 1 and s.energy > params["sheep_reproduction_energy_threshold"]:
                if random.random() < params["base_sheep_reproduction_prob"]:
                    parent2 = random.choice([x for x in sheep if x != s])
                    child_genome = inherit_genome(s.genome, parent2.genome, params["mutation_rate"])
                    child = Sheep(len(sheep) + len(sheep) * 1000, 
                                params["offspring_energy_fraction"] * s.energy, 
                                child_genome, params)
                    new_sheep.append(child)
                    s.energy *= (1 - params["offspring_energy_fraction"])
        
        sheep.extend(new_sheep)
        
        # Reprodução wolves
        new_wolves = []
        for w in wolves:
            if len(wolves) > 1 and w.energy > params["wolf_reproduction_energy_threshold"]:
                if random.random() < params["base_wolf_reproduction_prob"]:
                    parent2 = random.choice([x for x in wolves if x != w])
                    child_genome = inherit_genome(w.genome, parent2.genome, params["mutation_rate"])
                    child = Wolf(len(wolves) + len(wolves) * 2000, 
                               params["offspring_energy_fraction"] * w.energy, 
                               child_genome, params)
                    new_wolves.append(child)
                    w.energy *= (1 - params["offspring_energy_fraction"])
        
        wolves.extend(new_wolves)
        
        # Migração
        if params.get("use_migration", False) and random.random() < params["migration_prob"]:
            if random.random() < 0.5 and len(sheep) < 500:
                new_sheep = Sheep(len(sheep) + len(sheep) * 3000,
                                params["initial_sheep_energy"],
                                make_random_genome(SHEEP_GENES), params)
                sheep.append(new_sheep)
            elif len(wolves) < 100:
                new_wolf = Wolf(len(wolves) + len(wolves) * 4000,
                              params["initial_wolf_energy"],
                              make_random_genome(WOLF_GENES), params)
                wolves.append(new_wolf)
        
        # Coleta dados
        sheep_freq_S = allele_frequency(sheep, "S", dominant=True) if sheep else 0
        sheep_freq_R = allele_frequency(sheep, "R", dominant=True) if sheep else 0
        wolf_freq_H = allele_frequency(wolves, "H", dominant=True) if wolves else 0
        wolf_freq_R = allele_frequency(wolves, "R", dominant=True) if wolves else 0
        
        mean_sheep_energy = np.mean([s.energy for s in sheep]) if sheep else 0
        mean_wolf_energy = np.mean([w.energy for w in wolves]) if wolves else 0
        mean_grass = np.mean(grass)
        
        history.append({
            "tick": tick,
            "sheep": len(sheep),
            "wolves": len(wolves),
            "eaten_sheep": eaten_count,
            "sheep_births": len(new_sheep),
            "wolf_births": len(new_wolves),
            "mean_grass": mean_grass,
            "grass_growth_rate": growth_rate,
            "season": get_season(tick, params),
            "mean_sheep_energy": mean_sheep_energy,
            "mean_wolf_energy": mean_wolf_energy,
            "sheep_freq_S": sheep_freq_S,
            "sheep_freq_R": sheep_freq_R,
            "wolf_freq_H": wolf_freq_H,
            "wolf_freq_R": wolf_freq_R,
        })
        
        # Parar se populações acabarem
        if len(sheep) == 0 or len(wolves) == 0:
            break
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(history)


# INTERFACE STREAMLIT
# Sidebar para seleção de cenário
st.sidebar.header("⚙️ Configuração")

scenario_choice = st.sidebar.selectbox(
    "**Selecione um cenário predefinido:**",
    ["Personalizado", "Base (sem recursos)", "Ampliado (com estações e obstáculos)", "Evolutivo (completo)"],
    help="Base: sem complexidade. Ampliado: com estações/obstáculos. Evolutivo: com genética."
)

# Inicializar parâmetros
if "params" not in st.session_state:
    if scenario_choice == "Base (sem recursos)":
        st.session_state.params = scenario_params("base")
    elif scenario_choice == "Ampliado (com estações e obstáculos)":
        st.session_state.params = scenario_params("ampliado")
    elif scenario_choice == "Evolutivo (completo)":
        st.session_state.params = scenario_params("evolutivo")
    else:
        st.session_state.params = params_base.copy()

if scenario_choice != "Personalizado":
    if scenario_choice == "Base (sem recursos)":
        st.session_state.params = scenario_params("base")
    elif scenario_choice == "Ampliado (com estações e obstáculos)":
        st.session_state.params = scenario_params("ampliado")
    elif scenario_choice == "Evolutivo (completo)":
        st.session_state.params = scenario_params("evolutivo")

params = st.session_state.params

# Expanders para ajuste de parâmetros
with st.sidebar.expander("🌍 Ambiente", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["width"] = st.slider("Largura", 30, 80, params["width"])
        params["height"] = st.slider("Altura", 30, 80, params["height"])
    with col2:
        params["grass_max"] = st.slider("Máx de grama", 5.0, 20.0, params["grass_max"])
        params["grass_regrowth_base"] = st.slider("Taxa crescimento", 0.2, 1.0, params["grass_regrowth_base"], 0.05)

with st.sidebar.expander("👥 Populações Iniciais", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["initial_sheep"] = st.slider("Ovelhas iniciais", 50, 300, params["initial_sheep"], 10)
    with col2:
        params["initial_wolves"] = st.slider("Lobos iniciais", 10, 100, params["initial_wolves"], 5)

with st.sidebar.expander("⚡ Energia", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["initial_sheep_energy"] = st.slider("Energia inicial (ovelha)", 10.0, 50.0, params["initial_sheep_energy"])
        params["sheep_movement_cost"] = st.slider("Custo movimento (ovelha)", 0.5, 3.0, params["sheep_movement_cost"], 0.1)
    with col2:
        params["initial_wolf_energy"] = st.slider("Energia inicial (lobo)", 20.0, 60.0, params["initial_wolf_energy"])
        params["wolf_movement_cost"] = st.slider("Custo movimento (lobo)", 0.5, 3.0, params["wolf_movement_cost"], 0.1)

with st.sidebar.expander("🔄 Reprodução", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["base_sheep_reproduction_prob"] = st.slider("Prob. reprodução (ovelha)", 0.01, 0.15, params["base_sheep_reproduction_prob"], 0.005)
        params["sheep_reproduction_energy_threshold"] = st.slider("Energia mínima (ovelha)", 20.0, 60.0, params["sheep_reproduction_energy_threshold"])
    with col2:
        params["base_wolf_reproduction_prob"] = st.slider("Prob. reprodução (lobo)", 0.005, 0.1, params["base_wolf_reproduction_prob"], 0.005)
        params["wolf_reproduction_energy_threshold"] = st.slider("Energia mínima (lobo)", 30.0, 70.0, params["wolf_reproduction_energy_threshold"])

with st.sidebar.expander("🧬 Genética", expanded=False):
    params["mutation_rate"] = st.slider("Taxa de mutação", 0.0, 0.1, params["mutation_rate"], 0.005)
    col1, col2 = st.columns(2)
    with col1:
        params["use_genetics"] = st.checkbox("Ativar genética", params["use_genetics"])
    with col2:
        params["use_migration"] = st.checkbox("Ativar migração", params["use_migration"])

with st.sidebar.expander("🌡️ Ambiente Dinâmico", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["use_seasons"] = st.checkbox("Ativar estações", params["use_seasons"])
        params["use_obstacles"] = st.checkbox("Ativar obstáculos", params["use_obstacles"])
    with col2:
        params["use_disease"] = st.checkbox("Ativar doenças", params["use_disease"])
        params["obstacle_density"] = st.slider("Densidade obstáculos", 0.0, 0.2, params["obstacle_density"], 0.01)

with st.sidebar.expander("🎬 Simulação", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        params["n_steps"] = st.slider("Número de ticks", 50, 500, params["n_steps"], 50)
    with col2:
        params["random_seed"] = st.number_input("Seed aleatória", 0, 10000, params["random_seed"])

# Botão para executar
st.sidebar.markdown("---")

if st.sidebar.button("🚀 EXECUTAR SIMULAÇÃO", use_container_width=True, type="primary"):
    st.session_state.run_simulation = True
    st.session_state.df_result = run_simulation(params)

# EXIBIÇÃO DE RESULTADOS
if "df_result" in st.session_state:
    df = st.session_state.df_result
    
    # Resumo em cards
    st.markdown("---")
    st.subheader("📊 Resumo da Simulação")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Ticks executados", int(df["tick"].max() + 1))
    with col2:
        st.metric("Ovelhas finais", int(df["sheep"].iloc[-1]))
    with col3:
        st.metric("Lobos finais", int(df["wolves"].iloc[-1]))
    with col4:
        st.metric("Máx. ovelhas", int(df["sheep"].max()))
    with col5:
        st.metric("Máx. lobos", int(df["wolves"].max()))
    with col6:
        st.metric("Total predado", int(df["eaten_sheep"].sum()))
    
    # Gráficos
    st.markdown("---")
    st.subheader("📈 Dinâmica Populacional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["tick"], df["sheep"], label="Ovelhas", linewidth=2, color="white", marker="o", markersize=3)
        ax.plot(df["tick"], df["wolves"], label="Lobos", linewidth=2, color="red", marker="*", markersize=5)
        ax.set_xlabel("Tick", fontsize=11)
        ax.set_ylabel("População", fontsize=11)
        ax.set_title("Populações ao longo do tempo", fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["tick"], df["mean_sheep_energy"], label="Energia (ovelhas)", linewidth=2, color="lightblue")
        ax.plot(df["tick"], df["mean_wolf_energy"], label="Energia (lobos)", linewidth=2, color="orange")
        ax.set_xlabel("Tick", fontsize=11)
        ax.set_ylabel("Energia média", fontsize=11)
        ax.set_title("Energia média das populações", fontsize=12, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Genética
    if params.get("use_genetics", True):
        st.markdown("---")
        st.subheader("🧬 Evolução Genética")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df["tick"], df["sheep_freq_S"], label="Fuga (S)", linewidth=2, marker="o", markersize=3)
            ax.plot(df["tick"], df["sheep_freq_R"], label="Resistência (R)", linewidth=2, marker="s", markersize=3)
            ax.set_ylim(0, 1)
            ax.set_xlabel("Tick", fontsize=11)
            ax.set_ylabel("Frequência alélica", fontsize=11)
            ax.set_title("Frequências alélicas nas ovelhas", fontsize=12, fontweight="bold")
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df["tick"], df["wolf_freq_H"], label="Caça (H)", linewidth=2, marker="o", markersize=3)
            ax.plot(df["tick"], df["wolf_freq_R"], label="Resistência (R)", linewidth=2, marker="s", markersize=3)
            ax.set_ylim(0, 1)
            ax.set_xlabel("Tick", fontsize=11)
            ax.set_ylabel("Frequência alélica", fontsize=11)
            ax.set_title("Frequências alélicas nos lobos", fontsize=12, fontweight="bold")
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)
    
    # Grama e estações
    st.markdown("---")
    st.subheader("🌿 Recursos e Ambiente")
    
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df["tick"], df["mean_grass"], label="Grama média", linewidth=2, color="green")
    ax.fill_between(df["tick"], 0, df["mean_grass"], alpha=0.3, color="green")
    ax.set_xlabel("Tick", fontsize=11)
    ax.set_ylabel("Quantidade de grama", fontsize=11)
    ax.set_title("Disponibilidade de grama ao longo do tempo", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabela de dados
    st.markdown("---")
    st.subheader("📋 Dados Completos")
    
    if st.checkbox("Mostrar tabela de dados", value=False):
        st.dataframe(df, use_container_width=True)
    
    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name="wolf_sheep_simulacao.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Configure os parâmetros na barra lateral e clique em **EXECUTAR SIMULAÇÃO** para começar!")

# INFORMAÇÕES
st.markdown("---")
st.markdown("""
### 📚 Sobre o Modelo

Este é um **ecossistema evolutivo artificial** que combina:

- **Ecologia**: Dinâmica predador-presa (Lotka-Volterra)
- **Genética**: Herança mendeliana, mutação, recombinação
- **Evolução**: Seleção natural e coevolução
- **Complexidade**: Emergência, auto-organização, feedback

#### 🧬 Genes
- **V (Visão)**: Capacidade de detectar presas/predadores
- **S/H (Comportamento)**: Fuga (ovelhas) ou Caça (lobos)
- **R (Resistência)**: Defesa contra doenças
- **F (Fertilidade)**: Taxa de reprodução

#### 🔗 Leis Científicas Incorporadas
- **Mendel**: Primeira e Segunda Lei
- **Darwin**: Seleção Natural
- **Lotka-Volterra**: Dinâmica predador-presa
- **Sistemas Complexos**: Emergência e auto-organização
""")
