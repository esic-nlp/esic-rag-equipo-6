# 🚀 Servidor Web FastAPI - Asistente Nutricional DIA

Esta es una aplicación web moderna construida con FastAPI que sirve tu asistente de productos nutricionales basado en RAG con una interfaz frontal limpia y responsiva.

## Características

✨ **Interfaz Frontend Moderna**
- Diseño limpio y responsivo usando colores de marca DIA (Rojo #E20613, Blanco #F9F9F7)
- Búsqueda de productos en tiempo real con integración del sistema RAG
- Panel de estadísticas de productos
- Animaciones y transiciones suaves
- Interfaz amigable con dispositivos móviles

⚡ **Backend FastAPI**
- Endpoints de API REST para búsqueda y recuperación de productos
- Integración de búsqueda semántica basada en FAISS
- Filtrado de productos y paginación
- Endpoint de estadísticas de base de datos
- Endpoint de verificación de estado

## Comencemos

### 1. Instalar Dependencias

Asegúrate de tener Python 3.8+ instalado, luego:

```bash
pip install -r requirements.txt
```

### 2. Preparar Datos

Asegúrate de que tus datos de productos limpios estén disponibles en:
```
data/clean/productos_limpios.csv
```

Si aún no los has generado, ejecuta primero el pipeline principal:
```bash
python main.py
```

### 3. Ejecutar el Servidor

Inicia el servidor FastAPI con:

```bash
python api.py
```

O usa uvicorn directamente:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Opciones:**
- `--reload`: Recarga automática al cambiar código (solo desarrollo)
- `--host 0.0.0.0`: Escucha en todas las interfaces disponibles
- `--port 8000`: Ejecuta en el puerto 8000 (cambiar si es necesario)

### 4. Acceder a la Aplicación

Abre tu navegador y ve a:
```
http://localhost:8000
```

## Endpoints de la API

### GET `/`
Retorna la página HTML principal con la interfaz de usuario.

### GET `/api/products?limit=20&offset=0`
Recupera productos con paginación.

**Parámetros:**
- `limit` (int): Número de productos a retornar (predeterminado: 20)
- `offset` (int): Posición inicial (predeterminado: 0)

**Ejemplo:**
```bash
curl http://localhost:8000/api/products?limit=10&offset=0
```

### POST `/api/search`
Busca productos usando el sistema RAG con comprensión semántica.

**Cuerpo de la solicitud:**
```json
{
  "query": "proteína alta"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "bajo precio"}'
```

### GET `/api/stats`
Obtiene estadísticas de la base de datos (total de productos, precio promedio, calorías, etc.)

**Ejemplo:**
```bash
curl http://localhost:8000/api/stats
```

### GET `/api/health`
Endpoint de verificación de estado para confirmar que el servidor está ejecutándose y los datos están cargados.

**Ejemplo:**
```bash
curl http://localhost:8000/api/health
```

## Uso de la Interfaz Frontend

### Características de Búsqueda

La interfaz frontal admite varios tipos de consultas de búsqueda:

- **Por Nutrición**: "proteína alta", "bajo en calorías", "más fibra"
- **Por Precio**: "económico", "bajo precio", "más barato"
- **Por Tipo de Producto**: "frutas frescas", "carnes magras"
- **Por Cantidad**: "dame 5", "top 10" (especificar cuántos resultados)

### Etiquetas de Sugerencia

Opciones de búsqueda rápida disponibles en la página principal:
- 🥇 Más Proteína
- 💰 Económico
- ⚡ Bajo en Calorías
- 🍎 Frutas Frescas

### Tarjetas de Productos

Cada producto muestra:
- Precio (exhibición roja prominente)
- Información nutricional (proteínas, calorías, carbohidratos, grasas)
- Enlace directo a la página del producto
- Animaciones al pasar el ratón para mejor experiencia de usuario

### Panel de Estadísticas

Ver estadísticas generales de la base de datos:
- Número total de productos
- Precio promedio
- Calorías promedio
- Contenido promedio de proteínas

## Estructura del Proyecto

```
esic-rag-equipo-6/
├── api.py                      # Aplicación FastAPI
├── main.py                     # Punto de entrada del pipeline original
├── requirements.txt            # Dependencias de Python
├── README.md                   # Documentación del proyecto
├── data/
│   ├── raw/                    # Datos sin procesar del web scraping
│   ├── clean/                  # Datos procesados en CSV
│   └── ejemplo.json            # Estructura de datos de ejemplo
├── src/
│   ├── acquisition.py          # Web scraping
│   ├── preprocessing.py        # Limpieza de datos
│   └── rag.py                  # Sistema RAG (búsqueda y ranking)
└── static/                     # Archivos frontal
    ├── index.html              # Página principal
    ├── style.css               # Hoja de estilos
    └── script.js               # Lógica frontal
```

## Consejos de Desarrollo

### Ejecutar con Recarga Automática

Durante el desarrollo, usa la bandera `--reload` para reiniciar automáticamente el servidor cuando hagas cambios:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Acceder a la Documentación de la API

FastAPI genera automáticamente documentación interactiva de la API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Cambiar el Puerto

Si el puerto 8000 ya está en uso, especifica un puerto diferente:

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

Luego accede a la aplicación en `http://localhost:8080`

## Solución de Problemas

### Error "Datos no cargados"
- Verifica que `data/clean/productos_limpios.csv` exista
- Ejecuta `python main.py` para generar los datos limpios

### Solicitudes de Búsqueda Lentas
- El índice FAISS se crea al iniciar - la primera carga puede tardar 10-30 segundos
- Las búsquedas posteriores deberían ser rápidas (< 1 segundo)
- Verifica que el modelo `sentence-transformers` esté correctamente instalado

### Puerto Ya en Uso
- Encuentra el proceso usando el puerto 8000: `lsof -i :8000` (macOS/Linux) o `netstat -ano | findstr :8000` (Windows)
- Mata el proceso o usa un puerto diferente

### Problemas de CORS (si consumes la API desde un dominio externo)
- Añade middleware CORS a `api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
