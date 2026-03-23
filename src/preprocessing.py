# Todo: implementar código de limpieza de los datos para ingestarlos en el RAG


"""def limpiar_datos(datos):
    Función principal para limpiar los datos obtenidos.

    return None"""

import pandas as pd
import numpy as np
import json
import os
import re

def limpiar_valor_nutricional(texto):
    """Convierte strings como '30.4 gr' o '537 kcal' a float."""
    if pd.isna(texto):
        return 0.0
    # Busca el primer número (entero o decimal) en el string
    match = re.search(r'(\d+(?:\.\d+)?)', str(texto).replace(',', '.'))
    if match:
        return float(match.group(1))
    return 0.0

def procesar_datos(ruta_json='data/raw/productos.json'):
    """Limpia, normaliza y enriquece los datos extraídos."""
    print("Iniciando preprocesamiento de datos...")
    
    with open(ruta_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    df = pd.json_normalize(data)
    
    # Renombrar columnas anidadas del JSON
    cols_mapping = {
        'valores_nutricionales_100_g.Proteinas': 'proteinas',
        'valores_nutricionales_100_g.Carbohidratos': 'carbohidratos',
        'valores_nutricionales_100_g.Grasas': 'grasas',
        'valores_nutricionales_100_g.Fibra': 'fibra',
        'valores_nutricionales_100_g.Valor energetico': 'calories',
        'precio_total': 'precio'
    }
    
    # Asegurarnos de que las columnas existan, si no, crear vacías
    for old_col, new_col in cols_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
        else:
            df[new_col] = '0'

    # 1. Limpieza de datos
    df.dropna(subset=['titulo', 'precio'], inplace=True)
    df.drop_duplicates(subset=['titulo'], inplace=True)
    
    for col in ['proteinas', 'carbohidratos', 'grasas', 'fibra', 'calories']:
        df[col] = df[col].apply(limpiar_valor_nutricional)
        
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0)

    # 2. Normalización y Enriquecimiento
    # texto_busqueda = titulo + categorías
    df['categorias_str'] = df['categorias'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))
    df['texto_busqueda'] = (df['titulo'] + ' ' + df['categorias_str'] + ' ' + df.get('descripcion', '')).str.lower()
    
    # norm_precio: Escalado inverso (más barato = más cercano a 1)
    min_precio = df['precio'].min()
    max_precio = df['precio'].max()
    df['norm_precio'] = 1 - ((df['precio'] - min_precio) / (max_precio - min_precio + 1e-9))
    
    # norm_nutri: Score 0-100 basado en proteína
    max_prot = df['proteinas'].max()
    df['norm_nutri'] = (df['proteinas'] / (max_prot + 1e-9)) * 100
    
    # score_nutricional: Fórmula de macronutrientes (Proteina - Grasas)
    df['score_nutricional'] = df['proteinas'] + df['fibra'] - df['grasas'] - (df['carbohidratos'] * 0.5)

    # Seleccionar columnas finales
    cols_finales = ['titulo', 'precio', 'proteinas', 'carbohidratos', 'grasas', 'fibra', 
                    'calories', 'texto_busqueda', 'norm_precio', 'norm_nutri', 'score_nutricional', 'url']
    
    df_clean = df[cols_finales].copy()
    
    # Guardar resultado
    os.makedirs('data/clean', exist_ok=True)
    ruta_clean = 'data/clean/productos_limpios.csv'
    df_clean.to_csv(ruta_clean, index=False)
    
    print(f"Preprocesamiento completado. Datos guardados en {ruta_clean}")
    return df_clean

if __name__ == "__main__":
    procesar_datos()