let currentPage = 1;
let loading = false;
let hasMore = true;
let articleModal;

function showError(message) {
    const container = document.querySelector('.error-container') || (() => {
        const div = document.createElement('div');
        div.className = 'error-container';
        document.body.appendChild(div);
        return div;
    })();
    
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger alert-dismissible fade show';
    errorAlert.role = 'alert';
    errorAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.appendChild(errorAlert);
    setTimeout(() => errorAlert.remove(), 5000);
}

function validateArticleData(article) {
    if (!article || typeof article !== 'object') {
        throw new Error('Invalid article data');
    }
    
    const images = Array.isArray(article.images) ? article.images : [];
    const prompts = Array.isArray(article.prompts) ? article.prompts : [];
    
    return {
        ...article,
        images: images.filter(url => url && typeof url === 'string'),
        prompts: prompts.filter(prompt => prompt && typeof prompt === 'string')
    };
}

function showArticleDetails(article) {
    try {
        const validatedArticle = validateArticleData(article);
        if (!validatedArticle.images.length) {
            showError('No valid images available for this article');
            return;
        }
        
        const modal = document.getElementById('articleModal');
        const title = modal.querySelector('.modal-title');
        const comicHeader = modal.querySelector('.comic-header');
        const comicSummary = modal.querySelector('.comic-summary');
        const imageGrid = modal.querySelector('.image-grid');
        
        title.textContent = validatedArticle.title;
        comicHeader.textContent = validatedArticle.comic_header;
        comicSummary.textContent = validatedArticle.summary;
        imageGrid.innerHTML = '';
        
        validatedArticle.images.forEach((imageUrl, index) => {
            const container = document.createElement('div');
            container.className = 'image-container';
            
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = `${validatedArticle.title} - Image ${index + 1}`;
            img.loading = 'lazy';
            
            img.onerror = function() {
                this.src = 'https://placehold.co/768x768?text=Comic+News';
                this.alt = 'Failed to load image';
            };
            
            const promptDiv = document.createElement('div');
            promptDiv.className = 'image-prompt';
            promptDiv.textContent = validatedArticle.prompts[index] || 'Image description unavailable';
            
            container.appendChild(img);
            container.appendChild(promptDiv);
            imageGrid.appendChild(container);
        });
        
        articleModal.show();
    } catch (error) {
        showError(`Failed to display article: ${error.message}`);
    }
}

async function loadArticles() {
    if (loading || !hasMore) return;
    
    const loadingEl = document.getElementById('loading');
    loadingEl.classList.remove('d-none');
    loading = true;
    
    try {
        const response = await fetch(`/api/news/${currentPage}`);
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to load articles');
        }
        
        const articles = data.articles;
        if (!Array.isArray(articles)) {
            throw new Error('Invalid response format: articles not found');
        }
        
        if (articles.length === 0) {
            hasMore = false;
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
        try {
            const validatedArticle = validateArticleData(article);
            if (!validatedArticle.images.length) return;
            
            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.article-card');
            const previewImage = clone.querySelector('.article-preview-image');
            
            previewImage.src = validatedArticle.images[0];
            previewImage.alt = validatedArticle.title;
            previewImage.loading = 'lazy';
            
            previewImage.onerror = function() {
                this.src = 'https://placehold.co/768x768?text=Comic+News';
                this.alt = 'Failed to load image';
            };
            
            clone.querySelector('.article-title').textContent = validatedArticle.title;
            card.addEventListener('click', () => showArticleDetails(validatedArticle));
            
            container.appendChild(clone);
        } catch (error) {
            console.error('Failed to render article:', error);
        }
    });
}

// Initialize
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
