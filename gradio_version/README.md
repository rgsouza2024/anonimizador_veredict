# ⚖️ AnonimizaJUD (Versão Gradio)

O **AnonimizaJUD** é uma poderosa ferramenta de anonimização de documentos jurídicos, projetada para auxiliar profissionais do direito a proteger informações sensíveis em textos e arquivos PDF.

A aplicação funciona em um processo de duas camadas:
1.  **Camada 1 (Anonimização com Presidio):** Utiliza o motor do Microsoft Presidio, aprimorado com regras customizadas para o contexto jurídico brasileiro, para detectar e substituir dados pessoais (Nomes, CPFs, Endereços, etc.) por tags genéricas (ex: `<NOME>`, `<CPF>`).
2.  **Camada 2 (Reescrita com IA Generativa):** Opcionalmente, o texto "taggeado" pode ser processado por um Grande Modelo de Linguagem (LLM) de sua escolha. A IA reescreve o conteúdo, transformando as tags em um texto fluido e natural, como se fosse um resumo jurídico profissional, preservando o contexto original sem expor os dados.

Esta versão utiliza a biblioteca **Gradio** para criar uma interface web interativa e fácil de usar.

## 🚀 Principais Funcionalidades

* **✒️ Anonimização via Texto Direto:** Cole qualquer texto jurídico na interface para anonimização instantânea.
* **📄 Anonimização via Arquivo PDF:** Faça o upload de documentos `.pdf` para extrair e anonimizar o conteúdo automaticamente.
* **🧠 Motor de Detecção Robusto:** Baseado no Microsoft Presidio e spaCy, com dezenas de reconhecedores customizados para dados brasileiros (CPF, OAB, CEP, CNH, SIAPE, Processo CNJ, etc.).
* **🤖 Reescrita com Múltiplos Modelos de IA:** Suporte integrado para os principais modelos de IA do mercado:
    * Google Gemini
    * OpenAI GPT
    * Anthropic Claude
    * Groq (Llama 3)
    * Modelos locais via Ollama
* **📊 Visualização de Entidades:** Veja uma tabela detalhada com todas as informações sensíveis que foram detectadas no seu texto.
* **✨ Interface Intuitiva:** Um layout limpo com abas que separa claramente as funcionalidades de texto e PDF.

## 📸 Visualização da Interface

![Screenshot da Aplicação](https://i.imgur.com/gK6pI3g.png)
*A interface principal, com as abas para anonimização de texto e PDF, e a seção de resumo com IA.*

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Interface Web:** Gradio
* **Motor de Anonimização:** Microsoft Presidio
* **Processamento de PDF:** PyMuPDF
* **NLP (Base):** spaCy (com o modelo `pt_core_news_lg`)
* **Integração com LLMs:** Google, OpenAI, Anthropic, Groq, Ollama

## ⚙️ Instalação e Configuração

Siga este guia passo a passo para executar a aplicação em seu computador local.

### 1. Pré-requisitos

Certifique-se de ter o **Python 3.9** ou superior instalado em seu sistema. Você pode verificar com o comando:
```bash
python --version
2. Crie um Ambiente Virtual
É uma boa prática isolar as dependências do projeto. Crie e ative um ambiente virtual:

Bash

# Crie a pasta do ambiente virtual (ex: .venv)
python -m venv .venv

# Ative o ambiente:
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No macOS/Linux:
source .venv/bin/activate
Seu terminal deve agora exibir (.venv) no início da linha.

3. Instale as Dependências
Crie um arquivo chamado requirements.txt na pasta do seu projeto com o seguinte conteúdo:

Plaintext

gradio
presidio-analyzer
presidio-anonymizer
spacy
pandas
PyMuPDF
python-docx
python-dotenv
google-generativeai
groq
openai
anthropic
requests
tiktoken
httpx
Agora, instale todas as bibliotecas de uma vez com o comando:

Bash

pip install -r requirements.txt
4. Baixe o Modelo de Linguagem spaCy
O Presidio depende de um modelo de linguagem do spaCy para a análise do texto em português. Baixe-o com o comando:

Bash

python -m spacy download pt_core_news_lg
5. Configure as Chaves de API (Obrigatório para a Camada 2)
Para usar a funcionalidade de resumo com IA, você precisa das chaves de API dos respectivos serviços.

Crie um arquivo chamado .env na mesma pasta do projeto.

Copie o conteúdo abaixo para o seu arquivo .env e substitua SUA_CHAVE_AQUI pelas suas chaves reais.

Snippet de código

# .env.example - Renomeie este arquivo para .env e adicione suas chaves

# Chave para os modelos do Google (Gemini)
GOOGLE_API_KEY="SUA_CHAVE_AQUI"

# Chave para os modelos da OpenAI (GPT-4o, etc.)
OPENAI_API_KEY="SUA_CHAVE_AQUI"

# Chave para os modelos da Anthropic (Claude)
ANTHROPIC_API_KEY="SUA_CHAVE_AQUI"

# Chave para a API da Groq (Llama 3)
GROQ_API_KEY="SUA_CHAVE_AQUI"
Observação: Você só precisa preencher as chaves dos serviços que pretende usar. As outras podem ser deixadas em branco.

6. Verifique os Arquivos de Apoio
Certifique-se de que os seguintes arquivos de texto (.txt) estão na mesma pasta que o anonimizador_gradio.py:

sobrenomes_comuns.txt

termos_comuns.txt

prompt_instrucao_llm_base.txt

▶️ Como Executar a Aplicação
Com o ambiente virtual ativado e todas as dependências instaladas, execute o seguinte comando no seu terminal:

Bash

python anonimizador_gradio.py
O terminal exibirá uma mensagem indicando que a aplicação está rodando, geralmente em um endereço local como http://127.0.0.1:7860. Abra este endereço no seu navegador para começar a usar o AnonimizaJUD!

📂 Estrutura do Projeto
/seu-projeto/
│
├── .venv/                   # Pasta do ambiente virtual (criada no passo 2)
│
├── anonimizador_gradio.py   # O código principal da aplicação Gradio
│
├── requirements.txt         # Lista de dependências Python
├── .env                     # Arquivo com suas chaves de API secretas
│
├── sobrenomes_comuns.txt    # Lista de sobrenomes para o motor de detecção
├── termos_comuns.txt        # Lista de termos a serem ignorados
└── prompt_instrucao_llm_base.txt # Prompt padrão para os modelos de IA
👤 Autor
Juiz Federal Rodrigo Gonçalves de Souza