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
    .stApp {
        background-color: #F9F9F7;
    }
    .main {
        color: #333;
    }
    .stButton>button {
        background-color: #E20613;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 25px;
    }
    .stButton>button:hover {
        background-color: #B3050F;
        color: white;
    }
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #E20613;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .price-tag {
        color: #E20613;
        font-weight: bold;
        font-size: 1.2rem;
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

df, index = inicializar_sistema()

# Barra de búsqueda
query = st.text_input("¿Qué estás buscando hoy?", placeholder="Ej: top 5 embutidos con más proteina")

if query:
    with st.spinner('Buscando en el catálogo...'):
        # Reutilizamos tu lógica de rag.py
        # Modificamos ligeramente la llamada para obtener el DataFrame de resultados
        from src.rag import analizar_intencion, extraer_top_n, embedder
        import numpy as np

        intencion = analizar_intencion(query)
        top_n = extraer_top_n(query)
        
        # Lógica simplificada de recuperación para la web
        if intencion["es_ranking_puro"]:
            palabras = [p for p in intencion["termino_busqueda"].split() if len(p) > 3]
            df_res = df.copy()
            if palabras:
                mask = df_res['titulo'].str.contains('|'.join(palabras), case=False, na=False)
                df_res = df_res[mask]
            resultados = df_res.sort_values(intencion["columna_sort"], ascending=intencion["ascendente"]).head(top_n)
        else:
            vec_query = embedder.encode([query]).astype("float32")
            dist, indices = index.search(vec_query, 50)
            candidatos = df.iloc[indices[0]].copy()
            max_d = dist[0].max() if dist[0].max() > 0 else 1
            candidatos["score"] = 1 - (dist[0] / max_d)
            candidatos = candidatos[candidatos["score"] > 0.45]
            resultados = candidatos.sort_values("score", ascending=False).head(top_n)

        # Mostrar resultados en tarjetas
        if resultados.empty:
            st.warning("No se encontraron productos exactos. Intenta con otros términos.")
        else:
            st.subheader(f"Mostrando {len(resultados)} resultados")
            
            for _, row in resultados.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="product-card">
                        <h3>{row['titulo']}</h3>
                        <p><span class="price-tag">{row['precio']:.2f}€</span></p>
                        <p><b>Proteínas:</b> {row['proteinas']}g | <b>Calorías:</b> {row['calories']}kcal</p>
                        <a href="{row.get('url', '#')}" target="_blank" style="color: #E20613; text-decoration: none; font-weight: bold;">Ver producto en tienda →</a>
                    </div>
                    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Datos extraídos de DIA.es - Proyecto RAG Experimental")