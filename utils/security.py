"""Security and utility functions."""
import os
import re
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Maximum file sizes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_BATCH_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file in batch


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename from upload

    Returns:
        Safe filename with UUID prefix
    """
    # Get base filename only (removes any path components)
    base_name = os.path.basename(filename)

    # Remove any remaining suspicious characters
    safe_name = re.sub(r'[^\w\s.-]', '', base_name)

    # Limit length
    safe_name = safe_name[:100]

    # Add UUID prefix to ensure uniqueness and prevent collisions
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"

    return unique_name


async def validate_and_save_upload(
    upload_file: UploadFile,
    destination_dir: Path,
    max_size: int = MAX_FILE_SIZE,
    allowed_types: tuple = ('image/jpeg', 'image/png', 'image/webp', 'image/jpg')
) -> Path:
    """Validate and securely save an uploaded file.

    Args:
        upload_file: FastAPI UploadFile object
        destination_dir: Directory to save file
        max_size: Maximum file size in bytes
        allowed_types: Tuple of allowed MIME types

    Returns:
        Path to saved file

    Raises:
        HTTPException: If validation fails
    """
    # Validate content type
    if upload_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    # Read file content
    content = await upload_file.read()

    # Validate file size
    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB"
        )

    # Validate file is not empty
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Create destination directory
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_filename = sanitize_filename(upload_file.filename)
    file_path = destination_dir / safe_filename

    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    return file_path


def validate_input_text(
    text: Optional[str],
    max_length: int = 200,
    allow_commas: bool = True
) -> str:
    """Validate and sanitize text input to prevent injection attacks.

    Args:
        text: Input text
        max_length: Maximum allowed length
        allow_commas: Whether to allow commas

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Allow only alphanumeric, spaces, hyphens, periods, and optionally commas
    if allow_commas:
        pattern = r'[^\w\s,.-]'
    else:
        pattern = r'[^\w\s.-]'

    cleaned = re.sub(pattern, '', text)

    # Limit length
    cleaned = cleaned[:max_length].strip()

    return cleaned


def validate_batch_id(batch_id: str) -> bool:
    """Validate batch ID is a valid UUID.

    Args:
        batch_id: Batch ID to validate

    Returns:
        True if valid UUID format
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, batch_id.lower()))


def get_client_ip(request) -> str:
    """Extract client IP address from request.

    SECURITY: Only use this in production with proper proxy configuration.
    In development, returns actual client IP without trusting headers.

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address
    """
    # In production with trusted proxy, you can uncomment this:
    # forwarded = request.headers.get("X-Forwarded-For")
    # if forwarded:
    #     return forwarded.split(",")[0].strip()

    # For now, use direct client IP (safe default)
    if request.client:
        return request.client.host
    return "unknown"
