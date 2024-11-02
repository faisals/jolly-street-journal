from app import db
from datetime import datetime

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guardian_id = db.Column(db.String(200), unique=True)
    title = db.Column(db.String(500))
    original_text = db.Column(db.Text)
    comic_summary = db.Column(db.Text)
    image_urls = db.Column(db.Text)  # Store multiple URLs as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
