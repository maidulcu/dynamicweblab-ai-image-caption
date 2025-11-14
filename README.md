# AI Image Caption Generator

An intelligent image captioning system that automatically generates:
- **Alt-text** for accessibility and SEO
- **Social media captions** optimized for different platforms
- **SEO metadata** for improved search visibility

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

5. **Run the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Usage

### Web Interface

Access the web interface at `http://localhost:8000` to:
1. Upload an image
2. Enter product details (optional)
3. Add SEO keywords (optional)
4. Generate complete package with one click

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

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Technology Stack

- **Backend:** FastAPI (Python)
- **AI/ML:**
  - HuggingFace Transformers
  - BLIP (Bootstrapping Language-Image Pre-training)
  - PyTorch
- **Image Processing:** PIL, OpenCV
- **Frontend:** HTML, CSS, JavaScript (vanilla)

## Project Structure

```
dynamicweblab-ai-image-caption/
├── core/
│   ├── __init__.py
│   ├── image_analyzer.py          # Core image analysis engine
│   ├── alt_text_generator.py      # Alt-text generation
│   ├── social_caption_generator.py # Social media captions
│   └── seo_optimizer.py           # SEO metadata optimization
├── api/
│   ├── __init__.py
│   └── routes.py                  # API endpoints
├── static/
│   └── index.html                 # Web interface
├── uploads/                       # Temporary upload directory
├── config.py                      # Configuration management
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
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
- **Batch Processing:** Supports multiple images
- **Concurrent Requests:** FastAPI async support

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
