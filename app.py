import streamlit as st
import pandas as pd
import os
from src.rag import buscar_y_responder, crear_indice
from src.preprocessing import procesar_datos

# Configuración de página
st.set_page_config(page_title="Asistente Nutricional DIA", page_icon="🛒", layout="wide")

# Estilos personalizados (Colores DIA: Rojo #E20613, Blanco Hueso #F9F9F7)
st.markdown("""
    <style>
    :root {
        --dia-red: #E20613;
        --dia-white: #F9F9F7;
        --dia-dark: #1a1a1a;
        --dia-light: #f5f5f5;
    }
    
    .stApp {
        background: linear-gradient(135deg, #F9F9F7 0%, #ffffff 100%);
    }
    
    .main {
        color: #333;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #E20613 0%, #c70410 100%);
        padding: 40px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(226, 6, 19, 0.15);
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    .header-container p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        opacity: 0.95;
        font-weight: 300;
    }
    
    /* Search input styling */
    .search-container {
        margin-bottom: 30px;
    }
    
    .stTextInput > div > div > input {
        font-size: 1.05em;
        padding: 16px 20px !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #E20613 !important;
        box-shadow: 0 0 0 3px rgba(226, 6, 19, 0.1) !important;
    }
    
    /* Response styling */
    .chat-response {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f7 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #E20613;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-top: 20px;
        white-space: pre-wrap;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
    }
    
    /* Suggestions styling */
    .suggestion-box {
        background-color: #f0f5ff;
        border: 1px solid #d0deff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        font-size: 0.95em;
        color: #333;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .suggestion-box:hover {
        background-color: #e6edff;
        border-color: #E20613;
        transform: translateX(4px);
    }
    
    /* Spinner overlay */
    .stSpinner > div {
        border-color: #E20613 !important;
    }
    
    /* Footer styling */
    .footer-container {
        text-align: center;
        padding: 25px;
        color: #999;
        font-size: 0.9em;
        border-top: 1px solid #e0e0e0;
        margin-top: 40px;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    /* Subheader styling */
    .subheader {
        color: #E20613;
        font-weight: 600;
        font-size: 1.3em;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    /* Loading state */
    .loading-text {
        color: #E20613;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def inicializar_sistema():
    """Carga los datos y el índice una sola vez para que sea rápido."""
    if not os.path.exists('data/clean/productos_limpios.csv'):
        df = procesar_datos()
    else:
        df = pd.read_csv('data/clean/productos_limpios.csv')
    
    index = crear_indice(df)
    return df, index

# --- Interfaz de Usuario ---
st.markdown("""
    <div class="header-container">
        <h1>🛒 Asistente Nutricional DIA</h1>
        <p>Tu compañero inteligente para elegir mejor productos</p>
    </div>
    """, unsafe_allow_html=True)

# Inicializamos el dataframe y el índice FAISS
df, index = inicializar_sistema()

# Sección de búsqueda
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.markdown("### Busca productos inteligentemente")

col1, col2 = st.columns([4, 1], gap="small")
with col1:
    query = st.text_input("¿Qué estás buscando?", placeholder="Ej: top 5 embutidos con más proteína, productos bajos en grasa, opciones veganas...")
with col2:
    search_button = st.button("🔍 Buscar", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sugerencias de búsqueda
if not query:
    st.markdown("### 💡 Ejemplos de búsqueda")
    col1, col2, col3 = st.columns(3, gap="small")
    
    examples = [
        ("🥩 Top proteínas", "Embutidos con mayor contenido de proteína"),
        ("💰 Mejores precios", "Productos más económicos por categoría"),
        ("🥗 Opciones saludables", "Alimentos bajos en grasas saturadas")
    ]
    
    cols = [col1, col2, col3]
    for idx, (icon_text, description) in enumerate(examples):
        with cols[idx]:
            st.markdown(f"""
            <div class="suggestion-box">
                <strong>{icon_text}</strong><br/>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)

# Procesamiento de búsqueda
if query or search_button:
    if query:
        with st.spinner('⏳ Analizando tu consulta con IA...'):
            respuesta_rag = buscar_y_responder(query, df, index)
            
            st.markdown("### 📊 Resultados")
            st.markdown(f'<div class="chat-response">{respuesta_rag}</div>', unsafe_allow_html=True)

# Footer mejorado
st.markdown("---")
st.markdown("""
    <div class="footer-container">
        <p><strong>Asistente Nutricional DIA</strong></p>
        <p>📦 Datos en tiempo real de DIA.es | 🤖 Powered by RAG + IA</p>
        <p style="margin-top: 10px; font-size: 0.85em; color: #bbb;">Proyecto experimental - Educación en PLN</p>
    </div>
    """, unsafe_allow_html=True)