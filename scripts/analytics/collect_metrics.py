#!/usr/bin/env python3
"""
TrainerApp.AI - Analytics Collector
Collect performance metrics from Instagram and TikTok
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from utils import Config, setup_logging, console
from uploaders.instagram_uploader import InstagramUploader
from uploaders.tiktok_uploader import TikTokUploader

logger = setup_logging("analytics")


class MetricsCollector:
    """Collect and aggregate metrics from social platforms"""

    def __init__(self):
        self.config = Config()
        self.ig_uploader = None
        self.tt_uploader = None

        try:
            self.ig_uploader = InstagramUploader()
        except:
            logger.warning("Instagram not configured")

        try:
            self.tt_uploader = TikTokUploader()
        except:
            logger.warning("TikTok not configured")

    def collect_all(self, days: int = 7) -> dict:
        """Collect metrics from all platforms"""

        metrics = {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'instagram': self._collect_instagram(days),
            'tiktok': self._collect_tiktok(days),
        }

        # Calculate aggregates
        metrics['totals'] = {
            'impressions': sum([
                metrics['instagram'].get('impressions', 0),
                metrics['tiktok'].get('views', 0)
            ]),
            'engagement': sum([
                metrics['instagram'].get('engagement', 0),
                metrics['tiktok'].get('engagement', 0)
            ])
        }

        # Save metrics
        self._save_metrics(metrics)

        return metrics

    def _collect_instagram(self, days: int) -> dict:
        """Collect Instagram metrics"""

        if not self.ig_uploader:
            return {}

        try:
            insights = self.ig_uploader.get_account_insights(days=days)

            return {
                'impressions': insights.get('impressions', 0),
                'reach': insights.get('reach', 0),
                'engagement': insights.get('engagement', 0),
                'followers': insights.get('follower_count', 0)
            }

        except Exception as e:
            logger.error(f"Instagram metrics failed: {str(e)}")
            return {}

    def _collect_tiktok(self, days: int) -> dict:
        """Collect TikTok metrics"""

        if not self.tt_uploader:
            return {}

        try:
            user_info = self.tt_uploader.get_user_info()

            return {
                'views': user_info.get('video_views', 0),
                'likes': user_info.get('likes_count', 0),
                'followers': user_info.get('follower_count', 0),
                'engagement': user_info.get('likes_count', 0)  # Simplified
            }

        except Exception as e:
            logger.error(f"TikTok metrics failed: {str(e)}")
            return {}

    def _save_metrics(self, metrics: dict):
        """Save metrics to file"""

        output_dir = Path(__file__).parent.parent.parent / "storage" / "metadata"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Daily metrics file
        date_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = output_dir / f"metrics_{date_str}.json"

        with open(daily_file, 'w') as f:
            json.dump(metrics, f, indent=2)

        # Also update latest
        latest_file = output_dir / "metrics_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(metrics, f, indent=2)

        console.print(f"[green]✓[/green] Metrics saved to {daily_file}")


def main():
    """CLI interface"""

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)

    args = parser.parse_args()

    collector = MetricsCollector()
    metrics = collector.collect_all(days=args.days)

    # Print summary
    console.print("\n[bold cyan]📊 Metrics Summary[/bold cyan]\n")
    console.print(f"Instagram Impressions: {metrics['instagram'].get('impressions', 0):,}")
    console.print(f"TikTok Views: {metrics['tiktok'].get('views', 0):,}")
    console.print(f"Total Engagement: {metrics['totals']['engagement']:,}")


if __name__ == "__main__":
    main()
