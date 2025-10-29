#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "scripts"))

from generators.image_generator import ImageGenerator
from utils import console

# Use VERY low strength to minimize morphing
base_image = Path("storage/generated/images/test_20251028_163758_test_001.jpg")

generator = ImageGenerator(provider='replicate_dev')

console.print("\n[cyan]Testing with low strength (0.3 = only 30% changes)[/cyan]\n")

result = generator.generate_single(
    prompt="Athletic person with phone visible showing workout app",
    metadata={'variant_id': 'low_strength_001', 'theme': 'test'},
    base_image=base_image,
    strength=0.3  # MUCH lower
)

console.print(f"\n[green]Result:[/green] {result}")
