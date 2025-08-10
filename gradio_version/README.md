# 🚀 AnonimizaJud - Versão Gradio

**Uma ferramenta inteligente para anonimização de documentos jurídicos e textuais com Microsoft Presidio e Gradio.**

Este projeto oferece uma solução robusta e de fácil utilização para detectar e anonimizar automaticamente Informações de Identificação Pessoal (PII) em documentos, com um foco especial no contexto linguístico e jurídico do Brasil.

## 🎯 Visão Geral

O **AnonimizaJud** utiliza o poder do **Microsoft Presidio**, uma biblioteca de IA de código aberto, para analisar textos e identificar dezenas de tipos de dados sensíveis. A aplicação é encapsulada numa interface web simples e interativa criada com **Gradio**, permitindo que utilizadores, mesmo sem conhecimentos técnicos, possam carregar os seus documentos (`.pdf`, `.docx`, `.txt`) e receber uma versão segura e anonimizada em segundos.

O sistema foi meticulosamente configurado com regras, padrões e listas de exceções específicas para o português brasileiro, garantindo alta precisão na remoção de dados sensíveis enquanto preserva a integridade e o contexto de documentos legais.

## ✨ Principais Funcionalidades

  - **Suporte a Múltiplos Formatos**: Processa ficheiros `.pdf`, `.docx` e `.txt` de forma transparente para o utilizador.
  - **Anonimização de Alta Precisão**: Utiliza o motor de NLP (Processamento de Linguagem Natural) da biblioteca `spaCy` (`pt_core_news_lg`) para uma análise contextual profunda do texto em português.
  - **Reconhecimento do Contexto Brasileiro**: Inclui reconhecedores personalizados (via Regex) para identificar dados específicos do Brasil, como:
      - CPF (Cadastro de Pessoa Física)
      - OAB (Inscrição na Ordem dos Advogados do Brasil)
      - CEP (Código de Endereçamento Postal)
      - E outros documentos como CNH e SIAPE.
  - **Preservação Inteligente de Termos**: Utiliza listas de exceções (`deny lists`) para evitar a anonimização incorreta de termos jurídicos, nomes de instituições e palavras comuns, garantindo que o documento permaneça legível e com o seu significado original.
  - **Interface Web Amigável**: Interface limpa e intuitiva construída com Gradio, que simplifica o processo de upload e visualização.
  - **Instalação Automatizada**: Scripts de instalação para Windows (`.bat`) e Linux/macOS (`.sh`) que configuram todo o ambiente necessário com um único comando.

## 🛠️ Tecnologias Utilizadas

  - **Backend**: Python 3.8+
  - **Motor de Anonimização**: Microsoft Presidio (Analyzer & Anonymizer)
  - **Processamento de Linguagem Natural (NLP)**: spaCy (com o modelo `pt_core_news_lg`)
  - **Interface Web**: Gradio
  - **Extração de Texto**: PyPDF2 (para PDFs), python-docx (para DOCX)

## ⚙️ Instalação

Siga os passos abaixo para configurar e executar o projeto no seu ambiente local.

### **Pré-requisitos**

  - **Python 3.8 ou superior** instalado. Pode verificar a sua versão com o comando `python --version`.

### **Opção 1: Instalação Automática (Recomendado)**

Os scripts automatizam todo o processo, incluindo a instalação de dependências e o download do modelo de linguagem.

  - **No Windows**:
    Abra uma linha de comandos (CMD ou PowerShell) e execute:

    ```bash
    install_presidio_avancado.bat
    ```

  - **No Linux ou macOS**:
    Abra um terminal, dê permissão de execução ao script e corra-o:

    ```bash
    chmod +x install_presidio_avancado.sh
    ./install_presidio_avancado.sh
    ```

### **Opção 2: Instalação Manual**

Para utilizadores avançados que preferem controlar o processo.

1.  **Crie e Ative um Ambiente Virtual (Altamente Recomendado)**:

    ```bash
    # Criar o ambiente
    python -m venv venv

    # Ativar no Windows
    .\venv\Scripts\activate

    # Ativar no Linux/macOS
    source venv/bin/activate
    ```

2.  **Instale as Dependências Python**:

    ```bash
    pip install -r requirements_gradio.txt
    ```

3.  **Faça o Download do Modelo de Linguagem spaCy**:

    ```bash
    python -m spacy download pt_core_news_lg
    ```

## 🎮 Como Usar a Aplicação

1.  Certifique-se de que todas as dependências estão instaladas e que o seu ambiente virtual (se usou um) está ativo.
2.  Execute o seguinte comando no seu terminal:
    ```bash
    python app_gradio.py
    ```
3.  O terminal irá mostrar um endereço local, como `Running on local URL: http://127.0.0.1:7860`. Abra este link no seu navegador.
4.  Na interface web:
      - Arraste e solte (ou clique para selecionar) o ficheiro `.pdf`, `.docx` ou `.txt` que deseja anonimizar.
      - Clique no botão **"🚀 Anonimizar Documento"**.
      - O texto anonimizado aparecerá na caixa de resultados à direita.

## 📁 Estrutura do Projeto

```
gradio_version/
│
├── 📜 anonimizador_core.py      # O "cérebro": toda a lógica de anonimização com Presidio.
├── 🖥️ app_gradio.py             # A interface web criada com Gradio.
│
├── 🔧 install_presidio_avancado.bat # Script de instalação para Windows.
├── 🔧 install_presidio_avancado.sh  # Script de instalação para Linux/macOS.
│
├── 🧪 teste_presidio_avancado.py  # Script de teste completo da funcionalidade.
├── 🧪 teste_simples.py          # Teste básico para verificar o método principal.
├── 🧪 test_quick.py             # Teste rápido para verificar as dependências.
│
├── 📚 requirements_gradio.txt     # Lista completa de todas as dependências Python.
├── 📚 requirements_minimal.txt    # Lista mínima de dependências para funcionar.
│
├── 📄 sobrenomes_comuns.txt       # Lista de sobrenomes para melhorar a deteção de nomes.
├── 📄 termos_comuns.txt           # Lista de palavras comuns a serem ignoradas pela anonimização.
├── 📄 termos_legais.txt           # Lista de jargão jurídico a ser preservado.
│
└── 📖 README.md                   # Este ficheiro.
```

## 🧠 Como Funciona: O Pipeline de Anonimização

O processo ocorre numa sequência lógica bem definida dentro do `anonimizador_core.py`:

1.  **Extração de Texto**: A aplicação primeiro deteta o tipo de ficheiro e usa a biblioteca correspondente (`PyPDF2` ou `python-docx`) para extrair o texto puro do documento.
2.  **Análise NLP com spaCy**: O texto extraído é passado para o `AnalyzerEngine` do Presidio. Internamente, o motor usa o modelo `pt_core_news_lg` do `spaCy` para realizar uma análise linguística, identificando a estrutura gramatical, verbos, substantivos, etc..
3.  **Reconhecimento de Entidades (PII)**: O `AnalyzerEngine` aplica várias camadas de reconhecedores para encontrar dados sensíveis:
      - **Reconhecedores Padrão**: As regras internas do Presidio para entidades universais (NOMES, EMAILS, DATAS, etc.).
      - **Reconhecedores Personalizados (Regex)**: As regras específicas criadas para o Brasil (CPF, OAB, CEP, etc.) são aplicadas.
      - **Listas de Negação (`deny_lists`)**: As listas `termos_comuns.txt` e `termos_legais.txt` são usadas para criar reconhecedores que marcam essas palavras como "seguras", impedindo que sejam anonimizadas por engano.
      - **Listas de Apoio**: A lista `sobrenomes_comuns.txt` ajuda o Presidio a ter maior certeza ao classificar um termo como um nome de pessoa.
4.  **Operação de Anonimização**: Uma vez que o `AnalyzerEngine` produz uma lista de todas as entidades sensíveis encontradas, essa lista é enviada para o `AnonymizerEngine`.
5.  **Substituição Contextual**: O `AnonymizerEngine` consulta um dicionário de "operadores" (`obter_operadores_anonimizacao`) que define como cada tipo de entidade deve ser substituído. Por exemplo:
      - `PERSON` → substitui por `<NOME>`
      - `CPF` → substitui por `***`
      - `PHONE_NUMBER` → mascara os últimos 4 dígitos: `(11) 9****-****`
      - `LEGAL_TERM` → mantém o termo original (`keep`).
6.  **Resultado Final**: O texto com as substituições realizadas é então retornado e exibido na interface do Gradio.

## 🔬 Testes

Para garantir a qualidade e o correto funcionamento do código, pode executar os testes automatizados.

  - **Teste Completo**: Valida o pipeline de ponta a ponta com um texto de exemplo complexo.
    ```bash
    python teste_presidio_avancado.py
    ```
  - **Verificação de Dependências**: Verifica se todas as bibliotecas foram instaladas corretamente.
    ```bash
    python test_quick.py
    ```

## 🎨 Personalização e Extensibilidade

Pode facilmente estender as capacidades do anonimizador editando o ficheiro `anonimizador_core.py`.

### Adicionar uma Nova Regra de Reconhecimento

Por exemplo, para reconhecer um "Número de Protocolo" no formato `PROT-123456`:

1.  **Adicione um `PatternRecognizer` em `_adicionar_reconhecedores_pt_br`**:

    ```python
    protocolo_pattern = Pattern(name="ProtocoloRegexPattern", regex=r"\bPROT-\d{6}\b", score=0.95)
    self.analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PROTOCOLO", patterns=[protocolo_pattern]))
    ```

2.  **Defina o operador de anonimização em `obter_operadores_anonimizacao`**:

    ```python
    "PROTOCOLO": OperatorConfig("replace", {"new_value": "<PROTOCOLO>"}),
    ```

## 🚨 Solução de Problemas Comuns

  - **Erro: "ModuleNotFoundError: No module named 'presidio\_analyzer'"**

      - **Causa**: As dependências não foram instaladas ou o ambiente virtual não está ativo.
      - **Solução**: Execute o script de instalação apropriado ou `pip install -r requirements_gradio.txt` com o ambiente virtual ativado.

  - **Erro: "OSError: [E050] Can't find model 'pt\_core\_news\_lg'"**

      - **Causa**: O modelo de linguagem do spaCy não foi baixado.
      - **Solução**: Execute `python -m spacy download pt_core_news_lg` no seu terminal.

  - **Erro: "OSError: [WinError 10048]... address already in use"**

      - **Causa**: A porta 7860, usada pelo Gradio, já está a ser usada por outro programa.
      - **Solução**: O script `app_gradio.py` já tenta automaticamente usar a porta 7861 ou uma porta livre. Se o erro persistir, feche o programa que está a usar a porta ou reinicie o computador.

