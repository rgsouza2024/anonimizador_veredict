# Anonimizador Veredict

**Versão 1.1 (Beta)**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

---

## Sumário

O Anonimizador Veredict é uma ferramenta avançada para auxiliar na anonimização de documentos jurídicos. Ele emprega uma técnica inovadora de **Anonimização em Duas Camadas**, combinando a precisão da anonimização tradicional (baseada em regras e modelos estatísticos com Presidio e spaCy) com a flexibilidade de Modelos de Linguagem Grandes (LLMs) para refinar o texto resultante.

A **primeira camada** realiza uma anonimização determinística e controlada, substituindo informações pessoais identificáveis (PII) por tags (ex: `<NOME>`, `<ENDERECO>`). Esta etapa é segura e não utiliza IA Generativa.

A **segunda camada**, opcional, processa o texto já anonimizado (com tags) utilizando uma LLM à escolha do usuário (atualmente com suporte para Anthropic Claude, OpenAI, e Google Gemini). A LLM é instruída a elaborar um resumo jurídico detalhado e minucioso do documento, omitindo as informações das tags e apresentando um texto final fluido e natural. Adicionalmente, foi incorporada uma funcionalidade de **calculadora de tokens** para estimar o tamanho do texto de entrada para as LLMs.

## A Técnica de Anonimização em Duas Camadas

O projeto adota uma abordagem metodológica em duas etapas distintas:

### Camada 1: Anonimização Estruturada e Controlada (Presidio + spaCy)
* **Detecção de PII:** Utiliza o Presidio Analyzer, o modelo `pt_core_news_lg` do spaCy e reconhecedores customizados (Regex, listas) para identificar PIIs como CPF, OAB, CEP, Nomes (aprimorado por lista externa `sobrenomes_comuns.txt`), etc.
* **Preservação de Termos:** Configurações para manter intactos Estados/Capitais, termos de cabeçalho jurídico, estados civis e organizações conhecidas.
* **Substituição por Tags:** As PIIs detectadas são substituídas por tags genéricas (ex: `<NOME>`).
* **Segurança e Determinismo:** Processamento controlado sem IA Generativa nesta fase crítica.

### Camada 2: Reescrita e Sumarização Jurídica com IA Generativa (Opcional)
O texto anonimizado com tags pode ser processado por uma LLM para:
* **LLMs Suportadas (em scripts separados):**
    * **Anthropic Claude 3 Haiku** (no script `anonimizador_veredict.py` - *confirme se este é o seu script Claude*)
    * **OpenAI GPT-4o Mini** (no script `anonimizador_veredict2.py`)
    * **Google Gemini 2.0 Flash Lite** (no script `anonimizador_veredict3.py`)
* **Objetivo:** Elaborar um resumo jurídico detalhado, omitindo as informações das tags de forma fluida, sem inventar dados e sem incluir frases introdutórias/de encerramento desnecessárias.
* **Controle:** O usuário opta por esta segunda camada após a anonimização inicial.

## Funcionalidades Principais

* Anonimização precisa de diversas PIIs.
* Listas de permissão para termos específicos.
* Lista customizável de sobrenomes (`sobrenomes_comuns.txt`).
* Suporte a upload de arquivos PDF com extração de texto.
* Entrada de texto manual.
* **Calculadora de Tokens:** Exibe uma estimativa de tokens (baseada em `tiktoken`) para o texto extraído de PDFs antes do processamento pela LLM.
* **Sumarização Jurídica por IA:** Opção de usar diferentes LLMs (Claude, OpenAI, Gemini) para gerar resumos fluidos a partir do texto anonimizado.
* Opções de saída: Download como `.docx` (para PDFs anonimizados) e cópia para área de transferência.

## Tecnologias Utilizadas

* Python 3.9+
* Streamlit
* Presidio (Analyzer & Anonymizer)
* spaCy (modelo `pt_core_news_lg`)
* **APIs de LLM:**
    * Anthropic API
    * OpenAI API
    * Google Generative AI API (Gemini)
* `python-dotenv` (para gerenciamento de chaves API)
* `httpx` (usado pelas bibliotecas de LLM)
* `tiktoken` (para estimativa de contagem de tokens)
* Pandas, PyMuPDF (fitz), python-docx, st-copy-to-clipboard

## Configuração do Ambiente Local

### 1. Clonar o Repositório (se aplicável)
   ```bash
   git clone [https://github.com/rgsouza2024/anonimizador_veredict.git](https://github.com/rgsouza2024/anonimizador_veredict.git)
   cd anonimizador_veredict



# 2. Ambiente Virtual (Recomendado)
Bash

python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows CMD: .\.venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate

# 3. Instalar Dependências
Crie (ou atualize) seu arquivo requirements.txt para incluir todas as bibliotecas:

Plaintext

streamlit
spacy
presidio-analyzer
presidio-anonymizer
pandas
st-copy-to-clipboard
PyMuPDF
python-docx
anthropic
openai
google-generativeai
python-dotenv
httpx
tiktoken
Instale com:

Bash

pip install -r requirements.txt

# 4. Baixar Modelo spaCy
Bash

python -m spacy download pt_core_news_lg

# 5. Configurar Chaves de API
Crie um arquivo chamado .env na raiz do projeto e adicione suas chaves API:

Snippet de código

ANTHROPIC_API_KEY="sua_chave_anthropic_aqui"
OPENAI_API_KEY="sua_chave_openai_aqui"
GOOGLE_API_KEY="sua_chave_google_aqui"
IMPORTANTE: Adicione .env ao seu arquivo .gitignore!

# 6. Arquivo de Sobrenomes
Certifique-se de que o arquivo sobrenomes_comuns.txt está na raiz do projeto, com um sobrenome por linha.

Como Executar a Aplicação
Ative seu ambiente virtual.
Navegue até a pasta do projeto.
Execute o script desejado:
Para a versão com Anthropic Claude:
Bash

streamlit run anonimizador_veredict.py 
Para a versão com OpenAI GPT-4o Mini:
Bash

streamlit run anonimizador_veredict2.py
Para a versão com Google Gemini 1.5 Flash:
Bash

streamlit run anonimizador_veredict3.py
A aplicação abrirá no seu navegador.
Como Usar a Ferramenta
A interface é dividida em abas ("Anonimizar Arquivo PDF" e "Anonimizar Texto Colado").

Camada 1 - Anonimização:

Realize a anonimização do seu texto (via upload de PDF ou colando o texto).
Na aba PDF, após o upload, a contagem estimada de tokens do texto original será exibida.
O resultado será um texto com PIIs substituídas por tags (ex: <NOME>).
Camada 2 - Geração de Resumo Jurídico com IA (Opcional):

Após a anonimização, clique no botão "✨ Gerar Texto Reescrito pela IA".
A LLM configurada no script em execução (Claude, OpenAI ou Gemini) processará o texto anonimizado.
O resultado será um resumo jurídico, reescrito para ser fluido e omitindo as informações das tags.
Importante:

Esta é uma ferramenta em desenvolvimento (Versão 1.1 Beta).
A funcionalidade de reescrita com IA requer a chave API correspondente (Anthropic, OpenAI ou Google) configurada corretamente.
Sempre confira o resultado gerado, tanto da anonimização quanto da reescrita pela IA, pois nenhum sistema é 100% infalível.
Autor
Juiz Federal Rodrigo Gonçalves de Souza

Licença
(Considere adicionar uma licença open-source se o repositório for público.)