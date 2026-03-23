import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Inicializamos el modelo de lenguaje de forma global para mejorar la eficiencia
# (Este modelo es excelente porque es ligero y entiende español perfectamente)
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def crear_indice(df):
    """
    Transforma el texto de búsqueda en vectores y crea el índice FAISS.
    Recibe: DataFrame con la columna 'texto_busqueda'.
    Retorna: El índice FAISS listo para consultas.
    """
    print("[RAG] Generando embeddings e índice FAISS (esto puede tardar unos segundos)...")
    embeddings = embedder.encode(df["texto_busqueda"].tolist(), show_progress_bar=False)

    # Creamos un índice de tipo L2 (distancia euclidiana)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype("float32"))

    return index


def buscar_y_responder(consulta, df, index):
    """
    Busca los productos más relevantes y aplica el ranking personalizado.
    Recibe: consulta (str), dataframe procesado y el índice FAISS.
    """
    # 1. Búsqueda Vectorial
    vec_query = embedder.encode([consulta]).astype("float32")
    dist, indices = index.search(vec_query, 15)  # Recuperamos 15 candidatos iniciales

    candidatos = df.iloc[indices[0]].copy()

    # 2. Re-ranking (Normalización local de distancias)
    max_dist = dist[0].max() if dist[0].max() > 0 else 1
    candidatos["norm_dist"] = 1 - (dist[0] / max_dist)

    # Aplicamos la fórmula: 60% Semántica + 20% Salud + 20% Precio
    # Se divide norm_nutri entre 100 para que esté en escala 0-1 igual que el resto
    candidatos["rank_final"] = (
        candidatos["norm_dist"] * 0.6
        + (candidatos["norm_nutri"] / 100.0) * 0.2
        + candidatos["norm_precio"] * 0.2
    )

    # 3. Formateo de respuesta
    mejores = candidatos.sort_values("rank_final", ascending=False).head(3)

    # Formateamos la salida para que los números no tengan demasiados decimales
    contexto = "".join(
        [
            f"- {r['titulo']} | Precio: {r['precio']:.2f}€ | Proteínas: {r['proteinas']:.1f}g | Salud: {int(r['norm_nutri'])}/100\n"
            for _, r in mejores.iterrows()
        ]
    )

    return f"**Asistente Nutricional:** Para '{consulta}', he encontrado estas opciones:\n\n{contexto}"


def consultar(df):
    """
    Función principal para ejecutar el RAG.
    """
    id_index = crear_indice(df)
    print("\n✅ ¡Sistema RAG listo! Ya puedes chatear con el asistente.\n")
    
    while True:
        consulta = input("Introduce tu consulta (o 'salir' para terminar): ")
        
        if consulta.lower() == "salir":
            print("¡Hasta luego!")
            break
            
        # Evitamos que pete si el usuario pulsa Enter sin escribir nada
        if not consulta.strip():
            continue
            
        respuesta = buscar_y_responder(consulta, df, id_index)
        print("\n" + respuesta + "-" * 60 + "\n")