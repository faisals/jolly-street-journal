import requests
import logging
from flask import current_app
from models import db, Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_api_key(api_key):
    if not api_key or api_key == "test":
        raise ValueError("NYTimes API key is not configured")

def get_news(page=1):
    api_key = current_app.config['NYTIMES_API_KEY']
    
    try:
        validate_api_key(api_key)
        
        base_url = "https://api.nytimes.com/svc/topstories/v2/home.json"
        params = {
            'api-key': api_key
        }
        
        logger.info(f"Fetching news articles from NYTimes API")
        response = requests.get(base_url, params=params)
        
        if response.status_code == 401:
            raise ValueError("Invalid NYTimes API key")
        
        response.raise_for_status()
        data = response.json()
        
        if 'results' not in data:
            raise ValueError("Unexpected API response format")
        
        articles = []
        for result in data['results']:
            article = {
                'id': result['uri'],
                'title': result['title'],
                'text': result['abstract'] + "\n\n" + (result.get('lead_paragraph', ''))
            }
            articles.append(article)
            
        logger.info(f"Successfully fetched {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to NYTimes API failed: {str(e)}")
        raise Exception(f"Failed to connect to NYTimes API: {str(e)}")
    except ValueError as e:
        logger.error(f"NYTimes API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_news: {str(e)}")
        raise Exception(f"Failed to fetch news: {str(e)}")
