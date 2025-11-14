"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.routes import router
from config import settings

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
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
                "complete_package": "/api/v1/generate/complete"
            }
        }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting AI Image Caption API...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload directory: {settings.upload_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down AI Image Caption API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
