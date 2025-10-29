#!/usr/bin/env python3
"""
Simple approach: Real stock photos + UI overlay only
No AI generation = No morphing
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from stock_photo_fetcher import StockPhotoFetcher
from compositing import UICompositor
from utils import console

def main():
    console.print("\n[bold cyan]📸 Simple Stock + UI Composite[/bold cyan]")
    console.print("[dim]No AI generation = No morphing issues[/dim]")
    console.print("━" * 60 + "\n")

    # Fetch real stock photos
    fetcher = StockPhotoFetcher()

    if not fetcher.api_key:
        console.print("[yellow]⚠️  Set PEXELS_API_KEY in .env[/yellow]")
        console.print("Get free key at: https://www.pexels.com/api/\n")
        return

    # Fetch diverse fitness photos
    console.print("[bold]Step 1: Fetching Real Stock Photos[/bold]")
    photos = fetcher.fetch_fitness_base_images(num_images=10)

    if not photos:
        console.print("[red]No photos fetched[/red]")
        return

    # Composite UI
    console.print("\n[bold]Step 2: Adding Your App UI[/bold]")

    ui_path = Path("storage/raw_inputs/test_ui.png")
    if not ui_path.exists():
        console.print(f"[red]UI screenshot not found: {ui_path}[/red]")
        return

    compositor = UICompositor()

    results = compositor.batch_composite(
        image_paths=photos,
        ui_screenshot_path=ui_path,
        position='auto',
        phone_scale=0.3
    )

    console.print("\n" + "━" * 60)
    console.print("[bold green]✅ Done![/bold green]\n")
    console.print(f"📊 Created: {len(results)} images")
    console.print(f"💰 Cost: $0.00 (just API calls)")
    console.print(f"📁 Location: storage/generated/images/\n")

    console.print("[cyan]Pros:[/cyan]")
    console.print("  ✅ Zero morphing - real photos")
    console.print("  ✅ Free (except stock license)")
    console.print("  ✅ Fast\n")

    console.print("[yellow]Cons:[/yellow]")
    console.print("  ⚠️  Limited to stock photo library")
    console.print("  ⚠️  UI overlay may look pasted on")

    # Open folder
    import os
    os.system(f"open {photos[0].parent}")

if __name__ == "__main__":
    main()
