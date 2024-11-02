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

@app.route('/api/news/<page>')
def get_news_page(page):
    try:
        articles = get_news(page)
        for article in articles:
            article['summary'] = get_comic_summary(article['text'])
            article['image'] = generate_image(article['summary'])
        return jsonify({"success": True, "articles": articles})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
