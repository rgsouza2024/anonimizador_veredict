# 🔧 INSTALAÇÃO MANUAL - MICROSOFT PRESIDIO AVANÇADO

## 📋 Pré-requisitos

- **Python 3.8+** instalado e configurado
- **pip** atualizado
- **Conexão com internet** para baixar modelos
- **Permissões de administrador** (recomendado)

## 🚀 Passo a Passo

### **1. Verificar Python**
```bash
# Verificar versão
python --version
# ou
python3 --version

# Deve mostrar Python 3.8.0 ou superior
```

### **2. Atualizar pip**
```bash
# Windows
python -m pip install --upgrade pip

# Linux/Mac
python3 -m pip install --upgrade pip
```

### **3. Instalar Dependências Básicas**
```bash
# Windows
pip install gradio
pip install presidio-analyzer
pip install presidio-anonymizer
pip install spacy
pip install presidio-analyzer[spacy]
pip install PyPDF2
pip install requests
pip install python-dotenv

# Linux/Mac
pip3 install gradio
pip3 install presidio-analyzer
pip3 install presidio-anonymizer
pip3 install spacy
pip3 install presidio-analyzer[spacy]
pip3 install PyPDF2
pip3 install requests
pip3 install python-dotenv
```

### **4. Baixar Modelo Spacy**
```bash
# Tentar modelo grande (recomendado)
python -m spacy download pt_core_news_lg

# Se falhar, tentar modelo pequeno
python -m spacy download pt_core_news_sm

# Se ainda falhar, instalar manualmente
pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.7.0/pt_core_news_lg-3.7.0-py3-none-any.whl
```

### **5. Verificar Instalação**
```bash
# Testar importações
python -c "import presidio_analyzer; print('✅ presidio_analyzer OK')"
python -c "import presidio_anonymizer; print('✅ presidio_anonymizer OK')"
python -c "import spacy; print('✅ spacy OK')"
python -c "import gradio; print('✅ gradio OK')"
```

### **6. Testar Funcionalidade**
```bash
# Executar teste
python teste_presidio_avancado.py

# Se funcionar, executar interface
python app_gradio.py
```

## 🚨 Solução de Problemas

### **Erro: "No matching distribution found"**
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Limpar cache
pip cache purge

# Tentar com versões específicas
pip install presidio-analyzer==2.2.0
pip install presidio-anonymizer==2.2.0
```

### **Erro: "Microsoft Visual C++ 14.0 is required" (Windows)**
- Baixar e instalar **Microsoft Visual C++ Build Tools**
- Ou usar **conda** em vez de pip:
```bash
conda install -c conda-forge presidio-analyzer presidio-anonymizer
```

### **Erro: "Permission denied" (Linux/Mac)**
```bash
# Usar sudo
sudo pip3 install [pacote]

# Ou instalar para usuário
pip3 install --user [pacote]
```

### **Erro: "Model not found" (Spacy)**
```bash
# Verificar modelos instalados
python -m spacy info

# Listar modelos disponíveis
python -m spacy download --help

# Instalar modelo específico
python -m spacy download pt_core_news_sm
```

## 🔍 Verificação Final

### **Teste Rápido**
```python
# Criar arquivo test_quick.py
import sys
print(f"Python: {sys.version}")

try:
    import presidio_analyzer
    print("✅ presidio_analyzer OK")
except ImportError as e:
    print(f"❌ presidio_analyzer: {e}")

try:
    import presidio_anonymizer
    print("✅ presidio_anonymizer OK")
except ImportError as e:
    print(f"❌ presidio_anonymizer: {e}")

try:
    import spacy
    nlp = spacy.load("pt_core_news_lg")
    print("✅ spacy pt_core_news_lg OK")
except Exception as e:
    print(f"❌ spacy pt_core_news_lg: {e}")

try:
    import gradio
    print("✅ gradio OK")
except ImportError as e:
    print(f"❌ gradio: {e}")
```

### **Executar Teste**
```bash
python test_quick.py
```

## 📚 Recursos Adicionais

### **Documentação Oficial**
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [Spacy](https://spacy.io/)
- [Gradio](https://gradio.app/)

### **Comunidade**
- [GitHub Presidio](https://github.com/microsoft/presidio)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/presidio)
- [Issues Presidio](https://github.com/microsoft/presidio/issues)

## 🎯 Próximos Passos

Após instalação bem-sucedida:

1. **Testar com documentos reais**
2. **Ajustar configurações** se necessário
3. **Implementar melhorias** de performance
4. **Deploy em produção**

---

**💡 Dica:** Se ainda houver problemas, tente usar um ambiente virtual:
```bash
# Criar ambiente virtual
python -m venv presidio_env

# Ativar (Windows)
presidio_env\Scripts\activate

# Ativar (Linux/Mac)
source presidio_env/bin/activate

# Instalar dependências no ambiente limpo
pip install -r requirements_minimal.txt
```
