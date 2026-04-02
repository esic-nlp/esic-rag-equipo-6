2from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import os
from src.rag import buscar_y_responder, crear_indice

# Initialize FastAPI app
app = FastAPI(title="Asistente Nutricional DIA", description="RAG System for nutritional products")

# Global variables for data and index
df_data = None
faiss_index = None

class QueryRequest(BaseModel):
    query: str

class ProductResponse(BaseModel):
    titulo: str
    precio: float
    proteinas: float
    carbohidratos: float
    grasas: float
    fibra: float
    calories: float
    url: str

@app.on_event("startup")
async def startup_event():
    """Load data and create FAISS index on startup"""
    global df_data, faiss_index
    
    print("[API] Loading product data...")
    
    # Load the clean data
    if os.path.exists('data/clean/productos_limpios.csv'):
        df_data = pd.read_csv('data/clean/productos_limpios.csv')
        print(f"[API] Loaded {len(df_data)} products")
        
        # Create FAISS index
        faiss_index = crear_indice(df_data)
        print("[API] FAISS index created successfully")
    else:
        print("[API] ERROR: Clean data not found at data/clean/productos_limpios.csv")
        raise FileNotFoundError("Clean product data not found")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html", media_type="text/html")

@app.get("/api/products", response_model=list[ProductResponse])
async def get_all_products(limit: int = 20, offset: int = 0):
    """Get all products with pagination"""
    if df_data is None:
        return {"error": "Data not loaded"}
    
    subset = df_data.iloc[offset:offset+limit]
    products = []
    
    for _, row in subset.iterrows():
        products.append({
            "titulo": row["titulo"],
            "precio": float(row["precio"]),
            "proteinas": float(row["proteinas"]),
            "carbohidratos": float(row["carbohidratos"]),
            "grasas": float(row["grasas"]),
            "fibra": float(row["fibra"]),
            "calories": float(row["calories"]),
            "url": row["url"]
        })
    
    return products

@app.post("/api/search")
async def search_products(request: QueryRequest):
    """Search products using RAG system"""
    if df_data is None or faiss_index is None:
        return {"error": "Data not loaded"}
    
    if not request.query.strip():
        return {"error": "Query cannot be empty"}
    
    try:
        # Get the RAG response
        response_text = buscar_y_responder(request.query, df_data, faiss_index)
        
        # Parse the response to extract products
        lines = response_text.strip().split('\n')
        products = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for numbered results (e.g., "1. Product Name")
            if line and line[0].isdigit() and '.' in line:
                # Extract product info
                product_title = line.split('. ', 1)[1] if '. ' in line else ""
                
                # Next line should have price, protein, calories
                if i + 1 < len(lines):
                    details_line = lines[i + 1].strip()
                    product_info = {
                        "titulo": product_title,
                        "details": details_line
                    }
                    
                    # Try to extract from details
                    try:
                        # Find product in dataframe
                        matching = df_data[df_data['titulo'].str.contains(product_title[:30], case=False, na=False)]
                        if not matching.empty:
                            row = matching.iloc[0]
                            product_info.update({
                                "precio": float(row["precio"]),
                                "proteinas": float(row["proteinas"]),
                                "carbohidratos": float(row["carbohidratos"]),
                                "grasas": float(row["grasas"]),
                                "fibra": float(row["fibra"]),
                                "calories": float(row["calories"]),
                                "url": row["url"]
                            })
                    except:
                        pass
                    
                    products.append(product_info)
                    i += 3  # Skip the details and empty lines
                else:
                    i += 1
            else:
                i += 1
        
        return {
            "query": request.query,
            "response": response_text,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Get statistics about the product database"""
    if df_data is None:
        return {"error": "Data not loaded"}
    
    return {
        "total_products": len(df_data),
        "avg_price": float(df_data["precio"].mean()),
        "avg_calories": float(df_data["calories"].mean()),
        "avg_protein": float(df_data["proteinas"].mean()),
        "price_range": {
            "min": float(df_data["precio"].min()),
            "max": float(df_data["precio"].max())
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "data_loaded": df_data is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
