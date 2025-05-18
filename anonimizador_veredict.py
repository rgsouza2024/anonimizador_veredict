# Versão final (1.0) do Anonimizador Veredict
# Nome do arquivo: anonimizador_veredict.py
# Versão com sidebar ajustada e integração LLM (Claude 3.5 Haiku).

import streamlit as st
import os
from dotenv import load_dotenv # Importa a função para carregar o .env
load_dotenv()
import spacy
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.pattern import Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import pandas as pd
from st_copy_to_clipboard import st_copy_to_clipboard
import io
import fitz  # PyMuPDF
from docx import Document
import re
import os
import anthropic

# --- Constantes ---
NOME_ARQUIVO_SOBRENOMES = "sobrenomes_comuns.txt"
SYSTEM_PROMPT_CLAUDE = "Atue como um especialista em redação jurídica e experiência no tratamento de documentos anonimizados."
PROMPT_INSTRUCAO_LLM_CLAUDE = """Você receberá um texto que foi previamente anonimizado. As informações removidas foram substituídas por tags como <NOME>, <ENDERECO>, <CPF>, etc.. Sua tarefa é reescrever este texto para que se torne mais fluido, claro e agradável para leitura. Limite-se ao conteúdo do texto recebido. Não invente, não crie e nem altere informações. Seja descritivo e não faça juízo de valor. Ao encontrar uma tag (ex: <NOME>), não tente adivinhar ou recriar a informação original. Em vez disso, reescreva a frase de forma a omitir esse detalhe específico ou indique que a informação foi suprimida por razões de privacidade, mantendo o sentido geral do texto. Evite simplesmente substituir a tag por expressões como '[informação omitida]', buscando uma redação mais natural. Por exemplo, se o texto anonimizado for: "O Sr. <NOME>, CPF <CPF>, contatou a empresa pelo <EMAIL>.", uma reescrita desejada poderia ser: "Um indivíduo contatou a empresa por e-mail. Traga no output apenas o texto reescrito. Nunca apresente frases introdutórias do tipo 'Aqui está a versão reescrita do texto...' ou frases de encerramento do tipo 'A reescrita mantém a estrutura formal do documento...'."
"""

# --- Configuração da Página ---
st.set_page_config(
    page_title="Anonimizador Veredict",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Chaves para os widgets e session state ---
KEY_TEXTO_ORIGINAL_AREA = "texto_original_input_area_v6"
KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE = "texto_anonimizado_output_area_state_v6"
KEY_OUTPUT_PDF_ANONIMIZADO_DISPLAY_STATE = "output_pdf_anonimizado_display_state_v6" 
KEY_PDF_UPLOADER = "pdf_uploader_v6"
KEY_BOTAO_ANONIMIZAR_PDF = "botao_anonimizar_pdf_v6"
KEY_BOTAO_APAGAR_AREA = "botao_apagar_area_v6"
KEY_BOTAO_ANONIMIZAR_AREA = "botao_anonimizar_area_v6"
KEY_COPY_BTN_FILE = "copy_btn_file_v6"
KEY_COPY_BTN_AREA = "copy_btn_area_v6"
KEY_TEXTO_ORIGINAL_PDF_DISPLAY = "texto_original_pdf_exp_v6"
KEY_LLM_REWRITE_BTN_PDF = "llm_rewrite_pdf_v6"
KEY_LLM_REWRITE_BTN_AREA = "llm_rewrite_area_v6"
KEY_LLM_OUTPUT_PDF_STATE = "llm_output_pdf_state_v6"
KEY_LLM_OUTPUT_AREA_STATE = "llm_output_area_state_v6"
KEY_COPY_LLM_PDF = "copy_llm_pdf_v6"
KEY_COPY_LLM_AREA = "copy_llm_area_v6"

# --- Funções de Callback e Utilitárias ---
def callback_apagar_textos_area():
    st.session_state[KEY_TEXTO_ORIGINAL_AREA] = ""
    st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = "O resultado da anonimização aparecerá aqui..."
    if 'resultados_df_area' in st.session_state:
        st.session_state.resultados_df_area = pd.DataFrame()
    if KEY_LLM_OUTPUT_AREA_STATE in st.session_state:
        st.session_state[KEY_LLM_OUTPUT_AREA_STATE] = None
    if 'nome_arquivo_carregado' in st.session_state:
        del st.session_state.nome_arquivo_carregado
    if 'texto_anonimizado_arquivo' in st.session_state: 
        st.session_state.texto_anonimizado_arquivo = None
    if KEY_TEXTO_ORIGINAL_PDF_DISPLAY in st.session_state:
        st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = ""
    if KEY_LLM_OUTPUT_PDF_STATE in st.session_state:
        st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None

def carregar_lista_de_arquivo(nome_arquivo):
    lista_itens = []
    caminho_base = os.path.dirname(__file__)
    caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                item = linha.strip()
                if item:
                    lista_itens.append(item)
        if not lista_itens and os.path.exists(caminho_arquivo):
            st.warning(f"O arquivo de lista '{nome_arquivo}' foi encontrado na pasta do script, mas está vazio ou não contém itens válidos.")
    except FileNotFoundError:
        st.warning(f"Arquivo de lista '{nome_arquivo}' não encontrado. O reconhecedor de sobrenomes não será carregado com esta lista.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo de lista '{nome_arquivo}': {e}")
    return lista_itens

# --- Listas Estáticas (Completas, conforme fornecido pelo usuário) ---
LISTA_ESTADOS_CAPITAIS_BR = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", "DF",
    "Espírito Santo", "Goiás", "GO", "Maranhão", "MA", "Mato Grosso", "Mato Grosso do Sul",
    "Minas Gerais", "MG", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí",
    "Rio de Janeiro", "RJ", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
    "Roraima", "Santa Catarina", "SC", "São Paulo", "SP", "Sergipe", "Tocantins",
    "Rio Branco", "Maceió", "Macapá", "Manaus", "Salvador", "Fortaleza", "Brasília",
    "Vitória", "Goiânia", "São Luís", "Cuiabá", "Campo Grande", "Belo Horizonte",
    "Belém", "João Pessoa", "Curitiba", "Recife", "Teresina",
    "Natal", "Porto Alegre", "Porto Velho", "Boa Vista", "Florianópolis",
    "Aracaju", "Palmas"
]
TERMOS_CABECALHO_LEGAL_NAO_ANONIMIZAR = [
    "EXMO. SR. DR. JUIZ FEDERAL", "EXMO SR DR JUIZ FEDERAL",
    "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL", "JUIZ FEDERAL",
    "EXMO. SR. DR. JUIZ DE DIREITO", "EXMO SR DR JUIZ DE DIREITO",
    "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO", "JUIZ DE DIREITO",
    "JUIZADO ESPECIAL FEDERAL", "VARA DA SEÇÃO JUDICIÁRIA", "SEÇÃO JUDICIÁRIA", "EXMO.",
    "EXMO", "SR.", "DR.", "Dra.", "DRA."
]
LISTA_ESTADO_CIVIL = [
    "casado", "casada", "solteiro", "solteira", "viúvo", "viúva", 
    "divorciado", "divorciada", "separado", "separada", "unido", "unida",
    "companheiro", "companheira"
]
LISTA_ORGANIZACOES_CONHECIDAS = [
    "SIAPE", "FUNASA", "INSS", "IBAMA", "CNPQ", "IBGE", "FIOCRUZ", "SERPRO", "DATAPREV"
]

LISTA_SOBRENOMES_FREQUENTES_BR = carregar_lista_de_arquivo(NOME_ARQUIVO_SOBRENOMES)

# --- Configuração e Inicialização do Presidio ---
@st.cache_resource
def carregar_analyzer_engine(termos_safe_location, termos_legal_header, lista_sobrenomes,
                             termos_estado_civil, termos_organizacoes_conhecidas):
    try:
        try: spacy.load('pt_core_news_lg')
        except OSError:
            st.error("Modelo spaCy 'pt_core_news_lg' não encontrado. Instale com: python -m spacy download pt_core_news_lg")
            return None
        spacy_engine_obj = SpacyNlpEngine(models=[{'lang_code': 'pt', 'model_name': 'pt_core_news_lg'}])
        analyzer = AnalyzerEngine(nlp_engine=spacy_engine_obj, supported_languages=["pt"], default_score_threshold=0.4)
        
        recognizer_safe_location = PatternRecognizer(supported_entity="SAFE_LOCATION", name="SafeLocationRecognizer", deny_list=termos_safe_location, supported_language="pt", deny_list_score=0.99)
        analyzer.registry.add_recognizer(recognizer_safe_location)
        recognizer_legal_header = PatternRecognizer(supported_entity="LEGAL_HEADER", name="LegalHeaderRecognizer", deny_list=termos_legal_header, supported_language="pt", deny_list_score=0.99)
        analyzer.registry.add_recognizer(recognizer_legal_header)
        cpf_pattern = Pattern(name="CpfRegexPattern", regex=r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", score=0.85)
        cpf_recognizer = PatternRecognizer(supported_entity="CPF", name="CustomCpfRecognizer", patterns=[cpf_pattern], supported_language="pt")
        analyzer.registry.add_recognizer(cpf_recognizer)
        oab_pattern = Pattern(name="OabRegexPattern", regex=r"\b(?:OAB\s+)?\d{1,6}(?:\.\d{3})?\s*\/\s*[A-Z]{2}\b", score=0.85)
        oab_recognizer = PatternRecognizer(supported_entity="OAB_NUMBER", name="CustomOabRecognizer", patterns=[oab_pattern], supported_language="pt")
        analyzer.registry.add_recognizer(oab_recognizer)
        cep_pattern = Pattern(name="CepPattern", regex=r"\b(\d{5}-?\d{3}|\d{2}\.\d{3}-?\d{3})\b", score=0.80) 
        cep_recognizer = PatternRecognizer(supported_entity="CEP_NUMBER", name="CustomCepRecognizer", patterns=[cep_pattern], supported_language="pt")
        analyzer.registry.add_recognizer(cep_recognizer)

        if termos_estado_civil:
            estado_civil_patterns = [Pattern(name=f"estado_civil_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in termos_estado_civil]
            ec_recognizer = PatternRecognizer(supported_entity="ESTADO_CIVIL", name="EstadoCivilRecognizer", patterns=estado_civil_patterns, supported_language="pt")
            analyzer.registry.add_recognizer(ec_recognizer)
        if termos_organizacoes_conhecidas:
            org_patterns = [Pattern(name=f"org_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in termos_organizacoes_conhecidas]
            org_recognizer = PatternRecognizer(supported_entity="ORGANIZACAO_CONHECIDA", name="OrganizacaoConhecidaRecognizer", patterns=org_patterns, supported_language="pt")
            analyzer.registry.add_recognizer(org_recognizer)
        if lista_sobrenomes:
            surnames_patterns = [Pattern(name=f"surname_{s.lower().replace(' ', '_')}", regex=rf"(?i)\b{re.escape(s)}\b", score=0.95) for s in lista_sobrenomes]
            surnames_recognizer = PatternRecognizer(supported_entity="PERSON", name="BrazilianCommonSurnamesRecognizer", patterns=surnames_patterns, supported_language="pt")
            analyzer.registry.add_recognizer(surnames_recognizer)
        
        return analyzer
    except Exception as e:
        st.error(f"Erro crítico ao carregar o AnalyzerEngine: {e}.")
        return None

@st.cache_resource
def carregar_anonymizer_engine():
    try:
        engine = AnonymizerEngine()
        return engine
    except Exception as e:
        st.error(f"Erro crítico ao carregar o AnonymizerEngine: {e}.")
        return None

def obter_operadores_anonimizacao():
    return {
        "DEFAULT": OperatorConfig("keep"),
        "PERSON": OperatorConfig("replace", {"new_value": "<NOME>"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "<ENDERECO>"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
        "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),
        "CPF": OperatorConfig("replace", {"new_value": "<CPF>"}),
        "DATE_TIME": OperatorConfig("replace", {"new_value": "<DATA>"}),
        "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
        "CEP_NUMBER": OperatorConfig("replace", {"new_value": "<CEP>"}),
        "ESTADO_CIVIL": OperatorConfig("keep"),
        "ORGANIZACAO_CONHECIDA": OperatorConfig("keep")
    }

analyzer_engine = carregar_analyzer_engine(
    LISTA_ESTADOS_CAPITAIS_BR,
    TERMOS_CABECALHO_LEGAL_NAO_ANONIMIZAR,
    LISTA_SOBRENOMES_FREQUENTES_BR,
    LISTA_ESTADO_CIVIL,
    LISTA_ORGANIZACOES_CONHECIDAS
)
anonymizer_engine = carregar_anonymizer_engine()
operadores = obter_operadores_anonimizacao()

def extrair_texto_de_pdf(arquivo_pdf_bytes):
    texto_completo = ""
    try:
        documento_pdf = fitz.open(stream=arquivo_pdf_bytes, filetype="pdf")
        for pagina in documento_pdf: texto_completo += pagina.get_text()
        documento_pdf.close()
    except Exception as e: st.error(f"Erro ao extrair texto do PDF: {e}"); return None
    return texto_completo

def criar_docx_bytes(texto_anonimizado):
    documento = Document(); documento.add_paragraph(texto_anonimizado)
    bio = io.BytesIO(); documento.save(bio); bio.seek(0)
    return bio.getvalue()

def carregar_chave_anthropic():
    api_key = os.getenv("ANTHROPIC_API_KEY") 
    if not api_key: 
        try:
            if hasattr(st, 'secrets') and st.secrets.get("ANTHROPIC_API_KEY"):
                api_key = st.secrets["ANTHROPIC_API_KEY"]
        except FileNotFoundError: pass 
        except Exception as e: st.warning(f"Problema ao acessar st.secrets para Anthropic: {e}")
    if not api_key:
        st.error("Chave API da Anthropic não configurada. Defina ANTHROPIC_API_KEY.")
        return None
    return api_key

def reescrever_texto_com_claude(texto_anonimizado: str, prompt_instrucao_usuario: str, system_prompt: str, api_key: str) -> str | None:
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning("Não há texto anonimizado para reescrever.")
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=len(texto_anonimizado.split()) + 8000, 
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": f"{prompt_instrucao_usuario}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"}]
        )
        if response.content and isinstance(response.content, list) and len(response.content) > 0:
            texto_reescrito_partes = [block.text for block in response.content if block.type == 'text']
            return "".join(texto_reescrito_partes).strip() if texto_reescrito_partes else None
        st.error("A LLM não retornou uma resposta de texto válida.")
        return None
    except anthropic.APIConnectionError as e: st.error(f"Erro de conexão com a API da Anthropic: {e}")
    except anthropic.RateLimitError as e: st.error(f"Limite de requisições da API da Anthropic atingido: {e}")
    except anthropic.AuthenticationError: st.error("Erro de autenticação com a API da Anthropic. Verifique sua chave API.")
    except anthropic.APIError as e: st.error(f"Erro na API da Anthropic: {e}")
    except Exception as e: st.error(f"Ocorreu um erro inesperado ao processar com a LLM: {e}")
    return None

# --- Interface Streamlit Principal ---
path_da_logo = "logo_veredict.png"
try: st.image(path_da_logo, width=420)
except: st.warning("Logo não pôde ser carregada.")
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>Anonimizador Veredict</h1>", unsafe_allow_html=True)

tab_pdf, tab_texto = st.tabs(["🗂️ Anonimizar Arquivo PDF", "⌨️ Anonimizar Texto Colado"])

st.session_state.setdefault(KEY_LLM_OUTPUT_PDF_STATE, None)
st.session_state.setdefault(KEY_LLM_OUTPUT_AREA_STATE, None)
st.session_state.setdefault('texto_anonimizado_arquivo', None)
st.session_state.setdefault(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE, "O resultado da área de texto aparecerá aqui...")
st.session_state.setdefault(KEY_TEXTO_ORIGINAL_PDF_DISPLAY, "")
st.session_state.setdefault('nome_arquivo_carregado', None)
st.session_state.setdefault('resultados_df_area', pd.DataFrame())
st.session_state.setdefault(KEY_TEXTO_ORIGINAL_AREA, ("EXMO. SR. DR. JUIZ FEDERAL DA ____ª VARA DA SEÇÃO JUDICIÁRIA DE SÃO LUÍS – MA – JUIZADO ESPECIAL FEDERAL.\n"
                                                     "João Silva, casado, RG 123456 SSP/MA, CPF 123.456.789-00, SIAPE 12345, FUNASA.\n" # Ajustado o nome para o exemplo
                                                     "Com CEP residencial é 70423-673 e o comercial é 70423673. Outro CEP: 70.423673.\n"
                                                     "Contato por email joao.silva@emailficticio.com e meu telefone é (21) 98765-4321."))

with tab_pdf:
    st.header("Processar Arquivo PDF")
    arquivo_pdf_carregado = st.file_uploader("Escolha um arquivo PDF:", type=["pdf"], key=KEY_PDF_UPLOADER, help="Faça o upload de um arquivo PDF para extrair o texto e anonimizá-lo.")

    if arquivo_pdf_carregado is not None:
        if st.session_state.nome_arquivo_carregado != arquivo_pdf_carregado.name:
            st.session_state.nome_arquivo_carregado = arquivo_pdf_carregado.name
            st.session_state.texto_anonimizado_arquivo = None 
            st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = "" 
            st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None

        if st.button("🔍 Anonimizar PDF Carregado", key=KEY_BOTAO_ANONIMIZAR_PDF, type="primary", disabled=(not analyzer_engine or not anonymizer_engine)):
            if analyzer_engine and anonymizer_engine:
                with st.spinner(f"Processando '{arquivo_pdf_carregado.name}'..."):
                    bytes_pdf = arquivo_pdf_carregado.getvalue()
                    texto_extraido = extrair_texto_de_pdf(bytes_pdf)
                    st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = texto_extraido if texto_extraido else ""
                    st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None
                    if texto_extraido and texto_extraido.strip():
                        entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA"]
                        entidades_para_analise = list(set(entidades_para_analise)); 
                        if "DEFAULT" in entidades_para_analise: entidades_para_analise.remove("DEFAULT")
                        resultados_analise_pdf = analyzer_engine.analyze(text=texto_extraido, language='pt', entities=entidades_para_analise, return_decision_process=False)
                        resultado_anonimizado_pdf_obj = anonymizer_engine.anonymize(text=texto_extraido, analyzer_results=resultados_analise_pdf, operators=operadores)
                        st.session_state.texto_anonimizado_arquivo = resultado_anonimizado_pdf_obj.text
                        st.success(f"Arquivo '{arquivo_pdf_carregado.name}' anonimizado com sucesso!")
                    elif texto_extraido is not None: st.warning("O PDF carregado parece não conter texto útil.")
                    else: st.session_state.texto_anonimizado_arquivo = None 
            else: st.error("Motores de anonimização não estão prontos.")
        
        if st.session_state.get(KEY_TEXTO_ORIGINAL_PDF_DISPLAY, "").strip():
            with st.expander("📄 Ver Texto Extraído do PDF (Original)", expanded=False):
                st.text_area("Texto Original:", value=st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY], height=200, disabled=True)

    texto_anonimizado_pdf_atual = st.session_state.get('texto_anonimizado_arquivo')
    if texto_anonimizado_pdf_atual:
        st.subheader("Texto Anonimizado do Arquivo PDF")
        st.text_area("Resultado do arquivo:", value=texto_anonimizado_pdf_atual, height=300, disabled=True)
        col_dl_docx, col_copy_text_file = st.columns(2) 
        with col_dl_docx:
            try:
                docx_bytes = criar_docx_bytes(texto_anonimizado_pdf_atual)
                st.download_button(label="📥 Baixar como .docx", data=docx_bytes, file_name=f"anonimizado_{st.session_state.get('nome_arquivo_carregado', 'arquivo')}.docx", 
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="secondary")
            except Exception as e: st.error(f"Erro ao gerar DOCX: {e}")
        with col_copy_text_file:
            st_copy_to_clipboard(texto_anonimizado_pdf_atual, "📋 Copiar Texto Gerado", key=KEY_COPY_BTN_FILE)

        st.divider()
        st.subheader("Melhorar Fluidez do Texto Anonimizado com Inteligência Artificial")
        if st.button("✨ Gerar Texto Reescrito pela IA", key=KEY_LLM_REWRITE_BTN_PDF, type="primary"):
            anthropic_api_key = carregar_chave_anthropic()
            if anthropic_api_key and texto_anonimizado_pdf_atual:
                with st.spinner("Trabalhando na reescrita... Por favor, aguarde."):
                    texto_reescrito = reescrever_texto_com_claude(texto_anonimizado_pdf_atual, PROMPT_INSTRUCAO_LLM_CLAUDE, SYSTEM_PROMPT_CLAUDE, anthropic_api_key)
                    st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = texto_reescrito
            elif not anthropic_api_key: pass 
            elif not texto_anonimizado_pdf_atual: st.warning("Não há texto anonimizado do PDF para reescrever.")

        texto_llm_pdf_atual = st.session_state.get(KEY_LLM_OUTPUT_PDF_STATE)
        if texto_llm_pdf_atual:
            st.text_area("Texto Reescrito com Inteligência Artificial:", value=texto_llm_pdf_atual, height=300, disabled=True)
            st_copy_to_clipboard(texto_llm_pdf_atual, "📋 Copiar Texto Reescrito", key=KEY_COPY_LLM_PDF)
        elif texto_anonimizado_pdf_atual: 
            st.caption("Clique no botão acima para gerar uma versão reescrita e mais fluida do texto anonimizado do PDF.")

with tab_texto:
    st.header("Analisar Texto Colado")
    
    col_original, col_anonimizado = st.columns(2)
    with col_original:
        st.subheader("Texto Original")
        # Removido o 'value=' explícito, pois a 'key' e setdefault cuidam disso.
        st.text_area("Cole ou digite o texto para anonimizar:", height=300, key=KEY_TEXTO_ORIGINAL_AREA, 
                     help="Insira o texto que você deseja analisar e anonimizar.")
        st.button("🗑️ Limpar Área de Texto", key=KEY_BOTAO_APAGAR_AREA, on_click=callback_apagar_textos_area, help="Apaga o texto original, o resultado anonimizado e as entidades detectadas.")
    with col_anonimizado:
        st.subheader("Texto Anonimizado")
        st.text_area("Resultado da anonimização:", value=st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE, "O resultado da área de texto aparecerá aqui..."), 
                     height=300, disabled=True) # KEY REMOVIDA
        if st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE) and \
           st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE) not in ["O resultado da área de texto aparecerá aqui...", "Erro ao processar o texto da área."]:
            st_copy_to_clipboard(st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE], "📋 Copiar Texto Anonimizado", key=KEY_COPY_BTN_AREA)
        else: st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
    
    st.divider()

    if st.button("✨ Anonimizar Texto da Área", type="primary", key=KEY_BOTAO_ANONIMIZAR_AREA,
                  disabled=(not analyzer_engine or not anonymizer_engine)):
        texto_para_processar = st.session_state[KEY_TEXTO_ORIGINAL_AREA]
        st.session_state[KEY_LLM_OUTPUT_AREA_STATE] = None
        if not texto_para_processar.strip():
            st.warning("Por favor, insira um texto na área para anonimizar.")
        elif analyzer_engine and anonymizer_engine:
            try:
                with st.spinner("Analisando e anonimizando o texto da área..."):
                    entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA"]
                    entidades_para_analise = list(set(entidades_para_analise))
                    if "DEFAULT" in entidades_para_analise: entidades_para_analise.remove("DEFAULT")
                    resultados_analise = analyzer_engine.analyze(text=texto_para_processar, language='pt', entities=entidades_para_analise, return_decision_process=False)
                    resultado_anonimizado_obj = anonymizer_engine.anonymize(text=texto_para_processar, analyzer_results=resultados_analise, operators=operadores)
                st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = resultado_anonimizado_obj.text
                dados_resultados = []
                if resultados_analise:
                    for res in sorted(resultados_analise, key=lambda x: x.start):
                        dados_resultados.append({"Entidade": res.entity_type, "Texto Detectado": texto_para_processar[res.start:res.end], 
                                                 "Início": res.start, "Fim": res.end, "Score": f"{res.score:.2f}"})
                st.session_state.resultados_df_area = pd.DataFrame(dados_resultados)
                if dados_resultados: st.success("Texto da área anonimizado e entidades detectadas!")
                else: st.info("Nenhuma PII detectada no texto da área.")
            except Exception as e:
                st.error(f"Ocorreu um erro durante a anonimização da área de texto: {e}")
                st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = "Erro ao processar o texto da área."
                st.session_state.resultados_df_area = pd.DataFrame()
        else: st.error("Motores de anonimização não estão prontos.")

    if not st.session_state.get('resultados_df_area', pd.DataFrame()).empty:
        with st.expander("📊 Ver Entidades Detectadas (da Área de Texto)", expanded=False):
            st.markdown("As seguintes entidades foram detectadas no texto original da área:")
            st.dataframe(st.session_state.resultados_df_area, use_container_width=True) 

    texto_anonimizado_area_atual = st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE)
    if texto_anonimizado_area_atual and texto_anonimizado_area_atual not in ["O resultado da área de texto aparecerá aqui...", "Erro ao processar o texto da área."]:
        st.divider()
        st.subheader("Melhorar Fluidez do Texto Anonimizado com Inteligência Artificial")
        if st.button("✨ Gerar Texto Reescrito pela IA", key=KEY_LLM_REWRITE_BTN_AREA, type="primary"):
            anthropic_api_key = carregar_chave_anthropic()
            if anthropic_api_key and texto_anonimizado_area_atual:
                with st.spinner("Trabalhando na reescrita... Por favor, aguarde."):
                    texto_reescrito = reescrever_texto_com_claude(texto_anonimizado_area_atual, PROMPT_INSTRUCAO_LLM_CLAUDE, SYSTEM_PROMPT_CLAUDE, anthropic_api_key)
                    st.session_state[KEY_LLM_OUTPUT_AREA_STATE] = texto_reescrito
            elif not anthropic_api_key: pass
        
        texto_llm_area_atual = st.session_state.get(KEY_LLM_OUTPUT_AREA_STATE)
        if texto_llm_area_atual:
            st.text_area("Texto Reescrito pela Inteligência Artificial:", value=texto_llm_area_atual, height=300, disabled=True) # KEY REMOVIDA
            st_copy_to_clipboard(texto_llm_area_atual, "📋 Copiar Texto Reescrito", key=KEY_COPY_LLM_AREA)
        elif texto_anonimizado_area_atual and texto_anonimizado_area_atual not in ["O resultado da área de texto aparecerá aqui...", "Erro ao processar o texto da área."]:
            st.caption("Clique no botão acima para gerar uma versão reescrita e mais fluida do texto anonimizado da área.")

# --- Informações na Sidebar ---
st.sidebar.header("Sobre")
sidebar_text_sobre = """
**Anonimizador Veredict**

Versão 1.0 (Beta) 

Desenvolvido por:

Juiz Federal Rodrigo Gonçalves de Souza
"""
st.sidebar.markdown(sidebar_text_sobre) # Nome da variável corrigido para evitar conflito com o nome do módulo 'sidebar_text' se existisse

st.sidebar.divider()
st.sidebar.markdown(
    "**Como usar:**\n\n"
    "1. **Anonimize seu texto** (via PDF ou colando na área de texto apropriada).\n"
    "   - Na aba '🗂️ Anonimizar Arquivo PDF', carregue um PDF e clique em 'Anonimizar PDF Carregado'.\n"
    "   - Na aba '⌨️ Anonimizar Texto Colado', insira o texto e clique em 'Anonimizar Texto da Área'.\n\n"
    "2. **Melhore a Fluidez com IA (Opcional):**\n"
    "   - Após a anonimização, se desejar uma versão do texto mais fluida (sem as tags de anonimização explícitas),"
    " clique no botão '✨ Gerar Texto Reescrito pela IA'.\n\n"
    "**Importante:**\n"
    "- Trata-se de ferramenta em desenvolvimento.\n"
    "- Sempre confira o resultado gerado (a IA pode cometer erros)."
)