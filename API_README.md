# 🚀 FastAPI Web Server - Asistente Nutricional DIA

This is a modern web application built with FastAPI that serves your RAG-based nutritional products assistant with a clean, responsive frontend.

## Features

✨ **Modern Frontend**
- Clean, responsive design using DIA brand colors (Red #E20613, White #F9F9F7)
- Real-time product search with RAG system integration
- Product statistics dashboard
- Smooth animations and transitions
- Mobile-friendly interface

⚡ **FastAPI Backend**
- RESTful API endpoints for product search and retrieval
- FAISS-based semantic search integration
- Product filtering and pagination
- Database statistics endpoint
- Health check endpoint

## Getting Started

### 1. Install Dependencies

Make sure you have Python 3.8+ installed, then:

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Ensure your cleaned product data is available at:
```
data/clean/productos_limpios.csv
```

If you haven't generated this yet, run the main pipeline first:
```bash
python main.py
```

### 3. Run the Server

Start the FastAPI server with:

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `--reload`: Auto-reload on code changes (development only)
- `--host 0.0.0.0`: Listen on all available interfaces
- `--port 8000`: Run on port 8000 (change if needed)

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## API Endpoints

### GET `/`
Returns the main HTML page with the user interface.

### GET `/api/products?limit=20&offset=0`
Retrieve products with pagination.

**Parameters:**
- `limit` (int): Number of products to return (default: 20)
- `offset` (int): Starting position (default: 0)

**Example:**
```bash
curl http://localhost:8000/api/products?limit=10&offset=0
```

### POST `/api/search`
Search products using the RAG system with semantic understanding.

**Request body:**
```json
{
  "query": "proteína alta"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "bajo precio"}'
```

### GET `/api/stats`
Get database statistics (total products, average price, calories, etc.)

**Example:**
```bash
curl http://localhost:8000/api/stats
```

### GET `/api/health`
Health check endpoint to verify the server is running and data is loaded.

**Example:**
```bash
curl http://localhost:8000/api/health
```

## Frontend Usage

### Search Features

The frontend supports various search queries:

- **By Nutrition**: "proteína alta", "bajo en calorías", "más fibra"
- **By Price**: "economico", "bajo precio", "más barato"
- **By Product Type**: "frutas frescas", "carnes magras"
- **By Quantity**: "dame 5", "top 10" (specify how many results)

### Suggestion Tags

Quick search options available on the homepage:
- 🥇 Más Proteína
- 💰 Económico
- ⚡ Bajo en Calorías
- 🍎 Frutas Frescas

### Product Cards

Each product displays:
- Price (prominent red display)
- Nutritional information (proteins, calories, carbs, fats)
- Direct link to the product page
- Hover animations for better UX

### Statistics Dashboard

View overall database statistics:
- Total number of products
- Average price
- Average calories
- Average protein content

## Project Structure

```
esic-rag-equipo-6/
├── api.py                      # FastAPI application
├── main.py                     # Original pipeline entry
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── data/
│   ├── raw/                    # Raw data from web scraping
│   ├── clean/                  # Processed CSV data
│   └── ejemplo.json            # Example data structure
├── src/
│   ├── acquisition.py          # Web scraping
│   ├── preprocessing.py        # Data cleaning
│   └── rag.py                  # RAG system (search & ranking)
└── static/                     # Frontend files
    ├── index.html              # Main page
    ├── style.css               # Stylesheet
    └── script.js               # Frontend logic
```

## Development Tips

### Running with Auto-Reload

During development, use the `--reload` flag to automatically restart the server when you make changes:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Accessing API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Changing the Port

If port 8000 is already in use, specify a different port:

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

Then access the app at `http://localhost:8080`

## Troubleshooting

### "Data not loaded" Error
- Verify `data/clean/productos_limpios.csv` exists
- Run `python main.py` to generate the cleaned data

### Slow Search Requests
- FAISS index is created on startup - first load may take 10-30 seconds
- Subsequent searches should be fast (< 1 second)
- Check that `sentence-transformers` model is properly installed

### Port Already in Use
- Find the process using port 8000: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)
- Kill the process or use a different port

### CORS Issues (if consuming API from external domain)
- Add CORS middleware to `api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Notes

- First request to `/api/search` initializes the FAISS index (10-30 seconds)
- Subsequent searches are optimized for speed
- Product pagination uses efficient offset-limit approach
- Frontend lazy-loads products with "Load More" button

## Browser Compatibility

The frontend works on:
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- 📊 Advanced filtering options
- 🗂️ Product categories and sorting
- ⭐ User favorites/bookmarks
- 📱 Progressive Web App (PWA) support
- 🔔 Price alerts for specific products
- 🌙 Dark mode

## Support

For issues or questions about the RAG system, see the main [README.md](./README.md)

---

**Built with ❤️ using FastAPI and modern web technologies**
