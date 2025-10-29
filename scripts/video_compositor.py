"""
TRAINERAPP.AI - Video Compositor
Create engaging social media videos from UI screenshots + text overlays
Uses MoviePy for video editing (will need to install: pip install moviepy)
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

import sys
sys.path.append(str(Path(__file__).parent))

from utils import setup_logging, console
from generators.image_generator import ImageGenerator

logger = setup_logging("video_compositor")

# Check if moviepy is available
try:
    from moviepy.editor import (
        ImageClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, AudioFileClip
    )
    from moviepy.video.fx import resize, fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("MoviePy not installed. Install with: pip install moviepy")


class VideoCompositor:
    """
    Create TikTok/Instagram Reels videos from UI screenshots and text
    """

    # Video specs for social media
    VIDEO_SIZE = (1080, 1920)  # 9:16 vertical
    FPS = 30
    DEFAULT_DURATION = 15  # seconds

    def __init__(self):
        self.storage_path = Path(__file__).parent.parent / "storage"
        self.screenshots_path = self.storage_path / "raw_inputs" / "trainerapp_screenshots"
        self.backgrounds_path = self.storage_path / "backgrounds"
        self.output_path = self.storage_path / "generated" / "videos" / "social"

        # Create directories
        for path in [self.screenshots_path, self.backgrounds_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.image_generator = ImageGenerator(provider='replicate_dev')

    def create_type1_feature_spotlight(
        self,
        feature_name: str,
        screenshots: List[Path],
        text_overlays: List[str],
        hook: str,
        cta: str,
        background_style: str = "gym_aesthetic"
    ) -> Path:
        """
        Type 1: Feature Spotlight Video

        Format: Phone screen mockup + text overlays + background

        Args:
            feature_name: e.g. "workout_tracker"
            screenshots: 2-4 UI screenshots to showcase
            text_overlays: Text to show over each screenshot
            hook: Opening hook text
            cta: Call to action at end
            background_style: Style of background to generate

        Returns: Path to generated video
        """

        logger.info(f"Creating Type 1 video for: {feature_name}")

        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy required for video generation. Install: pip install moviepy")

        # Step 1: Generate simple background
        background_path = self._get_or_generate_background(background_style)

        # Step 2: Create phone mockups from screenshots
        phone_clips = []

        for i, (screenshot, text) in enumerate(zip(screenshots, text_overlays)):
            # Create phone mockup with screenshot
            phone_frame = self._create_phone_frame(screenshot)

            # Create clip
            clip = ImageClip(str(phone_frame), duration=3)

            # Add text overlay
            txt_clip = TextClip(
                text,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center'
            ).set_position(('center', 200)).set_duration(3)

            # Add shadow to text
            shadow_clip = TextClip(
                text,
                fontsize=60,
                color='black',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center'
            ).set_position(('center', 202)).set_duration(3)

            # Composite
            frame_clip = CompositeVideoClip([clip, shadow_clip, txt_clip])
            phone_clips.append(frame_clip)

        # Step 3: Create opening hook clip
        hook_bg = ImageClip(str(background_path), duration=2)
        hook_txt = TextClip(
            hook,
            fontsize=70,
            color='white',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(2)

        hook_shadow = TextClip(
            hook,
            fontsize=70,
            color='black',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position(('center', 2)).set_duration(2)

        hook_clip = CompositeVideoClip([hook_bg, hook_shadow, hook_txt])

        # Step 4: Create CTA ending clip
        cta_bg = ImageClip(str(background_path), duration=2)
        cta_txt = TextClip(
            cta,
            fontsize=80,
            color='#FF6B35',  # Orange
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(2)

        cta_clip = CompositeVideoClip([cta_bg, cta_txt])

        # Step 5: Concatenate all clips
        final = concatenate_videoclips([hook_clip] + phone_clips + [cta_clip])

        # Step 6: Export
        output_file = self.output_path / f"type1_{feature_name}_{int(time.time())}.mp4"

        final.write_videofile(
            str(output_file),
            fps=self.FPS,
            codec='libx264',
            audio=False,
            preset='medium'
        )

        logger.info(f"✓ Created Type 1 video: {output_file.name}")
        return output_file

    def create_type2_pov_relatable(
        self,
        concept: Dict[str, Any],
        num_scenes: int = 4
    ) -> Path:
        """
        Type 2: POV/Relatable Format

        Format: Text-heavy storytelling over aesthetic backgrounds
        No UI screenshots needed

        Args:
            concept: Dict with 'title', 'scenes' (list of text), 'ending'
            num_scenes: Number of scenes (usually 3-5)

        Returns: Path to generated video
        """

        logger.info(f"Creating Type 2 video: {concept['title']}")

        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy required")

        clips = []

        # Generate backgrounds for each scene
        for i, scene_text in enumerate(concept['scenes']):
            # Generate simple aesthetic background
            bg_style = random.choice([
                "empty modern gym interior, no people, cinematic lighting",
                "minimalist fitness studio, soft shadows, aesthetic",
                "abstract blue orange gradient, fitness inspired",
                "blurred gym equipment background, bokeh effect"
            ])

            bg_path = self._get_or_generate_background(bg_style, cache_key=f"pov_{i}")

            # Create background clip
            bg_clip = ImageClip(str(bg_path), duration=3)

            # Add text overlay
            txt = TextClip(
                scene_text,
                fontsize=65,
                color='white',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center'
            ).set_position('center').set_duration(3)

            shadow = TextClip(
                scene_text,
                fontsize=65,
                color='black',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center'
            ).set_position(('center', 2)).set_duration(3)

            # Composite
            scene_clip = CompositeVideoClip([bg_clip, shadow, txt])

            # Add fade transitions
            scene_clip = scene_clip.crossfadein(0.5).crossfadeout(0.5)

            clips.append(scene_clip)

        # Concatenate
        final = concatenate_videoclips(clips)

        # Export
        output_file = self.output_path / f"type2_{concept['title'].replace(' ', '_')[:30]}_{int(time.time())}.mp4"

        final.write_videofile(
            str(output_file),
            fps=self.FPS,
            codec='libx264',
            audio=False,
            preset='medium'
        )

        logger.info(f"✓ Created Type 2 video: {output_file.name}")
        return output_file

    def create_type3_results_data(
        self,
        progress_screenshots: List[Path],
        timeline_text: List[str],
        title: str,
        insight: str
    ) -> Path:
        """
        Type 3: Results/Data Visualization

        Format: Progress screenshots with timeline annotations

        Args:
            progress_screenshots: Screenshots showing progress (graphs, stats)
            timeline_text: Text for each screenshot (e.g., "Day 1", "Day 30")
            title: Video title
            insight: Key insight/lesson learned

        Returns: Path to generated video
        """

        logger.info(f"Creating Type 3 video: {title}")

        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy required")

        clips = []

        # Opening title
        bg = self._get_or_generate_background("solid_dark")
        title_clip = self._create_text_clip(title, str(bg), duration=2, fontsize=70)
        clips.append(title_clip)

        # Progress screenshots
        for screenshot, text in zip(progress_screenshots, timeline_text):
            # Screenshot as background
            img_clip = ImageClip(str(screenshot), duration=3)

            # Timeline text overlay
            txt = TextClip(
                text,
                fontsize=80,
                color='#FF6B35',
                font='Arial-Bold'
            ).set_position(('center', 150)).set_duration(3)

            scene = CompositeVideoClip([img_clip, txt])
            clips.append(scene)

        # Closing insight
        insight_clip = self._create_text_clip(insight, str(bg), duration=2, fontsize=60)
        clips.append(insight_clip)

        # Concatenate
        final = concatenate_videoclips(clips)

        # Export
        output_file = self.output_path / f"type3_{title.replace(' ', '_')[:30]}_{int(time.time())}.mp4"

        final.write_videofile(
            str(output_file),
            fps=self.FPS,
            codec='libx264',
            audio=False,
            preset='medium'
        )

        logger.info(f"✓ Created Type 3 video: {output_file.name}")
        return output_file

    def _create_phone_frame(self, screenshot_path: Path) -> Path:
        """Add phone frame around screenshot"""

        from compositing import UICompositor

        compositor = UICompositor()

        # Load screenshot
        screenshot = Image.open(screenshot_path)

        # Create phone frame
        phone = compositor._add_phone_frame(screenshot.convert('RGBA'))

        # Save to temp
        temp_path = self.storage_path / "temp" / f"phone_{screenshot_path.stem}.png"
        temp_path.parent.mkdir(exist_ok=True)
        phone.save(temp_path)

        return temp_path

    def _get_or_generate_background(self, style: str, cache_key: Optional[str] = None) -> Path:
        """Get cached background or generate new one"""

        # Check cache
        cache_filename = f"bg_{cache_key or style.replace(' ', '_')[:30]}.jpg"
        cache_path = self.backgrounds_path / cache_filename

        if cache_path.exists():
            logger.info(f"Using cached background: {cache_filename}")
            return cache_path

        # Generate new background
        logger.info(f"Generating background: {style}")

        prompt = f"{style}, no people, no text, vertical 9:16 format, cinematic, professional photography"

        result = self.image_generator.generate_single(
            prompt=prompt,
            metadata={'type': 'background', 'style': style},
            size="1080x1920"
        )

        if result:
            # Copy to backgrounds cache
            import shutil
            shutil.copy(result, cache_path)
            return cache_path

        # Fallback: create solid color background
        return self._create_solid_background()

    def _create_solid_background(self, color: Tuple[int, int, int] = (20, 20, 30)) -> Path:
        """Create solid color background as fallback"""

        img = Image.new('RGB', self.VIDEO_SIZE, color)
        path = self.backgrounds_path / "solid_dark.jpg"
        img.save(path, quality=95)
        return path

    def _create_text_clip(self, text: str, background_path: str, duration: float, fontsize: int) -> CompositeVideoClip:
        """Helper to create text over background"""

        bg = ImageClip(background_path, duration=duration)

        txt = TextClip(
            text,
            fontsize=fontsize,
            color='white',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(duration)

        shadow = TextClip(
            text,
            fontsize=fontsize,
            color='black',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position(('center', 2)).set_duration(duration)

        return CompositeVideoClip([bg, shadow, txt])


import time

# Test function
if __name__ == "__main__":
    console.print("\n[cyan]Testing Video Compositor[/cyan]\n")

    compositor = VideoCompositor()

    # Test creating solid background
    bg = compositor._create_solid_background()
    console.print(f"[green]✓[/green] Created background: {bg}")
