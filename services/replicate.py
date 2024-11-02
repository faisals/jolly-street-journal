import replicate
import logging
import json
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_IMAGE_URL = "https://placehold.co/768x768?text=Comic+News"
DEFAULT_IMAGE_URLS = [DEFAULT_IMAGE_URL] * 4  # Updated to 4 images
DEFAULT_PROMPTS = ["No prompt available"] * 4  # Updated to 4 prompts

def validate_api_key(api_token):
    if not api_token or api_token == "test":
        logger.warning("Replicate API key is not configured, using default image")
        return False
    return True

def generate_images(summary, prompts=None):
    """Generate images using Replicate API with detailed logging"""
    api_token = current_app.config['REPLICATE_API_KEY']
    
    if not validate_api_key(api_token):
        logger.info("Using default images due to missing API key")
        return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)
    
    try:
        logger.info("Starting image generation process using Replicate API")
        client = replicate.Client(api_token=api_token)
        
        # Use provided prompts or generate default styles
        if not prompts or len(prompts) < 4:  # Updated to check for 4 prompts
            prompts = [
                f"{summary} in the style of garfield-strip with vibrant colors",
                f"{summary} in the style of garfield-strip with dramatic lighting",
                f"{summary} in the style of garfield-strip with dynamic composition",
                f"{summary} in the style of garfield-strip with cinematic framing"
            ]
            logger.info("Using default prompt styles as no custom prompts provided")
        
        logger.info("Generated prompts for image creation:")
        for idx, prompt in enumerate(prompts[:4], 1):  # Updated to use 4 prompts
            logger.info(f"Prompt {idx}: {prompt}")
        
        model_params = {
            "prompt": None,  # Will be set in loop
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
        logger.info(f"Using model parameters: {json.dumps(model_params, indent=2)}")
        
        image_urls = []
        for idx, prompt in enumerate(prompts[:4]):  # Updated to generate 4 images
            logger.info(f"Generating image {idx + 1}/4 with prompt: {prompt}")
            
            model_params["prompt"] = prompt
            output = client.run(
                "faisals/jolly-street-journal:41ff8cf9e035e0837c5a8b1b58bee6b8b5a11d9193914d085ada970484831a27",
                input=model_params
            )
            
            if output and isinstance(output, list) and output[0]:
                image_url = str(output[0])
                logger.info(f"Successfully generated image {idx + 1}, URL: {image_url}")
                image_urls.append(image_url)
            else:
                logger.warning(f"Failed to generate image {idx + 1}, using default image")
                image_urls.append(DEFAULT_IMAGE_URL)
        
        if not all(image_urls):
            logger.warning("Some images failed to generate, returning default images")
            return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)
            
        logger.info(f"Successfully generated all {len(image_urls)} images")
        return json.dumps(image_urls), json.dumps(prompts[:4])  # Updated to return 4 prompts
        
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}")
        if "Unauthenticated" in str(e):
            logger.error("Authentication failed - invalid API token")
        else:
            logger.error(f"API Error details: {str(e)}")
        return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)
    except Exception as e:
        logger.error(f"Unexpected error in generate_images: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)
