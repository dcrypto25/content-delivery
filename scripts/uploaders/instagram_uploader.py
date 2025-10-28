"""
TRAINERAPP.AI - Instagram Uploader
Automated posting to Instagram using Meta Graph API
"""

import os
import time
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils import (
    Config,
    FileManager,
    setup_logging,
    console,
    APIRateLimiter
)

logger = setup_logging("instagram_uploader")


class InstagramUploader:
    """
    Upload content to Instagram using Meta Graph API
    Supports: Feed posts, Reels, Stories
    """

    API_VERSION = "v21.0"
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()

        # API credentials
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.business_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')

        if not self.access_token or not self.business_account_id:
            raise ValueError("Instagram credentials not configured. Check .env file")

        # Rate limiter (Instagram: 25 posts per day, ~1 per hour)
        self.rate_limiter = APIRateLimiter(calls_per_minute=1)

        logger.info("✓ Instagram Uploader initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=30))
    def upload_media(
        self,
        media_path: Path,
        caption: str,
        media_type: str = "REELS",  # REELS, IMAGE, CAROUSEL_ALBUM
        hashtags: Optional[List[str]] = None,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload media to Instagram

        Returns: Response with post ID and permalink
        """

        logger.info(f"Uploading {media_type} to Instagram: {media_path.name}")
        self.rate_limiter.wait_if_needed()

        # Build caption with hashtags
        full_caption = self._build_caption(caption, hashtags)

        # Step 1: Create media container
        container_id = self._create_media_container(
            media_path=media_path,
            caption=full_caption,
            media_type=media_type,
            location_id=location_id
        )

        if not container_id:
            raise Exception("Failed to create media container")

        logger.info(f"Media container created: {container_id}")

        # Step 2: Wait for processing (required for videos)
        if media_type == "REELS":
            self._wait_for_processing(container_id)

        # Step 3: Publish media
        publish_response = self._publish_media(container_id)

        logger.info(f"✓ Published to Instagram: {publish_response.get('id')}")

        # Get permalink
        post_id = publish_response.get('id')
        permalink = self._get_permalink(post_id)

        return {
            'success': True,
            'post_id': post_id,
            'permalink': permalink,
            'container_id': container_id
        }

    def _create_media_container(
        self,
        media_path: Path,
        caption: str,
        media_type: str,
        location_id: Optional[str] = None
    ) -> Optional[str]:
        """Create media container (step 1 of posting)"""

        # First, upload media to a publicly accessible URL
        # Instagram requires media to be hosted (not direct file upload)
        media_url = self._upload_to_hosting(media_path)

        if not media_url:
            raise Exception("Failed to upload media to hosting")

        # Prepare API request
        endpoint = f"{self.BASE_URL}/{self.business_account_id}/media"

        params = {
            'access_token': self.access_token,
            'caption': caption,
        }

        if media_type == "REELS":
            params['media_type'] = 'REELS'
            params['video_url'] = media_url
            params['share_to_feed'] = True

        elif media_type == "IMAGE":
            params['image_url'] = media_url

        if location_id:
            params['location_id'] = location_id

        # Make request
        response = requests.post(endpoint, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data.get('id')

    def _wait_for_processing(self, container_id: str, max_wait: int = 300):
        """Wait for video processing to complete"""

        logger.info("Waiting for video processing...")

        endpoint = f"{self.BASE_URL}/{container_id}"

        start_time = time.time()

        while time.time() - start_time < max_wait:
            params = {
                'access_token': self.access_token,
                'fields': 'status_code'
            }

            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            status = data.get('status_code')

            if status == 'FINISHED':
                logger.info("✓ Processing complete")
                return True

            elif status == 'ERROR':
                raise Exception("Video processing failed")

            logger.info(f"Status: {status}, waiting...")
            time.sleep(10)

        raise Exception("Video processing timeout")

    def _publish_media(self, container_id: str) -> Dict[str, Any]:
        """Publish media container (step 2 of posting)"""

        endpoint = f"{self.BASE_URL}/{self.business_account_id}/media_publish"

        params = {
            'access_token': self.access_token,
            'creation_id': container_id
        }

        response = requests.post(endpoint, params=params, timeout=30)
        response.raise_for_status()

        return response.json()

    def _get_permalink(self, post_id: str) -> Optional[str]:
        """Get permalink for published post"""

        endpoint = f"{self.BASE_URL}/{post_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'permalink'
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('permalink')

        except Exception as e:
            logger.error(f"Failed to get permalink: {str(e)}")
            return None

    def _upload_to_hosting(self, media_path: Path) -> Optional[str]:
        """
        Upload media to publicly accessible hosting
        Options:
        1. Google Drive (with public link)
        2. AWS S3 (public bucket)
        3. Cloudinary
        4. Your own server

        For this example, we'll use a placeholder
        YOU NEED TO IMPLEMENT THIS BASED ON YOUR HOSTING CHOICE
        """

        # TODO: Implement actual hosting upload
        # For now, return a placeholder

        logger.warning("⚠️  Using placeholder media URL. Implement _upload_to_hosting() for production!")

        # Example implementations:

        # Option 1: AWS S3
        # import boto3
        # s3 = boto3.client('s3')
        # bucket = os.getenv('AWS_S3_BUCKET')
        # key = f"instagram/{media_path.name}"
        # s3.upload_file(str(media_path), bucket, key)
        # return f"https://{bucket}.s3.amazonaws.com/{key}"

        # Option 2: Cloudinary
        # import cloudinary
        # import cloudinary.uploader
        # result = cloudinary.uploader.upload(str(media_path))
        # return result['secure_url']

        # Option 3: Your server
        # Upload to your web server and return public URL

        return f"https://your-cdn.com/media/{media_path.name}"

    def _build_caption(self, caption: str, hashtags: Optional[List[str]] = None) -> str:
        """Build complete caption with hashtags"""

        full_caption = caption

        if hashtags:
            # Instagram best practice: hashtags at the end
            hashtag_string = ' '.join(hashtags)
            full_caption = f"{caption}\n\n{hashtag_string}"

        # Ensure within length limit
        max_length = self.config.get('platforms.instagram.captions.max_length', 2200)

        if len(full_caption) > max_length:
            # Truncate caption but keep hashtags
            if hashtags:
                hashtag_string = ' '.join(hashtags)
                available_length = max_length - len(hashtag_string) - 10
                full_caption = f"{caption[:available_length]}...\n\n{hashtag_string}"
            else:
                full_caption = full_caption[:max_length]

        return full_caption

    def schedule_post(
        self,
        media_path: Path,
        caption: str,
        scheduled_time: str,  # ISO 8601 format
        media_type: str = "REELS"
    ):
        """
        Schedule a post for later
        Note: Scheduling requires Instagram Creator or Business account
        """

        # TODO: Implement scheduling
        # Instagram Graph API doesn't support scheduling directly
        # You need to use Meta Business Suite API or third-party scheduler

        logger.warning("Instagram scheduling not yet implemented")
        pass

    def get_account_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get account performance metrics"""

        endpoint = f"{self.BASE_URL}/{self.business_account_id}/insights"

        params = {
            'access_token': self.access_token,
            'metric': 'impressions,reach,profile_views,follower_count',
            'period': 'day'
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get insights: {str(e)}")
            return {}

    def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """Get insights for a specific post"""

        endpoint = f"{self.BASE_URL}/{post_id}/insights"

        params = {
            'access_token': self.access_token,
            'metric': 'likes,comments,shares,saves,impressions,reach,engagement'
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get post insights: {str(e)}")
            return {}


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface for testing"""

    import argparse

    parser = argparse.ArgumentParser(description="TrainerApp.AI Instagram Uploader")
    parser.add_argument('--media', type=str, required=True, help='Path to media file')
    parser.add_argument('--caption', type=str, required=True, help='Post caption')
    parser.add_argument('--type', type=str, default='REELS', choices=['REELS', 'IMAGE'])
    parser.add_argument('--hashtags', type=str, help='Comma-separated hashtags')

    args = parser.parse_args()

    uploader = InstagramUploader()

    hashtags = args.hashtags.split(',') if args.hashtags else None

    console.print(f"\n[cyan]📸 Uploading to Instagram...[/cyan]")

    result = uploader.upload_media(
        media_path=Path(args.media),
        caption=args.caption,
        media_type=args.type,
        hashtags=hashtags
    )

    console.print(f"\n[green]✓ Success![/green]")
    console.print(f"Post ID: {result['post_id']}")
    console.print(f"Permalink: {result['permalink']}")


if __name__ == "__main__":
    main()
