import requests
import logging
from flask import current_app
from models import db, Article
import json

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
            # Skip articles without required fields
            if not all(key in result for key in ['uri', 'title', 'abstract']):
                logger.warning(f"Skipping article due to missing required fields: {result.get('uri', 'unknown')}")
                continue

            # Combine abstract and lead paragraph for fuller content
            text = result['abstract']
            if 'lead_paragraph' in result and result['lead_paragraph']:
                text += "\n\n" + result['lead_paragraph']
            
            # Add multimedia if available
            if 'multimedia' in result and result['multimedia']:
                text += "\n\nImage description: " + result['multimedia'][0].get('caption', '')

            article = {
                'id': result['uri'],
                'title': result['title'],
                'text': text
            }
            articles.append(article)
            
        if not articles:
            logger.warning("No valid articles found in the API response")
            return []
            
        logger.info(f"Successfully fetched {len(articles)} articles")
        return articles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to NYTimes API failed: {str(e)}")
        return []
    except ValueError as e:
        logger.error(f"NYTimes API error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_news: {str(e)}")
        return []
