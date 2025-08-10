"""
Arquivo de configuração para a versão Gradio do AnonimizaJud
"""

import os
from pathlib import Path

# Configurações da aplicação
APP_CONFIG = {
    "title": "🔒 AnonimizaJud - Sistema de Anonimização para Documentos Jurídicos",
    "description": "Sistema inteligente de anonimização de documentos jurídicos utilizando IA para proteger dados sensíveis.",
    "version": "1.0.0",
    "author": "Equipe AnonimizaJud",
    "port": 7860,
    "host": "0.0.0.0",
    "share": False,
    "show_error": True,
    "show_tips": True,
    "quiet": False
}

# Configurações de tema
THEME_CONFIG = {
    "primary_hue": "blue",
    "secondary_hue": "gray", 
    "neutral_hue": "slate",
    "font": "Inter"
}

# Configurações de modelos LLM
LLM_MODELS = {
    "openai": {
        "name": "OpenAI GPT",
        "description": "Modelo GPT da OpenAI",
        "requires_key": True,
        "default_model": "gpt-3.5-turbo"
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "description": "Modelo Claude da Anthropic",
        "requires_key": True,
        "default_model": "claude-3-sonnet-20240229"
    },
    "gemini": {
        "name": "Gemini (Google)",
        "description": "Modelo Gemini da Google",
        "requires_key": True,
        "default_model": "gemini-pro"
    },
    "groq": {
        "name": "Groq",
        "description": "Modelo Groq para inferência rápida",
        "requires_key": True,
        "default_model": "llama2-70b-4096"
    },
    "ollama": {
        "name": "Ollama",
        "description": "Modelo local Ollama",
        "requires_key": False,
        "default_model": "llama2"
    }
}

# Configurações de anonimização
ANONYMIZATION_LEVELS = {
    "baixo": {
        "name": "Baixo",
        "description": "Anonimização básica - protege apenas dados críticos",
        "confidence_threshold": 0.7
    },
    "medio": {
        "name": "Médio", 
        "description": "Anonimização padrão - protege dados sensíveis e pessoais",
        "confidence_threshold": 0.8
    },
    "alto": {
        "name": "Alto",
        "description": "Anonimização rigorosa - protege todos os dados identificáveis",
        "confidence_threshold": 0.9
    }
}

# Configurações de idiomas
LANGUAGES = {
    "pt": {
        "name": "Português",
        "code": "pt",
        "description": "Português brasileiro"
    },
    "en": {
        "name": "English", 
        "code": "en",
        "description": "English"
    },
    "es": {
        "name": "Español",
        "code": "es", 
        "description": "Español"
    }
}

# Configurações de entidades
ENTITY_TYPES = [
    "CPF",
    "CNPJ", 
    "OAB",
    "CEP",
    "CNH",
    "SIAPE",
    "RG",
    "TITULO_ELEITOR",
    "PIS_PASEP",
    "CARTAO_CREDITO",
    "TELEFONE",
    "EMAIL",
    "ENDERECO",
    "NOME_PESSOA",
    "NOME_ORGAO"
]

# Configurações de arquivos
FILE_CONFIG = {
    "supported_formats": [".txt"],
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "encoding": "utf-8",
    "output_prefix": "anonimizado_"
}

# Configurações de exportação
EXPORT_FORMATS = {
    "TXT": {
        "name": "Arquivo de Texto",
        "extension": ".txt",
        "description": "Arquivo de texto simples"
    },
    "JSON": {
        "name": "JSON",
        "extension": ".json", 
        "description": "Formato JSON estruturado"
    }
}

# Configurações de cache
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 100,
    "ttl": 3600,  # 1 hora
    "cleanup_interval": 300  # 5 minutos
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "anonimizajud_gradio.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Configurações de segurança
SECURITY_CONFIG = {
    "max_text_length": 100000,  # 100k caracteres
    "rate_limit": 100,  # 100 requisições por hora
    "allowed_ips": [],  # Lista vazia = todos permitidos
    "session_timeout": 3600  # 1 hora
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "max_workers": 4,
    "timeout": 300,  # 5 minutos
    "memory_limit": 1024 * 1024 * 1024,  # 1GB
    "enable_profiling": False
}

def get_config(section, key=None):
    """Obtém configuração específica"""
    if section == "app":
        config = APP_CONFIG
    elif section == "theme":
        config = THEME_CONFIG
    elif section == "llm":
        config = LLM_MODELS
    elif section == "anonymization":
        config = ANONYMIZATION_LEVELS
    elif section == "languages":
        config = LANGUAGES
    elif section == "entities":
        config = ENTITY_TYPES
    elif section == "files":
        config = FILE_CONFIG
    elif section == "export":
        config = EXPORT_FORMATS
    elif section == "cache":
        config = CACHE_CONFIG
    elif section == "logging":
        config = LOGGING_CONFIG
    elif section == "security":
        config = SECURITY_CONFIG
    elif section == "performance":
        config = PERFORMANCE_CONFIG
    else:
        raise ValueError(f"Seção de configuração '{section}' não encontrada")
    
    if key:
        return config.get(key)
    return config

def get_llm_model_info(model_name):
    """Obtém informações sobre um modelo LLM específico"""
    return LLM_MODELS.get(model_name, {})

def get_anonymization_level_info(level):
    """Obtém informações sobre um nível de anonimização"""
    return ANONYMIZATION_LEVELS.get(level, {})

def get_language_info(lang_code):
    """Obtém informações sobre um idioma"""
    return LANGUAGES.get(lang_code, {})

def get_export_format_info(format_name):
    """Obtém informações sobre um formato de exportação"""
    return EXPORT_FORMATS.get(format_name, {})

def is_development():
    """Verifica se está em modo de desenvolvimento"""
    return os.getenv("ANONIMIZAJUD_ENV", "production") == "development"

def get_data_dir():
    """Obtém o diretório de dados"""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir

def get_logs_dir():
    """Obtém o diretório de logs"""
    base_dir = Path(__file__).parent.parent
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

def get_temp_dir():
    """Obtém o diretório temporário"""
    base_dir = Path(__file__).parent.parent
    temp_dir = base_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir

# Configurações de ambiente
ENV_VARS = {
    "OPENAI_API_KEY": "Chave da API OpenAI",
    "ANTHROPIC_API_KEY": "Chave da API Anthropic (Claude)",
    "GOOGLE_API_KEY": "Chave da API Google (Gemini)",
    "GROQ_API_KEY": "Chave da API Groq",
    "OLLAMA_HOST": "Host do Ollama (padrão: localhost:11434)",
    "ANONIMIZAJUD_ENV": "Ambiente (development/production)",
    "ANONIMIZAJUD_DEBUG": "Modo debug (true/false)",
    "ANONIMIZAJUD_LOG_LEVEL": "Nível de log (DEBUG/INFO/WARNING/ERROR)"
}

def get_env_config():
    """Obtém configurações de variáveis de ambiente"""
    config = {}
    for var, description in ENV_VARS.items():
        value = os.getenv(var)
        if value:
            config[var] = value
    return config

def validate_config():
    """Valida as configurações"""
    errors = []
    
    # Verificar diretórios necessários
    try:
        get_data_dir()
        get_logs_dir()
        get_temp_dir()
    except Exception as e:
        errors.append(f"Erro ao criar diretórios: {e}")
    
    # Verificar configurações obrigatórias
    if not APP_CONFIG.get("title"):
        errors.append("Título da aplicação não configurado")
    
    if not APP_CONFIG.get("port"):
        errors.append("Porta da aplicação não configurada")
    
    return errors

if __name__ == "__main__":
    # Teste das configurações
    print("🔧 Testando configurações...")
    
    try:
        errors = validate_config()
        if errors:
            print("❌ Erros encontrados:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ Todas as configurações estão válidas")
        
        print(f"\n📱 Porta da aplicação: {get_config('app', 'port')}")
        print(f"🎨 Tema primário: {get_config('theme', 'primary_hue')}")
        print(f"🤖 Modelos LLM disponíveis: {len(LLM_MODELS)}")
        print(f"🛡️ Níveis de anonimização: {len(ANONYMIZATION_LEVELS)}")
        print(f"🌍 Idiomas suportados: {len(LANGUAGES)}")
        
    except Exception as e:
        print(f"❌ Erro ao testar configurações: {e}")
