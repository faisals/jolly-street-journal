import anthropic
import logging
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_api_key(api_key):
    if not api_key or api_key == "test":
        raise ValueError("Claude API key is not configured")

def get_comic_summary(text):
    api_key = current_app.config['CLAUDE_API_KEY']
    
    try:
        validate_api_key(api_key)
        
        logger.info("Creating comic summary using Claude API")
        client = anthropic.Client(api_key=api_key)
        
        prompt = f"""
        Please create a humorous summary of this news article. Keep it light and entertaining while maintaining the key points:
        
        {text}
        
        Write a summary in about 3-4 sentences with a comedic twist.
        """
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.info("Successfully generated comic summary")
        return response.content[0].text
        
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        raise ValueError(f"Claude API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_comic_summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")
