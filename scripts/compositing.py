"""
TRAINERAPP.AI - Image Compositing
Overlay real app UI screenshots onto phone screens in generated images
"""

import os
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

import sys
sys.path.append(str(Path(__file__).parent))

from utils import setup_logging, console

logger = setup_logging("compositing")


class UICompositor:
    """
    Composite real app UI onto generated fitness images
    """

    def __init__(self):
        self.ui_screenshots_dir = Path(__file__).parent.parent / "storage" / "raw_inputs"

    def overlay_ui_on_image(
        self,
        base_image_path: Path,
        ui_screenshot_path: Path,
        position: str = "auto",  # auto, center, right, left
        phone_scale: float = 0.25,  # Size of phone relative to image
        perspective: bool = True,  # Add slight perspective/angle
        opacity: float = 0.95  # UI opacity
    ) -> Path:
        """
        Overlay app UI screenshot onto an image

        Args:
            base_image_path: Path to fitness photo
            ui_screenshot_path: Path to app screenshot
            position: Where to place the phone UI
            phone_scale: How large the phone should be (0.0-1.0)
            perspective: Add realistic perspective/angle
            opacity: UI transparency (0.0-1.0)

        Returns: Path to composited image
        """

        logger.info(f"Compositing UI onto {base_image_path.name}")

        try:
            # Load images
            base = Image.open(base_image_path).convert('RGBA')
            ui_screenshot = Image.open(ui_screenshot_path).convert('RGBA')

            # Calculate phone dimensions
            base_width, base_height = base.size
            phone_width = int(base_width * phone_scale)

            # Scale UI screenshot to phone width
            ui_aspect = ui_screenshot.height / ui_screenshot.width
            phone_height = int(phone_width * ui_aspect)

            ui_resized = ui_screenshot.resize((phone_width, phone_height), Image.Resampling.LANCZOS)

            # Add phone frame/bezel around UI
            phone_image = self._add_phone_frame(ui_resized)

            # Apply perspective if requested
            if perspective:
                phone_image = self._add_perspective(phone_image, angle=random.uniform(-15, 15))

            # Determine position
            x, y = self._calculate_position(
                base_size=(base_width, base_height),
                phone_size=phone_image.size,
                position=position
            )

            # Adjust opacity
            if opacity < 1.0:
                phone_image = self._adjust_opacity(phone_image, opacity)

            # Add shadow for realism
            shadow = self._create_shadow(phone_image, offset=(5, 5), blur=10)
            base.paste(shadow, (x + 5, y + 5), shadow)

            # Composite phone onto base
            base.paste(phone_image, (x, y), phone_image)

            # Save result
            output_path = base_image_path.parent / f"{base_image_path.stem}_with_ui.png"
            final = base.convert('RGB')
            final.save(output_path, quality=95)

            logger.info(f"✓ Saved composited image: {output_path.name}")
            return output_path

        except Exception as e:
            logger.error(f"Compositing failed: {str(e)}")
            raise

    def _add_phone_frame(self, ui_screenshot: Image.Image, bezel_size: int = 20) -> Image.Image:
        """Add a phone frame/bezel around the UI screenshot"""

        width, height = ui_screenshot.size

        # Create frame with rounded corners
        frame_width = width + (bezel_size * 2)
        frame_height = height + (bezel_size * 2)

        # Create phone frame (dark gray/black)
        frame = Image.new('RGBA', (frame_width, frame_height), (20, 20, 20, 255))

        # Add rounded corners
        frame = self._add_rounded_corners(frame, radius=30)

        # Paste UI into frame
        frame.paste(ui_screenshot, (bezel_size, bezel_size), ui_screenshot)

        # Add subtle screen glare/reflection
        frame = self._add_screen_glare(frame)

        return frame

    def _add_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Add rounded corners to image"""

        # Create mask
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)

        # Apply mask
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)

        return output

    def _add_screen_glare(self, img: Image.Image) -> Image.Image:
        """Add subtle screen glare for realism"""

        width, height = img.size

        # Create glare layer
        glare = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(glare)

        # Diagonal glare (top-right to bottom-left)
        glare_opacity = 30
        glare_width = width // 3

        for i in range(glare_width):
            opacity = int(glare_opacity * (1 - i / glare_width))
            draw.line(
                [(width - i, 0), (width, i)],
                fill=(255, 255, 255, opacity),
                width=2
            )

        # Composite glare
        img = Image.alpha_composite(img, glare)

        return img

    def _add_perspective(self, img: Image.Image, angle: float = 10) -> Image.Image:
        """Add slight perspective/rotation for realism"""

        # Rotate slightly
        rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

        return rotated

    def _adjust_opacity(self, img: Image.Image, opacity: float) -> Image.Image:
        """Adjust overall image opacity"""

        img_copy = img.copy()
        alpha = img_copy.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        img_copy.putalpha(alpha)

        return img_copy

    def _create_shadow(self, img: Image.Image, offset: Tuple[int, int], blur: int = 10) -> Image.Image:
        """Create drop shadow for phone"""

        # Create shadow mask
        shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 180))

        # Use alpha channel as mask
        shadow.paste(shadow_layer, (0, 0), img.split()[3])

        # Blur shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

        return shadow

    def _calculate_position(
        self,
        base_size: Tuple[int, int],
        phone_size: Tuple[int, int],
        position: str
    ) -> Tuple[int, int]:
        """Calculate where to place phone UI"""

        base_width, base_height = base_size
        phone_width, phone_height = phone_size

        if position == "center":
            x = (base_width - phone_width) // 2
            y = (base_height - phone_height) // 2

        elif position == "right":
            x = base_width - phone_width - 50
            y = (base_height - phone_height) // 2

        elif position == "left":
            x = 50
            y = (base_height - phone_height) // 2

        else:  # auto - choose best position
            # Place in bottom-right with some padding
            x = base_width - phone_width - 80
            y = base_height - phone_height - 80

        return (x, y)

    def batch_composite(
        self,
        image_paths: list[Path],
        ui_screenshot_path: Path,
        **kwargs
    ) -> list[Path]:
        """
        Composite UI onto multiple images

        Returns: List of composited image paths
        """

        console.print(f"\n[cyan]🎨 Compositing UI onto {len(image_paths)} images...[/cyan]")

        composited = []

        for img_path in image_paths:
            try:
                result = self.overlay_ui_on_image(img_path, ui_screenshot_path, **kwargs)
                composited.append(result)
            except Exception as e:
                logger.error(f"Failed to composite {img_path.name}: {str(e)}")
                continue

        console.print(f"[green]✓[/green] Composited {len(composited)} images")

        return composited


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Composite app UI onto fitness images")
    parser.add_argument('--base', type=str, required=True, help='Base fitness image')
    parser.add_argument('--ui', type=str, required=True, help='UI screenshot')
    parser.add_argument('--position', type=str, default='auto', choices=['auto', 'center', 'left', 'right'])
    parser.add_argument('--scale', type=float, default=0.25, help='Phone scale (0.0-1.0)')

    args = parser.parse_args()

    compositor = UICompositor()
    result = compositor.overlay_ui_on_image(
        base_image_path=Path(args.base),
        ui_screenshot_path=Path(args.ui),
        position=args.position,
        phone_scale=args.scale
    )

    console.print(f"\n[green]✓[/green] Result saved: {result}")
