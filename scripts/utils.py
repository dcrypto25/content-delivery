"""
TRAINERAPP.AI - Content Automation Utilities
Shared helper functions across all modules
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Initialize Rich Console for beautiful terminal output
console = Console()

# Load environment variables
load_dotenv()

# ==========================================
# CONFIGURATION MANAGEMENT
# ==========================================

class Config:
    """Centralized configuration management"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self):
        """Load configuration from YAML and environment"""
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"

        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Override with environment variables where applicable
        self._config['openai_api_key'] = os.getenv('OPENAI_API_KEY')
        self._config['gemini_api_key'] = os.getenv('GEMINI_API_KEY')
        self._config['runway_api_key'] = os.getenv('RUNWAY_API_KEY')
        self._config['replicate_api_token'] = os.getenv('REPLICATE_API_TOKEN')

        console.print("[green]✓[/green] Configuration loaded successfully")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    def get_active_profile(self) -> Dict[str, Any]:
        """Get the currently active generation profile"""
        profile_name = self.get('active_profile', 'balanced')
        return self.get(f'profiles.{profile_name}')


# ==========================================
# LOGGING SETUP
# ==========================================

def setup_logging(name: str = "trainerapp") -> logging.Logger:
    """Configure logging with Rich handler"""

    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[
            RichHandler(rich_tracebacks=True, console=console),
            logging.FileHandler(log_dir / "system.log"),
        ]
    )

    logger = logging.getLogger(name)
    return logger


# ==========================================
# FILE MANAGEMENT
# ==========================================

class FileManager:
    """Handle all file operations with proper organization"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.storage_path = self.base_path / "storage"
        self.config = Config()

    def save_generated_asset(
        self,
        content: bytes,
        asset_type: str,  # 'image' or 'video'
        metadata: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Path:
        """
        Save generated asset with metadata

        Returns: Path to saved file
        """

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            theme = metadata.get('theme', 'general')
            variant_id = metadata.get('variant_id', '000')

            # Sanitize theme to avoid path separators
            # If theme contains multiple values (e.g., from choices list), take first one
            if isinstance(theme, str):
                theme = theme.replace('/', '_').replace('\\', '_')
                if '_' in theme:
                    # Take first theme if multiple concatenated
                    theme = theme.split('_')[0]

            # Sanitize variant_id as well
            if isinstance(variant_id, str):
                variant_id = variant_id.replace('/', '_').replace('\\', '_')

            extension = 'jpg' if asset_type == 'image' else 'mp4'
            filename = f"{theme}_{timestamp}_{variant_id}.{extension}"

        # Determine save path
        save_dir = self.storage_path / "generated" / f"{asset_type}s"
        save_dir.mkdir(parents=True, exist_ok=True)

        save_path = save_dir / filename

        # Save file
        with open(save_path, 'wb') as f:
            f.write(content)

        # Save metadata
        self.save_metadata(filename, metadata)

        console.print(f"[green]✓[/green] Saved {asset_type}: {filename}")
        return save_path

    def save_metadata(self, filename: str, metadata: Dict[str, Any]):
        """Save metadata as JSON alongside the asset"""

        metadata_dir = self.storage_path / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = metadata_dir / f"{Path(filename).stem}.json"

        # Add timestamp
        metadata['saved_at'] = datetime.now().isoformat()

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self, filename: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a file"""

        metadata_file = self.storage_path / "metadata" / f"{Path(filename).stem}.json"

        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)

        return None

    def organize_by_platform(self, asset_path: Path, platform: str):
        """Move/copy asset to platform-specific folder"""

        platform_dir = self.storage_path / "processed" / platform
        platform_dir.mkdir(parents=True, exist_ok=True)

        # Copy file
        dest = platform_dir / asset_path.name
        dest.write_bytes(asset_path.read_bytes())

        return dest


# ==========================================
# API HELPERS
# ==========================================

class APIRateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        """Block if rate limit would be exceeded"""
        import time

        now = time.time()

        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]

        # Wait if at limit
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                console.print(f"[yellow]⏳[/yellow] Rate limit reached, waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time)

        self.calls.append(now)


# ==========================================
# PROMPT UTILITIES
# ==========================================

def generate_utm_link(
    base_url: str = "trainerapp.ai",
    source: str = "automated_content",
    medium: str = "social",
    campaign: str = "content_automation"
) -> str:
    """Generate UTM-tagged link for tracking"""

    return f"https://{base_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""

    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}

    words = text.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]

    # Return most frequent
    from collections import Counter
    return [word for word, _ in Counter(keywords).most_common(max_keywords)]


# ==========================================
# ANALYTICS HELPERS
# ==========================================

class PerformanceTracker:
    """Track generation performance metrics"""

    def __init__(self):
        self.metrics = {
            'images_generated': 0,
            'videos_generated': 0,
            'api_calls': 0,
            'errors': 0,
            'total_cost': 0.0,
            'start_time': datetime.now()
        }

    def log_generation(self, asset_type: str, cost: float = 0.0):
        """Log a successful generation"""

        if asset_type == 'image':
            self.metrics['images_generated'] += 1
        elif asset_type == 'video':
            self.metrics['videos_generated'] += 1

        self.metrics['api_calls'] += 1
        self.metrics['total_cost'] += cost

    def log_error(self):
        """Log an error"""
        self.metrics['errors'] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""

        elapsed = (datetime.now() - self.metrics['start_time']).total_seconds()

        return {
            **self.metrics,
            'elapsed_seconds': elapsed,
            'images_per_minute': (self.metrics['images_generated'] / elapsed) * 60 if elapsed > 0 else 0,
            'cost_per_asset': self.metrics['total_cost'] / (self.metrics['images_generated'] + self.metrics['videos_generated']) if (self.metrics['images_generated'] + self.metrics['videos_generated']) > 0 else 0
        }

    def print_summary(self):
        """Print performance summary to console"""

        summary = self.get_summary()

        console.print("\n[bold cyan]📊 Performance Summary[/bold cyan]")
        console.print(f"Images: {summary['images_generated']}")
        console.print(f"Videos: {summary['videos_generated']}")
        console.print(f"Total Cost: ${summary['total_cost']:.2f}")
        console.print(f"Errors: {summary['errors']}")
        console.print(f"Time: {summary['elapsed_seconds']:.1f}s")
        console.print(f"Rate: {summary['images_per_minute']:.1f} images/min")


# ==========================================
# VALIDATION
# ==========================================

def validate_environment() -> bool:
    """Validate that all required environment variables are set"""

    required_vars = [
        'OPENAI_API_KEY',
    ]

    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        console.print(f"[red]✗[/red] Missing environment variables: {', '.join(missing)}")
        console.print("\n[yellow]Please configure your .env file[/yellow]")
        return False

    console.print("[green]✓[/green] Environment validated")
    return True


# ==========================================
# EXPORTS
# ==========================================

__all__ = [
    'Config',
    'FileManager',
    'APIRateLimiter',
    'PerformanceTracker',
    'setup_logging',
    'generate_utm_link',
    'extract_keywords',
    'validate_environment',
    'console'
]
