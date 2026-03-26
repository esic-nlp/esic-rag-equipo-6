import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# Modelo robusto para español
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def extraer_top_n(consulta, default=3):
    match = re.search(r"(?:top|dame|los|las)\s*(\d+)", consulta.lower())
    if match: return int(match.group(1))
    match_simple = re.search(r"(\d+)", consulta)
    return int(match_simple.group(1)) if match_simple else default

def analizar_intencion(consulta):
    c = consulta.lower()
    es_ranking_puro = False
    col = None
    asc = False

    if "proteina" in c or "proteico" in c:
        if any(x in c for x in ["más", "mas", "alto", "ranking"]):
            es_ranking_puro, col, asc = True, "proteinas", False
    elif any(x in c for x in ["barato", "económico", "precio"]):
        es_ranking_puro, col, asc = True, "precio", True
        
    return {
        "es_ranking_puro": es_ranking_puro,
        "columna_sort": col,
        "ascendente": asc,
        "termino_busqueda": c.replace("top", "").strip()
    }

def crear_indice(df):
    # Usamos solo el título para el embedding para evitar confusión con descripciones largas
    embeddings = embedder.encode(df["titulo"].tolist(), show_progress_bar=False)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))
    return index

def buscar_y_responder(consulta, df, index):
    intencion = analizar_intencion(consulta)
    top_n = extraer_top_n(consulta)
    
    # 1. FILTRO DE PALABRAS CLAVE (Para evitar gazpachos en embutidos)
    # Extraemos la palabra más importante de la consulta (quitando 'top 5', etc)
    palabras_clave = [p for p in intencion["termino_busqueda"].split() if len(p) > 3]
    
    if intencion["es_ranking_puro"]:
        # Si pide ranking de proteínas de ALGO específico (ej: top 5 embutidos con proteina)
        df_filtrado = df.copy()
        if palabras_clave:
            # Filtramos que el título contenga al menos una de las palabras clave
            mask = df_filtrado['titulo'].str.contains('|'.join(palabras_clave), case=False, na=False)
            df_filtrado = df_filtrado[mask]
        
        mejores = df_filtrado.sort_values(intencion["columna_sort"], ascending=intencion["ascendente"]).head(top_n)
        metodo = "Ranking Directo"
    else:
        # 2. BÚSQUEDA SEMÁNTICA CON FILTRO DE CORTE
        vec_query = embedder.encode([consulta]).astype("float32")
        dist, indices = index.search(vec_query, 100) # Buscamos en 100 productos
        candidatos = df.iloc[indices[0]].copy()
        
        # Invertimos la distancia para que 1 sea perfecto y 0 nada
        max_d = dist[0].max() if dist[0].max() > 0 else 1
        candidatos["score_texto"] = 1 - (dist[0] / max_d)
        
        # FILTRO DE CORTE ESTRICTO: Si el score de texto es bajo, fuera.
        candidatos = candidatos[candidatos["score_texto"] > 0.45]
        
        # 3. RE-RANKING (80% Texto, 20% Nutrición)
        candidatos["rank_final"] = (candidatos["score_texto"] * 0.8) + ((candidatos["norm_nutri"]/100) * 0.2)
        
        mejores = candidatos.sort_values("rank_final", ascending=False).head(top_n)
        metodo = "Búsqueda Semántica Optimizada"

    # --- FORMATO DE SALIDA ---
    if mejores.empty:
        return f"No encontré productos que coincidan con '{consulta}'. Intenta ser más específico."

    res = f"Resultados para: {consulta} ({metodo})\n" + "="*40 + "\n"
    for i, (_, r) in enumerate(mejores.iterrows()):
        res += f"{i+1}. {r['titulo']}\n"
        res += f"   Precio: {r['precio']:.2f}€ | Prot: {r['proteinas']}g | Cal: {r['calories']}kcal\n"
        res += f"   Link: {r.get('url', 'n/a')}\n\n"
    return res

def consultar(df):
    index = crear_indice(df)
    print("Asistente listo. Sin emojis y con filtros estrictos.")
    while True:
        user_input = input("Que buscas?: ")
        if user_input.lower() in ["salir", "exit"]: break
        print(buscar_y_responder(user_input, df, index))