from app import db
from datetime import datetime

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(200), unique=True)  # Changed from guardian_id
    source = db.Column(db.String(50), default='guardian')  # Added source field
    title = db.Column(db.String(500))
    original_text = db.Column(db.Text)
    comic_header = db.Column(db.Text)  # Add this field
    comic_summary = db.Column(db.Text)
    image_urls = db.Column(db.Text)  # Store multiple URLs as JSON string
    image_prompts = db.Column(db.Text)  # Store prompts as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
