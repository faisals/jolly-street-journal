import replicate
import logging
import json
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_IMAGE_URL = "https://placehold.co/768x768?text=Comic+News"
DEFAULT_IMAGE_URLS = [DEFAULT_IMAGE_URL] * 3

def validate_api_key(api_token):
    if not api_token or api_token == "test":
        logger.warning("Replicate API key is not configured, using default image")
        return False
    return True

def generate_images(summary):
    api_token = current_app.config['REPLICATE_API_KEY']
    
    if not validate_api_key(api_token):
        return json.dumps(DEFAULT_IMAGE_URLS)
    
    try:
        logger.info("Generating images using Replicate API")
        client = replicate.Client(api_token=api_token)
        
        # Generate three different styles of images
        styles = [
            "in the style of garfield-strip with vibrant colors",
            "in the style of garfield-strip with dramatic lighting",
            "in the style of garfield-strip with dynamic composition"
        ]
        
        image_urls = []
        for style in styles:
            output = client.run(
                "faisals/jolly-street-journal:41ff8cf9e035e0837c5a8b1b58bee6b8b5a11d9193914d085ada970484831a27",
                input={
                    "prompt": f"{summary} {style}",
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
            
            if output and isinstance(output, list) and output[0]:
                image_urls.append(str(output[0]))
            else:
                image_urls.append(DEFAULT_IMAGE_URL)
        
        logger.info(f"Successfully generated {len(image_urls)} images")
        return json.dumps(image_urls)
        
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}")
        if "Unauthenticated" in str(e):
            logger.error("Authentication failed - invalid API token")
        return json.dumps(DEFAULT_IMAGE_URLS)
    except Exception as e:
        logger.error(f"Unexpected error in generate_images: {str(e)}")
        return json.dumps(DEFAULT_IMAGE_URLS)
