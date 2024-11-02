let currentPage = 1;
let loading = false;
let hasMore = true;

async function loadArticles() {
    if (loading || !hasMore) return;
    
    const loadingEl = document.getElementById('loading');
    loadingEl.classList.remove('d-none');
    loading = true;

    try {
        const response = await fetch(`/api/news/${currentPage}`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error);
        }

        const articles = data.articles;
        if (articles.length === 0) {
            hasMore = false;
            return;
        }

        renderArticles(articles);
        currentPage++;
    } catch (error) {
        console.error('Error loading articles:', error);
        alert('Failed to load articles. Please try again later.');
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
        
        clone.querySelector('.article-title').textContent = article.title;
        clone.querySelector('.article-summary').textContent = article.summary;
        clone.querySelector('.article-image').src = article.image;
        
        container.appendChild(clone);
    });
}

// Infinite scroll
window.addEventListener('scroll', () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
        loadArticles();
    }
});

// Initial load
loadArticles();
