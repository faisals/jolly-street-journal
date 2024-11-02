import requests
from flask import current_app
from models import db, Article

def get_news(page=1):
    api_key = current_app.config['GUARDIAN_API_KEY']
    base_url = "https://content.guardianapis.com/search"
    
    params = {
        'api-key': api_key,
        'page': page,
        'show-fields': 'bodyText',
        'page-size': 10
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        for result in data['response']['results']:
            article = {
                'id': result['id'],
                'title': result['webTitle'],
                'text': result['fields']['bodyText']
            }
            articles.append(article)
            
        return articles
    except Exception as e:
        raise Exception(f"Failed to fetch news: {str(e)}")
