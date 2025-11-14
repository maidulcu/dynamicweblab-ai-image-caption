"""Request size limit middleware for FastAPI."""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent DoS attacks."""

    def __init__(self, app, max_request_size: int = 50 * 1024 * 1024):
        """Initialize middleware.

        Args:
            app: FastAPI application
            max_request_size: Maximum request body size in bytes (default: 50MB)
        """
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """Check request size before processing.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response or error if request too large
        """
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                content_length = int(content_length)
                if content_length > self.max_request_size:
                    logger.warning(
                        f"Request too large: {content_length} bytes from {request.client.host}"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "Request too large",
                            "detail": f"Request body exceeds maximum size of {self.max_request_size / (1024 * 1024):.1f}MB",
                            "max_size_mb": self.max_request_size / (1024 * 1024)
                        }
                    )
            except ValueError:
                # Invalid Content-Length header
                pass

        response = await call_next(request)
        return response
