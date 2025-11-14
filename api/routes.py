"""API routes for the image caption service - SECURITY HARDENED."""
import os
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Header
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
import aiofiles
from pathlib import Path
from datetime import datetime

from core import ImageAnalyzer, AltTextGenerator, SocialCaptionGenerator, SEOOptimizer
from core.social_caption_generator import SocialPlatform
from core.batch_processor import BatchProcessor, ProgressTracker
from core.rate_limiter import get_rate_limiter
from utils import (
    validate_and_save_upload,
    validate_input_text,
    validate_batch_id,
    get_client_ip,
    run_in_executor,
    MAX_FILE_SIZE,
    MAX_BATCH_FILE_SIZE
)
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


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring.

    Returns:
        Health status and service information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "AI Image Caption Generator",
        "rate_limiting": "enabled" if settings.rate_limit_enabled else "disabled"
    }


@router.post("/analyze")
async def analyze_image(
    request: Request,
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None)
):
    """Analyze an image and return base analysis.

    Args:
        request: Request object for IP extraction
        image: Image file to analyze
        keywords: Comma-separated keywords
        product_name: Product name
        product_category: Product category
        product_brand: Product brand

    Returns:
        Image analysis results
    """
    file_path = None
    try:
        # SECURITY: Validate and save upload securely
        upload_dir = Path(settings.upload_dir)
        file_path = await validate_and_save_upload(image, upload_dir, MAX_FILE_SIZE)

        # PERFORMANCE: Run blocking AI operation in thread pool
        analyzer = get_image_analyzer()
        analysis = await run_in_executor(analyzer.analyze_image, str(file_path))

        # SECURITY: Record image processing for rate limiting
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        await rate_limiter.record_request(client_ip, num_images=1)

        return JSONResponse(content={"success": True, "analysis": analysis})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing image. Please try again later."
        )
    finally:
        # SECURITY: Always cleanup temp files
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")


@router.post("/generate/alt-text")
async def generate_alt_text(
    request: Request,
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    product_style: Optional[str] = Form(None)
):
    """Generate SEO-optimized alt-text for an image."""
    file_path = None
    try:
        # SECURITY: Validate and save upload
        upload_dir = Path(settings.upload_dir)
        file_path = await validate_and_save_upload(image, upload_dir, MAX_FILE_SIZE)

        # PERFORMANCE: Run blocking AI operation in thread pool
        analyzer = get_image_analyzer()
        analysis = await run_in_executor(analyzer.analyze_image, str(file_path))

        # SECURITY: Validate and sanitize inputs
        product_info = {}
        if product_name:
            product_info["name"] = validate_input_text(product_name)
        if product_category:
            product_info["category"] = validate_input_text(product_category)
        if product_brand:
            product_info["brand"] = validate_input_text(product_brand)
        if product_material:
            product_info["material"] = validate_input_text(product_material)
        if product_style:
            product_info["style"] = validate_input_text(product_style)

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [validate_input_text(k.strip()) for k in keywords.split(',')]

        # PERFORMANCE: Run blocking AI operation in thread pool
        alt_gen = get_alt_text_generator()
        alt_text = await run_in_executor(
            alt_gen.generate_alt_text,
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # SECURITY: Record image processing
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        await rate_limiter.record_request(client_ip, num_images=1)

        return JSONResponse(content={
            "success": True,
            "alt_text": alt_text,
            "base_analysis": analysis
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating alt-text: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")


@router.post("/generate/social-caption")
async def generate_social_caption(
    request: Request,
    image: UploadFile = File(...),
    platform: str = Form(...),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    custom_message: Optional[str] = Form(None),
    brand_voice: Optional[str] = Form(None),
    include_hashtags: bool = Form(True)
):
    """Generate platform-optimized social media caption."""
    file_path = None
    try:
        # Validate platform
        try:
            social_platform = SocialPlatform(platform.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Must be one of: {', '.join([p.value for p in SocialPlatform])}"
            )

        # SECURITY: Validate and save upload
        upload_dir = Path(settings.upload_dir)
        file_path = await validate_and_save_upload(image, upload_dir, MAX_FILE_SIZE)

        # PERFORMANCE: Run blocking AI operation in thread pool
        analyzer = get_image_analyzer()
        analysis = await run_in_executor(analyzer.analyze_image, str(file_path))

        # SECURITY: Validate inputs
        product_info = {}
        if product_name:
            product_info["name"] = validate_input_text(product_name)
        if product_category:
            product_info["category"] = validate_input_text(product_category)
        if product_brand:
            product_info["brand"] = validate_input_text(product_brand)

        # Validate custom message
        safe_custom_message = validate_input_text(custom_message, max_length=500) if custom_message else None

        # PERFORMANCE: Run blocking AI operation in thread pool
        caption_gen = get_social_caption_generator()
        caption = await run_in_executor(
            caption_gen.generate_caption,
            analysis,
            social_platform,
            product_info=product_info if product_info else None,
            brand_voice=brand_voice,
            include_hashtags=include_hashtags,
            custom_message=safe_custom_message
        )

        # SECURITY: Record image processing
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        await rate_limiter.record_request(client_ip, num_images=1)

        return JSONResponse(content={
            "success": True,
            "caption": caption,
            "base_analysis": analysis
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating social caption: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")


@router.post("/generate/seo-metadata")
async def generate_seo_metadata(
    request: Request,
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    url_slug: Optional[str] = Form(None)
):
    """Generate comprehensive SEO metadata for an image."""
    file_path = None
    try:
        # SECURITY: Validate and save upload
        upload_dir = Path(settings.upload_dir)
        file_path = await validate_and_save_upload(image, upload_dir, MAX_FILE_SIZE)

        # PERFORMANCE: Run blocking AI operation in thread pool
        analyzer = get_image_analyzer()
        analysis = await run_in_executor(analyzer.analyze_image, str(file_path))

        # SECURITY: Validate inputs
        product_info = {}
        if product_name:
            product_info["name"] = validate_input_text(product_name)
        if product_category:
            product_info["category"] = validate_input_text(product_category)
        if product_brand:
            product_info["brand"] = validate_input_text(product_brand)
        if product_material:
            product_info["material"] = validate_input_text(product_material)

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [validate_input_text(k.strip()) for k in keywords.split(',')]

        # Generate alt-text first
        alt_gen = get_alt_text_generator()
        alt_text_data = alt_gen.generate_alt_text(
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # PERFORMANCE: Run blocking AI operation in thread pool
        seo_opt = get_seo_optimizer()
        seo_metadata = await run_in_executor(
            seo_opt.optimize_metadata,
            analysis,
            alt_text_data["standard"],
            product_info=product_info if product_info else None,
            target_keywords=keyword_list,
            url_slug=validate_input_text(url_slug, allow_commas=False) if url_slug else None
        )

        # SECURITY: Record image processing
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        await rate_limiter.record_request(client_ip, num_images=1)

        return JSONResponse(content={
            "success": True,
            "seo_metadata": seo_metadata,
            "alt_text": alt_text_data,
            "base_analysis": analysis
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating SEO metadata: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")


@router.post("/generate/complete")
async def generate_complete_package(
    request: Request,
    image: UploadFile = File(...),
    keywords: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None),
    product_brand: Optional[str] = Form(None),
    product_material: Optional[str] = Form(None),
    product_style: Optional[str] = Form(None),
    platforms: Optional[str] = Form("instagram,facebook,twitter")
):
    """Generate complete package: alt-text, social captions, and SEO metadata."""
    file_path = None
    try:
        # SECURITY: Validate and save upload
        upload_dir = Path(settings.upload_dir)
        file_path = await validate_and_save_upload(image, upload_dir, MAX_FILE_SIZE)

        # PERFORMANCE: Run blocking AI operation in thread pool
        analyzer = get_image_analyzer()
        analysis = await run_in_executor(analyzer.analyze_image, str(file_path))

        # SECURITY: Validate inputs
        product_info = {}
        if product_name:
            product_info["name"] = validate_input_text(product_name)
        if product_category:
            product_info["category"] = validate_input_text(product_category)
        if product_brand:
            product_info["brand"] = validate_input_text(product_brand)
        if product_material:
            product_info["material"] = validate_input_text(product_material)
        if product_style:
            product_info["style"] = validate_input_text(product_style)

        # Parse keywords
        keyword_list = None
        if keywords:
            keyword_list = [validate_input_text(k.strip()) for k in keywords.split(',')]

        # Parse platforms
        platform_list = [SocialPlatform(p.strip().lower()) for p in platforms.split(',')]

        # PERFORMANCE: Run blocking AI operation in thread pool
        alt_gen = get_alt_text_generator()
        alt_text = await run_in_executor(
            alt_gen.generate_alt_text,
            analysis,
            keywords=keyword_list,
            product_info=product_info if product_info else None
        )

        # PERFORMANCE: Run blocking AI operation in thread pool
        caption_gen = get_social_caption_generator()
        social_captions = await run_in_executor(
            caption_gen.generate_multi_platform,
            analysis,
            product_info=product_info if product_info else None,
            platforms=platform_list
        )

        # PERFORMANCE: Run blocking AI operation in thread pool
        seo_opt = get_seo_optimizer()
        seo_metadata = await run_in_executor(
            seo_opt.optimize_metadata,
            analysis,
            alt_text["standard"],
            product_info=product_info if product_info else None,
            target_keywords=keyword_list
        )

        # SECURITY: Record image processing
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        await rate_limiter.record_request(client_ip, num_images=1)

        return JSONResponse(content={
            "success": True,
            "alt_text": alt_text,
            "social_captions": social_captions,
            "seo_metadata": seo_metadata,
            "base_analysis": analysis
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating complete package: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
    finally:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")


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


@router.get("/rate-limit/status")
async def rate_limit_status(request: Request):
    """Get current rate limit status for the requesting IP."""
    # SECURITY: Use secure IP extraction
    client_ip = get_client_ip(request)
    rate_limiter = get_rate_limiter()
    quota = await rate_limiter.get_remaining_quota(client_ip)

    return {
        "ip": client_ip,
        "quota": quota,
        "message": "Free service with usage limits. Upgrade for higher limits.",
        "documentation": "/docs"
    }


@router.get("/admin/analytics")
async def admin_analytics(request: Request, authorization: str = Header(None)):
    """Get usage analytics (admin only).

    Args:
        request: Request object for logging
        authorization: Bearer token in Authorization header

    Returns:
        Usage statistics
    """
    client_ip = get_client_ip(request)

    # SECURITY: Fixed hardcoded credentials with logging
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning(f"SECURITY: Missing auth header from {client_ip}")
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    if not settings.admin_api_key:
        logger.error("SECURITY: Admin API accessed but ADMIN_API_KEY not configured")
        raise HTTPException(status_code=503, detail="Admin API not configured")

    if token != settings.admin_api_key:
        logger.warning(f"SECURITY: Failed admin authentication from {client_ip}")
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # Log successful admin access
    logger.info(f"SECURITY: Admin analytics accessed from {client_ip}")

    rate_limiter = get_rate_limiter()
    analytics = await rate_limiter.get_analytics()

    return {
        "analytics": analytics,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/batch/upload")
async def batch_upload(
    request: Request,
    images: List[UploadFile] = File(...),
    keywords: Optional[str] = Form(None),
    platforms: str = Form("instagram,facebook,twitter")
):
    """Upload multiple images for batch processing."""
    batch_dir = None
    try:
        # SECURITY: Check batch limit from configuration
        max_batch = settings.batch_limit
        if len(images) > max_batch:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {max_batch} images per batch (free service limit)"
            )

        # Generate batch ID
        batch_id = str(uuid.uuid4())
        batch_dir = Path(settings.upload_dir) / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)

        # SECURITY: Validate and save uploaded files
        saved_paths = []
        for idx, image in enumerate(images):
            try:
                file_path = await validate_and_save_upload(
                    image,
                    batch_dir,
                    MAX_BATCH_FILE_SIZE  # Smaller limit for batch
                )
                saved_paths.append(str(file_path))
            except HTTPException as e:
                logger.warning(f"Skipped invalid file {idx}: {e.detail}")
                continue

        if not saved_paths:
            raise HTTPException(status_code=400, detail="No valid images to process")

        # SECURITY: Validate inputs
        keyword_list = None
        if keywords:
            keyword_list = [validate_input_text(k.strip()) for k in keywords.split(',')]

        platform_list = [SocialPlatform(p.strip().lower()) for p in platforms.split(',')]

        # Process batch asynchronously
        async def process_single_image(image_path, product_info=None, keywords=None):
            """Process a single image."""
            analyzer = get_image_analyzer()
            alt_gen = get_alt_text_generator()
            caption_gen = get_social_caption_generator()
            seo_opt = get_seo_optimizer()

            # PERFORMANCE: Run blocking AI operations in thread pool
            analysis = await run_in_executor(analyzer.analyze_image, image_path)

            # PERFORMANCE: Run blocking AI operations in thread pool
            alt_text = await run_in_executor(
                alt_gen.generate_alt_text,
                analysis,
                keywords=keywords,
                product_info=product_info
            )

            # PERFORMANCE: Run blocking AI operations in thread pool
            social_captions = await run_in_executor(
                caption_gen.generate_multi_platform,
                analysis,
                product_info=product_info,
                platforms=platform_list
            )

            # PERFORMANCE: Run blocking AI operations in thread pool
            seo_metadata = await run_in_executor(
                seo_opt.optimize_metadata,
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

        # SECURITY: Record batch processing (images counted separately as they complete)
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        # Record the request, images will be counted as they're processed
        await rate_limiter.record_request(client_ip, num_images=0)

        return JSONResponse(content={
            "success": True,
            "batch_id": batch_id,
            "total_images": len(saved_paths),
            "status": "processing",
            "message": f"Processing {len(saved_paths)} images. Use /batch/status/{batch_id} to check progress."
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
    finally:
        # SECURITY: Clean up batch directory if processing never started
        # (If processing started, batch_processor will clean it up)
        # This handles the case where we fail before asyncio.create_task
        pass  # Cleanup happens in batch_processor after processing completes


@router.get("/batch/status/{batch_id}")
async def batch_status(batch_id: str):
    """Get status of a batch processing job."""
    try:
        # SECURITY: Validate batch ID format
        if not validate_batch_id(batch_id):
            raise HTTPException(status_code=400, detail="Invalid batch ID format")

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
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )


@router.get("/batch/results/{batch_id}")
async def batch_results(batch_id: str, request: Request):
    """Get results of a completed batch."""
    try:
        # SECURITY: Validate batch ID
        if not validate_batch_id(batch_id):
            raise HTTPException(status_code=400, detail="Invalid batch ID format")

        batch_processor = get_batch_processor()
        batch_data = batch_processor.get_batch_status(batch_id)

        if not batch_data:
            raise HTTPException(status_code=404, detail="Batch not found")

        if batch_data.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="Batch processing not yet completed"
            )

        # SECURITY: Record images for completed batch
        client_ip = get_client_ip(request)
        rate_limiter = get_rate_limiter()
        successful_count = batch_data.get("successful", 0)
        if successful_count > 0:
            await rate_limiter.record_request(client_ip, num_images=successful_count)

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
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )


@router.get("/batch/export/{batch_id}")
async def batch_export(batch_id: str, format: str = "csv"):
    """Export batch results to file."""
    try:
        # SECURITY: Validate batch ID
        if not validate_batch_id(batch_id):
            raise HTTPException(status_code=400, detail="Invalid batch ID format")

        if format not in ["csv", "json"]:
            raise HTTPException(
                status_code=400,
                detail="Format must be 'csv' or 'json'"
            )

        batch_processor = get_batch_processor()
        export_path = batch_processor.export_batch_results(batch_id, format)

        if not export_path:
            raise HTTPException(status_code=404, detail="Batch not found")

        return FileResponse(
            export_path,
            media_type="text/csv" if format == "csv" else "application/json",
            filename=f"batch_{batch_id}.{format}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting batch: {e}")
        # SECURITY: Don't expose internal errors to users
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )
