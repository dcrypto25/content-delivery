"""
TRAINERAPP.AI - Stock Photo Fetcher
Fetch high-quality stock fitness photos from Pexels (free API)
"""

import os
import requests
from typing import List, Optional, Dict, Any
from pathlib import Path
import time

import sys
sys.path.append(str(Path(__file__).parent))

from utils import setup_logging, console

logger = setup_logging("stock_fetcher")


class StockPhotoFetcher:
    """
    Fetch stock photos from Pexels
    Free tier: 200 requests/hour
    """

    def __init__(self):
        self.api_key = os.getenv('PEXELS_API_KEY')
        if not self.api_key:
            # Provide a default key for testing, but users should get their own
            logger.warning("PEXELS_API_KEY not set. Get free key at: https://www.pexels.com/api/")
            console.print("[yellow]⚠️  Get free Pexels API key at: https://www.pexels.com/api/[/yellow]")

        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key} if self.api_key else {}

        self.cache_dir = Path(__file__).parent.parent / "storage" / "stock_photos"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_photos(
        self,
        query: str,
        per_page: int = 10,
        orientation: str = "portrait"  # portrait for phone screens
    ) -> List[Dict[str, Any]]:
        """
        Search for stock photos

        Args:
            query: Search term (e.g., "person exercising gym")
            per_page: Number of results (max 80)
            orientation: portrait, landscape, or square

        Returns: List of photo metadata
        """

        if not self.api_key:
            logger.error("No Pexels API key set")
            return []

        logger.info(f"Searching Pexels: '{query}' ({per_page} results)")

        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": orientation
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            photos = data.get('photos', [])

            logger.info(f"✓ Found {len(photos)} photos")
            return photos

        except Exception as e:
            logger.error(f"Failed to search Pexels: {str(e)}")
            return []

    def download_photo(
        self,
        photo: Dict[str, Any],
        size: str = "large"  # original, large, medium, small
    ) -> Optional[Path]:
        """
        Download a photo to cache

        Returns: Path to downloaded file
        """

        try:
            # Get URL for requested size
            url = photo['src'].get(size, photo['src']['large'])
            photo_id = photo['id']

            # Check cache first
            filename = f"pexels_{photo_id}_{size}.jpg"
            cache_path = self.cache_dir / filename

            if cache_path.exists():
                logger.info(f"Using cached: {filename}")
                return cache_path

            # Download
            logger.info(f"Downloading photo {photo_id}...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Save
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✓ Downloaded: {filename}")

            # Add attribution metadata
            self._save_attribution(cache_path, photo)

            return cache_path

        except Exception as e:
            logger.error(f"Failed to download photo: {str(e)}")
            return None

    def _save_attribution(self, photo_path: Path, photo: Dict[str, Any]):
        """Save attribution info as required by Pexels"""

        attribution_file = photo_path.with_suffix('.txt')

        photographer = photo.get('photographer', 'Unknown')
        photo_url = photo.get('url', '')

        with open(attribution_file, 'w') as f:
            f.write(f"Photo by {photographer} on Pexels\n")
            f.write(f"{photo_url}\n")

    def fetch_fitness_base_images(
        self,
        num_images: int = 10,
        workout_type: Optional[str] = None
    ) -> List[Path]:
        """
        Fetch diverse fitness photos for use as base images

        Args:
            num_images: Number of photos to fetch
            workout_type: Optional specific workout (e.g., "squat", "deadlift")

        Returns: List of downloaded photo paths
        """

        # Diverse search queries for fitness content
        queries = [
            "person exercising gym",
            "athlete workout",
            "fitness training",
            "gym workout phone",
            "person using phone gym",
            "fitness app",
            "gym selfie",
            "workout phone tracking"
        ]

        if workout_type:
            queries.insert(0, f"person {workout_type} exercise")

        downloaded = []
        per_query = max(2, num_images // len(queries))

        console.print(f"[cyan]📸 Fetching {num_images} stock fitness photos...[/cyan]")

        for query in queries:
            if len(downloaded) >= num_images:
                break

            photos = self.search_photos(query, per_page=per_query)

            for photo in photos[:per_query]:
                if len(downloaded) >= num_images:
                    break

                path = self.download_photo(photo)
                if path:
                    downloaded.append(path)

                time.sleep(0.2)  # Rate limiting

        console.print(f"[green]✓[/green] Downloaded {len(downloaded)} photos")
        return downloaded


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch stock fitness photos")
    parser.add_argument('--query', type=str, default='gym workout', help='Search query')
    parser.add_argument('--count', type=int, default=5, help='Number of photos')

    args = parser.parse_args()

    fetcher = StockPhotoFetcher()
    photos = fetcher.search_photos(args.query, per_page=args.count)

    console.print(f"\nFound {len(photos)} photos:")

    for i, photo in enumerate(photos, 1):
        console.print(f"{i}. {photo['photographer']} - {photo['url']}")
        path = fetcher.download_photo(photo)
        if path:
            console.print(f"   Saved: {path}")
