@echo off
REM Script para instalar dependências e executar o Streamlit no Windows

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🐺🐑 Wolf Sheep Integrado — Dashboard Streamlit           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.8 ou superior.
    echo.
    echo Você pode baixar em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Mostrar versão do Python
echo ✓ Python detectado:
python --version
echo.

REM Instalar dependências
echo 📦 Instalando dependências...
echo.

echo    • Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1

echo    • Instalando streamlit...
python -m pip install streamlit -q

echo    • Instalando pandas...
python -m pip install pandas -q

echo    • Instalando numpy...
python -m pip install numpy -q

echo    • Instalando matplotlib...
python -m pip install matplotlib -q

echo.
echo ✓ Dependências instaladas com sucesso!
echo.
echo 🚀 Iniciando Streamlit...
echo.
echo    Dashboard disponível em: http://localhost:8501
echo.
echo    Feche esta janela para encerrar.
echo.
echo.

REM Executar Streamlit
python -m streamlit run streamlit_wolf_sheep_integrado.py

pause
