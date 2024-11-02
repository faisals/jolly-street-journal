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
        You are a witty comic strip writer for a digital news portal. Review this news article and create these components:

        Article text:
        {text}

        Please provide your response in exactly this format with these components, separated by double newlines:

        1. HEADER:
        Create a short, punchy, comic-style headline (max 10 words) that captures the essence of the story in a humorous way. Use wordplay, puns, or classic comic exclamations where appropriate.

        2. SUMMARY:
        Write a 3-4 sentence summary that maintains journalistic accuracy but adds a light, humorous twist. The tone should be similar to The Onion but less satirical - focus on clever observations and gentle humor rather than satire.

        3. IMAGE PROMPTS:
        Create four distinct image prompts for AI image generation, each capturing a different aspect or moment from the story. Each prompt must:
        - Start with "Create a comic-style illustration:"
        - Include "in the style of garfield-strip"
        - Specify key visual elements, characters, and their actions
        - Add relevant artistic details (lighting, composition, etc.)
        - Keep each prompt focused and concise (max 100 words)
        
        FORMAT FOR EACH PROMPT:
        PROMPT 1: [First scene - Main event or key moment]
        PROMPT 2: [Second scene - Reaction or consequence]
        PROMPT 3: [Third scene - Humorous detail or side story]
        PROMPT 4: [Fourth scene - Conclusion or resolution]

        Note: Make each prompt visually distinct while maintaining a cohesive narrative flow across all four scenes.
        """

        response = client.messages.create(model="claude-3-sonnet-20240229",
                                       max_tokens=1000,
                                       messages=[{
                                           "role": "user",
                                           "content": prompt
                                       }])

        logger.info("Successfully generated comic summary")
        return response.content[0].text

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        raise ValueError(f"Claude API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_comic_summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")
