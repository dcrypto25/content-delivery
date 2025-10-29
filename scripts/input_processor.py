#!/usr/bin/env python3
"""
TRAINERAPP.AI - Input Processor
Process user inputs: images/videos + descriptions → Generate content variations
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from utils import (
    Config,
    FileManager,
    setup_logging,
    console,
)

from generators.prompt_generator import PromptGenerator

logger = setup_logging("input_processor")


class InputProcessor:
    """
    Process user inputs to generate content
    Supports: images, videos, URLs, text descriptions
    """

    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()
        self.prompt_generator = PromptGenerator()

    def process_input(
        self,
        input_path: Optional[str] = None,
        input_url: Optional[str] = None,
        description: str = "",
        style: str = "similar",
        quantity: int = 10,
        variations: Optional[List[str]] = None,
        theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process input and generate content brief

        Args:
            input_path: Path to local image/video
            input_url: URL to image/video
            description: User description of desired output
            style: How to use input (similar/opposite/inspired_by)
            quantity: Number of variations to generate
            variations: Specific variation instructions
            theme: Override detected theme

        Returns:
            Content brief with prompts and metadata
        """

        console.print(f"\n[cyan]📥 Processing Input[/cyan]\n")

        # Step 1: Get the input file
        input_file = self._get_input_file(input_path, input_url)

        # Step 2: Analyze with Vision AI
        console.print("[cyan]🔍 Analyzing input with AI...[/cyan]")
        vision_analysis = self.prompt_generator.analyze_input_with_vision(input_file)

        # Step 3: Merge with user description
        console.print("[cyan]✍️  Processing your description...[/cyan]")
        content_brief = self._create_content_brief(
            vision_analysis=vision_analysis,
            user_description=description,
            style=style,
            variations=variations,
            theme=theme
        )

        # Step 4: Generate prompts
        console.print(f"\n[cyan]🎨 Generating {quantity} content variations...[/cyan]")
        prompts = self._generate_content_prompts(
            content_brief=content_brief,
            quantity=quantity
        )

        # Step 5: Save everything
        output = {
            'input_file': str(input_file),
            'user_description': description,
            'style': style,
            'vision_analysis': vision_analysis,
            'content_brief': content_brief,
            'prompts': prompts,
            'quantity': len(prompts),
            'timestamp': datetime.now().isoformat()
        }

        self._save_output(output)

        console.print(f"\n[green]✓ Generated {len(prompts)} content variations[/green]")

        return output

    def _get_input_file(
        self,
        input_path: Optional[str],
        input_url: Optional[str]
    ) -> str:
        """Get input file (download if URL)"""

        if input_path and os.path.exists(input_path):
            return input_path

        elif input_url:
            console.print(f"[cyan]⬇️  Downloading from URL...[/cyan]")
            return self._download_from_url(input_url)

        else:
            raise ValueError("Must provide either input_path or input_url")

    def _download_from_url(self, url: str) -> str:
        """Download file from URL"""

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Determine file extension
        content_type = response.headers.get('content-type', '')
        if 'image' in content_type:
            ext = 'jpg'
        elif 'video' in content_type:
            ext = 'mp4'
        else:
            ext = 'jpg'  # Default

        # Save to raw_inputs
        filename = f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        save_path = self.file_manager.storage_path / "raw_inputs" / filename

        save_path.write_bytes(response.content)

        logger.info(f"✓ Downloaded to {save_path}")
        return str(save_path)

    def _create_content_brief(
        self,
        vision_analysis: Dict[str, Any],
        user_description: str,
        style: str,
        variations: Optional[List[str]],
        theme: Optional[str]
    ) -> Dict[str, Any]:
        """Create comprehensive content brief"""

        # Use GPT to merge vision analysis + user description
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        prompt = f"""You are a creative director for fitness content.

INPUT ANALYSIS (from image):
{json.dumps(vision_analysis, indent=2)}

USER DESCRIPTION:
"{user_description}"

STYLE DIRECTION: {style}
- similar: Create content similar to the input
- opposite: Create contrasting content
- inspired_by: Use input as inspiration but make it unique

VARIATIONS REQUESTED: {variations or 'None specified'}

Create a detailed content brief that merges the visual analysis with the user's description.

Include:
1. Core message/theme
2. Visual style to replicate or contrast
3. Key elements to include/exclude
4. Target audience insights
5. Emotional tone
6. Specific content angles to explore
7. Technical specifications (lighting, composition, etc.)

Return as JSON:
{{
  "core_message": "...",
  "visual_style": "...",
  "key_elements": ["...", "..."],
  "elements_to_avoid": ["...", "..."],
  "target_audience": "...",
  "emotional_tone": "...",
  "content_angles": ["...", "..."],
  "technical_specs": {{}},
  "theme": "workout/nutrition/motivation/app_features"
}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative director for fitness marketing content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        brief = json.loads(response.choices[0].message.content)

        # Override theme if specified
        if theme:
            brief['theme'] = theme

        return brief

    def _generate_content_prompts(
        self,
        content_brief: Dict[str, Any],
        quantity: int
    ) -> List[Dict[str, Any]]:
        """Generate prompts based on content brief"""

        # Enhanced prompt generation using the content brief
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        system_prompt = f"""You are an expert at creating diverse, engaging fitness content prompts.

CONTENT BRIEF:
{json.dumps(content_brief, indent=2)}

Generate {quantity} unique, specific prompts for image/video generation.

Each prompt should:
1. Align with the core message and visual style
2. Include specific details (person description, action, setting, lighting)
3. Incorporate key elements from the brief
4. Avoid elements marked to avoid
5. Match the emotional tone
6. Be diverse (different people, locations, times of day)
7. Include TrainerApp.AI integration naturally
8. Add motivational text overlay

Return as JSON array:
[{{
  "prompt": "detailed generation prompt",
  "variant_id": "001",
  "content_angle": "which angle from brief",
  "diversity_attributes": {{"body_type": "", "ethnicity": "", "age_range": "", "gender": ""}},
  "platform": "instagram/tiktok/both",
  "estimated_virality": "low/medium/high",
  "tags": ["tag1", "tag2"],
  "text_overlay": "motivational text to display"
}}]
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate {quantity} prompts now."}
            ],
            max_tokens=4000,
            temperature=0.9,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        prompts = result.get('prompts', [])

        # Enhance each prompt
        for i, prompt_obj in enumerate(prompts):
            prompt_obj['variant_id'] = f"{content_brief.get('theme', 'gen')[:3]}_{i+1:03d}"
            prompt_obj['theme'] = content_brief.get('theme', 'workout')
            prompt_obj['content_type'] = 'image'  # Can be 'video' later

        return prompts

    def _save_output(self, output: Dict[str, Any]):
        """Save processed output"""

        output_dir = self.file_manager.storage_path / "metadata"
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"input_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file = output_dir / filename

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        logger.info(f"✓ Saved to {output_file}")


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface"""

    parser = argparse.ArgumentParser(
        description="TrainerApp.AI Input Processor - Turn any input into content variations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Analyze competitor ad and create variations
  python input_processor.py \\
    --input competitor_ad.jpg \\
    --description "Create similar ads but featuring our AI coach technology" \\
    --quantity 20

  # Analyze website feature screenshot
  python input_processor.py \\
    --input website_feature.png \\
    --description "Show this workout tracking feature in real gym settings with diverse people" \\
    --style inspired_by \\
    --quantity 50

  # From URL
  python input_processor.py \\
    --url "https://example.com/ad.jpg" \\
    --description "Make it more modern and tech-focused" \\
    --quantity 30

  # Opposite style
  python input_processor.py \\
    --input dark_moody_ad.jpg \\
    --description "Bright, energetic, morning workout vibes" \\
    --style opposite \\
    --quantity 25

  # Specific variations
  python input_processor.py \\
    --input basic_gym.jpg \\
    --description "Home workout versions of this" \\
    --variations "outdoor park" "hotel room" "office break room" \\
    --quantity 15
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', type=str, help='Path to input image/video')
    input_group.add_argument('--url', type=str, help='URL to input image/video')

    # Description
    parser.add_argument('--description', type=str, required=True,
                       help='Describe what you want the output to look like')

    # Style
    parser.add_argument('--style', type=str, default='similar',
                       choices=['similar', 'opposite', 'inspired_by'],
                       help='How to use the input (default: similar)')

    # Quantity
    parser.add_argument('--quantity', type=int, default=10,
                       help='Number of variations to generate (default: 10)')

    # Optional variations
    parser.add_argument('--variations', nargs='+',
                       help='Specific variations to create (e.g., "outdoor" "home" "gym")')

    # Theme override
    parser.add_argument('--theme', type=str,
                       choices=['workout', 'nutrition', 'motivation', 'app_features'],
                       help='Override auto-detected theme')

    # Output
    parser.add_argument('--output', type=str,
                       help='Output file for prompts (default: auto-generated)')

    # Generate immediately
    parser.add_argument('--generate', action='store_true',
                       help='Generate images immediately (otherwise just create prompts)')

    args = parser.parse_args()

    # Process input
    processor = InputProcessor()

    output = processor.process_input(
        input_path=args.input,
        input_url=args.url,
        description=args.description,
        style=args.style,
        quantity=args.quantity,
        variations=args.variations,
        theme=args.theme
    )

    # Display summary
    console.print("\n[bold cyan]📋 Content Brief Summary[/bold cyan]\n")
    console.print(f"Core Message: {output['content_brief'].get('core_message')}")
    console.print(f"Theme: {output['content_brief'].get('theme')}")
    console.print(f"Target Audience: {output['content_brief'].get('target_audience')}")
    console.print(f"Emotional Tone: {output['content_brief'].get('emotional_tone')}")

    console.print(f"\n[bold]Generated {len(output['prompts'])} Prompts:[/bold]\n")
    for i, prompt in enumerate(output['prompts'][:3], 1):
        console.print(f"{i}. [yellow]{prompt['variant_id']}[/yellow]")
        console.print(f"   {prompt['prompt'][:150]}...")
        console.print(f"   Platform: {prompt.get('platform', 'both')} | Virality: {prompt.get('estimated_virality', 'medium')}\n")

    # Generate images if requested
    if args.generate:
        console.print("\n[cyan]🎨 Generating images...[/cyan]\n")

        from generators.image_generator import ImageGenerator

        generator = ImageGenerator(provider='replicate_dev')

        generated_paths = generator.generate_batch(output['prompts'])

        console.print(f"\n[green]✓ Generated {len(generated_paths)} images[/green]")
        console.print(f"Location: storage/generated/images/")

        # Open folder
        os.system(f"open {generator.file_manager.storage_path / 'generated' / 'images'}")

    else:
        console.print(f"\n[yellow]💡 Tip: Add --generate to create images immediately[/yellow]")
        console.print(f"\nOr run:")
        console.print(f"  python scripts/orchestrator.py --batch {output['prompts'][0].get('variant_id', 'latest')}")


if __name__ == "__main__":
    main()
