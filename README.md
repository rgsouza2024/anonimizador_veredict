# Anonimizador Veredict

**Versão 1.0 (Beta)**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

---

## Sumário

O Anonimizador Veredict é uma ferramenta desenvolvida para auxiliar na anonimização de documentos jurídicos, utilizando uma técnica inovadora chamada **Anonimização em Duas Camadas**. Esta abordagem combina a precisão da anonimização tradicional com a capacidade da Inteligência Artificial Generativa (OpenAI GPT-4o Mini) para refinar o texto resultante, tornando-o mais fluido e natural para leitura, ou gerando resumos jurídicos focados nos aspectos processuais.

A **primeira camada** realiza uma anonimização determinística e controlada do texto original. Ela utiliza o Presidio Analyzer e o modelo de linguagem `pt_core_news_lg` do spaCy, juntamente com reconhecedores customizados, para identificar e substituir informações pessoais identificáveis (PII) por tags genéricas (ex: `<NOME>`, `<ENDERECO>`, `<CPF>`). Esta etapa é crucial por ocorrer sem interferência de IA Generativa, garantindo um processamento seguro e focado na substituição precisa dos dados sensíveis, sem risco de introdução de alucinações ou vazamento de dados durante o mascaramento inicial.

A **segunda camada**, que é opcional, permite ao usuário submeter o texto já anonimizado (contendo as tags) a um Modelo de Linguagem Grande (LLM) – atualmente o **OpenAI GPT-4o Mini**. A LLM é instruída, através de um prompt customizado, a reescrever o texto ou elaborar um resumo jurídico detalhado. O objetivo é omitir elegantemente as informações representadas pelas tags, mantendo a clareza, a fluidez e o sentido geral do documento, sem tentar recriar ou adivinhar os dados originais.

## A Técnica de Anonimização em Duas Camadas

O diferencial do Anonimizador Veredict reside em sua abordagem metodológica em duas etapas distintas, oferecendo controle e flexibilidade ao usuário:

### Camada 1: Anonimização Estruturada e Controlada (Presidio + spaCy)
Nesta fase inicial, o texto original é processado por mecanismos de anonimização robustos e não generativos:
* **Detecção de PII:** Utiliza o Presidio Analyzer, apoiado pelo modelo de linguagem `pt_core_news_lg` do spaCy, além de reconhecedores customizados baseados em expressões regulares (Regex) e listas de termos (deny lists) para CPF, OAB, CEP, estados/capitais (para preservação como `SAFE_LOCATION`), termos de cabeçalho jurídico (para preservação como `LEGAL_HEADER`), estado civil (para preservação como `ESTADO_CIVIL`), organizações conhecidas (para preservação como `ORGANIZACAO_CONHECIDA`), e uma lista externa customizável de sobrenomes comuns (`sobrenomes_comuns.txt`) para aprimorar a detecção de `PERSON`.
* **Substituição por Tags:** As informações identificadas como PII (exceto as marcadas para preservação) são substituídas por tags genéricas e informativas (ex: `<NOME>`, `<ENDERECO>`).
* **Segurança e Determinismo:** Esta camada opera de forma determinística. A ausência de IA Generativa nesta etapa crítica de remoção de dados sensíveis visa garantir que o processo seja focado exclusivamente na identificação e mascaramento baseados nas regras e modelos configurados.

O resultado desta primeira camada é um texto integralmente anonimizado com tags, pronto para uso onde a privacidade dos dados originais é essencial.

### Camada 2: Reescrita Avançada com IA Generativa (OpenAI GPT-4o Mini - Opcional)
Após a anonimização pela primeira camada, o usuário pode optar por um processamento adicional do texto (que contém as tags) utilizando a LLM OpenAI GPT-4o Mini:
* **LLM Utilizada:** OpenAI GPT-4o Mini (acessada via API).
* **Objetivo (Conforme Prompt Atual):** Elaborar um resumo detalhado e minucioso do documento jurídico fornecido, destacando todos os aspectos factuais e processuais relevantes (partes, fatos, fundamentação, pedidos, etc.), enquanto omite rigorosamente as informações representadas pelas tags de anonimização.
* **Tratamento Inteligente das Tags:** A LLM é instruída a não replicar as tags, mas a reescrever as frases de forma natural, indicando a omissão de detalhes por privacidade ou simplesmente construindo o resumo com as informações não sensíveis disponíveis. A LLM não deve inventar dados.
* **Output:** Um texto (resumo jurídico) com maior fluidez e legibilidade, adequado para contextos onde as tags explícitas podem ser uma distração, mantendo o foco nos dados juridicamente essenciais.

Esta abordagem em duas camadas oferece um equilíbrio entre a segurança e o controle da anonimização tradicional e a capacidade de refino textual das LLMs modernas.

## Funcionalidades Principais

* **Anonimização Detalhada:** Capacidade de identificar e substituir um vasto conjunto de PIIs.
* **Preservação Configurável:** Listas de permissão para termos que não devem ser anonimizados.
* **Reconhecimento Aprimorado de Nomes:** Uso de lista externa de sobrenomes para aumentar a acurácia.
* **Suporte a Arquivos PDF:** Extração automática de texto de PDFs para anonimização.
* **Entrada de Texto Manual:** Opção para colar texto diretamente na interface.
* **Reescrita/Sumarização por IA:** Utilização do OpenAI GPT-4o Mini para processar o texto anonimizado, gerando um resumo jurídico mais natural.
* **Interface Intuitiva:** Desenvolvida com Streamlit, organizada em abas para fácil navegação.
* **Recursos Adicionais:** Visualização de texto original (PDF), tabela de entidades detectadas (texto colado), botões para copiar textos e para download do texto anonimizado de PDFs em formato `.docx`.

## Tecnologias Utilizadas

* **Python 3.9+**
* **Streamlit:** Para a interface web.
* **Presidio (Analyzer & Anonymizer):** Núcleo da anonimização.
* **spaCy (modelo `pt_core_news_lg`):** Para PLN e NER.
* **OpenAI API (modelo `gpt-4o-mini`):** Para reescrita/sumarização com IA.
* **python-dotenv:** Para gerenciamento de chaves API via arquivo `.env`.
* **httpx:** Cliente HTTP (usado internamente pela biblioteca `openai`).
* **Pandas:** Para visualização de dados.
* **PyMuPDF (fitz):** Para extração de texto de PDF.
* **python-docx:** Para gerar arquivos `.docx`.
* **st-copy-to-clipboard:** Para funcionalidade de cópia.

## Configuração do Ambiente Local

Siga os passos para configurar e executar o projeto:

### 1. Clonar o Repositório (Opcional)
   Se estiver buscando do GitHub:
   ```bash
   git clone [https://github.com/rgsouza2024/anonimizador_veredict.git](https://github.com/rgsouza2024/anonimizador_veredict.git)
   cd anonimizador_veredict

# Autor
Juiz Federal Rodrigo Gonçalves de Souza