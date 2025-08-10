#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a substituição por "***" 
dos novos padrões de anonimização
"""

import re

def testar_substituicao_asteriscos():
    """Testa se os padrões regex estão detectando corretamente os documentos"""
    
    print("🧪 TESTE DE SUBSTITUIÇÃO POR '***'")
    print("=" * 50)
    
    # Padrões regex implementados
    padroes = {
        "CNH": [
            r"\bCNH\s*(?:nº|n\.)?\s*\d{11}\b",  # CNH formatado
            r"\b(?<![\w])\d{11}(?![\w])\b"       # CNH apenas números
        ],
        "SIAPE": [
            r"\bSIAPE\s*(?:nº|n\.)?\s*\d{7}\b",  # SIAPE formatado
            r"\b(?<![\w])\d{7}(?![\w])\b"         # SIAPE apenas números
        ],
        "CI": [
            r"\bCI\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b",  # CI formatado
            r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b"           # CI padrão
        ],
        "CIN": [
            r"\bCIN\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", # CIN formatado
            r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b"           # CIN padrão
        ],
        "RG": [
            r"\bRG\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b",  # RG formatado
            r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b"           # RG padrão
        ]
    }
    
    # Textos de teste
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
    
    print("📋 TEXTOS DE TESTE:")
    print("-" * 30)
    
    for i, texto in enumerate(textos_teste, 1):
        print(f"{i:2d}. {texto}")
    
    print("\n🔍 RESULTADOS DA DETECÇÃO:")
    print("-" * 30)
    
    total_detectado = 0
    total_esperado = len(textos_teste)
    
    for texto in textos_teste:
        detectado = False
        tipo_detectado = None
        
        # Testa cada padrão
        for tipo, padrao_list in padroes.items():
            for padrao in padrao_list:
                if re.search(padrao, texto, re.IGNORECASE):
                    detectado = True
                    tipo_detectado = tipo
                    break
            if detectado:
                break
        
        if detectado:
            total_detectado += 1
            # Simula a substituição por "***"
            texto_anonimizado = re.sub(r'\b(?:CNH|SIAPE|CI|CIN|RG)\s*(?:nº|n\.)?\s*[\d.\-]+\b', '***', texto)
            texto_anonimizado = re.sub(r'\b\d{11}\b', '***', texto_anonimizado)  # CNH
            texto_anonimizado = re.sub(r'\b\d{7}\b', '***', texto_anonimizado)   # SIAPE
            texto_anonimizado = re.sub(r'\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b', '***', texto_anonimizado)  # CI/CIN/RG
            
            print(f"✅ {tipo_detectado}: {texto}")
            print(f"   → {texto_anonimizado}")
        else:
            print(f"❌ Não detectado: {texto}")
    
    print("\n📊 RESUMO:")
    print("-" * 30)
    print(f"Total de textos: {total_esperado}")
    print(f"Detectados: {total_detectado}")
    print(f"Taxa de sucesso: {(total_detectado/total_esperado)*100:.1f}%")
    
    if total_detectado == total_esperado:
        print("🎉 Todos os padrões foram detectados com sucesso!")
    else:
        print("⚠️  Alguns padrões não foram detectados. Verifique os regex.")
    
    print("\n💡 EXEMPLO DE ANONIMIZAÇÃO COMPLETA:")
    print("-" * 40)
    
    texto_exemplo = """
    O servidor João Silva, portador da CNH 12345678901,
    apresentou seu SIAPE 1234567 e CI nº 12.345.678-9.
    Também possui RG 11.222.333-4 e CIN 98.765.432-1.
    """
    
    print("ANTES:")
    print(texto_exemplo)
    
    # Aplica todas as substituições
    texto_anonimizado = texto_exemplo
    for tipo, padrao_list in padroes.items():
        for padrao in padrao_list:
            texto_anonimizado = re.sub(padrao, '***', texto_anonimizado, flags=re.IGNORECASE)
    
    print("DEPOIS (com '***'):")
    print(texto_anonimizado)

if __name__ == "__main__":
    testar_substituicao_asteriscos()
