"""Configuration management for the AI Image Caption system."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Anthropic Claude API
    anthropic_api_key: Optional[str] = None
    use_claude_api: bool = False

    # Model Configuration
    caption_model: str = "Salesforce/blip-image-captioning-large"

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

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
