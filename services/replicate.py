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
            "faisals/jolly-street-journal:41ff8cf9e035e0837c5a8b1b58bee6b8b5a11d9193914d085ada970484831a27",
            input={
                "prompt": summary,
                "model": "dev",
                "lora_scale": 1,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "guidance_scale": 3.5,
                "output_quality": 90,
                "prompt_strength": 0.8,
                "extra_lora_scale": 1,
                "num_inference_steps": 28
            }
        )
        
        if not output or not isinstance(output, list) or not output[0]:
            logger.warning("No image was generated, using default image")
            return DEFAULT_IMAGE_URL
            
        # Convert FileOutput to string URL
        image_url = str(output[0])
        logger.info("Successfully generated image")
        return image_url
        
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}")
        if "Unauthenticated" in str(e):
            logger.error("Authentication failed - invalid API token")
        return DEFAULT_IMAGE_URL
    except Exception as e:
        logger.error(f"Unexpected error in generate_image: {str(e)}")
        return DEFAULT_IMAGE_URL
