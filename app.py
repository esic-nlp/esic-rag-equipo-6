import streamlit as st
import pandas as pd
import os
from src.rag import buscar_y_responder, crear_indice
from src.preprocessing import procesar_datos

# Configuración de página
st.set_page_config(page_title="Asistente Nutricional DIA", page_icon="🛒", layout="centered")

# Estilos personalizados (Colores DIA: Rojo #E20613, Blanco Hueso #F9F9F7)
st.markdown("""
    <style>
    .stApp {
        background-color: #F9F9F7;
    }
    .main {
        color: #333;
    }
    /* Estilo para simular la caja de respuestas del Chat */
    .chat-response {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #E20613;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-top: 15px;
        white-space: pre-wrap; /* Mantiene los saltos de línea del texto */
        font-family: monospace;
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
st.title("🛒 Asistente Nutricional DIA")
st.markdown("Busca productos, compara proteínas o encuentra los mejores precios.")

# Inicializamos el dataframe y el índice FAISS
df, index = inicializar_sistema()

# Barra de búsqueda interactiva
query = st.text_input("¿Qué estás buscando hoy?", placeholder="Ej: top 5 embutidos con más proteina")

if query:
    with st.spinner('Procesando consulta con el RAG...'):
        # Invocamos directamente la función de tu archivo rag.py
        # Esto asegura que use tus filtros estrictos de 0.60 y el re-ranking
        respuesta_rag = buscar_y_responder(query, df, index)
        
        st.subheader("Resultados del Asistente")
        
        # Mostramos la respuesta con un estilo de tarjeta limpia
        st.markdown(f'<div class="chat-response">{respuesta_rag}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Datos extraídos de DIA.es - Proyecto RAG Experimental")