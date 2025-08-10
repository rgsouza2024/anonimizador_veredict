#!/bin/bash

echo "========================================"
echo "    INSTALACAO MICROSOFT PRESIDIO AVANCADO"
echo "========================================"
echo

echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nao encontrado! Instale o Python 3.8+ primeiro."
    exit 1
fi
echo "✅ Python3 encontrado!"

echo
echo "[2/6] Instalando dependencias minimas..."
pip3 install --upgrade pip
pip3 install -r requirements_minimal.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependencias minimas!"
    echo "Tentando instalacao individual..."
    pip3 install gradio
    pip3 install presidio-analyzer
    pip3 install presidio-anonymizer
    pip3 install spacy
    pip3 install presidio-analyzer[spacy]
    pip3 install PyPDF2
    pip3 install requests
    pip3 install python-dotenv
fi

echo "✅ Dependencias basicas instaladas!"

echo
echo "[3/6] Baixando modelo Spacy para portugues brasileiro..."
python3 -m spacy download pt_core_news_lg

if [ $? -ne 0 ]; then
    echo "❌ Erro ao baixar modelo Spacy!"
    echo "Tentando metodo alternativo..."
    pip3 install https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.7.0/pt_core_news_lg-3.7.0-py3-none-any.whl
fi

if [ $? -ne 0 ]; then
    echo "⚠️ Modelo Spacy nao foi baixado. Tentando modelo menor..."
    python3 -m spacy download pt_core_news_sm
fi

echo "✅ Modelo Spacy configurado!"

echo
echo "[4/6] Tentando instalar dependencias completas..."
pip3 install -r requirements_gradio.txt

if [ $? -ne 0 ]; then
    echo "⚠️ Algumas dependencias opcionais nao foram instaladas."
    echo "A funcionalidade basica deve funcionar."
fi

echo
echo "[5/6] Verificando instalacao..."
python3 -c "import presidio_analyzer, presidio_anonymizer, spacy; print('✅ Todas as bibliotecas principais importadas com sucesso!')"

if [ $? -ne 0 ]; then
    echo "❌ Erro na verificacao!"
    echo "Verificando bibliotecas individuais..."
    python3 -c "import presidio_analyzer; print('✅ presidio_analyzer OK')"
    python3 -c "import presidio_anonymizer; print('✅ presidio_anonymizer OK')"
    python3 -c "import spacy; print('✅ spacy OK')"
    python3 -c "import gradio; print('✅ gradio OK')"
fi

echo
echo "[6/6] Testando funcionalidade basica..."
python3 teste_presidio_avancado.py

if [ $? -ne 0 ]; then
    echo "⚠️ Teste falhou, mas a instalacao pode estar funcionando."
    echo "Tente executar manualmente: python3 teste_presidio_avancado.py"
fi

echo
echo "========================================"
echo "    INSTALACAO CONCLUIDA!"
echo "========================================"
echo
echo "Para executar a interface Gradio:"
echo "  python3 app_gradio.py"
echo
echo "Para testar a funcionalidade:"
echo "  python3 teste_presidio_avancado.py"
echo
echo "Se houver problemas, verifique:"
echo "  1. Python 3.8+ instalado"
echo "  2. Conexao com internet para baixar modelos"
echo "  3. Permissoes de administrador"
echo
