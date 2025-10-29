# 🎯 Realistic Content Generation Guide

## The Problem

Pure AI generation (text-to-image) creates:
- ❌ AI-looking people (uncanny valley)
- ❌ Morphed hands and equipment
- ❌ Wrong exercise form
- ❌ Fake UI text that doesn't match your app

## The Solutions

### ✅ **OPTION 1: Stock Photos + UI Overlay** (RECOMMENDED)

**Best for**: Quick, reliable results with zero morphing

```bash
# Get free Pexels API key
# https://www.pexels.com/api/

# Add to .env
PEXELS_API_KEY=your_key_here

# Run
python scripts/simple_stock_composite.py
```

**Pros:**
- ✅ Zero morphing (real photos)
- ✅ Free (except stock license)
- ✅ Fast (no AI generation)
- ✅ Reliable quality

**Cons:**
- ⚠️  Limited to stock library
- ⚠️  UI may look "pasted on"

---

### ✅ **OPTION 2: Very Light img2img**

**Best for**: When you need variations but want to keep realism

Use strength 0.2-0.4 (not 0.7):

```bash
python test_low_strength.py
```

**How it works:**
- `strength=0.2` → 80% original, 20% AI changes
- `strength=0.5` → 50/50 mix
- `strength=0.7` → 30% original, 70% AI (causes morphing!)

---

### ✅ **OPTION 3: Simpler Scenarios**

**Avoid complex gym scenes**. Use simpler scenarios:

#### ✅ GOOD Scenarios (Less Morphing)

**Close-ups:**
```bash
--prompt "Close-up of hand holding iPhone showing TrainerApp.AI workout screen, rest timer visible, gym in background blur"
```

**Simple positions:**
```bash
--prompt "Person standing in gym holding phone, checking workout progress, natural pose"
```

**Post-workout:**
```bash
--prompt "Athlete taking selfie post-workout, phone showing completed workout summary"
```

**Outdoor/Home:**
```bash
--prompt "Person doing yoga at home, phone propped against water bottle showing yoga flow"
--prompt "Runner in park checking phone for running stats"
```

#### ❌ AVOID (High Morphing Risk)

- ❌ Complex gym equipment (barbells, cables, machines)
- ❌ Hands gripping equipment + phone visible
- ❌ Multiple people interacting
- ❌ Fast motion (jumping, running)
- ❌ Complex poses (handstands, olympic lifts)

---

## Recommended Workflow

### For Maximum Quality:

**Step 1: Use Real Stock Photos**
```bash
# Fetch 50 diverse stock photos
python scripts/simple_stock_composite.py
```

**Step 2: Manually Select Best Ones**
- Choose photos where phone placement makes sense
- Look for natural poses
- Check lighting and composition

**Step 3: Composite Your UI**
- Adjust position/scale for each image
- Add perspective for realism

**Step 4: Minor Touch-ups (Optional)**
- Use Photoshop/Canva for final adjustments
- Add text overlays
- Adjust colors

---

## Cost Comparison

| Approach | Cost per Image | Quality | Time |
|----------|---------------|---------|------|
| Pure AI (old) | $0.025 | ⚠️  Morphing issues | 20s |
| Stock + Overlay | ~$0.00* | ✅ Real photos | 2s |
| img2img (low strength) | $0.025 | ⚠️  Some morphing | 25s |

*Pexels is free, but check license for commercial use

---

## Quick Start

1. **Get Pexels API key**: https://www.pexels.com/api/
2. **Add to .env**: `PEXELS_API_KEY=your_key`
3. **Add your app screenshots** to `storage/raw_inputs/`
4. **Run**: `python scripts/simple_stock_composite.py`

---

## Examples

### Simple Scenario That Works

```bash
python scripts/create_realistic_content.py \
  --ui storage/raw_inputs/test_ui.png \
  --prompt "Person sitting on bench in gym, resting between sets, checking phone for next exercise" \
  --count 10 \
  --strength 0.3
```

### Even Simpler (Just UI on Stock Photos)

```bash
python scripts/simple_stock_composite.py
```

This fetches 10 real stock photos and adds your UI. Zero AI generation = zero morphing.

---

## If You Still Get Morphing

1. **Lower the strength**: Try 0.2 or 0.3
2. **Use simpler prompts**: Less details = less chance of errors
3. **Skip img2img entirely**: Just use stock photos
4. **Manual compositing**: Use Photoshop/Canva for complex scenes

---

## Pro Tip: Hybrid Approach

For best results:
1. Use stock photos as base (real people, correct form)
2. Composite your real UI screenshots (readable text)
3. Add text overlays in Canva/Photoshop (captions, CTAs)
4. Minimal or no AI generation

This gives you production-quality content that looks 100% real.
