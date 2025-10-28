#!/usr/bin/env python3
"""
TRAINERAPP.AI - Content Automation Orchestrator
Main entry point for generating and posting content
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add scripts to path
sys.path.append(str(Path(__file__).parent))

from utils import (
    Config,
    FileManager,
    setup_logging,
    console,
    validate_environment,
    PerformanceTracker
)

from generators.prompt_generator import PromptGenerator
from generators.image_generator import ImageGenerator
# from generators.video_generator import VideoGenerator  # To be created
from uploaders.instagram_uploader import InstagramUploader
from uploaders.tiktok_uploader import TikTokUploader

logger = setup_logging("orchestrator")


class ContentOrchestrator:
    """
    Main orchestrator for the entire content pipeline
    Input → Analysis → Prompts → Generation → Enhancement → Posting
    """

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with optional config override"""

        self.config = Config()
        self.file_manager = FileManager()
        self.tracker = PerformanceTracker()

        # Override config if provided
        if config_override:
            for key, value in config_override.items():
                setattr(self.config, key, value)

        # Initialize generators
        self.prompt_generator = PromptGenerator()

        profile = self.config.get_active_profile()
        self.image_generator = ImageGenerator(provider=profile.get('image_provider'))

        # Initialize uploaders
        self.instagram_uploader = None
        self.tiktok_uploader = None

        # Lazy init uploaders (only if needed)
        if self.config.get('platforms.instagram.enabled'):
            try:
                self.instagram_uploader = InstagramUploader()
            except Exception as e:
                logger.warning(f"Instagram uploader not available: {str(e)}")

        if self.config.get('platforms.tiktok.enabled'):
            try:
                self.tiktok_uploader = TikTokUploader()
            except Exception as e:
                logger.warning(f"TikTok uploader not available: {str(e)}")

        logger.info("✓ Content Orchestrator initialized")

    def run_full_pipeline(
        self,
        input_source: Optional[str] = None,
        theme: str = "workout",
        quantity: int = 100,
        skip_generation: bool = False,
        skip_posting: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline from input to posting

        Args:
            input_source: Path to input image/video or URL
            theme: Content theme (workout/nutrition/motivation/app_features)
            quantity: Number of assets to generate
            skip_generation: Use existing generated assets
            skip_posting: Generate but don't post

        Returns:
            Pipeline results with stats
        """

        console.print("\n[bold cyan]🚀 TRAINERAPP.AI CONTENT AUTOMATION PIPELINE[/bold cyan]\n")

        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'config': {
                'theme': theme,
                'quantity': quantity,
                'provider': self.image_generator.provider
            },
            'prompts_generated': 0,
            'images_generated': 0,
            'videos_generated': 0,
            'posts_created': 0,
            'errors': []
        }

        try:
            # STEP 1: Analyze input (if provided)
            base_analysis = None
            if input_source:
                console.print(f"[cyan]📸 Step 1: Analyzing input...[/cyan]")
                base_analysis = self._analyze_input(input_source)
                console.print(f"[green]✓[/green] Analysis complete\n")

            # STEP 2: Generate prompts
            console.print(f"[cyan]🎨 Step 2: Generating {quantity} prompts...[/cyan]")
            prompts = self._generate_prompts(
                base_analysis=base_analysis,
                theme=theme,
                quantity=quantity
            )
            results['prompts_generated'] = len(prompts)
            console.print(f"[green]✓[/green] Generated {len(prompts)} prompts\n")

            # Split prompts by content type
            image_prompts = [p for p in prompts if p.get('content_type', 'image') == 'image']
            video_prompts = [p for p in prompts if p.get('content_type') == 'video']

            # STEP 3: Generate images
            generated_paths = []

            if not skip_generation and image_prompts:
                console.print(f"[cyan]🖼️  Step 3: Generating {len(image_prompts)} images...[/cyan]")
                image_paths = self.image_generator.generate_batch(image_prompts)
                generated_paths.extend(image_paths)
                results['images_generated'] = len(image_paths)
                console.print(f"[green]✓[/green] Generated {len(image_paths)} images\n")

            # STEP 4: Generate videos (if applicable)
            # TODO: Implement video generation
            if video_prompts:
                console.print(f"[yellow]⚠️  Video generation not yet implemented (skipping {len(video_prompts)} videos)[/yellow]\n")

            # STEP 5: Post to social media
            if not skip_posting and generated_paths:
                console.print(f"[cyan]📱 Step 4: Posting to social media...[/cyan]")
                posted_count = self._post_to_social_media(generated_paths, prompts)
                results['posts_created'] = posted_count
                console.print(f"[green]✓[/green] Posted {posted_count} assets\n")

            # Calculate final stats
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            results['success'] = True

            # Print summary
            self._print_summary(results)

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)

        return results

    def _analyze_input(self, input_source: str) -> Optional[Dict[str, Any]]:
        """Analyze input image/video with AI"""

        try:
            # Check if it's a file or URL
            if os.path.exists(input_source):
                # Local file
                return self.prompt_generator.analyze_input_with_vision(input_source)

            elif input_source.startswith('http'):
                # URL - download first
                import requests
                response = requests.get(input_source, timeout=30)
                response.raise_for_status()

                # Save temporarily
                temp_path = Path("/tmp/trainerapp_input.jpg")
                temp_path.write_bytes(response.content)

                return self.prompt_generator.analyze_input_with_vision(str(temp_path))

            else:
                logger.warning(f"Invalid input source: {input_source}")
                return None

        except Exception as e:
            logger.error(f"Input analysis failed: {str(e)}")
            return None

    def _generate_prompts(
        self,
        base_analysis: Optional[Dict[str, Any]],
        theme: str,
        quantity: int
    ) -> List[Dict[str, Any]]:
        """Generate batch of prompts"""

        # Determine split between images and videos
        profile = self.config.get_active_profile()
        image_qty = profile.get('image_quantity', 70)
        video_qty = profile.get('video_quantity', 30)

        # Adjust to match requested quantity
        ratio = image_qty / (image_qty + video_qty)
        image_count = int(quantity * ratio)
        video_count = quantity - image_count

        prompts = []

        # Generate image prompts
        if image_count > 0:
            image_prompts = self.prompt_generator.generate_batch_prompts(
                base_analysis=base_analysis,
                theme=theme,
                quantity=image_count,
                content_type='image'
            )
            prompts.extend(image_prompts)

        # Generate video prompts
        if video_count > 0:
            video_prompts = self.prompt_generator.generate_batch_prompts(
                base_analysis=base_analysis,
                theme=theme,
                quantity=video_count,
                content_type='video'
            )
            prompts.extend(video_prompts)

        # Save prompts for reference
        self.prompt_generator.save_prompts_batch(
            prompts,
            f"{theme}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        return prompts

    def _post_to_social_media(
        self,
        asset_paths: List[Path],
        prompts: List[Dict[str, Any]]
    ) -> int:
        """Post assets to configured platforms"""

        posted_count = 0

        # Create mapping of asset paths to prompts
        # (assuming same order)
        for i, asset_path in enumerate(asset_paths):
            if i >= len(prompts):
                break

            prompt_data = prompts[i]

            # Generate caption
            captions = self.prompt_generator.generate_caption_variants(
                prompt_data,
                num_variants=1,
                platform='instagram'  # Can be dynamic
            )

            caption = captions[0] if captions else "Check out TrainerApp.AI for your personalized fitness plan!"

            # Extract hashtags from config
            hashtags = self._get_hashtags(prompt_data.get('theme'))

            # Determine platform based on prompt data
            target_platform = prompt_data.get('platform', 'both')

            try:
                # Post to Instagram
                if target_platform in ['instagram', 'both'] and self.instagram_uploader:
                    media_type = "REELS" if asset_path.suffix in ['.mp4', '.mov'] else "IMAGE"

                    self.instagram_uploader.upload_media(
                        media_path=asset_path,
                        caption=caption,
                        media_type=media_type,
                        hashtags=hashtags
                    )

                    posted_count += 1
                    logger.info(f"✓ Posted to Instagram: {asset_path.name}")

                # Post to TikTok
                if target_platform in ['tiktok', 'both'] and self.tiktok_uploader:
                    if asset_path.suffix in ['.mp4', '.mov']:
                        self.tiktok_uploader.upload_video(
                            video_path=asset_path,
                            title=prompt_data.get('title', 'Fitness Motivation'),
                            description=caption,
                            hashtags=hashtags
                        )

                        posted_count += 1
                        logger.info(f"✓ Posted to TikTok: {asset_path.name}")

            except Exception as e:
                logger.error(f"Failed to post {asset_path.name}: {str(e)}")
                continue

        return posted_count

    def _get_hashtags(self, theme: str) -> List[str]:
        """Get hashtags for theme"""

        # Get theme-specific hashtags
        theme_config = self.config.get(f'themes.{theme}', {})
        keywords = theme_config.get('keywords', [])

        # Convert keywords to hashtags
        hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords]

        # Add evergreen hashtags
        evergreen = self.config.get('hashtags.evergreen.fitness', [])
        hashtags.extend(evergreen[:5])

        # Add brand hashtags
        brand = self.config.get('hashtags.evergreen.brand', [])
        hashtags.extend(brand)

        return hashtags[:20]  # Limit to 20

    def _print_summary(self, results: Dict[str, Any]):
        """Print pipeline summary"""

        console.print("\n[bold cyan]📊 PIPELINE SUMMARY[/bold cyan]\n")

        console.print(f"Theme: [yellow]{results['config']['theme']}[/yellow]")
        console.print(f"Provider: [yellow]{results['config']['provider']}[/yellow]")
        console.print(f"Duration: [yellow]{results['duration_seconds']:.1f}s[/yellow]")
        console.print(f"\nPrompts: [green]{results['prompts_generated']}[/green]")
        console.print(f"Images: [green]{results['images_generated']}[/green]")
        console.print(f"Videos: [green]{results['videos_generated']}[/green]")
        console.print(f"Posted: [green]{results['posts_created']}[/green]")

        # Cost estimation
        self.tracker.print_summary()


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface"""

    parser = argparse.ArgumentParser(
        description="TrainerApp.AI Content Automation Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100 workout images
  python orchestrator.py --theme workout --quantity 100

  # Analyze competitor content and create variations
  python orchestrator.py --input rival_post.jpg --quantity 50

  # Generate without posting (for review)
  python orchestrator.py --theme nutrition --quantity 20 --skip-posting

  # Use existing prompts (skip generation)
  python orchestrator.py --skip-generation --post-existing
        """
    )

    parser.add_argument('--input', type=str, help='Input image/video path or URL')
    parser.add_argument('--theme', type=str, default='workout',
                       choices=['workout', 'nutrition', 'motivation', 'app_features'],
                       help='Content theme')
    parser.add_argument('--quantity', type=int, default=10, help='Number of assets to generate')
    parser.add_argument('--skip-generation', action='store_true', help='Skip generation step')
    parser.add_argument('--skip-posting', action='store_true', help='Skip posting step')
    parser.add_argument('--provider', type=str, choices=['gemini', 'replicate'],
                       help='Override image generation provider')

    args = parser.parse_args()

    # Validate environment
    if not validate_environment():
        sys.exit(1)

    # Initialize orchestrator
    config_override = {}
    if args.provider:
        config_override['image_provider'] = args.provider

    orchestrator = ContentOrchestrator(config_override=config_override)

    # Run pipeline
    results = orchestrator.run_full_pipeline(
        input_source=args.input,
        theme=args.theme,
        quantity=args.quantity,
        skip_generation=args.skip_generation,
        skip_posting=args.skip_posting
    )

    # Save results
    results_path = Path(__file__).parent.parent / "storage" / "metadata" / "last_run.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
