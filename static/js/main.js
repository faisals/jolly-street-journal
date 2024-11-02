let currentPage = 1;
let loading = false;
let hasMore = true;

function showError(message) {
    const container = document.getElementById('articles-container');
    const existingError = container.querySelector('.alert');
    if (existingError) {
        existingError.remove();
    }
    
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger alert-dismissible fade show w-100';
    errorAlert.role = 'alert';
    errorAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    container.insertBefore(errorAlert, container.firstChild);
}

async function loadArticles() {
    if (loading || !hasMore) return;
    
    const loadingEl = document.getElementById('loading');
    loadingEl.classList.remove('d-none');
    loading = true;

    try {
        const response = await fetch(`/api/news/${currentPage}`);
        let data;
        
        try {
            data = await response.json();
        } catch (parseError) {
            throw new Error('Invalid response format from server');
        }

        if (!response.ok) {
            throw new Error(data.error || `Server error: ${response.status}`);
        }

        if (!data.success) {
            throw new Error(data.error || 'Failed to load articles');
        }

        const articles = data.articles;
        if (!Array.isArray(articles)) {
            throw new Error('Invalid response format: articles not found');
        }

        if (articles.length === 0) {
            hasMore = false;
            loadingEl.classList.add('d-none');
            if (currentPage === 1) {
                showError('No articles available at the moment. Please try again later.');
            }
            return;
        }

        renderArticles(articles);
        currentPage++;
    } catch (error) {
        console.error('Error loading articles:', error.message);
        showError(`Failed to load articles: ${error.message}`);
        hasMore = false;
    } finally {
        loading = false;
        loadingEl.classList.add('d-none');
    }
}

function renderArticles(articles) {
    const container = document.getElementById('articles-container');
    const template = document.getElementById('article-template');

    articles.forEach(article => {
        const clone = template.content.cloneNode(true);
        const imageGrid = clone.querySelector('.image-grid');
        
        // Add images to the grid
        article.images.forEach((imageUrl, index) => {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = `${article.title} - Image ${index + 1}`;
            img.className = 'img-fluid';
            
            // Add error handling for images
            img.onerror = function() {
                this.src = 'https://placehold.co/768x768?text=Comic+News';
                this.alt = 'Failed to load image';
            };
            
            imageGrid.appendChild(img);
        });
        
        clone.querySelector('.article-title').textContent = article.title;
        clone.querySelector('.article-summary').textContent = article.summary;
        
        container.appendChild(clone);
    });
}

// Infinite scroll with debounce
let scrollTimeout;
window.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
            loadArticles();
        }
    }, 100);
});

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
});
