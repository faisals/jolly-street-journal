import logging
from datetime import datetime, timedelta
from models import db, Article
from services.guardian import get_news as get_guardian_news
from services.nytimes import get_news as get_nytimes_news
from services.claude import get_comic_summary
from services.replicate import generate_images
import json

logger = logging.getLogger(__name__)

def fetch_and_process_articles():
    """Background job to fetch and process articles"""
    from app import app  # Import app at function level
    
    def process_article(article_data, source):
        """Process a single article and save to database"""
        try:
            # Check if article already exists
            existing = Article.query.filter_by(source_id=article_data['id']).first()
            if existing:
                logger.info(f"Article {article_data['id']} already exists, skipping")
                return
                
            summary = get_comic_summary(article_data['text'])
            image_urls, image_prompts = generate_images(summary)
            
            # Ensure proper JSON serialization
            image_urls_json = json.dumps(json.loads(image_urls) if image_urls else [])
            image_prompts_json = json.dumps(json.loads(image_prompts) if image_prompts else [])
            
            article = Article(
                source_id=article_data['id'],
                source=source,
                title=article_data['title'],
                original_text=article_data['text'],
                comic_summary=summary,
                image_urls=image_urls_json,
                image_prompts=image_prompts_json
            )
            
            db.session.add(article)
            db.session.commit()
            logger.info(f"Successfully processed and saved article: {article_data['id']}")
            
        except Exception as e:
            logger.error(f"Failed to process article {article_data['id']}: {str(e)}")
            db.session.rollback()

    def cleanup_old_articles():
        """Remove articles older than 24 hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            old_articles = Article.query.filter(Article.created_at < cutoff_time).all()
            
            for article in old_articles:
                db.session.delete(article)
            
            db.session.commit()
            logger.info(f"Cleaned up {len(old_articles)} old articles")
        except Exception as e:
            logger.error(f"Failed to cleanup old articles: {str(e)}")
            db.session.rollback()
    
    with app.app_context():
        try:
            logger.info("Starting background article fetch and process job")
            
            # Get news source from config
            news_source = app.config.get('NEWS_SOURCE', 'guardian')
            
            # Fetch articles based on configured source
            if news_source == 'nytimes':
                articles = get_nytimes_news()
            else:
                articles = get_guardian_news(page=1)
            
            # Process each article
            for article in articles:
                process_article(article, news_source)
                
            # Cleanup old articles
            cleanup_old_articles()
            
            logger.info("Completed background article processing job")
            
        except Exception as e:
            logger.error(f"Background job failed: {str(e)}")
