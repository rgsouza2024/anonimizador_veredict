# app_gradio.py

import os
import logging
import gradio as gr
from anonimizador_core import AnonimizadorCore # Apenas o Core é necessário

# Configurar logging
logging.basicConfig(
    level=logging.INFO, # Alterado para INFO para uma saída menos verbosa em produção
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# REMOVIDO: A função processar_documento que existia aqui foi removida
# pois a lógica agora está 100% no AnonimizadorCore.

def anonimizar_documento_interface(arquivo, modelo_llm, chave_api):
    """
    Função "ponte" que a interface Gradio chama.
    Ela é responsável por instanciar o Core e chamar o método de processamento.
    """
    try:
        if arquivo is None:
            logger.warning("Tentativa de processar sem arquivo.")
            return "❌ Por favor, selecione um arquivo para anonimizar."
        
        caminho_do_arquivo = arquivo.name
        logger.info(f"Processando arquivo: {caminho_do_arquivo}")
        
        # Verificar se o arquivo existe (boa prática)
        if not os.path.exists(caminho_do_arquivo):
            logger.error(f"Arquivo não encontrado no sistema: {caminho_do_arquivo}")
            return "❌ Arquivo não encontrado no sistema."
            
        # Inicializar o motor de anonimização
        anonimizador = AnonimizadorCore()
        
        # Processar o documento usando a lógica centralizada do Core
        # Note que não precisamos mais saber o tipo do arquivo aqui.
        logger.info(f"Iniciando processamento com o motor Core...")
        resultado = anonimizador.processar_documento(caminho_do_arquivo, modelo_llm, chave_api)
        
        if resultado.startswith("❌") or resultado.startswith("⚠️"):
            logger.error(f"Erro ou aviso no processamento: {resultado}")
        else:
            logger.info("Documento processado com sucesso.")
            
        return resultado
        
    except Exception as e:
        logger.exception("Erro inesperado durante a anonimização na interface.")
        return f"❌ Erro crítico durante a anonimização: {str(e)}"

# Configuração da interface (permanece praticamente a mesma)
with gr.Blocks(title="AnonimizaJud - Gradio", theme=gr.themes.Soft()) as interface:
    gr.Markdown("# 🚀 AnonimizaJud - Anonimizador de Documentos")
    gr.Markdown("### Versão Gradio - Interface Simplificada com Presidio Avançado")
    gr.Markdown("**🔒 Anonimização automática usando Microsoft Presidio com configuração avançada para português brasileiro**")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📤 **Upload e Configuração**")
            
            arquivo = gr.File(
                label="📄 Upload do Documento",
                file_types=[".pdf", ".txt", ".docx"], # Tipos de arquivo permitidos
                height=100
            )
            
            # Opcionais para futuras implementações com LLMs
            modelo_llm = gr.Dropdown(
                choices=["GPT-4", "Claude", "Gemini", "Groq", "Ollama"],
                value="GPT-4",
                label="🤖 Modelo LLM (opcional, não usado na anonimização Presidio)"
            )
            
            chave_api = gr.Textbox(
                label="🔑 Chave API (opcional)",
                type="password",
                placeholder="Digite sua chave API se o modelo exigir..."
            )
            
            btn_processar = gr.Button(
                "🚀 Anonimizar Documento",
                variant="primary",
                size="lg"
            )
            
            gr.Markdown("---")
            gr.Markdown("### ℹ️ **Como usar:**")
            gr.Markdown("1. 📤 Faça upload do seu documento (`.pdf`, `.txt` ou `.docx`).")
            gr.Markdown("2. 🚀 Clique em 'Anonimizar Documento'.")
            gr.Markdown("3. 📋 O resultado anonimizado aparecerá ao lado.")
        
        with gr.Column(scale=3):
            gr.Markdown("### 📋 **Resultado da Anonimização**")
            
            resultado_textbox = gr.Textbox(
                label="Resultado",
                lines=25,
                max_lines=30,
                interactive=False,
                show_label=False
            )
            
            gr.Markdown("---")
            gr.Markdown("### 🔍 **Sobre a Tecnologia (Microsoft Presidio):**")
            gr.Markdown("• **Detecção automática** de Nomes, CPFs, RGs, OABs, Endereços, etc.")
            gr.Markdown("• **Regras personalizadas** para o contexto jurídico e administrativo brasileiro.")
            gr.Markdown("• **Listas de exceções** para evitar a anonimização de termos comuns e nomes de locais públicos (estados, capitais).")

    # Eventos
    btn_processar.click(
        fn=anonimizar_documento_interface,
        inputs=[arquivo, modelo_llm, chave_api],
        outputs=resultado_textbox
    )

# Lançar a aplicação
if __name__ == "__main__":
    print("🚀 Iniciando a interface do AnonimizaJud...")
    # ... (bloco try/except para portas permanece o mesmo) ...
    try:
        interface.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=True)
    except OSError:
        print("⚠️ Porta 7860 ocupada, tentando porta 7861...")
        try:
            interface.launch(server_name="0.0.0.0", server_port=7861, share=False, debug=True)
        except OSError:
            print("⚠️ Portas 7860 e 7861 ocupadas, usando porta automática...")
            interface.launch(server_name="0.0.0.0", share=False, debug=True)