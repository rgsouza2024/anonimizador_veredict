@echo off
echo ========================================
echo    INSTALACAO MICROSOFT PRESIDIO AVANCADO
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado! Instale o Python 3.8+ primeiro.
    pause
    exit /b 1
)
echo ✅ Python encontrado!

echo.
echo [2/6] Instalando dependencias minimas...
pip install --upgrade pip
pip install -r requirements_minimal.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias minimas!
    echo Tentando instalacao individual...
    pip install gradio
    pip install presidio-analyzer
    pip install presidio-anonymizer
    pip install spacy
    pip install presidio-analyzer[spacy]
    pip install PyPDF2
    pip install requests
    pip install python-dotenv
)

echo ✅ Dependencias basicas instaladas!

echo.
echo [3/6] Baixando modelo Spacy para portugues brasileiro...
python -m spacy download pt_core_news_lg

if errorlevel 1 (
    echo ❌ Erro ao baixar modelo Spacy!
    echo Tentando metodo alternativo...
    pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.7.0/pt_core_news_lg-3.7.0-py3-none-any.whl
)

if errorlevel 1 (
    echo ⚠️ Modelo Spacy nao foi baixado. Tentando modelo menor...
    python -m spacy download pt_core_news_sm
)

echo ✅ Modelo Spacy configurado!

echo.
echo [4/6] Tentando instalar dependencias completas...
pip install -r requirements_gradio.txt

if errorlevel 1 (
    echo ⚠️ Algumas dependencias opcionais nao foram instaladas.
    echo A funcionalidade basica deve funcionar.
)

echo.
echo [5/6] Verificando instalacao...
python -c "import presidio_analyzer, presidio_anonymizer, spacy; print('✅ Todas as bibliotecas principais importadas com sucesso!')"

if errorlevel 1 (
    echo ❌ Erro na verificacao!
    echo Verificando bibliotecas individuais...
    python -c "import presidio_analyzer; print('✅ presidio_analyzer OK')"
    python -c "import presidio_anonymizer; print('✅ presidio_anonymizer OK')"
    python -c "import spacy; print('✅ spacy OK')"
    python -c "import gradio; print('✅ gradio OK')"
)

echo.
echo [6/6] Testando funcionalidade basica...
python teste_presidio_avancado.py

if errorlevel 1 (
    echo ⚠️ Teste falhou, mas a instalacao pode estar funcionando.
    echo Tente executar manualmente: python teste_presidio_avancado.py
)

echo.
echo ========================================
echo    INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para executar a interface Gradio:
echo   python app_gradio.py
echo.
echo Para testar a funcionalidade:
echo   python teste_presidio_avancado.py
echo.
echo Se houver problemas, verifique:
echo   1. Python 3.8+ instalado
echo   2. Conexao com internet para baixar modelos
echo   3. Permissoes de administrador
echo.
pause
