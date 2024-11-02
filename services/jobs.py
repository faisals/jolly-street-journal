import logging
from datetime import datetime, timedelta
from models import db, Article
from services.guardian import get_news as get_guardian_news
from services.nytimes import get_news as get_nytimes_news
from services.claude import get_comic_summary
from services.replicate import generate_images
import json
import re

logger = logging.getLogger(__name__)

def fetch_and_process_articles():
    """Background job to fetch and process articles"""
    from app import app  # Import app at function level
    
    def process_article(article_data, source):
        """Process a single article and save to database"""
        try:
            if not article_data or not isinstance(article_data, dict):
                logger.error("Invalid article data received")
                return

            # Check if article already exists
            existing = Article.query.filter_by(source_id=article_data['id'], source=source).first()
            if existing:
                logger.info(f"Article {article_data['id']} from {source} already exists, skipping")
                return
            
            # Generate comic summary
            summary = get_comic_summary(article_data['text'])
            if not summary:
                logger.error(f"Failed to generate summary for article {article_data['id']}")
                return

            # Extract comic_header and summary from response
            comic_header = None
            comic_summary = None
            
            comic_header_match = re.search(r'<comic_header>(.*?)</comic_header>', summary, re.DOTALL)
            if comic_header_match:
                comic_header = comic_header_match.group(1).strip()
                
            summary_match = re.search(r'<summary>(.*?)</summary>', summary, re.DOTALL)
            if summary_match:
                comic_summary = summary_match.group(1).strip()
            
            # Generate images and ensure proper JSON handling
            image_urls, image_prompts = generate_images(summary)
            
            # Parse and validate image URLs and prompts
            try:
                image_urls_list = json.loads(image_urls) if isinstance(image_urls, str) else []
                prompts_list = json.loads(image_prompts) if isinstance(image_prompts, str) else []
                
                if not isinstance(image_urls_list, list):
                    image_urls_list = []
                if not isinstance(prompts_list, list):
                    prompts_list = []
                
                # Re-serialize as valid JSON strings
                image_urls_json = json.dumps(image_urls_list)
                prompts_json = json.dumps(prompts_list)
                
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"JSON processing error for article {article_data['id']}: {str(e)}")
                image_urls_json = json.dumps([])
                prompts_json = json.dumps([])
            
            article = Article(
                source_id=article_data['id'],
                source=source,
                title=article_data['title'],
                original_text=article_data['text'],
                comic_header=comic_header,
                comic_summary=comic_summary,  # Use extracted summary
                image_urls=image_urls_json,
                image_prompts=prompts_json
            )
            
            db.session.add(article)
            db.session.commit()
            logger.info(f"Successfully processed and saved article: {article_data['id']} from {source}")
            
        except Exception as e:
            logger.error(f"Failed to process article {article_data.get('id', 'unknown')}: {str(e)}")
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
            logger.info(f"Using news source: {news_source}")
            
            # Fetch articles based on configured source
            articles = []
            try:
                articles = get_nytimes_news() if news_source == 'nytimes' else get_guardian_news(page=1)
            except Exception as e:
                logger.error(f"Failed to fetch articles from {news_source}: {str(e)}")
            
            if not articles:
                logger.warning(f"No articles returned from {news_source}")
                return
            
            # Process each article
            for article in articles:
                if article and isinstance(article, dict):
                    process_article(article, news_source)
                else:
                    logger.warning(f"Skipping invalid article data: {article}")
            
            # Cleanup old articles
            cleanup_old_articles()
            
            logger.info("Completed background article processing job")
            
        except Exception as e:
            logger.error(f"Background job failed: {str(e)}")
