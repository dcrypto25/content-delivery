#!/usr/bin/env python3
"""
TRAINERAPP.AI - Social Media Video Generator
Main script to create all 3 types of content for Instagram Reels & TikTok

Usage:
  python create_social_videos.py --type all --count 75
  python create_social_videos.py --type feature --count 50
  python create_social_videos.py --type pov --count 20
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent / "scripts"))

from video_compositor import VideoCompositor, MOVIEPY_AVAILABLE
from utils import console

# Feature video concepts (Type 1)
FEATURE_SPOTLIGHT_CONCEPTS = [
    {
        "feature": "workout_tracker",
        "screenshots_folder": "workout_tracker",
        "screenshots_needed": ["tracker_exercise_view.png", "tracker_set_input.png", "tracker_rest_timer.png"],
        "hooks": [
            "POV: Your app tracks EVERYTHING",
            "This app knows when you're slacking",
            "Your notes app could never"
        ],
        "text_overlays": [
            "Sets, reps, weight, how hard it felt...",
            "Even your rest timer",
            "Never lose track mid-workout"
        ],
        "cta": "trainerapp.ai"
    },
    {
        "feature": "form_review",
        "screenshots_folder": "form_review",
        "screenshots_needed": ["form_upload.png", "form_analyzing.png", "form_results.png"],
        "hooks": [
            "This app just told me my squat form was off...",
            "Your gym bro can't do this",
            "Better than a personal trainer?"
        ],
        "text_overlays": [
            "...before I even sent the video",
            "AI spotted the issue instantly",
            "5 free reviews per month"
        ],
        "cta": "Get your form checked"
    },
    {
        "feature": "workout_generator",
        "screenshots_folder": "workout_generator",
        "screenshots_needed": ["generator_form.png", "generator_result.png"],
        "hooks": [
            "This app just built my ENTIRE workout...",
            "POV: You skip leg day and the AI knows",
            "AI-generated workouts hit different"
        ],
        "text_overlays": [
            "...in 10 seconds",
            "Personalized to MY goals",
            "Never guess what to do again"
        ],
        "cta": "trainerapp.ai"
    },
    {
        "feature": "physique_scan",
        "screenshots_folder": "physique_scan",
        "screenshots_needed": ["scan_interface.png", "scan_results.png"],
        "hooks": [
            "This app scanned my body...",
            "Forget the scale. Use THIS.",
            "This AI knows more than my mirror"
        ],
        "text_overlays": [
            "...and told me my ACTUAL body fat %",
            "No calipers. No DEXA. Just AI.",
            "$14.99/mo Premium feature"
        ],
        "cta": "See your real progress"
    },
    {
        "feature": "meal_planner",
        "screenshots_folder": "meal_planner",
        "screenshots_needed": ["meal_preferences.png", "meal_options.png", "meal_details.png"],
        "hooks": [
            "I told this app I hate chicken...",
            "Meal prep but make it not boring",
            "POV: Your meal plan actually tastes good"
        ],
        "text_overlays": [
            "...and it made me 3 meal plans WITHOUT it",
            "Macros matched PERFECTLY",
            "Never eat the same boring meals"
        ],
        "cta": "AI-powered meal planning"
    },
    {
        "feature": "macro_tracker",
        "screenshots_folder": "macro_tracker",
        "screenshots_needed": ["tracker_empty.png", "tracker_logged.png", "tracker_summary.png"],
        "hooks": [
            "Why your macros are off...",
            "This app shows you in REAL TIME",
            "Stay accountable every day"
        ],
        "text_overlays": [
            "This app shows you in REAL TIME",
            "Not tomorrow. Not next week. NOW.",
            "Track what actually matters"
        ],
        "cta": "Hit your macros daily"
    },
    {
        "feature": "weight_tracker",
        "screenshots_folder": "weight_tracker",
        "screenshots_needed": ["weight_entry.png", "weight_graph.png"],
        "hooks": [
            "The scale lied to you this morning",
            "But THIS shows the real trend",
            "See progress, not just numbers"
        ],
        "text_overlays": [
            "But THIS shows the real trend",
            "You're down 5lbs this month",
            "Weight trends > daily numbers"
        ],
        "cta": "Track the real progress"
    },
    {
        "feature": "water_tracker",
        "screenshots_folder": "water_tracker",
        "screenshots_needed": ["water_empty.png", "water_adding.png", "water_complete.png"],
        "hooks": [
            "POV: You finally drink enough water",
            "Because the app won't let you forget",
            "Build a 30-day streak"
        ],
        "text_overlays": [
            "Because the app won't let you forget",
            "Quick tap. That's it.",
            "Goal reached! 64/64 oz"
        ],
        "cta": "Stay hydrated daily"
    },
    {
        "feature": "hype",
        "screenshots_folder": "hype",
        "screenshots_needed": ["hype_input.png", "hype_stern.png", "hype_understanding.png"],
        "hooks": [
            "I told my app I didn't want to workout...",
            "This AI is meaner than my ex",
            "When you need a pep talk at 5am"
        ],
        "text_overlays": [
            "...and it roasted me",
            "Or it can be nice if you want",
            "Your AI coach that gets you"
        ],
        "cta": "Get motivated. Get moving."
    },
    {
        "feature": "dashboard",
        "screenshots_folder": "dashboard",
        "screenshots_needed": ["dashboard_overview.png", "dashboard_streaks.png"],
        "hooks": [
            "Your progress. All in one place.",
            "See how far you've come",
            "15-day streak and counting"
        ],
        "text_overlays": [
            "Workouts, macros, weight, water...",
            "Plus your 15-day streak",
            "Everything in one dashboard"
        ],
        "cta": "Track it all"
    }
]

# POV/Relatable concepts (Type 2)
POV_RELATABLE_CONCEPTS = [
    {
        "title": "tried_6_apps",
        "scenes": [
            "POV: You've tried 6 workout apps",
            "They all make you input every. single. rep.",
            "Then you find one with AI tracking",
            "Game. Changed."
        ]
    },
    {
        "title": "forgot_workout",
        "scenes": [
            "That feeling when you forget what workout you did last week",
            "Because you wrote it in your notes app",
            "And now it's buried under grocery lists",
            "TrainerApp remembers for you"
        ]
    },
    {
        "title": "gym_bro_advice",
        "scenes": [
            "Your gym bro: 'Just do more volume bro'",
            "Your app: 'Your RPE was 9/10, recover first'",
            "Who's giving better advice?",
            "Yeah. The app."
        ]
    },
    {
        "title": "new_year_resolutions",
        "scenes": [
            "January 1st: Download fitness app",
            "January 3rd: Too complicated, give up",
            "This year try an app that's actually simple",
            "TrainerApp.AI"
        ]
    },
    {
        "title": "meal_prep_sunday",
        "scenes": [
            "Meal prep Sunday hits different when",
            "The app tells you EXACTLY what to cook",
            "With the EXACT macros you need",
            "Goodbye guesswork"
        ]
    },
    {
        "title": "progress_pics",
        "scenes": [
            "Taking progress pics in bad lighting",
            "Wondering if you're actually making progress",
            "Or just use an app that scans your physique",
            "And tracks it for you"
        ]
    },
    {
        "title": "motivation_missing",
        "scenes": [
            "When you have zero motivation",
            "And your workout is in 20 minutes",
            "So you ask your app for a pep talk",
            "And it actually works"
        ]
    },
    {
        "title": "form_check",
        "scenes": [
            "Asking random gym people to check your form",
            "Getting 5 different answers",
            "Or just upload a video to AI",
            "One answer. Actually helpful."
        ]
    },
    {
        "title": "tracking_macros",
        "scenes": [
            "You: I'm eating healthy",
            "Also you: No idea how much protein you ate",
            "Start tracking. See the difference.",
            "In real-time. Every day."
        ]
    },
    {
        "title": "water_intake",
        "scenes": [
            "Everyone: Drink more water",
            "You: I forgot",
            "Again.",
            "Let the app remind you"
        ]
    }
]

# Results/Data concepts (Type 3)
RESULTS_DATA_CONCEPTS = [
    {
        "title": "squat_progression",
        "screenshots_folder": "weight_tracker",
        "screenshots_needed": ["weight_graph.png"],
        "timeline": [
            "Day 1: Struggled with 95lbs",
            "Day 30: Hit 135lbs for reps"
        ],
        "insight": "All because the app told me WHEN to add weight"
    },
    {
        "title": "body_recomp",
        "screenshots_folder": "physique_scan",
        "screenshots_needed": ["scan_results.png"],
        "timeline": [
            "Week 1: 22% body fat",
            "Week 12: 17% body fat"
        ],
        "insight": "Same weight. Different body. AI tracked it all."
    },
    {
        "title": "streak_momentum",
        "screenshots_folder": "dashboard",
        "screenshots_needed": ["dashboard_streaks.png"],
        "timeline": [
            "Day 1: New app who dis",
            "Day 50: Longest streak of my life"
        ],
        "insight": "Streaks work. Accountability works."
    },
    {
        "title": "macro_consistency",
        "screenshots_folder": "macro_tracker",
        "screenshots_needed": ["tracker_summary.png"],
        "timeline": [
            "Month 1: Hit macros 12/30 days",
            "Month 3: Hit macros 28/30 days"
        ],
        "insight": "You can't improve what you don't track"
    },
    {
        "title": "water_habit",
        "screenshots_folder": "water_tracker",
        "screenshots_needed": ["water_complete.png"],
        "timeline": [
            "Before: 32oz per day",
            "After: 80oz per day, 21-day streak"
        ],
        "insight": "Simple tracking = life-changing habits"
    }
]


def main():
    parser = argparse.ArgumentParser(
        description="🎬 TrainerApp.AI Social Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE RUNNING:

1. Capture screenshots and organize them:
   storage/raw_inputs/trainerapp_screenshots/workout_tracker/*.png
   storage/raw_inputs/trainerapp_screenshots/form_review/*.png
   ... (see docs/TRAINERAPP_FEATURES_FOR_VIDEO.md)

2. Install MoviePy:
   pip install moviepy

3. Run:
   python create_social_videos.py --type all --count 75

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXAMPLES:

  Generate all 3 types (balanced mix):
    python create_social_videos.py --type all --count 75

  Just feature spotlights:
    python create_social_videos.py --type feature --count 50

  Just POV/relatable:
    python create_social_videos.py --type pov --count 20

  Just results/data:
    python create_social_videos.py --type results --count 10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    )

    parser.add_argument('--type', type=str, default='all',
                       choices=['all', 'feature', 'pov', 'results'],
                       help='Type of videos to generate')

    parser.add_argument('--count', type=int, default=75,
                       help='Total number of videos to generate')

    parser.add_argument('--check-only', action='store_true',
                       help='Check if screenshots exist without generating videos')

    args = parser.parse_args()

    # Welcome
    console.print("\n[bold cyan]🎬 TrainerApp.AI Social Video Generator[/bold cyan]")
    console.print("[dim]Option 1: App-First Approach[/dim]")
    console.print("━" * 60 + "\n")

    # Check MoviePy
    if not MOVIEPY_AVAILABLE and not args.check_only:
        console.print("[red]❌ MoviePy not installed![/red]")
        console.print("\nInstall with:")
        console.print("  pip install moviepy")
        console.print("\nOr run with --check-only to verify screenshots first")
        return

    compositor = VideoCompositor()

    # Check screenshot availability
    console.print("[bold]Step 1: Checking Screenshots[/bold]\n")

    missing_screenshots = check_screenshots_availability(compositor.screenshots_path)

    if missing_screenshots:
        console.print(f"[yellow]⚠️  Missing {len(missing_screenshots)} screenshot folders[/yellow]\n")

        for folder in missing_screenshots[:10]:  # Show first 10
            console.print(f"  • {folder}")

        console.print(f"\n[cyan]💡 See docs/TRAINERAPP_FEATURES_FOR_VIDEO.md for full list[/cyan]")

        if args.check_only:
            return
        else:
            console.print("\n[yellow]Continuing with available screenshots...[/yellow]\n")

    # Calculate video distribution
    if args.type == 'all':
        type1_count = int(args.count * 0.70)  # 70%
        type2_count = int(args.count * 0.20)  # 20%
        type3_count = int(args.count * 0.10)  # 10%
    elif args.type == 'feature':
        type1_count = args.count
        type2_count = 0
        type3_count = 0
    elif args.type == 'pov':
        type1_count = 0
        type2_count = args.count
        type3_count = 0
    else:  # results
        type1_count = 0
        type2_count = 0
        type3_count = args.count

    console.print(f"[bold]Step 2: Generating Videos[/bold]\n")
    console.print(f"  Type 1 (Feature Spotlight): {type1_count} videos")
    console.print(f"  Type 2 (POV/Relatable): {type2_count} videos")
    console.print(f"  Type 3 (Results/Data): {type3_count} videos")
    console.print()

    generated_videos = []

    # Generate Type 1 videos
    if type1_count > 0:
        console.print("[cyan]🎯 Generating Type 1: Feature Spotlights[/cyan]\n")
        generated_videos.extend(
            generate_type1_videos(compositor, type1_count, FEATURE_SPOTLIGHT_CONCEPTS)
        )

    # Generate Type 2 videos
    if type2_count > 0:
        console.print("\n[cyan]💭 Generating Type 2: POV/Relatable[/cyan]\n")
        generated_videos.extend(
            generate_type2_videos(compositor, type2_count, POV_RELATABLE_CONCEPTS)
        )

    # Generate Type 3 videos
    if type3_count > 0:
        console.print("\n[cyan]📊 Generating Type 3: Results/Data[/cyan]\n")
        generated_videos.extend(
            generate_type3_videos(compositor, type3_count, RESULTS_DATA_CONCEPTS)
        )

    # Summary
    console.print("\n" + "━" * 60)
    console.print("[bold green]✅ VIDEO GENERATION COMPLETE![/bold green]\n")
    console.print(f"📊 Generated: {len(generated_videos)} videos")
    console.print(f"📁 Location: {compositor.output_path}")
    console.print(f"⏱️  Average length: 10-15 seconds each")
    console.print(f"📱 Format: 1080x1920 (9:16 for Reels/TikTok)")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Review videos in storage/generated/videos/social/")
    console.print("  2. Add trending audio (use CapCut or similar)")
    console.print("  3. Schedule posts to Instagram & TikTok")
    console.print("  4. Post 2x/day on Instagram, 3x/day on TikTok")

    # Open folder
    import os
    os.system(f"open {compositor.output_path}")


def check_screenshots_availability(screenshots_path: Path) -> List[str]:
    """Check which screenshot folders exist"""

    required_folders = set()

    for concept in FEATURE_SPOTLIGHT_CONCEPTS:
        required_folders.add(concept['screenshots_folder'])

    for concept in RESULTS_DATA_CONCEPTS:
        required_folders.add(concept['screenshots_folder'])

    missing = []

    for folder in required_folders:
        folder_path = screenshots_path / folder
        if not folder_path.exists():
            missing.append(folder)

    return missing


def generate_type1_videos(
    compositor: VideoCompositor,
    count: int,
    concepts: List[Dict[str, Any]]
) -> List[Path]:
    """Generate Type 1 feature spotlight videos"""

    import itertools

    generated = []

    # Cycle through concepts
    concept_cycle = itertools.cycle(concepts)

    from tqdm import tqdm

    for i in tqdm(range(count), desc="Type 1 videos"):
        concept = next(concept_cycle)

        # Check if screenshots exist
        screenshots_folder = compositor.screenshots_path / concept['screenshots_folder']

        if not screenshots_folder.exists():
            console.print(f"[yellow]⚠️  Skipping {concept['feature']} - no screenshots[/yellow]")
            continue

        # Get screenshots
        screenshots = []
        for filename in concept['screenshots_needed']:
            path = screenshots_folder / filename
            if path.exists():
                screenshots.append(path)

        if len(screenshots) < 2:
            console.print(f"[yellow]⚠️  Skipping {concept['feature']} - not enough screenshots[/yellow]")
            continue

        # Pick a random hook variation
        import random
        hook = random.choice(concept['hooks'])

        try:
            video_path = compositor.create_type1_feature_spotlight(
                feature_name=concept['feature'],
                screenshots=screenshots[:3],  # Use first 3
                text_overlays=concept['text_overlays'][:3],
                hook=hook,
                cta=concept['cta']
            )

            generated.append(video_path)

        except Exception as e:
            console.print(f"[red]Failed to create {concept['feature']}: {str(e)}[/red]")
            continue

    return generated


def generate_type2_videos(
    compositor: VideoCompositor,
    count: int,
    concepts: List[Dict[str, Any]]
) -> List[Path]:
    """Generate Type 2 POV/relatable videos"""

    import itertools

    generated = []
    concept_cycle = itertools.cycle(concepts)

    from tqdm import tqdm

    for i in tqdm(range(count), desc="Type 2 videos"):
        concept = next(concept_cycle)

        try:
            video_path = compositor.create_type2_pov_relatable(concept)
            generated.append(video_path)

        except Exception as e:
            console.print(f"[red]Failed to create {concept['title']}: {str(e)}[/red]")
            continue

    return generated


def generate_type3_videos(
    compositor: VideoCompositor,
    count: int,
    concepts: List[Dict[str, Any]]
) -> List[Path]:
    """Generate Type 3 results/data videos"""

    import itertools

    generated = []
    concept_cycle = itertools.cycle(concepts)

    from tqdm import tqdm

    for i in tqdm(range(count), desc="Type 3 videos"):
        concept = next(concept_cycle)

        # Check if screenshots exist
        screenshots_folder = compositor.screenshots_path / concept['screenshots_folder']

        if not screenshots_folder.exists():
            console.print(f"[yellow]⚠️  Skipping {concept['title']} - no screenshots[/yellow]")
            continue

        # Get screenshots
        screenshots = []
        for filename in concept['screenshots_needed']:
            path = screenshots_folder / filename
            if path.exists():
                screenshots.append(path)

        if not screenshots:
            console.print(f"[yellow]⚠️  Skipping {concept['title']} - no screenshots[/yellow]")
            continue

        try:
            video_path = compositor.create_type3_results_data(
                progress_screenshots=screenshots,
                timeline_text=concept['timeline'],
                title=concept['title'].replace('_', ' ').title(),
                insight=concept['insight']
            )

            generated.append(video_path)

        except Exception as e:
            console.print(f"[red]Failed to create {concept['title']}: {str(e)}[/red]")
            continue

    return generated


if __name__ == "__main__":
    main()
