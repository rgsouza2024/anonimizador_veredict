# 📋 Documentação: Novos Padrões de Anonimização

## 🎯 Objetivo
Implementação de novos padrões regex para anonimização automática dos seguintes documentos brasileiros:
- **CNH** (Carteira Nacional de Habilitação)
- **SIAPE** (Sistema Integrado de Administração de Recursos Humanos)
- **CI** (Cédula de Identidade)
- **CIN** (Cédula de Identidade Nacional)
- **RG** (Registro Geral - já existia no sistema)

## 🔧 Modificações Implementadas

### 1. **Novos Reconhecedores Específicos**

#### **CNH (Carteira Nacional de Habilitação)**
```python
cnh_patterns = [
    # CNH com formatação: CNH 12345678901 ou CNH nº 12345678901
    Pattern(name="cnh_formatado", regex=r"\bCNH\s*(?:nº|n\.)?\s*\d{11}\b", score=0.98),
    # CNH sem formatação: apenas os 11 dígitos (mais específico para evitar falsos positivos)
    Pattern(name="cnh_apenas_numeros", regex=r"\b(?<![\w])\d{11}(?![\w])\b", score=0.85, context=["CNH", "Carteira", "Habilitação"])
]
```

**Formatos Detectados:**
- `CNH 12345678901`
- `CNH nº 12345678901`
- `CNH n. 12345678901`
- `12345678901` (quando no contexto de CNH)

#### **SIAPE (Sistema Integrado de Administração de Recursos Humanos)**
```python
siape_patterns = [
    # SIAPE com formatação: SIAPE 1234567 ou SIAPE nº 1234567
    Pattern(name="siape_formatado", regex=r"\bSIAPE\s*(?:nº|n\.)?\s*\d{7}\b", score=0.98),
    # SIAPE sem formatação: apenas os 7 dígitos (mais específico)
    Pattern(name="siape_apenas_numeros", regex=r"\b(?<![\w])\d{7}(?![\w])\b", score=0.85, context=["SIAPE", "Servidor", "Funcionário"])
]
```

**Formatos Detectados:**
- `SIAPE 1234567`
- `SIAPE nº 1234567`
- `SIAPE n. 1234567`
- `1234567` (quando no contexto de SIAPE)

#### **CI (Cédula de Identidade)**
```python
ci_patterns = [
    # CI com formatação: CI 12345678-9 ou CI nº 12345678-9
    Pattern(name="ci_formatado", regex=r"\bCI\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
    # CI sem formatação: formato padrão brasileiro
    Pattern(name="ci_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90, context=["CI", "Cédula", "Identidade"])
]
```

**Formatos Detectados:**
- `CI 12345678-9`
- `CI nº 12.345.678-9`
- `CI n. 98.765.432-1`
- `12345678-9`
- `12.345.678-9`

#### **CIN (Cédula de Identidade Nacional)**
```python
cin_patterns = [
    # CIN com formatação: CIN 12345678-9 ou CIN nº 12345678-9
    Pattern(name="cin_formatado", regex=r"\bCIN\s*(?:nº|n\.)?\s*[\d.]{7,11}-?\d\b", score=0.98),
    # CIN sem formatação: formato padrão brasileiro
    Pattern(name="cin_padrao", regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?\d\b", score=0.90, context=["CIN", "Cédula", "Nacional"])
]
```

**Formatos Detectados:**
- `CIN 12345678-9`
- `CIN nº 12.345.678-9`
- `CIN n. 98.765.432-1`
- `12345678-9`
- `12.345.678-9`

### 2. **Novos Operadores de Anonimização**

```python
def obter_operadores_anonimizacao():
    return {
        # ... operadores existentes ...
        "CNH": OperatorConfig("replace", {"new_value": "***"}),
        "SIAPE": OperatorConfig("replace", {"new_value": "***"}),
        "CI": OperatorConfig("replace", {"new_value": "***"}),
        "CIN": OperatorConfig("replace", {"new_value": "***"})
    }
```

### 3. **Atualização das Entidades de Análise**

As novas entidades foram adicionadas às listas de análise tanto para PDF quanto para texto:

```python
# Para PDF
entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA", "ID_DOCUMENTO", "CNH", "SIAPE", "CI", "CIN"]

# Para texto da área
entidades_para_analise = list(operadores.keys()) + ["SAFE_LOCATION", "LEGAL_HEADER", "ESTADO_CIVIL", "ORGANIZACAO_CONHECIDA", "CNH", "SIAPE", "CI", "CIN"]
```

## 🎨 Características dos Padrões

### **Scores de Confiança**
- **Score 0.98**: Padrões com prefixo claro (CNH, SIAPE, CI, CIN)
- **Score 0.85-0.90**: Padrões numéricos sem prefixo (com regex específicos)

### **Precisão dos Padrões**
- Padrões numéricos isolados com regex específicos para evitar falsos positivos
- Uso de lookahead/lookbehind para maior precisão na detecção

### **Flexibilidade de Formatação**
- Suporte a diferentes separadores (`nº`, `n.`, espaços)
- Aceita formatos com ou sem pontuação
- Case-insensitive para maior abrangência

### **Substituição por Privacidade Máxima**
- Todos os documentos detectados são substituídos por "***"
- Garante máxima proteção da privacidade
- Substituição consistente e padronizada

## 🧪 Teste dos Padrões

Execute o arquivo de teste para verificar o funcionamento:

```bash
python teste_novos_documentos.py
```

## 📊 Exemplos de Uso

### **Antes da Anonimização:**
```
O servidor João Silva, SIAPE 1234567, portador da CNH 98765432109,
apresentou sua CI nº 12.345.678-9 para identificação.
```

### **Após a Anonimização:**
```
O servidor <NOME>, SIAPE ***, portador da CNH ***,
apresentou sua CI *** para identificação.
```

## 🔒 Segurança e Privacidade

- **Score alto (0.98)** para padrões com prefixo claro
- **Context** para evitar detecção acidental de números similares
- **Substituição por "***"** para máxima privacidade
- **Integração** com o sistema existente de anonimização
- **Proteção total** de dados sensíveis

## 🚀 Benefícios da Implementação

1. **Cobertura Expandida**: Detecta mais tipos de documentos sensíveis
2. **Precisão Melhorada**: Padrões específicos para cada tipo de documento
3. **Flexibilidade**: Suporta diferentes formatos e variações
4. **Manutenibilidade**: Código organizado e bem documentado
5. **Escalabilidade**: Fácil adição de novos padrões no futuro

## 📝 Notas de Implementação

- Todos os novos padrões seguem a mesma estrutura dos existentes
- Uso de `@st.cache_resource` para otimização de performance
- Integração completa com o framework Microsoft Presidio
- Compatibilidade com as funcionalidades existentes do anonimizador
