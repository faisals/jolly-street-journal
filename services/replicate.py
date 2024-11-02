import replicate
import logging
import json
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_IMAGE_URL = "https://placehold.co/768x768?text=Comic+News"
DEFAULT_IMAGE_URLS = [DEFAULT_IMAGE_URL] * 4
DEFAULT_PROMPTS = ["No prompt available"] * 4

def validate_api_key(api_token):
    if not api_token or api_token == "test":
        logger.warning("Replicate API key is not configured, using default image")
        return False
    return True

def extract_prompts(summary):
    """Extract image prompts from the summary text"""
    prompts = []
    for i in range(1, 5):
        tag = f'<image_prompt{i}>'
        end_tag = f'</image_prompt{i}>'
        start = summary.find(tag) + len(tag)
        end = summary.find(end_tag)
        if start > -1 and end > -1:
            prompt = summary[start:end].strip()
            logger.info(f"Extracted prompt {i}: {prompt}")
            prompts.append(prompt)
        else:
            logger.warning(f"Could not find prompt {i} in summary")
    return prompts

def generate_images(summary, prompts=None):
    """Generate images using Replicate API with detailed logging"""
    api_token = current_app.config['REPLICATE_API_KEY']

    if not validate_api_key(api_token):
        logger.info("Using default images due to missing API key")
        return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)

    try:
        logger.info("Starting image generation process using Replicate API")
        client = replicate.Client(api_token=api_token)

        # Extract prompts from summary if not provided
        if not prompts:
            extracted_prompts = extract_prompts(summary)
            if len(extracted_prompts) == 4:
                prompts = extracted_prompts
                logger.info("Successfully extracted all 4 prompts from summary")
            else:
                logger.warning(f"Found only {len(extracted_prompts)} prompts, using default prompts")
                prompts = [
                    f"{summary} in the style of garfield-strip with vibrant colors",
                    f"{summary} in the style of garfield-strip with dramatic lighting",
                    f"{summary} in the style of garfield-strip with dynamic composition",
                    f"{summary} in the style of garfield-strip with cinematic framing"
                ]

        model_params = {
            "prompt": None,  # Will be set in loop
            "model": "dev",
            "lora_scale": 0.7,
            "num_outputs": 1,
            "aspect_ratio": "16:9",
            "output_format": "webp",
            "guidance_scale": 5,
            "output_quality": 80,
            "prompt_strength": 0.8,
            "extra_lora_scale": 1,
            "num_inference_steps": 50
        }
        logger.info(f"Using model parameters: {json.dumps(model_params, indent=2)}")

        image_urls = []
        for idx, prompt in enumerate(prompts[:4]):
            logger.info(f"Generating image {idx + 1}/4")
            logger.info(f"Using prompt: {prompt}")

            # Ensure the prompt includes the required style
            if "in the style of garfield-strip" not in prompt.lower():
                prompt = f"{prompt} in the style of garfield-strip"

            model_params["prompt"] = prompt
            output = client.run(
                "pellmellism/xkcd:7e0502efc2a94a6b42f8572bade751196af37e9f4c4e430cd3d5c19c1ed31647",
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
        return json.dumps(image_urls), json.dumps(prompts[:4])

    except Exception as e:
        logger.error(f"Unexpected error in generate_images: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        return json.dumps(DEFAULT_IMAGE_URLS), json.dumps(DEFAULT_PROMPTS)
