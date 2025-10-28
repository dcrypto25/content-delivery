"""
TRAINERAPP.AI - TikTok Uploader
Automated posting to TikTok using Content Posting API
"""

import os
import time
import requests
import hashlib
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

logger = setup_logging("tiktok_uploader")


class TikTokUploader:
    """
    Upload content to TikTok using Content Posting API
    Requires: TikTok Developer access and approved app
    """

    BASE_URL = "https://open.tiktokapis.com"
    API_VERSION = "v2"

    def __init__(self):
        self.config = Config()
        self.file_manager = FileManager()

        # API credentials
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')

        if not all([self.client_key, self.client_secret, self.access_token]):
            raise ValueError("TikTok credentials not configured. Check .env file")

        # Rate limiter (TikTok: more generous than Instagram)
        self.rate_limiter = APIRateLimiter(calls_per_minute=int(os.getenv('TIKTOK_RPM', 10)))

        logger.info("✓ TikTok Uploader initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=5, max=30))
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        hashtags: Optional[List[str]] = None,
        privacy_level: str = "PUBLIC_TO_EVERYONE",  # or MUTUAL_FOLLOW_FRIENDS, SELF_ONLY
        disable_duet: bool = False,
        disable_stitch: bool = False,
        disable_comment: bool = False,
    ) -> Dict[str, Any]:
        """
        Upload video to TikTok

        Returns: Response with video ID and share URL
        """

        logger.info(f"Uploading video to TikTok: {video_path.name}")
        self.rate_limiter.wait_if_needed()

        # Build caption with hashtags
        full_caption = self._build_caption(title, description, hashtags)

        # Step 1: Initialize upload
        upload_url, publish_id = self._initialize_upload(video_path)

        if not upload_url or not publish_id:
            raise Exception("Failed to initialize upload")

        logger.info(f"Upload initialized: {publish_id}")

        # Step 2: Upload video chunks
        self._upload_video_chunks(video_path, upload_url)

        # Step 3: Publish video
        publish_response = self._publish_video(
            publish_id=publish_id,
            caption=full_caption,
            privacy_level=privacy_level,
            disable_duet=disable_duet,
            disable_stitch=disable_stitch,
            disable_comment=disable_comment
        )

        logger.info(f"✓ Published to TikTok: {publish_response.get('publish_id')}")

        return {
            'success': True,
            'publish_id': publish_id,
            'share_url': publish_response.get('share_url'),
            'video_id': publish_response.get('video_id')
        }

    def _initialize_upload(self, video_path: Path) -> tuple[Optional[str], Optional[str]]:
        """Initialize video upload and get upload URL"""

        endpoint = f"{self.BASE_URL}/{self.API_VERSION}/post/publish/video/init/"

        # Get video size
        video_size = video_path.stat().st_size

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        payload = {
            'post_info': {
                'title': 'TrainerApp.AI Content',
                'privacy_level': 'PUBLIC_TO_EVERYONE',
                'disable_duet': False,
                'disable_comment': False,
                'disable_stitch': False,
                'video_cover_timestamp_ms': 1000
            },
            'source_info': {
                'source': 'FILE_UPLOAD',
                'video_size': video_size,
                'chunk_size': 10000000,  # 10MB chunks
                'total_chunk_count': (video_size // 10000000) + 1
            }
        }

        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get('error'):
            raise Exception(f"TikTok API error: {data['error']}")

        return (
            data.get('data', {}).get('upload_url'),
            data.get('data', {}).get('publish_id')
        )

    def _upload_video_chunks(self, video_path: Path, upload_url: str):
        """Upload video in chunks"""

        logger.info("Uploading video chunks...")

        chunk_size = 10000000  # 10MB

        with open(video_path, 'rb') as video_file:
            chunk_index = 0

            while True:
                chunk = video_file.read(chunk_size)

                if not chunk:
                    break

                headers = {
                    'Content-Range': f'bytes {chunk_index * chunk_size}-{chunk_index * chunk_size + len(chunk) - 1}/*',
                    'Content-Type': 'video/mp4'
                }

                response = requests.put(upload_url, data=chunk, headers=headers, timeout=60)
                response.raise_for_status()

                chunk_index += 1
                logger.info(f"Uploaded chunk {chunk_index}")

        logger.info("✓ All chunks uploaded")

    def _publish_video(
        self,
        publish_id: str,
        caption: str,
        privacy_level: str,
        disable_duet: bool,
        disable_stitch: bool,
        disable_comment: bool
    ) -> Dict[str, Any]:
        """Publish the uploaded video"""

        endpoint = f"{self.BASE_URL}/{self.API_VERSION}/post/publish/status/fetch/"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        payload = {
            'publish_id': publish_id
        }

        # Poll for completion
        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            status = data.get('data', {}).get('status')

            if status == 'PUBLISH_COMPLETE':
                logger.info("✓ Publish complete")
                return data.get('data', {})

            elif status == 'FAILED':
                raise Exception("Video publish failed")

            logger.info(f"Status: {status}, waiting...")
            time.sleep(5)
            attempt += 1

        raise Exception("Video publish timeout")

    def _build_caption(
        self,
        title: str,
        description: str,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """Build complete caption with hashtags"""

        # TikTok format: Title + Description + Hashtags
        caption_parts = []

        if title:
            caption_parts.append(title)

        if description:
            caption_parts.append(description)

        if hashtags:
            # Ensure hashtags have # prefix
            formatted_hashtags = [
                tag if tag.startswith('#') else f'#{tag}'
                for tag in hashtags
            ]
            caption_parts.append(' '.join(formatted_hashtags))

        full_caption = '\n\n'.join(caption_parts)

        # TikTok caption limit
        max_length = self.config.get('platforms.tiktok.captions.max_length', 2200)

        if len(full_caption) > max_length:
            full_caption = full_caption[:max_length-3] + '...'

        return full_caption

    def refresh_access_token(self) -> str:
        """Refresh OAuth access token"""

        endpoint = "https://open.tiktokapis.com/v2/oauth/token/"

        refresh_token = os.getenv('TIKTOK_REFRESH_TOKEN')

        if not refresh_token:
            raise ValueError("TIKTOK_REFRESH_TOKEN not set")

        payload = {
            'client_key': self.client_key,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        new_access_token = data.get('data', {}).get('access_token')
        new_refresh_token = data.get('data', {}).get('refresh_token')

        logger.info("✓ Access token refreshed")

        # TODO: Save new tokens to .env or database
        return new_access_token

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get information about a published video"""

        endpoint = f"{self.BASE_URL}/{self.API_VERSION}/video/query/"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json; charset=UTF-8'
        }

        payload = {
            'filters': {
                'video_ids': [video_id]
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {}

    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""

        endpoint = f"{self.BASE_URL}/{self.API_VERSION}/user/info/"

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        params = {
            'fields': 'open_id,union_id,avatar_url,display_name,follower_count,following_count,likes_count,video_count'
        }

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            return {}


# ==========================================
# ALTERNATIVE: Unofficial TikTok Upload
# (For testing/development only)
# ==========================================

class TikTokUnofficialUploader:
    """
    Unofficial TikTok uploader using tiktok-uploader library
    Easier for testing but not recommended for production
    """

    def __init__(self):
        try:
            from tiktok_uploader.upload import upload_video
            self.upload_video = upload_video
            logger.info("✓ TikTok Unofficial Uploader initialized")

        except ImportError:
            raise ImportError("tiktok-uploader not installed. Run: pip install tiktok-uploader")

    def upload(
        self,
        video_path: Path,
        description: str,
        cookies_file: str = "tiktok_cookies.txt"
    ) -> bool:
        """
        Upload using unofficial method
        Requires: cookies from logged-in TikTok session
        """

        try:
            self.upload_video(
                filename=str(video_path),
                description=description,
                cookies=cookies_file
            )

            logger.info("✓ Video uploaded (unofficial)")
            return True

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False


# ==========================================
# CLI INTERFACE
# ==========================================

def main():
    """Command-line interface for testing"""

    import argparse

    parser = argparse.ArgumentParser(description="TrainerApp.AI TikTok Uploader")
    parser.add_argument('--video', type=str, required=True, help='Path to video file')
    parser.add_argument('--title', type=str, required=True, help='Video title')
    parser.add_argument('--description', type=str, help='Video description')
    parser.add_argument('--hashtags', type=str, help='Comma-separated hashtags')
    parser.add_argument('--unofficial', action='store_true', help='Use unofficial uploader')

    args = parser.parse_args()

    if args.unofficial:
        uploader = TikTokUnofficialUploader()
        description = f"{args.title}\n\n{args.description or ''}"

        if args.hashtags:
            hashtags = ' '.join([f'#{tag.strip()}' for tag in args.hashtags.split(',')])
            description += f"\n\n{hashtags}"

        console.print(f"\n[cyan]📱 Uploading to TikTok (unofficial)...[/cyan]")

        success = uploader.upload(
            video_path=Path(args.video),
            description=description
        )

        if success:
            console.print(f"\n[green]✓ Success![/green]")

    else:
        uploader = TikTokUploader()

        hashtags = args.hashtags.split(',') if args.hashtags else None

        console.print(f"\n[cyan]📱 Uploading to TikTok...[/cyan]")

        result = uploader.upload_video(
            video_path=Path(args.video),
            title=args.title,
            description=args.description or '',
            hashtags=hashtags
        )

        console.print(f"\n[green]✓ Success![/green]")
        console.print(f"Publish ID: {result['publish_id']}")
        console.print(f"Share URL: {result['share_url']}")


if __name__ == "__main__":
    main()
