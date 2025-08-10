#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o Microsoft Presidio está funcionando
"""

import os
import sys

def testar_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🔍 Testando imports...")
    
    try:
        import presidio_analyzer
        print("✅ presidio_analyzer - OK")
    except ImportError as e:
        print(f"❌ presidio_analyzer - ERRO: {e}")
        return False
    
    try:
        import presidio_anonymizer
        print("✅ presidio_anonymizer - OK")
    except ImportError as e:
        print(f"❌ presidio_anonymizer - ERRO: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 - OK")
    except ImportError as e:
        print(f"❌ PyPDF2 - ERRO: {e}")
        return False
    
    try:
        import spacy
        print("✅ spacy - OK")
    except ImportError as e:
        print(f"❌ spacy - ERRO: {e}")
        return False
    
    return True

def testar_modelo_spacy():
    """Testa se o modelo português do spaCy está disponível"""
    print("\n🌍 Testando modelo spaCy português...")
    
    try:
        import spacy
        nlp = spacy.load("pt_core_news_sm")
        print("✅ Modelo pt_core_news_sm carregado com sucesso")
        return True
    except OSError:
        print("❌ Modelo pt_core_news_sm não encontrado")
        print("💡 Execute: python -m spacy download pt_core_news_sm")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False

def testar_presidio():
    """Testa se o Presidio está funcionando"""
    print("\n🔒 Testando Microsoft Presidio...")
    
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        
        # Testar analyzer
        analyzer = AnalyzerEngine()
        print("✅ AnalyzerEngine criado com sucesso")
        
        # Testar anonymizer
        anonymizer = AnonymizerEngine()
        print("✅ AnonymizerEngine criado com sucesso")
        
        # Testar análise simples
        texto_teste = "Meu nome é João Silva e meu telefone é (11) 99999-9999"
        resultados = analyzer.analyze(text=texto_teste, entities=["PERSON", "PHONE_NUMBER"], language='pt')
        
        if resultados:
            print(f"✅ Análise funcionando - {len(resultados)} entidades detectadas")
            for resultado in resultados:
                print(f"   - {resultado.entity_type}: '{resultado.text}' (confiança: {resultado.score:.2f})")
        else:
            print("⚠️ Nenhuma entidade detectada no texto de teste")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Presidio: {e}")
        return False

def testar_anonimizador_core():
    """Testa se a classe AnonimizadorCore está funcionando"""
    print("\n🚀 Testando AnonimizadorCore...")
    
    try:
        from anonimizador_core import AnonimizadorCore
        
        anonimizador = AnonimizadorCore()
        print("✅ AnonimizadorCore criado com sucesso")
        
        # Testar validação de arquivo
        arquivo_valido = "teste.pdf"
        arquivo_invalido = "teste.txt"
        
        if anonimizador.validar_arquivo(arquivo_valido):
            print("✅ Validação de arquivo funcionando")
        else:
            print("❌ Validação de arquivo falhou")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no AnonimizadorCore: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 ========================================")
    print("   TESTE DO ANONIMIZAJUD - PRESIDIO")
    print("   ========================================")
    print()
    
    # Testar imports
    if not testar_imports():
        print("\n❌ Falha nos imports. Verifique a instalação.")
        return False
    
    # Testar modelo spaCy
    if not testar_modelo_spacy():
        print("\n❌ Falha no modelo spaCy. Execute a instalação.")
        return False
    
    # Testar Presidio
    if not testar_presidio():
        print("\n❌ Falha no Presidio. Verifique a instalação.")
        return False
    
    # Testar AnonimizadorCore
    if not testar_anonimizador_core():
        print("\n❌ Falha no AnonimizadorCore. Verifique o código.")
        return False
    
    print("\n🎉 ========================================")
    print("   TODOS OS TESTES PASSARAM!")
    print("   ========================================")
    print()
    print("✅ O AnonimizaJud com Presidio está funcionando perfeitamente!")
    print("🚀 Execute: python app_gradio.py")
    print()
    
    return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
