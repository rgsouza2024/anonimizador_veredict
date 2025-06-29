"""
Componentes utilitários para melhorar a interface da aplicação Anonimizador
"""

import streamlit as st
import base64
from typing import Optional, Dict, Any
import pandas as pd

def load_css():
    """Carrega o CSS customizado"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Arquivo style.css não encontrado!")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

def create_header(logo_path: str = "Logo - AnonimizaJud.png", version: str = "0.91 Beta"):
    """Cria um header moderno e profissional"""
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    except:
        logo_base64 = ""
    
    header_html = f"""
    <div class="custom-header">
        <div style="display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                {f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; filter: brightness(0) invert(1);">' if logo_base64 else ''}
                <div>
                    <h1>AnonimizaJUD</h1>
                    <p>Proteção inteligente de dados pessoais em documentos jurídicos</p>
                </div>
            </div>
            <div style="text-align: right;">
                <span class="status-badge beta">{version}</span>
                <div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">
                    Powered by AI
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def create_info_card(title: str, content: str, icon: str = "ℹ️", color: str = "info"):
    """Cria um card informativo"""
    card_html = f"""
    <div class="custom-card">
        <h3>{icon} {title}</h3>
        <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">{content}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_stats_row(stats: Dict[str, Any]):
    """Cria uma linha de estatísticas"""
    cols = st.columns(len(stats))
    for i, (label, value) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label=label, value=value)

def create_progress_section(title: str, current_step: int, total_steps: int, description: str = ""):
    """Cria uma seção de progresso visual"""
    progress_html = f"""
    <div class="custom-card">
        <h3>📊 {title}</h3>
        <div style="margin: 1rem 0;">
            <div class="custom-progress">
                <div class="custom-progress-bar" style="width: {(current_step/total_steps)*100}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">
                <span>Passo {current_step} de {total_steps}</span>
                <span>{int((current_step/total_steps)*100)}%</span>
            </div>
        </div>
        {f'<p style="color: var(--text-secondary); margin: 0;">{description}</p>' if description else ''}
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def create_feature_card(title: str, description: str, icon: str, features: list):
    """Cria um card de funcionalidade"""
    features_html = ""
    for feature in features:
        features_html += f'<li style="margin: 0.5rem 0;">{feature}</li>'
    
    card_html = f"""
    <div class="custom-card">
        <h3>{icon} {title}</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">{description}</p>
        <ul style="color: var(--text-secondary); padding-left: 1.5rem; margin: 0;">
            {features_html}
        </ul>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def create_alert_box(message: str, alert_type: str = "info", title: str = ""):
    """Cria uma caixa de alerta customizada"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    colors = {
        "info": "#d1ecf1",
        "success": "#d4edda",
        "warning": "#fff3cd",
        "error": "#f8d7da"
    }
    
    text_colors = {
        "info": "#0c5460",
        "success": "#155724",
        "warning": "#856404",
        "error": "#721c24"
    }
    
    alert_html = f"""
    <div style="background: {colors[alert_type]}; border: 1px solid {text_colors[alert_type]}; 
                border-radius: var(--border-radius); padding: 1rem; margin: 1rem 0; 
                color: {text_colors[alert_type]};">
        <div style="display: flex; align-items: center; gap: 0.5rem; font-weight: 500;">
            {icons[alert_type]} {title if title else alert_type.title()}
        </div>
        <p style="margin: 0.5rem 0 0 0; line-height: 1.5;">{message}</p>
    </div>
    """
    st.markdown(alert_html, unsafe_allow_html=True)

def create_download_section(title: str, content: str, filename: str, file_type: str = "text/plain"):
    """Cria uma seção de download com visual melhorado"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{title}**")
        st.text_area("Conteúdo:", value=content, height=200, disabled=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Baixar",
            data=content,
            file_name=filename,
            mime=file_type,
            type="primary"
        )

def create_model_selection_card(models: Dict[str, str], selected_model: str, key: str):
    """Cria um card para seleção de modelo com visual melhorado"""
    st.markdown("""
    <div class="custom-card">
        <h3>🤖 Selecionar Modelo de IA</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">
            Escolha o modelo de inteligência artificial para processar seu texto:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    selected = st.selectbox(
        "Modelo:",
        options=list(models.keys()),
        index=list(models.keys()).index(selected_model) if selected_model in models else 0,
        key=key,
        help="Selecione o modelo de IA que será usado para processar o texto anonimizado"
    )
    
    # Mostrar informações do modelo selecionado
    if selected in models:
        model_info = models[selected]
        st.markdown(f"""
        <div style="background: var(--light-bg); padding: 1rem; border-radius: var(--border-radius); 
                    border-left: 4px solid var(--primary-color); margin: 1rem 0;">
            <strong>Modelo Selecionado:</strong> {selected}<br>
            <small style="color: var(--text-secondary);">{model_info}</small>
        </div>
        """, unsafe_allow_html=True)
    
    return selected

def create_results_table(df: pd.DataFrame, title: str = "Resultados da Análise"):
    """Cria uma tabela de resultados com visual melhorado"""
    if df.empty:
        st.info("Nenhum resultado encontrado.")
        return
    
    st.markdown(f"""
    <div class="custom-card">
        <h3>📊 {title}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Aplicar estilos à tabela
    styled_df = df.style.set_properties(**{
        'background-color': 'white',
        'color': 'var(--text-primary)',
        'border': '1px solid var(--border-color)',
        'border-radius': 'var(--border-radius)',
        'padding': '0.5rem'
    })
    
    st.dataframe(styled_df, use_container_width=True)

def create_sidebar_info():
    """Cria informações na sidebar com visual melhorado"""
    st.sidebar.markdown("""
    <div class="custom-card" style="margin-bottom: 1rem;">
        <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">ℹ️ Sobre</h3>
        <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0;">
            <strong>AnonimizaJUD</strong><br>
            Versão 0.91 (Beta)<br><br>
            <strong>Desenvolvido por:</strong><br>
            Juiz Federal<br>
            Rodrigo Gonçalves de Souza
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div class="custom-card">
        <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">📋 Como Usar</h3>
        <ol style="font-size: 0.9rem; color: var(--text-secondary); padding-left: 1.2rem; margin: 0;">
            <li><strong>Anonimize</strong> seu texto (Camada 1)</li>
            <li><strong>Gere resumo</strong> com IA (Camada 2)</li>
            <li><strong>Confira</strong> sempre o resultado</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: var(--border-radius); 
                padding: 1rem; margin-top: 1rem;">
        <p style="color: #856404; font-size: 0.85rem; margin: 0; text-align: center;">
            ⚠️ <strong>Importante:</strong><br>
            Ferramenta em desenvolvimento.<br>
            Sempre confira os resultados.
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_footer():
    """Cria um footer profissional"""
    footer_html = """
    <div style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--border-color); 
                text-align: center; color: var(--text-secondary);">
        <p style="margin: 0; font-size: 0.9rem;">
            © 2024 AnonimizaJUD - Proteção inteligente de dados pessoais
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">
            Desenvolvido com ❤️ para a comunidade jurídica brasileira
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True) 