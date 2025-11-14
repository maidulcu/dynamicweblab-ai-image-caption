"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.routes import router
from config import settings
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestSizeLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Image Caption Generator",
    description="Automatic generation of alt-text, social media captions, and SEO metadata for images",
    version="1.0.0",
    # SECURITY: Disable API docs in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add request size limit middleware (prevent DoS via large requests)
app.add_middleware(RequestSizeLimitMiddleware, max_request_size=50 * 1024 * 1024)  # 50MB

# Add CORS middleware with secure configuration
allowed_origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["*"],
)

# Add rate limiting middleware (FREE SERVICE PROTECTION)
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.requests_per_minute,
        requests_per_hour=settings.requests_per_hour,
        requests_per_day=settings.requests_per_day,
        images_per_day=settings.images_per_day,
        batch_limit=settings.batch_limit
    )

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Image Captioning"])

# Create upload directory
upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(exist_ok=True)

# Serve static files (web interface)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve web interface
from fastapi.responses import FileResponse


@app.get("/")
async def root():
    """Serve the web interface."""
    index_file = Path("static/index.html")
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return {
            "message": "AI Image Caption API",
            "version": "1.0.0",
            "docs": "/docs",
            "endpoints": {
                "analyze": "/api/v1/analyze",
                "alt_text": "/api/v1/generate/alt-text",
                "social_caption": "/api/v1/generate/social-caption",
                "seo_metadata": "/api/v1/generate/seo-metadata",
                "complete_package": "/api/v1/generate/complete",
                "batch_upload": "/api/v1/batch/upload",
                "rate_limit_status": "/api/v1/rate-limit/status"
            },
            "note": "This is a free service with rate limits. See /docs for details."
        }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting AI Image Caption API...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    logger.info(f"Allowed origins: {settings.allowed_origins}")

    # SECURITY: Validate critical environment variables for production
    if not settings.debug:
        if not settings.admin_api_key:
            raise RuntimeError(
                "CRITICAL: ADMIN_API_KEY must be set in production. "
                "Set DEBUG=True for development or configure ADMIN_API_KEY."
            )

        if settings.allowed_origins == "*" or "http://localhost" in settings.allowed_origins:
            raise RuntimeError(
                "CRITICAL: ALLOWED_ORIGINS must be configured for production domains. "
                "Current value includes localhost or wildcard."
            )

        logger.info("✓ Production environment validation passed")
    else:
        if not settings.admin_api_key:
            logger.warning("WARNING: ADMIN_API_KEY not set. Admin endpoints will be inaccessible.")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down AI Image Caption API...")

    # PERFORMANCE: Gracefully shutdown thread pool executor
    from utils import shutdown_executor
    shutdown_executor()
    logger.info("✓ Thread pool executor shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
