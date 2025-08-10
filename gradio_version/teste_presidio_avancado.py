#!/usr/bin/env python3
"""
Teste da implementação avançada do Microsoft Presidio para anonimização
"""

import os
import sys
from anonimizador_core import AnonimizadorCore

def testar_presidio_avancado():
    """Testa a funcionalidade avançada do Presidio"""
    
    print("🧪 Testando Microsoft Presidio Avançado...")
    print("=" * 60)
    
    try:
        # Inicializar anonimizador
        anonimizador = AnonimizadorCore()
        print("✅ Anonimizador inicializado com sucesso")
        
        # Testar texto com informações brasileiras
        texto_teste = """
        PROCESSO Nº 1234567-89.2023.8.26.0100
        
        EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JOÃO SILVA SANTOS
        JUIZ(A) DE DIREITO DA 2ª VARA CÍVEL DA COMARCA DE SÃO PAULO - SP
        
        REQUERENTE: MARIA OLIVEIRA COSTA
        CPF: 123.456.789-00
        OAB: 123456/SP
        ENDEREÇO: Rua das Flores, 123, Centro, São Paulo - SP, CEP: 01234-567
        
        REQUERIDO: PEDRO SANTOS LIMA
        CNPJ: 12.345.678/0001-90
        ENDEREÇO: Av. Paulista, 1000, Bela Vista, São Paulo - SP
        
        VISTOS, os autos em que pugnam pela presente ação de indenização por danos morais.
        
        DECISÃO
        
        Ante o exposto, DEFIRO o pedido liminar, determinando que o requerido se abstenha de praticar os atos ilícitos denunciados.
        
        Publique-se. Registre-se. Intime-se.
        
        São Paulo, 15 de dezembro de 2023.
        
        JOÃO SILVA SANTOS
        Juiz de Direito
        """
        
        print("\n📝 Texto de teste:")
        print("-" * 40)
        print(texto_teste[:200] + "...")
        
        # Testar anonimização
        print("\n🔒 Testando anonimização...")
        resultado = anonimizador.anonimizar_texto(texto_teste)
        
        print("\n✅ Resultado da anonimização:")
        print("-" * 40)
        print(resultado)
        
        # Verificar entidades detectadas
        print("\n🔍 Verificando entidades detectadas...")
        entidades = anonimizador.analisar_entidades(texto_teste)
        
        if entidades:
            print(f"✅ {len(entidades)} entidades detectadas:")
            for entidade in entidades[:10]:  # Mostrar apenas as primeiras 10
                print(f"   • {entidade.entity_type}: '{entidade.text}' (score: {entidade.score:.2f})")
        else:
            print("❌ Nenhuma entidade detectada")
        
        print("\n🎉 Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

def testar_reconhecedores_personalizados():
    """Testa os reconhecedores regex personalizados"""
    
    print("\n🔍 Testando reconhecedores personalizados...")
    print("=" * 60)
    
    try:
        anonimizador = AnonimizadorCore()
        
        # Testar CPF
        cpf_teste = "123.456.789-00"
        resultado_cpf = anonimizador.anonimizar_texto(cpf_teste)
        print(f"CPF: {cpf_teste} -> {resultado_cpf}")
        
        # Testar OAB
        oab_teste = "OAB 123456/SP"
        resultado_oab = anonimizador.anonimizar_texto(oab_teste)
        print(f"OAB: {oab_teste} -> {resultado_oab}")
        
        # Testar CEP
        cep_teste = "01234-567"
        resultado_cep = anonimizador.anonimizar_texto(cep_teste)
        print(f"CEP: {cep_teste} -> {resultado_cep}")
        
        # Testar telefone
        telefone_teste = "(11) 99999-9999"
        resultado_telefone = anonimizador.anonimizar_texto(telefone_teste)
        print(f"Telefone: {telefone_teste} -> {resultado_telefone}")
        
        print("✅ Teste dos reconhecedores concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste dos reconhecedores: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do Microsoft Presidio Avançado")
    print("=" * 60)
    
    # Testar funcionalidade principal
    testar_presidio_avancado()
    
    # Testar reconhecedores personalizados
    testar_reconhecedores_personalizados()
    
    print("\n" + "=" * 60)
    print("🎯 Todos os testes foram executados!")
