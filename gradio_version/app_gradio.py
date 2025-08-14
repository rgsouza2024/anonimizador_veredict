# app_gradio.py

import os
import logging
import gradio as gr
import tempfile
from datetime import datetime
from anonimizador_core import AnonimizadorCore

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variável global para armazenar o último resultado
ultimo_resultado = ""

def anonimizar_documento_interface(arquivo, modelo_llm, chave_api):
    """
    Função "ponte" que a interface Gradio chama.
    Ela é responsável por instanciar o Core e chamar o método de processamento.
    """
    global ultimo_resultado
    
    try:
        if arquivo is None:
            logger.warning("Tentativa de processar sem arquivo.")
            return "❌ Por favor, selecione um arquivo para anonimizar.", None, gr.update(visible=False), gr.update(visible=False)
        
        caminho_do_arquivo = arquivo.name
        logger.info(f"Processando arquivo: {caminho_do_arquivo}")
        
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_do_arquivo):
            logger.error(f"Arquivo não encontrado no sistema: {caminho_do_arquivo}")
            return "❌ Arquivo não encontrado no sistema.", None, gr.update(visible=False), gr.update(visible=False)
            
        # Inicializar o motor de anonimização
        anonimizador = AnonimizadorCore()
        
        # Processar o documento
        logger.info(f"Iniciando processamento com o motor Core...")
        resultado = anonimizador.processar_documento(caminho_do_arquivo, modelo_llm, chave_api)
        
        if resultado.startswith("❌") or resultado.startswith("⚠️"):
            logger.error(f"Erro ou aviso no processamento: {resultado}")
            return resultado, None, gr.update(visible=False), gr.update(visible=False)
        else:
            logger.info("Documento processado com sucesso.")
            ultimo_resultado = resultado
            
            # Criar arquivo temporário para download
            arquivo_download = criar_arquivo_download(resultado, caminho_do_arquivo)
            
            return resultado, arquivo_download, gr.update(visible=True), gr.update(visible=True)
        
    except Exception as e:
        logger.exception("Erro inesperado durante a anonimização na interface.")
        return f"❌ Erro crítico durante a anonimização: {str(e)}", None, gr.update(visible=False), gr.update(visible=False)

def criar_arquivo_download(texto_anonimizado, arquivo_original):
    """
    Cria um arquivo temporário com o texto anonimizado para download.
    """
    try:
        # Extrair nome base do arquivo original
        nome_base = os.path.splitext(os.path.basename(arquivo_original))[0]
        
        # Adicionar timestamp para evitar conflitos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar nome do arquivo anonimizado
        nome_arquivo = f"{nome_base}_anonimizado_{timestamp}.txt"
        
        # Criar arquivo temporário
        temp_dir = tempfile.gettempdir()
        caminho_completo = os.path.join(temp_dir, nome_arquivo)
        
        # Escrever conteúdo
        with open(caminho_completo, 'w', encoding='utf-8') as f:
            # Adicionar cabeçalho informativo
            f.write("=" * 60 + "\n")
            f.write("DOCUMENTO ANONIMIZADO - AnonimizaJud\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo original: {os.path.basename(arquivo_original)}\n")
            f.write("=" * 60 + "\n\n")
            f.write(texto_anonimizado)
            
        logger.info(f"Arquivo para download criado: {caminho_completo}")
        return caminho_completo
        
    except Exception as e:
        logger.error(f"Erro ao criar arquivo para download: {str(e)}")
        return None

def limpar_resultados():
    """
    Limpa os resultados e reseta a interface.
    """
    global ultimo_resultado
    ultimo_resultado = ""
    return "", None, gr.update(visible=False), gr.update(visible=False)



# Configuração da interface com tema mais moderno
with gr.Blocks(
    title="AnonimizaJud - Gradio",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .download-section {
        background-color: #f0f9ff;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    """
) as interface:
    gr.Markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>🚀 AnonimizaJud - Anonimizador de Documentos</h1>")
    gr.Markdown("")
        
    with gr.Row():
        # --- COLUNA DA ESQUERDA ---
        with gr.Column(scale=2):
            gr.Markdown("### 📤 **Upload e Configuração**")
            
            arquivo = gr.File(
                label="📄 Upload do Documento",
                file_types=[".pdf", ".txt", ".docx"],
                height=150
            )
            
            with gr.Accordion("⚙️ Configurações Avançadas (Opcional)", open=False):
                modelo_llm = gr.Dropdown(
                    choices=["GPT-4", "Claude", "Gemini", "Groq", "Ollama"],
                    value="GPT-4",
                    label="🤖 Modelo LLM (para futuras implementações)"
                )
                
                chave_api = gr.Textbox(
                    label="🔑 Chave API",
                    type="password",
                    placeholder="Digite sua chave API se necessário..."
                )
            
            with gr.Row():
                btn_processar = gr.Button(
                    "🚀 Anonimizar Documento",
                    variant="primary",
                    size="lg"
                )
                
                btn_limpar = gr.Button(
                    "🗑️ Limpar",
                    variant="secondary",
                    size="lg"
                )
            
            gr.Markdown("---")
            
            # Seção de Download (sem o botão copiar)
            with gr.Column(visible=False) as download_section:
                gr.Markdown("### 📥 **Download do Resultado**")
                
                arquivo_download = gr.File(
                    label="Arquivo Anonimizado",
                    interactive=False
                )
            
            gr.Markdown("---")
            gr.Markdown("### ℹ️ **Como usar:**")
            gr.Markdown("1. 📤 Faça upload do seu documento (`.pdf`, `.txt` ou `.docx`)")
            gr.Markdown("2. 🚀 Clique em 'Anonimizar Documento'")
            gr.Markdown("3. 📋 Visualize o resultado ao lado")
            gr.Markdown("4. 📥 Baixe o arquivo anonimizado ou copie o texto")
        
        # --- COLUNA DA DIREITA ---
        with gr.Column(scale=2):
            with gr.Row():
                gr.Markdown("### 📋 **Resultado da Anonimização**")
                gr.Button("📋 Copiar").click(
                    None, [], [],
                    js="""() => {
                        const textarea = document.querySelector('#resultado textarea');
                        if (textarea) {
                            navigator.clipboard.writeText(textarea.value);
                            alert('Texto copiado para a área de transferência!');
                        }
                    }"""
                )

            resultado_textbox = gr.Textbox(
                label="Texto Anonimizado",
                lines=25,
                max_lines=30,
                interactive=False,
                show_label=False, # Ocultamos o label original pois já temos um título
                elem_id="resultado"
            )
            
            with gr.Accordion("📊 Estatísticas da Anonimização", open=False):
                stats_output = gr.Markdown(
                    """
                    *Processe um documento para ver as estatísticas*
                    """
                )

    # --- LIGAÇÃO DOS EVENTOS ---
    btn_processar.click(
        fn=anonimizar_documento_interface,
        inputs=[arquivo, modelo_llm, chave_api],
        outputs=[resultado_textbox, arquivo_download, download_section]
    )
    
    btn_limpar.click(
        fn=limpar_resultados,
        inputs=[],
        outputs=[resultado_textbox, arquivo_download, download_section]
    )
    
    

# Lançar a aplicação
if __name__ == "__main__":
    print("Iniciando a interface do AnonimizaJud...")
    interface.launch(server_name="0.0.0.0", server_port=7860, show_error=True)