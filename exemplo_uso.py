#!/usr/bin/env python3
"""
Exemplo de uso da versão Gradio do AnonimizaJud
"""

import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importar o módulo anonimizador
sys.path.append(str(Path(__file__).parent.parent))

def exemplo_anonimizacao_texto():
    """Exemplo de anonimização de texto"""
    print("📝 Exemplo: Anonimização de Texto")
    print("=" * 50)
    
    try:
        from anonimizador import Anonimizador
        
        # Inicializar o anonimizador
        anonimizador = Anonimizador()
        
        # Texto de exemplo com dados sensíveis
        texto_exemplo = """
        PROCESSO Nº 123456/2024
        
        EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO
        
        JOÃO SILVA SANTOS, brasileiro, casado, portador da Cédula de Identidade RG nº 12.345.678-9 SSP/SP, 
        inscrito no CPF sob o nº 123.456.789-00, residente e domiciliado na Rua das Flores, nº 123, 
        Bairro Centro, CEP 12345-678, Município de São Paulo/SP, telefone (11) 99999-9999, 
        e-mail joao.silva@email.com, vem, respeitosamente, à presença de Vossa Excelência, 
        requerer a presente PETIÇÃO INICIAL, com fundamento no art. 319 do Código de Processo Civil.
        
        DADOS DO ADVOGADO:
        Nome: MARIA SANTOS OLIVEIRA
        OAB/SP: 123.456
        Endereço: Av. Paulista, 1000, São Paulo/SP
        CEP: 01310-100
        """
        
        print("📄 Texto Original:")
        print(texto_exemplo)
        print("\n" + "="*50)
        
        # Realizar anonimização
        print("🔒 Anonimizando texto...")
        resultado = anonimizador.anonimizar_texto(
            texto_exemplo,
            nivel_anonimizacao="medio",
            idioma="pt"
        )
        
        if resultado:
            texto_anonimizado = resultado.get('texto_anonimizado', '')
            entidades_detectadas = resultado.get('entidades_detectadas', [])
            estatisticas = resultado.get('estatisticas', {})
            
            print("✅ Texto Anonimizado:")
            print(texto_anonimizado)
            
            print(f"\n📊 Estatísticas:")
            print(f"• Entidades detectadas: {len(entidades_detectadas)}")
            print(f"• Palavras processadas: {estatisticas.get('palavras_processadas', 0)}")
            print(f"• Tempo de processamento: {estatisticas.get('tempo_processamento', 0):.2f}s")
            print(f"• Confiança média: {estatisticas.get('confianca_media', 0):.2f}%")
            
            print(f"\n🔍 Entidades Detectadas:")
            for i, entidade in enumerate(entidades_detectadas[:5], 1):  # Mostrar apenas as primeiras 5
                print(f"{i}. Tipo: {entidade.get('tipo', 'N/A')}")
                print(f"   Texto: {entidade.get('texto', 'N/A')}")
                print(f"   Confiança: {entidade.get('confianca', 0):.2f}%")
                print(f"   Posição: {entidade.get('posicao_inicio', 0)}-{entidade.get('posicao_fim', 0)}")
                print()
            
        else:
            print("❌ Erro na anonimização")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def exemplo_analise_entidades():
    """Exemplo de análise de entidades"""
    print("\n🔍 Exemplo: Análise de Entidades")
    print("=" * 50)
    
    try:
        from anonimizador import Anonimizador
        
        # Inicializar o anonimizador
        anonimizador = Anonimizador()
        
        # Texto de exemplo
        texto_exemplo = """
        O documento foi assinado por Dr. Carlos Mendes, OAB/SP 987.654, 
        CPF 987.654.321-00, residente na Rua Augusta, 500, São Paulo, CEP 01212-000.
        Telefone: (11) 88888-8888, e-mail: carlos.mendes@advocacia.com.br
        """
        
        print("📄 Texto para Análise:")
        print(texto_exemplo)
        print("\n" + "="*50)
        
        # Analisar entidades
        print("🔍 Analisando entidades...")
        resultado = anonimizador.analisar_entidades(texto_exemplo)
        
        if resultado:
            entidades = resultado.get('entidades_detectadas', [])
            
            if entidades:
                print(f"✅ {len(entidades)} entidades detectadas:")
                print()
                
                for i, entidade in enumerate(entidades, 1):
                    print(f"{i}. Tipo: {entidade.get('tipo', 'N/A')}")
                    print(f"   Texto: {entidade.get('texto', 'N/A')}")
                    print(f"   Confiança: {entidade.get('confianca', 0):.2f}%")
                    print(f"   Posição: {entidade.get('posicao_inicio', 0)}-{entidade.get('posicao_fim', 0)}")
                    print()
            else:
                print("ℹ️ Nenhuma entidade sensível detectada")
        else:
            print("❌ Erro na análise de entidades")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def exemplo_configuracao_llm():
    """Exemplo de configuração de modelo LLM"""
    print("\n🤖 Exemplo: Configuração de Modelo LLM")
    print("=" * 50)
    
    try:
        from anonimizador import Anonimizador
        
        # Inicializar o anonimizador
        anonimizador = Anonimizador()
        
        # Exemplo de configuração (sem chave real)
        modelo = "openai"
        chave_api = "sua_chave_api_aqui"  # Substitua pela sua chave real
        
        print(f"🔧 Configurando modelo: {modelo}")
        print(f"🔑 Chave API: {chave_api[:10]}..." if len(chave_api) > 10 else f"🔑 Chave API: {chave_api}")
        
        # Configurar modelo (comentado para não executar sem chave real)
        # sucesso = anonimizador.configurar_modelo_llm(modelo, chave_api)
        
        print("\n💡 Para usar este exemplo:")
        print("1. Obtenha uma chave de API válida")
        print("2. Descomente a linha de configuração")
        print("3. Substitua 'sua_chave_api_aqui' pela chave real")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def exemplo_estatisticas():
    """Exemplo de obtenção de estatísticas"""
    print("\n📊 Exemplo: Estatísticas do Sistema")
    print("=" * 50)
    
    try:
        from anonimizador import Anonimizador
        
        # Inicializar o anonimizador
        anonimizador = Anonimizador()
        
        # Obter estatísticas
        print("📈 Obtendo estatísticas do sistema...")
        stats = anonimizador.obter_estatisticas()
        
        if stats:
            print("✅ Estatísticas obtidas:")
            print(f"• Total de documentos processados: {stats.get('total_documentos', 0)}")
            print(f"• Total de entidades detectadas: {stats.get('total_entidades', 0)}")
            print(f"• Tempo médio de processamento: {stats.get('tempo_medio', 0):.2f}s")
            print(f"• Taxa de detecção: {stats.get('taxa_deteccao', 0):.2f}%")
            print(f"• Falsos positivos: {stats.get('falsos_positivos', 0):.2f}%")
            print(f"• Memória utilizada: {stats.get('memoria_utilizada', 0):.2f} MB")
            print(f"• Cache hit rate: {stats.get('cache_hit_rate', 0):.2f}%")
        else:
            print("ℹ️ Nenhuma estatística disponível no momento")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def main():
    """Função principal"""
    print("🚀 Exemplos de Uso - AnonimizaJud Gradio")
    print("=" * 60)
    print()
    
    exemplos = [
        ("Anonimização de Texto", exemplo_anonimizacao_texto),
        ("Análise de Entidades", exemplo_analise_entidades),
        ("Configuração de Modelo LLM", exemplo_configuracao_llm),
        ("Estatísticas do Sistema", exemplo_estatisticas)
    ]
    
    for i, (nome, funcao) in enumerate(exemplos, 1):
        print(f"{i}. {nome}")
    
    print("\n" + "="*60)
    
    # Executar todos os exemplos
    for nome, funcao in exemplos:
        try:
            funcao()
        except Exception as e:
            print(f"❌ Erro ao executar exemplo '{nome}': {str(e)}")
        
        print("\n" + "-"*60)
    
    print("\n🎉 Exemplos concluídos!")
    print("\n💡 Para usar a interface web:")
    print("   python app_gradio.py")
    print("\n💡 Para testar a instalação:")
    print("   python test_gradio.py")

if __name__ == "__main__":
    main()
