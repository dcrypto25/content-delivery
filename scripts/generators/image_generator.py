"""
TRAINERAPP.AI - Image Generator
Support for multiple image generation providers with cost optimization
"""

import os
import io
import time
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
from PIL import Image
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Provider imports
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import replicate
except ImportError:
    replicate = None

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    Config,
    FileManager,
    setup_logging,
    console,
    APIRateLimiter,
    PerformanceTracker
)

logger = setup_logging("image_generator")


class ImageGenerator:
    """
    Multi-provider image generator with automatic failover
    Supports: Gemini (Google), Replicate (FLUX), and fallbacks
    """

    PROVIDER_COSTS = {
        'gemini': 0.005,      # $0.005 per image
        'replicate': 0.0055,  # $0.0055 per image (FLUX Schnell)
        'replicate_pro': 0.04, # $0.04 per image (FLUX Pro - PHOTOREALISTIC)
        'replicate_dev': 0.025, # $0.025 per image (FLUX Dev - High quality)
        'stability': 0.02,    # $0.02 per image (if needed)
    }

    def __init__(self, provider: Optional[str] = None):
        self.config = Config()
        self.file_manager = FileManager()
        self.tracker = PerformanceTracker()

        # Determine provider
        profile = self.config.get_active_profile()
        self.provider = provider or profile.get('image_provider', 'gemini')

        logger.info(f"Initializing ImageGenerator with provider: {self.provider}")

        # Initialize provider
        self._init_provider()

        # Rate limiter
        self.rate_limiter = APIRateLimiter(
            calls_per_minute=int(os.getenv('GEMINI_RPM', 60))
        )

    def _init_provider(self):
        """Initialize the selected provider"""

        if self.provider == 'gemini':
            if genai is None:
                raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp'))

            logger.info("✓ Gemini initialized")

        elif self.provider in ['replicate', 'replicate_dev', 'replicate_pro']:
            if replicate is None:
                raise ImportError("replicate not installed. Run: pip install replicate")

            api_token = os.getenv('REPLICATE_API_TOKEN')
            if not api_token:
                raise ValueError("REPLICATE_API_TOKEN not set")

            os.environ['REPLICATE_API_TOKEN'] = api_token

            # Log which quality level
            quality_map = {
                'replicate': 'Fast (Schnell)',
                'replicate_dev': 'High Quality (Dev)',
                'replicate_pro': 'Photorealistic (Pro)'
            }
            logger.info(f"✓ Replicate initialized - {quality_map.get(self.provider, 'Unknown')}")

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_single(
        self,
        prompt: str,
        metadata: Dict[str, Any],
        size: str = "1080x1920"
    ) -> Optional[Path]:
        """
        Generate a single image

        Returns: Path to saved image file
        """

        logger.info(f"Generating image: {metadata.get('variant_id', 'unknown')}")
        self.rate_limiter.wait_if_needed()

        try:
            if self.provider == 'gemini':
                image_data = self._generate_gemini(prompt, size)
            elif self.provider in ['replicate', 'replicate_dev', 'replicate_pro']:
                image_data = self._generate_replicate(prompt, size)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            # Save image
            if image_data:
                path = self.file_manager.save_generated_asset(
                    content=image_data,
                    asset_type='image',
                    metadata={
                        **metadata,
                        'provider': self.provider,
                        'size': size,
                        'prompt': prompt
                    }
                )

                # Track performance
                cost = self.PROVIDER_COSTS.get(self.provider, 0)
                self.tracker.log_generation('image', cost)

                return path

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            self.tracker.log_error()
            raise

        return None

    def _generate_gemini(self, prompt: str, size: str) -> bytes:
        """Generate image using Gemini (Imagen via Generative AI SDK)"""

        # Note: As of early 2025, Gemini doesn't directly generate images via the generativeai SDK
        # This is a placeholder for when image generation is available
        # For now, we'll use Imagen 2 via Vertex AI

        logger.warning("Gemini image generation via SDK not yet available. Use Vertex AI or switch to Replicate.")

        # Fallback to Replicate
        return self._generate_replicate(prompt, size)

    def _generate_replicate(self, prompt: str, size: str) -> bytes:
        """Generate image using Replicate (FLUX models)"""

        # Parse size
        width, height = map(int, size.split('x'))

        # Determine which FLUX model to use based on provider setting
        model_map = {
            'replicate': 'black-forest-labs/flux-schnell',      # Fast, cheap
            'replicate_dev': 'black-forest-labs/flux-dev',      # High quality
            'replicate_pro': 'black-forest-labs/flux-1.1-pro'   # PHOTOREALISTIC
        }

        model = model_map.get(self.provider, 'black-forest-labs/flux-dev')

        # Override with env var if set
        if os.getenv('REPLICATE_IMAGE_MODEL'):
            model = os.getenv('REPLICATE_IMAGE_MODEL')

        logger.info(f"Calling Replicate: {model}")

        # Enhance prompt for photorealism
        enhanced_prompt = self._enhance_prompt_for_realism(prompt)

        # Model-specific parameters
        if 'schnell' in model:
            # Fast model (4 steps, no guidance)
            input_params = {
                "prompt": enhanced_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "num_inference_steps": 4,
                "output_format": "jpg",
                "output_quality": 95
            }
        elif 'pro' in model:
            # Pro model (best quality)
            input_params = {
                "prompt": enhanced_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "output_format": "jpg",
                "output_quality": 95,
                "safety_tolerance": 2,  # Less restrictive for fitness content
                "prompt_upsampling": True  # Better prompt understanding
            }
        else:
            # Dev model (balanced)
            input_params = {
                "prompt": enhanced_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "num_inference_steps": 28,  # More steps = better quality
                "guidance_scale": 3.5,      # Moderate guidance
                "output_format": "jpg",
                "output_quality": 95
            }

        output = replicate.run(model, input=input_params)

        # Download image
        if output and len(output) > 0:
            image_url = output[0]
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            return response.content

        raise Exception("No output from Replicate")

    def _enhance_prompt_for_realism(self, prompt: str) -> str:
        """Enhance prompt with photorealism keywords"""

        # Keywords that dramatically improve realism
        realism_keywords = [
            "photorealistic",
            "shot on Canon EOS R5",
            "85mm f/1.4 lens",
            "natural skin texture",
            "real photography",
            "ultra detailed",
            "sharp focus",
            "studio lighting",
            "professional photography",
            "8K resolution",
            "lifelike",
            "highly detailed facial features"
        ]

        # Check if prompt already has realism keywords
        if not any(kw.lower() in prompt.lower() for kw in ["photorealistic", "photography", "canon", "shot on"]):
            # Add photorealism prefix
            prompt = f"Professional photorealistic photography, shot on Canon EOS R5, 85mm lens: {prompt}"

        # Add natural skin texture emphasis for people
        if any(word in prompt.lower() for word in ["person", "woman", "man", "athlete", "people", "trainer"]):
            if "skin" not in prompt.lower():
                prompt = f"{prompt}, natural skin texture, realistic pores and details"

        # Ensure we specify NOT to be digital art/illustration
        if "not" not in prompt.lower():
            prompt = f"{prompt}, NOT digital art, NOT illustration, NOT painting, NOT anime"

        return prompt

    def generate_batch(
        self,
        prompts: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Path]:
        """
        Generate a batch of images with rate limiting

        Returns: List of paths to saved images
        """

        logger.info(f"Starting batch generation: {len(prompts)} images")
        console.print(f"\n[cyan]🎨 Generating {len(prompts)} images with {self.provider}...[/cyan]\n")

        generated_paths = []

        from tqdm import tqdm

        for prompt_obj in tqdm(prompts, desc="Generating images"):
            try:
                # Determine size based on platform
                platform = prompt_obj.get('platform', 'instagram')
                size = "1080x1920" if platform in ['tiktok', 'reels'] else "1080x1080"

                path = self.generate_single(
                    prompt=prompt_obj['prompt'],
                    metadata=prompt_obj,
                    size=size
                )

                if path:
                    generated_paths.append(path)

                    # Apply post-processing
                    self._apply_enhancements(path, prompt_obj)

            except Exception as e:
                logger.error(f"Failed to generate {prompt_obj.get('variant_id')}: {str(e)}")
                continue

        # Print summary
        self.tracker.print_summary()

        return generated_paths

    def _apply_enhancements(self, image_path: Path, metadata: Dict[str, Any]):
        """Apply watermark, text overlay, filters"""

        try:
            img = Image.open(image_path)

            # 1. Add watermark
            if os.getenv('WATERMARK_ENABLED', 'true').lower() == 'true':
                img = self._add_watermark(img)

            # 2. Apply filters (optional)
            img = self._apply_filters(img)

            # Save enhanced image
            img.save(image_path, quality=int(os.getenv('IMAGE_QUALITY', 90)))

            logger.info(f"✓ Enhanced: {image_path.name}")

        except Exception as e:
            logger.error(f"Enhancement failed: {str(e)}")

    def _add_watermark(self, img: Image.Image) -> Image.Image:
        """Add watermark to image"""

        from PIL import ImageDraw, ImageFont

        # Create watermark
        draw = ImageDraw.Draw(img)

        # Simple text watermark (can be replaced with logo)
        watermark_text = "trainerapp.ai"

        # Position
        width, height = img.size
        opacity = int(255 * float(os.getenv('WATERMARK_OPACITY', 0.15)))

        # Draw text (simplified - you'd want to load a proper font)
        position = (width - 200, height - 50)

        try:
            # Try to use a nice font
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()

        draw.text(position, watermark_text, fill=(255, 255, 255, opacity), font=font)

        return img

    def _apply_filters(self, img: Image.Image) -> Image.Image:
        """Apply Instagram-style filters"""

        from PIL import ImageEnhance

        # Subtle enhancements
        brightness = float(os.getenv('IMAGE_BRIGHTNESS', 1.1))
        contrast = float(os.getenv('IMAGE_CONTRAST', 1.15))
        saturation = float(os.getenv('IMAGE_SATURATION', 1.1))

        # Apply
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Color(img).enhance(saturation)

        return img


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface for testing"""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="TrainerApp.AI Image Generator")
    parser.add_argument('--provider', type=str,
                       choices=['gemini', 'replicate', 'replicate_dev', 'replicate_pro'],
                       help='Generation provider (replicate_dev=best quality, replicate_pro=photorealistic)')
    parser.add_argument('--prompt', type=str, help='Single prompt to generate')
    parser.add_argument('--batch', type=str, help='Path to JSON file with prompts')
    parser.add_argument('--size', type=str, default='1080x1920', help='Image size')

    args = parser.parse_args()

    generator = ImageGenerator(provider=args.provider)

    if args.prompt:
        # Single generation
        console.print(f"\n[cyan]🎨 Generating single image...[/cyan]")

        path = generator.generate_single(
            prompt=args.prompt,
            metadata={'variant_id': 'test_001', 'theme': 'test'},
            size=args.size
        )

        console.print(f"[green]✓[/green] Generated: {path}")

    elif args.batch:
        # Batch generation
        with open(args.batch, 'r') as f:
            data = json.load(f)
            prompts = data.get('prompts', [])

        paths = generator.generate_batch(prompts)

        console.print(f"\n[green]✓[/green] Generated {len(paths)} images")

    else:
        console.print("[red]Error:[/red] Provide either --prompt or --batch")


if __name__ == "__main__":
    main()
