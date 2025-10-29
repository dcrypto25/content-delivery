# 🎉 NEW FEATURE: Input-Based Content Generation

## What's New

You can now turn **any image or video** into **unlimited variations** with custom descriptions!

---

## 🚀 Super Simple Usage

```bash
python create_content.py \
  --input competitor_ad.jpg \
  --what "Create workout content like this but featuring TrainerApp.AI" \
  --how-many 50
```

**That's it!** The AI will analyze the input and generate 50 unique variations based on your description.

---

## 📸 Perfect For

- **Competitor Analysis** - Recreate successful competitor ads with your branding
- **Feature Showcase** - Turn app screenshots into real-world social content
- **Viral Recreation** - Make your own versions of viral fitness content
- **Brand Variations** - Generate unlimited variations of your hero content

---

## 💡 Real Examples

### Example 1: From Competitor Ad

```bash
python create_content.py \
  --input peloton_viral_ad.jpg \
  --what "Create similar high-energy workout content but show TrainerApp.AI's AI coach feature on phone screens" \
  --how-many 30 \
  --quality high
```

**Output:** 30 images similar to competitor but with your branding
**Cost:** $0.75

---

### Example 2: From Website Screenshot

```bash
python create_content.py \
  --input workout_tracker_screenshot.png \
  --what "Show real people using this feature in gyms and at home, with the app visible on their phones" \
  --variations "gym" "home" "park" "hotel" \
  --how-many 40
```

**Output:** 40 photorealistic images in 4 different settings
**Cost:** $1.00

---

### Example 3: From URL

```bash
python create_content.py \
  --url "https://instagram.com/p/viral-post/image.jpg" \
  --what "Recreate with diverse body types and TrainerApp.AI branding" \
  --how-many 20
```

**Output:** 20 variations of viral content with your brand
**Cost:** $0.50

---

## ⚡ Key Features

1. **AI Vision Analysis** - Automatically understands what makes content work
2. **Custom Descriptions** - You control the output with natural language
3. **Style Options** - Similar, opposite, or inspired_by
4. **Variations** - Generate multiple settings/contexts automatically
5. **Quality Tiers** - Fast, high, or premium quality

---

## 📚 Full Documentation

Read the complete guide: **`docs/INPUT_BASED_GENERATION.md`**

Includes:
- Detailed examples
- Writing great descriptions
- Style options explained
- Batch processing workflows
- Pro tips and best practices

---

## 💰 Cost

**High Quality (Recommended):**
- 10 images = $0.25
- 50 images = $1.25
- 100 images = $2.50

**Still 99% cheaper than hiring designers!**

---

## 🎯 Quick Start

1. **Test with 5 images:**

```bash
python create_content.py \
  --input your_image.jpg \
  --what "Your description here" \
  --how-many 5 \
  --quality fast
```

2. **Generate full batch:**

```bash
python create_content.py \
  --input your_image.jpg \
  --what "Your refined description" \
  --how-many 50 \
  --quality high
```

3. **View results:**

```bash
open storage/generated/images/
```

---

## 🔥 Pro Tip

**Write Better Descriptions:**

❌ Bad: "Make workout content"

✅ Good: "Create energetic HIIT workout content showing TrainerApp.AI's timer feature on phone screens, with diverse people (ages 25-45, various body types) in modern gyms and outdoor parks. Natural lighting, authentic sweat, determined expressions."

**The more specific, the better the output!**

---

**Try it now!** 🚀
