@echo off
echo ========================================
echo    Executando AnonimizaJud - Gradio
echo ========================================
echo.

echo [1/2] Ativando ambiente virtual...
call venv_gradio\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual
    echo Execute install_gradio.bat primeiro!
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativado

echo.
echo [2/2] Iniciando aplicacao...
echo 🚀 Aplicacao iniciando em http://localhost:7860
echo.
echo Pressione Ctrl+C para parar a aplicacao
echo.
python app_gradio.py

pause
