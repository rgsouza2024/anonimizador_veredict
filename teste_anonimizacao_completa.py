#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste completo para verificar a anonimização real
das expressões CNH, RG, SIAPE, CI e CIN usando Microsoft Presidio
"""

import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine, OperatorConfig

def testar_anonimizacao_presidio():
    """Testa a anonimização real usando Microsoft Presidio"""
    
    print("🧪 TESTE COMPLETO DE ANONIMIZAÇÃO COM MICROSOFT PRESIDIO")
    print("=" * 60)
    
    # 1. Criar o AnalyzerEngine
    print("1️⃣ Configurando AnalyzerEngine...")
    analyzer = AnalyzerEngine()
    
    # 2. Adicionar os reconhecedores específicos
    print("2️⃣ Adicionando reconhecedores...")
    
    # CNH
    cnh_patterns = [
        Pattern(name="cnh_formatado", regex=r"\bCNH\s*(?:nº|n\.)?\s*\d{11}\b", score=0.98),
        Pattern(name="cnh_apenas_numeros", regex=r"\b(?<![\w])\d{11}(?![\w])\b", score=0.85)
    ]
    cnh_recognizer = PatternRecognizer(
        supported_entity="CNH",
        name="CNHRecognizer",
        patterns=cnh_patterns
    )
    analyzer.registry.add_recognizer(cnh_recognizer)
    
    # SIAPE
    siape_patterns = [
        Pattern(name="siape_formatado", regex=r"\bSIAPE\s*(?:nº|n\.)?\s*\d{7}\b", score=0.98),
        Pattern(name="siape_apenas_numeros", regex=r"\b(?<![\w])\d{7}(?![\w])\b", score=0.85)
    ]
    siape_recognizer = PatternRecognizer(
        supported_entity="SIAPE",
        name="SIAPERecognizer",
        patterns=siape_patterns
    )
    analyzer.registry.add_recognizer(siape_recognizer)
    
    # CI
    ci_patterns = [
        Pattern(name="ci_formatado", regex=r"\bCI\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
        Pattern(name="ci_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90)
    ]
    ci_recognizer = PatternRecognizer(
        supported_entity="CI",
        name="CIRecognizer",
        patterns=ci_patterns
    )
    analyzer.registry.add_recognizer(ci_recognizer)
    
    # CIN
    cin_patterns = [
        Pattern(name="cin_formatado", regex=r"\bCIN\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
        Pattern(name="cin_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90)
    ]
    cin_recognizer = PatternRecognizer(
        supported_entity="CIN",
        name="CINRecognizer",
        patterns=cin_patterns
    )
    analyzer.registry.add_recognizer(cin_recognizer)
    
    # RG
    rg_patterns = [
        Pattern(name="rg_formatado", regex=r"\bRG\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
        Pattern(name="rg_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90)
    ]
    rg_recognizer = PatternRecognizer(
        supported_entity="RG",
        name="RGRecognizer",
        patterns=rg_patterns
    )
    analyzer.registry.add_recognizer(rg_recognizer)
    
    print("   ✅ Reconhecedores adicionados com sucesso!")
    
    # 3. Configurar o AnonymizerEngine
    print("3️⃣ Configurando AnonymizerEngine...")
    anonymizer = AnonymizerEngine()
    
    # 4. Definir operadores de anonimização
    operadores = {
        "CNH": OperatorConfig("replace", {"new_value": "***"}),
        "SIAPE": OperatorConfig("replace", {"new_value": "***"}),
        "CI": OperatorConfig("replace", {"new_value": "***"}),
        "CIN": OperatorConfig("replace", {"new_value": "***"}),
        "RG": OperatorConfig("replace", {"new_value": "***"})
    }
    
    print("   ✅ Operadores configurados!")
    
    # 5. Textos de teste
    textos_teste = [
        "O motorista apresentou sua CNH 12345678901",
        "Servidor com SIAPE 1234567",
        "Portador da CI nº 12.345.678-9",
        "Documento CIN 98.765.432-1",
        "RG nº 11.222.333-4",
        "CNH nº 98765432109 válida",
        "SIAPE n. 7654321 ativo",
        "CI 87654321-0 em dia",
        "CIN 12.345.678-9 válido",
        "RG 11.222.333-4 atualizado"
    ]
    
    print("\n4️⃣ TEXTOS DE TESTE:")
    print("-" * 40)
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"{i:2d}. {texto}")
    
    # 6. Executar análise e anonimização
    print("\n5️⃣ EXECUTANDO ANÁLISE E ANONIMIZAÇÃO:")
    print("-" * 40)
    
    total_processado = 0
    total_esperado = len(textos_teste)
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"\n📝 Texto {i}: {texto}")
        
        # Análise
        try:
            resultados = analyzer.analyze(
                text=texto,
                language="en",
                entities=list(operadores.keys())
            )
            
            if resultados:
                print(f"   🔍 Entidades detectadas: {len(resultados)}")
                for resultado in resultados:
                    print(f"      - {resultado.entity_type}: '{texto[resultado.start:resultado.end]}' (score: {resultado.score:.2f})")
                
                # Anonimização
                resultado_anonimizacao = anonymizer.anonymize(
                    text=texto,
                    analyzer_results=resultados,
                    operators=operadores
                )
                
                texto_anonimizado = resultado_anonimizacao.text
                print(f"   ✅ ANONIMIZADO: {texto_anonimizado}")
                
                # Verificar se foi substituído por "***"
                if "***" in texto_anonimizado:
                    total_processado += 1
                    print(f"   🎯 SUBSTITUIÇÃO CONFIRMADA: '***' encontrado!")
                else:
                    print(f"   ❌ PROBLEMA: '***' NÃO encontrado!")
                    
            else:
                print(f"   ❌ NENHUMA entidade detectada!")
                
        except Exception as e:
            print(f"   💥 ERRO: {e}")
    
    # 7. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL:")
    print("=" * 60)
    print(f"Total de textos: {total_esperado}")
    print(f"Processados com sucesso: {total_processado}")
    print(f"Taxa de sucesso: {(total_processado/total_esperado)*100:.1f}%")
    
    if total_processado == total_esperado:
        print("\n🎉 SUCESSO TOTAL! Todas as expressões foram anonimizadas com '***'!")
    else:
        print(f"\n⚠️  PROBLEMA: {total_esperado - total_processado} textos não foram anonimizados corretamente.")
    
    # 8. Teste adicional com texto complexo
    print("\n6️⃣ TESTE COM TEXTO COMPLEXO:")
    print("-" * 40)
    
    texto_complexo = """
    O servidor João Silva, portador da CNH 12345678901,
    apresentou seu SIAPE 1234567 e CI nº 12.345.678-9.
    Também possui RG 11.222.333-4 e CIN 98.765.432-1.
    """
    
    print("ANTES:")
    print(texto_complexo)
    
    try:
        resultados = analyzer.analyze(
            text=texto_complexo,
            language="en",
            entities=list(operadores.keys())
        )
        
        if resultados:
            resultado_anonimizacao = anonymizer.anonymize(
                text=texto_complexo,
                analyzer_results=resultados,
                operators=operadores
            )
            
            print("DEPOIS (anonimizado):")
            print(resultado_anonimizacao.text)
            
            # Contar ocorrências de "***"
            ocorrencias = resultado_anonimizacao.text.count("***")
            print(f"\n🎯 Total de substituições por '***': {ocorrencias}")
            
        else:
            print("❌ Nenhuma entidade detectada no texto complexo!")
            
    except Exception as e:
        print(f"💥 ERRO no texto complexo: {e}")

if __name__ == "__main__":
    testar_anonimizacao_presidio()
