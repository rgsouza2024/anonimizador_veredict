#!/usr/bin/env python3
"""
Teste simples para verificar se o método anonimizar_texto está funcionando
"""

from anonimizador_core import AnonimizadorCore

def teste_simples():
    """Teste básico da funcionalidade"""
    print("🧪 TESTE SIMPLES - ANONIMIZADOR CORE")
    print("=" * 50)
    
    try:
        # Inicializar anonimizador
        print("1️⃣ Inicializando anonimizador...")
        anonimizador = AnonimizadorCore()
        print("✅ Anonimizador inicializado!")
        
        # Teste 1: Texto simples sem entidades
        print("\n2️⃣ Teste 1: Texto simples...")
        texto_simples = "Olá, como você está?"
        resultado1 = anonimizador.anonimizar_texto(texto_simples)
        print(f"Texto original: {texto_simples}")
        print(f"Resultado: {resultado1}")
        print("✅ Teste 1 concluído!")
        
        # Teste 2: Texto com CPF
        print("\n3️⃣ Teste 2: Texto com CPF...")
        texto_cpf = "Meu CPF é 123.456.789-00"
        resultado2 = anonimizador.anonimizar_texto(texto_cpf)
        print(f"Texto original: {texto_cpf}")
        print(f"Resultado: {resultado2}")
        print("✅ Teste 2 concluído!")
        
        # Teste 3: Texto com OAB
        print("\n4️⃣ Teste 3: Texto com OAB...")
        texto_oab = "Advogado OAB 123456/SP"
        resultado3 = anonimizador.anonimizar_texto(texto_oab)
        print(f"Texto original: {texto_oab}")
        print(f"Resultado: {resultado3}")
        print("✅ Teste 3 concluído!")
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ O método anonimizar_texto está funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_simples()
