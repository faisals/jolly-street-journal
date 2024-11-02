import requests
import logging
from flask import current_app
from models import db, Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_api_key(api_key):
    if not api_key or api_key == "test":
        raise ValueError("Guardian API key is not configured")

def get_news(page=1):
    api_key = current_app.config['GUARDIAN_API_KEY']
    
    try:
        validate_api_key(api_key)
        
        base_url = "https://content.guardianapis.com/search"
        params = {
            'api-key': api_key,
            'page': page,
            'show-fields': 'bodyText',
            'page-size': 10
        }
        
        logger.info(f"Fetching news articles from Guardian API - page {page}")
        response = requests.get(base_url, params=params)
        
        if response.status_code == 401:
            raise ValueError("Invalid Guardian API key")
        
        response.raise_for_status()
        data = response.json()
        
        if 'response' not in data:
            raise ValueError("Unexpected API response format")
        
        articles = []
        for result in data['response']['results']:
            article = {
                'id': result['id'],
                'title': result['webTitle'],
                'text': result['fields']['bodyText']
            }
            articles.append(article)
            
        logger.info(f"Successfully fetched {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Guardian API failed: {str(e)}")
        raise Exception(f"Failed to connect to Guardian API: {str(e)}")
    except ValueError as e:
        logger.error(f"Guardian API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_news: {str(e)}")
        raise Exception(f"Failed to fetch news: {str(e)}")
