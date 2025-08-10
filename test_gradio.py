#!/usr/bin/env python3
"""
Script de teste para a versão Gradio do AnonimizaJud
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Testa se todas as importações estão funcionando"""
    print("🧪 Testando importações...")
    
    try:
        import gradio as gr
        print("✅ Gradio importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Gradio: {e}")
        return False
    
    try:
        # Adicionar o diretório pai ao path
        sys.path.append(str(Path(__file__).parent.parent))
        from anonimizador import Anonimizador
        print("✅ Módulo anonimizador importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo anonimizador: {e}")
        return False
    
    try:
        import presidio_analyzer
        print("✅ Presidio Analyzer importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Presidio Analyzer: {e}")
        return False
    
    try:
        import spacy
        print("✅ SpaCy importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar SpaCy: {e}")
        return False
    
    return True

def test_anonimizador():
    """Testa se o anonimizador está funcionando"""
    print("\n🔒 Testando anonimizador...")
    
    try:
        from anonimizador import Anonimizador
        anonimizador = Anonimizador()
        print("✅ Anonimizador inicializado com sucesso")
        
        # Teste simples de análise de entidades
        texto_teste = "O CPF 123.456.789-00 e o CEP 12345-678 foram encontrados."
        resultado = anonimizador.analisar_entidades(texto_teste)
        
        if resultado:
            print("✅ Análise de entidades funcionando")
        else:
            print("⚠️ Análise de entidades retornou None")
            
    except Exception as e:
        print(f"❌ Erro ao testar anonimizador: {e}")
        return False
    
    return True

def test_gradio_interface():
    """Testa se a interface Gradio pode ser criada"""
    print("\n🎨 Testando interface Gradio...")
    
    try:
        import gradio as gr
        
        # Teste simples de criação de interface
        with gr.Blocks() as interface:
            gr.Markdown("# Teste")
            gr.Textbox(label="Teste")
        
        print("✅ Interface Gradio criada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar interface Gradio: {e}")
        return False

def test_dependencies():
    """Testa se todas as dependências estão disponíveis"""
    print("\n📦 Testando dependências...")
    
    dependencies = [
        "pandas", "numpy", "PIL", "requests", "tiktoken",
        "openai", "anthropic", "google.generativeai", "groq", "ollama"
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            if dep == "PIL":
                import PIL
            elif dep == "google.generativeai":
                import google.generativeai
            else:
                __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"⚠️ {dep} (opcional)")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️ Dependências opcionais não encontradas: {', '.join(missing_deps)}")
        print("   Estas são opcionais e não impedem o funcionamento básico")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da versão Gradio do AnonimizaJud...\n")
    
    tests = [
        ("Importações", test_imports),
        ("Anonimizador", test_anonimizador),
        ("Interface Gradio", test_gradio_interface),
        ("Dependências", test_dependencies)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A versão Gradio está pronta para uso.")
        print("\n🚀 Para executar a aplicação:")
        print("   python app_gradio.py")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("\n💡 Dicas para resolver problemas:")
        print("   1. Instale as dependências: pip install -r requirements_gradio.txt")
        print("   2. Verifique se o arquivo anonimizador.py está na pasta pai")
        print("   3. Certifique-se de que o Python 3.8+ está instalado")

if __name__ == "__main__":
    main()
