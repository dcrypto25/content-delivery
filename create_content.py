#!/usr/bin/env python3
"""
TRAINERAPP.AI - Simple Content Creator
Easy interface: Input image + description → Generate content
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "scripts"))

from input_processor import InputProcessor
from generators.image_generator import ImageGenerator
from generators.video_generator import VideoGenerator
from utils import console


def main():
    parser = argparse.ArgumentParser(
        description="🚀 TrainerApp.AI Content Creator - Turn any image into unlimited variations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES:

  📸 From Competitor Ad:

    python create_content.py \\
      --input competitor_tiktok.jpg \\
      --what "Create similar workout motivation content but featuring TrainerApp.AI" \\
      --how-many 50

  🖥️  From Website Feature:

    python create_content.py \\
      --input website_screenshot.png \\
      --what "Show this workout tracking feature in real gym environments with real people using phones" \\
      --how-many 30 \\
      --style inspired_by

  🌐 From URL:

    python create_content.py \\
      --url "https://example.com/viral-post.jpg" \\
      --what "Make it more energetic and show diverse body types" \\
      --how-many 20

  🎨 Opposite Style:

    python create_content.py \\
      --input dark_gym_ad.jpg \\
      --what "Bright, outdoor, morning energy vibes" \\
      --style opposite \\
      --how-many 25

  📱 Multiple Variations:

    python create_content.py \\
      --input basic_exercise.jpg \\
      --what "Same exercise in different settings" \\
      --variations "home" "gym" "park" "hotel room" \\
      --how-many 40

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUALITY LEVELS (use --quality):

  fast      - $0.0055/image, 4 seconds   (for testing)
  high      - $0.025/image, 15 seconds   (recommended ⭐)
  premium   - $0.04/image, 20 seconds    (photorealistic)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    )

    # Input
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', type=str,
                            help='📁 Path to input image/video (competitor ad, website screenshot, etc.)')
    input_group.add_argument('--url', '-u', type=str,
                            help='🌐 URL to input image/video')

    # Description (the key part!)
    parser.add_argument('--what', '-w', type=str, required=True,
                       help='✍️  What do you want the output to look like? (be specific!)')

    # Quantity
    parser.add_argument('--how-many', '-n', type=int, default=10,
                       help='🔢 How many variations to create (default: 10)')

    # Style
    parser.add_argument('--style', '-s', type=str, default='similar',
                       choices=['similar', 'opposite', 'inspired_by'],
                       help='🎨 Style direction (default: similar)')

    # Variations
    parser.add_argument('--variations', '-v', nargs='+',
                       help='🔀 Specific variations (e.g., "outdoor" "home" "gym")')

    # Quality
    parser.add_argument('--quality', '-q', type=str, default='high',
                       choices=['fast', 'high', 'premium'],
                       help='⭐ Image quality (default: high)')

    # Theme override
    parser.add_argument('--theme', '-t', type=str,
                       choices=['workout', 'nutrition', 'motivation', 'app_features'],
                       help='🏷️  Override theme detection')

    # Content type
    parser.add_argument('--type', type=str, default='image',
                       choices=['image', 'video', 'both'],
                       help='🎬 Content type to generate (default: image)')

    # Video-specific options
    parser.add_argument('--duration', type=int, default=5,
                       help='⏱️  Video duration in seconds (default: 5)')

    # Skip generation (just create prompts)
    parser.add_argument('--prompts-only', action='store_true',
                       help='📝 Only generate prompts, don\'t create content')

    args = parser.parse_args()

    # Map quality to provider
    quality_map = {
        'fast': 'replicate',
        'high': 'replicate_dev',
        'premium': 'replicate_pro'
    }
    provider = quality_map[args.quality]

    # Welcome message
    console.print("\n[bold cyan]🚀 TrainerApp.AI Content Creator[/bold cyan]")
    console.print("━" * 60 + "\n")

    console.print(f"📥 Input: {args.input or args.url}")
    console.print(f"✍️  Goal: {args.what}")
    console.print(f"🎨 Style: {args.style}")
    console.print(f"🔢 Quantity: {args.how_many}")
    console.print(f"⭐ Quality: {args.quality}")
    console.print("\n" + "━" * 60 + "\n")

    # Step 1: Process input
    console.print("[bold]STEP 1: Processing Input[/bold]")

    processor = InputProcessor()

    output = processor.process_input(
        input_path=args.input,
        input_url=args.url,
        description=args.what,
        style=args.style,
        quantity=args.how_many,
        variations=args.variations,
        theme=args.theme
    )

    # Step 2: Generate content (images and/or videos)
    if not args.prompts_only:
        console.print("\n[bold]STEP 2: Generating Content[/bold]")

        generated_paths = []
        total_cost = 0

        # Generate images
        if args.type in ['image', 'both']:
            console.print(f"\n[cyan]🖼️  Generating images...[/cyan]")

            image_generator = ImageGenerator(provider=provider)
            image_paths = image_generator.generate_batch(output['prompts'])

            generated_paths.extend(image_paths)
            total_cost += len(image_paths) * image_generator.PROVIDER_COSTS.get(provider, 0)

            console.print(f"[green]✓[/green] Generated {len(image_paths)} images")

        # Generate videos
        if args.type in ['video', 'both']:
            console.print(f"\n[cyan]🎬 Generating videos...[/cyan]")
            console.print(f"[yellow]⚠️  Videos take 1-3 minutes each[/yellow]")

            video_generator = VideoGenerator(provider='replicate_minimax')

            # Add duration to prompts
            for prompt in output['prompts']:
                prompt['duration'] = args.duration

            video_paths = video_generator.generate_batch(output['prompts'])

            generated_paths.extend(video_paths)
            total_cost += len(video_paths) * video_generator.PROVIDER_COSTS.get('replicate_minimax', 0) * args.duration

            console.print(f"[green]✓[/green] Generated {len(video_paths)} videos")

        # Print summary
        console.print("\n" + "━" * 60)
        console.print("[bold green]✅ SUCCESS![/bold green]\n")
        console.print(f"📊 Generated: {len(generated_paths)} items")
        console.print(f"💰 Total Cost: ${total_cost:.2f}")
        console.print(f"📁 Location: storage/generated/")

        # Open folder
        import os
        if args.type == 'image':
            folder = image_generator.file_manager.storage_path / 'generated' / 'images'
        elif args.type == 'video':
            folder = video_generator.file_manager.storage_path / 'generated' / 'videos'
        else:  # both
            folder = image_generator.file_manager.storage_path / 'generated'

        os.system(f"open {folder}")

    else:
        console.print("\n" + "━" * 60)
        console.print("[bold yellow]📝 Prompts Generated[/bold yellow]\n")
        console.print(f"Total: {len(output['prompts'])} prompts")
        console.print(f"Saved to: storage/metadata/")
        console.print("\n[cyan]Run again without --prompts-only to generate images[/cyan]")


if __name__ == "__main__":
    main()
