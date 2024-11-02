import anthropic
import logging
import re
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_api_key(api_key):
    if not api_key or api_key == "test":
        raise ValueError("Claude API key is not configured")

def validate_response_format(response):
    """Validate that the response contains all required tags with content"""
    required_tags = ['comic_header', 'summary']
    required_tags.extend([f'image_prompt{i}' for i in range(1, 5)])
    
    for tag in required_tags:
        pattern = f'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, response, re.DOTALL)
        if not match or not match.group(1).strip():
            logger.error(f"Missing or empty {tag} tag in response")
            return False
    return True

def get_comic_summary(text):
    api_key = current_app.config['CLAUDE_API_KEY']

    try:
        validate_api_key(api_key)
        logger.info("Creating comic summary using Claude API")
        
        client = anthropic.Client(api_key=api_key)
        
        prompt = """You are a comic strip artist creating a four-panel comic strip narrative from a news article. Follow these instructions EXACTLY:

1. Read this news article:
{text}

2. Generate your response using ONLY these XML tags in this EXACT order:

<comic_header>
Write ONLY a short, punchy headline (max 8 words) that captures the story's essence with comic-style humor.
</comic_header>

<summary>
Write ONLY 2-3 sentences summarizing the story with gentle humor while maintaining journalistic accuracy.
</summary>

Now create EXACTLY 4 comic panel descriptions, each in its own XML tag:

<image_prompt1>
Write ONLY a clear, detailed scene description for Panel 1 (Opening): Introduce key characters and setting. MUST include "A black and white stick figure comic panel in XKCD style.The linework should be simple and clean, typical of XKCD comics." and describe specific expressions, poses, and environment.
</image_prompt1>

<image_prompt2>
Write ONLY a clear, detailed scene description for Panel 2 (Action): Show the main conflict or event unfolding. MUST include "A black and white stick figure comic panel in XKCD style.The linework should be simple and clean, typical of XKCD comics." and describe specific movements, reactions, and tension.
</image_prompt2>

<image_prompt3>
Write ONLY a clear, detailed scene description for Panel 3 (Reaction): Show emotional responses or consequences. MUST include "A black and white stick figure comic panel in XKCD style.The linework should be simple and clean, typical of XKCD comics." and describe specific character reactions and environmental details.
</image_prompt3>

<image_prompt4>
Write ONLY a clear, detailed scene description for Panel 4 (Conclusion): Show the story's resolution with a comedic twist. MUST include "A black and white stick figure comic panel in XKCD style.The linework should be simple and clean, typical of XKCD comics." and describe specific final poses and expressions.
</image_prompt4>

CRITICAL RULES:
- Each image prompt MUST include the phrase "A black and white stick figure comic panel in XKCD style.The linework should be simple and clean, typical of XKCD comics."
- Keep each prompt under 75 words
- Use specific visual descriptions (poses, expressions, actions)
- Maintain consistent characters across all panels
- Make sure each panel flows logically into the next
- DO NOT include any text or explanation outside the XML tags
- DO NOT use nested tags or modify tag names
"""

        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt.format(text=text)
            }]
        )

        generated_text = response.content[0].text.strip()
        
        if not validate_response_format(generated_text):
            logger.error("Generated response does not match required format")
            raise ValueError("Invalid response format from Claude API")
            
        logger.info("Successfully generated comic summary with validated format")
        return generated_text

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        raise ValueError(f"Claude API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_comic_summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")
