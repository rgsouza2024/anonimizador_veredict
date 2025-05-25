# Anonimizador Veredict

**Versão 1.1 (Beta)**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

---

## Sumário

O Anonimizador Veredict é uma ferramenta avançada e flexível, desenvolvida em Python com Streamlit, para auxiliar na anonimização de documentos jurídicos. O projeto emprega uma técnica de **Anonimização em Duas Camadas**: a primeira camada realiza uma anonimização determinística e controlada de Informações Pessoais Identificáveis (PII) usando Presidio Analyzer e spaCy; a segunda camada, opcional, utiliza um Modelo de Linguagem Grande (LLM) à escolha do usuário para reescrever o texto anonimizado, gerando um resumo jurídico detalhado, fluido e natural.

Atualmente, a ferramenta oferece suporte para interação com as seguintes LLMs na segunda camada:
* Google Gemini 1.5 Flash
* OpenAI GPT-4o Mini
* Anthropic Claude 3 Haiku
* Um modelo local via Ollama (configurado para `gemma3:4b`)

Uma funcionalidade de calculadora de tokens também foi incorporada para auxiliar na estimativa do tamanho do texto extraído de PDFs.

## A Técnica de Anonimização em Duas Camadas

A metodologia central do Anonimizador Veredict baseia-se em duas etapas distintas para garantir tanto a segurança da anonimização quanto a qualidade do texto final:

### Camada 1: Anonimização Estruturada e Controlada (Presidio + spaCy)
Nesta fase crucial, o texto original é submetido a um processo de anonimização robusto e não generativo:
* **Detecção de PII:** Utiliza o Presidio Analyzer, apoiado pelo modelo de linguagem `pt_core_news_lg` do spaCy. São empregados reconhecedores customizados (baseados em Regex e listas de termos) para identificar uma ampla gama de PIIs, incluindo CPF, OAB, CEP, Nomes (com suporte de uma lista externa customizável em `sobrenomes_comuns.txt`), entre outros.
* **Preservação Inteligente:** Termos específicos como Estados/Capitais (`SAFE_LOCATION`), expressões de cabeçalho jurídico (`LEGAL_HEADER`), estado civil (`ESTADO_CIVIL`) e nomes de organizações conhecidas (`ORGANIZACAO_CONHECIDA`) são identificados e preservados, conforme configurado.
* **Substituição por Tags:** As PIIs detectadas (que não estão nas listas de preservação) são substituídas por tags genéricas e claras (ex: `<NOME>`, `<ENDERECO>`, `<CPF>`).
* **Segurança e Determinismo:** Esta camada opera de forma totalmente determinística. A ausência de IA Generativa nesta etapa garante que a identificação e o mascaramento de dados sensíveis sejam baseados estritamente nas regras e modelos configurados, eliminando riscos de alucinações ou vazamentos de dados durante o processo de anonimização primária.

O resultado desta primeira camada é um texto integralmente anonimizado, com placeholders no lugar dos dados sensíveis, pronto para uso seguro.

### Camada 2: Sumarização Jurídica Avançada com IA Generativa (Opcional e Flexível)
Após a anonimização pela primeira camada, o usuário tem a opção de processar o texto (que agora contém as tags) com uma LLM de sua escolha:
* **Seleção de LLMs:** A interface permite ao usuário escolher entre:
    * Google Gemini 1.5 Flash (`gemini-1.5-flash-latest`)
    * OpenAI GPT-4o Mini (`gpt-4o-mini`)
    * Anthropic Claude 3 Haiku (`claude-3-haiku-20240307`)
    * LLM local via Ollama (configurado para `gemma3:4b` ou outro modelo disponível localmente)
* **Objetivo da LLM (Conforme Prompt Detalhado):** A LLM é instruída a "Elaborar um resumo detalhado e minucioso do documento jurídico fornecido, destacando todos os aspectos factuais e processuais relevantes (...) omitindo rigorosamente quaisquer informações pessoais ou sensíveis que tenham sido substituídas por tags de anonimização (...) mantendo apenas os dados juridicamente essenciais para compreensão do caso (...) estruturando o resumo em linguagem jurídica precisa e objetiva." A LLM também é instruída a não repetir as tags e a não incluir frases introdutórias ou de encerramento genéricas.
* **Output Refinado:** O resultado é um texto resumido, com linguagem jurídica, que busca fluidez e clareza, ideal para contextos onde a leitura direta das tags de anonimização seria menos prática.

Esta abordagem dual permite um controle robusto sobre a privacidade dos dados, ao mesmo tempo que oferece o poder da IA Generativa para refinar e resumir o conteúdo de forma inteligente.

## Funcionalidades Principais

* Anonimização precisa e configurável de uma vasta gama de PIIs.
* Preservação de termos importantes através de listas de permissão.
* Reconhecimento de nomes aprimorado por lista externa de sobrenomes.
* Suporte para anonimização de texto extraído de arquivos PDF.
* Opção para anonimizar texto colado diretamente na interface.
* **Calculadora de Tokens:** Exibe uma estimativa de tokens (baseada em `tiktoken`) para o texto de PDFs carregados.
* **Seleção de Múltiplas LLMs:** Permite ao usuário escolher entre Google Gemini, OpenAI GPT-4o Mini, Anthropic Claude 3 Haiku, ou um modelo Ollama local para a tarefa de sumarização/reescrita.
* Geração de resumos jurídicos fluidos e detalhados a partir do texto anonimizado.
* Interface organizada em abas, com passos claros para o usuário.
* Opções para download do texto anonimizado de PDFs em formato `.docx`.
* Botões para copiar os textos anonimizados e os textos reescritos pela IA.

## Tecnologias Utilizadas

* **Python 3.9+**
* **Streamlit:** Para a interface web interativa.
* **Presidio (Analyzer & Anonymizer):** Para a lógica de anonimização (Camada 1).
* **spaCy (modelo `pt_core_news_lg`):** Para Processamento de Linguagem Natural e NER.
* **APIs de LLM (Camada 2):**
    * `google-generativeai` (para Google Gemini)
    * `openai` (para OpenAI GPT-4o Mini)
    * `anthropic` (para Anthropic Claude 3 Haiku)
    * `requests` (para interagir com a API local do Ollama)
* **Gerenciamento de Configuração:**
    * `python-dotenv`: Para carregar chaves API de um arquivo `.env`.
* **Outras Bibliotecas:**
    * `httpx`: Cliente HTTP (usado pela biblioteca `openai`).
    * `tiktoken`: Para estimativa de contagem de tokens (principalmente para modelos OpenAI).
    * `pandas`: Para visualização de entidades detectadas.
    * `PyMuPDF (fitz)`: Para extração de texto de PDF.
    * `python-docx`: Para criação de arquivos `.docx`.
    * `st-copy-to-clipboard`: Para funcionalidade de cópia.

## Configuração do Ambiente Local

Siga os passos abaixo para configurar e executar o projeto na sua máquina.

### 1. Clonar o Repositório (se aplicável)
   ```bash
   git clone [https://github.com/rgsouza2024/anonimizador_veredict.git](https://github.com/rgsouza2024/anonimizador_veredict.git)
   cd anonimizador_veredict
2. Criar e Ativar um Ambiente Virtual (Recomendado)
Bash

python -m venv .venv
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Windows (CMD):
.\.venv\Scripts\activate.bat
# No macOS/Linux:
# source .venv/bin/activate
3. Instalar Dependências
Certifique-se de que o arquivo requirements.txt na raiz do projeto contém todas as bibliotecas listadas na seção "Tecnologias Utilizadas". Se não, crie ou atualize-o:

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
requests
tiktoken
httpx
Em seguida, instale as dependências:

Bash

pip install -r requirements.txt
4. Baixar o Modelo de Linguagem spaCy
Bash

python -m spacy download pt_core_news_lg
5. Configurar Chaves de API e Ollama
Arquivo .env: Crie um arquivo chamado .env na raiz do projeto (anonimizador_veredict/.env) e adicione suas chaves API:
Snippet de código

GOOGLE_API_KEY="sua_chave_api_do_google_aqui"
OPENAI_API_KEY="sua_chave_api_da_openai_aqui"
ANTHROPIC_API_KEY="sua_chave_api_da_anthropic_aqui"
IMPORTANTE: Adicione o arquivo .env ao seu .gitignore para não versionar suas chaves!
Ollama:
Certifique-se de que o Ollama está instalado e em execução na sua máquina (geralmente em http://localhost:11434).
Baixe o modelo Gemma desejado via terminal. Para o gemma3:4b que você mencionou (verifique o tag exato no Ollama Hub se este não for o correto):
Bash

ollama pull gemma3:4b
(Substitua gemma3:4b pelo tag exato do modelo Gemma que você instalou, por exemplo gemma2:9b ou gemma:7b se "gemma3:4b" não for um tag padrão reconhecido pelo seu Ollama).
6. Arquivo de Sobrenomes
Crie (ou certifique-se que existe) o arquivo sobrenomes_comuns.txt na raiz do projeto, com um sobrenome por linha, para aprimorar a anonimização de nomes.

Como Executar a Aplicação
Ative seu ambiente virtual.
Navegue até a pasta do projeto no seu terminal.
Execute o Streamlit:
Bash

streamlit run anonimizador_veredict.py
A aplicação abrirá automaticamente no seu navegador web padrão (geralmente http://localhost:8501).
Como Usar a Ferramenta
A interface da aplicação é dividida em abas para "Anonimizar Arquivo PDF" e "Anonimizar Texto Colado".

Camada 1 - Anonimização:

Para PDFs: Na aba correspondente, carregue seu arquivo. Uma estimativa de tokens será exibida. Clique em "🔍 Anonimizar PDF Carregado".
Para Texto Colado: Na aba correspondente, insira o texto e clique em "✨ Anonimizar Texto da Área".
O resultado será um texto com PIIs substituídas por tags (ex: <NOME>). Você pode visualizar o texto original (para PDFs), baixar o texto anonimizado (PDFs) ou copiá-lo.
Camada 2 - Geração de Resumo Jurídico com IA (Opcional):

Após a anonimização da Camada 1, uma seção "Passo 3 (Opcional): Gere um resumo jurídico com IA" aparecerá.
Escolha a LLM desejada na lista suspensa (Google Gemini, OpenAI GPT-4o Mini, Anthropic Claude Haiku, ou Ollama Local).
Clique no botão "✨ Gerar Resumo com [Nome da LLM]".
Aguarde o processamento. O resultado será um resumo jurídico do texto, reescrito para ser fluido e omitindo as informações das tags. Este texto também pode ser copiado.
Importante:

Trata-se de ferramenta em desenvolvimento (Versão 1.1 Beta).
A funcionalidade de reescrita com IA requer a chave API correspondente ao serviço em nuvem escolhido, devidamente configurada no arquivo .env. Para Ollama, o servidor local deve estar em execução com o modelo especificado.
Sempre confira o resultado gerado, tanto da anonimização quanto da reescrita pela IA. A IA, embora poderosa, pode cometer erros ou interpretar instruções de maneiras inesperadas.
Autor
Juiz Federal Rodrigo Gonçalves de Souza

Licença
(Considere adicionar uma licença open-source como MIT ou Apache 2.0 se o repositório for público e você desejar incentivar a colaboração e o reuso. Caso contrário, pode omitir ou declarar "Todos os direitos reservados".)


**Recomendações para você:**
* **Verifique os Nomes dos Modelos:** Confirme os IDs exatos dos modelos que você está usando (especialmente para "Gemma3 4B" no Ollama e se "Claude 3.5 Haiku" tem um ID diferente de `claude-3-haiku-20240307` que seja o `latest`). Ajuste as constantes `MODELO_...` no script se necessário.
* **Teste Cada LLM:** Certifique-se de que cada opção de LLM funciona conforme esperado após configurar as respectivas chaves API e o servidor Ollama.
* **Adicione e Commite:** Salve este conteúdo como `README.md` na raiz do seu projeto, e depois adicione, commite e dê push para o seu GitHub para que ele fique atualizado.

Este README agora deve cobrir de forma abrangente o estado atual e as capacidades do seu projeto "Anonimizador Veredict"!