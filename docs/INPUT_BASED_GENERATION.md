# 🎨 Input-Based Content Generation Guide

## Overview

Turn **any input image or video** into **unlimited variations** with custom descriptions.

**Perfect for:**
- 📱 Analyzing competitor ads and creating better versions
- 🖥️ Turning website features into social media content
- 🎥 Recreating viral content with your brand
- 🔄 Creating variations of successful posts

---

## 🚀 Quick Start

### Super Simple Interface

```bash
python create_content.py \
  --input competitor_ad.jpg \
  --what "Create workout motivation content like this but featuring TrainerApp.AI" \
  --how-many 20
```

**That's it!** The AI will:
1. ✅ Analyze the input image
2. ✅ Understand your description
3. ✅ Generate 20 unique variations
4. ✅ Create photorealistic images

---

## 📋 How It Works

### The Magic Formula:

```
Input Image/Video + Your Description = Unlimited Variations
```

**Step 1: AI Vision Analysis**
- Analyzes composition, style, people, setting, lighting
- Extracts key elements and message
- Identifies what makes it work

**Step 2: Merge with Your Description**
- Combines AI analysis with your creative direction
- Creates comprehensive content brief
- Generates diverse prompt variations

**Step 3: Content Generation**
- Creates unique variations maintaining core appeal
- Ensures diversity (body types, ages, locations)
- Integrates your brand (TrainerApp.AI)

---

## 💡 Real-World Examples

### Example 1: Competitor Ad Analysis

**Input:** Competitor's viral TikTok screenshot

```bash
python create_content.py \
  --input peloton_ad.jpg \
  --what "Create similar high-energy workout content but show our AI coach feature on the phone screen" \
  --how-many 50 \
  --quality high
```

**Output:** 50 variations showing:
- Similar energy and composition
- TrainerApp.AI interface visible
- Diverse people and settings
- Your branding

**Cost:** $1.25 (50 × $0.025)

---

### Example 2: Website Feature → Social Content

**Input:** Screenshot of your app's workout tracker

```bash
python create_content.py \
  --input workout_tracker_screenshot.png \
  --what "Show people actually using this feature in real gyms and at home, with the app interface visible on their phones" \
  --how-many 30 \
  --variations "gym" "home" "outdoor park" "office"
```

**Output:** 30 images showing:
- Real people using the app
- App interface integrated naturally
- 4 different settings
- Photorealistic quality

**Cost:** $0.75 (30 × $0.025)

---

### Example 3: Opposite Style

**Input:** Dark, intense gym photography

```bash
python create_content.py \
  --input dark_gym.jpg \
  --what "Bright, energetic morning workout vibes with natural lighting" \
  --style opposite \
  --how-many 25
```

**Output:** Complete opposite aesthetic while maintaining fitness theme

---

### Example 4: Recreate Viral Content

**Input:** Viral fitness transformation post

```bash
python create_content.py \
  --url "https://instagram.com/p/viral-post/image.jpg" \
  --what "Create before/after transformation content showing TrainerApp.AI results with diverse body types" \
  --how-many 40 \
  --quality premium
```

**Output:** Professional transformation content with your branding

**Cost:** $1.60 (40 × $0.04 premium quality)

---

## 🎯 Command Line Options

### Required Arguments

```bash
# Input source (choose one)
--input, -i        Path to local image/video
--url, -u          URL to image/video

# Description (required!)
--what, -w         Describe what you want the output to look like
```

### Optional Arguments

```bash
# Quantity
--how-many, -n     Number of variations (default: 10)

# Style direction
--style, -s        How to use input
                   • similar (default) - Create similar content
                   • opposite - Create contrasting content
                   • inspired_by - Use as inspiration only

# Quality level
--quality, -q      Image quality
                   • fast ($0.0055, 4 sec) - Quick drafts
                   • high ($0.025, 15 sec) - Recommended ⭐
                   • premium ($0.04, 20 sec) - Photorealistic

# Specific variations
--variations, -v   Space-separated variations
                   Example: --variations "gym" "home" "park"

# Theme override
--theme, -t        Force specific theme
                   • workout
                   • nutrition
                   • motivation
                   • app_features

# Prompts only
--prompts-only     Generate prompts without creating images
```

---

## 📝 Writing Great Descriptions

### The `--what` Parameter is Key!

**Bad Description:**
```bash
--what "Make it better"
```

**Good Description:**
```bash
--what "Create energetic workout content showing the AI coach feature on phone screens, with diverse people in modern gyms"
```

**Great Description:**
```bash
--what "Transform this into TrainerApp.AI ads showing real people using the workout tracker feature. Focus on the moment of achievement - finishing a tough set, checking their phone for next exercise, smiling at their progress. Use natural lighting, diverse body types (athletic, average, curvy), ages 25-45, in both gym and home settings. Include visible app UI showing rep counter and AI coach suggestions."
```

### Pro Tips:

✅ **Be Specific:**
- ❌ "Make workout content"
- ✅ "Show HIIT workouts in outdoor parks with TrainerApp.AI timer visible"

✅ **Mention Your Product:**
- ❌ "Fitness motivation"
- ✅ "People using TrainerApp.AI's AI coach feature mid-workout"

✅ **Describe the Setting:**
- ❌ "At the gym"
- ✅ "Modern boutique gym with natural lighting and plants"

✅ **Include Diversity:**
- ❌ "Athlete working out"
- ✅ "Diverse people (various body types, ages, ethnicities) doing strength training"

✅ **Add Emotional Context:**
- ❌ "Person exercising"
- ✅ "Person feeling accomplished after crushing a workout, checking their TrainerApp.AI progress"

---

## 🎨 Style Options Explained

### `--style similar` (Default)

**Use when:** You want content like the input but with variations

**Example:**
```bash
--input successful_ad.jpg \
--what "More ads like this but different exercises and people" \
--style similar
```

**Result:** Maintains composition, energy, style but varies specifics

---

### `--style opposite`

**Use when:** You want to contrast the input

**Example:**
```bash
--input dark_moody_gym.jpg \
--what "Bright, happy, morning energy" \
--style opposite
```

**Result:** Complete opposite aesthetic (dark → bright, intense → cheerful)

---

### `--style inspired_by`

**Use when:** You like elements but want something different

**Example:**
```bash
--input competitor_ad.jpg \
--what "Use the energy level but make it about nutrition instead of workouts" \
--style inspired_by
```

**Result:** Captures essence but creates original content

---

## 🔄 Workflow Examples

### Workflow 1: Analyze → Refine → Generate

```bash
# Step 1: Analyze and create prompts only
python create_content.py \
  --input input.jpg \
  --what "Your description" \
  --how-many 50 \
  --prompts-only

# Step 2: Review prompts in storage/metadata/

# Step 3: Generate images
python create_content.py \
  --input input.jpg \
  --what "Your description" \
  --how-many 50
```

---

### Workflow 2: Test → Scale

```bash
# Step 1: Test with 5 fast images
python create_content.py \
  --input input.jpg \
  --what "Your description" \
  --how-many 5 \
  --quality fast

# Step 2: Review and refine description

# Step 3: Generate full batch with high quality
python create_content.py \
  --input input.jpg \
  --what "Refined description" \
  --how-many 100 \
  --quality high
```

---

### Workflow 3: Competitive Analysis

```bash
# Analyze top 5 competitor ads
for ad in competitor_*.jpg; do
    python create_content.py \
      --input "$ad" \
      --what "Create better version featuring TrainerApp.AI" \
      --how-many 20 \
      --quality high
done
```

---

## 📊 Output Structure

After running, you'll get:

```
storage/
├── raw_inputs/
│   └── input_20251028_123456.jpg          ← Downloaded/saved input
├── metadata/
│   └── input_processed_20251028_123456.json  ← Analysis + prompts
└── generated/
    └── images/
        ├── wor_001.jpg                     ← Generated variations
        ├── wor_002.jpg
        └── ...
```

**Metadata file contains:**
```json
{
  "input_file": "path/to/input.jpg",
  "user_description": "Your --what description",
  "vision_analysis": {
    "scene": "...",
    "subject": "...",
    "emotion": "...",
    "style": "..."
  },
  "content_brief": {
    "core_message": "...",
    "visual_style": "...",
    "key_elements": ["...", "..."],
    "target_audience": "..."
  },
  "prompts": [
    {
      "prompt": "Detailed generation prompt",
      "variant_id": "wor_001",
      "platform": "instagram",
      "estimated_virality": "high"
    }
  ]
}
```

---

## 💰 Cost Examples

| Scenario | Quantity | Quality | Cost |
|----------|----------|---------|------|
| Quick test | 5 | Fast | $0.03 |
| Small batch | 20 | High | $0.50 |
| Medium batch | 50 | High | $1.25 |
| Large batch | 100 | High | $2.50 |
| Premium batch | 50 | Premium | $2.00 |

**Still 99% cheaper than hiring a designer ($500+ for 50 images)!**

---

## 🎯 Use Cases & Templates

### Use Case 1: Competitor Ad Replication

```bash
python create_content.py \
  --input competitors/peloton_ad.jpg \
  --what "Recreate this ad style but show TrainerApp.AI's AI coach giving real-time form corrections during workouts. Keep the high energy but make it about our personalized training technology." \
  --how-many 30 \
  --quality high
```

---

### Use Case 2: Feature Launch

```bash
python create_content.py \
  --input screenshots/new_feature.png \
  --what "Turn this app screenshot into real-world usage scenarios. Show people actually using this feature in their daily workouts - checking their phone between sets, following the AI recommendations, tracking their progress. Include diverse people and settings." \
  --variations "gym" "home" "park" "travel" \
  --how-many 40 \
  --theme app_features
```

---

### Use Case 3: Viral Content Recreation

```bash
python create_content.py \
  --url "https://tiktok.com/@fitness/viral-video-thumbnail.jpg" \
  --what "Create content with the same energy and composition but featuring TrainerApp.AI users. Show the moment of breakthrough - when the AI coach helps someone perfect their form or achieve a PR." \
  --how-many 25 \
  --style inspired_by
```

---

### Use Case 4: Seasonal Campaign

```bash
python create_content.py \
  --input campaigns/summer_body.jpg \
  --what "New Year fitness resolution content. Show people starting their fitness journey with TrainerApp.AI in January. Focus on determination, fresh starts, and having an AI coach to guide them. Winter gym lighting, people in new workout gear." \
  --how-many 60 \
  --quality premium
```

---

## 🔧 Advanced Usage

### Batch Processing Multiple Inputs

```bash
#!/bin/bash
# Process all competitor ads

for input_file in competitors/*.jpg; do
    echo "Processing: $input_file"

    python create_content.py \
      --input "$input_file" \
      --what "Create TrainerApp.AI version of this ad" \
      --how-many 15 \
      --quality high

    sleep 5  # Rate limiting
done
```

---

### Integration with Orchestrator

```bash
# Generate prompts from input
python create_content.py \
  --input competitor.jpg \
  --what "Your description" \
  --how-many 50 \
  --prompts-only

# Then use orchestrator for full pipeline
python scripts/orchestrator.py \
  --batch storage/metadata/input_processed_*.json \
  --provider replicate_dev
```

---

## ⚠️ Best Practices

### Do's ✅

- ✅ Be specific in descriptions
- ✅ Mention your product/features
- ✅ Request diversity in people and settings
- ✅ Test with --prompts-only first
- ✅ Start with small batches (10-20)
- ✅ Use high quality as default
- ✅ Keep input images high resolution

### Don'ts ❌

- ❌ Use copyrighted competitor images publicly
- ❌ Be too vague in descriptions
- ❌ Generate thousands at once (rate limits)
- ❌ Use low-res inputs
- ❌ Skip the description (it's crucial!)

---

## 🎓 Tips from Experience

### Tip 1: Layer Your Descriptions

Good → Better → Best:

**Good:**
```
"Workout content with app"
```

**Better:**
```
"People using TrainerApp.AI during workouts in gyms"
```

**Best:**
```
"Diverse people (ages 25-50, various body types) checking TrainerApp.AI on their phones during gym workouts. Show the moment they complete a set and look at the app for their next exercise. Natural gym lighting, modern equipment, visible sweat showing effort. App UI should show rep counter and AI coach suggestions."
```

---

### Tip 2: Use Variations for Settings

```bash
--variations "24hr gym 2am" "home living room 6am" "outdoor park noon" "hotel gym 8pm"
```

This creates the same content in 4 different contexts automatically!

---

### Tip 3: Refine Based on Output

1. Generate 5 test images
2. See what works
3. Refine description
4. Generate full batch

---

## 🚀 Next Steps

Now that you can create custom content:

1. **Analyze Your Competitors**
   - Save their top-performing ads
   - Create better versions

2. **Showcase Your Features**
   - Screenshot your app
   - Turn into social content

3. **Recreate Viral Content**
   - Find viral fitness posts
   - Create your own versions

4. **Build a Content Library**
   - 500+ variations from 5-10 inputs
   - Never run out of content

---

## 💡 Pro Workflow

```bash
# Monday: Analyze competitors
python create_content.py --input competitor1.jpg --what "..." --how-many 20
python create_content.py --input competitor2.jpg --what "..." --how-many 20

# Tuesday: Feature showcase
python create_content.py --input feature1.png --what "..." --how-many 30

# Wednesday: Viral recreation
python create_content.py --url "viral_post_url" --what "..." --how-many 25

# Result: 95 unique posts from 4 inputs!
```

---

**You can now turn ANY input into unlimited content variations!** 🎨🚀
