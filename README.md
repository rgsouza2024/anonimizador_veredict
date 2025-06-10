---
title: Anonimizador Jurídico
emoji: ⚖️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.40.2
app_file: app.py
pinned: false
license: mit
---

# Anonimizador Jurídico v0.98 (Beta)

**Ferramenta avançada para anonimização de documentos jurídicos com IA**

Desenvolvido por: Juiz Federal Rodrigo Gonçalves de Souza

## 🎯 Funcionalidades

### 📋 Anonimização em Duas Camadas
1. **Camada 1:** Detecção e substituição automática de dados pessoais (PII)
2. **Camada 2:** Geração de resumo jurídico com IA (opcional)

### 🔍 Detecção de Dados Pessoais
- Nomes completos
- CPFs, RGs, OABs
- Endereços e CEPs
- Telefones e e-mails
- Preservação inteligente de termos jurídicos

### 🤖 Modelos de IA Suportados
- Google Gemini
- OpenAI GPT
- Anthropic Claude
- Groq Llama
- Modelos locais via Ollama

## 📱 Como Usar

1. **Upload de PDF** ou **Cole o texto** na área designada
2. Clique em **Anonimizar** para processar (Camada 1)
3. Opcionalmente, gere um **resumo com IA** (Camada 2)
4. Baixe ou copie o resultado

## 🔐 Privacidade

- Processamento seguro de documentos sensíveis
- Dados não são armazenados permanentemente
- Compatível com LGPD

## ⚠️ Aviso Legal

Esta é uma versão beta (0.98). Sempre revise os resultados gerados antes de usar em contextos oficiais.

## 🛠️ Tecnologias

- Python + Streamlit
- Presidio Analyzer
- spaCy (PLN em português)
- APIs de LLMs modernas

---

**Nota:** Para usar os modelos de IA, configure suas chaves de API nas variáveis de ambiente do Space.