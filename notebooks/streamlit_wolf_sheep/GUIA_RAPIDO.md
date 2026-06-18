# 🎛️ Guia Rápido — Dashboard Streamlit

## ⚡ Quick Start

### Windows
1. Abra a pasta contendo os arquivos
2. **Clique duplo em `run_streamlit.bat`**
3. Seu navegador abrirá automaticamente em `http://localhost:8501`

### Linux/Mac
1. Abra o terminal na pasta contendo os arquivos
2. Execute: `bash run_streamlit.sh`
3. Acesse `http://localhost:8501` no navegador

### Manual (qualquer SO)
```bash
pip install -r requirements.txt
streamlit run streamlit_wolf_sheep_integrado.py
```

---

## 🎯 Funcionalidades Principais

### 1️⃣ **Seleção de Cenário** (Barra Lateral)

**4 opções predefinidas:**
- **Personalizado**: Ajuste todos os parâmetros do zero
- **Base**: Mundo simples (só predador-presa)
- **Ampliado**: Adiciona estações, obstáculos, doenças
- **Evolutivo**: Ativa genética completa com evolução

### 2️⃣ **Controles de Parâmetro** (Expanders Interativos)

Clique para expandir/recolher cada seção:

| Seção | O que controla |
|-------|---------------|
| 🌍 Ambiente | Tamanho do mundo e recursos |
| 👥 Populações | Números iniciais de ovelhas/lobos |
| ⚡ Energia | Vida e custo de movimento |
| 🔄 Reprodução | Taxa e requisitos de fertilidade |
| 🧬 Genética | Mutações e hereditariedade |
| 🌡️ Dinâmico | Estações, obstáculos, doenças |
| 🎬 Simulação | Duração e seed aleatória |

### 3️⃣ **Execução da Simulação**

**Botão Verde EXECUTAR SIMULAÇÃO**
- Inicia a simulação com parâmetros atuais
- Mostra progresso em tempo real
- Pode levar alguns segundos dependendo do número de ticks

### 4️⃣ **Visualizações em Tempo Real**

Após a execução:

**📊 Resumo (6 cards)**
- Ticks executados
- Populações finais
- Máximos atingidos
- Total de presas comidas

**📈 Dinâmica Populacional (2 gráficos)**
- Oscilações de ovelhas e lobos
- Energia média de cada espécie

**🧬 Evolução Genética (2 gráficos)** *Se genética ativada*
- Frequências alélicas das ovelhas
- Frequências alélicas dos lobos
- Valores entre 0 (recessivo) e 1 (dominante)

**🌿 Recursos e Ambiente (1 gráfico)**
- Disponibilidade de grama ao longo do tempo

**📋 Tabela (opcional)**
- Todos os dados em formato de planilha
- Checkbox para mostrar/ocultar

**📥 Download CSV**
- Exporte os dados para análise em Excel/Python

---

## 🎮 Exemplo de Uso Passo-a-Passo

### Cenário 1: Entender Lotka-Volterra

1. **Selecione**: "Base (sem recursos)"
2. **Ajustes**:
   - Ovelhas iniciais: 100
   - Lobos iniciais: 40
   - Número de ticks: 300
3. **Clique**: EXECUTAR SIMULAÇÃO
4. **Observe**: Oscilações periódicas regulares

**O que você verá:**
- Ciclos previsíveis: ovelhas ↑ → lobos ↑ → ovelhas ↓ → lobos ↓ → repete

---

### Cenário 2: Impacto das Estações

1. **Selecione**: "Ampliado (com estações e obstáculos)"
2. **Desative**:
   - ❌ Ativar doenças
   - ❌ Ativar migração
3. **Ajustes**:
   - Season length: 25 (estações mais rápidas)
   - Número de ticks: 300
4. **Clique**: EXECUTAR SIMULAÇÃO

**O que você verá:**
- Oscilações afetadas pelas estações
- Quedas no inverno (menos grama)
- Picos na primavera (mais recursos)

---

### Cenário 3: Evolução em Ação

1. **Selecione**: "Evolutivo (completo)"
2. **Ajustes**:
   - Taxa de mutação: 3%
   - Número de ticks: 400
   - Inicialmente: desative "use_genetics"
3. **Execute a simulação 1️⃣**
4. **Salve os dados 💾**
5. **Recarregue e habilite genética** ✅
6. **Execute a simulação 2️⃣**
7. **Compare os resultados**

**O que você verá:**
- Sem genética: frequências alélicas constantes
- Com genética: frequências mudam ao longo do tempo
- Genes benéficos aumentam em frequência

---

## 📊 Interpretando os Gráficos

### Gráfico de Populações

```
    ↑ População
    │     Lobos
    │        ╱╲    ╱╲
    │       ╱  ╲  ╱  ╲
    │  ╱╲  ╱    ╲╱    ╲
    │ ╱  ╲╱              Ovelhas
    ╱─────────────────────→ Tempo
```

**Padrão esperado**: Defasagem de ~90° entre espécies

---

### Gráfico de Frequências Alélicas

```
    1.0 ├─────────────────────── Alelo dominante
        │    ╱───────────╲
        │   ╱             ╲
        │  ╱               ╲    Aumenta se vantajoso
        │ ╱                 ╲   Diminui se prejudicial
    0.0 └─────────────────────
        └─────────────────────→ Tempo
```

**Interpretação:**
- 📈 Linha subindo = Seleção natural favorecendo esse alelo
- 📉 Linha descendo = Alelo sendo eliminado
- 🔄 Oscilação = Pressão seletiva mudando

---

## 🔧 Dicas de Otimização

### Simulação Rápida
```
width/height: 30
n_steps: 100
use_genetics: FALSE
```
⏱️ ~5 segundos

### Simulação Média
```
width/height: 50
n_steps: 200
use_genetics: TRUE
```
⏱️ ~30 segundos

### Simulação Completa
```
width/height: 70
n_steps: 400
use_genetics: TRUE
all features: TRUE
```
⏱️ ~2-3 minutos

---

## 🧪 Experimentos Sugeridos

### Exp. A: Qual Fator é Mais Importante?

1. Base + apenas estações
2. Base + apenas doenças
3. Base + apenas obstáculos
4. Compare os resultados

### Exp. B: Resistência a Doenças

1. Execute com doença = 0%
2. Execute com doença = 5%
3. Execute com doença = 15%
4. Observe o efeito na população

### Exp. C: Velocidade vs Visão

1. Diminua só a fertilidade (fuga) das ovelhas
2. Diminua só a visão das ovelhas
3. Qual afeta mais a sobrevivência?

### Exp. D: Pressão Seletiva Extrema

1. Selecione "Evolutivo"
2. Configure:
   - Taxa de mutação: 10%
   - Doenças: 20%
   - Obstáculos: 20%
   - Fome máxima: 8 (muito rigorosa)
3. Observe como populações se adaptam

---

## ⚠️ Possíveis Problemas

| Problema | Causa | Solução |
|----------|-------|---------|
| Populações desaparecem rápido | Fome alta | Aumentar grama ou energia inicial |
| Nenhuma evolução | Mutation rate = 0% | Aumentar para 3-5% |
| Simulação muito lenta | Mundo grande + muitos ticks | Reduzir ambos |
| Grafos vazios | CSV não existe | Clicar EXECUTAR SIMULAÇÃO |
| Padrões muito caóticos | Doenças muito agressivas | Reduzir initial_disease_prob |

---

## 🔬 Validação Científica

### Como saber se está funcionando corretamente?

✅ **Cenário Base deve:**
- Mostrar oscilações periódicas regulares
- Imitador o modelo de Lotka-Volterra
- Nunca entrar em equilíbrio estável

✅ **Genética deve:**
- Mostrar frequências alélicas mudando
- Genes benéficos aumentarem sob pressão
- Haver variação entre execuções

✅ **Estações devem:**
- Criar padrão de oscilação + sazonalidade
- Inverno = redução de grama
- Primavera = recuperação

---

## 📚 Recursos Adicionais

**Para Aprender Mais:**
- Lotka-Volterra: Wikipedia ou MIT OpenCourseWare
- Genética Mendeliana: Khan Academy
- Sistemas Complexos: Wolfram MathWorld
- Agent-Based Modeling: Mesa Documentation

**Ferramentas Similares:**
- NetLogo (Desktop)
- Repast Simphony (Java)
- AnyLogic (Comercial)

---

## 💬 Feedback

Se encontrou problemas ou tem sugestões:
1. Verifique o arquivo README_STREAMLIT.md
2. Teste com parâmetros padrão
3. Verifique se todas as dependências estão instaladas

**Divirta-se explorando o modelo! 🚀**
