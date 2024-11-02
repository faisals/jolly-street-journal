from app import app, db
from models import Article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_all_articles():
    with app.app_context():
        try:
            # Get count of articles before deletion
            count = Article.query.count()
            
            # Delete all articles
            Article.query.delete()
            db.session.commit()
            
            logger.info(f"Successfully deleted {count} articles from the database")
            print(f"Successfully deleted {count} articles from the database")
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Failed to delete articles: {str(e)}"
            logger.error(error_msg)
            print(error_msg)

if __name__ == "__main__":
    delete_all_articles()
