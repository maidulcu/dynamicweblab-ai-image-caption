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
from core.batch_processor import BatchProcessor, ProgressTracker
from config import settings
import uuid
import asyncio

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services (lazy loading for faster startup)
_image_analyzer = None
_alt_text_generator = None
_social_caption_generator = None
_seo_optimizer = None
_batch_processor = None
_progress_tracker = None


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


def get_batch_processor():
    """Get or create BatchProcessor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor(max_concurrent=5)
    return _batch_processor


def get_progress_tracker():
    """Get or create ProgressTracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker


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


@router.post("/batch/upload")
async def batch_upload(
    images: List[UploadFile] = File(...),
    keywords: Optional[str] = Form(None),
    platforms: str = Form("instagram,facebook,twitter")
):
    """Upload multiple images for batch processing.

    Args:
        images: List of image files
        keywords: Comma-separated keywords (optional)
        platforms: Comma-separated list of platforms

    Returns:
        Batch ID and processing status
    """
    try:
        if len(images) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 images per batch"
            )

        # Generate batch ID
        batch_id = str(uuid.uuid4())

        # Save uploaded files
        upload_dir = Path(settings.upload_dir) / batch_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for idx, image in enumerate(images):
            if not image.content_type.startswith('image/'):
                continue

            file_path = upload_dir / f"{idx}_{image.filename}"
            await save_upload_file(image, file_path)
            saved_paths.append(str(file_path))

        # Parse parameters
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]

        platform_list = [SocialPlatform(p.strip().lower()) for p in platforms.split(',')]

        # Process batch asynchronously
        async def process_single_image(image_path, product_info=None, keywords=None):
            """Process a single image."""
            analyzer = get_image_analyzer()
            alt_gen = get_alt_text_generator()
            caption_gen = get_social_caption_generator()
            seo_opt = get_seo_optimizer()

            # Analyze image
            analysis = analyzer.analyze_image(image_path)

            # Generate alt-text
            alt_text = alt_gen.generate_alt_text(
                analysis,
                keywords=keywords,
                product_info=product_info
            )

            # Generate social captions
            social_captions = caption_gen.generate_multi_platform(
                analysis,
                product_info=product_info,
                platforms=platform_list
            )

            # Generate SEO metadata
            seo_metadata = seo_opt.optimize_metadata(
                analysis,
                alt_text["standard"],
                product_info=product_info,
                target_keywords=keywords
            )

            return {
                "alt_text": alt_text,
                "social_captions": social_captions,
                "seo_metadata": seo_metadata,
                "analysis": analysis
            }

        # Start batch processing
        batch_processor = get_batch_processor()
        progress_tracker = get_progress_tracker()

        # Create progress tracker
        progress_tracker.create_tracker(batch_id, len(saved_paths))

        # Define progress callback
        async def progress_callback(batch_data):
            """Update progress."""
            progress_tracker.update(batch_id, batch_data["processed"])

        # Process in background
        asyncio.create_task(
            batch_processor.process_batch(
                saved_paths,
                process_single_image,
                keywords=keyword_list,
                batch_id=batch_id,
                progress_callback=progress_callback
            )
        )

        return JSONResponse(content={
            "success": True,
            "batch_id": batch_id,
            "total_images": len(saved_paths),
            "status": "processing",
            "message": f"Processing {len(saved_paths)} images. Use /batch/status/{batch_id} to check progress."
        })

    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/status/{batch_id}")
async def batch_status(batch_id: str):
    """Get status of a batch processing job.

    Args:
        batch_id: Batch identifier

    Returns:
        Current batch status and progress
    """
    try:
        batch_processor = get_batch_processor()
        progress_tracker = get_progress_tracker()

        batch_data = batch_processor.get_batch_status(batch_id)
        progress_data = progress_tracker.get_progress(batch_id)

        if not batch_data:
            raise HTTPException(status_code=404, detail="Batch not found")

        return JSONResponse(content={
            "success": True,
            "batch_id": batch_id,
            "status": batch_data.get("status"),
            "progress": {
                "total": batch_data.get("total_images"),
                "processed": batch_data.get("processed"),
                "successful": batch_data.get("successful"),
                "failed": batch_data.get("failed"),
                "percentage": progress_data.get("percentage", 0) if progress_data else 0,
                "estimated_completion": progress_data.get("estimated_completion") if progress_data else None
            },
            "start_time": batch_data.get("start_time"),
            "end_time": batch_data.get("end_time")
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/results/{batch_id}")
async def batch_results(batch_id: str):
    """Get results of a completed batch.

    Args:
        batch_id: Batch identifier

    Returns:
        Complete batch results
    """
    try:
        batch_processor = get_batch_processor()
        batch_data = batch_processor.get_batch_status(batch_id)

        if not batch_data:
            raise HTTPException(status_code=404, detail="Batch not found")

        if batch_data.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="Batch processing not yet completed"
            )

        return JSONResponse(content={
            "success": True,
            "batch_id": batch_id,
            "results": batch_data.get("results", []),
            "errors": batch_data.get("errors", []),
            "summary": {
                "total": batch_data.get("total_images"),
                "successful": batch_data.get("successful"),
                "failed": batch_data.get("failed")
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/export/{batch_id}")
async def batch_export(
    batch_id: str,
    format: str = "csv"
):
    """Export batch results to file.

    Args:
        batch_id: Batch identifier
        format: Export format (csv or json)

    Returns:
        Download link for exported file
    """
    try:
        if format not in ["csv", "json"]:
            raise HTTPException(
                status_code=400,
                detail="Format must be 'csv' or 'json'"
            )

        batch_processor = get_batch_processor()
        export_path = batch_processor.export_batch_results(batch_id, format)

        if not export_path:
            raise HTTPException(status_code=404, detail="Batch not found")

        from fastapi.responses import FileResponse
        return FileResponse(
            export_path,
            media_type="text/csv" if format == "csv" else "application/json",
            filename=f"batch_{batch_id}.{format}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
