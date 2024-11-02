import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
scheduler = APScheduler()

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# API Keys
app.config["GUARDIAN_API_KEY"] = os.environ.get("GUARDIAN_API_KEY", "test")
app.config["NYTIMES_API_KEY"] = os.environ.get("NYTIMES_API_KEY", "test")
app.config["CLAUDE_API_KEY"] = os.environ.get("CLAUDE_API_KEY", "test")
app.config["REPLICATE_API_KEY"] = os.environ.get("REPLICATE_API_KEY", "test")

# Set news source to NYTimes
app.config["NEWS_SOURCE"] = "nytimes"

# Scheduler config
app.config['SCHEDULER_API_ENABLED'] = True
app.config['SCHEDULER_TIMEZONE'] = 'UTC'

db.init_app(app)
scheduler.init_app(app)

with app.app_context():
    import models
    db.create_all()

    # Import and register background jobs
    from services.jobs import fetch_and_process_articles
    
    # Schedule the background job
    scheduler.add_job(
        id='fetch_articles',
        func=fetch_and_process_articles,
        trigger='interval',
        minutes=30,
        next_run_time=datetime.now()  # Run immediately on startup
    )
    
    scheduler.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/refresh', methods=['POST'])
def refresh_articles():
    try:
        fetch_and_process_articles()
        return jsonify({
            "success": True,
            "message": "Articles refresh triggered successfully"
        })
    except Exception as e:
        logger.error(f"Failed to refresh articles: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to refresh articles: {str(e)}"
        }), 500

@app.route('/api/news/<int:page>')
def get_news_page(page):
    try:
        per_page = 10
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Query articles from the last 24 hours
        articles = models.Article.query\
            .filter(models.Article.created_at >= cutoff_time)\
            .order_by(models.Article.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        if not articles.items:
            return jsonify({
                "success": True,
                "articles": []
            })
            
        processed_articles = []
        for article in articles.items:
            try:
                # Safely parse JSON strings with proper error handling
                try:
                    images = json.loads(article.image_urls) if article.image_urls else []
                    prompts = json.loads(article.image_prompts) if article.image_prompts else []
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"JSON parsing error for article {article.id}: {str(e)}")
                    images = []
                    prompts = []
                
                # Skip articles without required data
                if not images or not prompts:
                    logger.warning(f"Article {article.id} has missing images or prompts")
                    continue
                    
                processed_articles.append({
                    'title': article.title,
                    'summary': article.comic_summary,
                    'images': images,
                    'prompts': prompts
                })
            except Exception as e:
                logger.error(f"Failed to process article {article.id}: {str(e)}")
                continue
        
        return jsonify({
            "success": True,
            "articles": processed_articles
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch news page {page}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to fetch news: {str(e)}"
        }), 500
