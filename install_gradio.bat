@echo off
echo ========================================
echo    Instalando AnonimizaJud - Gradio
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado! Instale o Python 3.8+ primeiro.
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo [2/4] Criando ambiente virtual...
python -m venv venv_gradio
if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual
    pause
    exit /b 1
)
echo ✅ Ambiente virtual criado

echo.
echo [3/4] Ativando ambiente virtual...
call venv_gradio\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativado

echo.
echo [4/4] Instalando dependencias...
pip install -r requirements_gradio.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo ========================================
echo    Instalacao concluida com sucesso!
echo ========================================
echo.
echo Para executar a aplicacao:
echo   1. Ative o ambiente virtual: venv_gradio\Scripts\activate.bat
echo   2. Execute: python app_gradio.py
echo   3. Acesse: http://localhost:7860
echo.
echo Para testar a instalacao:
echo   python test_gradio.py
echo.
pause
