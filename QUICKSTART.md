# ⚡ QUICKSTART - Get Running in 10 Minutes

## Prerequisites
- Python 3.11+
- OpenAI API key ($10 credit)
- Replicate API token ($10 credit)

---

## Step 1: Setup (3 minutes)

```bash
# Clone & navigate
cd /Users/dcrypto25/content

# Setup environment
make setup-env

# Edit .env with your API keys
nano .env
# Add:
# OPENAI_API_KEY=sk-your-key
# REPLICATE_API_TOKEN=r8_your-token

# Install dependencies
make install
```

---

## Step 2: Test Generation (2 minutes)

```bash
# Generate 10 test posts (no posting)
make generate

# View output
open storage/generated/images/
```

---

## Step 3: Generate Full Batch (5 minutes)

```bash
# Generate 100 workout posts
python scripts/orchestrator.py --theme workout --quantity 100 --skip-posting

# OR use Makefile
make generate-full
```

---

## Step 4: Deploy (Optional)

```bash
# Deploy with Docker
make deploy

# Access n8n
open http://localhost:5678
```

---

## 🎯 Most Common Commands

```bash
# Generate test batch (10 posts)
make generate

# Generate full batch (100 posts)
make generate-full

# Analyze competitor post
python scripts/orchestrator.py --input rival_post.jpg --quantity 50

# View analytics
make analytics

# Clean generated files
make clean

# View logs
make logs
```

---

## 🔥 Quick Tips

1. **Start small**: Test with 10 posts before scaling to 100+
2. **Review output**: Check `storage/generated/images/` before posting
3. **Monitor costs**: Check OpenAI/Replicate usage dashboards
4. **Adjust quality**: Edit `config/config.yaml` if needed

---

## 📚 Full Documentation

- **Setup Guide**: `docs/YOUR_SETUP_GUIDE.md`
- **System Overview**: `docs/SYSTEM_OVERVIEW.md`
- **Main README**: `README.md`

---

## 🆘 Issues?

```bash
# Check logs
tail -f logs/system.log

# Test API keys
python -c "import openai; print('OpenAI OK')"
python -c "import replicate; print('Replicate OK')"

# Get help
cat docs/YOUR_SETUP_GUIDE.md | grep -A 10 "Troubleshooting"
```

---

**You're ready to generate infinite content! 🚀**
