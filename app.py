import os
import sys
import streamlit as st

# Configurar diretórios para HF Spaces
os.environ['HOME'] = '/tmp'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '7860'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Criar diretório .streamlit no local permitido
streamlit_config_dir = '/tmp/.streamlit'
os.makedirs(streamlit_config_dir, exist_ok=True)

# Criar config.toml
config_content = """
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false
"""

with open(f'{streamlit_config_dir}/config.toml', 'w') as f:
    f.write(config_content)

# Importar e executar o app principal
from anonimizador import *