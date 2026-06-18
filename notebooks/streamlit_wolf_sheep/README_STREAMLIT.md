# 🐺🐑 Wolf Sheep Simple 3 — Modelo Integrado

Dashboard interativo em Streamlit para simulação e análise de um ecossistema evolutivo artificial que combina ecologia, genética, evolução e sistemas complexos.

---

## 🚀 Como Usar

### 1. **Instalação de Dependências**

```bash
pip install streamlit pandas numpy matplotlib
```

### 2. **Executar o Dashboard**

```bash
streamlit run streamlit_wolf_sheep_integrado.py
```

A aplicação abrirá em seu navegador padrão (geralmente `http://localhost:8501`).

---

## 📊 Interface do Dashboard

### **Barra Lateral Esquerda**

Todos os parâmetros do modelo podem ser ajustados aqui antes de executar a simulação:

#### 🌍 **Ambiente**
- **Largura/Altura**: Tamanho do mundo (células)
- **Máx de grama**: Quantidade máxima de recurso por célula
- **Taxa de crescimento**: Velocidade de regeneração da grama

#### 👥 **Populações Iniciais**
- **Ovelhas iniciais**: Número de herbívoros no início
- **Lobos iniciais**: Número de predadores no início

#### ⚡ **Energia**
- **Energia inicial**: Quanto de energia cada agente começa
- **Custo de movimento**: Energia gasta para se mover a cada tick

#### 🔄 **Reprodução**
- **Probabilidade de reprodução**: Chance de um agente se reproduzir
- **Energia mínima**: Quanto de energia é necessário para reproduzir

#### 🧬 **Genética**
- **Taxa de mutação**: Probabilidade de alteração genética (0-10%)
- **Ativar genética**: Ativa evolução e herança genética
- **Ativar migração**: Novos agentes entram no ecossistema

#### 🌡️ **Ambiente Dinâmico**
- **Ativar estações**: Alterna primavera/verão/outono/inverno (afeta crescimento da grama)
- **Ativar obstáculos**: Adiciona barreiras no mundo
- **Ativar doenças**: Doenças afetam populações
- **Densidade de obstáculos**: Percentual de células bloqueadas

#### 🎬 **Simulação**
- **Número de ticks**: Duração da simulação (1 tick = 1 passo de tempo)
- **Seed aleatória**: Para reproduzibilidade dos resultados

### **Botão EXECUTAR SIMULAÇÃO**

Clique para iniciar a simulação com os parâmetros definidos. O progresso será mostrado em tempo real.

---

## 📈 Resultados Exibidos

Após a simulação, você verá:

### **1. Resumo em Cards**
Métricas principais:
- Ticks executados
- Populações finais
- Populações máximas
- Total de presas predadas

### **2. Dinâmica Populacional**
Dois gráficos lado-a-lado:
- **Esquerda**: Populações de ovelhas e lobos ao longo do tempo
- **Direita**: Energia média de cada espécie

### **3. Evolução Genética** (se ativada)
Dois gráficos mostrando frequências alélicas:
- **Ovelhas**: Genes de fuga (S) e resistência (R)
- **Lobos**: Genes de caça (H) e resistência (R)

Os valores oscilam entre 0 (alelo recessivo) e 1 (alelo dominante).

### **4. Recursos e Ambiente**
Gráfico de disponibilidade de grama ao longo do tempo.

### **5. Tabela de Dados**
Todos os dados coletados em formato tabular (opcional).

### **6. Download**
Botão para baixar os dados em CSV para análise posterior.

---

## 🎯 Cenários Predefinidos

Escolha um cenário no início para começar rapidamente:

### **1. Base (sem recursos)**
Mundo simples, sem:
- Estações
- Obstáculos
- Doenças
- Migração
- Genética

Útil para entender a dinâmica básica predador-presa de **Lotka-Volterra**.

### **2. Ampliado (com estações e obstáculos)**
Adiciona complexidade:
- ✅ Estações (primavera/verão/outono/inverno)
- ✅ Obstáculos (montanhas, rochas)
- ✅ Doenças
- ✅ Migração
- ❌ Genética (ainda desativada)

Mostra como fatores ambientais afetam populações.

### **3. Evolutivo (completo)**
Ativa TUDO:
- ✅ Estações
- ✅ Obstáculos
- ✅ Doenças
- ✅ Migração
- ✅ **Genética com Hereditariedade Mendeliana**

Demonstra seleção natural, evolução e coevolução.

### **4. Personalizado**
Crie sua própria combinação de parâmetros!

---

## 🧬 Sistema Genético

### **Genes nas Ovelhas**
| Gene | Nome | Efeito |
|------|------|--------|
| **V** | Visão | Capacidade de detectar predadores |
| **S** | Fuga | Velocidade/agilidade para escapar |
| **R** | Resistência | Defesa contra doenças |
| **F** | Fertilidade | Taxa de reprodução |

### **Genes nos Lobos**
| Gene | Nome | Efeito |
|------|------|--------|
| **V** | Visão | Capacidade de detectar presas |
| **H** | Caça | Eficiência de predação |
| **R** | Resistência | Defesa contra doenças |
| **F** | Fertilidade | Taxa de reprodução |

### **Hereditariedade**
- Cada gene possui 2 alelos (um de cada pai)
- **Alelos dominantes** (maiúsculas): expressos no fenótipo
- **Alelos recessivos** (minúsculas): ocultos
- **Segregação**: Cada pai passa 1 alelo ao filho
- **Mutação**: Pequena chance de alelo mudar durante herança

---

## 📊 Interpretando os Gráficos

### **Populações**
Procure por **oscilações periódicas** (padrão Lotka-Volterra):
- Aumentam presas → aumentam predadores → diminuem presas → diminuem predadores → repete

### **Frequências Alélicas**
Valores crescentes mostram **seleção natural**:
- Gene **S** (fuga) deve aumentar se predação é alta
- Gene **H** (caça) deve aumentar se há muitas presas
- Gene **R** (resistência) deve aumentar se doenças são prevalentes

### **Energia Média**
Indica saúde da população:
- Energia baixa = escassez de recursos
- Energia alta = abundância

---

## 🔬 Conceitos Científicos Incorporados

### **Ecologia**
- Cadeia alimentar: Grama → Ovelhas → Lobos
- Oscilações predador-presa (Lotka-Volterra)
- Competição e capacidade de suporte

### **Genética**
- **Lei 1 de Mendel**: Segregação de alelos
- **Lei 2 de Mendel**: Segregação independente de genes
- Herança mendeliana com recessividade
- Mutação como fonte de variabilidade

### **Evolução**
- **Seleção natural**: Genes vantajosos aumentam em frequência
- **Coevolução**: Predadores e presas evoluem juntos
- **Fitness diferencial**: Agentes com melhores genes sobrevivem e reproduzem mais

### **Sistemas Complexos**
- **Emergência**: Padrões globais surgem sem programação explícita
- **Auto-organização**: Populações se reorganizam continuamente
- **Feedback**: Ciclos de retroalimentação positiva e negativa
- **Não-linearidade**: Pequenas mudanças podem ter efeitos grandes

---

## 💡 Sugestões de Experimentos

### **Experimento 1: Impacto das Estações**
1. Selecione "Base"
2. Copie os parâmetros exatos
3. Crie duas simulações: uma com estações, outra sem
4. Compare as oscilações populacionais

### **Experimento 2: Mutação e Adaptação**
1. Selecione "Evolutivo"
2. Execute com taxa de mutação = 0%
3. Execute com taxa de mutação = 5%
4. Observe como frequências alélicas mudam

### **Experimento 3: Efeito de Doenças**
1. Selecione "Ampliado"
2. Ajuste `initial_disease_prob` de 0 a 0.1
3. Observe o colapso das populações com altas taxas

### **Experimento 4: Qualidade do Predador**
1. Aumentar `base_wolf_reproduction_prob`
2. Aumentar `default_wolf_vision`
3. Observe se os lobos dominam o ecossistema

---

## 📈 Comparando com Lotka-Volterra

No cenário "Base", as oscilações deverão se aproximar do modelo matemático clássico:

$$\frac{dN}{dt} = \alpha N - \beta NP \quad \text{(presas)}$$
$$\frac{dP}{dt} = \delta NP - \gamma P \quad \text{(predadores)}$$

Onde:
- N = população de presas (ovelhas)
- P = população de predadores (lobos)
- α, β, δ, γ = parâmetros

---

## 🐛 Troubleshooting

### **Simulação muito lenta?**
- Reduza `n_steps` (número de ticks)
- Reduza tamanho do mundo (width/height)
- Desative "Ativar genética"

### **Populações desaparecem rápido?**
- Aumentar `initial_sheep_energy`
- Aumentar `grass_max`
- Diminuir `wolf_movement_cost`

### **Nenhuma evolução aparente?**
- Aumentar `mutation_rate` para ~5%
- Aumentar `n_steps` para 300+
- Ativar doenças (pressão seletiva)

---

## 📚 Referências

- **Lotka-Volterra**: Dinâmica predador-presa
- **Mendel**: Genética de populações
- **Darwin**: Seleção natural
- **Mesa (Multi-agent Modeling)**: Framework de simulação
- **NetLogo**: Inspiração para agent-based models

---

## 📝 Autor

Modelo integrado combinando:
- Ecologia (Lotka-Volterra)
- Genética (Mendel)
- Evolução (Darwin)
- Sistemas complexos (Complexidade)

Desenvolvido como ferramenta educacional para ensino de biologia, ecologia, genética e ciência da complexidade.

---

**Aproveite a simulação! 🚀**
