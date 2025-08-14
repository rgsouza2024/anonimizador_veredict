# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import logging
from dataclasses import dataclass
from typing import List, Tuple, Iterable, Dict, Set

import PyPDF2 as pypdf
import docx

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.pattern import Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s %(name)s: %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class EntityPriority:
    priority: int  # maior = mais importante


ENTITY_PRIORITY: Dict[str, EntityPriority] = {
    # Identificadores
    "CPF": EntityPriority(100),
    "RG_NUMBER": EntityPriority(95),
    "SIAPE": EntityPriority(93),
    "EMAIL_ADDRESS": EntityPriority(90),
    "PHONE_NUMBER": EntityPriority(88),
    "PHONE_NUMBER_BR": EntityPriority(88),

    # Endereços
    "ENDERECO_POSTAL": EntityPriority(80),
    "CEP_BR": EntityPriority(78),

    # NER padrão spaCy/Presidio
    "LOCATION": EntityPriority(70),
    "PERSON": EntityPriority(65),
    "ORGANIZATION": EntityPriority(60),

    "DATE_TIME": EntityPriority(40),
    "LEGAL_TERM": EntityPriority(10),
    "COMMON_TERM": EntityPriority(10),
    "DEFAULT": EntityPriority(1),
}


class AnonimizadorCore:
    """
    Núcleo de anonimização PT-BR com Microsoft Presidio.
    Ajustes-chave: SIAPE e CEP dedicados; RG robusto; mapeamento correto de ORGANIZATION;
    tokens padronizados (<CPF>, <RG>, <SIAPE>, <CEP>, <ENDERECO>, <NOME>, <LOCAL>).
    """

    # Política: manter endereço de órgão público (quando próximo de ORGANIZATION)?
    ANONIMIZAR_ENDERECO_DE_ORGAO_PUBLICO = False
    JANELA_ORG_ENDERECO = 160  # caracteres de proximidade

    def __init__(self, spacy_model: str = "pt_core_news_lg") -> None:
        self._carregar_listas_brasileiras()
        self._termos_legais_set: Set[str] = {t.casefold() for t in self.termos_legais}
        self._termos_comuns_set: Set[str] = {t.casefold() for t in self.termos_comuns}

        try:
            logger.info("Carregando spaCy model '%s'…", spacy_model)
            nlp_engine = SpacyNlpEngine(models=[{"lang_code": "pt", "model_name": spacy_model}])
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pt"])
            logger.info("AnalyzerEngine inicializado com NLP PT.")
        except OSError:
            try:
                alt = "pt_core_news_md"
                logger.warning("Modelo '%s' não encontrado. Tentando '%s'…", spacy_model, alt)
                nlp_engine = SpacyNlpEngine(models=[{"lang_code": "pt", "model_name": alt}])
                self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pt"])
            except Exception:
                logger.exception("Falha ao carregar modelos spaCy PT. Usando AnalyzerEngine mínimo.")
                self.analyzer = AnalyzerEngine(supported_languages=["pt"])

        self._adicionar_reconhecedores_pt_br()
        self.anonymizer = AnonymizerEngine()

    # ----------------------- Listas auxiliares -----------------------
    def _carregar_lista_de_arquivo(self, nome_arquivo: str) -> List[str]:
        caminho = os.path.join(os.path.dirname(__file__), nome_arquivo)
        try:
            with open(caminho, encoding="utf-8") as f:
                return [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except FileNotFoundError:
            logger.warning("Arquivo não encontrado: %s", nome_arquivo)
            return []
        except Exception:
            logger.exception("Erro ao carregar '%s'.", nome_arquivo)
            return []

    def _carregar_listas_brasileiras(self) -> None:
        self.termos_comuns = self._carregar_lista_de_arquivo("termos_comuns.txt")
        self.termos_legais = self._carregar_lista_de_arquivo("termos_legais.txt")
        self.sobrenomes_comuns = self._carregar_lista_de_arquivo("sobrenomes_comuns.txt")

    # ----------------------- Reconhecedores --------------------------
    def _adicionar_reconhecedores_pt_br(self) -> None:
        """
        Registra reconhecedores customizados no registro do Analyzer.
        Importante: usar nomes de entidades compatíveis com o Presidio (ex.: ORGANIZATION).
        """
        try:
            registry = self.analyzer.registry

            # ENDEREÇO POSTAL (logradouro + número; aceita bairro/quadra/lote no contexto)
            address_pattern = Pattern(
                name="AddressPattern",
                regex=(
                    r"\b(?:Rua|R\.|Av\.?|Avenida|Praça|Travessa|Trv\.?|Largo|Rodovia|Estrada|Alameda|Quadra|Qd\.?|Lote|Lt\.?)"
                    r"\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9\s\.\-ºª]{2,100}"
                    r"(?:,\s*(?:n[º°o]\.?\s*)?\d{1,6}[A-Za-z]?)?"
                ),
                score=0.75,
            )
            address_recognizer = PatternRecognizer(
                supported_entity="ENDERECO_POSTAL",
                name="AddressRecognizer",
                patterns=[address_pattern],
                context=["logradouro", "endereço", "residência", "domicílio", "CEP", "bairro", "quadra", "lote", "cidade", "sede"],
            )

            # RG (várias formas; aceita curtos/longos; hífen opcional; contexto forte e SSP-UF)
            rg_ctx = Pattern(
                name="RGctx",
                regex=r"\b(?:RG|R\.G\.|Carteira\s+de\s+Identidade|Identidade)\s*(?:n[º°o]\.?\s*)?:?\s*\d{4,14}\s*-?\s*[\dX]\b",
                score=0.9,
            )
            rg_ssp = Pattern(
                name="RGssp",
                regex=r"\b\d{4,14}\s*-?\s*[\dX]\b(?=.*\bSSP-?[A-Z]{2}\b)",
                score=0.82,
            )
            rg_iso = Pattern(
                name="RGiso",
                regex=r"\b\d{6,14}\s*-?\s*[\dX]\b",
                score=0.58,
            )
            rg_recognizer = PatternRecognizer(
                supported_entity="RG_NUMBER",
                name="RgRecognizerBR",
                patterns=[rg_ctx, rg_ssp, rg_iso],
                context=["RG", "Identidade", "SSP", "documento"],
            )

            # CPF
            cpf_pat = Pattern(name="CpfPattern", regex=r"\b\d{3}\.?\d{3}\.?\d{3}\s*-?\s*\d{2}\b", score=0.9)
            cpf_recognizer = PatternRecognizer(
                supported_entity="CPF",
                name="CpfRecognizer",
                patterns=[cpf_pat],
                context=["CPF", "cadastro de pessoa física", "cadastro"],
            )

            # Telefones BR (genérico)
            phone_pat = Pattern(
                name="PhoneBRPattern",
                regex=r"\b(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9?\d{4})-?\d{4}\b",
                score=0.7,
            )
            phone_recognizer = PatternRecognizer(
                supported_entity="PHONE_NUMBER_BR",
                name="PhoneBRRecognizer",
                patterns=[phone_pat],
                context=["telefone", "celular", "whatsapp", "contato"],
            )

            # CEP (aceita espaços antes/depois do hífen, visto em “65725 -000”)
            cep_pat = Pattern(name="CepBR", regex=r"\b\d{5}\s*-\s*\d{3}\b", score=0.88)
            cep_recognizer = PatternRecognizer(
                supported_entity="CEP_BR",
                name="CepRecognizer",
                patterns=[cep_pat],
                context=["CEP", "endereço", "logradouro", "bairro", "cidade"],
            )

            # SIAPE (matrícula funcional) — pega “SIAPE nº 496760” e “matrícula nº 519473”
            siape_ctx = Pattern(
                name="SiapeCtx",
                regex=r"\b(?:matr[ií]cula\s+)?SIAPE\s*(?:n[º°o]\.?\s*)?(\d{5,7})\b",
                score=0.9,
            )
            siape_iso = Pattern(
                name="SiapeIso",
                regex=r"\bmatr[ií]cula\s*(?:funcional\s*)?(?:n[º°o]\.?\s*)?(\d{5,7})\b",
                score=0.76,
            )
            siape_recognizer = PatternRecognizer(
                supported_entity="SIAPE",
                name="SiapeRecognizer",
                patterns=[siape_ctx, siape_iso],
                context=["SIAPE", "matrícula", "servidor", "funcional"],
            )

            # Registro
            for rec in [address_recognizer, rg_recognizer, cpf_recognizer, phone_recognizer, cep_recognizer, siape_recognizer]:
                registry.add_recognizer(rec)

            # Deny lists (evitam PERSON/LOCATION em termos jurídicos/comuns)
            deny_legal = PatternRecognizer(supported_entity="LEGAL_TERM", name="LegalTermDenyList", deny_list=self.termos_legais)
            deny_comuns = PatternRecognizer(supported_entity="COMMON_TERM", name="CommonTermDenyList", deny_list=self.termos_comuns)
            registry.add_recognizer(deny_legal)
            registry.add_recognizer(deny_comuns)

            logger.info("Reconhecedores PT-BR (ENDERECO, RG, CPF, PHONE, CEP, SIAPE) registrados.")
        except Exception:
            logger.exception("Erro ao adicionar reconhecedores personalizados.")

    # ----------------------- Operadores ------------------------------
    def obter_operadores_anonimizacao(self) -> Dict[str, OperatorConfig]:
        return {
            # Padrão
            "DEFAULT": OperatorConfig("replace", {"new_value": "<DADO_SENSIVEL>"}),

            # Pessoas/locais/org
            "PERSON": OperatorConfig("replace", {"new_value": "<NOME>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<LOCAL>"}),
            "ORGANIZATION": OperatorConfig("keep"),  # manter órgãos/empresas

            # Endereço/CEP
            "ENDERECO_POSTAL": OperatorConfig("replace", {"new_value": "<ENDERECO>"}),
            "CEP_BR": OperatorConfig("replace", {"new_value": "<CEP>"}),

            # Contatos
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),
            "PHONE_NUMBER_BR": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": True}),

            # Identificadores brasileiros
            "CPF": OperatorConfig("replace", {"new_value": "<CPF>"}),
            "RG_NUMBER": OperatorConfig("replace", {"new_value": "<RG>"}),
            "SIAPE": OperatorConfig("replace", {"new_value": "<SIAPE>"}),

            # Outros
            "OAB_NUMBER": OperatorConfig("replace", {"new_value": "<OAB>"}),
            "CRM_NUMBER": OperatorConfig("replace", {"new_value": "<CRM>"}),
            "CRESS_NUMBER": OperatorConfig("replace", {"new_value": "<CRESS>"}),

            "LEGAL_TERM": OperatorConfig("keep"),
            "COMMON_TERM": OperatorConfig("keep"),
            "DATE_TIME": OperatorConfig("keep"),
        }

    # ----------------------- Extração de texto -----------------------
    def extrair_texto_pdf(self, caminho_arquivo: str) -> str:
        texto: List[str] = []
        try:
            with open(caminho_arquivo, "rb") as fh:
                reader = pypdf.PdfReader(fh)
                for i, pg in enumerate(reader.pages):
                    try:
                        t = pg.extract_text() or ""
                        if t.strip():
                            t = re.sub(r"[ \t]+\n", "\n", t)
                            texto.append(t)
                    except Exception:
                        logger.exception("Falha ao extrair texto da página %d.", i + 1)
        except Exception:
            logger.exception("Erro ao abrir/ler PDF.")
        return "\n".join(texto)

    def extrair_texto_docx(self, caminho_arquivo: str) -> str:
        try:
            d = docx.Document(caminho_arquivo)
            return "\n".join(p.text for p in d.paragraphs if p.text is not None)
        except Exception:
            logger.exception("Erro ao extrair texto do DOCX.")
            return ""

    # ----------------------- Pipeline de análise ---------------------
    @staticmethod
    def _chunk_text(texto: str, max_chars: int = 10000, overlap: int = 200) -> Iterable[Tuple[int, str]]:
        n = len(texto)
        if n <= max_chars:
            yield 0, texto
            return
        s = 0
        while s < n:
            e = min(s + max_chars, n)
            if e < n:
                brk = texto.rfind("\n\n", s, e)
                if brk > s + 1000:
                    e = brk + 2
            yield s, texto[s:e]
            if e >= n:
                break
            s = max(0, e - overlap)

    @staticmethod
    def _valida_cpf(s: str) -> bool:
        nums = re.sub(r"\D", "", s)
        if len(nums) != 11 or nums == nums[0] * 11:
            return False
        for i in range(9, 11):
            soma = sum(int(nums[j]) * ((i + 1) - j) for j in range(i))
            dv = ((soma * 10) % 11) % 10
            if dv != int(nums[i]):
                return False
        return True

    def _filtra_por_listas(self, texto: str, res: List[RecognizerResult]) -> List[RecognizerResult]:
        out: List[RecognizerResult] = []
        for r in res:
            trecho = texto[r.start:r.end].strip()
            if r.entity_type in {"PERSON", "LOCATION"}:
                if trecho.casefold() in self._termos_legais_set or trecho.casefold() in self._termos_comuns_set:
                    continue
            out.append(r)
        return out

    def _valida_e_ajusta(self, texto: str, res: List[RecognizerResult]) -> List[RecognizerResult]:
        out: List[RecognizerResult] = []
        for r in res:
            if r.entity_type == "CPF":
                trecho = texto[r.start:r.end]
                if not self._valida_cpf(trecho):
                    r.score = min(r.score, 0.4)
            out.append(r)
        return out

    def _resolver_conflitos(self, res: List[RecognizerResult]) -> List[RecognizerResult]:
        if not res:
            return res

        def key(r: RecognizerResult):
            pri = ENTITY_PRIORITY.get(r.entity_type, ENTITY_PRIORITY["DEFAULT"]).priority
            return (r.start, -pri, -r.score, -(r.end - r.start))

        res = sorted(res, key=key)
        final: List[RecognizerResult] = []
        for r in res:
            if not final:
                final.append(r)
                continue
            last = final[-1]
            if r.start < last.end:  # overlap
                pri_r = ENTITY_PRIORITY.get(r.entity_type, ENTITY_PRIORITY["DEFAULT"]).priority
                pri_l = ENTITY_PRIORITY.get(last.entity_type, ENTITY_PRIORITY["DEFAULT"]).priority
                if (pri_r, r.score, r.end - r.start) > (pri_l, last.score, last.end - last.start):
                    final[-1] = r
            else:
                final.append(r)
        return final

    def _aplicar_politicas(self, texto: str, res: List[RecognizerResult]) -> List[RecognizerResult]:
        """
        Política: se ANONIMIZAR_ENDERECO_DE_ORGAO_PUBLICO == False,
        não anonimiza ENDERECO_POSTAL quando houver ORGANIZATION próxima.
        """
        if not res or self.ANONIMIZAR_ENDERECO_DE_ORGAO_PUBLICO:
            return res

        org_spans = [(r.start, r.end) for r in res if r.entity_type == "ORGANIZATION"]
        if not org_spans:
            return res

        janela = self.JANELA_ORG_ENDERECO
        filtrados: List[RecognizerResult] = []
        for r in res:
            if r.entity_type != "ENDERECO_POSTAL":
                filtrados.append(r)
                continue
            prox = any((org_s >= r.start - janela and org_s <= r.end + janela) or
                       (org_e >= r.start - janela and org_e <= r.end + janela)
                       for (org_s, org_e) in org_spans)
            if prox:
                # endereço institucional → manter
                continue
            filtrados.append(r)
        return filtrados

    def detectar_entidades(self, texto: str) -> List[RecognizerResult]:
        todos: List[RecognizerResult] = []
        for off, chunk in self._chunk_text(texto):
            try:
                partial = self.analyzer.analyze(text=chunk, language="pt")
                for r in partial:
                    r.start += off
                    r.end += off
                todos.extend(partial)
            except Exception:
                logger.exception("Erro na análise de chunk offset=%d.", off)

        todos = self._filtra_por_listas(texto, todos)
        todos = self._valida_e_ajusta(texto, todos)
        todos = self._resolver_conflitos(todos)
        todos = self._aplicar_politicas(texto, todos)
        return todos

    def anonimizar_texto(self, texto: str, entidades_detectadas: List[RecognizerResult] | None = None) -> str:
        try:
            if entidades_detectadas is None:
                entidades_detectadas = self.detectar_entidades(texto)
            result = self.anonymizer.anonymize(
                text=texto,
                analyzer_results=entidades_detectadas,
                operators=self.obter_operadores_anonimizacao(),
            )
            return result.text
        except Exception:
            logger.exception("Erro ao anonimizar texto.")
            raise

    def processar_documento(self, caminho_arquivo: str, modelo: str = "", chave_api: str = "") -> str:
        try:
            if not os.path.exists(caminho_arquivo):
                return "❌ Arquivo não encontrado."

            if caminho_arquivo.lower().endswith(".pdf"):
                texto = self.extrair_texto_pdf(caminho_arquivo)
            elif caminho_arquivo.lower().endswith(".txt"):
                try:
                    with open(caminho_arquivo, "r", encoding="utf-8") as f:
                        texto = f.read()
                except UnicodeDecodeError:
                    with open(caminho_arquivo, "r", encoding="latin-1") as f:
                        texto = f.read()
            elif caminho_arquivo.lower().endswith(".docx"):
                texto = self.extrair_texto_docx(caminho_arquivo)
            else:
                return "❌ Formato de arquivo não suportado. Use .pdf, .txt ou .docx."

            if not texto.strip():
                return "❌ Não foi possível extrair texto do arquivo ou o arquivo está vazio."

            entidades = self.detectar_entidades(texto)
            if not entidades:
                return "✅ Documento processado. Nenhuma entidade sensível foi detectada para anonimização."

            return self.anonimizar_texto(texto, entidades)
        except Exception as e:
            logger.exception("Erro detalhado no processamento.")
            return f"❌ Erro ao processar documento: {str(e)}"
