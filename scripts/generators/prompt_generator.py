"""
TRAINERAPP.AI - Prompt Generator
Generate diverse, high-quality prompts for image and video generation
"""

import os
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    Config,
    setup_logging,
    console,
    APIRateLimiter,
    generate_utm_link
)

logger = setup_logging("prompt_generator")


class PromptGenerator:
    """
    Generate prompts for image and video generation
    Uses GPT-4o-mini for cost-effective prompt engineering
    """

    def __init__(self):
        self.config = Config()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.rate_limiter = APIRateLimiter(calls_per_minute=60)

        # Load templates from config
        self.image_template = self.config.get('prompts.image_generation.base_template')
        self.video_template = self.config.get('prompts.video_generation.base_template')
        self.themes = self.config.get('themes', {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def analyze_input_with_vision(self, image_path: str) -> Dict[str, Any]:
        """
        Use GPT-4o Vision to analyze input image
        Returns structured analysis for prompt generation
        """

        logger.info(f"Analyzing image with GPT-4o Vision: {image_path}")
        self.rate_limiter.wait_if_needed()

        # Read and encode image
        import base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_VISION_MODEL', 'gpt-4o'),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this fitness/health image in detail. Return a JSON with:
                            - scene: physical environment description
                            - subject: person(s) description (body type, ethnicity, gender, age, clothing)
                            - action: what they're doing
                            - emotion: mood/energy level
                            - ui_elements: any app interface elements visible
                            - text_overlay: any text visible
                            - lighting: lighting style/quality
                            - colors: dominant colors
                            - style: photography/art style
                            - fitness_category: workout/nutrition/motivation/tech

                            Be specific and detailed. Focus on elements that can be replicated."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        analysis = json.loads(response.choices[0].message.content)
        logger.info("✓ Vision analysis complete")

        return analysis

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_batch_prompts(
        self,
        base_analysis: Optional[Dict[str, Any]] = None,
        theme: str = "workout",
        quantity: int = 100,
        content_type: str = "image"  # 'image' or 'video'
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of diverse prompts based on analysis or theme

        Returns list of prompt objects with metadata
        """

        logger.info(f"Generating {quantity} {content_type} prompts for theme: {theme}")
        self.rate_limiter.wait_if_needed()

        # Build context from theme
        theme_config = self.themes.get(theme, {})
        keywords = theme_config.get('keywords', [])
        colors = theme_config.get('colors', [])

        # Prepare prompt for GPT
        system_prompt = f"""You are an expert at creating diverse, engaging fitness content prompts.

Theme: {theme}
Keywords: {', '.join(keywords)}
Brand: TrainerApp.AI - AI-powered personal training app

Generate {quantity} unique prompts for {content_type} generation that will perform well on Instagram Reels and TikTok.

Requirements:
1. DIVERSE representation (body types, ethnicities, ages, genders)
2. Mix of locations (gym, home, outdoor, studio)
3. Various times of day and lighting
4. Include app UI integration naturally
5. Add motivational text overlays
6. Vary angles and perspectives
7. Include specific fitness activities
8. Make content relatable and aspirational
9. Each prompt should stand alone as unique content

Return as JSON array with this structure:
[{{
  "prompt": "detailed generation prompt",
  "variant_id": "001",
  "theme": "{theme}",
  "tags": ["tag1", "tag2"],
  "platform": "both/instagram/tiktok",
  "estimated_virality": "low/medium/high",
  "diversity_attributes": {{"body_type": "", "ethnicity": "", "age_range": "", "gender": ""}},
  "location": "",
  "time_of_day": "",
  "energy_level": "low/medium/high"
}}]
"""

        user_prompt = ""
        if base_analysis:
            user_prompt = f"""Base this batch on this reference content:
{json.dumps(base_analysis, indent=2)}

Create {quantity} variations that maintain the core appeal while introducing diversity and variety."""
        else:
            user_prompt = f"Create {quantity} original prompts for {theme} theme fitness content."

        # Call GPT-4o-mini (cheap and fast)
        response = self.client.chat.completions.create(
            model=os.getenv('OPENAI_PROMPT_MODEL', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 4000)),
            temperature=0.9,  # High creativity
            response_format={"type": "json_object"}
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)
        prompts = result.get('prompts', [])

        # Enhance each prompt with additional metadata
        for i, prompt_obj in enumerate(prompts):
            prompt_obj['variant_id'] = f"{theme[:3]}_{i+1:03d}"
            prompt_obj['utm_link'] = generate_utm_link(
                source="tiktok" if prompt_obj.get('platform') == 'tiktok' else "instagram",
                campaign=f"{theme}_auto"
            )

            # Add content-type specific enhancements
            if content_type == "image":
                prompt_obj = self._enhance_image_prompt(prompt_obj)
            else:
                prompt_obj = self._enhance_video_prompt(prompt_obj)

        logger.info(f"✓ Generated {len(prompts)} prompts")
        return prompts

    def _enhance_image_prompt(self, prompt_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Add image-specific enhancements to prompt"""

        styles = self.config.get('prompts.image_generation.style_variations', [])
        locations = self.config.get('prompts.image_generation.locations', [])

        # Add random style if not specified
        if 'style' not in prompt_obj['prompt'].lower():
            style = random.choice(styles)
            prompt_obj['prompt'] = f"{style}: {prompt_obj['prompt']}"

        # Ensure technical quality keywords
        quality_keywords = [
            "high resolution",
            "professional photography",
            "sharp focus",
            "Instagram-worthy",
            "cinematic lighting"
        ]

        # Add if missing
        if not any(kw in prompt_obj['prompt'].lower() for kw in ['quality', 'resolution', 'professional']):
            prompt_obj['prompt'] += f", {random.choice(quality_keywords)}"

        # Add app integration if not present
        if 'trainerapp' not in prompt_obj['prompt'].lower():
            app_elements = [
                "phone screen showing TrainerApp.AI interface in background",
                "TrainerApp.AI logo subtly visible on equipment",
                "person checking TrainerApp.AI on smartwatch",
                "app interface overlay showing workout stats"
            ]
            prompt_obj['prompt'] += f", {random.choice(app_elements)}"

        return prompt_obj

    def _enhance_video_prompt(self, prompt_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Add video-specific enhancements to prompt"""

        camera_movements = self.config.get('prompts.video_generation.camera_movements', [])
        app_ui_elements = self.config.get('prompts.video_generation.app_ui_elements', [])

        # Add duration if not specified
        if 'second' not in prompt_obj['prompt']:
            duration = random.choice([15, 20, 30])
            prompt_obj['prompt'] = f"{duration} second vertical video: {prompt_obj['prompt']}"

        # Add camera movement
        if not any(move in prompt_obj['prompt'].lower() for move in ['zoom', 'pan', 'tracking']):
            movement = random.choice(camera_movements)
            prompt_obj['prompt'] += f", {movement}"

        # Add app UI element
        ui_element = random.choice(app_ui_elements)
        prompt_obj['prompt'] += f", {ui_element}"

        # Add ending
        endings = [
            "end with TrainerApp.AI logo",
            "final frame shows QR code to trainerapp.ai",
            "fade to black with text 'Download TrainerApp.AI'",
            "end with app download call-to-action"
        ]
        prompt_obj['prompt'] += f", {random.choice(endings)}"

        return prompt_obj

    def generate_caption_variants(
        self,
        prompt_metadata: Dict[str, Any],
        num_variants: int = 3,
        platform: str = "instagram"
    ) -> List[str]:
        """
        Generate caption variants for a piece of content

        Returns list of caption strings
        """

        logger.info(f"Generating {num_variants} caption variants for {platform}")
        self.rate_limiter.wait_if_needed()

        platform_config = self.config.get(f'platforms.{platform}')
        caption_config = platform_config.get('captions', {})

        max_length = caption_config.get('max_length', 2200)
        hashtag_range = caption_config.get('hashtag_count', [10, 20])
        emoji_density = caption_config.get('emoji_density', 'medium')

        system_prompt = f"""You are a social media expert specializing in {platform} fitness content.

Create {num_variants} caption variants that will drive engagement and conversions.

Platform: {platform}
Max length: {max_length} characters
Hashtags: {hashtag_range[0]}-{hashtag_range[1]}
Emoji density: {emoji_density}

Content metadata:
{json.dumps(prompt_metadata, indent=2)}

Requirements:
1. Strong hook in first line
2. Relatable story or insight
3. Include specific fitness advice
4. Natural product integration (TrainerApp.AI)
5. Clear call-to-action
6. Strategic hashtag placement
7. Appropriate emoji usage
8. Authentic voice (not salesy)

Return as JSON:
{{"captions": ["caption1", "caption2", "caption3"]}}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate the captions now."}
            ],
            max_tokens=2000,
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        captions = result.get('captions', [])

        logger.info(f"✓ Generated {len(captions)} caption variants")
        return captions

    def save_prompts_batch(self, prompts: List[Dict[str, Any]], filename: str = "prompts_batch.json"):
        """Save generated prompts to file"""

        output_dir = Path(__file__).parent.parent.parent / "storage" / "metadata"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            json.dump({
                'generated_at': json.dumps(prompts, indent=2),
                'count': len(prompts),
                'prompts': prompts
            }, f, indent=2)

        console.print(f"[green]✓[/green] Saved {len(prompts)} prompts to {output_path}")

        return output_path


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface for testing"""

    import argparse

    parser = argparse.ArgumentParser(description="TrainerApp.AI Prompt Generator")
    parser.add_argument('--theme', type=str, default='workout', help='Content theme')
    parser.add_argument('--quantity', type=int, default=10, help='Number of prompts')
    parser.add_argument('--type', type=str, default='image', choices=['image', 'video'])
    parser.add_argument('--analyze', type=str, help='Path to image to analyze first')

    args = parser.parse_args()

    generator = PromptGenerator()

    base_analysis = None
    if args.analyze:
        console.print(f"\n[cyan]📸 Analyzing input image...[/cyan]")
        base_analysis = generator.analyze_input_with_vision(args.analyze)
        console.print(json.dumps(base_analysis, indent=2))

    console.print(f"\n[cyan]🎨 Generating {args.quantity} {args.type} prompts...[/cyan]")

    prompts = generator.generate_batch_prompts(
        base_analysis=base_analysis,
        theme=args.theme,
        quantity=args.quantity,
        content_type=args.type
    )

    # Print first 3 examples
    console.print("\n[bold]Sample Prompts:[/bold]")
    for i, prompt in enumerate(prompts[:3], 1):
        console.print(f"\n{i}. [yellow]{prompt['variant_id']}[/yellow]")
        console.print(f"   {prompt['prompt'][:200]}...")

    # Save all
    generator.save_prompts_batch(prompts, f"{args.theme}_{args.type}_prompts.json")


if __name__ == "__main__":
    main()
