# ...existing code...
def processar_documento(self, caminho_arquivo: str, modelo: str, chave_api: str = "") -> str:
    """Processa um documento para anonimização usando Presidio com configuração avançada"""
    try:
        # Detectar tipo de arquivo e extrair texto
        if caminho_arquivo.lower().endswith('.pdf'):
            texto = self.extrair_texto_pdf(caminho_arquivo)
        elif caminho_arquivo.lower().endswith('.txt'):
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                texto = f.read()
        elif caminho_arquivo.lower().endswith('.docx'):
            import docx
            doc = docx.Document(caminho_arquivo)
            texto = "\n".join([p.text for p in doc.paragraphs])
        else:
            return "❌ Formato de arquivo não suportado."

        entidades = self.detectar_entidades(texto)
        texto_anonimizado = self.anonimizar_texto(texto, entidades)

        # Retorne apenas o texto anonimizado completo, sem resumo
        return texto_anonimizado
    except Exception as e:
        return f"❌ Erro ao processar documento: {str(e)}"
# ...existing code...resultado = gr.Textbox(
    label="",
    lines=25,
    max_lines=50,  # ou remova max_lines para não limitar
    interactive=False,
    show_label=False
# ...existing code...
import gradio as gr
from anonimizador_core import AnonimizadorCore
# ...existing code...# ...existing code in _adicionar_reconhecedores_pt_br...


def anonimizar_documento(arquivo, modelo_llm, chave_api):
    """Função principal para anonimização"""
    try:
        if arquivo is None:
            return "❌ Por favor, selecione um arquivo para anonimizar."
        
        # Inicializar anonimizador com configuração avançada
        anonimizador = AnonimizadorCore()
        
        # Processar documento
        resultado = anonimizador.processar_documento(arquivo.name, modelo_llm, chave_api)
        
        return resultado
        
    except Exception as e:
        return f"❌ Erro durante a anonimização: {str(e)}"

# Configuração da interface
with gr.Blocks(title="AnonimizaJud - Gradio", theme=gr.themes.Soft()) as interface:
    gr.Markdown("# 🚀 AnonimizaJud - Anonimizador de Documentos")
    gr.Markdown("### Versão Gradio - Interface Simplificada com Presidio Avançado")
    gr.Markdown("**🔒 Anonimização automática usando Microsoft Presidio com configuração avançada para português brasileiro**")
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📤 **Upload e Configuração**")
            
            arquivo = gr.File(
                label="📄 Upload do Documento",
                file_types=[".pdf", ".txt", ".docx"],
                height=100
            )
            
            modelo_llm = gr.Dropdown(
                choices=["GPT-4", "Claude", "Gemini", "Groq", "Ollama"],
                value="GPT-4",
                label="🤖 Modelo LLM (opcional para Presidio)"
            )
            
            chave_api = gr.Textbox(
                label="🔑 Chave API (opcional para Presidio)",
                type="password",
                placeholder="Digite sua chave API..."
            )
            
            btn_processar = gr.Button(
                "🚀 Anonimizar Documento",
                variant="primary",
                size="lg"
            )
            
            gr.Markdown("---")
            gr.Markdown("### ℹ️ **Como usar:**")
            gr.Markdown("1. 📤 Faça upload do documento que deseja anonimizar")
            gr.Markdown("2. 🤖 Selecione o modelo LLM (opcional)")
            gr.Markdown("3. 🔑 Digite sua chave API (opcional)")
            gr.Markdown("4. 🚀 Clique em 'Anonimizar Documento'")
            gr.Markdown("5. 🔒 O resultado será exibido ao lado")
        
        with gr.Column(scale=3):
            gr.Markdown("### 📋 **Resultado da Anonimização**")
            
            resultado = gr.Textbox(
                label="",
                lines=25,
                max_lines=30,
                interactive=False,
                show_label=False
            )
            
            gr.Markdown("---")
            gr.Markdown("### 🔍 **Sobre o Microsoft Presidio Avançado:**")
            gr.Markdown("• **Detecção automática** de informações pessoais (PII)")
            gr.Markdown("• **Anonimização inteligente** com marcadores seguros")
            gr.Markdown("• **Suporte completo ao português** brasileiro")
            gr.Markdown("• **Reconhecedores personalizados** para documentos brasileiros")
            gr.Markdown("• **Listas de termos específicos** (estados, cabeçalhos legais, sobrenomes)")
            gr.Markdown("• **Operadores de anonimização** inteligentes")
            gr.Markdown("• **Entidades detectadas:** Nomes, telefones, emails, CPFs, OAB, CNH, SIAPE, etc.")
    
    # Eventos
    btn_processar.click(
        fn=anonimizar_documento,
        inputs=[arquivo, modelo_llm, chave_api],
        outputs=resultado
    )

# Lançar a aplicação
if __name__ == "__main__":
    try:
        # Tentar porta padrão primeiro
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )
    except OSError:
        # Se a porta 7860 estiver ocupada, tentar porta alternativa
        print("⚠️ Porta 7860 ocupada, tentando porta 7861...")
        try:
            interface.launch(
                server_name="0.0.0.0",
                server_port=7861,
                share=False,
                debug=True
            )
        except OSError:
            # Se ambas estiverem ocupadas, usar porta automática
            print("⚠️ Portas 7860 e 7861 ocupadas, usando porta automática...")
            interface.launch(
                server_name="0.0.0.0",
                server_port=0,  # Porta automática
                share=False,
                debug=True
            )