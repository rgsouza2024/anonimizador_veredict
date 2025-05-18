# Anonimizador Veredict

**Versão 1.0 (Beta)**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

---

## Sumário

O Anonimizador Veredict é uma ferramenta inovadora desenvolvida para auxiliar na anonimização de documentos jurídicos, empregando uma técnica de **Anonimização em Duas Camadas**. Esta abordagem combina a robustez da anonimização tradicional, baseada em regras e modelos estatísticos, com a capacidade de Inteligência Artificial Generativa para refinar o texto final, tornando-o mais fluido e natural para leitura.

A **primeira camada** realiza uma anonimização determinística e controlada, utilizando Presidio Analyzer e spaCy para identificar e substituir informações pessoais identificáveis (PII) por tags (ex: `<NOME>`, `<ENDERECO>`). Esta etapa ocorre sem interferência de IA Generativa, garantindo um processamento seguro e focado na substituição precisa dos dados sensíveis.

A **segunda camada**, opcional, submete o texto já anonimizado (com as tags) a um Modelo de Linguagem Grande (LLM) – atualmente o Claude 3 Haiku da Anthropic. A LLM é instruída a reescrever o texto, elaborando um resumo jurídico que omite elegantemente as informações representadas pelas tags, resultando em um documento final claro, conciso e com linguagem natural, sem tentar recriar ou adivinhar os dados originais.

## A Técnica de Anonimização em Duas Camadas

O diferencial do Anonimizador Veredict reside em sua abordagem metodológica em duas etapas distintas:

### Camada 1: Anonimização Estruturada e Controlada
Nesta fase inicial, o texto original é processado por mecanismos de anonimização bem estabelecidos:
* **Detecção de PII:** Utiliza o Presidio Analyzer, apoiado pelo modelo de linguagem `pt_core_news_lg` do spaCy e reconhecedores customizados (regex e listas de termos).
* **Substituição por Tags:** As informações identificadas como PII são substituídas por tags genéricas (ex: `<NOME>`, `<CPF>`, `<ENDERECO>`).
* **Segurança e Determinismo:** Esta camada opera de forma determinística, baseada em regras e modelos não generativos. Isso assegura que o processo de identificação e mascaramento de PII seja realizado de maneira controlada, sem os riscos inerentes à geração de texto por IA nesta fase crítica de remoção de dados sensíveis.

O resultado desta camada é um texto integralmente anonimizado, onde os dados sensíveis foram substituídos por placeholders.

### Camada 2: Reescrita e Sumarização Jurídica com IA Generativa (Opcional)
Após a primeira camada, o usuário tem a opção de submeter o texto anonimizado (com tags) a um processamento adicional por uma LLM:
* **LLM Utilizada:** Claude 3 Haiku (Anthropic).
* **Objetivo:** A LLM é instruída a não apenas tornar o texto mais fluido, mas a **elaborar um resumo detalhado e minucioso do documento jurídico**, destacando aspectos processuais relevantes, fundamentação legal, e outros dados juridicamente essenciais.
* **Tratamento das Tags:** A instrução para a LLM é crucial: ela deve omitir rigorosamente as informações representadas pelas tags, reescrevendo as frases para que façam sentido sem esses dados específicos, ou indicando de forma genérica a supressão da informação por privacidade. A LLM **não** tenta adivinhar ou recriar o conteúdo original das tags.
* **Output:** Um texto resumido, em linguagem jurídica precisa e objetiva, pronto para leitura e compreensão, sem as interrupções visuais das tags de anonimização.

Esta abordagem em duas camadas permite um controle granular sobre o processo, oferecendo um output anonimizado e seguro e, subsequentemente, um texto refinado pela IA para melhor usabilidade.

## Funcionalidades Principais

* **Anonimização Precisa:** Identificação e substituição de Nomes, Endereços, CPFs, CEPs, E-mails, Telefones, Datas, Números de OAB, etc.
* **Listas de Permissão:** Preservação configurável de Estados/Capitais, termos jurídicos comuns em cabeçalhos, estados civis e organizações conhecidas.
* **Lista Customizável de Sobrenomes:** Permite carregar uma lista externa (`sobrenomes_comuns.txt`) para aprimorar o reconhecimento de nomes.
* **Suporte a PDF:** Extração de texto de arquivos PDF para anonimização.
* **Entrada de Texto Direta:** Anonimização de texto colado em área específica.
* **Sumarização Jurídica por IA:** Utilização do Claude 3 Haiku para gerar resumos fluidos e informativos a partir do texto anonimizado.
* **Opções de Saída:** Download do texto anonimizado (de PDFs) como `.docx` e cópia para área de transferência para todos os textos processados.

## Tecnologias Utilizadas

* Python 3.9+
* Streamlit
* Presidio (Analyzer & Anonymizer)
* spaCy (com modelo `pt_core_news_lg`)
* Anthropic API (para Claude 3 Haiku)
* Pandas
* PyMuPDF (fitz)
* python-docx
* st-copy-to-clipboard

## Configuração do Ambiente Local

### 1. Clonar o Repositório (se aplicável)
   ```bash
   git clone [https://github.com/rgsouza2024/anonimizador_veredict.git](https://github.com/rgsouza2024/anonimizador_veredict.git)
   cd anonimizador_veredict