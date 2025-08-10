import gradio as gr
import os
import sys
from pathlib import Path
import json
import time
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import io

# Adicionar o diretório pai ao path para importar o módulo anonimizador
sys.path.append(str(Path(__file__).parent.parent))
from anonimizador import Anonimizador

# Configurações globais
TITLE = "🔒 AnonimizaJud - Sistema de Anonimização para Documentos Jurídicos"
DESCRIPTION = """
Sistema inteligente de anonimização de documentos jurídicos utilizando IA para proteger dados sensíveis.
Desenvolvido para uso em processos judiciais, garantindo conformidade com LGPD e sigilo profissional.
"""

# Inicializar o anonimizador
anonimizador = Anonimizador()

def create_header():
    """Cria o cabeçalho da aplicação"""
    return gr.HTML("""
    <div style="
        background: linear-gradient(135deg, #1f4e79 0%, #2d5a8b 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            🔒 AnonimizaJud
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Sistema de Anonimização para Documentos Jurídicos
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">
            Proteção inteligente de dados sensíveis com conformidade LGPD
        </p>
    </div>
    """)

def anonimizar_texto(texto, modelo_llm, chave_api, nivel_anonimizacao, idioma):
    """Função para anonimizar texto"""
    try:
        if not texto.strip():
            return "❌ Por favor, insira um texto para anonimizar.", None, None
        
        # Configurar o modelo LLM
        if chave_api:
            anonimizador.configurar_modelo_llm(modelo_llm, chave_api)
        
        # Realizar anonimização
        resultado = anonimizador.anonimizar_texto(
            texto, 
            nivel_anonimizacao=nivel_anonimizacao,
            idioma=idioma
        )
        
        if resultado:
            texto_anonimizado = resultado.get('texto_anonimizado', '')
            entidades_detectadas = resultado.get('entidades_detectadas', [])
            estatisticas = resultado.get('estatisticas', {})
            
            # Formatar estatísticas
            stats_text = f"""
            📊 **Estatísticas da Anonimização:**
            • Entidades detectadas: {len(entidades_detectadas)}
            • Palavras processadas: {estatisticas.get('palavras_processadas', 0)}
            • Tempo de processamento: {estatisticas.get('tempo_processamento', 0):.2f}s
            • Confiança média: {estatisticas.get('confianca_media', 0):.2f}%
            """
            
            return texto_anonimizado, stats_text, entidades_detectadas
        else:
            return "❌ Erro na anonimização. Verifique os parâmetros.", None, None
            
    except Exception as e:
        return f"❌ Erro: {str(e)}", None, None

def anonimizar_arquivo(arquivo, modelo_llm, chave_api, nivel_anonimizacao, idioma):
    """Função para anonimizar arquivo"""
    try:
        if not arquivo:
            return "❌ Por favor, selecione um arquivo para anonimizar.", None, None, None
        
        # Ler o arquivo
        if arquivo.name.endswith('.txt'):
            with open(arquivo.name, 'r', encoding='utf-8') as f:
                texto = f.read()
        elif arquivo.name.endswith('.pdf'):
            # Aqui você pode adicionar lógica para PDF se necessário
            return "❌ Suporte a PDF será implementado em breve.", None, None, None
        else:
            return "❌ Formato de arquivo não suportado. Use arquivos .txt", None, None, None
        
        # Configurar o modelo LLM
        if chave_api:
            anonimizador.configurar_modelo_llm(modelo_llm, chave_api)
        
        # Realizar anonimização
        resultado = anonimizador.anonimizar_texto(
            texto, 
            nivel_anonimizacao=nivel_anonimizacao,
            idioma=idioma
        )
        
        if resultado:
            texto_anonimizado = resultado.get('texto_anonimizado', '')
            entidades_detectadas = resultado.get('entidades_detectadas', [])
            estatisticas = resultado.get('estatisticas', {})
            
            # Formatar estatísticas
            stats_text = f"""
            📊 **Estatísticas da Anonimização:**
            • Entidades detectadas: {len(entidades_detectadas)}
            • Palavras processadas: {estatisticas.get('palavras_processadas', 0)}
            • Tempo de processamento: {estatisticas.get('tempo_processamento', 0):.2f}s
            • Confiança média: {estatisticas.get('confianca_media', 0):.2f}%
            """
            
            # Criar arquivo de saída
            nome_arquivo_saida = f"anonimizado_{Path(arquivo.name).stem}.txt"
            with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
                f.write(texto_anonimizado)
            
            return texto_anonimizado, stats_text, entidades_detectadas, nome_arquivo_saida
        else:
            return "❌ Erro na anonimização. Verifique os parâmetros.", None, None, None
            
    except Exception as e:
        return f"❌ Erro: {str(e)}", None, None, None

def analisar_entidades(texto):
    """Função para analisar entidades em um texto"""
    try:
        if not texto.strip():
            return "❌ Por favor, insira um texto para análise.", None
        
        resultado = anonimizador.analisar_entidades(texto)
        
        if resultado:
            entidades = resultado.get('entidades_detectadas', [])
            
            if entidades:
                # Criar tabela de entidades
                df = pd.DataFrame(entidades)
                return df, f"✅ {len(entidades)} entidades detectadas no texto."
            else:
                return None, "ℹ️ Nenhuma entidade sensível detectada no texto."
        else:
            return None, "❌ Erro na análise de entidades."
            
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"

def configurar_modelo_llm(modelo, chave_api):
    """Função para configurar o modelo LLM"""
    try:
        if not chave_api:
            return "❌ Por favor, insira uma chave de API válida."
        
        sucesso = anonimizador.configurar_modelo_llm(modelo, chave_api)
        
        if sucesso:
            return f"✅ Modelo {modelo} configurado com sucesso!"
        else:
            return f"❌ Erro ao configurar o modelo {modelo}."
            
    except Exception as e:
        return f"❌ Erro: {str(e)}"

def obter_estatisticas():
    """Função para obter estatísticas do sistema"""
    try:
        stats = anonimizador.obter_estatisticas()
        
        if stats:
            stats_text = f"""
            📈 **Estatísticas do Sistema:**
            
            🔍 **Análises Realizadas:**
            • Total de documentos processados: {stats.get('total_documentos', 0)}
            • Total de entidades detectadas: {stats.get('total_entidades', 0)}
            • Tempo médio de processamento: {stats.get('tempo_medio', 0):.2f}s
            
            🎯 **Precisão:**
            • Taxa de detecção: {stats.get('taxa_deteccao', 0):.2f}%
            • Falsos positivos: {stats.get('falsos_positivos', 0):.2f}%
            
            💾 **Recursos:**
            • Memória utilizada: {stats.get('memoria_utilizada', 0):.2f} MB
            • Cache hit rate: {stats.get('cache_hit_rate', 0):.2f}%
            """
            return stats_text
        else:
            return "ℹ️ Nenhuma estatística disponível no momento."
            
    except Exception as e:
        return f"❌ Erro ao obter estatísticas: {str(e)}"

def limpar_cache():
    """Função para limpar o cache do sistema"""
    try:
        anonimizador.limpar_cache()
        return "✅ Cache limpo com sucesso!"
    except Exception as e:
        return f"❌ Erro ao limpar cache: {str(e)}"

def exportar_resultado(texto_anonimizado, formato):
    """Função para exportar resultado"""
    try:
        if not texto_anonimizado or texto_anonimizado.startswith("❌"):
            return None, "❌ Nenhum texto anonimizado para exportar."
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == "TXT":
            nome_arquivo = f"anonimizado_{timestamp}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(texto_anonimizado)
            return nome_arquivo, f"✅ Arquivo exportado: {nome_arquivo}"
        
        elif formato == "JSON":
            nome_arquivo = f"anonimizado_{timestamp}.json"
            dados = {
                "texto_anonimizado": texto_anonimizado,
                "timestamp": timestamp,
                "versao": "1.0"
            }
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            return nome_arquivo, f"✅ Arquivo exportado: {nome_arquivo}"
        
        else:
            return None, "❌ Formato não suportado."
            
    except Exception as e:
        return None, f"❌ Erro ao exportar: {str(e)}"

# Criar a interface Gradio
def create_interface():
    """Cria a interface principal da aplicação"""
    
    with gr.Blocks(
        title=TITLE,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate"
        ),
        css="""
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        """
    ) as interface:
        
        # Cabeçalho
        create_header()
        
        # Abas principais
        with gr.Tabs():
            
            # Aba: Anonimização de Texto
            with gr.Tab("📝 Anonimização de Texto"):
                gr.Markdown("### Anonimize texto diretamente na interface")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        texto_input = gr.Textbox(
                            label="📄 Texto para Anonimizar",
                            placeholder="Cole aqui o texto que deseja anonimizar...",
                            lines=10,
                            max_lines=20
                        )
                        
                        with gr.Row():
                            modelo_llm = gr.Dropdown(
                                choices=["openai", "claude", "gemini", "groq", "ollama"],
                                value="openai",
                                label="🤖 Modelo LLM",
                                info="Selecione o modelo de IA para anonimização"
                            )
                            
                            nivel_anonimizacao = gr.Dropdown(
                                choices=["baixo", "medio", "alto"],
                                value="medio",
                                label="🛡️ Nível de Anonimização",
                                info="Nível de proteção dos dados"
                            )
                        
                        with gr.Row():
                            idioma = gr.Dropdown(
                                choices=["pt", "en", "es"],
                                value="pt",
                                label="🌍 Idioma",
                                info="Idioma do texto"
                            )
                            
                            chave_api = gr.Textbox(
                                label="🔑 Chave da API",
                                placeholder="Insira sua chave de API (opcional)",
                                type="password"
                            )
                        
                        btn_anonimizar = gr.Button(
                            "🚀 Anonimizar Texto",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        texto_output = gr.Textbox(
                            label="✅ Texto Anonimizado",
                            lines=10,
                            max_lines=20,
                            interactive=False
                        )
                        
                        estatisticas_output = gr.Markdown(
                            label="📊 Estatísticas",
                            value=""
                        )
                        
                        with gr.Row():
                            formato_export = gr.Dropdown(
                                choices=["TXT", "JSON"],
                                value="TXT",
                                label="📁 Formato de Exportação"
                            )
                            
                            btn_exportar = gr.Button(
                                "💾 Exportar Resultado",
                                variant="secondary"
                            )
                        
                        arquivo_exportado = gr.File(
                            label="📄 Arquivo Exportado",
                            visible=False
                        )
                        
                        msg_exportacao = gr.Markdown("")
                
                # Conectar eventos
                btn_anonimizar.click(
                    fn=anonimizar_texto,
                    inputs=[texto_input, modelo_llm, chave_api, nivel_anonimizacao, idioma],
                    outputs=[texto_output, estatisticas_output]
                )
                
                btn_exportar.click(
                    fn=exportar_resultado,
                    inputs=[texto_output, formato_export],
                    outputs=[arquivo_exportado, msg_exportacao]
                )
            
            # Aba: Anonimização de Arquivo
            with gr.Tab("📁 Anonimização de Arquivo"):
                gr.Markdown("### Anonimize arquivos de texto")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        arquivo_input = gr.File(
                            label="📁 Selecionar Arquivo",
                            file_types=[".txt"],
                            file_count="single"
                        )
                        
                        with gr.Row():
                            modelo_llm_arquivo = gr.Dropdown(
                                choices=["openai", "claude", "gemini", "groq", "ollama"],
                                value="openai",
                                label="🤖 Modelo LLM"
                            )
                            
                            nivel_anonimizacao_arquivo = gr.Dropdown(
                                choices=["baixo", "medio", "alto"],
                                value="medio",
                                label="🛡️ Nível de Anonimização"
                            )
                        
                        with gr.Row():
                            idioma_arquivo = gr.Dropdown(
                                choices=["pt", "en", "es"],
                                value="pt",
                                label="🌍 Idioma"
                            )
                            
                            chave_api_arquivo = gr.Textbox(
                                label="🔑 Chave da API",
                                placeholder="Insira sua chave de API (opcional)",
                                type="password"
                            )
                        
                        btn_anonimizar_arquivo = gr.Button(
                            "🚀 Anonimizar Arquivo",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        texto_arquivo_output = gr.Textbox(
                            label="✅ Texto Anonimizado",
                            lines=10,
                            max_lines=20,
                            interactive=False
                        )
                        
                        estatisticas_arquivo_output = gr.Markdown(
                            label="📊 Estatísticas",
                            value=""
                        )
                        
                        arquivo_saida = gr.File(
                            label="📄 Arquivo de Saída",
                            visible=False
                        )
                
                # Conectar eventos
                btn_anonimizar_arquivo.click(
                    fn=anonimizar_arquivo,
                    inputs=[arquivo_input, modelo_llm_arquivo, chave_api_arquivo, nivel_anonimizacao_arquivo, idioma_arquivo],
                    outputs=[texto_arquivo_output, estatisticas_arquivo_output, arquivo_saida]
                )
            
            # Aba: Análise de Entidades
            with gr.Tab("🔍 Análise de Entidades"):
                gr.Markdown("### Analise entidades sensíveis em um texto")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        texto_analise = gr.Textbox(
                            label="📄 Texto para Análise",
                            placeholder="Cole aqui o texto para análise de entidades...",
                            lines=8,
                            max_lines=15
                        )
                        
                        btn_analisar = gr.Button(
                            "🔍 Analisar Entidades",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        tabela_entidades = gr.DataFrame(
                            label="📊 Entidades Detectadas",
                            headers=["Tipo", "Texto", "Confiança", "Posição"],
                            visible=False
                        )
                        
                        msg_analise = gr.Markdown("")
                
                # Conectar eventos
                btn_analisar.click(
                    fn=analisar_entidades,
                    inputs=[texto_analise],
                    outputs=[tabela_entidades, msg_analise]
                )
            
            # Aba: Configurações
            with gr.Tab("⚙️ Configurações"):
                gr.Markdown("### Configure o sistema e modelos")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🤖 Configuração de Modelo LLM")
                        
                        modelo_config = gr.Dropdown(
                            choices=["openai", "claude", "gemini", "groq", "ollama"],
                            value="openai",
                            label="Modelo"
                        )
                        
                        chave_api_config = gr.Textbox(
                            label="Chave da API",
                            placeholder="Insira sua chave de API",
                            type="password"
                        )
                        
                        btn_configurar = gr.Button(
                            "🔧 Configurar Modelo",
                            variant="primary"
                        )
                        
                        msg_config = gr.Markdown("")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("#### 🛠️ Manutenção do Sistema")
                        
                        btn_estatisticas = gr.Button(
                            "📊 Ver Estatísticas",
                            variant="secondary"
                        )
                        
                        btn_limpar_cache = gr.Button(
                            "🧹 Limpar Cache",
                            variant="secondary"
                        )
                        
                        msg_sistema = gr.Markdown("")
                
                # Conectar eventos
                btn_configurar.click(
                    fn=configurar_modelo_llm,
                    inputs=[modelo_config, chave_api_config],
                    outputs=[msg_config]
                )
                
                btn_estatisticas.click(
                    fn=obter_estatisticas,
                    outputs=[msg_sistema]
                )
                
                btn_limpar_cache.click(
                    fn=limpar_cache,
                    outputs=[msg_sistema]
                )
            
            # Aba: Sobre
            with gr.Tab("ℹ️ Sobre"):
                gr.Markdown("""
                ## 🔒 AnonimizaJud - Sistema de Anonimização para Documentos Jurídicos
                
                ### 📋 Descrição
                O AnonimizaJud é um sistema inteligente de anonimização de documentos jurídicos que utiliza 
                tecnologias de Inteligência Artificial para proteger dados sensíveis, garantindo conformidade 
                com a LGPD e sigilo profissional.
                
                ### 🚀 Funcionalidades Principais
                - **Anonimização Inteligente**: Detecta e protege automaticamente dados sensíveis
                - **Múltiplos Modelos de IA**: Suporte a OpenAI, Claude, Gemini, Groq e Ollama
                - **Análise de Entidades**: Identifica CPF, OAB, CEP, CNH, SIAPE e outros dados sensíveis
                - **Processamento de Arquivos**: Suporte a arquivos de texto
                - **Exportação**: Múltiplos formatos de saída
                
                ### 🛡️ Recursos de Segurança
                - Detecção automática de entidades sensíveis
                - Múltiplos níveis de anonimização
                - Cache seguro para otimização
                - Logs de auditoria
                
                ### 🔧 Tecnologias Utilizadas
                - **Microsoft Presidio**: Framework de anonimização
                - **SpaCy**: Processamento de linguagem natural
                - **Gradio**: Interface web moderna
                - **Python**: Linguagem de programação
                
                ### 📚 Casos de Uso
                - Documentos judiciais
                - Petições e recursos
                - Laudos periciais
                - Contratos e acordos
                - Relatórios confidenciais
                
                ### 📞 Suporte
                Para dúvidas ou suporte técnico, entre em contato com a equipe de desenvolvimento.
                
                ---
                **Versão**: 1.0.0 | **Desenvolvido com** ❤️ para a comunidade jurídica
                """)
        
        # Rodapé
        gr.Markdown("---")
        gr.Markdown(
            "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
            "🔒 AnonimizaJud - Sistema de Anonimização para Documentos Jurídicos | "
            "Desenvolvido com ❤️ para a comunidade jurídica"
            "</div>"
        )
    
    return interface

# Função principal
if __name__ == "__main__":
    # Criar e lançar a interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True,
        quiet=False
    )
