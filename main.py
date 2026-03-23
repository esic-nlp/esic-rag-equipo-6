from src.acquisition import obtener_productos
from src.preprocessing import procesar_datos
from src.rag import consultar
import os
import pandas as pd

def main():
    print("=== INICIANDO PROYECTO RAG: ASISTENTE NUTRICIONAL ===")
    
    # 1. Adquisición (solo extrae si no existe el raw para no tardar cada vez que pruebas)
    if not os.path.exists('data/raw/productos.json'):
        obtener_productos()
    else:
        print("[INFO] Los datos raw ya existen. Omitiendo extracción de la web.")
        
    # 2. Preprocesamiento (limpia los datos y crea las columnas necesarias)
    if not os.path.exists('data/clean/productos_limpios.csv'):
        df_procesado = procesar_datos()
    else:
        print("[INFO] Los datos limpios ya existen. Cargando directamente...")
        df_procesado = pd.read_csv('data/clean/productos_limpios.csv')

    if len(df_procesado) == 0:
        print("Error: No hay datos procesados.")
        return

    # 3. Lanzar el sistema RAG interactivo
    consultar(df_procesado)

if __name__ == "__main__":
    main()