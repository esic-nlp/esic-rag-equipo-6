// Globals
// (No globals needed)

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const closeResultsBtn = document.getElementById('closeResults');
    const suggestionTags = document.querySelectorAll('.suggestion-tag');

    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    // Close results
    closeResultsBtn.addEventListener('click', closeResults);

    // Suggestions
    suggestionTags.forEach(tag => {
        tag.addEventListener('click', () => {
            searchInput.value = tag.getAttribute('data-query');
            handleSearch();
        });
    });
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('totalProducts').textContent = stats.total_products;
        document.getElementById('avgPrice').textContent = `€${stats.avg_price.toFixed(2)}`;
        document.getElementById('avgCalories').textContent = `${Math.round(stats.avg_calories)} kcal`;
        document.getElementById('avgProtein').textContent = `${stats.avg_protein.toFixed(1)}g`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Handle search
async function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();

    if (!query) {
        alert('Por favor, ingresa una búsqueda');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        showLoading(false);

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayResults(data);
    } catch (error) {
        console.error('Error searching:', error);
        showLoading(false);
        alert('Error al realizar la búsqueda');
    }
}

// Display results
function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsResponse = document.getElementById('resultsResponse');
    const productsGrid = document.getElementById('productsGrid');

    // Parse RAG response to extract header info
    const responseText = data.response || '';
    const headerMatch = responseText.match(/Resultados para '([^']+)' \(([^)]+)\)/);
    const header = headerMatch ? `${headerMatch[1]} • ${headerMatch[2]}` : 'Resultados de búsqueda';
    
    // Show parsed header with search icon
    resultsResponse.innerHTML = `<strong><svg class="lucide-icon inline" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; margin-right: 8px; vertical-align: middle;"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>${header}</strong>`;

    // Parse products from RAG response
    const parsedProducts = parseRagResponse(responseText);
    
    // Build products grid
    productsGrid.innerHTML = '';

    if (parsedProducts.length > 0) {
        parsedProducts.forEach(product => {
            productsGrid.appendChild(createProductCard(product));
        });
    } else {
        productsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: #999;">No se encontraron productos</p>';
    }

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Parse RAG response to extract product data
function parseRagResponse(responseText) {
    const products = [];
    
    // Split by numbered items (e.g., "1. Product Name")
    const itemRegex = /^\d+\.\s+(.+?)$/m;
    const lines = responseText.split('\n');
    
    let currentProduct = null;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (!line) continue;
        
        // Match numbered products
        const numberMatch = line.match(/^(\d+)\.\s+(.+)$/);
        if (numberMatch) {
            // Save previous product if exists
            if (currentProduct && currentProduct.titulo) {
                products.push(currentProduct);
            }
            currentProduct = {
                titulo: numberMatch[2],
                precio: 0,
                proteinas: 0,
                carbohidratos: 0,
                grasas: 0,
                fibra: 0,
                calories: 0,
                url: ''
            };
        } 
        // Match price, protein, calories line
        else if (currentProduct && line.includes('Precio:')) {
            const precioMatch = line.match(/Precio:\s*([\d.,]+)\s*€/);
            const proteinMatch = line.match(/Proteínas:\s*([\d.,]+)\s*g/);
            const caloriesMatch = line.match(/Calorías:\s*([\d.,]+)\s*kcal/);
            
            if (precioMatch) currentProduct.precio = parseFloat(precioMatch[1].replace(',', '.'));
            if (proteinMatch) currentProduct.proteinas = parseFloat(proteinMatch[1].replace(',', '.'));
            if (caloriesMatch) currentProduct.calories = parseFloat(caloriesMatch[1].replace(',', '.'));
        }
        // Match URL/Enlace line
        else if (currentProduct && (line.includes('Enlace:') || line.includes('https://'))) {
            const urlMatch = line.match(/(https?:\/\/[^\s]+)/);
            if (urlMatch) currentProduct.url = urlMatch[1];
        }
    }
    
    // Add last product
    if (currentProduct && currentProduct.titulo) {
        products.push(currentProduct);
    }
    
    return products;
}

// Create product card
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    const nutritionStats = [
        { label: 'Proteínas', value: product.proteinas || 0, unit: 'g' },
        { label: 'Calorías', value: product.calories || 0, unit: 'kcal' },
        { label: 'Carbohidratos', value: product.carbohidratos || 0, unit: 'g' },
        { label: 'Grasas', value: product.grasas || 0, unit: 'g' }
    ];

    const nutritionHTML = nutritionStats.map(stat => `
        <div class="nutrition-item">
            <div class="nutrition-label">${stat.label}</div>
            <div class="nutrition-value">${(stat.value || 0).toFixed(1)}${stat.unit}</div>
        </div>
    `).join('');

    const priceDisplay = product.precio ? `€${product.precio.toFixed(2)}` : 'N/A';
    const linkHTML = product.url ? `<a href="${product.url}" target="_blank" class="product-link">Ver Producto</a>` : '<span class="product-link" style="opacity: 0.5;">Sin enlace</span>';

    card.innerHTML = `
        <div class="product-header">
            <div class="product-title">${product.titulo}</div>
        </div>
        <div class="product-body">
            <div class="product-price">${priceDisplay}</div>
            <div class="nutrition-info">
                ${nutritionHTML}
            </div>
            <div class="product-footer">
                ${linkHTML}
            </div>
        </div>
    `;

    return card;
}

// Show/hide loading
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// Close results
function closeResults() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('searchInput').value = '';
    document.getElementById('searchInput').focus();
}
