#!/usr/bin/env python3
"""
Quick test of the realistic content approach:
1. Use existing image as base
2. Generate variation with img2img
3. Composite real UI on top
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "scripts"))

from generators.image_generator import ImageGenerator
from compositing import UICompositor
from utils import console

def main():
    console.print("\n[bold cyan]🧪 Testing Realistic Content Approach[/bold cyan]")
    console.print("━" * 60 + "\n")

    # Use existing image as base
    base_image = Path("storage/generated/images/test_20251028_163758_test_001.jpg")
    ui_screenshot = Path("storage/raw_inputs/test_ui.png")

    if not base_image.exists():
        console.print("[red]Error:[/red] Base image not found")
        return

    if not ui_screenshot.exists():
        console.print("[red]Error:[/red] UI screenshot not found")
        return

    console.print(f"📸 Base Image: {base_image.name}")
    console.print(f"🖥️  UI Screenshot: {ui_screenshot.name}\n")

    # Step 1: Generate variation using img2img
    console.print("[bold]Step 1: Generate Variation (img2img)[/bold]")
    console.print("[dim]This maintains realism from the base photo[/dim]\n")

    generator = ImageGenerator(provider='replicate_dev')

    try:
        prompt = "Athletic person doing squats in gym, checking phone with TrainerApp.AI workout tracker app, professional photography, natural lighting, real gym environment"

        variation = generator.generate_single(
            prompt=prompt,
            metadata={
                'variant_id': 'realistic_test_001',
                'theme': 'realistic_test'
            },
            base_image=base_image,
            strength=0.7  # 70% transformation
        )

        if not variation:
            console.print("[red]Failed to generate variation[/red]")
            return

        console.print(f"[green]✓[/green] Generated: {variation.name}\n")

        # Step 2: Composite real UI
        console.print("[bold]Step 2: Composite Real UI[/bold]")
        console.print("[dim]Overlay your actual app screenshot[/dim]\n")

        compositor = UICompositor()

        final = compositor.overlay_ui_on_image(
            base_image_path=variation,
            ui_screenshot_path=ui_screenshot,
            position='auto',
            phone_scale=0.25,
            perspective=True
        )

        console.print(f"[green]✓[/green] Final image: {final.name}\n")

        # Summary
        console.print("━" * 60)
        console.print("[bold green]✅ Test Complete![/bold green]\n")

        console.print("Compare the results:")
        console.print(f"  1. Original (AI only): {base_image.name}")
        console.print(f"  2. img2img variation: {variation.name}")
        console.print(f"  3. With real UI: {final.name}")

        console.print("\n[cyan]💡 The difference:[/cyan]")
        console.print("  • img2img keeps realistic people/exercises")
        console.print("  • Real UI overlay shows your actual app")
        console.print("  • Result looks like professional content")

        # Open folder
        import os
        os.system(f"open {variation.parent}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
