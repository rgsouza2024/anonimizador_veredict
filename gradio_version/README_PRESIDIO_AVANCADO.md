# 🚀 AnonimizaJud - Microsoft Presidio Avançado

## 📋 Visão Geral

Esta versão do AnonimizaJud implementa **todas as funcionalidades avançadas** do Microsoft Presidio encontradas no código principal, incluindo:

- ✅ **Engine de análise avançado** com modelo Spacy para português brasileiro
- ✅ **Reconhecedores regex personalizados** para documentos brasileiros
- ✅ **Listas de termos específicos** (estados, cabeçalhos legais, sobrenomes)
- ✅ **Operadores de anonimização inteligentes**
- ✅ **Detecção automática** de entidades brasileiras específicas

## 🔧 Configurações Implementadas

### **1. Engine de Análise**
- **SpacyNlpEngine** com modelo `pt_core_news_lg`
- **Score threshold** configurado para 0.4
- **Suporte completo** ao idioma português

### **2. Reconhecedores Regex Personalizados**
- **CPF**: Padrão brasileiro (XXX.XXX.XXX-XX)
- **OAB**: Número de inscrição da OAB
- **CEP**: Código postal brasileiro
- **Telefone**: Formatos brasileiros
- **CNH**: Carteira Nacional de Habilitação
- **SIAPE**: Número SIAPE de servidores públicos

### **3. Listas de Termos Brasileiros**
- **Estados e capitais** (não anonimizados)
- **Cabeçalhos legais** (não anonimizados)
- **Sobrenomes comuns** brasileiros
- **Termos legais** específicos

### **4. Operadores de Anonimização**
- **Replace**: Substituição por texto personalizado
- **Mask**: Mascaramento com caracteres especiais
- **Redact**: Remoção completa
- **Hash**: Criptografia hash
- **Custom**: Operadores personalizados

## 🚀 Como Usar

### **Instalação Automática (Recomendado)**
```bash
# Windows
install_presidio_avancado.bat

# Linux/Mac
./install_presidio_avancado.sh
```

### **Instalação Manual**
```bash
# Dependências básicas
pip install gradio presidio-analyzer presidio-anonymizer spacy PyPDF2

# Extensão Spacy
pip install presidio-analyzer[spacy]

# Modelo português
python -m spacy download pt_core_news_lg
```

### **Execução**
```bash
# Interface Gradio
python app_gradio.py

# Teste de funcionalidade
python teste_presidio_avancado.py

# Teste simples
python teste_simples.py

# Verificação de dependências
python test_quick.py
```

## 🔍 Funcionalidades Detectadas

### **Entidades PII Padrão**
- **Nomes** de pessoas
- **Emails** e endereços
- **Telefones** e números
- **Endereços** físicos
- **Datas** e horários

### **Entidades Brasileiras Específicas**
- **CPF** (Cadastro de Pessoa Física)
- **OAB** (Ordem dos Advogados do Brasil)
- **CEP** (Código de Endereçamento Postal)
- **CNH** (Carteira Nacional de Habilitação)
- **SIAPE** (Sistema Integrado de Administração de Recursos Humanos)

## 📊 Comparação com Versão Anterior

| Funcionalidade | Versão Anterior | Versão Avançada |
|----------------|------------------|------------------|
| **Engine NLP** | Básico | Spacy português |
| **Reconhecedores** | Padrão | Personalizados BR |
| **Termos BR** | Não | Sim |
| **Operadores** | Básicos | Avançados |
| **Suporte PT-BR** | Limitado | Completo |

## 🧪 Testes

### **Teste Completo**
```bash
python teste_presidio_avancado.py
```

### **Teste Simples**
```bash
python teste_simples.py
```

### **Verificação de Dependências**
```bash
python test_quick.py
```

## ⚙️ Personalização

### **Adicionar Novos Reconhecedores**
```python
# Exemplo de reconhecedor personalizado
novo_reconhecedor = PatternRecognizer(
    supported_entity="NOVA_ENTIDADE",
    patterns=[Pattern(regex=r"padrão", score=0.8)]
)
anonimizador.analyzer.registry.add_recognizer(novo_reconhecedor)
```

### **Modificar Operadores**
```python
# Exemplo de operador personalizado
operador_personalizado = OperatorConfig(
    "replace", 
    {"new_value": "***ANONIMIZADO***"}
)
```

## 📈 Performance

### **Otimizações Implementadas**
- **Score threshold** configurado para 0.4
- **Modelo Spacy otimizado** para português
- **Cache de reconhecedores** personalizados
- **Processamento em lote** para documentos grandes

### **Recomendações**
- **Modelo grande** (`pt_core_news_lg`) para máxima precisão
- **Modelo pequeno** (`pt_core_news_sm`) para velocidade
- **Ambiente virtual** para isolamento de dependências

## 🚨 Solução de Problemas

### **Erro: "missing 1 required positional argument"**
- ✅ **CORRIGIDO**: O método `anonimizar_texto` agora detecta entidades automaticamente
- **Solução**: Execute `python teste_simples.py` para verificar

### **Erro: "Porta ocupada"**
- ✅ **CORRIGIDO**: Aplicação tenta portas alternativas automaticamente
- **Portas**: 7860 → 7861 → automática

### **Erro: "No matching distribution found"**
- **Solução**: Use `requirements_minimal.txt` primeiro
- **Alternativa**: Instalação manual passo a passo

### **Erro: "Model not found" (Spacy)**
- **Solução**: Execute `python -m spacy download pt_core_news_lg`
- **Alternativa**: Use modelo menor `pt_core_news_sm`

## 🔮 Melhorias Futuras

### **Próximas Versões**
- **Suporte a mais idiomas** (espanhol, francês)
- **Reconhecedores de imagem** para documentos escaneados
- **API REST** para integração com outros sistemas
- **Interface web** mais avançada
- **Relatórios de anonimização** detalhados

### **Contribuições**
- **Pull requests** são bem-vindos
- **Issues** para reportar problemas
- **Documentação** para melhorias
- **Testes** para novas funcionalidades

## 📚 Recursos Adicionais

### **Documentação**
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [Spacy](https://spacy.io/)
- [Gradio](https://gradio.app/)

### **Comunidade**
- [GitHub Presidio](https://github.com/microsoft/presidio)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/presidio)

---

**🎯 Versão atualizada com todas as correções implementadas!**

**✅ Problemas resolvidos:**
- Método `anonimizar_texto` corrigido
- Tratamento de porta ocupada
- Teste rápido robusto
- Scripts de instalação melhorados
