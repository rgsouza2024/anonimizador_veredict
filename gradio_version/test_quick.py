#!/usr/bin/env python3
"""
Teste rápido para verificar se as dependências estão funcionando
"""

import sys
print("=" * 60)
print("🧪 TESTE RÁPIDO - DEPENDÊNCIAS MICROSOFT PRESIDIO")
print("=" * 60)
print()

print(f"🐍 Python: {sys.version}")
print(f"📁 Diretório: {sys.executable}")
print()

# Testar presidio_analyzer
try:
    import presidio_analyzer
    try:
        version = presidio_analyzer.__version__
        print(f"✅ presidio_analyzer: {version}")
    except AttributeError:
        print("✅ presidio_analyzer: OK (versão não disponível)")
except ImportError as e:
    print(f"❌ presidio_analyzer: {e}")

# Testar presidio_anonymizer
try:
    import presidio_anonymizer
    try:
        version = presidio_anonymizer.__version__
        print(f"✅ presidio_anonymizer: {version}")
    except AttributeError:
        print("✅ presidio_anonymizer: OK (versão não disponível)")
except ImportError as e:
    print(f"❌ presidio_anonymizer: {e}")

# Testar spacy
try:
    import spacy
    try:
        version = spacy.__version__
        print(f"✅ spacy: {version}")
    except AttributeError:
        print("✅ spacy: OK (versão não disponível)")
    
    # Tentar carregar modelo português
    try:
        nlp = spacy.load("pt_core_news_lg")
        print("✅ spacy pt_core_news_lg: Carregado com sucesso")
    except OSError:
        try:
            nlp = spacy.load("pt_core_news_sm")
            print("✅ spacy pt_core_news_sm: Carregado com sucesso (modelo menor)")
        except OSError:
            print("❌ spacy: Nenhum modelo português encontrado")
            print("   Execute: python -m spacy download pt_core_news_lg")
            
except ImportError as e:
    print(f"❌ spacy: {e}")

# Testar gradio
try:
    import gradio
    try:
        version = gradio.__version__
        print(f"✅ gradio: {version}")
    except AttributeError:
        print("✅ gradio: OK (versão não disponível)")
except ImportError as e:
    print(f"❌ gradio: {e}")

# Testar outras dependências
try:
    import PyPDF2
    try:
        version = PyPDF2.__version__
        print(f"✅ PyPDF2: {version}")
    except AttributeError:
        print("✅ PyPDF2: OK (versão não disponível)")
except ImportError as e:
    print(f"❌ PyPDF2: {e}")

try:
    import requests
    try:
        version = requests.__version__
        print(f"✅ requests: {version}")
    except AttributeError:
        print("✅ requests: OK (versão não disponível)")
except ImportError as e:
    print(f"❌ requests: {e}")

try:
    import dotenv
    print("✅ python-dotenv: OK")
except ImportError as e:
    print(f"❌ python-dotenv: {e}")

print()
print("=" * 60)

# Verificar se tudo está funcionando
print("🔍 VERIFICAÇÃO FINAL:")
print()

if 'presidio_analyzer' in sys.modules and 'presidio_anonymizer' in sys.modules and 'spacy' in sys.modules:
    print("🎉 TODAS AS DEPENDÊNCIAS PRINCIPAIS ESTÃO FUNCIONANDO!")
    print("✅ Você pode executar: python app_gradio.py")
    print("✅ Você pode executar: python teste_presidio_avancado.py")
else:
    print("⚠️ ALGUMAS DEPENDÊNCIAS ESTÃO FALTANDO!")
    print("📖 Consulte: INSTALACAO_MANUAL.md")
    print("🔧 Execute: install_presidio_avancado.bat (Windows)")
    print("🔧 Execute: ./install_presidio_avancado.sh (Linux/Mac)")

print()
print("=" * 60)
