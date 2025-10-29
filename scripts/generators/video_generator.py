"""
TRAINERAPP.AI - Video Generator
Generate short-form videos for social media using Runway and Replicate
"""

import os
import io
import time
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import replicate
except ImportError:
    replicate = None

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    Config,
    FileManager,
    setup_logging,
    console,
    APIRateLimiter,
    PerformanceTracker
)

logger = setup_logging("video_generator")


class VideoGenerator:
    """
    Multi-provider video generator
    Supports: Runway Gen-3, Replicate (Minimax, Luma, etc.)
    """

    PROVIDER_COSTS = {
        'runway': 0.05,        # $0.05 per second
        'replicate_minimax': 0.10,  # $0.10 per video
        'replicate_luma': 0.15,     # $0.15 per video
    }

    def __init__(self, provider: Optional[str] = None):
        self.config = Config()
        self.file_manager = FileManager()
        self.tracker = PerformanceTracker()

        # Determine provider
        profile = self.config.get_active_profile()
        self.provider = provider or profile.get('video_provider', 'replicate_minimax')

        logger.info(f"Initializing VideoGenerator with provider: {self.provider}")

        # Initialize provider
        self._init_provider()

        # Rate limiter
        self.rate_limiter = APIRateLimiter(
            calls_per_minute=int(os.getenv('RUNWAY_RPM', 10))
        )

    def _init_provider(self):
        """Initialize the selected provider"""

        if self.provider.startswith('replicate'):
            if replicate is None:
                raise ImportError("replicate not installed. Run: pip install replicate")

            api_token = os.getenv('REPLICATE_API_TOKEN')
            if not api_token:
                raise ValueError("REPLICATE_API_TOKEN not set")

            os.environ['REPLICATE_API_TOKEN'] = api_token
            logger.info(f"✓ Replicate initialized for video: {self.provider}")

        elif self.provider == 'runway':
            api_key = os.getenv('RUNWAY_API_KEY')
            if api_key:
                logger.info("✓ Runway initialized")
            else:
                logger.warning("RUNWAY_API_KEY not set, will use Replicate fallback")
                self.provider = 'replicate_minimax'

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=30))
    def generate_single(
        self,
        prompt: str,
        metadata: Dict[str, Any],
        duration: int = 5,
        size: str = "1080x1920"
    ) -> Optional[Path]:
        """
        Generate a single video

        Args:
            prompt: Text prompt for video generation
            metadata: Additional metadata
            duration: Video duration in seconds (default: 5)
            size: Video resolution (default: 1080x1920 for vertical)

        Returns: Path to saved video file
        """

        logger.info(f"Generating video: {metadata.get('variant_id', 'unknown')}")
        self.rate_limiter.wait_if_needed()

        try:
            # Enhance prompt for better video quality
            enhanced_prompt = self._enhance_prompt_for_video(prompt)

            if self.provider.startswith('replicate'):
                video_data = self._generate_replicate(enhanced_prompt, duration, size)
            elif self.provider == 'runway':
                video_data = self._generate_runway(enhanced_prompt, duration, size)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            # Save video
            if video_data:
                path = self.file_manager.save_generated_asset(
                    content=video_data,
                    asset_type='video',
                    metadata={
                        **metadata,
                        'provider': self.provider,
                        'duration': duration,
                        'size': size,
                        'prompt': prompt
                    }
                )

                # Track performance
                cost = self.PROVIDER_COSTS.get(self.provider, 0) * duration
                self.tracker.log_generation('video', cost)

                return path

        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            self.tracker.log_error()
            raise

        return None

    def _generate_replicate(self, prompt: str, duration: int, size: str) -> bytes:
        """Generate video using Replicate models"""

        width, height = map(int, size.split('x'))

        # Model selection based on provider
        model_map = {
            'replicate_minimax': 'minimax/video-01',
            'replicate_luma': 'luma/photon',
        }

        model = model_map.get(self.provider, 'minimax/video-01')

        console.print(f"[yellow]⏳ Generating video with {model}...[/yellow]")
        console.print(f"[dim]This may take 1-3 minutes...[/dim]")

        start_time = time.time()

        try:
            # Model-specific parameters
            if 'minimax' in model:
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "prompt_optimizer": True,  # Enhance prompt
                    }
                )
            elif 'luma' in model:
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        "aspect_ratio": "9:16" if height > width else "16:9",
                        "loop": False
                    }
                )

            elapsed = time.time() - start_time
            console.print(f"[green]✓[/green] Generated in {elapsed:.1f}s")

            # Download video
            if output:
                video_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else output.get('url')

                console.print(f"[cyan]⬇️  Downloading video...[/cyan]")
                response = requests.get(video_url, timeout=120)
                response.raise_for_status()

                return response.content

        except Exception as e:
            logger.error(f"Replicate video generation failed: {str(e)}")
            raise

        raise Exception("No output from Replicate")

    def _generate_runway(self, prompt: str, duration: int, size: str) -> bytes:
        """Generate video using Runway Gen-3"""

        console.print(f"[yellow]⏳ Generating video with Runway Gen-3...[/yellow]")
        console.print(f"[dim]This may take 2-4 minutes...[/dim]")

        # Runway Gen-3 API is not yet publicly available
        # This is a placeholder for when it becomes available

        logger.warning("Runway Gen-3 API not yet publicly available. Falling back to Replicate.")

        # Fallback to Replicate
        original_provider = self.provider
        self.provider = 'replicate_minimax'
        result = self._generate_replicate(prompt, duration, size)
        self.provider = original_provider

        return result

    def _enhance_prompt_for_video(self, prompt: str) -> str:
        """Enhance prompt specifically for video generation"""

        # Video-specific enhancements
        video_keywords = []

        # Add movement descriptions if missing
        if not any(word in prompt.lower() for word in ['moving', 'motion', 'dynamic', 'action']):
            video_keywords.append("smooth natural movement")

        # Emphasize realism for people
        if any(word in prompt.lower() for word in ['person', 'woman', 'man', 'athlete']):
            video_keywords.append("natural realistic motion")
            video_keywords.append("authentic human movement")

        # Camera work
        if not any(word in prompt.lower() for word in ['camera', 'shot', 'angle']):
            video_keywords.append("steady camera")

        # App integration for videos
        if 'trainerapp' in prompt.lower():
            video_keywords.append("phone screen clearly visible throughout video")
            video_keywords.append("app interface responsive and animated")

        # Fitness-specific
        if 'workout' in prompt.lower() or 'exercise' in prompt.lower():
            video_keywords.append("proper exercise form")
            video_keywords.append("realistic workout intensity")

        # Combine enhancements
        if video_keywords:
            prompt = f"{prompt}, {', '.join(video_keywords)}"

        # Anti-CGI
        prompt = f"{prompt}, NOT CGI, NOT animated, NOT cartoon, real footage style"

        return prompt

    def generate_batch(
        self,
        prompts: List[Dict[str, Any]],
        max_concurrent: int = 3  # Videos take longer, limit concurrency
    ) -> List[Path]:
        """
        Generate a batch of videos

        Returns: List of paths to saved videos
        """

        logger.info(f"Starting batch video generation: {len(prompts)} videos")
        console.print(f"\n[cyan]🎬 Generating {len(prompts)} videos with {self.provider}...[/cyan]")
        console.print(f"[yellow]⚠️  Note: Video generation is slower than images (1-3 min each)[/yellow]\n")

        generated_paths = []

        from tqdm import tqdm

        for prompt_obj in tqdm(prompts, desc="Generating videos"):
            try:
                # Get duration from metadata or use default
                duration = prompt_obj.get('duration', 5)

                # Determine size based on platform
                platform = prompt_obj.get('platform', 'tiktok')
                size = "1080x1920"  # Vertical for TikTok/Reels

                path = self.generate_single(
                    prompt=prompt_obj['prompt'],
                    metadata=prompt_obj,
                    duration=duration,
                    size=size
                )

                if path:
                    generated_paths.append(path)

            except Exception as e:
                logger.error(f"Failed to generate {prompt_obj.get('variant_id')}: {str(e)}")
                continue

        # Print summary
        self.tracker.print_summary()

        return generated_paths


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface for testing"""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="TrainerApp.AI Video Generator")
    parser.add_argument('--provider', type=str,
                       choices=['runway', 'replicate_minimax', 'replicate_luma'],
                       help='Video generation provider')
    parser.add_argument('--prompt', type=str, help='Single prompt to generate')
    parser.add_argument('--batch', type=str, help='Path to JSON file with prompts')
    parser.add_argument('--duration', type=int, default=5, help='Video duration in seconds')
    parser.add_argument('--size', type=str, default='1080x1920', help='Video size')

    args = parser.parse_args()

    generator = VideoGenerator(provider=args.provider)

    if args.prompt:
        # Single generation
        console.print(f"\n[cyan]🎬 Generating single video...[/cyan]")

        path = generator.generate_single(
            prompt=args.prompt,
            metadata={'variant_id': 'test_001', 'theme': 'test'},
            duration=args.duration,
            size=args.size
        )

        console.print(f"[green]✓[/green] Generated: {path}")

    elif args.batch:
        # Batch generation
        with open(args.batch, 'r') as f:
            data = json.load(f)
            prompts = data.get('prompts', [])

        paths = generator.generate_batch(prompts)

        console.print(f"\n[green]✓[/green] Generated {len(paths)} videos")

    else:
        console.print("[red]Error:[/red] Provide either --prompt or --batch")


if __name__ == "__main__":
    main()
