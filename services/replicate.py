import replicate
import logging
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_IMAGE_URL = "https://placehold.co/768x768?text=Comic+News"

def validate_api_key(api_token):
    if not api_token or api_token == "test":
        logger.warning("Replicate API key is not configured, using default image")
        return False
    return True

def generate_image(summary):
    api_token = current_app.config['REPLICATE_API_KEY']
    
    if not validate_api_key(api_token):
        return DEFAULT_IMAGE_URL
    
    try:
        logger.info("Generating image using Replicate API")
        client = replicate.Client(api_token=api_token)
        
        output = client.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": summary,
                "negative_prompt": "text, watermark, low quality, blurry",
                "width": 768,
                "height": 768,
            }
        )
        
        if not output:
            logger.warning("No image was generated, using default image")
            return DEFAULT_IMAGE_URL
            
        logger.info("Successfully generated image")
        return output[0]
        
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}")
        return DEFAULT_IMAGE_URL
    except Exception as e:
        logger.error(f"Unexpected error in generate_image: {str(e)}")
        return DEFAULT_IMAGE_URL
