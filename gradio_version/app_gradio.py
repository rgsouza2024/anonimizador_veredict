# app_gradio.py

# -*- coding: utf-8 -*-
import os
import logging
from functools import lru_cache
from collections import Counter
from datetime import datetime
import tempfile
import gradio as gr

from anonimizador_core import AnonimizadorCore

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Core singleton (evita recarga do spaCy/Presidio a cada clique)
# ---------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_core() -> AnonimizadorCore:
    logger.info("Inicializando AnonimizadorCore (singleton)...")
    return AnonimizadorCore()

# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------
def _resolver_caminho_arquivo(arquivo) -> str | None:
    """
    Gradio v4 pode fornecer: str (path), objeto com .name ou dict.
    """
    if arquivo is None:
        return None
    if isinstance(arquivo, str):
        return arquivo
    # objeto com atributo .name
    path = getattr(arquivo, "name", None)
    if path:
        return path
    # dict com chaves 'name'/'path'
    if isinstance(arquivo, dict):
        return arquivo.get("name") or arquivo.get("path")
    return None

def _ler_texto_bruto(core: AnonimizadorCore, caminho: str) -> str:
    """
    Reutiliza os métodos do Core para extrair o texto sem duplicar lógica.
    """
    lower = caminho.lower()
    if lower.endswith(".pdf"):
        return core.extrair_texto_pdf(caminho)
    if lower.endswith(".txt"):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # fallback comum para Windows
            with open(caminho, "r", encoding="latin-1") as f:
                return f.read()
    if lower.endswith(".docx"):
        return core.extrair_texto_docx(caminho)
    return ""

def _criar_arquivo_download(texto_anonimizado: str, arquivo_original: str) -> str | None:
    """
    Gera .txt temporário para download.
    """
    try:
        nome_base = os.path.splitext(os.path.basename(arquivo_original))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{nome_base}_anonimizado_{timestamp}.txt"

        temp_dir = tempfile.gettempdir()
        caminho_completo = os.path.join(temp_dir, nome_arquivo)

        with open(caminho_completo, "w", encoding="utf-8", newline="\n") as f:
            f.write("=" * 60 + "\n")
            f.write("DOCUMENTO ANONIMIZADO - AnonimizaJud\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo original: {os.path.basename(arquivo_original)}\n")
            f.write("=" * 60 + "\n\n")
            f.write(texto_anonimizado)

        logger.info("Arquivo para download criado em %s", caminho_completo)
        return caminho_completo
    except Exception:
        logger.exception("Erro ao criar arquivo para download.")
        return None

def _formatar_estatisticas(entidades) -> str:
    if not entidades:
        return "_Nenhuma entidade sensível detectada._"
    c = Counter([e.entity_type for e in entidades])
    linhas = [f"- **{k}**: {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
    total = sum(c.values())
    return f"**Total de entidades:** {total}\n\n" + "\n".join(linhas)

# ---------------------------------------------------------------------
# Funções da Interface
# ---------------------------------------------------------------------
def anonimizar_documento_interface(arquivo, modelo_llm, chave_api):
    """
    Retorna 4 outputs, alinhados com o .click():
    1) Texto anoninizado (str)
    2) Arquivo para download (path ou None)
    3) Atualização de visibilidade do container de download (gr.update)
    4) Markdown com estatísticas (gr.update(value=...))
    """
    try:
        caminho = _resolver_caminho_arquivo(arquivo)
        if not caminho:
            logger.warning("Tentativa de processar sem arquivo.")
            return ("❌ Por favor, selecione um arquivo para anonimizar.",
                    None,
                    gr.update(visible=False),
                    gr.update(value="_Aguardando processamento._"))

        if not os.path.exists(caminho):
            logger.error("Arquivo não encontrado no sistema: %s", caminho)
            return ("❌ Arquivo não encontrado no sistema.",
                    None,
                    gr.update(visible=False),
                    gr.update(value="_Aguardando processamento._"))

        # Limite opcional de tamanho (10 MB) para proteger a UI
        try:
            if os.path.getsize(caminho) > 10 * 1024 * 1024:
                return ("⚠️ Arquivo muito grande (>10MB). Utilize um documento menor.",
                        None,
                        gr.update(visible=False),
                        gr.update(value="_Aguardando processamento._"))
        except Exception:
            pass

        core = get_core()
        logger.info("Extraindo texto...")
        texto = _ler_texto_bruto(core, caminho).strip()
        if not texto:
            return ("❌ Não foi possível extrair texto do arquivo ou o arquivo está vazio.",
                    None,
                    gr.update(visible=False),
                    gr.update(value="_Aguardando processamento._"))

        logger.info("Detectando entidades...")
        entidades = core.detectar_entidades(texto)
        stats_md = _formatar_estatisticas(entidades)

        if not entidades:
            # Mesmo sem entidades, devolve o texto original (ou uma mensagem)
            logger.info("Nenhuma entidade sensível detectada.")
            resultado_texto = "✅ Documento processado. Nenhuma entidade sensível foi detectada para anonimização.\n\n" + texto
            # Oferece download do texto (útil para auditoria)
            arquivo_dl = _criar_arquivo_download(resultado_texto, caminho)
            return (resultado_texto, arquivo_dl, gr.update(visible=True), gr.update(value=stats_md))

        logger.info("Anonimizando texto...")
        texto_anon = core.anonimizar_texto(texto, entidades_detectadas=entidades)

        arquivo_dl = _criar_arquivo_download(texto_anon, caminho)
        return (texto_anon, arquivo_dl, gr.update(visible=True), gr.update(value=stats_md))

    except Exception as e:
        logger.exception("Erro inesperado durante a anonimização.")
        return (f"❌ Erro crítico durante a anonimização: {str(e)}",
                None,
                gr.update(visible=False),
                gr.update(value="_Falha na execução._"))

def limpar_resultados():
    return ("", None, gr.update(visible=False), gr.update(value="_Processe um documento para ver as estatísticas_"))

# ---------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------
with gr.Blocks(
    title="AnonimizaJud - Gradio",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { font-family: 'Inter', sans-serif; }
    .download-section { background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-top: 10px; }
    """
) as interface:

    gr.Markdown("<h1 style='text-align: center; margin-bottom: 1rem;'>🚀 AnonimizaJud - Anonimizador de Documentos</h1>")

    with gr.Row():
        # --- ESQUERDA ---
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
                btn_processar = gr.Button("🚀 Anonimizar Documento", variant="primary", size="lg")
                btn_limpar = gr.Button("🗑️ Limpar", variant="secondary", size="lg")

            gr.Markdown("---")

            with gr.Column(visible=False, elem_classes=["download-section"]) as download_section:
                gr.Markdown("### 📥 **Download do Resultado**")
                arquivo_download = gr.File(label="Arquivo Anonimizado", interactive=False)

            gr.Markdown("---")
            gr.Markdown("### ℹ️ **Como usar:**")
            gr.Markdown("1. 📤 Faça upload do seu documento (`.pdf`, `.txt` ou `.docx`)")
            gr.Markdown("2. 🚀 Clique em 'Anonimizar Documento'")
            gr.Markdown("3. 📋 Visualize o resultado ao lado")
            gr.Markdown("4. 📥 Baixe o arquivo anonimizado ou copie o texto")

        # --- DIREITA ---
        with gr.Column(scale=2):
            with gr.Row():
                gr.Markdown("### 📋 **Resultado da Anonimização**")
                gr.Button("📋 Copiar").click(
                    None, [], [],
                    js="""
                    () => {
                        const root = document.querySelector('#resultado');
                        const ta = root ? root.querySelector('textarea,input') : null;
                        if (ta && ta.value) {
                            navigator.clipboard.writeText(ta.value);
                            alert('Texto copiado para a área de transferência!');
                        }
                    }
                    """
                )

            resultado_textbox = gr.Textbox(
                label="Texto Anonimizado",
                lines=25,
                max_lines=30,
                interactive=False,
                show_label=False,
                elem_id="resultado"
            )

            with gr.Accordion("📊 Estatísticas da Anonimização", open=False):
                stats_output = gr.Markdown("_Processe um documento para ver as estatísticas_")

    # Ligações
    btn_processar.click(
        fn=anonimizar_documento_interface,
        inputs=[arquivo, modelo_llm, chave_api],
        outputs=[resultado_textbox, arquivo_download, download_section, stats_output],
        show_progress=True
    )

    btn_limpar.click(
        fn=limpar_resultados,
        inputs=[],
        outputs=[resultado_textbox, arquivo_download, download_section, stats_output]
    )

# Fila para melhor responsividade
interface.queue(max_size=8)

if __name__ == "__main__":
    print("Iniciando a interface do AnonimizaJud...")
    interface.launch(server_name="0.0.0.0", server_port=7860, show_error=True)

