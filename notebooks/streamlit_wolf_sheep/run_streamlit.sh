#!/bin/bash

# Script para instalar dependências e executar o Streamlit
# Compatível com Linux/Mac e Git Bash no Windows

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🐺🐑 Wolf Sheep Integrado — Dashboard Streamlit           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Usar python3 se disponível, senão python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✓ Python detectado: $($PYTHON_CMD --version)"
echo ""

# Instalar dependências
echo "📦 Instalando dependências..."
$PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1

echo "   • streamlit"
$PYTHON_CMD -m pip install streamlit -q

echo "   • pandas"
$PYTHON_CMD -m pip install pandas -q

echo "   • numpy"
$PYTHON_CMD -m pip install numpy -q

echo "   • matplotlib"
$PYTHON_CMD -m pip install matplotlib -q

echo ""
echo "✓ Dependências instaladas com sucesso!"
echo ""
echo "🚀 Iniciando Streamlit..."
echo "   Dashboard disponível em: http://localhost:8501"
echo ""
echo "   Pressione Ctrl+C para encerrar."
echo ""

# Executar Streamlit
$PYTHON_CMD -m streamlit run streamlit_wolf_sheep_integrado.py
