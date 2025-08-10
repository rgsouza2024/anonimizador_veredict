#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste dos novos padrões regex para CNH, SIAPE, CI e CIN
Demonstra como os padrões funcionam e detectam diferentes formatos
"""

import re

def testar_padroes_regex():
    """Testa todos os novos padrões regex implementados"""
    
    print("🔍 TESTE DOS NOVOS PADRÕES REGEX PARA ANONIMIZAÇÃO\n")
    
    # Padrões implementados
    padroes = {
        "CNH": [
            r"\bCNH\s*(?:nº|n\.)?\s*\d{11}\b",  # CNH formatado
            r"\b(?<![\w])\d{11}(?![\w])\b"       # CNH apenas números
        ],
        "SIAPE": [
            r"\bSIAPE\s*(?:nº|n\.)?\s*\d{7}\b",  # SIAPE formatado
            r"\b(?<![\w])\d{7}(?![\w])\b"        # SIAPE apenas números
        ],
        "CI": [
            r"\bCI\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b",  # CI formatado
            r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b"           # CI padrão
        ],
        "CIN": [
            r"\bCIN\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", # CIN formatado
            r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b"           # CIN padrão
        ]
    }
    
    # Textos de teste
    textos_teste = [
        # CNH
        "Minha CNH é 12345678901",
        "CNH nº 98765432109",
        "CNH n. 11122233344",
        "Carteira de habilitação: 55566677788",
        
        # SIAPE
        "Meu número SIAPE é 1234567",
        "SIAPE nº 7654321",
        "SIAPE n. 9998888",
        "Funcionário público SIAPE 1112222",
        
        # CI
        "Minha CI é 12345678-9",
        "CI nº 12.345.678-9",
        "CI n. 98.765.432-1",
        "Cédula de identidade: 11.222.333-4",
        
        # CIN
        "Minha CIN é 12345678-9",
        "CIN nº 12.345.678-9",
        "CIN n. 98.765.432-1",
        "Cédula de identidade nacional: 11.222.333-4",
        
        # Casos que NÃO devem ser detectados
        "Telefone: 12345678901",  # Não é CNH
        "CPF: 1234567",           # Não é SIAPE
        "RG: 12345678-9",         # Não é CI/CIN
        "Processo: 123456789"     # Não é nenhum dos documentos
    ]
    
    # Testa cada padrão
    for tipo_documento, regex_list in padroes.items():
        print(f"📋 {tipo_documento}:")
        
        for i, regex in enumerate(regex_list):
            print(f"   Padrão {i+1}: {regex}")
            
            for texto in textos_teste:
                matches = re.findall(regex, texto, re.IGNORECASE)
                if matches:
                    print(f"     ✅ '{texto}' → Detectado: {matches}")
            
            print()
    
    print("🎯 RESUMO DOS PADRÕES IMPLEMENTADOS:")
    print("   • CNH: Detecta números de 11 dígitos com ou sem prefixo 'CNH'")
    print("   • SIAPE: Detecta números de 7 dígitos com ou sem prefixo 'SIAPE'")
    print("   • CI: Detecta formato brasileiro padrão (XX.XXX.XXX-X) com ou sem prefixo 'CI'")
    print("   • CIN: Detecta formato brasileiro padrão (XX.XXX.XXX-X) com ou sem prefixo 'CIN'")
    print("\n💡 Os padrões usam context para evitar falsos positivos e scores diferentes para precisão")

if __name__ == "__main__":
    testar_padroes_regex()
