# anonimizador_core.py

import os
import PyPDF2
import io
import re
import spacy
import docx
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.pattern import Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class AnonimizadorCore:
    """Sistema inteligente de anonimização de documentos jurídicos brasileiros utilizando IA (Microsoft Presidio) para proteger dados sensíveis."""
    
    def __init__(self):
        """Inicializa o motor de anonimização, carregando modelos, listas e reconhecedores."""
        self.modelos_disponiveis = {
            "GPT-4": "openai", "Claude": "anthropic", "Gemini": "google",
            "Groq": "groq", "Ollama": "ollama"
        }
        
        # Carrega todas as listas de configuração de arquivos externos
        self._carregar_listas_brasileiras()
        
        # Configura o motor de Processamento de Linguagem Natural (NLP)
        try:
            spacy.load('pt_core_news_lg')
            spacy_engine_obj = SpacyNlpEngine(models=[{'lang_code': 'pt', 'model_name': 'pt_core_news_lg'}])
            self.analyzer = AnalyzerEngine(nlp_engine=spacy_engine_obj, supported_languages=["pt"], default_score_threshold=0.4)
            print("✅ Engine spaCy português configurado com sucesso!")
        except OSError:
            print("⚠️ Modelo spaCy 'pt_core_news_lg' não encontrado. Usando configuração básica.")
            self.analyzer = AnalyzerEngine()
        except Exception as e:
            print(f"⚠️ Erro ao configurar NLP Engine: {e}")
            self.analyzer = AnalyzerEngine()
        
        # Inicializa o motor que efetivamente anonimiza o texto
        self.anonymizer = AnonymizerEngine()
        
        # Adiciona todas as regras e conhecimentos específicos do Brasil ao motor
        self._adicionar_reconhecedores_pt_br()
    
    # --- MÉTODOS DE CARREGAMENTO DE LISTAS ---

    def _carregar_lista_de_arquivo(self, nome_arquivo: str) -> list[str]:
        """Função genérica e reutilizável para carregar uma lista de um arquivo .txt."""
        caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
        try:
            with open(caminho, encoding="utf-8") as f:
                # Lê cada linha, remove espaços extras e ignora linhas vazias ou de comentário
                return [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]
        except FileNotFoundError:
            print(f"⚠️ Arquivo de configuração não encontrado: '{nome_arquivo}'. A lista ficará vazia.")
            return []
        except Exception as e:
            print(f"⚠️ Erro ao carregar o arquivo '{nome_arquivo}': {e}")
            return []

    def _carregar_listas_brasileiras(self):
        """Carrega todas as listas de termos específicos brasileiros, tanto as internas quanto as de arquivos."""
        self.estados_capitais = [
            "Acre", "AC", "Alagoas", "AL", "Amapá", "AP", "Amazonas", "AM", "Bahia", "BA", "Ceará", "CE", 
            "Distrito Federal", "DF", "Espírito Santo", "ES", "Goiás", "GO", "Maranhão", "MA", "Mato Grosso", "MT", 
            "Mato Grosso do Sul", "MS", "Minas Gerais", "MG", "Pará", "PA", "Paraíba", "PB", "Paraná", "PR", 
            "Pernambuco", "PE", "Piauí", "PI", "Rio de Janeiro", "RJ", "Rio Grande do Norte", "RN", 
            "Rio Grande do Sul", "RS", "Rondônia", "RO", "Roraima", "RR", "Santa Catarina", "SC", "São Paulo", "SP", 
            "Sergipe", "SE", "Tocantins", "TO", "Aracaju", "Belém", "Belo Horizonte", "Boa Vista", "Brasília", 
            "Campo Grande", "Cuiabá", "Curitiba", "Florianópolis", "Fortaleza", "Goiânia", "João Pessoa", "Macapá", 
            "Maceió", "Manaus", "Natal", "Palmas", "Porto Alegre", "Porto Velho", "Recife", "Rio Branco", "Salvador", 
            "São Luís", "São Paulo", "Teresina", "Vitória"
        ]
        self.termos_legal_header = [
            "EXMO. SR. DR. JUIZ FEDERAL", "EXMO SR DR JUIZ FEDERAL", "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL", 
            "JUIZ FEDERAL", "EXMO. SR. DR. JUIZ DE DIREITO", "EXMO SR DR JUIZ DE DIREITO", 
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO", "JUIZ DE DIREITO", "JUIZADO ESPECIAL FEDERAL", 
            "VARA DA SEÇÃO JUDICIÁRIA", "SEÇÃO JUDICIÁRIA", "EXMO.", "EXMO", "SR.", "DR.", "Dra.", "DRA.", 
            "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) FEDERAL", "EXCELENTÍSSIMO", "Senhor", "Doutor", 
            "Senhora", "Doutora", "EXCELENTÍSSIMA", "EXCELENTÍSSIMO(A)", "Senhor(a)", "Doutor(a)", "Juiz", 
            "Juíza", "Juiz(a)", "Juiz(íza)"
        ]
        
        # Carregamento das listas externas usando a função genérica
        self.sobrenomes_comuns = self._carregar_lista_de_arquivo("sobrenomes_comuns.txt")
        self.termos_comuns = self._carregar_lista_de_arquivo("termos_comuns.txt")
        self.termos_legais = self._carregar_lista_de_arquivo("termos_legais.txt")

    # --- MÉTODOS DE CONFIGURAÇÃO E ANONIMIZAÇÃO ---

    def _adicionar_reconhecedores_pt_br(self):
        """Adiciona reconhecedores personalizados para o contexto brasileiro."""
        try:
            # --- Reconhecedores de NEGAÇÃO (Deny-List) ---
            # O objetivo é impedir a anonimização de termos que não são sensíveis.
            if self.estados_capitais:
                self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="SAFE_LOCATION", name="SafeLocationRecognizer", deny_list=self.estados_capitais, deny_list_score=0.99))
            if self.termos_legal_header:
                self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="LEGAL_HEADER", name="LegalHeaderRecognizer", deny_list=self.termos_legal_header, deny_list_score=0.99))
            if self.termos_comuns:
                self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="COMMON_TERM", name="CommonTermRecognizer", deny_list=self.termos_comuns, deny_list_score=0.9))

            # --- Reconhecedores POSITIVOS (Pattern Matching) ---
            # O objetivo é encontrar e classificar ativamente entidades específicas.
            
            # Reconhecedores para documentos (CPF, OAB, CEP, etc.)
            cpf_pattern = Pattern(name="CpfRegexPattern", regex=r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", score=0.95)
            self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="CPF", patterns=[cpf_pattern]))
            oab_pattern = Pattern(name="OabRegexPattern", regex=r"\bOAB[/\s]*[A-Z]{2}\s*\d{1,6}\b", score=0.95)
            self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="OAB_NUMBER", patterns=[oab_pattern]))
            # Adicione aqui outros reconhecedores de documentos (CEP, CNH, RG...)

            # Reconhecedor para Jargão Jurídico (Nossa nova regra)
            if self.termos_legais:
                legal_patterns = [Pattern(name=f"legal_{t.lower().replace(' ', '_')}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.98) for t in self.termos_legais]
                self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="LEGAL_TERM", name="LegalTermRecognizer", patterns=legal_patterns))

            # Reconhecedor para Sobrenomes Frequentes para ajudar a encontrar nomes
            if self.sobrenomes_comuns:
                surnames_patterns = [Pattern(name=f"surname_{s.lower().replace(' ', '_')}", regex=rf"(?i)\b{re.escape(s)}\b", score=0.97) for s in self.sobrenomes_comuns]
                self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PERSON", name="BrazilianCommonSurnamesRecognizer", patterns=surnames_patterns))

            print("✅ Reconhecedores personalizados avançados para português brasileiro adicionados!")
        except Exception as e:
            print(f"⚠️ Erro ao adicionar reconhecedores personalizados: {e}")

    def obter_operadores_anonimizacao(self):
        """Define como cada tipo de entidade (PII) deve ser tratado durante a anonimização."""
        return {
            "DEFAULT": OperatorConfig("keep"),
            # --- Entidades a serem ANONIMIZADAS ---
            "PERSON": OperatorConfig("replace", {"new_value": "<NOME>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<ENDERECO>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "CPF": OperatorConfig("replace", {"new_value": "***"}),
            "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
            "CEP_NUMBER": OperatorConfig("replace", {"new_value": "***"}),
            "CNH": OperatorConfig("replace", {"new_value": "***"}),
            "SIAPE": OperatorConfig("replace", {"new_value": "***"}),
            "RG": OperatorConfig("replace", {"new_value": "***"}),
            "CI": OperatorConfig("replace", {"new_value": "***"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),
            
            # --- Entidades a serem MANTIDAS (Protegidas) ---
            "LEGAL_TERM": OperatorConfig("keep"),
            "COMMON_TERM": OperatorConfig("keep"),
            "SAFE_LOCATION": OperatorConfig("keep"),
            "LEGAL_HEADER": OperatorConfig("keep"),
            "ID_DOCUMENTO": OperatorConfig("keep"),
            "DATE_TIME": OperatorConfig("keep"),
        }

    # --- MÉTODOS DE EXTRAÇÃO E PROCESSAMENTO ---
    
    def extrair_texto_pdf(self, caminho_arquivo: str) -> str:
        """Extrai texto de um arquivo PDF."""
        try:
            texto_completo = []
            with open(caminho_arquivo, 'rb') as arquivo:
                leitor_pdf = PyPDF2.PdfReader(arquivo)
                for pagina in leitor_pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo.append(texto)
            return "\n".join(texto_completo)
        except Exception as e:
            print(f"❌ Erro ao extrair texto do PDF: {str(e)}")
            return ""

    def extrair_texto_docx(self, caminho_arquivo: str) -> str:
        """Extrai texto de um arquivo DOCX."""
        try:
            documento = docx.Document(caminho_arquivo)
            texto_completo = [paragrafo.text for paragrafo in documento.paragraphs]
            return "\n".join(texto_completo)
        except Exception as e:
            print(f"❌ Erro ao extrair texto do DOCX: {str(e)}")
            return ""
    
    def detectar_entidades(self, texto: str) -> list:
        """Usa o motor do Presidio para analisar o texto e encontrar entidades."""
        try:
            return self.analyzer.analyze(text=texto, language='pt')
        except Exception as e:
            raise Exception(f"Erro ao detectar entidades: {str(e)}")
            
    def anonimizar_texto(self, texto: str, entidades_detectadas: list = None) -> str:
        """Aplica a anonimização no texto com base nas entidades encontradas."""
        try:
            if entidades_detectadas is None:
                entidades_detectadas = self.detectar_entidades(texto)
            
            operadores = self.obter_operadores_anonimizacao()
            
            resultado = self.anonymizer.anonymize(
                text=texto,
                analyzer_results=entidades_detectadas,
                operators=operadores
            )
            return resultado.text
        except Exception as e:
            raise Exception(f"Erro ao anonimizar texto: {str(e)}")
            
    def processar_documento(self, caminho_arquivo: str, modelo: str = "", chave_api: str = "") -> str:
        """Orquestra o fluxo completo: ler arquivo, detectar entidades e anonimizar."""
        try:
            if not os.path.exists(caminho_arquivo):
                return "❌ Arquivo não encontrado."
            
            texto = ""
            caminho_lower = caminho_arquivo.lower()
            
            if caminho_lower.endswith('.pdf'):
                texto = self.extrair_texto_pdf(caminho_arquivo)
            elif caminho_lower.endswith('.txt'):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    texto = f.read()
            elif caminho_lower.endswith('.docx'):
                texto = self.extrair_texto_docx(caminho_arquivo)
            else:
                return "❌ Formato de arquivo não suportado. Use .pdf, .txt ou .docx."

            if not texto:
                return "❌ Não foi possível extrair texto do arquivo."

            entidades = self.detectar_entidades(texto)
            if not entidades:
                return "✅ Documento processado. Nenhuma entidade sensível foi detectada para anonimização."

            texto_anonimizado = self.anonimizar_texto(texto, entidades)
            return texto_anonimizado
            
        except Exception as e:
            return f"❌ Erro ao processar documento: {str(e)}"