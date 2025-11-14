"""API routes for the image caption service."""
import os
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import aiofiles
from pathlib import Path

from core import ImageAnalyzer, AltTextGenerator, SocialCaptionGenerator, SEOOptimizer
from core.social_caption_generator import SocialPlatform
from config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services (lazy loading for faster startup)
_image_analyzer = None
_alt_text_generator = None
_social_caption_generator = None
_seo_optimizer = None


def get_image_analyzer():
    """Get or create ImageAnalyzer instance."""
    global _image_analyzer
    if _image_analyzer is None:
        _image_analyzer = ImageAnalyzer(settings.caption_model)
    return _image_analyzer


def get_alt_text_generator():
    """Get or create AltTextGenerator instance."""
    global _alt_text_generator
    if _alt_text_generator is None:
        _alt_text_generator = AltTextGenerator(settings.max_alt_text_length)
    return _alt_text_generator


def get_social_caption_generator():
    """Get or create SocialCaptionGenerator instance."""
    global _social_caption_generator
    if _social_caption_generator is None:
        _social_caption_generator = SocialCaptionGenerator()
    return _social_caption_generator


def get_seo_optimizer():
    """Get or create SEOOptimizer instance."""
    global _seo_optimizer
    if _seo_optimizer is None:
        _seo_optimizer = SEOOptimizer()
    return _seo_optimizer


async def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """Save uploaded file to disk.

    Args:
        upload_file: Uploaded file
        destination: Destination path
    """
    async with aiofiles.open(destination, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None)
):
    """Analyze an image and return base analysis.

    Args:
        image: Image file to analyze
        keywords: Comma-separated keywords
        product_name: Product name
        product_category: Product category
        product_brand: Product brand

    Returns:
        Image analysis results
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / image.filename
        await save_upload_file(image, file_path)

        # Analyze image
        analyzer = get_image_analyzer()
        analysis = analyzer.analyze_image(str(file_path))

        # Clean up file
        file_path.unlink()

        return JSONResponse(content={"success": True, "analysis": analysis})

    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/alt-text")
async def generate_alt_text(
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    product_style: Optional[str] = Form(None)
):
    """Generate SEO-optimized alt-text for an image.

    Args:
        image: Image file
        keywords: Comma-separated SEO keywords
        product_name: Product name
        product_category: Product category
        product_brand: Product brand
        product_material: Product material
        product_style: Product style

    Returns:
        Generated alt-text with variations
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / image.filename
        await save_upload_file(image, file_path)

        # Analyze image
        analyzer = get_image_analyzer()
        analysis = analyzer.analyze_image(str(file_path))

        # Prepare product info
        product_info = {}
        if product_name:
            product_info["name"] = product_name
        if product_category:
            product_info["category"] = product_category
        if product_brand:
            product_info["brand"] = product_brand
        if product_material:
            product_info["material"] = product_material
        if product_style:
            product_info["style"] = product_style

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]

        # Generate alt-text
        alt_gen = get_alt_text_generator()
        alt_text = alt_gen.generate_alt_text(
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # Clean up file
        file_path.unlink()

        return JSONResponse(content={
            "success": True,
            "alt_text": alt_text,
            "base_analysis": analysis
        })

    except Exception as e:
        logger.error(f"Error generating alt-text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/social-caption")
async def generate_social_caption(
    image: UploadFile = File(...),
    platform: str = Form(...),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    custom_message: Optional[str] = Form(None),
    brand_voice: Optional[str] = Form(None),
    include_hashtags: bool = Form(True)
):
    """Generate platform-optimized social media caption.

    Args:
        image: Image file
        platform: Social media platform (instagram, twitter, facebook, etc.)
        product_name: Product name
        product_category: Product category
        product_brand: Product brand
        custom_message: Custom message to include
        brand_voice: Brand voice/tone
        include_hashtags: Whether to include hashtags

    Returns:
        Generated social media caption
    """
    try:
        # Validate platform
        try:
            social_platform = SocialPlatform(platform.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Must be one of: {', '.join([p.value for p in SocialPlatform])}"
            )

        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / image.filename
        await save_upload_file(image, file_path)

        # Analyze image
        analyzer = get_image_analyzer()
        analysis = analyzer.analyze_image(str(file_path))

        # Prepare product info
        product_info = {}
        if product_name:
            product_info["name"] = product_name
        if product_category:
            product_info["category"] = product_category
        if product_brand:
            product_info["brand"] = product_brand

        # Generate caption
        caption_gen = get_social_caption_generator()
        caption = caption_gen.generate_caption(
            analysis,
            social_platform,
            product_info=product_info if product_info else None,
            brand_voice=brand_voice,
            include_hashtags=include_hashtags,
            custom_message=custom_message
        )

        # Clean up file
        file_path.unlink()

        return JSONResponse(content={
            "success": True,
            "caption": caption,
            "base_analysis": analysis
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating social caption: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/seo-metadata")
async def generate_seo_metadata(
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    url_slug: Optional[str] = Form(None)
):
    """Generate comprehensive SEO metadata for an image.

    Args:
        image: Image file
        keywords: Comma-separated target keywords
        product_name: Product name
        product_category: Product category
        product_brand: Product brand
        product_material: Product material
        url_slug: URL slug for the product/image

    Returns:
        Complete SEO metadata package
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / image.filename
        await save_upload_file(image, file_path)

        # Analyze image
        analyzer = get_image_analyzer()
        analysis = analyzer.analyze_image(str(file_path))

        # Prepare product info
        product_info = {}
        if product_name:
            product_info["name"] = product_name
        if product_category:
            product_info["category"] = product_category
        if product_brand:
            product_info["brand"] = product_brand
        if product_material:
            product_info["material"] = product_material

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]

        # Generate alt-text first
        alt_gen = get_alt_text_generator()
        alt_text_data = alt_gen.generate_alt_text(
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # Generate SEO metadata
        seo_opt = get_seo_optimizer()
        seo_metadata = seo_opt.optimize_metadata(
            analysis,
            alt_text_data["standard"],
            product_info=product_info if product_info else None,
            target_keywords=keyword_list,
            url_slug=url_slug
        )

        # Clean up file
        file_path.unlink()

        return JSONResponse(content={
            "success": True,
            "seo_metadata": seo_metadata,
            "alt_text": alt_text_data,
            "base_analysis": analysis
        })

    except Exception as e:
        logger.error(f"Error generating SEO metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/complete")
async def generate_complete_package(
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    product_style: Optional[str] = Form(None),
    platforms: Optional[str] = Form("instagram,facebook,twitter")
):
    """Generate complete package: alt-text, social captions, and SEO metadata.

    Args:
        image: Image file
        keywords: Comma-separated keywords
        product_name: Product name
        product_category: Product category
        product_brand: Product brand
        product_material: Product material
        product_style: Product style
        platforms: Comma-separated list of platforms

    Returns:
        Complete content generation package
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Save uploaded file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / image.filename
        await save_upload_file(image, file_path)

        # Analyze image
        analyzer = get_image_analyzer()
        analysis = analyzer.analyze_image(str(file_path))

        # Prepare product info
        product_info = {}
        if product_name:
            product_info["name"] = product_name
        if product_category:
            product_info["category"] = product_category
        if product_brand:
            product_info["brand"] = product_brand
        if product_material:
            product_info["material"] = product_material
        if product_style:
            product_info["style"] = product_style

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]

        # Parse platforms
        platform_list = [SocialPlatform(p.strip().lower()) for p in platforms.split(',')]

        # Generate alt-text
        alt_gen = get_alt_text_generator()
        alt_text = alt_gen.generate_alt_text(
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # Generate social captions for all platforms
        caption_gen = get_social_caption_generator()
        social_captions = caption_gen.generate_multi_platform(
            analysis,
            product_info=product_info if product_info else None,
            platforms=platform_list
        )

        # Generate SEO metadata
        seo_opt = get_seo_optimizer()
        seo_metadata = seo_opt.optimize_metadata(
            analysis,
            alt_text["standard"],
            product_info=product_info if product_info else None,
            target_keywords=keyword_list
        )

        # Clean up file
        file_path.unlink()

        return JSONResponse(content={
            "success": True,
            "alt_text": alt_text,
            "social_captions": social_captions,
            "seo_metadata": seo_metadata,
            "base_analysis": analysis
        })

    except Exception as e:
        logger.error(f"Error generating complete package: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Image Caption API"}


@router.get("/platforms")
async def list_platforms():
    """List supported social media platforms."""
    return {
        "platforms": [
            {
                "name": platform.value,
                "display_name": platform.value.title(),
                "max_length": SocialCaptionGenerator.PLATFORM_CONFIGS[platform]["max_length"]
            }
            for platform in SocialPlatform
        ]
    }
