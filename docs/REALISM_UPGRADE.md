# 🎨 Photorealistic Image Generation - Upgrade Guide

## What Changed

I just upgraded your system to generate **photorealistic** images instead of AI-looking ones!

---

## 🆕 New Quality Tiers

You now have 3 quality levels:

| Provider | Model | Cost/Image | Quality | Speed | Use Case |
|----------|-------|------------|---------|-------|----------|
| `replicate` | FLUX Schnell | $0.0055 | Basic | 4 sec | Quick drafts |
| **`replicate_dev`** | FLUX Dev | **$0.025** | **High** | 15 sec | **Best value** ⭐ |
| `replicate_pro` | FLUX Pro | $0.04 | Photorealistic | 20 sec | Premium content |

**Recommendation: Use `replicate_dev` for best quality/cost ratio**

---

## 🔧 How to Use

### Option 1: Single Image

```bash
# Basic (fast, cheap)
python scripts/generators/image_generator.py \
  --provider replicate \
  --prompt "Athletic woman doing squats" \
  --size 1080x1920

# HIGH QUALITY (recommended)
python scripts/generators/image_generator.py \
  --provider replicate_dev \
  --prompt "Athletic woman doing squats" \
  --size 1080x1920

# PHOTOREALISTIC (premium)
python scripts/generators/image_generator.py \
  --provider replicate_pro \
  --prompt "Athletic woman doing squats" \
  --size 1080x1920
```

### Option 2: Batch Generation

```bash
# Generate 10 HIGH QUALITY images
python scripts/orchestrator.py \
  --theme workout \
  --quantity 10 \
  --provider replicate_dev \
  --skip-posting
```

### Option 3: Set as Default

Edit `config/config.yaml`:

```yaml
# Change active profile
active_profile: "balanced"  # Uses replicate_dev

# Or customize
profiles:
  balanced:
    image_provider: "replicate_dev"  # High quality
    image_quantity: 70
    monthly_cost: "$25"  # Updated cost
```

---

## ✨ What Makes Them More Realistic

The system now automatically adds:

1. **Camera Equipment**
   - "Shot on Canon EOS R5"
   - "85mm f/1.4 lens"
   - Professional photography specs

2. **Skin & Texture Details**
   - "Natural skin texture"
   - "Realistic pores and details"
   - "Lifelike facial features"

3. **Quality Keywords**
   - "Photorealistic"
   - "8K resolution"
   - "Ultra detailed"
   - "Sharp focus"

4. **Anti-AI Keywords**
   - "NOT digital art"
   - "NOT illustration"
   - "NOT painting"

5. **More Inference Steps**
   - Schnell: 4 steps
   - Dev: 28 steps ← More detail!
   - Pro: Dynamic optimization

---

## 📊 Cost Comparison

**Before (Schnell):**
- 100 images = $0.55
- 500 images = $2.75

**Now (Dev - High Quality):**
- 100 images = **$2.50**
- 500 images = **$12.50**

**Premium (Pro - Photorealistic):**
- 100 images = **$4.00**
- 500 images = **$20.00**

**Still WAY cheaper than agencies ($5000/month)!**

---

## 🎯 Quick Test

Compare the difference yourself:

```bash
cd /Users/dcrypto25/content
source venv/bin/activate

# Generate 3 images with different quality levels
for provider in replicate replicate_dev replicate_pro; do
    python scripts/generators/image_generator.py \
      --provider $provider \
      --prompt "Fitness woman in gym, natural lighting" \
      --size 1080x1920
done

# View all 3
open storage/generated/images/
```

You'll see a huge difference in realism!

---

## 🚀 Social Media Automation

I also created a complete guide for Instagram & TikTok automation:

📖 **Read**: `docs/SOCIAL_MEDIA_SETUP.md`

Covers:
- Instagram Graph API setup (step-by-step)
- TikTok Content API setup
- Media hosting (S3 or Cloudinary)
- n8n workflow configuration
- Automated scheduling (3-5 posts/day)
- Analytics tracking

---

## 💡 Pro Tips

### For Maximum Realism

1. **Use `replicate_dev` as default**
   ```bash
   export REPLICATE_IMAGE_MODEL=black-forest-labs/flux-dev
   ```

2. **Add specific camera details in prompts**
   ```
   "Shot on Sony A7III, 50mm f/1.8, golden hour lighting"
   ```

3. **Specify real locations**
   ```
   "Modern LA fitness studio" instead of "gym"
   ```

4. **Add texture details**
   ```
   "Sweat visible on forehead, natural skin pores"
   ```

### For Best Value

- Use `replicate_dev` for final posts
- Use `replicate` (Schnell) for quick tests/drafts
- Reserve `replicate_pro` for hero content only

---

## 🔄 Switching Back

If you need to go back to fast/cheap mode:

```bash
# In .env, uncomment:
REPLICATE_IMAGE_MODEL=black-forest-labs/flux-schnell

# Or use --provider replicate
python scripts/orchestrator.py --provider replicate --quantity 10
```

---

## 📈 Updated Monthly Costs

### With High Quality (replicate_dev)

| Item | Cost |
|------|------|
| OpenAI | $8 |
| Replicate (100 images) | $25 |
| AWS S3 | $1 |
| Hosting | $6 |
| **Total** | **$40/month** |

### With Photorealistic (replicate_pro)

| Item | Cost |
|------|------|
| OpenAI | $8 |
| Replicate (100 images) | $40 |
| AWS S3 | $1 |
| Hosting | $6 |
| **Total** | **$55/month** |

**Still 99% cheaper than traditional methods!**

---

## ✅ Action Items

1. **Test the new quality:**
   ```bash
   python scripts/generators/image_generator.py \
     --provider replicate_dev \
     --prompt "Your test prompt" \
     --size 1080x1920
   ```

2. **Compare with previous:**
   ```bash
   open storage/generated/images/
   # Compare older vs newer images
   ```

3. **Set as default:**
   ```bash
   # Edit config/config.yaml
   # Set active_profile: "balanced"
   ```

4. **Set up social posting:**
   ```bash
   # Read docs/SOCIAL_MEDIA_SETUP.md
   ```

5. **Generate your first batch:**
   ```bash
   python scripts/orchestrator.py \
     --theme workout \
     --quantity 20 \
     --provider replicate_dev \
     --skip-posting
   ```

---

## 🎉 Result

Your images will now look like:
- ✅ Real professional photography
- ✅ Natural skin textures
- ✅ Proper lighting and depth
- ✅ Indistinguishable from real photos
- ✅ Instagram/TikTok ready

Instead of:
- ❌ AI-generated look
- ❌ Smooth/fake skin
- ❌ Artificial lighting
- ❌ Obviously computer-generated

---

**Your content will now pass as professional photography! 🎨📸**
