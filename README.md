---
title: Anonimizador Jurídico
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.40.2
app_file: anonimizador.py
pinned: false
license: mit
---

# AnonimizaJUD - Proteção Inteligente de Dados

Uma aplicação moderna e profissional para anonimização de documentos jurídicos usando inteligência artificial.

## 🚀 Novidades na Versão 0.92 Beta

### ✨ Interface Modernizada
- **Design System Profissional**: Cores e tipografia consistentes com a identidade visual
- **Layout Responsivo**: Interface adaptável para diferentes tamanhos de tela
- **Componentes Visuais**: Cards, badges e ícones modernos
- **Animações Suaves**: Transições e efeitos visuais aprimorados
- **UX Melhorada**: Feedback visual e navegação intuitiva

### 🎨 Melhorias Visuais
- **Header Gradiente**: Design moderno com logo e informações da versão
- **Cards Informativos**: Apresentação clara das funcionalidades
- **Alertas Customizados**: Mensagens de status com ícones e cores
- **Tabelas Estilizadas**: Visualização melhorada dos resultados
- **Sidebar Organizada**: Informações estruturadas e acessíveis

### 🛠️ Funcionalidades Técnicas
- **CSS Customizado**: Estilos modernos com variáveis CSS
- **Componentes Reutilizáveis**: Código modular e organizado
- **Responsividade**: Interface adaptável para mobile e desktop
- **Acessibilidade**: Melhor contraste e navegação por teclado

## 📋 Funcionalidades

### 🔍 Anonimização Automática
- **Detecção Inteligente**: Identifica automaticamente informações pessoais
- **Múltiplos Formatos**: Suporte para PDF e texto colado
- **Exportação DOCX**: Gera documentos Word anonimizados
- **Tags Estruturadas**: Marcação consistente de dados sensíveis
- **Nova Detecção**: Reconhecimento de termos "matrícula" e "SIAPE"

### 🤖 IA Avançada
- **Múltiplos Modelos**: OpenAI, Claude, Gemini, Groq, Ollama
- **Resumos Jurídicos**: Geração inteligente de textos anonimizados
- **Instruções Customizáveis**: Controle sobre o processamento da IA
- **Estimativa de Tokens**: Controle de custos e limites

### 📊 Análise Detalhada
- **Entidades Detectadas**: Visualização das informações encontradas
- **Scores de Confiança**: Métricas de precisão da detecção
- **Estatísticas em Tempo Real**: Informações sobre o processamento

## 🛡️ Segurança e Privacidade

- **Processamento Local**: Opção de usar modelos Ollama localmente
- **Sem Armazenamento**: Dados não são salvos permanentemente
- **Anonimização Robusta**: Múltiplas camadas de proteção
- **Conformidade LGPD**: Adequado para uso jurídico brasileiro
- **Nova Proteção**: Anonimização de identificadores de matrícula e SIAPE

## 🚀 Como Usar

### 1. Anonimização (Camada 1)
- **PDF**: Carregue um arquivo PDF e clique em "Anonimizar PDF Carregado"
- **Texto**: Cole o texto na área e clique em "Anonimizar Texto da Área"

### 2. Resumo com IA (Camada 2 - Opcional)
- Selecione o modelo de IA desejado
- Ajuste as instruções (opcional)
- Clique em "Gerar Resumo"

### 3. Exportação
- Copie o texto anonimizado
- Baixe como arquivo DOCX
- Visualize as entidades detectadas

## 🛠️ Instalação

```bash
# Clone o repositório
git clone [url-do-repositorio]

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run anonimizador.py
```

## 📦 Dependências

- **Streamlit**: Interface web
- **Presidio**: Anonimização de dados
- **spaCy**: Processamento de linguagem natural
- **PyMuPDF**: Extração de texto de PDF
- **python-docx**: Geração de documentos Word
- **APIs de IA**: OpenAI, Anthropic, Google, Groq

## 🎯 Casos de Uso

- **Documentos Jurídicos**: Anonimização de petições e decisões
- **Relatórios**: Proteção de dados em documentos corporativos
- **Pesquisas**: Anonimização de dados para estudos
- **Compliance**: Adequação à LGPD e outras regulamentações

## 👨‍💻 Desenvolvimento

### Estrutura do Projeto
```
anonimizador_veredict/
├── anonimizador.py          # Aplicação principal
├── components.py            # Componentes de interface
├── style.css               # Estilos customizados
├── .streamlit/config.toml  # Configuração do Streamlit
├── requirements.txt        # Dependências Python
└── README.md              # Documentação
```

### Personalização
- **Cores**: Edite as variáveis CSS em `style.css`
- **Componentes**: Modifique `components.py`
- **Configuração**: Ajuste `.streamlit/config.toml`

## 📞 Suporte

**Desenvolvido por:**
- Juiz Federal Rodrigo Gonçalves de Souza

**Versão:** 0.92 Beta

## ⚠️ Importante

- Esta é uma ferramenta em desenvolvimento
- Sempre confira os resultados gerados
- A IA pode cometer erros
- Use com responsabilidade em documentos sensíveis

---

*Desenvolvido com ❤️ para a comunidade jurídica brasileira*