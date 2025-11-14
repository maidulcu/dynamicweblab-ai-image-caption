# AI Image Caption Generator

An intelligent image captioning system powered by BLIP and FastAPI that automatically generates:
- **Alt-text** for accessibility and SEO
- **Social media captions** optimized for different platforms
- **SEO metadata** for improved search visibility
- **Batch processing** for large inventories (up to 50 images at once)

## 🆓 Free Service with Rate Limits

This is a **free, open-source service** with usage limits to prevent abuse:
- **10 requests/minute** • **100 requests/hour** • **500 requests/day**
- **1,000 images/day per IP** • **50 images max per batch**
- See [RATE_LIMITS.md](RATE_LIMITS.md) for complete details

## Key Technologies

- **BLIP** (Bootstrapping Language-Image Pre-training) for advanced image analysis
- **FastAPI** for high-performance parallel processing with rate limiting
- **Next.js** frontend with modern UI and bulk upload
- **Batch processing** system for large-scale inventories
- **IP-based rate limiting** to ensure fair usage

## Features

### 1. Alt-Text Generation
Automatic generation of descriptive, keyword-rich alt-text for product images, improving both accessibility and SEO.

**Example:** "Red A-line cotton dress with floral pattern"

**Key Features:**
- Multiple length variations (short, medium, standard)
- SEO score calculation
- Keyword integration
- Accessibility-focused descriptions

### 2. Social Media Captions
Engaging, platform-optimized captions with relevant hashtags. According to research, 71% of online shoppers consider product images essential in purchasing decisions.

**Supported Platforms:**
- Instagram (up to 2,200 characters)
- Twitter (up to 280 characters)
- Facebook (up to 63,206 characters)
- LinkedIn (up to 3,000 characters)
- Pinterest (up to 500 characters)

**Key Features:**
- Platform-specific optimization
- Intelligent hashtag generation
- Call-to-action integration
- Engagement score prediction

### 3. SEO Optimization
Keyword integration for improved search visibility and organic traffic generation through intelligent content optimization.

**Key Features:**
- SEO-friendly filename generation
- Title tag optimization
- Meta description generation
- Open Graph tags for social sharing
- Schema.org markup
- Keyword analysis and recommendations

### 4. Batch Processing
Process up to 50 images simultaneously with real-time progress tracking and export capabilities.

**Key Features:**
- Parallel processing with configurable concurrency (5 concurrent tasks)
- Real-time progress updates with polling
- CSV and JSON export options
- Success/failure tracking per image
- Estimated completion time
- Automatic retry logic
- Rate limit compliance (max 50 images per batch)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/maidulcu/dynamicweblab-ai-image-caption.git
cd dynamicweblab-ai-image-caption
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the backend:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

6. **Run the Next.js frontend (optional):**
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Web Interfaces

**Legacy HTML Interface** (`http://localhost:8000`):
1. Upload an image
2. Enter product details (optional)
3. Add SEO keywords (optional)
4. Generate complete package with one click

**Next.js Frontend** (`http://localhost:3000`):
- **Home Page**: Feature overview and navigation
- **Single Upload** (`/single`): Process individual images with full product details
- **Batch Upload** (`/batch`): Upload up to 100 images with drag-and-drop, real-time progress tracking, and CSV/JSON export

### API Endpoints

#### 1. Generate Complete Package
```bash
POST /api/v1/generate/complete
```

**Parameters:**
- `image` (file): Image file
- `keywords` (string, optional): Comma-separated keywords
- `product_name` (string, optional): Product name
- `product_category` (string, optional): Product category
- `product_brand` (string, optional): Brand name
- `product_material` (string, optional): Material type
- `platforms` (string, optional): Comma-separated platforms (default: instagram,facebook,twitter)

**Example:**
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

#### 2. Generate Alt-Text Only
```bash
POST /api/v1/generate/alt-text
```

#### 3. Generate Social Caption
```bash
POST /api/v1/generate/social-caption
```

**Additional Parameters:**
- `platform` (required): instagram, twitter, facebook, linkedin, or pinterest
- `brand_voice` (optional): casual_engaging, concise_witty, professional
- `custom_message` (optional): Custom message to include

#### 4. Generate SEO Metadata
```bash
POST /api/v1/generate/seo-metadata
```

#### 5. Analyze Image
```bash
POST /api/v1/analyze
```

Returns base image analysis including detected colors, elements, and dimensions.

#### 6. List Platforms
```bash
GET /api/v1/platforms
```

Returns list of supported social media platforms.

#### 7. Health Check
```bash
GET /api/v1/health
```

#### 8. Batch Upload (Process Multiple Images)
```bash
POST /api/v1/batch/upload
```

**Parameters:**
- `images` (files): List of image files (max 100)
- `keywords` (string, optional): Comma-separated keywords
- `platforms` (string): Comma-separated platforms (default: instagram,facebook,twitter)

**Response:**
```json
{
  "success": true,
  "batch_id": "uuid-here",
  "total_images": 25,
  "status": "processing"
}
```

#### 9. Check Batch Status
```bash
GET /api/v1/batch/status/{batch_id}
```

**Response:**
```json
{
  "batch_id": "uuid",
  "status": "processing",
  "progress": {
    "total": 25,
    "processed": 15,
    "successful": 14,
    "failed": 1,
    "percentage": 60,
    "estimated_completion": "30s"
  }
}
```

#### 10. Get Batch Results
```bash
GET /api/v1/batch/results/{batch_id}
```

Returns complete results for all processed images.

#### 11. Export Batch Results
```bash
GET /api/v1/batch/export/{batch_id}?format=csv
```

Download results as CSV or JSON file.

#### 12. Check Rate Limit Status
```bash
GET /api/v1/rate-limit/status
```

Returns your current rate limit quota and usage.

## Rate Limits

This is a free service with IP-based rate limiting:

| Limit Type | Free Tier |
|-----------|-----------|
| Requests per minute | 10 |
| Requests per hour | 100 |
| Requests per day | 500 |
| Images per day | 1,000 |
| Max batch size | 50 |

**Rate limit headers** are included in all responses:
```
X-RateLimit-Remaining-Minute: 8
X-RateLimit-Remaining-Hour: 95
X-RateLimit-Remaining-Day: 487
X-RateLimit-Images-Remaining: 950
```

See [RATE_LIMITS.md](RATE_LIMITS.md) for complete documentation on rate limits, best practices, and handling rate limit errors.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Technology Stack

- **Backend:** FastAPI (Python) with async support
- **AI/ML:**
  - HuggingFace Transformers
  - BLIP (Bootstrapping Language-Image Pre-training)
  - PyTorch (with GPU acceleration)
- **Image Processing:** PIL, OpenCV
- **Frontend:**
  - Next.js 14 (App Router) with TypeScript
  - Tailwind CSS for styling
  - react-dropzone for drag-and-drop
  - Legacy HTML/CSS/JavaScript interface
- **Batch Processing:** Asyncio with semaphore-based concurrency control

## Project Structure

```
dynamicweblab-ai-image-caption/
├── core/
│   ├── __init__.py
│   ├── image_analyzer.py          # Core image analysis engine (BLIP)
│   ├── alt_text_generator.py      # Alt-text generation
│   ├── social_caption_generator.py # Social media captions
│   ├── seo_optimizer.py           # SEO metadata optimization
│   └── batch_processor.py         # Batch processing with progress tracking
├── api/
│   ├── __init__.py
│   └── routes.py                  # API endpoints (single + batch)
├── frontend/                      # Next.js frontend
│   ├── app/
│   │   ├── page.tsx              # Home page
│   │   ├── single/
│   │   │   └── page.tsx          # Single image upload
│   │   └── batch/
│   │       └── page.tsx          # Bulk upload with progress
│   ├── package.json
│   └── README.md
├── static/
│   └── index.html                 # Legacy web interface
├── uploads/                       # Temporary upload directory
├── batch_results/                 # Batch export directory
├── config.py                      # Configuration management
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose setup
└── README.md                      # This file
```

## Configuration

Edit `.env` file to customize settings:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Model Configuration
CAPTION_MODEL=Salesforce/blip-image-captioning-large
USE_CLAUDE_API=False

# SEO Configuration
DEFAULT_KEYWORDS=product,shop,buy,online,quality
MAX_ALT_TEXT_LENGTH=125

# Social Media Configuration
INSTAGRAM_MAX_LENGTH=2200
TWITTER_MAX_LENGTH=280
FACEBOOK_MAX_LENGTH=63206
```

## Performance

- **Processing Time:** 2-5 seconds per image (depending on hardware)
- **GPU Acceleration:** Automatically uses CUDA if available
- **Batch Processing:**
  - Up to 50 images per batch (free tier limit)
  - 5 concurrent processing tasks (configurable)
  - Real-time progress tracking every 2 seconds
  - Estimated completion time calculation
  - ~2-5 minutes for 50 images
- **Rate Limiting:** IP-based with minimal overhead
- **Concurrent Requests:** FastAPI async support
- **Scalability:** Horizontal scaling with load balancers

## Best Practices

### Alt-Text
- Keep between 50-125 characters for optimal SEO
- Include primary keyword naturally
- Describe the image accurately
- Avoid "image of" or "picture of" prefixes

### Social Media Captions
- Use platform-specific optimal lengths
- Include 1-3 relevant hashtags (varies by platform)
- Add clear call-to-action
- Match your brand voice

### SEO Metadata
- Use descriptive filenames with hyphens
- Include target keywords naturally
- Write compelling meta descriptions
- Implement Schema.org markup

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/maidulcu/dynamicweblab-ai-image-caption/issues)
- Email: support@dynamicweblab.com

## Acknowledgments

- BLIP model by Salesforce Research
- HuggingFace Transformers library
- FastAPI framework

## Roadmap

- [ ] Batch processing API
- [ ] Multiple language support
- [ ] Custom model training
- [ ] Integration with e-commerce platforms
- [ ] Advanced analytics dashboard
- [ ] A/B testing for captions
- [ ] Brand voice customization
- [ ] Image editing suggestions

---

**Built with ❤️ by DynamicWebLab**
