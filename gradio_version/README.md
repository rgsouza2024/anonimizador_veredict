# 🔒 AnonimizaJud - Gradio

Sistema inteligente de anonimização de documentos jurídicos brasileiros utilizando IA (Microsoft Presidio) para proteger dados sensíveis.

## Principais Funcionalidades

- **Anonimização automática** de nomes, endereços, CPFs, CEPs, SIAPE, RG, CNH, CI, e e-mails.
- **Substituição padronizada:**  
  - CPFs, CEPs, SIAPE, RG, CNH e CI são sempre substituídos por `***`.
  - Nomes por `<NOME>`, endereços por `<ENDERECO>`, e-mails por `<EMAIL>`.
- **Reconhecedores avançados** para padrões brasileiros (regex customizados).
- **Listas de termos e sobrenomes** para evitar falsos positivos e proteger apenas o que é sensível.
- **Preserva termos jurídicos e institucionais** relevantes.
- **Interface web amigável** via Gradio.

## Como usar

1. Faça upload de um arquivo PDF, TXT ou DOCX.
2. Clique em "Anonimizar Documento".
3. O texto anonimizado será exibido, com todos os dados sensíveis substituídos por marcadores seguros.

## Exemplo de anonimização

**Antes:**
```
José da Silva, matrícula SIAPE n° 1234567, CPF 123.456.789-00, CEP 01001-000, RG 1234567, CNH 123456789, CI 1234567, e-mail jose@email.com, residente na Rua das Flores, 100.
```

**Depois:**
```
<NOME>, matrícula SIAPE n° ***, CPF ***, CEP ***, RG ***, CNH ***, CI ***, e-mail <EMAIL>, residente na <ENDERECO>, 100.
```

## Requisitos

- Python 3.8+
- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- spaCy pt_core_news_lg
- Gradio

## Como rodar

```bash
pip install -r requirements.txt
python gradio_version/app_gradio.py
```

---

**Atualizado:** Agora CEP e CPF também são sempre substituídos por `***`, garantindo máxima segurança e padronização.