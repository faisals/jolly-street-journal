import anthropic
from flask import current_app

def get_comic_summary(text):
    client = anthropic.Client(api_key=current_app.config['CLAUDE_API_KEY'])
    
    prompt = f"""
    Please create a humorous summary of this news article. Keep it light and entertaining while maintaining the key points:
    
    {text}
    
    Write a summary in about 3-4 sentences with a comedic twist.
    """
    
    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        raise Exception(f"Failed to generate summary: {str(e)}")
