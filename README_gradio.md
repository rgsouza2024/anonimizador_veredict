# 🔒 AnonimizaJud - Versão Gradio

## 📋 Descrição
Esta é a versão Gradio do AnonimizaJud, um sistema inteligente de anonimização de documentos jurídicos que utiliza tecnologias de Inteligência Artificial para proteger dados sensíveis.

## 🚀 Como Executar

### 1. **Instalar Dependências**
```bash
pip install -r requirements_gradio.txt
```

### 2. **Executar a Aplicação**
```bash
python app_gradio.py
```

### 3. **Acessar a Interface**
A aplicação estará disponível em: `http://localhost:7860`

## 🛠️ Funcionalidades

### 📝 **Anonimização de Texto**
- Anonimização direta de texto na interface
- Múltiplos modelos de IA (OpenAI, Claude, Gemini, Groq, Ollama)
- Diferentes níveis de anonimização
- Suporte a múltiplos idiomas

### 📁 **Anonimização de Arquivo**
- Upload de arquivos de texto (.txt)
- Processamento em lote
- Download do arquivo anonimizado

### 🔍 **Análise de Entidades**
- Detecção automática de dados sensíveis
- Tabela de entidades detectadas
- Estatísticas de confiança

### ⚙️ **Configurações**
- Configuração de modelos LLM
- Gerenciamento de chaves de API
- Estatísticas do sistema
- Limpeza de cache

## 🔧 Tecnologias

- **Gradio 4.44.0**: Interface web moderna e responsiva
- **Microsoft Presidio**: Framework de anonimização
- **SpaCy**: Processamento de linguagem natural
- **Python**: Linguagem de programação

## 📁 Estrutura do Projeto

```
gradio_version/
├── app_gradio.py              # Aplicação principal Gradio
├── requirements_gradio.txt     # Dependências Python
└── README_gradio.md           # Esta documentação
```

## 🌟 Vantagens da Versão Gradio

1. **Interface Mais Moderna**: Design responsivo e intuitivo
2. **Melhor Performance**: Carregamento mais rápido
3. **Fácil Customização**: Temas e estilos personalizáveis
4. **Suporte Mobile**: Interface adaptável a dispositivos móveis
5. **Menos Código**: Implementação mais simples e direta

## 🔑 Configuração de APIs

### OpenAI
```python
# Configure sua chave de API OpenAI
chave_api = "sua_chave_openai_aqui"
```

### Claude (Anthropic)
```python
# Configure sua chave de API Claude
chave_api = "sua_chave_claude_aqui"
```

### Gemini (Google)
```python
# Configure sua chave de API Gemini
chave_api = "sua_chave_gemini_aqui"
```

### Groq
```python
# Configure sua chave de API Groq
chave_api = "sua_chave_groq_aqui"
```

### Ollama
```python
# Para Ollama local, não é necessária chave de API
# Certifique-se de que o Ollama está rodando localmente
```

## 🚨 Solução de Problemas

### Erro de Importação
Se houver erro ao importar o módulo `anonimizador`, certifique-se de que:
1. O arquivo `anonimizador.py` está na pasta pai
2. Todas as dependências estão instaladas

### Erro de Porta
Se a porta 7860 estiver ocupada, altere no código:
```python
interface.launch(server_port=7861)  # Use outra porta
```

### Erro de Dependências
Se houver problemas com dependências:
```bash
pip install --upgrade -r requirements_gradio.txt
```

## 📊 Comparação com Streamlit

| Aspecto | Streamlit | Gradio |
|---------|-----------|---------|
| **Facilidade** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Customização** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Mobile** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Código** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🤝 Contribuição

Para contribuir com melhorias:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Consulte a documentação
- Entre em contato com a equipe

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**🔒 AnonimizaJud - Versão Gradio | Desenvolvido com ❤️ para a comunidade jurídica**
