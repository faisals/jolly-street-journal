import replicate
from flask import current_app

def generate_image(summary):
    client = replicate.Client(api_token=current_app.config['REPLICATE_API_KEY'])
    
    try:
        output = client.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": summary,
                "negative_prompt": "text, watermark, low quality, blurry",
                "width": 768,
                "height": 768,
            }
        )
        return output[0] if output else None
    except Exception as e:
        raise Exception(f"Failed to generate image: {str(e)}")
