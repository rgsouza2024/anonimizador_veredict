# Exemplo de como usar as melhorias de interface no anonimizador
# Este arquivo demonstra como integrar as três sugestões de melhoria

import streamlit as st
import time

# Simular as funções que foram adicionadas ao anonimizador.py
def create_progress_steps(current_step, total_steps, step_labels):
    """Cria um progress bar visual com etapas numeradas"""
    progress_html = """
    <div style="margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    """
    
    for i, label in enumerate(step_labels, 1):
        is_active = i == current_step
        is_completed = i < current_step
        
        status_color = "#28a745" if is_completed else "#007bff" if is_active else "#dee2e6"
        text_color = "#fff" if (is_active or is_completed) else "#6c757d"
        
        progress_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: {status_color}; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;
                        font-weight: bold; color: {text_color}; font-size: 1.1rem;">
                {i if not is_completed else "✓"}
            </div>
            <span style="font-size: 0.85rem; color: {text_color}; text-align: center; font-weight: 500;">
                {label}
            </span>
        </div>
        """
        
        if i < len(step_labels):
            progress_html += f"""
            <div style="flex: 1; height: 2px; background: {'#28a745' if is_completed else '#dee2e6'}; 
                        margin: 0 1rem; margin-top: 20px;"></div>
            """
    
    progress_html += """
        </div>
        <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; text-align: center;">
            <span style="color: #007bff; font-weight: 600;">Etapa {current_step} de {total_steps}</span>
        </div>
    </div>
    """
    
    return progress_html

def show_enhanced_loading(operation_name, current_step=None, total_steps=None, step_labels=None):
    """Mostra loading melhorado com progress bar se disponível"""
    if current_step and total_steps and step_labels:
        st.markdown(create_progress_steps(current_step, total_steps, step_labels), unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div class="loading-spinner"></div>
            <div style="margin-left: 1rem;">
                <div style="font-weight: 600; color: #007bff; font-size: 1.1rem;">{operation_name}</div>
                <div style="color: #6c757d; font-size: 0.9rem;">Processando, aguarde...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_toast_notification(message, notification_type="info", duration=5):
    """Mostra notificação toast elegante"""
    colors = {
        "success": {"bg": "#d4edda", "border": "#c3e6cb", "text": "#155724", "icon": "✅"},
        "error": {"bg": "#f8d7da", "border": "#f5c6cb", "text": "#721c24", "icon": "❌"},
        "warning": {"bg": "#fff3cd", "border": "#ffeaa7", "text": "#856404", "icon": "⚠️"},
        "info": {"bg": "#d1ecf1", "border": "#bee5eb", "text": "#0c5460", "icon": "ℹ️"}
    }
    
    color_scheme = colors.get(notification_type, colors["info"])
    
    toast_html = f"""
    <div id="toast-{hash(message)}" style="
        position: fixed; top: 20px; right: 20px; z-index: 1000;
        background: {color_scheme['bg']}; border: 1px solid {color_scheme['border']};
        border-radius: 8px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        max-width: 400px; animation: slideInRight 0.3s ease-out;
        display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.2rem;">{color_scheme['icon']}</span>
        <div style="color: {color_scheme['text']}; font-weight: 500;">{message}</div>
        <button onclick="document.getElementById('toast-{hash(message)}').remove()" 
                style="margin-left: auto; background: none; border: none; color: {color_scheme['text']}; 
                       cursor: pointer; font-size: 1.2rem;">×</button>
    </div>
    <style>
        @keyframes slideInRight {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
    </style>
    <script>
        setTimeout(function() {{
            const toast = document.getElementById('toast-{hash(message)}');
            if (toast) {{
                toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
                setTimeout(() => toast.remove(), 300);
            }}
        }}, {duration * 1000});
        
        @keyframes slideOutRight {{
            from {{ transform: translateX(0); opacity: 1; }}
            to {{ transform: translateX(100%); opacity: 0; }}
        }}
    </script>
    """
    
    st.markdown(toast_html, unsafe_allow_html=True)

def create_contextual_help(help_text, icon="💡", title="Dica"):
    """Cria caixa de ajuda contextual elegante"""
    help_html = f"""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                border-left: 4px solid #2196f3; border-radius: 8px; padding: 1rem; 
                margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <strong style="color: #1976d2; font-size: 0.95rem;">{title}</strong>
        </div>
        <p style="color: #424242; font-size: 0.9rem; margin: 0; line-height: 1.4;">
            {help_text}
        </p>
    </div>
    """
    return help_html

def create_metrics_dashboard():
    """Cria dashboard de métricas visuais"""
    # Simular métricas (em produção, viriam do banco de dados)
    metrics = {
        "arquivos_processados": st.session_state.get('metric_arquivos_processados', 0),
        "textos_anonimizados": st.session_state.get('metric_textos_anonimizados', 0),
        "tokens_processados": st.session_state.get('metric_tokens_processados', 0),
        "tempo_medio_processamento": st.session_state.get('metric_tempo_medio', 0)
    }
    
    dashboard_html = f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 1rem 0;">
        <h3 style="color: #003366; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
            📊 Dashboard de Métricas
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <!-- Métrica 1 -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['arquivos_processados']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Arquivos Processados</div>
            </div>
            
            <!-- Métrica 2 -->
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['textos_anonimizados']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Textos Anonimizados</div>
            </div>
            
            <!-- Métrica 3 -->
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['tokens_processados']:,}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Tokens Processados</div>
            </div>
            
            <!-- Métrica 4 -->
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {metrics['tempo_medio_processamento']:.1f}s
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Tempo Médio</div>
            </div>
        </div>
        
        <!-- Gráfico de atividade (simulado) -->
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e0;">
            <h4 style="color: #003366; margin-bottom: 1rem;">Atividade Recente</h4>
            <div style="display: flex; align-items: end; gap: 0.5rem; height: 100px;">
                {''.join([f'<div style="background: linear-gradient(to top, #007bff, #0056b3); width: 30px; height: {20 + (i * 10)}px; border-radius: 4px 4px 0 0; opacity: {0.3 + (i * 0.1)};"></div>' for i in range(7)])}
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
                <span>7 dias atrás</span>
                <span>Hoje</span>
            </div>
        </div>
    </div>
    """
    
    return dashboard_html

# Configuração da página
st.set_page_config(page_title="Exemplo Melhorias Interface", layout="wide")

# CSS customizado
st.markdown("""
<style>
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Título
st.title("🎨 Exemplo de Melhorias de Interface")

# Inicializar métricas de exemplo
if 'metric_arquivos_processados' not in st.session_state:
    st.session_state.metric_arquivos_processados = 0
if 'metric_textos_anonimizados' not in st.session_state:
    st.session_state.metric_textos_anonimizados = 0
if 'metric_tokens_processados' not in st.session_state:
    st.session_state.metric_tokens_processados = 0
if 'metric_tempo_medio' not in st.session_state:
    st.session_state.metric_tempo_medio = 0

# Criar abas para demonstrar cada melhoria
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard", 
    "🔄 Progress Bar", 
    "🔔 Notificações", 
    "💡 Ajuda Contextual"
])

with tab1:
    st.header("Dashboard de Métricas")
    st.markdown(create_metrics_dashboard(), unsafe_allow_html=True)
    
    # Botões para simular incremento das métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📄 Processar Arquivo"):
            st.session_state.metric_arquivos_processados += 1
            show_toast_notification("Arquivo processado com sucesso!", "success")
            st.rerun()
    
    with col2:
        if st.button("📝 Anonimizar Texto"):
            st.session_state.metric_textos_anonimizados += 1
            show_toast_notification("Texto anonimizado!", "success")
            st.rerun()
    
    with col3:
        if st.button("🔢 Adicionar Tokens"):
            st.session_state.metric_tokens_processados += 1000
            show_toast_notification("Tokens adicionados!", "info")
            st.rerun()
    
    with col4:
        if st.button("⏱️ Atualizar Tempo"):
            st.session_state.metric_tempo_medio = 2.5
            show_toast_notification("Tempo médio atualizado!", "info")
            st.rerun()

with tab2:
    st.header("Progress Bar Inteligente")
    
    # Simular processo de anonimização
    if st.button("🚀 Iniciar Processo de Anonimização", type="primary"):
        # Etapa 1
        show_enhanced_loading(
            "Anonimizando PDF",
            current_step=1,
            total_steps=3,
            step_labels=["Extraindo texto", "Analisando entidades", "Aplicando anonimização"]
        )
        time.sleep(2)
        
        # Etapa 2
        show_enhanced_loading(
            "Anonimizando PDF",
            current_step=2,
            total_steps=3,
            step_labels=["Extraindo texto", "Analisando entidades", "Aplicando anonimização"]
        )
        time.sleep(2)
        
        # Etapa 3
        show_enhanced_loading(
            "Anonimizando PDF",
            current_step=3,
            total_steps=3,
            step_labels=["Extraindo texto", "Analisando entidades", "Aplicando anonimização"]
        )
        time.sleep(1)
        
        show_toast_notification("Processo concluído com sucesso!", "success", duration=4)
        st.success("✅ Anonimização concluída!")

with tab3:
    st.header("Sistema de Notificações Toast")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Sucesso"):
            show_toast_notification("Operação realizada com sucesso!", "success")
    
    with col2:
        if st.button("❌ Erro"):
            show_toast_notification("Ocorreu um erro durante o processamento", "error")
    
    with col3:
        if st.button("⚠️ Aviso"):
            show_toast_notification("Atenção: arquivo muito grande", "warning")
    
    with col4:
        if st.button("ℹ️ Info"):
            show_toast_notification("Informação importante sobre o processo", "info")

with tab4:
    st.header("Ajuda Contextual")
    
    # Exemplo de ajuda contextual
    st.markdown(create_contextual_help(
        "Para melhores resultados na anonimização, certifique-se de que o PDF contém texto selecionável e não é uma imagem escaneada.",
        icon="📝",
        title="Dica de Processamento"
    ), unsafe_allow_html=True)
    
    st.markdown(create_contextual_help(
        "O sistema suporta múltiplos modelos de IA. Experimente diferentes opções para encontrar o que funciona melhor para seu caso de uso.",
        icon="🤖",
        title="Modelos de IA"
    ), unsafe_allow_html=True)
    
    st.markdown(create_contextual_help(
        "As métricas são atualizadas em tempo real e podem ajudar você a acompanhar o uso da aplicação.",
        icon="📊",
        title="Métricas"
    ), unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Sobre as Melhorias")
    st.markdown("""
    **1. Progress Bar Inteligente:**
    - Mostra etapas do processo
    - Feedback visual em tempo real
    - Reduz ansiedade do usuário
    
    **2. Notificações Toast:**
    - Não intrusivas
    - Diferentes tipos (sucesso, erro, aviso, info)
    - Auto-dismiss após tempo configurável
    
    **3. Dashboard de Métricas:**
    - Visualização de dados de uso
    - Gráficos de atividade
    - Métricas em tempo real
    
    **4. Ajuda Contextual:**
    - Dicas específicas para cada funcionalidade
    - Design elegante e informativo
    - Melhora a experiência do usuário
    """)

st.markdown("---")
st.markdown("**💡 Dica:** Execute este exemplo para ver as melhorias em ação!") 