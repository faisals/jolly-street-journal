let currentPage = 1;
let loading = false;
let hasMore = true;
let articleModal;

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

function showArticleDetails(article) {
    const modal = document.getElementById('articleModal');
    const title = modal.querySelector('.modal-title');
    const imageGrid = modal.querySelector('.image-grid');

    // Set title
    title.textContent = article.title;

    // Clear and populate image grid
    imageGrid.innerHTML = '';
    
    article.images.forEach((imageUrl, index) => {
        const container = document.createElement('div');
        container.className = 'image-container';
        
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = `${article.title} - Image ${index + 1}`;
        img.className = 'img-fluid';
        
        img.onerror = function() {
            this.src = 'https://placehold.co/768x768?text=Comic+News';
            this.alt = 'Failed to load image';
        };
        
        const promptDiv = document.createElement('div');
        promptDiv.className = 'image-prompt';
        promptDiv.textContent = article.prompts?.[index] || 'Image description unavailable';
        
        container.appendChild(img);
        container.appendChild(promptDiv);
        imageGrid.appendChild(container);
    });

    // Show modal
    articleModal.show();
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
        const card = clone.querySelector('.article-card');
        const previewImage = clone.querySelector('.article-preview-image');
        
        // Set the preview image (first image only)
        previewImage.src = article.images[0];
        previewImage.alt = article.title;
        previewImage.onerror = function() {
            this.src = 'https://placehold.co/768x768?text=Comic+News';
            this.alt = 'Failed to load image';
        };
        
        // Set title
        clone.querySelector('.article-title').textContent = article.title;
        
        // Add click handler
        card.addEventListener('click', () => showArticleDetails(article));
        
        container.appendChild(clone);
    });
}

// Initialize modal
document.addEventListener('DOMContentLoaded', () => {
    articleModal = new bootstrap.Modal(document.getElementById('articleModal'));
    loadArticles();
});

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
