import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# API Keys
app.config["GUARDIAN_API_KEY"] = os.environ.get("GUARDIAN_API_KEY", "test")
app.config["CLAUDE_API_KEY"] = os.environ.get("CLAUDE_API_KEY", "test")
app.config["REPLICATE_API_KEY"] = os.environ.get("REPLICATE_API_KEY", "test")

db.init_app(app)

with app.app_context():
    import models
    db.create_all()

from flask import render_template, jsonify
from services.guardian import get_news
from services.claude import get_comic_summary
from services.replicate import generate_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news/<int:page>')
def get_news_page(page):
    try:
        articles = get_news(page)
        processed_articles = []
        
        for article in articles:
            try:
                summary = get_comic_summary(article['text'])
                image_url = generate_image(summary)
                
                processed_article = {
                    'title': article['title'],
                    'summary': summary,
                    'image': image_url
                }
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                # Skip failed articles instead of stopping the entire request
                continue
                
        if not processed_articles:
            return jsonify({
                "success": False,
                "error": "No articles could be processed successfully"
            }), 500
            
        return jsonify({
            "success": True,
            "articles": processed_articles
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
