"""Configuration management for the AI Image Caption system."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "127.0.0.1"  # Bind to localhost by default for security
    api_port: int = 8000
    debug: bool = False  # Disable debug in production

    # Anthropic Claude API
    anthropic_api_key: Optional[str] = None
    use_claude_api: bool = False

    # Model Configuration
    caption_model: str = "Salesforce/blip-image-captioning-large"
    use_moondream: bool = True  # Use Moondream if available (better quality)
    moondream_model: str = "vikhyatk/moondream2"  # Moondream model version
    moondream_revision: str = "2025-06-21"  # Latest stable revision
    moondream_api_key: Optional[str] = None  # Moondream Cloud API key (optional)

    # SEO Configuration
    default_keywords: str = "product,shop,buy,online,quality"
    max_alt_text_length: int = 125

    # Social Media Configuration
    instagram_max_length: int = 2200
    twitter_max_length: int = 280
    facebook_max_length: int = 63206

    # Upload Configuration
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # Rate Limiting (FREE SERVICE)
    rate_limit_enabled: bool = True
    requests_per_minute: int = 10
    requests_per_hour: int = 100
    requests_per_day: int = 500
    images_per_day: int = 1000
    batch_limit: int = 50

    # Security
    admin_api_key: Optional[str] = None
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    trust_proxy_headers: bool = False  # Set True only in production with trusted proxy

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
