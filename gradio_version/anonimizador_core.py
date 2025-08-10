# anonimizador_core.py

import os
import PyPDF2
import io
import re
import spacy
import docx
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.pattern import Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class AnonimizadorCore:
    """Sistema inteligente de anonimização de documentos jurídicos brasileiros utilizando IA (Microsoft Presidio) para proteger dados sensíveis."""
    
    def __init__(self):
        """Inicializa o motor de anonimização, carregando modelos, listas e reconhecedores."""
        self._carregar_listas_brasileiras()
        
        try:
            # --- CORREÇÃO FINAL APLICADA AQUI ---
            # 1. Carregar o modelo spaCy
            print("Carregando modelo spaCy 'pt_core_news_lg'...")
            nlp_engine = SpacyNlpEngine(models=[{'lang_code': 'pt', 'model_name': 'pt_core_news_lg'}])
            print("Modelo spaCy carregado.")

            # 2. Inicializar o AnalyzerEngine de forma padrão.
            # Isto garante que os reconhecedores base (como SpacyRecognizer para NOMES) são carregados.
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pt"])
            print("AnalyzerEngine inicializado com reconhecedores padrão.")

            # 3. AGORA, adicionar os nossos reconhecedores personalizados ao registro já existente.
            self._adicionar_reconhecedores_pt_br()
            
            print("✅ Configuração do Anonimizador concluída com sucesso!")

        except OSError:
            print("⚠️ Modelo spaCy 'pt_core_news_lg' não encontrado. Instale-o com: python -m spacy download pt_core_news_lg")
            # Fallback para configuração sem spaCy se o modelo não for encontrado
            self.analyzer = AnalyzerEngine(supported_languages=["pt"])
            self._adicionar_reconhecedores_pt_br()
        except Exception as e:
            print(f"❌ Erro crítico ao configurar o Anonimizador: {e}")
            # Em caso de erro, cria um analyzer vazio para evitar que a aplicação quebre
            self.analyzer = AnalyzerEngine()
        
        self.anonymizer = AnonymizerEngine()
    
    def _carregar_lista_de_arquivo(self, nome_arquivo: str) -> list[str]:
        caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
        try:
            with open(caminho, encoding="utf-8") as f:
                return [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]
        except FileNotFoundError:
            print(f"⚠️ Arquivo de configuração não encontrado: '{nome_arquivo}'.")
            return []
        except Exception as e:
            print(f"⚠️ Erro ao carregar o arquivo '{nome_arquivo}': {e}")
            return []

    def _carregar_listas_brasileiras(self):
        self.termos_comuns = self._carregar_lista_de_arquivo("termos_comuns.txt")
        self.termos_legais = self._carregar_lista_de_arquivo("termos_legais.txt")

    def _adicionar_reconhecedores_pt_br(self):
        """Adiciona reconhecedores personalizados (Regex) para o contexto brasileiro."""
        try:
            # Criar instâncias dos reconhecedores baseados em padrões
            cpf_recognizer = PatternRecognizer(supported_entity="CPF", name="CpfRecognizer",
                                               patterns=[Pattern(name="CpfPattern", regex=r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', score=1.0)])
            
            rg_recognizer = PatternRecognizer(supported_entity="RG_NUMBER", name="RgRecognizer",
                                              patterns=[Pattern(name="RgPattern", regex=r'\b(?:RG|R\.G\.|R G)\s*n?[°º]?\s*:?\s*(\d{1,2}[\.]?\d{3}[\.]?\d{3}-?[\dX])\b', score=1.0)])

            oab_recognizer = PatternRecognizer(supported_entity="OAB_NUMBER", name="OabRecognizer",
                                               patterns=[Pattern(name="OabPattern", regex=r'\bOAB[/\s]*[A-Z]{2}\s*\d{1,6}(?:\/\d{1,2})?\b', score=1.0)])

            crm_recognizer = PatternRecognizer(supported_entity="CRM_NUMBER", name="CrmRecognizer",
                                               patterns=[Pattern(name="CrmPattern", regex=r'\bCRM[/\s]*[A-Z]{2}\s*\d{1,6}\b', score=1.0)])

            cress_recognizer = PatternRecognizer(supported_entity="CRESS_NUMBER", name="CressRecognizer",
                                                 patterns=[Pattern(name="CressPattern", regex=r'\bCRESS[/\s]*[A-Z]{2}\s*\d{1,6}\b', score=1.0)])
            
            # Adicionar os reconhecedores ao registro do analyzer
            self.analyzer.registry.add_recognizer(cpf_recognizer)
            self.analyzer.registry.add_recognizer(rg_recognizer)
            self.analyzer.registry.add_recognizer(oab_recognizer)
            self.analyzer.registry.add_recognizer(crm_recognizer)
            self.analyzer.registry.add_recognizer(cress_recognizer)

            # Adicionar listas de negação para evitar falsos positivos
            deny_recognizer_legal = PatternRecognizer(supported_entity="LEGAL_TERM", name="LegalTermRecognizer", deny_list=self.termos_legais)
            self.analyzer.registry.add_recognizer(deny_recognizer_legal)
            
            print("✅ Reconhecedores personalizados para CPF, RG, OAB, etc., foram adicionados.")

        except Exception as e:
            print(f"⚠️ Erro ao adicionar reconhecedores personalizados: {e}")

    def obter_operadores_anonimizacao(self):
        """Define como cada tipo de entidade (PII) deve ser tratado durante a anonimização."""
        return {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<DADO_SENSIVEL>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<NOME>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<ENDERECO>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "CPF": OperatorConfig("replace", {"new_value": "<CPF>"}),
            "RG_NUMBER": OperatorConfig("replace", {"new_value": "<RG>"}),
            "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
            "CRM_NUMBER": OperatorConfig("replace", {"new_value": "<CRM>"}),
            "CRESS_NUMBER": OperatorConfig("replace", {"new_value": "<CRESS>"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),
            "LEGAL_TERM": OperatorConfig("keep"), # Manter termos legais
            "DATE_TIME": OperatorConfig("keep"),  # Manter datas
        }
    
    def extrair_texto_pdf(self, caminho_arquivo: str) -> str:
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
        try:
            documento = docx.Document(caminho_arquivo)
            texto_completo = [paragrafo.text for paragrafo in documento.paragraphs]
            return "\n".join(texto_completo)
        except Exception as e:
            print(f"❌ Erro ao extrair texto do DOCX: {str(e)}")
            return ""
    
    def detectar_entidades(self, texto: str) -> list:
        try:
            return self.analyzer.analyze(text=texto, language='pt')
        except Exception as e:
            raise Exception(f"Erro ao detectar entidades: {str(e)}")
            
    def anonimizar_texto(self, texto: str, entidades_detectadas: list = None) -> str:
        try:
            if entidades_detectadas is None:
                entidades_detectadas = self.detectar_entidades(texto)
            
            resultado = self.anonymizer.anonymize(
                text=texto,
                analyzer_results=entidades_detectadas,
                operators=self.obter_operadores_anonimizacao()
            )
            return resultado.text
        except Exception as e:
            raise Exception(f"Erro ao anonimizar texto: {str(e)}")
            
    def processar_documento(self, caminho_arquivo: str, modelo: str = "", chave_api: str = "") -> str:
        try:
            if not os.path.exists(caminho_arquivo):
                return "❌ Arquivo não encontrado."
            
            texto = ""
            if caminho_arquivo.lower().endswith('.pdf'):
                texto = self.extrair_texto_pdf(caminho_arquivo)
            elif caminho_arquivo.lower().endswith('.txt'):
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    texto = f.read()
            elif caminho_arquivo.lower().endswith('.docx'):
                texto = self.extrair_texto_docx(caminho_arquivo)
            else:
                return "❌ Formato de arquivo não suportado. Use .pdf, .txt ou .docx."

            if not texto.strip():
                return "❌ Não foi possível extrair texto do arquivo ou o arquivo está vazio."

            entidades = self.detectar_entidades(texto)
            if not entidades:
                return "✅ Documento processado. Nenhuma entidade sensível foi detectada para anonimização."

            texto_anonimizado = self.anonimizar_texto(texto, entidades)
            return texto_anonimizado
            
        except Exception as e:
            print(f"Erro detalhado no processamento: {repr(e)}")
            return f"❌ Erro ao processar documento: {str(e)}"