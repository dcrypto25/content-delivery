# TrainerApp.AI - Automated Content System 🚀

> **Generate 100-500+ social media posts from a single input. Fully automated. Under $50/month.**

An enterprise-grade content automation pipeline that transforms one piece of content into hundreds of unique, high-performing Instagram Reels and TikTok videos using AI.

---

## 🎯 What This Does

1. **Input**: Upload ONE screenshot, URL, or competitor post
2. **AI Analysis**: GPT-4o Vision analyzes and extracts key elements
3. **Prompt Generation**: GPT-4o-mini creates 100-500 unique variations
4. **Asset Generation**:
   - Images via Replicate FLUX ($0.0055 each) or Google Gemini
   - Videos via Runway Gen-3 (optional)
5. **Enhancement**: Auto-adds captions, hashtags, watermarks
6. **Scheduling**: Posts 3-5 times daily to Instagram + TikTok
7. **Analytics**: Tracks performance and auto-optimizes

**Result**: Never run out of content. Infinite variations. Viral-optimized. Fully automated.

---

## 📊 Cost Breakdown (500 Assets/Month)

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| **OpenAI** | $8 | Vision + prompt generation |
| **Replicate (Images)** | $11 | 400 images @ $0.0055/each |
| **Runway (Videos)** | $28 | 100 videos (optional) |
| **DigitalOcean** | $6 | Self-hosted n8n |
| **Total** | **$47/mo** | Scales to $100 at 1000+ posts |

Compare to: Hiring a content creator ($2000+/mo) or agencies ($5000+/mo)

---

## ⚡ Features

- ✅ **Multi-Provider Support**: Replicate, Gemini, Runway, OpenAI
- ✅ **Cost Optimized**: Automatic fallbacks to cheapest options
- ✅ **Diversity Built-In**: Body types, ethnicities, ages, locations
- ✅ **Platform Optimized**: Different prompts for IG vs TikTok
- ✅ **Auto-Scheduling**: n8n workflows handle posting cadence
- ✅ **Analytics Feedback**: Learns what performs best
- ✅ **Watermarking**: Brand protection
- ✅ **Hashtag Optimization**: Trending + evergreen mix
- ✅ **Rate Limiting**: Respects API limits
- ✅ **Error Handling**: Automatic retries + fallbacks

---

## 🏗️ Architecture

```
Input (Screenshot/URL)
    ↓
GPT-4o Vision Analysis
    ↓
GPT-4o-mini Prompt Generation (100-500 prompts)
    ↓
┌─────────────────┴─────────────────┐
│                                    │
Replicate FLUX              Runway Gen-3
(Images)                    (Videos)
│                                    │
└─────────────────┬─────────────────┘
                  ↓
         Enhancement Layer
    (Captions, Hashtags, Watermarks)
                  ↓
         Google Drive Storage
                  ↓
         n8n Scheduler (Cron)
                  ↓
         ┌────────┴────────┐
         │                 │
    Instagram          TikTok
         │                 │
         └────────┬────────┘
                  ↓
         Analytics Feedback
         (Auto-optimize prompts)
```

---

## 📁 Project Structure

```
content-delivery/
├── config/
│   ├── config.yaml           # Main configuration
│   └── google-credentials.json  # API credentials
├── scripts/
│   ├── utils.py              # Shared utilities
│   ├── orchestrator.py       # Main pipeline controller
│   ├── generators/
│   │   ├── prompt_generator.py    # AI prompt engineering
│   │   ├── image_generator.py     # Image generation
│   │   └── video_generator.py     # Video generation (TODO)
│   ├── uploaders/
│   │   ├── instagram_uploader.py  # IG posting
│   │   └── tiktok_uploader.py     # TikTok posting
│   └── analytics/
│       └── collect_metrics.py     # Performance tracking
├── workflows/
│   └── trainerapp-automation-workflow.json  # n8n workflow
├── storage/
│   ├── raw_inputs/           # Original uploads
│   ├── generated/            # Generated assets
│   │   ├── images/
│   │   └── videos/
│   ├── processed/            # Platform-ready
│   └── metadata/             # Prompts + analytics
├── templates/
│   ├── prompts/              # Prompt templates
│   ├── captions/             # Caption templates
│   └── hashtags/             # Hashtag strategies
├── logs/                     # System logs
├── docker-compose.yml        # Full stack deployment
├── Dockerfile                # Python app container
├── requirements.txt          # Python dependencies
└── .env.example              # Environment template
```

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

- Ubuntu 20.04+ server (or DigitalOcean droplet)
- Docker + Docker Compose
- API keys (see below)

### Step 1: Clone & Configure

```bash
git clone https://github.com/dcrypto25/content-delivery.git
cd content-delivery

# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### Step 2: Get API Keys

#### Required:
1. **OpenAI** (https://platform.openai.com/api-keys)
   - Create account → Generate API key
   - Add $10 credit

2. **Replicate** (https://replicate.com/account/api-tokens)
   - Sign up → Get API token
   - Add $10 credit

#### Optional (for social posting):
3. **Instagram** (https://developers.facebook.com/)
   - Create Facebook App
   - Connect Instagram Business Account
   - Get Access Token (see guide below)

4. **TikTok** (https://developers.tiktok.com/)
   - Apply for Developer Access
   - Create app → Get Client Key/Secret
   - Complete OAuth flow (see guide below)

### Step 3: Deploy with Docker

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f content-generator
```

### Step 4: Test Generation

```bash
# Test prompt generation
docker exec -it trainerapp-generator python scripts/generators/prompt_generator.py \
    --theme workout --quantity 5

# Test image generation
docker exec -it trainerapp-generator python scripts/generators/image_generator.py \
    --prompt "Fitness woman doing squats in gym" --provider replicate

# Run full pipeline (no posting)
docker exec -it trainerapp-generator python scripts/orchestrator.py \
    --theme nutrition --quantity 10 --skip-posting
```

### Step 5: Access n8n Dashboard

1. Open browser: `http://your-server-ip:5678`
2. Login with credentials from `.env`
3. Import workflow: `workflows/trainerapp-automation-workflow.json`
4. Activate workflow

---

## 🔑 Detailed Setup Guides

### Instagram API Setup

1. **Create Facebook Page**
   - Go to https://www.facebook.com/pages/create
   - Create business page

2. **Connect Instagram**
   - Settings → Instagram → Connect Account
   - Must be Instagram Business/Creator account

3. **Create Facebook App**
   - https://developers.facebook.com/apps/create
   - Type: Business
   - Add "Instagram" product

4. **Get Long-Lived Token**
   ```bash
   # Get short-lived token from Graph API Explorer
   # Then exchange for long-lived:
   curl "https://graph.facebook.com/v21.0/oauth/access_token?
       grant_type=fb_exchange_token&
       client_id=YOUR_APP_ID&
       client_secret=YOUR_APP_SECRET&
       fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

5. **Add to .env**
   ```
   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_id
   ```

### TikTok API Setup

1. **Apply for Developer Access**
   - https://developers.tiktok.com/
   - Complete application (1-2 weeks approval)
   - Use case: "Educational fitness content automation"

2. **Create App**
   - Developer Portal → Create App
   - Select "Content Posting API" scope

3. **OAuth Flow**
   ```bash
   # Authorization URL (replace YOUR_CLIENT_KEY):
   https://www.tiktok.com/v2/auth/authorize/?
       client_key=YOUR_CLIENT_KEY&
       scope=user.info.basic,video.publish&
       response_type=code&
       redirect_uri=YOUR_REDIRECT_URI

   # Exchange code for token:
   curl -X POST 'https://open.tiktokapis.com/v2/oauth/token/' \
       -H 'Content-Type: application/json' \
       -d '{
           "client_key": "YOUR_CLIENT_KEY",
           "client_secret": "YOUR_CLIENT_SECRET",
           "code": "AUTHORIZATION_CODE",
           "grant_type": "authorization_code"
       }'
   ```

4. **Add to .env**
   ```
   TIKTOK_CLIENT_KEY=your_client_key
   TIKTOK_CLIENT_SECRET=your_client_secret
   TIKTOK_ACCESS_TOKEN=your_access_token
   TIKTOK_REFRESH_TOKEN=your_refresh_token
   ```

### Google Cloud Setup (Gemini)

1. **Create Project**
   - https://console.cloud.google.com/
   - New Project → "TrainerApp Content"

2. **Enable APIs**
   - Vertex AI API
   - Generative Language API
   - Google Drive API (for storage)

3. **Create Service Account**
   - IAM → Service Accounts → Create
   - Download JSON key
   - Save as `config/google-credentials.json`

4. **Add to .env**
   ```
   GOOGLE_CLOUD_PROJECT_ID=your_project_id
   GEMINI_API_KEY=your_api_key
   GOOGLE_APPLICATION_CREDENTIALS=./config/google-credentials.json
   ```

---

## 🎮 Usage

### Command-Line Interface

```bash
# Generate 100 workout images
python scripts/orchestrator.py --theme workout --quantity 100

# Analyze competitor post and create 50 variations
python scripts/orchestrator.py --input rival_post.jpg --quantity 50

# Generate nutrition content with specific provider
python scripts/orchestrator.py --theme nutrition --quantity 20 --provider replicate

# Generate without posting (review first)
python scripts/orchestrator.py --theme motivation --quantity 10 --skip-posting
```

### n8n Webhook Trigger

```bash
curl -X POST http://your-server:5678/webhook/trainerapp-input \
  -H "Content-Type: application/json" \
  -d '{
    "input_url": "https://example.com/competitor-post.jpg",
    "theme": "workout",
    "quantity": 100,
    "provider": "replicate"
  }'
```

### Python API

```python
from scripts.orchestrator import ContentOrchestrator

orchestrator = ContentOrchestrator()

results = orchestrator.run_full_pipeline(
    input_source="path/to/image.jpg",
    theme="nutrition",
    quantity=50,
    skip_posting=True  # Generate only
)

print(f"Generated {results['images_generated']} images")
```

---

## 📈 Analytics & Optimization

### Viewing Analytics

```bash
# Collect latest metrics
python scripts/analytics/collect_metrics.py

# View performance report
python scripts/analytics/generate_report.py --days 7
```

### Automatic Optimization

The system automatically:
1. Tracks engagement rates per theme
2. Increases weight of high-performing themes
3. Reduces weight of low-performing content
4. Updates `config/config.yaml` weekly

### Manual Optimization

Edit `config/config.yaml`:

```yaml
themes:
  workout:
    weight: 50  # Higher = more content
  nutrition:
    weight: 30
  motivation:
    weight: 20
```

---

## 🔧 Configuration

### Switching Providers

**Use Replicate (Cheapest)**
```yaml
active_profile: "budget"  # In config/config.yaml
```

**Use Gemini (Balanced)**
```yaml
active_profile: "balanced"
```

### Posting Schedule

Edit `docker-compose.yml`:

```yaml
environment:
  - POST_TIMES=07:00,12:00,18:00,21:00  # 4 posts/day
```

Or in n8n:
- Open workflow
- Edit "Daily Content Scheduler" node
- Set cron: `0 7,12,18,21 * * *`

### Content Themes

Edit `config/config.yaml`:

```yaml
themes:
  custom_theme:
    weight: 25
    keywords: ["keyword1", "keyword2"]
    colors: ["#FF5722", "#F44336"]
    music_genre: "energetic"
    target_audience: "young_professionals"
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "OPENAI_API_KEY not set"**
```bash
# Check .env file exists and has correct format
cat .env | grep OPENAI_API_KEY

# If missing, add:
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Restart containers
docker-compose restart
```

**2. "Instagram upload failed: Media URL not accessible"**

The Instagram API requires publicly accessible media URLs. Solutions:

A. Use AWS S3 (Recommended):
```python
# In instagram_uploader.py, implement _upload_to_hosting():
import boto3
s3 = boto3.client('s3')
s3.upload_file(str(media_path), 'your-bucket', key)
return f"https://your-bucket.s3.amazonaws.com/{key}"
```

B. Use Cloudinary:
```bash
pip install cloudinary
```

```python
import cloudinary.uploader
result = cloudinary.uploader.upload(str(media_path))
return result['secure_url']
```

**3. "Rate limit exceeded"**
```bash
# Increase delays in config/config.yaml:
rate_limiting:
  api_rpm: 30  # Reduce from 60
  batch_delay_seconds: 5  # Increase from 2
```

**4. "Video processing timeout"**
```bash
# Increase timeout in tiktok_uploader.py:
max_wait = 600  # 10 minutes instead of 5
```

**5. n8n workflow not triggering**
```bash
# Check n8n logs
docker logs trainerapp-n8n

# Verify webhook URL
curl http://localhost:5678/webhook/trainerapp-input

# Check cron expression
# Use https://crontab.guru to validate
```

### Getting Help

1. Check logs: `docker-compose logs -f`
2. Open issue: https://github.com/dcrypto25/content-delivery/issues
3. Review API docs:
   - OpenAI: https://platform.openai.com/docs
   - Replicate: https://replicate.com/docs
   - Instagram: https://developers.facebook.com/docs/instagram-api
   - TikTok: https://developers.tiktok.com/doc

---

## 🚀 Scaling to 1000+ Posts/Month

### Infrastructure

```bash
# Upgrade to 4GB droplet
# $24/month on DigitalOcean

# Add Redis for caching
docker-compose up -d redis

# Enable batch processing
# In .env:
MAX_CONCURRENT_GENERATIONS=10
BATCH_DELAY_SECONDS=1
```

### Multi-Account Posting

```yaml
# config/accounts.yaml
accounts:
  - name: "main"
    instagram_id: "123"
    tiktok_id: "456"
  - name: "backup"
    instagram_id: "789"
    tiktok_id: "012"
```

### Cost at Scale (1000 posts/month)

| Item | Cost |
|------|------|
| OpenAI | $20 |
| Replicate | $28 |
| Runway | $95 |
| Server (4GB) | $24 |
| **Total** | **$167/mo** |

---

## 📚 Advanced Features

### A/B Testing

```python
# scripts/orchestrator.py
from scripts.analytics.ab_test import ABTest

ab_test = ABTest(variants=5)
winner = ab_test.run_experiment(theme="workout", quantity=50)
```

### Custom Prompts

```python
# templates/prompts/custom.yaml
custom_workout_prompts:
  - "CrossFit athlete {{action}} in industrial gym setting"
  - "Yoga practitioner {{pose}} on beach at sunset"
```

### Video Generation (Coming Soon)

```bash
# Using Runway Gen-3
python scripts/generators/video_generator.py \
    --prompt "Woman doing HIIT workout" \
    --duration 30 \
    --provider runway
```

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📜 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o
- Replicate for cost-effective image generation
- n8n for workflow automation
- The fitness tech community

---

## 📞 Support

- **Documentation**: https://docs.trainerapp.ai
- **Issues**: https://github.com/dcrypto25/content-delivery/issues
- **Discord**: https://discord.gg/trainerapp
- **Email**: tech@trainerapp.ai

---

**Built with ❤️ by TrainerApp.AI**

*Never run out of content again.*
