import os
import PyPDF2
import io
import re
import spacy
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.pattern import Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class AnonimizadorCore:
    """Classe principal para anonimização de documentos usando Microsoft Presidio com configuração avançada para português brasileiro"""
    
    def __init__(self):
        self.modelos_disponiveis = {
            "GPT-4": "openai",
            "Claude": "anthropic", 
            "Gemini": "google",
            "Groq": "groq",
            "Ollama": "ollama"
        }
        
        # Carregar listas de termos brasileiros
        self._carregar_listas_brasileiras()
        
        # Configurar NLP Engine com spaCy português
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
        
        # Inicializar anonymizer engine
        self.anonymizer = AnonymizerEngine()
        
        # Adicionar reconhecedores personalizados para português brasileiro
        self._adicionar_reconhecedores_pt_br()
    
    def _carregar_listas_brasileiras(self):
        """Carrega as listas de termos específicos brasileiros"""
        # Estados e capitais brasileiras (não anonimizar)
        self.estados_capitais = [
            "Acre", "AC", "Alagoas", "AL", "Amapá", "AP", "Amazonas", "AM", "Bahia", "BA",
            "Ceará", "CE", "Distrito Federal", "DF", "Espírito Santo", "ES", "Goiás", "GO",
            "Maranhão", "MA", "Mato Grosso", "MT", "Mato Grosso do Sul", "MS", "Minas Gerais", "MG",
            "Pará", "PA", "Paraíba", "PB", "Paraná", "PR", "Pernambuco", "PE", "Piauí", "PI",
            "Rio de Janeiro", "RJ", "Rio Grande do Norte", "RN", "Rio Grande do Sul", "RS",
            "Rondônia", "RO", "Roraima", "RR", "Santa Catarina", "SC", "São Paulo", "SP",
            "Sergipe", "SE", "Tocantins", "TO", "Aracaju", "Belém", "Belo Horizonte", "Boa Vista",
            "Brasília", "Campo Grande", "Cuiabá", "Curitiba", "Florianópolis", "Fortaleza",
            "Goiânia", "João Pessoa", "Macapá", "Maceió", "Manaus", "Natal", "Palmas",
            "Porto Alegre", "Porto Velho", "Recife", "Rio Branco", "Salvador", "São Luís",
            "São Paulo", "Teresina", "Vitória"
        ]
        
        # Termos de cabeçalho legal (não anonimizar)
        self.termos_legal_header = [
            "EXMO. SR. DR. JUIZ FEDERAL", "EXMO SR DR JUIZ FEDERAL",
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL", "JUIZ FEDERAL",
            "EXMO. SR. DR. JUIZ DE DIREITO", "EXMO SR DR JUIZ DE DIREITO",
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO", "JUIZ DE DIREITO",
            "JUIZADO ESPECIAL FEDERAL", "VARA DA SEÇÃO JUDICIÁRIA", "SEÇÃO JUDICIÁRIA", "EXMO.",
            "EXMO", "SR.", "DR.", "Dra.", "DRA.", "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) FEDERAL",
            "EXCELENTÍSSIMO", "Senhor", "Doutor", "Senhora", "Doutora", "EXCELENTÍSSIMA", "EXCELENTÍSSIMO(A)",
            "Senhor(a)", "Doutor(a)", "Juiz", "Juíza", "Juiz(a)", "Juiz(íza)", "Assunto", "Assuntos"
        ]
        
        # Estado civil
        self.estado_civil = [
            "casado", "casada", "solteiro", "solteira", "viúvo", "viúva", 
            "divorciado", "divorciada", "separado", "separada", "unido", "unida",
            "companheiro", "companheira", "amasiado", "amasiada", "união estável",
            "em união estável"
        ]
        
        # Organizações conhecidas
        self.organizacoes_conhecidas = [
            "SIAPE", "FUNASA", "INSS", "IBAMA", "CNPQ", "IBGE", "FIOCRUZ",
            "SERPRO", "DATAPREV", "VALOR", "Justiça", "Justica", "Segredo", "PJe",
            "Assunto", "Tribunal Regional Federal", "Assuntos", "Vara Federal",
            "Vara", "Justiça Federal", "Federal", "Juizado", "Especial", "Federal",
            "Vara Federal de Juizado Especial Cível", "Turma", "Turma Recursal", "PJE",
            "SJGO", "SJDF", "SJMA", "SJAC", "SJAL", "SJAP", "SJAM", "SJBA", "SJCE", 
            "SJDF", "SJES", "SJGO", "SJMA", "SJMG", "SJMS", "SJMT", "SJPA", "SJPB", 
            "SJPE", "SJPI", "SJPR", "SJPE", "SJRN", "SJRO", "SJRR", "SJRS", "SJSC",
            "SJSE", "SJSP", "SJTO", "Justiça Federal da 1ª Região", "PJe - Processo Judicial Eletrônico"
        ]
        
        # Carregar sobrenomes comuns do arquivo
        self.sobrenomes_comuns = self._carregar_sobrenomes_comuns()
        
        # Termos comuns a manter
        self.termos_comuns = self._carregar_termos_comuns()
    
    def _carregar_sobrenomes_comuns(self):
        """Carrega a lista de sobrenomes comuns brasileiros"""
        caminho = os.path.join(os.path.dirname(__file__), "sobrenomes_comuns.txt")
        try:
            with open(caminho, encoding="utf-8") as f:
                return [linha.strip() for linha in f if linha.strip()]
        except Exception:
            return []

    def _carregar_termos_comuns(self):
        """Carrega a lista de termos comuns"""
        caminho = os.path.join(os.path.dirname(__file__), "termos_comuns.txt")
        try:
            with open(caminho, encoding="utf-8") as f:
                return [linha.strip() for linha in f if linha.strip()]
        except Exception:
            return []
    
    def _adicionar_reconhecedores_pt_br(self):
        """Adiciona reconhecedores personalizados avançados para português brasileiro"""
        try:
            # Reconhecedor para Locais Seguros (Estados e Capitais)
            if self.estados_capitais:
                recognizer_safe_location = PatternRecognizer(
                    supported_entity="SAFE_LOCATION", 
                    name="SafeLocationRecognizer", 
                    deny_list=self.estados_capitais, 
                    supported_language="pt", 
                    deny_list_score=0.99
                )
                self.analyzer.registry.add_recognizer(recognizer_safe_location)
            
            # Reconhecedor para Cabeçalhos Legais
            if self.termos_legal_header:
                recognizer_legal_header = PatternRecognizer(
                    supported_entity="LEGAL_HEADER", 
                    name="LegalHeaderRecognizer", 
                    deny_list=self.termos_legal_header, 
                    supported_language="pt", 
                    deny_list_score=0.99
                )
                self.analyzer.registry.add_recognizer(recognizer_legal_header)
            
            # Reconhecedor para CPF (padrão avançado)
            cpf_pattern = Pattern(name="CpfRegexPattern", regex=r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", score=0.85)
            cpf_recognizer = PatternRecognizer(
                supported_entity="CPF", 
                name="CustomCpfRecognizer", 
                patterns=[cpf_pattern], 
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(cpf_recognizer)
            
            # Reconhecedor para OAB_NUMBER (padrão avançado)
            oab_pattern = Pattern(name="OabRegexPattern", regex=r"\b(?:OAB\s+)?\d{1,6}(?:\.\d{3})?\s*\/\s*[A-Z]{2}\b", score=0.85)
            oab_recognizer = PatternRecognizer(
                supported_entity="OAB_NUMBER", 
                name="CustomOabRecognizer", 
                patterns=[oab_pattern], 
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(oab_recognizer)

            # Reconhecedor para CEP_NUMBER (padrão avançado)
            cep_pattern = Pattern(name="CepPattern", regex=r"\b(\d{5}-?\d{3}|\d{2}\.\d{3}-?\d{3})\b", score=0.80) 
            cep_recognizer = PatternRecognizer(
                supported_entity="CEP_NUMBER", 
                name="CustomCepRecognizer", 
                patterns=[cep_pattern], 
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(cep_recognizer)

            # Reconhecedor para ESTADO_CIVIL
            if self.estado_civil:
                estado_civil_patterns = [Pattern(name=f"estado_civil_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in self.estado_civil]
                ec_recognizer = PatternRecognizer(
                    supported_entity="ESTADO_CIVIL", 
                    name="EstadoCivilRecognizer", 
                    patterns=estado_civil_patterns, 
                    supported_language="pt"
                )
                self.analyzer.registry.add_recognizer(ec_recognizer)

            # Reconhecedor para ORGANIZACOES_CONHECIDAS
            if self.organizacoes_conhecidas:
                org_patterns = [Pattern(name=f"org_{t.lower()}", regex=rf"(?i)\b{re.escape(t)}\b", score=0.99) for t in self.organizacoes_conhecidas]
                org_recognizer = PatternRecognizer(
                    supported_entity="ORGANIZACAO_CONHECIDA", 
                    name="OrganizacaoConhecidaRecognizer", 
                    patterns=org_patterns, 
                    supported_language="pt"
                )
                self.analyzer.registry.add_recognizer(org_recognizer)
            
            # Reconhecedor para Sobrenomes Frequentes (da lista externa)
            if self.sobrenomes_comuns:
                surnames_patterns = [Pattern(name=f"surname_{s.lower().replace(' ', '_')}", regex=rf"(?i)\b{re.escape(s)}\b", score=0.97) for s in self.sobrenomes_comuns]
                surnames_recognizer = PatternRecognizer(
                    supported_entity="PERSON", 
                    name="BrazilianCommonSurnamesRecognizer", 
                    patterns=surnames_patterns, 
                    supported_language="pt"
                )
                self.analyzer.registry.add_recognizer(surnames_recognizer)
            
            # Reconhecedor para SIAPE (Sistema Integrado de Administração de Recursos Humanos)
            siape_patterns = [
                Pattern(name="siape_formatado", regex=r"\bSIAPE\s*(?:n[ºo]\s*)?\d{5,10}\b", score=0.98),
                Pattern(name="siape_apenas_numeros", regex=r"\b\d{5,10}\b", score=0.85)
            ]
            siape_recognizer = PatternRecognizer(
                supported_entity="SIAPE",
                name="SIAPERecognizer",
                patterns=siape_patterns,
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(siape_recognizer)

            # Reconhecedor para RG
            rg_patterns = [
                Pattern(name="rg_formatado", regex=r"\bRG\s*(?:n[ºo]\s*)?\d{5,12}(-\d)?\b", score=0.98),
                Pattern(name="rg_apenas_numeros", regex=r"\b\d{5,12}(-\d)?\b", score=0.85)
            ]
            rg_recognizer = PatternRecognizer(
                supported_entity="RG",
                name="RGRecognizer",
                patterns=rg_patterns,
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(rg_recognizer)

            # Reconhecedor para CNH
            cnh_patterns = [
                Pattern(name="cnh_formatado", regex=r"\bCNH\s*(?:n[ºo]\s*)?\d{9,12}\b", score=0.98),
                Pattern(name="cnh_apenas_numeros", regex=r"\b\d{9,12}\b", score=0.85)
            ]
            cnh_recognizer = PatternRecognizer(
                supported_entity="CNH",
                name="CNHRecognizer",
                patterns=cnh_patterns,
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(cnh_recognizer)

            # Reconhecedor para CI
            ci_patterns = [
                Pattern(name="ci_formatado", regex=r"\bCI\s*(?:n[ºo]\s*)?\d{5,12}\b", score=0.98),
                Pattern(name="ci_apenas_numeros", regex=r"\b\d{5,12}\b", score=0.85)
            ]
            ci_recognizer = PatternRecognizer(
                supported_entity="CI",
                name="CIRecognizer",
                patterns=ci_patterns,
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(ci_recognizer)
            
            # Reconhecedor para IDs de Documento/Processo/Benefício (REFINADO)
            id_documento_patterns = [
                Pattern(name="numero_beneficio_nb_formatado", regex=r"\bNB\s*\d{1,3}(\.?\d{3}){2}-[\dX]\b", score=0.98),
                Pattern(name="id_numerico_longo_pje", regex=r"\b\d{10,25}\b", score=0.97), 
                Pattern(name="id_prefixo_numerico", regex=r"\bID\s*\d{8,12}\b", score=0.97),
                Pattern(name="numero_rg_completo", regex=r"\bRG\s*(?:nº|n\.)?\s*[\d.X-]+(?:-\dª\s*VIA)?\s*-\s*[A-Z]{2,3}\/[A-Z]{2}\b", score=0.98),
                Pattern(name="numero_rg_simples", regex=r"\bRG\s*(?:nº|n\.)?\s*[\d.X-]+\b", score=0.97),
                Pattern(name="numero_processo_cnj", regex=r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b", score=0.95),
                Pattern(name="numero_rnm", regex=r"\bRNM\s*(?:nº|n\.)?\s*[A-Z0-9]{7,15}\b", score=0.98),
                Pattern(name="numero_crm", regex=r"\bCRM\s*[A-Z]{2}\s*-\s*\d{1,6}\b", score=0.98)
            ]
            id_documento_recognizer = PatternRecognizer(
                supported_entity="ID_DOCUMENTO", 
                name="IdDocumentoRecognizer",
                patterns=id_documento_patterns,
                supported_language="pt"
            )
            self.analyzer.registry.add_recognizer(id_documento_recognizer)
            
            # Reconhecedor para Termos Comuns (whitelist)
            if self.termos_comuns:
                termos_comuns_recognizer = PatternRecognizer(
                    supported_entity="LEGAL_OR_COMMON_TERM",
                    name="LegalOrCommonTermRecognizer",
                    deny_list=self.termos_comuns,
                    supported_language="pt",
                    deny_list_score=0.99
                )
                self.analyzer.registry.add_recognizer(termos_comuns_recognizer)
            
            print("✅ Reconhecedores personalizados avançados para português brasileiro adicionados!")
            
        except Exception as e:
            print(f"⚠️ Erro ao adicionar reconhecedores personalizados: {e}")
    
    def extrair_texto_pdf(self, caminho_arquivo: str) -> str:
        """Extrai texto de um arquivo PDF"""
        try:
            with open(caminho_arquivo, 'rb') as arquivo:
                leitor_pdf = PyPDF2.PdfReader(arquivo)
                texto = ""
                
                for pagina in leitor_pdf.pages:
                    texto += pagina.extract_text() + "\n"
                
                return texto.strip()
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
    
    def detectar_entidades(self, texto: str) -> list:
        """Detecta entidades PII no texto usando Presidio Analyzer com configuração avançada"""
        try:
            # Usar configuração avançada com todas as entidades personalizadas
            resultados = self.analyzer.analyze(
                text=texto,
                language='pt'
            )
            
            return resultados
        except Exception as e:
            raise Exception(f"Erro ao detectar entidades: {str(e)}")
    
    def obter_operadores_anonimizacao(self):
        return {
            "DEFAULT": OperatorConfig("keep"),
            "PERSON": OperatorConfig("replace", {"new_value": "<NOME>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<ENDERECO>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),
            "CPF": OperatorConfig("replace", {"new_value": "***"}),
            "DATE_TIME": OperatorConfig("keep"), 
            "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
            "CEP_NUMBER": OperatorConfig("replace", {"new_value": "***"}),
            "ESTADO_CIVIL": OperatorConfig("keep"),
            "ORGANIZACAO_CONHECIDA": OperatorConfig("keep"),
            "ID_DOCUMENTO": OperatorConfig("keep"), 
            "LEGAL_OR_COMMON_TERM": OperatorConfig("keep"),
            "SAFE_LOCATION": OperatorConfig("keep"),
            "LEGAL_HEADER": OperatorConfig("keep"),
            "CNH": OperatorConfig("replace", {"new_value": "***"}),
            "SIAPE": OperatorConfig("replace", {"new_value": "***"}),
            "RG": OperatorConfig("replace", {"new_value": "***"}),
            "CI": OperatorConfig("replace", {"new_value": "***"})
        }
    
    def anonimizar_texto(self, texto: str, entidades_detectadas: list = None) -> str:
        """Anonimiza o texto substituindo entidades PII detectadas com operadores avançados"""
        try:
            # Se não foram fornecidas entidades, detectar automaticamente
            if entidades_detectadas is None:
                entidades_detectadas = self.detectar_entidades(texto)
            
            # Obter operadores de anonimização completos
            operadores = self.obter_operadores_anonimizacao()
            
            # Aplicar anonimização
            resultado = self.anonymizer.anonymize(
                text=texto,
                analyzer_results=entidades_detectadas,
                operators=operadores
            )
            
            return resultado.text
        except Exception as e:
            raise Exception(f"Erro ao anonimizar texto: {str(e)}")
    
    def processar_documento(self, caminho_arquivo: str, modelo: str, chave_api: str = "") -> str:
        """Processa um documento para anonimização usando Presidio com configuração avançada"""
        try:
            # Validar arquivo
            if not self.validar_arquivo(caminho_arquivo):
                return "❌ Tipo de arquivo não suportado. Use PDF, TXT ou DOCX."
            
            # Extrair texto do PDF
            texto_original = self.extrair_texto_pdf(caminho_arquivo)
            
            if not texto_original.strip():
                return "❌ Não foi possível extrair texto do documento."
            
            # Detectar entidades PII com configuração avançada
            entidades_detectadas = self.detectar_entidades(texto_original)
            
            # Anonimizar texto com operadores avançados
            texto_anonimizado = self.anonimizar_texto(texto_original, entidades_detectadas)
            
            # Contar entidades detectadas por tipo
            contagem_por_tipo = {}
            for entidade in entidades_detectadas:
                tipo = entidade.entity_type
                contagem_por_tipo[tipo] = contagem_por_tipo.get(tipo, 0) + 1
            
            # Preparar resultado detalhado
            resultado = f"""
✅ Documento processado com sucesso usando Microsoft Presidio Avançado!

📄 Arquivo: {os.path.basename(caminho_arquivo)}
🤖 Modelo: {modelo}
🔑 API: {'Configurada' if chave_api else 'Não configurada'}

📋 Status: Anonimização concluída
🎯 Total de entidades detectadas: {len(entidades_detectadas)}

📊 Detalhamento por tipo:
"""
            
            for tipo, contagem in contagem_por_tipo.items():
                resultado += f"   • {tipo}: {contagem}\n"
            
            resultado += f"""
🔄 Substituições realizadas: {len(entidades_detectadas)}

📝 TEXTO ORIGINAL:
{texto_original}

🔒 TEXTO ANONIMIZADO:
{texto_anonimizado}

💡 Documento anonimizado usando Microsoft Presidio com configuração avançada para português brasileiro.
   Todas as informações pessoais foram substituídas por marcadores seguros.
   
🔧 Funcionalidades ativas:
   • Reconhecedores regex avançados para documentos brasileiros
   • Listas de termos específicos (estados, cabeçalhos legais, sobrenomes)
   • Operadores de anonimização inteligentes
   • Suporte completo ao idioma português
            """
            
            return resultado
            
        except Exception as e:
            return f"❌ Erro ao processar documento: {str(e)}"
    
    def validar_arquivo(self, caminho: str) -> bool:
        """Valida se o arquivo é suportado"""
        extensoes_validas = ['.pdf', '.txt', '.docx']
        return any(caminho.lower().endswith(ext) for ext in extensoes_validas)

# 🔒 AnonimizaJud - Gradio

Sistema inteligente de anonimização de documentos jurídicos brasileiros utilizando IA (Microsoft Presidio) para proteger dados sensíveis.

## Principais Funcionalidades

- **Anonimização automática** de nomes, endereços, CPFs, CEPs, SIAPE, RG, CNH, CI, e e-mails.
- **Substituição padronizada:**  
  - CPFs, CEPs, SIAPE, RG, CNH e CI são sempre substituídos por `***`.
  - Nomes por `<NOME>`, endereços por `<ENDERECO>`, e-mails por `<EMAIL>`.