import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# Modelo
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# =========================
# EXTRAER TOP N
# =========================

def extraer_top_n(consulta, default=3):
    """Detecta números en la consulta para ajustar la cantidad de resultados."""
    # Busca patrones como 'top 5', 'los 10 mejores', 'dame 7'
    match = re.search(r"(?:top|dame|los|las)\s*(\d+)", consulta.lower())
    if match:
        return int(match.group(1))
    
    # Busca un número suelto si no hay palabras clave antes
    match_simple = re.search(r"(\d+)", consulta)
    if match_simple:
        return int(match_simple.group(1))
        
    return default

# =========================
# ANALIZAR INTENCIÓN
# =========================

def analizar_intencion(consulta):
    consulta = consulta.lower()
    
    es_ranking_puro = False
    columna_sort = None
    ascendente = False

    # Lógica para "más proteína"
    if "proteina" in consulta or "proteico" in consulta:
        if any(x in consulta for x in ["más", "mas", "alto", "mejor"]):
            es_ranking_puro = True
            columna_sort = "proteinas"
            ascendente = False
            
    # Lógica para "más barato"
    elif any(x in consulta for x in ["barato", "económico", "economico", "menor precio"]):
        es_ranking_puro = True
        columna_sort = "precio"
        ascendente = True

    # Lógica para "bajo en calorías"
    elif "caloría" in consulta or "caloria" in consulta or "light" in consulta:
        if "bajo" in consulta or "menos" in consulta:
            es_ranking_puro = True
            columna_sort = "calories"
            ascendente = True

    return {
        "saludable": "saludable" in consulta or "sano" in consulta,
        "alto_proteina": "proteina" in consulta,
        "bajo_calorias": "caloria" in consulta or "light" in consulta,
        "economico": "barato" in consulta or "economico" in consulta,
        "es_ranking_puro": es_ranking_puro,
        "columna_sort": columna_sort,
        "ascendente": ascendente
    }

# =========================
# CREAR ÍNDICE
# =========================

def crear_indice(df):
    print("[RAG] Generando embeddings e índice FAISS...")
    embeddings = embedder.encode(df["texto_busqueda"].tolist(), show_progress_bar=False)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings).astype("float32"))
    return index

# =========================
# BÚSQUEDA + RANKING
# =========================

def buscar_y_responder(consulta, df, index):
    intencion = analizar_intencion(consulta)
    top_n = extraer_top_n(consulta)

    if intencion["es_ranking_puro"]:
        # Ordenación directa por columna numérica
        mejores = df.sort_values(intencion["columna_sort"], ascending=intencion["ascendente"]).head(top_n)
        metodo = f"Ranking directo por {intencion['columna_sort']}"
    else:
        # Búsqueda semántica (vectorial)
        vec_query = embedder.encode([consulta]).astype("float32")
        # Buscamos un margen mayor (20) para luego filtrar y rankear
        dist, indices = index.search(vec_query, max(20, top_n))
        candidatos = df.iloc[indices[0]].copy()

        max_dist = dist[0].max() if dist[0].max() > 0 else 1
        candidatos["norm_dist"] = 1 - (dist[0] / max_dist)

        # Score ponderado: 50% semántica, 25% nutrición, 25% precio
        candidatos["rank_final"] = (
            candidatos["norm_dist"] * 0.5 + 
            (candidatos["norm_nutri"] / 100.0) * 0.25 + 
            candidatos["norm_precio"] * 0.25
        )

        # Bonus por intención
        if intencion["saludable"]: candidatos["rank_final"] += 0.2
        if intencion["alto_proteina"]: 
            max_p = df["proteinas"].max() if df["proteinas"].max() > 0 else 1
            candidatos["rank_final"] += (candidatos["proteinas"] / max_p) * 0.3

        mejores = candidatos.sort_values("rank_final", ascending=False).head(top_n)
        metodo = "Búsqueda Semántica + Re-ranking"

    # -------- CONSTRUCCIÓN DE LA RESPUESTA --------
    res_texto = f"\nResultados para '{consulta}' ({metodo} - Cantidad: {top_n}):\n\n"
    
    for i, (_, r) in enumerate(mejores.iterrows()):
        res_texto += (
            f"{i+1}. {r['titulo']}\n"
            f"   Precio: {r['precio']:.2f}€ | Proteínas: {r['proteinas']:.1f}g | Calorías: {r['calories']:.0f}kcal\n"
            f"   Enlace: {r.get('url', 'No disponible')}\n\n"
        )

    return res_texto

# =========================
# LOOP PRINCIPAL
# =========================

def consultar(df):
    index = crear_indice(df)
    print("\nSistema RAG listo.")
    
    while True:
        consulta = input("Consulta: ")
        
        if consulta.lower() in ["salir", "exit", "quit"]:
            print("Cerrando asistente.")
            break
            
        if not consulta.strip():
            continue
            
        respuesta = buscar_y_responder(consulta, df, index)
        print(respuesta + "-" * 50)