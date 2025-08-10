@echo off
echo ========================================
echo    Instalando AnonimizaJud - Presidio
echo ========================================
echo.

echo 1. Instalando dependencias basicas...
pip install -r requirements_gradio.txt

echo.
echo 2. Baixando modelo de lingua portuguesa para spaCy...
python -m spacy download pt_core_news_sm

echo.
echo 3. Verificando instalacao...
python -c "import presidio_analyzer, presidio_anonymizer, PyPDF2, spacy; print('✅ Todas as dependencias foram instaladas com sucesso!')"

echo.
echo ========================================
echo    Instalacao concluida!
echo ========================================
echo.
echo Para executar a aplicacao:
echo python app_gradio.py
echo.
pause
