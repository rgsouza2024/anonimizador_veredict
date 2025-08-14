# Nome do arquivo: anonimizador.py
# Versão 0.91 (Beta)

import streamlit as st
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
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import openai
import anthropic
import requests 
import json # Embora não usado diretamente no exemplo Ollama, pode ser útil para JSON payloads
import tiktoken 
import httpx

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Constantes ---
NOME_ARQUIVO_SOBRENOMES = "sobrenomes_comuns.txt"
NOME_ARQUIVO_TERMOS_COMUNS = "termos_comuns.txt"
NOME_ARQUIVO_PROMPT_INSTRUCAO = "prompt_instrucao_llm_base.txt" 
PATH_DA_LOGO = "Logo - AnonimizaJud.png" 
SYSTEM_PROMPT_BASE = "Atue como um assessor jurídico brasileiro especialista em redação jurídica e experiência no tratamento de documentos anonimizados. Seja descritivo e não faça juízo de valor. Responda DIRETAMENTE com a informação solicitada, sem justificativas. Limite-se ao conteúdo do texto fornecido pelo usuário. Não invente, não crie e nem altere informações. Substitua as informações das tags (ex: <NOME> e <ENDERECO>) por textos fluidos e expressões genéricas, sem utilização da tags ou de markdown. Retire do texto original qualquer dado que possa identificar as partes do processo (ex: matrícula SIAPE). /no_think "

# Modelos LLM IDs
MODELO_GEMINI = "gemini-2.5-flash-lite-preview-06-17"  # Atualizado para Gemini 2.5 Flash Lite Preview
MODELO_OPENAI = "gpt-4o-mini"
MODELO_CLAUDE = "claude-3-5-haiku-latest"
MODELO_GROQ_LLAMA3_70B = "llama-3.3-70b-versatile"
MODELO_OLLAMA_NEMOTRON = "nemotron-mini"
OLLAMA_BASE_URL = "http://localhost:11434"

# --- Configuração da Página ---
st.set_page_config(
    page_title="Anonimizador",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Chaves para os widgets e session state ---
VERSION_SUFFIX = "_multillm_v1_1" 
KEY_TEXTO_ORIGINAL_AREA = f"texto_original_input_area{VERSION_SUFFIX}"
KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE = f"texto_anonimizado_output_area_state{VERSION_SUFFIX}"
KEY_PDF_UPLOADER = f"pdf_uploader{VERSION_SUFFIX}"
KEY_BOTAO_ANONIMIZAR_PDF = f"botao_anonimizar_pdf{VERSION_SUFFIX}"
KEY_BOTAO_APAGAR_AREA = f"botao_apagar_area{VERSION_SUFFIX}"
KEY_BOTAO_ANONIMIZAR_AREA = f"botao_anonimizar_area{VERSION_SUFFIX}"
KEY_COPY_BTN_FILE_ANON = f"copy_btn_file_anon{VERSION_SUFFIX}" # Renomeado para clareza
KEY_COPY_BTN_AREA_ANON = f"copy_btn_area_anon{VERSION_SUFFIX}" # Renomeado para clareza
KEY_TEXTO_ORIGINAL_PDF_DISPLAY = f"texto_original_pdf_exp{VERSION_SUFFIX}"
KEY_LLM_CHOICE_PDF = f"llm_choice_pdf{VERSION_SUFFIX}"
KEY_LLM_CHOICE_AREA = f"llm_choice_area{VERSION_SUFFIX}"
KEY_LLM_REWRITE_BTN_PDF = f"llm_rewrite_pdf{VERSION_SUFFIX}"
KEY_LLM_REWRITE_BTN_AREA = f"llm_rewrite_area{VERSION_SUFFIX}"
KEY_LLM_OUTPUT_PDF_STATE = f"llm_output_pdf_state{VERSION_SUFFIX}"
KEY_LLM_OUTPUT_AREA_STATE = f"llm_output_area_state{VERSION_SUFFIX}"
KEY_COPY_LLM_PDF = f"copy_llm_pdf{VERSION_SUFFIX}"
KEY_COPY_LLM_AREA = f"copy_llm_area{VERSION_SUFFIX}"
KEY_CUSTOM_USER_PROMPT_LLM_INPUT = f"custom_user_prompt_llm_input{VERSION_SUFFIX}" # NOVA CHAVE
KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM = f"texto_extraido_pdf_contagem{VERSION_SUFFIX}"
KEY_NUM_TOKENS_PDF_EXTRAIDO = f"num_tokens_pdf_extraido{VERSION_SUFFIX}"

# --- Funções de Callback e Utilitárias ---
def callback_apagar_textos_area():
    # Apaga o conteúdo da área de texto original
    st.session_state[KEY_TEXTO_ORIGINAL_AREA] = ""
    # Reseta o placeholder da área de texto anonimizado
    st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = "O resultado da anonimização aparecerá aqui..."
    # Limpa o dataframe de resultados
    if 'resultados_df_area' in st.session_state: # Usando chave sem sufixo como no seu último código
        st.session_state.resultados_df_area = pd.DataFrame()
    
    # Limpa o output da LLM para a área de texto
    if KEY_LLM_OUTPUT_AREA_STATE in st.session_state:
        st.session_state[KEY_LLM_OUTPUT_AREA_STATE] = None
    
    # Reseta o prompt customizado da aba de texto para o padrão global
    custom_prompt_key_para_aba_area = f"{KEY_CUSTOM_USER_PROMPT_LLM_INPUT}_area"
    if custom_prompt_key_para_aba_area in st.session_state:
        st.session_state[custom_prompt_key_para_aba_area] = PROMPT_INSTRUCAO_LLM_BASE
        
    # Limpeza de estados relacionados ao PDF, caso o botão seja considerado "Limpar Tudo"
    # Se for só para a aba de texto, remova estas linhas.
    if 'nome_arquivo_carregado' in st.session_state:
        st.session_state.nome_arquivo_carregado = None
    if 'texto_anonimizado_arquivo' in st.session_state:
        st.session_state.texto_anonimizado_arquivo = None
    if KEY_TEXTO_ORIGINAL_PDF_DISPLAY in st.session_state:
        st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = ""
    if KEY_LLM_OUTPUT_PDF_STATE in st.session_state:
        st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None
    if KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM in st.session_state:
        st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM] = ""
    if KEY_NUM_TOKENS_PDF_EXTRAIDO in st.session_state:
        st.session_state[KEY_NUM_TOKENS_PDF_EXTRAIDO] = 0
   

def carregar_lista_de_arquivo(nome_arquivo):
    lista_itens = []
    caminho_base = os.path.dirname(__file__)
    caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                item = linha.strip()
                if item: lista_itens.append(item)
        if not lista_itens and os.path.exists(caminho_arquivo):
            st.warning(f"O arquivo de lista '{nome_arquivo}' foi encontrado, mas está vazio.")
    except FileNotFoundError: st.warning(f"Arquivo de lista '{nome_arquivo}' não encontrado.")
    except Exception as e: st.error(f"Erro ao ler o arquivo '{nome_arquivo}': {e}")
    return lista_itens

def carregar_texto_de_arquivo(nome_arquivo: str) -> str | None:
    """
    Lê todo o conteúdo de um arquivo de texto e o retorna como uma única string.
    Retorna None se o arquivo não for encontrado ou ocorrer um erro.
    """
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read().strip() 
        if not conteudo:
            st.warning(f"O arquivo de prompt '{nome_arquivo}' foi encontrado em '{caminho_arquivo}', mas está vazio.")
            return None 
        return conteudo
    except FileNotFoundError:
        st.error(f"Arquivo de prompt '{nome_arquivo}' NÃO encontrado em '{caminho_arquivo}'. "
                 f"Verifique se o arquivo existe na mesma pasta do script Python.")
        return None 
    except Exception as e:
        st.error(f"Erro ao ler o arquivo de prompt '{nome_arquivo}': {e}")
        return None

def render_header():
    """Renderiza o header compacto e profissional da aplicação"""
    # Primeiro, tenta carregar e codificar a imagem em base64
    import base64
    logo_base64 = ""
    try:
        with open(PATH_DA_LOGO, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except:
        pass  # Se não conseguir carregar a logo, continua sem ela
    
    # HTML do header
    header_html = f"""
    <div style="display: flex; align-items: center; padding: 1rem 0; border-bottom: 2px solid #e0e0e0; margin-bottom: 2rem;">
        {f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-right: 20px;">' if logo_base64 else ''}
        <div>
            <h1 style="margin: 0; color: #003366; font-size: 2.5rem; font-weight: 700;">Anonimizador</h1>
            <p style="margin: 0; color: #666; font-size: 1rem;">
                Proteja informações sensíveis em seus documentos com tecnologia avançada de IA
            </p>
        </div>
        <div style="margin-left: auto; text-align: right; padding-right: 1rem;">
            <span style="background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                Versão 0.91 Beta
            </span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def show_loading_message(message="Processando..."):
    """Mostra indicador de loading inline"""
    return st.markdown(f'<div style="display: flex; align-items: center; margin: 1rem 0;"><div class="loading-spinner"></div><span style="color: #007bff; font-weight: 500;">{message}</span></div>', unsafe_allow_html=True)

def show_success_animation(container):
    """Aplica animação de sucesso ao container"""
    with container:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

def close_success_animation():
    """Fecha a div de animação"""
    st.markdown('</div>', unsafe_allow_html=True)

def create_card(title="", icon="", help_text=""):
    """Cria um card visual para melhor organização do conteúdo"""
    card_html = f"""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;
                border: 1px solid #e0e0e0;">
        {f'<h3 style="color: #003366; margin-bottom: 1rem; display: flex; align-items: center;"><span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>{title}</h3>' if title else ''}
        {f'<p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">{help_text}</p>' if help_text else ''}
    </div>
    """
    return card_html

# Carregando o PROMPT_INSTRUCAO_LLM_BASE do arquivo .txt
PROMPT_INSTRUCAO_LLM_BASE = carregar_texto_de_arquivo(NOME_ARQUIVO_PROMPT_INSTRUCAO)

# Verificação e fallback (opcional, mas recomendado, para o caso do arquivo não ser encontrado ou estar vazio)
if PROMPT_INSTRUCAO_LLM_BASE is None or not PROMPT_INSTRUCAO_LLM_BASE.strip():
    st.error(f"ATENÇÃO: Não foi possível carregar o prompt de instrução do arquivo '{NOME_ARQUIVO_PROMPT_INSTRUCAO}'. "
             "Verifique se o arquivo existe na mesma pasta do script e não está vazio. "
             "Usando um prompt de instrução padrão genérico.")
    PROMPT_INSTRUCAO_LLM_BASE = """Instrução padrão de fallback: Faça um resumo detalhado do texto fornecido, omitindo informações pessoais ou sensíveis, e substituindo tags por expressões genéricas. /setnothink /no_think """

# --- Listas Estáticas (Completas) ---
LISTA_ESTADOS_CAPITAIS_BR = [
    "Acre", "AC",
    "Alagoas", "AL",
    "Amapá", "AP",
    "Amazonas", "AM",
    "Bahia", "BA",
    "Ceará", "CE",
    "Distrito Federal", "DF",
    "Espírito Santo", "ES",
    "Goiás", "GO",
    "Maranhão", "MA",
    "Mato Grosso", "MT",
    "Mato Grosso do Sul", "MS",
    "Minas Gerais", "MG",
    "Pará", "PA",
    "Paraíba", "PB",
    "Paraná", "PR",
    "Pernambuco", "PE",
    "Piauí", "PI",
    "Rio de Janeiro", "RJ",
    "Rio Grande do Norte", "RN",
    "Rio Grande do Sul", "RS",
    "Rondônia", "RO",
    "Roraima", "RR",
    "Santa Catarina", "SC",
    "São Paulo", "SP",
    "Sergipe", "SE",
    "Tocantins", "TO",
    "Aracaju",        # Sergipe
    "Belém",          # Pará
    "Belo Horizonte", # Minas Gerais
    "Boa Vista",      # Roraima
    "Brasília",       # Distrito Federal
    "Campo Grande",   # Mato Grosso do Sul
    "Cuiabá",         # Mato Grosso
    "Curitiba",       # Paraná
    "Florianópolis",  # Santa Catarina
    "Fortaleza",      # Ceará
    "Goiânia",        # Goiás
    "João Pessoa",    # Paraíba
    "Macapá",         # Amapá
    "Maceió",         # Alagoas
    "Manaus",         # Amazonas
    "Natal",          # Rio Grande do Norte
    "Palmas",         # Tocantins
    "Porto Alegre",   # Rio Grande do Sul
    "Porto Velho",    # Rondônia
    "Recife",         # Pernambuco
    "Rio Branco",     # Acre
    "Salvador",       # Bahia
    "São Luís",       # Maranhão
    "São Paulo",      # (cidade) - mesma situação do Rio de Janeiro.
    "Teresina",       # Piauí
    "Vitória"         # Espírito Santo
]
TERMOS_CABECALHO_LEGAL_NAO_ANONIMIZAR = [
    "EXMO. SR. DR. JUIZ FEDERAL", "EXMO SR DR JUIZ FEDERAL",
    "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL", "JUIZ FEDERAL",
    "EXMO. SR. DR. JUIZ DE DIREITO", "EXMO SR DR JUIZ DE DIREITO",
    "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO", "JUIZ DE DIREITO",
    "JUIZADO ESPECIAL FEDERAL", "VARA DA SEÇÃO JUDICIÁRIA", "SEÇÃO JUDICIÁRIA", "EXMO.",
    "EXMO", "SR.", "DR.", "Dra.", "DRA.", "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) FEDERAL",
    "EXCELENTÍSSIMO", "Senhor", "Doutor", "Senhora", "Doutora", "EXCELENTÍSSIMA", "EXCELENTÍSSIMO(A)",
    "Senhor(a)", "Doutor(a)", "Juiz", "Juíza", "Juiz(a)", "Juiz(íza)", "Assunto", "Assuntos"
]
LISTA_ESTADO_CIVIL = [
    "casado", "casada", "solteiro", "solteira", "viúvo", "viúva", 
    "divorciado", "divorciada", "separado", "separada", "unido", "unida",
    "companheiro", "companheira", "amasiado", "amasiada", "união estável",
    "em união estável"
]
LISTA_ORGANIZACOES_CONHECIDAS = [
    "SIAPE", "FUNASA", "INSS", "IBAMA", "CNPQ", "IBGE", "FIOCRUZ",
    "SERPRO", "DATAPREV", "VALOR", "Justiça", "Justica", "Segredo", "PJe"
    "Assunto", "Tribunal Regional Federal", "Assuntos", "Vara Federal",
    "Vara", "Justiça Federal", "Federal", "Juizado", "Especial", "Federal",
    "Vara Federal de Juizado Especial Cível", "Turma", "Turma Recursal", "PJE"
    "SJGO", "SJDF", "SJMA", "SJAC", "SJAL", "SJAP", "SJAM", "SJBA", "SJCE", 
    "SJDF", "SJES", "SJGO", "SJMA", "SJMG", "SJMS", "SJMT", "SJPA", "SJPB", 
    "SJPE", "SJPI", "SJPR", "SJPE", "SJRN", "SJRO", "SJRR", "SJRS", "SJSC",
    "SJSE", "SJSP", "SJTO", "Justiça Federal da 1ª Região", "PJe - Processo Judicial Eletrônico" 
]
LISTA_SOBRENOMES_FREQUENTES_BR = carregar_lista_de_arquivo(NOME_ARQUIVO_SOBRENOMES)
LISTA_TERMOS_COMUNS = carregar_lista_de_arquivo(NOME_ARQUIVO_TERMOS_COMUNS)

# --- Configuração e Inicialização do Presidio ---
@st.cache_resource
def carregar_analyzer_engine(termos_safe_location, 
                             termos_legal_header, 
                             lista_sobrenomes,
                             termos_estado_civil, 
                             termos_organizacoes_conhecidas, 
                             termos_comuns_a_manter):
    try:
        try:
            spacy.load('pt_core_news_lg')
        except OSError:
            st.error("Modelo spaCy 'pt_core_news_lg' não encontrado. Instale com: python -m spacy download pt_core_news_lg")
            return None
        
        spacy_engine_obj = SpacyNlpEngine(models=[{'lang_code': 'pt', 'model_name': 'pt_core_news_lg'}])
        analyzer = AnalyzerEngine(nlp_engine=spacy_engine_obj, supported_languages=["pt"], default_score_threshold=0.4)
        
        # Reconhecedor para Locais Seguros (Estados e Capitais)
        if termos_safe_location: # Adicionado check para lista não vazia
            recognizer_safe_location = PatternRecognizer(
                supported_entity="SAFE_LOCATION", 
                name="SafeLocationRecognizer", 
                deny_list=termos_safe_location, 
                supported_language="pt", 
                deny_list_score=0.99
            )
            analyzer.registry.add_recognizer(recognizer_safe_location)
        
        # Reconhecedor para Cabeçalhos Legais
        if termos_legal_header: # Adicionado check para lista não vazia
            recognizer_legal_header = PatternRecognizer(
                supported_entity="LEGAL_HEADER", 
                name="LegalHeaderRecognizer", 
                deny_list=termos_legal_header, 
                supported_language="pt", 
                deny_list_score=0.99
            )
            analyzer.registry.add_recognizer(recognizer_legal_header)
        
        # Reconhecedor para CPF
        cpf_pattern = Pattern(name="CpfRegexPattern", regex=r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", score=0.85)
        cpf_recognizer = PatternRecognizer(
            supported_entity="CPF", 
            name="CustomCpfRecognizer", 
            patterns=[cpf_pattern], 
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(cpf_recognizer)
        
        # Reconhecedor para OAB_NUMBER
        oab_pattern = Pattern(name="OabRegexPattern", regex=r"\b(?:OAB\s+)?\d{1,6}(?:\.\d{3})?\s*\/\s*[A-Z]{2}\b", score=0.85)
        oab_recognizer = PatternRecognizer(
            supported_entity="OAB_NUMBER", 
            name="CustomOabRecognizer", 
            patterns=[oab_pattern], 
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(oab_recognizer)

        # Reconhecedor para CEP_NUMBER
        cep_pattern = Pattern(name="CepPattern", regex=r"\b(\d{5}-?\d{3}|\d{2}\.\d{3}-?\d{3})\b", score=0.80) 
        cep_recognizer = PatternRecognizer(
            supported_entity="CEP_NUMBER", 
            name="CustomCepRecognizer", 
            patterns=[cep_pattern], 
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(cep_recognizer)

        # Reconhecedor para ESTADO_CIVIL
        if termos_estado_civil:
            estado_civil_patterns = [Pattern(name=f"estado_civil_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in termos_estado_civil]
            ec_recognizer = PatternRecognizer(
                supported_entity="ESTADO_CIVIL", 
                name="EstadoCivilRecognizer", 
                patterns=estado_civil_patterns, 
                supported_language="pt"
            )
            analyzer.registry.add_recognizer(ec_recognizer)

        # Reconhecedor para ORGANIZACOES_CONHECIDAS
        if termos_organizacoes_conhecidas:
            org_patterns = [Pattern(name=f"org_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in termos_organizacoes_conhecidas]
            org_recognizer = PatternRecognizer(
                supported_entity="ORGANIZACAO_CONHECIDA", 
                name="OrganizacaoConhecidaRecognizer", 
                patterns=org_patterns, 
                supported_language="pt"
            )
            analyzer.registry.add_recognizer(org_recognizer)
        
        # Reconhecedor para Sobrenomes Frequentes (da lista externa)
        if lista_sobrenomes:
            surnames_patterns = [Pattern(name=f"surname_{s.lower().replace(' ', '_')}", regex=rf"(?i)\b{re.escape(s)}\b", score=0.97) for s in lista_sobrenomes]
            surnames_recognizer = PatternRecognizer(
                supported_entity="PERSON", 
                name="BrazilianCommonSurnamesRecognizer", 
                patterns=surnames_patterns, 
                supported_language="pt"
            )
            analyzer.registry.add_recognizer(surnames_recognizer)
        
        # --- Reconhecedores Específicos para Documentos de Identificação ---
        
        # Reconhecedor para CNH (Carteira Nacional de Habilitação)
        cnh_patterns = [
            # CNH com formatação: CNH 12345678901 ou CNH nº 12345678901
            Pattern(name="cnh_formatado", regex=r"\bCNH\s*(?:nº|n\.)?\s*\d{11}\b", score=0.98),
            # CNH sem formatação: apenas os 11 dígitos (mais específico para evitar falsos positivos)
            Pattern(name="cnh_apenas_numeros", regex=r"\b(?<![\w])\d{11}(?![\w])\b", score=0.85)
        ]
        cnh_recognizer = PatternRecognizer(
            supported_entity="CNH",
            name="CNHRecognizer",
            patterns=cnh_patterns,
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(cnh_recognizer)
        
        # Reconhecedor para SIAPE (Sistema Integrado de Administração de Recursos Humanos)
        siape_patterns = [
            # SIAPE com formatação: SIAPE 1234567 ou SIAPE nº 1234567
            Pattern(name="siape_formatado", regex=r"\bSIAPE\s*(?:nº|n\.)?\s*\d{7}\b", score=0.98),
            # SIAPE sem formatação: apenas os 7 dígitos (mais específico)
            Pattern(name="siape_apenas_numeros", regex=r"\b(?<![\w])\d{7}(?![\w])\b", score=0.85)
        ]
        siape_recognizer = PatternRecognizer(
            supported_entity="SIAPE",
            name="SIAPERecognizer",
            patterns=siape_patterns,
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(siape_recognizer)
        
        # Reconhecedor para CI (Cédula de Identidade)
        ci_patterns = [
            # CI com formatação: CI 12345678-9 ou CI nº 12345678-9
            Pattern(name="ci_formatado", regex=r"\bCI\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
            # CI sem formatação: formato padrão brasileiro
            Pattern(name="ci_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90)
        ]
        ci_recognizer = PatternRecognizer(
            supported_entity="CI",
            name="CIRecognizer",
            patterns=ci_patterns,
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(ci_recognizer)
        
        # Reconhecedor para CIN (Cédula de Identidade Nacional)
        cin_patterns = [
            # CIN com formatação: CIN 12345678-9 ou CIN nº 12345678-9
            Pattern(name="cin_formatado", regex=r"\bCIN\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
            # CIN sem formatação: formato padrão brasileiro
            Pattern(name="cin_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90)
        ]
        cin_recognizer = PatternRecognizer(
            supported_entity="CIN",
            name="CINRecognizer",
            patterns=cin_patterns,
            supported_language="pt"
        )
        analyzer.registry.add_recognizer(cin_recognizer)
        
        # --- Reconhecedor para IDs de Documento/Processo/Benefício (REFINADO) ---
        id_documento_patterns = [
            # Para NB XXXXXXXXX-X ou XXX.XXX.XXX-X
            Pattern(name="numero_beneficio_nb_formatado", regex=r"\bNB\s*\d{1,3}(\.?\d{3}){2}-[\dX]\b", score=0.98),
            # Para IDs PJe longos e puramente numéricos (ex: ID do Documento, Número do Documento)
            # Este regex pega sequências de 10 a 25 dígitos. Ajuste os limites se necessário.
            Pattern(name="id_numerico_longo_pje", regex=r"\b\d{10,25}\b", score=0.97), 
            # Para IDs que começam com "ID " seguido de números (como no seu exemplo ID 2028869157 do teste anterior)
            Pattern(name="id_prefixo_numerico", regex=r"\bID\s*\d{8,12}\b", score=0.97),
            # Para RG no formato XXXXXXX-X ou X.XXX.XXX-X, com variações de "ª VIA" e órgão emissor
            Pattern(name="numero_rg_completo", regex=r"\bRG\s*(?:nº|n\.)?\s*[\d.X-]+(?:-\dª\s*VIA)?\s*-\s*[A-Z]{2,3}\/[A-Z]{2}\b", score=0.98),
            Pattern(name="numero_rg_simples", regex=r"\bRG\s*(?:nº|n\.)?\s*[\d.X-]+\b", score=0.97), # RG mais simples sem órgão emissor
            # Número de processo CNJ (manter score alto para proteção)
            Pattern(name="numero_processo_cnj", regex=r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b", score=0.95),
            # Para RNM (Registro Nacional Migratório)
            Pattern(name="numero_rnm", regex=r"\bRNM\s*(?:nº|n\.)?\s*[A-Z0-9]{7,15}\b", score=0.98), # Ex: RNM nº F5725832
            # Para CRM (Conselho Regional de Medicina)
            Pattern(name="numero_crm", regex=r"\bCRM\s*[A-Z]{2}\s*-\s*\d{1,6}\b", score=0.98) # Ex: CRM RR-2498
        ]
        id_documento_recognizer = PatternRecognizer(
            supported_entity="ID_DOCUMENTO", 
            name="IdDocumentoRecognizer",
            patterns=id_documento_patterns,
            supported_language="pt"
            # context = ["NB", "ID", "CRM", "RNM", "RG", "Processo"] # Contexto pode ajudar a aumentar a precisão
        )
        analyzer.registry.add_recognizer(id_documento_recognizer)
        # --- FIM DO NOVO RECONHECEDOR ---
        
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
        "DATE_TIME": OperatorConfig("keep"), 
        "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
        "CEP_NUMBER": OperatorConfig("replace", {"new_value": "<CEP>"}),
        "ESTADO_CIVIL": OperatorConfig("keep"),
        "ORGANIZACAO_CONHECIDA": OperatorConfig("keep"),
        "ID_DOCUMENTO": OperatorConfig("keep"), 
                        "LEGAL_OR_COMMON_TERM": OperatorConfig("keep"),
                # Operadores para documentos - substituindo por "***"
                "CNH": OperatorConfig("replace", {"new_value": "***"}),
                "SIAPE": OperatorConfig("replace", {"new_value": "***"}),
                "CI": OperatorConfig("replace", {"new_value": "***"}),
                "CIN": OperatorConfig("replace", {"new_value": "***"}),
                "RG": OperatorConfig("replace", {"new_value": "***"})
    }

analyzer_engine = carregar_analyzer_engine(
    LISTA_ESTADOS_CAPITAIS_BR,              # para termos_safe_location
    TERMOS_CABECALHO_LEGAL_NAO_ANONIMIZAR,  # para termos_legal_header
    LISTA_SOBRENOMES_FREQUENTES_BR,         # para lista_sobrenomes
    LISTA_ESTADO_CIVIL,                     # para termos_estado_civil (ESTAVA FALTANDO)
    LISTA_ORGANIZACOES_CONHECIDAS,           # para termos_organizacoes_conhecidas (ESTAVA FALTANDO)
    LISTA_TERMOS_COMUNS
)
anonymizer_engine = carregar_anonymizer_engine()
operadores = obter_operadores_anonimizacao()

def extrair_texto_de_pdf(arquivo_pdf_bytes_io):
    texto_completo = ""
    try:
        documento_pdf = fitz.open(stream=arquivo_pdf_bytes_io, filetype="pdf")
        for pagina in documento_pdf: texto_completo += pagina.get_text()
        documento_pdf.close()
    except Exception as e: st.error(f"Erro ao extrair texto do PDF: {e}"); return None
    return texto_completo

def criar_docx_bytes(texto_anonimizado):
    documento = Document(); documento.add_paragraph(texto_anonimizado)
    bio = io.BytesIO(); documento.save(bio); bio.seek(0)
    return bio.getvalue()

def contar_tokens_para_estimativa(texto: str, llm_provider: str = "openai") -> int:
    if not texto: return 0
    try:
        # Para OpenAI, Anthropic (Claude 2 e anteriores), e uma estimativa para Gemini
        if llm_provider in ["openai", "claude", "gemini_estimate"]: 
            encoding = tiktoken.get_encoding("cl100k_base")
        elif llm_provider == "ollama": 
            return len(texto.split()) # Estimativa grosseira para Ollama/Gemma
        else: 
            encoding = tiktoken.encoding_for_model("gpt-4o-mini") 
    except KeyError:
        try: encoding = tiktoken.get_encoding("cl100k_base")
        except: return len(texto.split()) 
    except Exception: return len(texto.split())
    return len(encoding.encode(texto))
# --- Funções de Carregamento de Chave API ---
def carregar_chave_api(env_var_name: str, secrets_key_name: str, servico_nome_exibicao: str) -> str | None:
    """Carrega uma chave API da variável de ambiente ou dos secrets do Streamlit."""
    api_key = os.getenv(env_var_name) 
    if not api_key: 
        try:
            if hasattr(st, 'secrets') and st.secrets.get(secrets_key_name):
                api_key = st.secrets[secrets_key_name]
        except FileNotFoundError: 
            # Isso é esperado se st.secrets for acessado localmente sem um arquivo secrets.toml
            pass 
        except Exception as e: 
            st.warning(f"Problema ao tentar acessar st.secrets para {servico_nome_exibicao}: {e}")
    
    if not api_key:
        st.error(f"Chave API para {servico_nome_exibicao} não configurada. "
                 f"Defina a variável de ambiente {env_var_name} no seu arquivo .env (localmente) "
                 f"ou configure {secrets_key_name} em 'Secrets' (para deploy no Streamlit Cloud).")
        return None
    return api_key

# --- Funções de Chamada das LLMs ---

def reescrever_texto_com_openai(texto_anonimizado: str, system_prompt: str, user_prompt_instruction: str, api_key: str) -> str | None:
    """Chama a API da OpenAI para reescrever/resumir o texto."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning("OpenAI: Não há texto anonimizado para reescrever.")
        return None
    try:
        meu_http_client = httpx.Client() # Para evitar problemas com proxies
        client = openai.OpenAI(api_key=api_key, http_client=meu_http_client)
        
        response = client.chat.completions.create(
            model=MODELO_OPENAI, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt_instruction}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"}
            ],
            temperature=0.3, 
            max_tokens=16384 
        )
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            st.error("A LLM (OpenAI) não retornou uma resposta de conteúdo válida.")
            return None
    except openai.AuthenticationError: st.error("Erro de autenticação com a API da OpenAI. Verifique sua chave API.")
    except openai.RateLimitError as e: st.error(f"Limite de requisições da API da OpenAI atingido: {e}")
    except openai.APIConnectionError as e: st.error(f"Erro de conexão com a API da OpenAI: {e}")
    except openai.APIError as e: st.error(f"Erro na API da OpenAI: {e}")
    except Exception as e: st.error(f"Erro inesperado com OpenAI: {type(e).__name__} - {e}"); return None
    return None # Garantir retorno em todos os caminhos

def reescrever_texto_com_claude(texto_anonimizado: str, system_prompt: str, user_prompt_instruction: str, api_key: str) -> str | None:
    """Chama a API da Anthropic (Claude) para reescrever/resumir o texto."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning("Claude: Não há texto anonimizado para reescrever.")
        return None
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODELO_CLAUDE, # ex: "claude-3-haiku-20240307"
            max_tokens=8192, # Limite generoso para Haiku
            temperature=0.3,
            system=system_prompt, # Claude usa o parâmetro 'system'
            messages=[
                {"role": "user", "content": f"{user_prompt_instruction}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"}
            ]
        )
        texto_final_reescrito = "".join([block.text for block in response.content if block.type == 'text'])
        return texto_final_reescrito.strip() if texto_final_reescrito else None
    except anthropic.AuthenticationError: st.error("Erro de autenticação com a API da Anthropic. Verifique sua chave API.")
    except anthropic.RateLimitError as e: st.error(f"Limite de requisições da API da Anthropic atingido: {e}")
    except anthropic.APIConnectionError as e: st.error(f"Erro de conexão com a API da Anthropic: {e}")
    except anthropic.APIError as e: st.error(f"Erro na API da Anthropic: {e}")
    except Exception as e: st.error(f"Erro inesperado com Anthropic Claude: {type(e).__name__} - {e}"); return None
    return None # Garantir retorno

def reescrever_texto_com_gemini(texto_anonimizado: str, system_prompt: str, user_prompt_instruction: str, api_key: str) -> str | None:
    """Chama a API do Google Gemini para reescrever/resumir o texto."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning("Gemini: Não há texto anonimizado para reescrever.")
        return None
    try:
        genai.configure(api_key=api_key)
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=64000,  # Atualizado para 64k tokens
            temperature=0.3
        )
        safety_settings = [ # Configurações de segurança mais permissivas para teste
            {"category": f"HARM_CATEGORY_{cat}", "threshold": "BLOCK_NONE"} 
            for cat in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
        ]
        model = genai.GenerativeModel(
            model_name=MODELO_GEMINI, 
            system_instruction=system_prompt, # Gemini suporta system_instruction
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        prompt_para_gemini = f"{user_prompt_instruction}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"
        response = model.generate_content(prompt_para_gemini)
        
        # Tratamento da resposta do Gemini (pode ser response.text ou response.parts)
        texto_final_reescrito = ""
        if hasattr(response, 'text') and response.text:
            texto_final_reescrito = response.text
        elif response.parts:
            for part in response.parts:
                if hasattr(part, 'text'):
                    texto_final_reescrito += part.text
        
        if texto_final_reescrito:
            return texto_final_reescrito.strip()
        else:
            # Verifica se o prompt foi bloqueado
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
                st.error(f"O prompt para Gemini foi bloqueado devido a: {response.prompt_feedback.block_reason.name}")
                if response.prompt_feedback.safety_ratings:
                    st.warning("Classificações de segurança do prompt:")
                    for rating in response.prompt_feedback.safety_ratings:
                        st.warning(f"  - Categoria: {rating.category.name}, Probabilidade: {rating.probability.name}")
            else:
                st.error("A LLM (Gemini) não retornou uma resposta de conteúdo válida ou o prompt foi bloqueado sem detalhes.")
            return None

    except ValueError as ve:
        if hasattr(ve, 'args') and ve.args and ("API Key not valid" in str(ve.args[0]) or "API_KEY_INVALID" in str(ve.args[0])):
             st.error(f"Erro de autenticação com a API do Google Gemini. Verifique sua chave API: {ve}")
        elif hasattr(ve, 'args') and ve.args and "prompt was blocked" in str(ve.args[0]).lower(): # Outra forma de prompt bloqueado
            st.error(f"O prompt foi bloqueado pela IA do Google (ValueError). Detalhe: {ve}")
        else:
            st.error(f"Ocorreu um erro de valor ao processar com a LLM (Gemini): {ve}")
    except Exception as e: 
        st.error(f"Erro inesperado com Google Gemini: {type(e).__name__} - {e}")
    return None

def reescrever_texto_com_groq(texto_anonimizado: str, system_prompt: str, user_prompt_instruction: str, api_key: str) -> str | None:
    """Chama a API da Groq para reescrever/resumir o texto com Llama 3 70B."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning(f"Groq ({MODELO_GROQ_LLAMA3_70B}): Não há texto anonimizado para reescrever.")
        return None
    try:
        # Correção: Usar apenas api_key, sem parâmetros extras
        client = Groq(api_key=api_key)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt_instruction}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"}
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODELO_GROQ_LLAMA3_70B,
            temperature=0.3,
            max_tokens=32768,
            # Remover parâmetros que podem causar conflito
        )
        
        if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
            return chat_completion.choices[0].message.content.strip()
        else:
            st.error(f"A LLM (Groq - {MODELO_GROQ_LLAMA3_70B}) não retornou uma resposta de conteúdo válida.")
            return None
            
    except Exception as e: 
        # Tratamento mais específico para problemas de inicialização
        if "unexpected keyword argument" in str(e).lower():
            st.error(f"Erro de compatibilidade com a biblioteca Groq. Tente atualizar: pip install --upgrade groq")
        elif "API key" in str(e).lower() or "authentication" in str(e).lower():
            st.error(f"Erro de autenticação com a API da Groq. Verifique sua GROQ_API_KEY: {e}")
        else:
            st.error(f"Erro com Groq ({MODELO_GROQ_LLAMA3_70B}): {type(e).__name__} - {e}")
        return None

def reescrever_texto_com_ollama(texto_anonimizado: str, system_prompt: str, user_prompt_instruction: str, model_name: str = MODELO_OLLAMA_NEMOTRON) -> str | None:
    """Chama a API do Ollama local para reescrever/resumir o texto."""
    if not texto_anonimizado or not texto_anonimizado.strip():
        st.warning(f"Ollama ({model_name}): Não há texto anonimizado para reescrever.")
        return None
    
    # Tenta incluir system prompt se o modelo/endpoint Ollama suportar, senão concatena ao prompt principal.
    # A API /api/generate do Ollama aceita um campo "system".
    prompt_para_ollama = f"{user_prompt_instruction}\n\nTexto anonimizado para reescrever:\n\n---\n{texto_anonimizado}\n---"
    
    payload = {
        "model": model_name,
        "system": system_prompt, 
        "prompt": prompt_para_ollama,
        "stream": False,
        "options": {
            "temperature": 0.3, 
            "num_predict": 32768, # Limite de tokens de saída para Ollama, ajuste se necessário
            "think":False
        }
    }
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=360) # Timeout aumentado
        response.raise_for_status() # Levanta erro para status HTTP ruins (4xx ou 5xx)
        response_data = response.json()
        
        if "response" in response_data and response_data["response"]:
            return response_data["response"].strip()
        elif "error" in response_data:
            st.error(f"Erro da API Ollama ({model_name}): {response_data['error']}")
            return None
        else:
            st.error(f"A LLM (Ollama - {model_name}) não retornou uma resposta de conteúdo válida ou a resposta estava vazia.")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error(f"Ollama ({model_name}) não está acessível em {OLLAMA_BASE_URL}. Verifique se o Ollama está em execução e o modelo '{model_name}' foi baixado (ex: `ollama pull {model_name}`).")
    except requests.exceptions.Timeout:
        st.error(f"A requisição para o Ollama ({model_name}) demorou muito (timeout). O servidor pode estar sobrecarregado.")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Erro HTTP ao chamar Ollama ({model_name}): {http_err}. Detalhes: {response.text}")
    except Exception as e:
        st.error(f"Erro inesperado com Ollama ({model_name}): {type(e).__name__} - {e}")
    return None

# --- Dicionário de Configurações das LLMs ---
LLM_CONFIGS = {
    "Google Gemini 2.5 Flash Lite": {  # Atualizado nome exibido
        "id": "gemini", "model_api_name": MODELO_GEMINI, 
        "key_loader_function": lambda: carregar_chave_api("GOOGLE_API_KEY", "GOOGLE_API_KEY", "Google Gemini"),
        "rewrite_function": reescrever_texto_com_gemini,
        "token_estimator_model": "gemini_estimate"
    },
    "OpenAI GPT-4o mini": {
        "id": "openai", "model_api_name": MODELO_OPENAI,
        "key_loader_function": lambda: carregar_chave_api("OPENAI_API_KEY", "OPENAI_API_KEY", "OpenAI"),
        "rewrite_function": reescrever_texto_com_openai,
        "token_estimator_model": MODELO_OPENAI
    },
    "Anthropic Claude 3.5 Haiku": {
        "id": "claude", "model_api_name": MODELO_CLAUDE,
        "key_loader_function": lambda: carregar_chave_api("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY", "Anthropic Claude"),
        "rewrite_function": reescrever_texto_com_claude,
        "token_estimator_model": "claude"
    },
    "Groq Llama3.3 70B Versatile": { 
        "id": "groq_llama3_3_70b", 
        "model_api_name": MODELO_GROQ_LLAMA3_70B,
        "key_loader_function": lambda: carregar_chave_api("GROQ_API_KEY", "GROQ_API_KEY", "Groq"),
        "rewrite_function": reescrever_texto_com_groq,
        "token_estimator_model": "openai" 
    },    
    f"Ollama Local NVIDIA NEMOTRON ({MODELO_OLLAMA_NEMOTRON})": {
        "id": "ollama_nemotron", 
        "model_api_name": MODELO_OLLAMA_NEMOTRON, 
        "key_loader_function": lambda: True, 
        "rewrite_function": lambda txt, sys_p, usr_p, api_key_placeholder: reescrever_texto_com_ollama(txt, sys_p, usr_p, MODELO_OLLAMA_NEMOTRON),
        "token_estimator_model": "ollama" 
    }
}
# --- Interface Streamlit Principal ---
# Adicionar ao CSS customizado
st.markdown("""
<style>
    /* Tabs mais modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f6;
        padding: 4px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 8px;
        color: #555;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #003366 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Animações de Loading */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Fade-in suave para resultados */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Pulse Effect para Upload */
    .upload-pulse {
        animation: uploadPulse 2s infinite;
        border-radius: 8px;
    }
    
    @keyframes uploadPulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- Toggle de Tema (Claro/Escuro) ---
col_toggle, col_logo, col_title = st.columns([2,0.1,8])
with col_toggle:
    st.markdown("""
    <style>
        .toggle-row {
            display: flex;
            align-items: center;
            gap: 0.5em;
            margin-bottom: 0.5em;
        }
        .toggle-row label {
            margin-bottom: 0 !important;
            white-space: nowrap;
            font-weight: 500;
            font-size: 1.1em;
            color: #FFD700;
        }
    </style>
    """, unsafe_allow_html=True)
    modo_escuro = st.toggle("", value=False, key="toggle_tema")
    st.markdown(
        '<div class="toggle-row">'
        f'<span style="margin-left: 0.5em;">🌙 Modo Escuro</span>'
        '</div>',
        unsafe_allow_html=True
    )

if modo_escuro:
    st.markdown("""
    <style>
        body, .stApp {
            background-color: #18191A !important;
            color: #F5F6F7 !important;
        }
        /* Header e cards */
        div[data-testid="stMarkdownContainer"] > div[style*="display: flex"] {
            background: #23272F !important;
            border-radius: 12px !important;
            border: 1px solid #222 !important;
        }
        /* Título principal do header */
        h1, h1 span, h1 strong {
            color: #FFF !important;
        }
        /* Subtítulo do header */
        div[data-testid="stMarkdownContainer"] p {
            color: #BBB !important;
        }
        /* Botões */
        .stButton>button, .stDownloadButton>button, .stCopyToClipboard>button {
            background-color: #222 !important;
            color: #FFD700 !important;
            border: 1px solid #444 !important;
        }
        .stButton>button:active, .stButton>button:focus, .stButton>button:hover {
            background-color: #333 !important;
            color: #FFF !important;
            border: 1px solid #FFD700 !important;
        }
        /* Áreas de texto e inputs */
        .stTextArea textarea, textarea, .stTextInput input {
            background-color: #23272F !important;
            color: #FFF !important;
            border: 1px solid #444 !important;
            font-weight: 500 !important;
        }
        /* Força texto branco em textarea desabilitado */
        .stTextArea textarea:disabled, textarea:disabled {
            background-color: #23272F !important;
            color: #FFF !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #FFF !important;
        }
        /* Força cor do texto em todos os estados */
        .stTextArea textarea, .stTextArea textarea:disabled, textarea, textarea:disabled {
            color: #FFF !important;
            -webkit-text-fill-color: #FFF !important;
            opacity: 1 !important;
        }
        /* Placeholder do textarea */
        .stTextArea textarea::placeholder {
            color: #AAA !important;
            opacity: 1 !important;
        }
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #23272F !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #F5F6F7 !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #18191A !important;
            color: #FFD700 !important;
        }
        /* Expander */
        .stExpanderHeader {
            color: #FFD700 !important;
        }
        /* DataFrame */
        .stDataFrame, .stTable {
            background-color: #23272F !important;
            color: #F5F6F7 !important;
        }
        /* Sidebar */
        .stSidebar, .stSidebarContent {
            background-color: #18191A !important;
            color: #F5F6F7 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Renderizar o novo header
render_header()

# O restante do código (abas, etc.) continua aqui
tab_pdf, tab_texto = st.tabs(["🗂️ Anonimizar Arquivo PDF", "⌨️ Anonimizar Texto Colado"])

# Inicialização de estados para garantir que todas as chaves existem
st.session_state.setdefault(KEY_LLM_OUTPUT_PDF_STATE, None)
st.session_state.setdefault(KEY_LLM_OUTPUT_AREA_STATE, None)
st.session_state.setdefault('texto_anonimizado_arquivo'+VERSION_SUFFIX, None)
st.session_state.setdefault(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE, "O resultado da anonimização aparecerá aqui...")
st.session_state.setdefault(KEY_TEXTO_ORIGINAL_PDF_DISPLAY, "")
st.session_state.setdefault(KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM, "")
st.session_state.setdefault(KEY_NUM_TOKENS_PDF_EXTRAIDO, 0)
st.session_state.setdefault('nome_arquivo_carregado'+VERSION_SUFFIX, None)
st.session_state.setdefault('resultados_df_area'+VERSION_SUFFIX, pd.DataFrame()) # Chave específica para df da área de texto
st.session_state.setdefault(KEY_TEXTO_ORIGINAL_AREA, (
    "EXMO. SR. DR. JUIZ FEDERAL DA ____ª VARA DA SEÇÃO JUDICIÁRIA DE SÃO LUÍS – MA – JUIZADO ESPECIAL FEDERAL.\n\n"  # Linha em branco adicionada
    "TRAMITAÇÃO PRIORITÁRIA – AUTOR IDOSO – ART.1.048, I DO CPC\n\n"  # Linha em branco adicionada
    "JOSÉ RIBAMAR SILVA, brasileiro, casado, servidor público federal, portador da Carteira de Identidade nº 19673822002-1 SSP-MA e CPF nº 047.017.123-53, residente e domiciliado na Rua dos Girassois, nº 13, Pedreiras-MA, CEP: 65725-000. \n\n"  # Linha em branco adicionada
    "LEANDRO REIS VIEIRA XAVIER, brasileiro, casado, servidor público federal, portador da Carteira de Identidade nº 048758962013-3 SSP-MA e CPF nº 074.816.243-72, residente e domiciliado na Rua Getulio Vargas, nº 151, Goiabal, Pedreiras-MA, CEP: 65725-000. \n\n"  # Linha em branco adicionada
    "JOÃO FERREIRA SANTOS CORDEIRO, brasileiro, casado, servidor público federal, portador da Carteira de Identidade nº 050513672013-2 SSP-MA e CPF nº 251.195.803-87, residente e domiciliado na Travessa Carlos Martins, nº 22, Seringal, Pedreiras-MA, CEP: 65725-000. \n\n"  # Linha em branco adicionada
    "PEDRO DA SILVA MARTINS OLIVEIRA, brasileiro, casado, servidor público federal, portador da Carteira de Identidade nº 267317 SSP-MA e CPF nº 047.003.093-34, residente e domiciliado na Rua José Sarney, nº 104, Nova Pedreiras, Pedreiras-MA, CEP: 65725-000. \n\n"  # Linha em branco adicionada
    "MANOEL DE JESUS COLEHO CUTRIM, brasileiro, casado, servidor público federal, portador da Carteira de Identidade nº 054691322014-7 SSP-MA e CPF nº 044.646.803-72, residente e domiciliado na Rua Tuiuti, nº 26, Vila do Bec, Zé Doca-MA, CEP: 65365-000, por meio de seu advogado, ao fim assinado, este com escritório profissional na Avenida do Vale, quadra 22, nº 10, Renascença II, São Luís/MA e endereço eletrônico escritorio@mnz.adv.br, onde recebe as notificações de praxe e estilo, ao fim assinado (procuração em anexo), propor a presente: \n\n"  # Linha em branco adicionada
    "AÇÃO ORDINÁRIA SOB O RITO DA LEI Nº 10.259/2001 \n\n"  # Linha em branco adicionada
    "Contra a FUNDAÇÃO NACIONAL DE SAÚDE – FUNASA, pessoa jurídica de Direito Público, situada na Rua do Apicum, n° 23, Centro – São Luís - MA, CEP 65025-070, São Luís/MA, pelos motivos de fato e de direito que passa a expor:"
    # A última linha não precisa de um \n\n extra, a menos que você queira um espaço duplo antes do usuário começar a digitar.
))

# Função genérica para exibir a seção da LLM
def exibir_secao_llm(texto_anonimizado_atual, key_llm_output_state, key_llm_choice, key_llm_rewrite_btn, key_copy_llm, tab_id_suffix):
    if texto_anonimizado_atual:
        st.divider()
        st.subheader("Passo 3 (Opcional): Gere um resumo jurídico com IA")

        llm_display_names = list(LLM_CONFIGS.keys())
        selectbox_key = f"{key_llm_choice}_{tab_id_suffix}"

        st.session_state.setdefault(selectbox_key, llm_display_names[0])

        selected_llm_display_name = st.selectbox(
            "Escolha o modelo de IA para o resumo:",
            options=llm_display_names,
            key=selectbox_key
        )

        config_llm_selecionada = LLM_CONFIGS[selected_llm_display_name]

        st.caption(f"Esta etapa usa o modelo {selected_llm_display_name.split('(')[0].strip()} para gerar o resumo.")

        # --- Seção para o prompt de instrução customizável ---
        # expander_key = f"expander_custom_prompt_{tab_id_suffix}" # Não é mais necessário
        custom_prompt_area_key = f"{KEY_CUSTOM_USER_PROMPT_LLM_INPUT}_{tab_id_suffix}"

        st.session_state.setdefault(custom_prompt_area_key, PROMPT_INSTRUCAO_LLM_BASE)

        # Removido key=expander_key daqui:
        with st.expander("Personalizar Instrução para a IA (Opcional)"): 
            st.markdown("""
            <small>Esta instrução detalhada guia a IA sobre como reescrever o texto anonimizado e substituir as tags (ex: <code>&lt;NOME&gt;</code>) por expressões genéricas.
            Modifique com cuidado, pois uma instrução mal formulada pode levar a resultados insatisfatórios. O texto abaixo é o padrão carregado do sistema.</small>
            """, unsafe_allow_html=True)
            
            st.text_area(
                label="Instrução da Tarefa para a LLM (editável):",
                value=st.session_state[custom_prompt_area_key],
                key=custom_prompt_area_key,
                height=200,
                help="Defina como a IA deve processar o texto anonimizado. O padrão é focado em redação jurídica fluida, substituindo tags por expressões genéricas sem usar markdown."
            )
        # --- Fim da seção do prompt customizável ---

        button_key = f"{key_llm_rewrite_btn}_{tab_id_suffix}"
        if st.button(f"✨ Gerar Resumo com {selected_llm_display_name.split('(')[0].strip()}", key=button_key, type="primary"):
            api_key_ou_status = config_llm_selecionada["key_loader_function"]()

            if api_key_ou_status and texto_anonimizado_atual:
                with st.spinner(f"{selected_llm_display_name.split('(')[0].strip()} está trabalhando na reescrita... Por favor, aguarde."):
                    texto_reescrito = None
                    current_user_instruction_prompt = st.session_state.get(custom_prompt_area_key, PROMPT_INSTRUCAO_LLM_BASE)

                    if not current_user_instruction_prompt or not current_user_instruction_prompt.strip():
                        st.warning("A instrução para a IA estava vazia. Usando a instrução padrão do sistema.")
                        current_user_instruction_prompt = PROMPT_INSTRUCAO_LLM_BASE
                        st.session_state[custom_prompt_area_key] = PROMPT_INSTRUCAO_LLM_BASE
                    
                    if config_llm_selecionada["id"].startswith("ollama"):
                        texto_reescrito = config_llm_selecionada["rewrite_function"](
                            texto_anonimizado_atual,
                            SYSTEM_PROMPT_BASE,
                            current_user_instruction_prompt,
                            None
                        )
                    else:
                        texto_reescrito = config_llm_selecionada["rewrite_function"](
                            texto_anonimizado_atual,
                            SYSTEM_PROMPT_BASE,
                            current_user_instruction_prompt,
                            api_key_ou_status
                        )
                    st.session_state[key_llm_output_state] = texto_reescrito
            elif not api_key_ou_status and not config_llm_selecionada["id"].startswith("ollama"):
                pass
            elif not texto_anonimizado_atual:
                st.warning("Não há texto anonimizado para reescrever.")

        texto_llm_atual = st.session_state.get(key_llm_output_state)
        if texto_llm_atual:
            output_area_key = f"llm_output_display_{tab_id_suffix}"
            copy_button_key = f"{key_copy_llm}_{tab_id_suffix}"
            st.text_area(f"Resumo Gerado por {selected_llm_display_name.split('(')[0].strip()}:", value=texto_llm_atual, height=300, disabled=True, key=output_area_key)
            st_copy_to_clipboard(texto_llm_atual, f"📋 Copiar Resumo ({selected_llm_display_name.split('(')[0].strip()})", key=copy_button_key)
        elif texto_anonimizado_atual:
            st.caption("Selecione uma LLM, ajuste a instrução (opcional) e clique no botão acima para gerar um resumo jurídico do texto anonimizado.")

with tab_pdf:
       
    st.subheader("Passo 1: Carregue seu documento PDF")
    arquivo_pdf_carregado = st.file_uploader(
        "Selecione o arquivo PDF para anonimização:", 
        type=["pdf"], 
        key=KEY_PDF_UPLOADER,
        help="Apenas arquivos .pdf são aceitos."
    )

    st.caption("Limite de 200MB por arquivo.")

    if arquivo_pdf_carregado is not None:
        # Verifica se o arquivo mudou para reprocessar a contagem de tokens
        # Usando .get() para nome_arquivo_carregado para evitar KeyError na primeira execução
        if st.session_state.get('nome_arquivo_carregado'+VERSION_SUFFIX) != arquivo_pdf_carregado.name:
            st.session_state['nome_arquivo_carregado'+VERSION_SUFFIX] = arquivo_pdf_carregado.name
            st.session_state['texto_anonimizado_arquivo'+VERSION_SUFFIX] = None 
            st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = "" 
            st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None
            st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM] = ""
            st.session_state[KEY_NUM_TOKENS_PDF_EXTRAIDO] = 0
            
            with st.spinner(f"Lendo o arquivo '{arquivo_pdf_carregado.name}' para calcular tokens..."):
                bytes_do_pdf = arquivo_pdf_carregado.getvalue()
                # Garante que passamos um objeto BytesIO para extrair_texto_de_pdf
                texto_extraido_contagem = extrair_texto_de_pdf(io.BytesIO(bytes_do_pdf))
                st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM] = texto_extraido_contagem if texto_extraido_contagem else ""
                
                if st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM].strip():
                    # Determina qual LLM está selecionada para estimar tokens (default para OpenAI se nada selecionado ainda)
                    llm_selecionada_para_token = LLM_CONFIGS.get(st.session_state.get(f"{KEY_LLM_CHOICE_PDF}_pdf", list(LLM_CONFIGS.keys())[0]), {}).get("token_estimator_model", "openai")
                    st.session_state[KEY_NUM_TOKENS_PDF_EXTRAIDO] = contar_tokens_para_estimativa(st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM], llm_provider=llm_selecionada_para_token)
                else:
                    if st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM] is not None: # Evita warning se extração falhou e já deu erro
                        st.warning("O PDF carregado parece não conter texto útil para contagem de tokens.")
            arquivo_pdf_carregado.seek(0) # Reseta para releitura

        # Exibe a contagem de tokens se disponível
        if st.session_state.get(KEY_NUM_TOKENS_PDF_EXTRAIDO, 0) > 0:
            llm_selecionada_display = st.session_state.get(f"{KEY_LLM_CHOICE_PDF}_pdf", list(LLM_CONFIGS.keys())[0]).split('(')[0].strip()
            token_provider_display = "Estimativa Genérica"
            if "OpenAI" in llm_selecionada_display: token_provider_display = "OpenAI"
            elif "Claude" in llm_selecionada_display: token_provider_display = "Anthropic"
            elif "Gemini" in llm_selecionada_display: token_provider_display = "Google"
            elif "Ollama" in llm_selecionada_display: token_provider_display = "Ollama"


            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown("<strong>Arquivo Carregado:</strong>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 1em; font-weight: normal; margin-top: -10px;'>{st.session_state.get('nome_arquivo_carregado'+VERSION_SUFFIX, 'N/A')}</p>", unsafe_allow_html=True)
            with col_info2:
                st.markdown(f"<strong>Tokens Estimados ({token_provider_display}):</strong>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 1em; font-weight: normal; margin-top: -10px;'>{st.session_state.get(KEY_NUM_TOKENS_PDF_EXTRAIDO, 0)}</p>", unsafe_allow_html=True)
        st.divider()

        st.subheader("Passo 2: Anonimize o conteúdo do PDF")
        if st.button("🔍 Anonimizar PDF Carregado", key=KEY_BOTAO_ANONIMIZAR_PDF, type="primary", 
                      disabled=(not analyzer_engine or not anonymizer_engine or not st.session_state.get(KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM,"").strip())):
            if analyzer_engine and anonymizer_engine:
                texto_para_anonimizar = st.session_state.get(KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM)
                # Tenta re-extrair se o texto não estiver no estado da sessão (ex: após refresh ou erro)
                if not texto_para_anonimizar or not texto_para_anonimizar.strip():
                    if arquivo_pdf_carregado: # Checa se o uploader ainda tem o arquivo
                        arquivo_pdf_carregado.seek(0) 
                        bytes_pdf = arquivo_pdf_carregado.getvalue()
                        texto_para_anonimizar = extrair_texto_de_pdf(io.BytesIO(bytes_pdf))
                        st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM] = texto_para_anonimizar if texto_para_anonimizar else ""
                    else:
                        st.warning("Por favor, carregue um arquivo PDF novamente.")
                        st.stop() # Interrompe a execução se não há arquivo para processar
                
                st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY] = st.session_state[KEY_TEXTO_EXTRAIDO_PDF_CONTAGEM]
                st.session_state[KEY_LLM_OUTPUT_PDF_STATE] = None # Limpa resumo anterior

                if texto_para_anonimizar and texto_para_anonimizar.strip():
                    with st.spinner(f"Anonimizando '{st.session_state.get('nome_arquivo_carregado'+VERSION_SUFFIX)}'..."):
                        entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA", "ID_DOCUMENTO", "CNH", "SIAPE", "CI", "CIN"]
                        entidades_para_analise = list(set(entidades_para_analise)); 
                        if "DEFAULT" in entidades_para_analise: entidades_para_analise.remove("DEFAULT")
                        resultados_analise_pdf = analyzer_engine.analyze(text=texto_para_anonimizar, language='pt', entities=entidades_para_analise, return_decision_process=False)
                        resultado_anonimizado_pdf_obj = anonymizer_engine.anonymize(text=texto_para_anonimizar, analyzer_results=resultados_analise_pdf, operators=operadores)
                        st.session_state['texto_anonimizado_arquivo'+VERSION_SUFFIX] = resultado_anonimizado_pdf_obj.text
                        st.success(f"Arquivo '{st.session_state.get('nome_arquivo_carregado'+VERSION_SUFFIX)}' anonimizado com sucesso!")
                elif texto_para_anonimizar is not None: 
                    st.warning("O PDF carregado parece não conter texto útil para anonimização.")
                    st.session_state['texto_anonimizado_arquivo'+VERSION_SUFFIX] = None
                else: # Falha na extração
                    st.session_state['texto_anonimizado_arquivo'+VERSION_SUFFIX] = None 
            else: 
                st.error("Motores de anonimização não estão prontos.")
        
        # Mostrar expander do texto original se ele existir no estado da sessão
        if st.session_state.get(KEY_TEXTO_ORIGINAL_PDF_DISPLAY, "").strip():
            with st.expander("📄 Ver Texto Extraído do PDF (Original)", expanded=False):
                st.text_area("Texto Original:", value=st.session_state[KEY_TEXTO_ORIGINAL_PDF_DISPLAY], height=200, disabled=True)

    # Exibir resultados da anonimização do PDF e opção de LLM
    texto_anonimizado_pdf_atual = st.session_state.get('texto_anonimizado_arquivo'+VERSION_SUFFIX)
    if texto_anonimizado_pdf_atual: # Se há texto anonimizado do PDF para mostrar
        st.divider()
        st.subheader("Resultado da Anonimização (Camada 1)")
        st.text_area("Texto Anonimizado (com tags):", value=texto_anonimizado_pdf_atual, height=300, disabled=True) # key removida
        
        col_dl_docx, col_copy_text_file = st.columns([1,1]) 
        with col_dl_docx:
            try:
                docx_bytes = criar_docx_bytes(texto_anonimizado_pdf_atual)
                st.download_button(label="📥 Baixar como .docx", data=docx_bytes, 
                                   file_name=f"anonimizado_{st.session_state.get('nome_arquivo_carregado'+VERSION_SUFFIX, 'arquivo')}.docx", 
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="secondary")
            except Exception as e: 
                st.error(f"Erro ao gerar DOCX: {e}")
        with col_copy_text_file:
            st_copy_to_clipboard(texto_anonimizado_pdf_atual, "📋 Copiar Texto Anonimizado", key=KEY_COPY_BTN_FILE_ANON)
        
        # Chama a função genérica para exibir a seção LLM
        exibir_secao_llm(texto_anonimizado_pdf_atual, 
                         KEY_LLM_OUTPUT_PDF_STATE, 
                         KEY_LLM_CHOICE_PDF, 
                         KEY_LLM_REWRITE_BTN_PDF, 
                         KEY_COPY_LLM_PDF, 
                         "pdf") # tab_id_suffix para chaves únicas
with tab_texto:
     
    st.subheader("Passo 1: Insira o texto para anonimizar")

    col_original, col_anonimizado = st.columns(2)
    with col_original:
        st.markdown("##### Texto Original")
        st.text_area("Cole ou digite o texto aqui:", height=300, key=KEY_TEXTO_ORIGINAL_AREA, 
                     help="Insira o texto que você deseja analisar e anonimizar.")
        st.button("🗑️ Limpar Tudo (Área de Texto)", key=KEY_BOTAO_APAGAR_AREA, on_click=callback_apagar_textos_area, 
                  help="Apaga o texto original, o resultado anonimizado, as entidades detectadas e o resumo da IA para esta aba.")
    with col_anonimizado:
        st.markdown("##### Texto Anonimizado (Camada 1)")
        st.text_area("Resultado da anonimização (com tags):", 
                     height=300, disabled=True, key=KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE) # key adicionada, value removido
        if st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE) and \
           st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE) not in ["O resultado da anonimização aparecerá aqui...", "O resultado da área de texto aparecerá aqui...", "Erro ao processar o texto da área."]:
            st_copy_to_clipboard(st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE], "📋 Copiar Texto Anonimizado", key=KEY_COPY_BTN_AREA_ANON)
        else: 
            st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True) # Mantém alinhamento
    
    st.divider()
    st.subheader("Passo 2: Anonimize o texto da área")
    if st.button("🔍 Anonimizar Texto da Área", type="primary", key=KEY_BOTAO_ANONIMIZAR_AREA, 
                  disabled=(not analyzer_engine or not anonymizer_engine)):
        texto_para_processar = st.session_state.get(KEY_TEXTO_ORIGINAL_AREA, "")
        st.session_state[KEY_LLM_OUTPUT_AREA_STATE] = None # Limpa resumo anterior
        
        if not texto_para_processar.strip():
            st.warning("Por favor, insira um texto na área para anonimizar.")
        elif analyzer_engine and anonymizer_engine:
            try:
                with st.spinner("Analisando e anonimizando o texto da área..."):
                    entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA", "CNH", "SIAPE", "CI", "CIN"]
                    entidades_para_analise = list(set(entidades_para_analise))
                    if "DEFAULT" in entidades_para_analise: entidades_para_analise.remove("DEFAULT")
                    
                    resultados_analise = analyzer_engine.analyze(text=texto_para_processar, language='pt', entities=entidades_para_analise, return_decision_process=False)
                    resultado_anonimizado_obj = anonymizer_engine.anonymize(text=texto_para_processar, analyzer_results=resultados_analise, operators=operadores)
                
                st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = resultado_anonimizado_obj.text
                
                dados_resultados = []
                if resultados_analise:
                    for res in sorted(resultados_analise, key=lambda x: x.start):
                        dados_resultados.append({
                            "Entidade": res.entity_type, 
                            "Texto Detectado": texto_para_processar[res.start:res.end], 
                            "Início": res.start, 
                            "Fim": res.end, 
                            "Score": f"{res.score:.2f}"
                        })
                st.session_state['resultados_df_area'+VERSION_SUFFIX] = pd.DataFrame(dados_resultados)
                
                if dados_resultados: 
                    st.success("Texto da área anonimizado e entidades detectadas!")
                else: 
                    st.info("Nenhuma PII detectada no texto da área.")
            except Exception as e:
                st.error(f"Ocorreu um erro durante a anonimização da área de texto: {e}")
                st.session_state[KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE] = "Erro ao processar o texto da área."
                st.session_state['resultados_df_area'+VERSION_SUFFIX] = pd.DataFrame()
        else: 
            st.error("Motores de anonimização não estão prontos.")

    # Exibir tabela de entidades detectadas
    # Usando .get() para segurança, e a chave correta para o dataframe
    df_resultados_atual = st.session_state.get('resultados_df_area'+VERSION_SUFFIX, pd.DataFrame())
    if not df_resultados_atual.empty:
        with st.expander("📊 Ver Entidades Detectadas (do Texto da Área Original)", expanded=False):
            st.markdown("As seguintes entidades foram detectadas no texto original da área:")
            st.dataframe(df_resultados_atual, use_container_width=True) 

    # Chamar a função genérica para exibir a seção LLM para a aba de texto
    texto_anonimizado_area_atual = st.session_state.get(KEY_TEXTO_ANONIMIZADO_OUTPUT_AREA_STATE)
    # Condição para evitar mostrar seção LLM se o texto for apenas o placeholder inicial ou de erro
    if texto_anonimizado_area_atual and \
       texto_anonimizado_area_atual not in ["O resultado da anonimização aparecerá aqui...", 
                                            "O resultado da área de texto aparecerá aqui...", 
                                            "Erro ao processar o texto da área."]:
        exibir_secao_llm(texto_anonimizado_area_atual, 
                         KEY_LLM_OUTPUT_AREA_STATE, 
                         KEY_LLM_CHOICE_AREA, 
                         KEY_LLM_REWRITE_BTN_AREA, 
                         KEY_COPY_LLM_AREA, 
                         "area") # tab_id_suffix para chaves únicas

# --- Informações na Sidebar ---
st.sidebar.header("Sobre")
sidebar_text_sobre = """
**AnonimizaJUD**

Versão 0.91 (Beta) 

Desenvolvido por:

Juiz Federal Rodrigo Gonçalves de Souza
"""
st.sidebar.markdown(sidebar_text_sobre)

st.sidebar.divider()
st.sidebar.markdown(
    "**Como usar:**\n\n"
    "1. **Anonimize seu texto** (Camada 1):\n"
    "   - Na aba '🗂️ Anonimizar Arquivo PDF', carregue um PDF e clique em 'Anonimizar PDF Carregado'. Uma estimativa de tokens será exibida.\n"
    "   - Na aba '⌨️ Anonimizar Texto Colado', insira o texto e clique em 'Anonimizar Texto da Área'.\n\n"
    "2. **Gere um Resumo Jurídico com IA** (Camada 2 - Opcional):\n"
    "   - Após a anonimização, escolha o modelo de IA desejado na lista suspensa.\n"
    "   - Clique no botão '✨ Gerar Resumo'.\n\n"
    "**Importante:**\n"
    "- Trata-se de ferramenta em desenvolvimento.\n"
    "- Sempre confira o resultado gerado (a IA pode cometer erro)."
)

# --- Funções de Interface Melhoradas ---
def create_progress_steps(current_step, total_steps, step_labels):
    """Cria um progress bar visual com etapas numeradas"""
    progress_html = """
    <div style="margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    """
    
    for i, label in enumerate(step_labels, 1):
        is_active = i == current_step
        is_completed = i < current_step
        
        status_color = "#28a745" if is_completed else "#007bff" if is_active else "#dee2e6"
        text_color = "#fff" if (is_active or is_completed) else "#6c757d"
        
        progress_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: {status_color}; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;
                        font-weight: bold; color: {text_color}; font-size: 1.1rem;">
                {i if not is_completed else "✓"}
            </div>
            <span style="font-size: 0.85rem; color: {text_color}; text-align: center; font-weight: 500;">
                {label}
            </span>
        </div>
        """
        
        if i < len(step_labels):
            progress_html += f"""
            <div style="flex: 1; height: 2px; background: {'#28a745' if is_completed else '#dee2e6'}; 
                        margin: 0 1rem; margin-top: 20px;"></div>
            """
    
    progress_html += """
        </div>
        <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; text-align: center;">
            <span style="color: #007bff; font-weight: 600;">Etapa {current_step} de {total_steps}</span>
        </div>
    </div>
    """
    
    return progress_html

def show_enhanced_loading(operation_name, current_step=None, total_steps=None, step_labels=None):
    """Mostra loading melhorado com progress bar se disponível"""
    if current_step and total_steps and step_labels:
        st.markdown(create_progress_steps(current_step, total_steps, step_labels), unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div class="loading-spinner"></div>
            <div style="margin-left: 1rem;">
                <div style="font-weight: 600; color: #007bff; font-size: 1.1rem;">{operation_name}</div>
                <div style="color: #6c757d; font-size: 0.9rem;">Processando, aguarde...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_toast_notification(message, notification_type="info", duration=5):
    """Mostra notificação toast elegante"""
    colors = {
        "success": {"bg": "#d4edda", "border": "#c3e6cb", "text": "#155724", "icon": "✅"},
        "error": {"bg": "#f8d7da", "border": "#f5c6cb", "text": "#721c24", "icon": "❌"},
        "warning": {"bg": "#fff3cd", "border": "#ffeaa7", "text": "#856404", "icon": "⚠️"},
        "info": {"bg": "#d1ecf1", "border": "#bee5eb", "text": "#0c5460", "icon": "ℹ️"}
    }
    
    color_scheme = colors.get(notification_type, colors["info"])
    
    toast_html = f"""
    <div id="toast-{hash(message)}" style="
        position: fixed; top: 20px; right: 20px; z-index: 1000;
        background: {color_scheme['bg']}; border: 1px solid {color_scheme['border']};
        border-radius: 8px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 400px; animation: slideInRight 0.3s ease-out;
        display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.2rem;">{color_scheme['icon']}</span>
        <div style="color: {color_scheme['text']}; font-weight: 500;">{message}</div>
        <button onclick="document.getElementById('toast-{hash(message)}').remove()" 
                style="margin-left: auto; background: none; border: none; color: {color_scheme['text']}; 
                       cursor: pointer; font-size: 1.2rem;">×</button>
    </div>
    <style>
        @keyframes slideInRight {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
    </style>
    <script>
        setTimeout(function() {{
            const toast = document.getElementById('toast-{hash(message)}');
            if (toast) {{
                toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
                setTimeout(() => toast.remove(), 300);
            }}
        }}, {duration * 1000});
        
        @keyframes slideOutRight {{
            from {{ transform: translateX(0); opacity: 1; }}
            to {{ transform: translateX(100%); opacity: 0; }}
        }}
    </script>
    """
    
    st.markdown(toast_html, unsafe_allow_html=True)

def create_contextual_help(help_text, icon="💡", title="Dica"):
    """Cria caixa de ajuda contextual elegante"""
    help_html = f"""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                border-left: 4px solid #2196f3; border-radius: 8px; padding: 1rem; 
                margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <strong style="color: #1976d2; font-size: 0.95rem;">{title}</strong>
        </div>
        <p style="color: #424242; font-size: 0.9rem; margin: 0; line-height: 1.4;">
            {help_text}
        </p>
    </div>
    """
    return help_html

def create_metrics_dashboard():
    """Cria dashboard de métricas visuais"""
    # Simular métricas (em produção, viriam do banco de dados)
    metrics = {
        "arquivos_processados": st.session_state.get('metric_arquivos_processados', 0),
        "textos_anonimizados": st.session_state.get('metric_textos_anonimizados', 0),
        "tokens_processados": st.session_state.get('metric_tokens_processados', 0),
        "tempo_medio_processamento": st.session_state.get('metric_tempo_medio', 0)
    }
    
    dashboard_html = f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 1rem 0;">
        <h3 style="color: #003366; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
            📊 Dashboard de Métricas
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <!-- Métrica 1 -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['arquivos_processados']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Arquivos Processados</div>
            </div>
            
            <!-- Métrica 2 -->
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['textos_anonimizados']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Textos Anonimizados</div>
            </div>
            
            <!-- Métrica 3 -->
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['tokens_processados']:,}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Tokens Processados</div>
            </div>
            
            <!-- Métrica 4 -->
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['tempo_medio_processamento']:.1f}s
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Tempo Médio</div>
            </div>
        </div>
        
        <!-- Gráfico de atividade (simulado) -->
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e0;">
            <h4 style="color: #003366; margin-bottom: 1rem;">Atividade Recente</h4>
            <div style="display: flex; align-items: end; gap: 0.5rem; height: 100px;">
                {''.join([f'<div style="background: linear-gradient(to top, #007bff, #0056b3); width: 30px; height: {20 + (i * 10)}px; border-radius: 4px 4px 0 0; opacity: {0.3 + (i * 0.1)};"></div>' for i in range(7)])}
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
                <span>7 dias atrás</span>
                <span>Hoje</span>
            </div>
        </div>
    </div>
    """
    
    return dashboard_html

def create_file_preview_card(file_name, file_size, file_type, upload_time):
    """Cria card de preview do arquivo carregado"""
    size_mb = file_size / (1024 * 1024)
    
    preview_html = f"""
    <div style="background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem;">
                📄
            </div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #003366; font-size: 1.1rem;">{file_name}</h4>
                <div style="display: flex; gap: 1rem; font-size: 0.85rem; color: #666;">
                    <span>📏 {size_mb:.1f} MB</span>
                    <span>📋 {file_type.upper()}</span>
                    <span>🕒 {upload_time}</span>
                </div>
            </div>
            <div style="background: #e8f5e8; color: #2e7d32; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                ✅ Carregado
            </div>
        </div>
    </div>
    """
    
    return preview_html

