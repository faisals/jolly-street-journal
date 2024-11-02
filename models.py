from app import db
from datetime import datetime

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guardian_id = db.Column(db.String(200), unique=True)
    title = db.Column(db.String(500))
    original_text = db.Column(db.Text)
    comic_summary = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
