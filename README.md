# Anonimizador

**Versão 0.98 (Beta)**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

---

## Sumário

O Anonimizador é uma ferramenta avançada, desenvolvida em Python com Streamlit, projetada para auxiliar na anonimização de documentos jurídicos e textuais. A aplicação emprega uma técnica de **Anonimização em Duas Camadas**:
1.  **Camada 1:** Realiza uma anonimização precisa e controlada de Informações Pessoais Identificáveis (PII) utilizando Presidio Analyzer e spaCy, substituindo PIIs por tags.
2.  **Camada 2 (Opcional):** Utiliza um Modelo de Linguagem Grande (LLM) à escolha do usuário para processar o texto já anonimizado, gerando um resumo jurídico detalhado, fluido e com as tags substituídas por expressões genéricas.

A ferramenta oferece flexibilidade na escolha da LLM, suportando modelos de grandes provedores de API e modelos rodando localmente via Ollama.

## Funcionalidades Principais

* **Anonimização Robusta (Camada 1):**
    * Detecção e substituição de PIIs como Nomes, Endereços, CPFs, E-mails, Telefones, OABs, CEPs.
    * Mascaramento de números de telefone.
    * Preservação de datas, IDs de documentos (processos, NBs, RGs, CRMs), termos de estado civil, e organizações conhecidas através de operadores `"keep"`.
    * Uso de listas customizáveis para aprimorar a detecção:
        * `sobrenomes_comuns.txt`: Ajuda na identificação de nomes.
        * `termos_comuns.txt`: Contém termos jurídicos, institucionais, siglas de legislação, pronomes de tratamento e outras palavras comuns a serem explicitamente preservadas, reduzindo falsos positivos.
        * Listas internas para estados/capitais e termos de cabeçalho legal.
* **Sumarização Jurídica com IA (Camada 2):**
    * Permite ao usuário escolher entre diversas LLMs para reescrever o texto anonimizado.
    * **Modelos Suportados (configurados no script):**
        * Google Gemini (ex: `gemini-2.0-flash-lite`)
        * OpenAI (ex: `gpt-4.1-nano-2025-04-14`)
        * Anthropic Claude (ex: `claude-3-5-haiku-latest`)
        * Groq Llama 3 (ex: `llama-3.3-70b-versatile`)
        * Ollama Local: Gemma (`gemma3:12b`), DeepSeek (`deepseek-r1`), Nemotron (`nemotron-mini`), Qwen (`qwen3:8b`).
    * **Prompt Detalhado e Flexível:** O prompt de instrução para a LLM é carregado de um arquivo externo (`prompt_instrucao_llm_base.txt`), permitindo fácil edição e experimentação.
* **Interface Intuitiva:**
    * Desenvolvida com Streamlit, organizada em abas para processamento de PDF e texto colado.
    * Fluxo de usuário guiado por "Passos".
    * Logotipo customizado (`Logo - AnonimizaJud.png`).
    * Sidebar com informações "Sobre" e "Como usar", configurada para iniciar recolhida.
* **Funcionalidades Adicionais:**
    * Calculadora de tokens para estimar o tamanho do texto de PDFs.
    * Opção de download do texto anonimizado (Camada 1) de PDFs em formato `.docx`.
    * Botões para copiar os textos anonimizados e os resumos gerados pela IA.
    * Visualização de entidades detectadas na aba de texto colado.

## Tecnologias Utilizadas

* **Python 3.9+**
* **Streamlit:** Para a interface web.
* **Presidio (Analyzer & Anonymizer):** Núcleo da anonimização.
* **spaCy (modelo `pt_core_news_lg`):** Para PLN base da Presidio.
* **LLM APIs & SDKs:**
    * `google-generativeai` (Google Gemini)
    * `openai` (OpenAI GPT)
    * `anthropic` (Anthropic Claude)
    * `groq` (Groq Llama)
    * `requests` (para interagir com a API local do Ollama)
* **Outras Bibliotecas:**
    * `python-dotenv`: Gerenciamento de chaves API.
    * `httpx`: Cliente HTTP usado pela biblioteca OpenAI.
    * `tiktoken`: Estimativa de contagem de tokens.
    * `pandas`: Visualização de entidades.
    * `PyMuPDF (fitz)`: Extração de texto de PDF.
    * `python-docx`: Criação de arquivos `.docx`.
    * `st-copy-to-clipboard`: Funcionalidade de cópia.

## Configuração do Ambiente Local

Siga os passos abaixo para configurar e executar o projeto.

### 1. Clonar o Repositório (Opcional)
   Se o projeto estiver no GitHub:
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd <NOME_DA_PASTA_DO_PROJETO>
2. Ambiente Virtual (Recomendado)
Bash

python -m venv .venv
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Windows (CMD):
.\.venv\Scripts\activate.bat
# No macOS/Linux:
# source .venv/bin/activate
3. Instalar Dependências
Crie (ou atualize) seu arquivo requirements.txt com as seguintes bibliotecas:

Plaintext

streamlit
spacy
presidio-analyzer
presidio-anonymizer
pandas
st-copy-to-clipboard
PyMuPDF
python-docx
python-dotenv
google-generativeai
openai
anthropic
groq
requests
tiktoken
httpx
Em seguida, instale as dependências (com o ambiente virtual ativado):

Bash

pip install -r requirements.txt
4. Baixar Modelo spaCy
Bash

python -m spacy download pt_core_news_lg
5. Configurar Chaves de API e Arquivos de Lista
Arquivo .env: Na raiz do projeto, crie um arquivo .env e adicione suas chaves API:
Snippet de código

GOOGLE_API_KEY="sua_chave_google_aqui"
OPENAI_API_KEY="sua_chave_openai_aqui"
ANTHROPIC_API_KEY="sua_chave_anthropic_aqui"
GROQ_API_KEY="sua_chave_groq_aqui"
IMPORTANTE: Adicione .env ao seu arquivo .gitignore!
sobrenomes_comuns.txt: Coloque este arquivo na raiz do projeto, com um sobrenome por linha.
termos_comuns.txt: Coloque este arquivo na raiz do projeto, com um termo/sigla a ser preservado por linha.
prompt_instrucao_llm_base.txt: Coloque este arquivo na raiz do projeto, contendo o texto do prompt principal para as LLMs.
Logotipo: Coloque o arquivo Logo - AnonimizaJud.png (ou o nome definido em PATH_DA_LOGO) na raiz do projeto.
6. Configurar Ollama (para LLMs Locais)
Certifique-se de que o Ollama está instalado e em execução.
Baixe os modelos desejados. Exemplo, para os modelos configurados no script:
Bash

ollama pull gemma3:12b 
ollama pull deepseek-r1 
ollama pull nemotron-mini 
ollama pull qwen3:8b
(Use os tags exatos que seu Ollama reconhece para estes modelos).
Como Executar a Aplicação
Ative seu ambiente virtual.
Navegue até a pasta do projeto no seu terminal.
Execute o Streamlit:
Bash

streamlit run anonimizador.py
A aplicação abrirá no seu navegador (geralmente http://localhost:8501).
Como Usar a Ferramenta
A interface é dividida em abas ("Anonimizar Arquivo PDF" e "Anonimizar Texto Colado").

Camada 1 - Anonimização:

Para PDFs: Na aba correspondente, carregue seu arquivo. Uma estimativa de tokens será exibida. Clique em "🔍 Anonimizar PDF Carregado".
Para Texto Colado: Na aba correspondente, insira o texto e clique em "✨ Anonimizar Texto da Área".
O resultado será um texto com PIIs substituídas por tags (ex: <NOME>). Você pode visualizar o texto original (para PDFs), baixar o texto anonimizado (PDFs) ou copiá-lo.
Camada 2 - Geração de Resumo Jurídico com IA (Opcional):

Após a anonimização da Camada 1, uma seção "Passo 3 (Opcional): Gere um resumo jurídico com IA" aparecerá.
Escolha o modelo de IA desejado na lista suspensa.
Clique no botão "✨ Gerar Resumo com [Nome da LLM]".
Aguarde o processamento. O resultado será um resumo jurídico do texto. Este texto também pode ser copiado.
Importante:

Trata-se de ferramenta em desenvolvimento (Versão 0.98 Beta).
A funcionalidade de reescrita com IA requer a chave API correspondente ao serviço em nuvem escolhido, ou o servidor Ollama em execução com o modelo local selecionado.
Sempre confira o resultado gerado, tanto da anonimização quanto da reescrita pela IA.
Autor
Juiz Federal Rodrigo Gonçalves de Souza

Licença
(Considere adicionar uma licença, ex: MIT, Apache 2.0, se o projeto for público.)


**Principais Atualizações neste README:**

* **Versão:** Atualizada para "0.98 (Beta)" conforme seu último código.
* **LLMs Suportadas:** Lista expandida para incluir Groq e as múltiplas opções do Ollama.
* **Prompt Externo:** Menção de que o `PROMPT_INSTRUCAO_LLM_BASE` é carregado de `prompt_instrucao_llm_base.txt`.
* **Logotipo:** Nome do arquivo do logo atualizado para `Logo - AnonimizaJud.png`.
* **Tecnologias:** Adicionada a biblioteca `groq`.
* **Configuração:**
    * `requirements.txt` atualizado.
    * Instruções para adicionar `GROQ_API_KEY` ao `.env`.
    * Instruções claras para baixar os múltiplos modelos Ollama.
    * Instruções para os arquivos `.txt` de listas e prompt.
* **Sidebar:** Texto "Sobre" e "Como usar" ajustados para refletir a versão e o uso multi-LLM.

