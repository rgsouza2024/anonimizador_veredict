# 🚀 AnonimizaJud - Versão Microsoft Presidio

## 🔒 **Anonimização Automática com IA**

Esta versão do AnonimizaJud utiliza o **Microsoft Presidio** para detectar e anonimizar automaticamente informações pessoais (PII) em documentos PDF, TXT e DOCX.

## ✨ **Funcionalidades**

- **🔍 Detecção automática** de informações pessoais
- **🔄 Anonimização inteligente** com marcadores seguros
- **🌍 Suporte ao português** brasileiro
- **📄 Processamento de PDFs** com extração de texto
- **⚡ Interface Gradio** moderna e responsiva

## 🎯 **Entidades Detectadas**

O Presidio identifica automaticamente:
- 👤 **Nomes de pessoas** → `[NOME]`
- 📞 **Números de telefone** → `[TELEFONE]`
- 📧 **Endereços de email** → `[EMAIL]`
- 💳 **Números de cartão** → `[CARTAO_CREDITO]`
- 🏦 **Códigos IBAN** → `[IBAN]`
- 🌐 **Endereços IP** → `[IP]`
- 📍 **Localizações** → `[LOCALIZACAO]`
- 📅 **Datas e horários** → `[DATA_HORA]`
- 🆔 **Registros nacionais** → `[REGISTRO_NACIONAL]`
- 🏥 **Licenças médicas** → `[LICENCA_MEDICA]`

## 🚀 **Instalação**

### **Windows:**
```bash
install_presidio.bat
```

### **Linux/Mac:**
```bash
chmod +x install_presidio.sh
./install_presidio.sh
```

### **Manual:**
```bash
pip install -r requirements_gradio.txt
python -m spacy download pt_core_news_sm
```

## 🎮 **Como Usar**

1. **📤 Upload**: Faça upload do documento (PDF, TXT, DOCX)
2. **🤖 Modelo**: Selecione o modelo LLM (opcional)
3. **🔑 API**: Digite sua chave API (opcional)
4. **🚀 Processar**: Clique em "Anonimizar Documento"
5. **📋 Resultado**: Visualize o texto anonimizado ao lado

## 🔧 **Arquivos Principais**

- `anonimizador_core.py` - Lógica de anonimização com Presidio
- `app_gradio.py` - Interface Gradio
- `requirements_gradio.txt` - Dependências Python
- `install_presidio.bat` - Script de instalação Windows
- `install_presidio.sh` - Script de instalação Linux/Mac

## 🌟 **Vantagens do Presidio**

- **🔒 Privacidade**: Anonimização local, sem envio para APIs externas
- **⚡ Velocidade**: Processamento rápido e eficiente
- **🎯 Precisão**: Detecção avançada de PII em português
- **🔄 Flexibilidade**: Fácil customização de regras
- **📚 Open Source**: Desenvolvido pela Microsoft

## 🚨 **Limitações**

- **📄 PDFs**: Funciona melhor com PDFs baseados em texto
- **🖼️ Imagens**: Não processa PDFs escaneados como imagem
- **🌍 Idiomas**: Otimizado para português e inglês

## 🆘 **Solução de Problemas**

### **Erro de instalação:**
```bash
pip install --upgrade pip
pip install -r requirements_gradio.txt
```

### **Modelo spaCy não encontrado:**
```bash
python -m spacy download pt_core_news_sm
```

### **Erro de memória:**
- Reduza o tamanho do arquivo PDF
- Feche outras aplicações

## 📞 **Suporte**

Para dúvidas ou problemas:
1. Verifique se todas as dependências foram instaladas
2. Confirme que o arquivo é um PDF válido
3. Teste com arquivos menores primeiro

---

**🔒 AnonimizaJud - Sua privacidade, nossa prioridade!**
