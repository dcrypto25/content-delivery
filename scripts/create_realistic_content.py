#!/usr/bin/env python3
"""
TRAINERAPP.AI - Realistic Content Creator
Uses stock photos + img2img + real UI compositing for production-quality results
"""

import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from stock_photo_fetcher import StockPhotoFetcher
from generators.image_generator import ImageGenerator
from compositing import UICompositor
from utils import console

def main():
    parser = argparse.ArgumentParser(
        description="🎯 Create realistic fitness content using stock photos + real UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES:

  1️⃣  Generate 10 images with your app UI:

    python scripts/create_realistic_content.py \\
      --ui storage/raw_inputs/test_ui.png \\
      --prompt "person doing squats in gym, checking phone for workout progress" \\
      --count 10

  2️⃣  Use specific stock photos as base:

    python scripts/create_realistic_content.py \\
      --ui storage/raw_inputs/test_ui.png \\
      --stock-base storage/stock_photos/pexels_*.jpg \\
      --prompt "athlete reviewing workout stats on phone"

  3️⃣  Different workout types:

    python scripts/create_realistic_content.py \\
      --ui storage/raw_inputs/test_ui.png \\
      --workout deadlift \\
      --count 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUALITY COMPARISON:

  OLD (text-to-image only):
    ❌ AI-looking people
    ❌ Wrong exercises
    ❌ Fake UI text

  NEW (stock + img2img + real UI):
    ✅ Real people from stock photos
    ✅ Correct exercises
    ✅ Your actual app UI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    )

    parser.add_argument('--ui', type=str, required=True,
                       help='Path to your app UI screenshot')

    parser.add_argument('--prompt', type=str,
                       help='Description of desired content')

    parser.add_argument('--count', type=int, default=10,
                       help='Number of variations to create')

    parser.add_argument('--workout', type=str,
                       help='Specific workout type (squat, deadlift, etc.)')

    parser.add_argument('--stock-base', type=str,
                       help='Use specific stock photos as base (glob pattern)')

    parser.add_argument('--quality', type=str, default='high',
                       choices=['fast', 'high', 'premium'],
                       help='Generation quality')

    parser.add_argument('--no-composite', action='store_true',
                       help='Skip UI compositing (just generate images)')

    parser.add_argument('--strength', type=float, default=0.7,
                       help='img2img strength (0.0-1.0, higher=more changes)')

    args = parser.parse_args()

    # Welcome
    console.print("\n[bold cyan]🎯 Realistic Content Creator[/bold cyan]")
    console.print("[dim]Stock Photos + img2img + Real UI = Production Quality[/dim]")
    console.print("━" * 60 + "\n")

    ui_path = Path(args.ui)
    if not ui_path.exists():
        console.print(f"[red]Error:[/red] UI screenshot not found: {ui_path}")
        return

    # Quality mapping
    quality_map = {
        'fast': 'replicate',
        'high': 'replicate_dev',
        'premium': 'replicate_pro'
    }
    provider = quality_map[args.quality]

    # Step 1: Get base stock photos
    console.print("[bold]STEP 1: Getting Base Stock Photos[/bold]")

    stock_photos = []

    if args.stock_base:
        # Use provided stock photos
        import glob
        stock_photos = [Path(p) for p in glob.glob(args.stock_base)]
        console.print(f"[green]✓[/green] Using {len(stock_photos)} provided stock photos")
    else:
        # Fetch from Pexels
        fetcher = StockPhotoFetcher()

        if not fetcher.api_key:
            console.print("[yellow]⚠️  No PEXELS_API_KEY set[/yellow]")
            console.print("Get free key at: https://www.pexels.com/api/")
            console.print("\nFor now, you can:")
            console.print("1. Set PEXELS_API_KEY in .env")
            console.print("2. Or provide stock photos with --stock-base")
            return

        stock_photos = fetcher.fetch_fitness_base_images(
            num_images=args.count,
            workout_type=args.workout
        )

    if not stock_photos:
        console.print("[red]Error:[/red] No stock photos available")
        return

    # Step 2: Generate variations using img2img
    console.print("\n[bold]STEP 2: Generating Variations (img2img)[/bold]")

    generator = ImageGenerator(provider=provider)

    # Build prompt
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = f"person exercising in gym, athletic wear, checking phone with workout app, natural lighting, professional photo"

    generated_images = []

    from tqdm import tqdm

    for i, stock_photo in enumerate(tqdm(stock_photos[:args.count], desc="Creating variations")):
        try:
            result = generator.generate_single(
                prompt=prompt,
                metadata={
                    'variant_id': f'realistic_{i+1:03d}',
                    'theme': 'realistic',
                    'base_photo': stock_photo.name
                },
                base_image=stock_photo,
                strength=args.strength
            )

            if result:
                generated_images.append(result)

        except Exception as e:
            console.print(f"[yellow]⚠️  Failed: {str(e)}[/yellow]")
            continue

    console.print(f"[green]✓[/green] Generated {len(generated_images)} variations")

    # Step 3: Composite real UI onto images
    if not args.no_composite:
        console.print("\n[bold]STEP 3: Compositing Real UI[/bold]")

        compositor = UICompositor()

        final_images = compositor.batch_composite(
            image_paths=generated_images,
            ui_screenshot_path=ui_path,
            position='auto',
            phone_scale=0.25,
            perspective=True
        )

        console.print(f"[green]✓[/green] Composited {len(final_images)} images")
    else:
        final_images = generated_images

    # Summary
    console.print("\n" + "━" * 60)
    console.print("[bold green]✅ SUCCESS![/bold green]\n")
    console.print(f"📊 Created: {len(final_images)} production-ready images")
    console.print(f"📁 Location: storage/generated/images/")
    console.print(f"💰 Est. Cost: ${len(final_images) * 0.025:.2f}")

    # Open folder
    import os
    output_dir = Path(__file__).parent.parent / "storage" / "generated" / "images"
    os.system(f"open {output_dir}")


if __name__ == "__main__":
    main()
