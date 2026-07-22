<div align="center">

# AI Image Caption Generator

**Automated alt-text, social media captions, and SEO metadata for product images — powered by Moondream & BLIP vision models.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20It%20Now-brightgreen)](http://localhost:3000)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-orange)](http://localhost:8000/docs)

</div>

---

An intelligent image captioning system that generates **SEO-optimized alt-text**, **platform-specific social media captions**, and **complete SEO metadata** from a single product image. Supports both **local GPU inference** (zero cost) and **Moondream Cloud API** (no GPU required).

![Architecture](https://img.shields.io/badge/Architecture-Moondream%20%2B%20BLIP%20%2B%20FastAPI-blueviolet)

---

## Why Choose This Project?

| Feature | Benefit |
|---------|---------|
| **Zero-cost local GPU inference** | Run entirely on your own hardware — no API fees, no data leaves your server |
| **Moondream Cloud fallback** | No GPU? Use Moondream Cloud API ($5 free/month) with identical quality |
| **Production-grade security** | Rate limiting, input sanitization, timing-safe auth, request size enforcement |
| **Batch processing** | Process up to 50 images in parallel with real-time progress tracking |
| **5 platforms at once** | Instagram, Twitter, Facebook, LinkedIn, Pinterest — optimized per platform |
| **SEO metadata included** | Filename, title tag, meta description, Open Graph, Schema.org markup |
| **Docker-ready** | One command to deploy: `docker-compose up` |
| **100% open source** | MIT license, no vendor lock-in |

---

## Who Is This For?

- **E-commerce developers** — Auto-generate alt-text and SEO metadata for product catalogs
- **Social media managers** — Create platform-optimized captions with hashtags in bulk
- **Accessibility compliance officers** — Meet WCAG alt-text requirements at scale
- **SEO agencies** — Generate optimized metadata for client image assets
- **Dropshippers & resellers** — Process large product image inventories quickly

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/Dynamic-Web-Lab/dynamicweblab-ai-image-caption.git
cd dynamicweblab-ai-image-caption
cp .env.example .env   # Edit with your settings
docker-compose up -d
```

- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Swagger docs: `http://localhost:8000/docs`

### Option 2: Local Setup

```bash
git clone https://github.com/Dynamic-Web-Lab/dynamicweblab-ai-image-caption.git
cd dynamicweblab-ai-image-caption

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env       # Edit with your settings

python main.py             # Backend on :8000
```

In a second terminal for the frontend:

```bash
cd frontend
npm install
npm run dev                # Frontend on :3000
```

---

## Features

### 1. Alt-Text Generation

Descriptive, keyword-rich alt-text for accessibility and SEO.

- Multiple length variations (short, medium, standard, descriptive)
- SEO score calculation (0-100)
- Keyword integration
- WCAG-compliant descriptions

**Example:** `"Red A-line cotton dress with floral pattern"`

### 2. Social Media Captions

Platform-optimized captions with hashtags and CTAs.

| Platform | Max Length | Optimal Hashtags |
|----------|-----------|-----------------|
| Instagram | 2,200 chars | 11 |
| Twitter | 280 chars | 1 |
| Facebook | 63,206 chars | 2 |
| LinkedIn | 3,000 chars | 3 |
| Pinterest | 500 chars | 10 |

Features: brand voice selection, engagement score prediction, CTA integration.

### 3. SEO Optimization

Complete metadata package for search visibility.

- SEO-friendly filename generation
- Title tag (50-60 chars optimal)
- Meta description (150-160 chars optimal)
- Open Graph tags for social sharing
- Schema.org JSON-LD markup
- Keyword density analysis & recommendations

### 4. Batch Processing

Process up to 50 images in parallel.

- Semaphore-based concurrency (5 concurrent tasks)
- Real-time progress tracking with ETA
- CSV and JSON export
- Per-image success/failure tracking
- Automatic cleanup after processing

### 5. Image Analysis

Base analysis using Moondream or BLIP vision models.

- Dominant color detection
- Object/element recognition
- Image dimensions and orientation
- Multi-model support (Moondream Cloud, Moondream Local, BLIP)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate/complete` | Full package: alt-text + captions + SEO |
| `POST` | `/api/v1/generate/alt-text` | Alt-text only |
| `POST` | `/api/v1/generate/social-caption` | Single platform caption |
| `POST` | `/api/v1/generate/seo-metadata` | SEO metadata only |
| `POST` | `/api/v1/analyze` | Raw image analysis |
| `POST` | `/api/v1/batch/upload` | Batch process multiple images |
| `GET` | `/api/v1/batch/status/{id}` | Check batch progress |
| `GET` | `/api/v1/batch/results/{id}` | Get batch results |
| `GET` | `/api/v1/batch/export/{id}?format=csv` | Export as CSV/JSON |
| `GET` | `/api/v1/rate-limit/status` | Your rate limit quota |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/platforms` | Supported platforms |

### Example: Generate Complete Package

```bash
curl -X POST "http://localhost:8000/api/v1/generate/complete" \
  -F "image=@product.jpg" \
  -F "product_name=Cotton Dress" \
  -F "product_category=Women's Fashion" \
  -F "keywords=dress,fashion,summer"
```

**Response:**

```json
{
  "success": true,
  "alt_text": {
    "standard": "Red A-line cotton dress with floral pattern",
    "short": "Red cotton dress",
    "medium": "Red A-line cotton dress",
    "seo_score": 85
  },
  "social_captions": {
    "instagram": {
      "caption": "Obsessed with this red cotton dress! 💕\n\nShop now! Link in bio\n\n#fashion #dress #summerstyle",
      "engagement_score": 75,
      "hashtag_count": 3
    }
  },
  "seo_metadata": {
    "filename": "womens-fashion-cotton-dress-red.jpg",
    "title": "Cotton Dress - Women's Fashion",
    "meta_description": "Red A-line cotton dress with floral pattern. Made from Cotton. Shop now.",
    "seo_score": 90
  }
}
```

Full API documentation: `http://localhost:8000/docs` (Swagger UI)

---

## Rate Limits

Free, no-login service with IP-based rate limiting:

| Limit | Free Tier |
|-------|-----------|
| Requests per minute | 10 |
| Requests per hour | 100 |
| Requests per day | 500 |
| Images per day | 1,000 |
| Max batch size | 50 |

Rate limit headers are included in every response. See [RATE_LIMITS.md](RATE_LIMITS.md) for details, error handling, and best practices.

---

## Security

This project implements production-grade security measures:

- **Timing-safe authentication** — `hmac.compare_digest()` for admin API key validation
- **Input sanitization** — HTML stripping, length limits, UUID-only batch IDs
- **File upload security** — MIME validation, size limits, UUID-prefixed filenames, path traversal prevention
- **Rate limiting** — IP-based with persistent storage across restarts
- **Request size enforcement** — Streaming body check (not just Content-Length header)
- **Security headers** — CSP, X-Frame-Options, X-Content-Type-Options, Permissions-Policy
- **No secrets in code** — All credentials via environment variables
- **Error sanitization** — Internal errors never exposed to clients

See [SECURITY_FIXES.md](SECURITY_FIXES.md) and [MEDIUM_SECURITY_ISSUES.md](MEDIUM_SECURITY_ISSUES.md) for the full security audit.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) with async support |
| **AI/ML** | Moondream 2 (primary), BLIP (fallback), HuggingFace Transformers, PyTorch |
| **Image Processing** | Pillow, OpenCV |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, react-dropzone |
| **Deployment** | Docker, Docker Compose |
| **Security** | Rate limiting, input validation, secure file handling |

---

## Model Configuration

The system supports three vision model backends, tried in order:

1. **Moondream Cloud API** — Best quality, requires API key, $5 free/month
2. **Moondream Local (GPU)** — Free, runs on CUDA/MPS/CPU, same model weights
3. **BLIP (Fallback)** — Always available, lower quality, larger model size

Configure in `.env`:

```env
USE_MOONDREAM=True
MOONDREAM_API_KEY=          # Optional: enables cloud API
MOONDREAM_MODEL=vikhyatk/moondream2
MOONDREAM_REVISION=2025-06-21
CAPTION_MODEL=Salesforce/blip-image-captioning-large
```

---

## Project Structure

```
dynamicweblab-ai-image-caption/
├── api/
│   ├── __init__.py
│   └── routes.py              # All API endpoints
├── core/
│   ├── __init__.py
│   ├── image_analyzer.py      # Vision model abstraction
│   ├── alt_text_generator.py  # Alt-text generation
│   ├── social_caption_generator.py  # Platform-specific captions
│   ├── seo_optimizer.py       # SEO metadata optimization
│   ├── batch_processor.py     # Parallel batch processing
│   └── rate_limiter.py        # IP-based rate limiting
├── middleware/
│   ├── __init__.py
│   ├── rate_limit_middleware.py    # Rate limit enforcement
│   ├── security_headers.py        # CSP, X-Frame-Options, etc.
│   └── request_size_limit.py      # Body size enforcement
├── utils/
│   ├── __init__.py
│   ├── security.py            # File validation, input sanitization
│   └── executor.py            # Thread pool for AI operations
├── frontend/                  # Next.js 14 frontend
│   ├── app/
│   │   ├── page.tsx           # Home
│   │   ├── single/page.tsx    # Single image upload
│   │   └── batch/page.tsx     # Batch upload with progress
│   └── package.json
├── static/
│   └── index.html             # Legacy web interface
├── uploads/                   # Temporary upload directory
├── batch_results/             # Persisted batch results
├── config.py                  # Settings via environment variables
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── Dockerfile
├── docker-compose.yml
├── SECURITY_FIXES.md          # Security audit report
├── RATE_LIMITS.md             # Rate limit documentation
└── README.md
```

---

## Configuration

All settings are configured via environment variables (see `.env.example`):

```env
# Server
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=False

# AI Models
USE_MOONDREAM=True
MOONDREAM_API_KEY=              # Optional cloud API
ANTHROPIC_API_KEY=              # Optional Claude captions
USE_CLAUDE_API=False

# Security
ADMIN_API_KEY=<generate-a-random-key>
ALLOWED_ORIGINS=http://localhost:3000
TRUST_PROXY_HEADERS=False

# Rate Limits
RATE_LIMIT_ENABLED=True
REQUESTS_PER_MINUTE=10
REQUESTS_PER_HOUR=100
REQUESTS_PER_DAY=500
IMAGES_PER_DAY=1000
BATCH_LIMIT=50
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Submit a pull request

---

## Roadmap

- [x] Batch processing with parallel execution
- [x] Moondream Cloud + Local GPU support
- [x] Production security hardening
- [x] Next.js frontend with drag-and-drop
- [x] Rate limiting with persistent storage
- [ ] Multiple language support
- [ ] Custom model fine-tuning
- [ ] E-commerce platform integrations (Shopify, WooCommerce)
- [ ] Advanced analytics dashboard
- [ ] A/B testing for captions
- [ ] Brand voice customization profiles
- [ ] Image editing suggestions

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/Dynamic-Web-Lab/dynamicweblab-ai-image-caption/issues)
- **Email:** support@dynamicweblab.com

---

<div align="center">

**Built by [DynamicWebLab](https://dynamicweblab.com)**

</div>
