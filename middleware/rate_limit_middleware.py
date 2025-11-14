"""FastAPI middleware for rate limiting."""
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.rate_limiter import get_rate_limiter
from utils import get_client_ip

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits on API requests."""

    def __init__(self, app, **kwargs):
        """Initialize middleware.

        Args:
            app: FastAPI application
            **kwargs: Rate limiter configuration
        """
        super().__init__(app)
        self.rate_limiter = get_rate_limiter(**kwargs)
        self.excluded_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/platforms"]

    async def dispatch(self, request: Request, call_next):
        """Process request and enforce rate limits.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with rate limit headers
        """
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Get client IP securely
        client_ip = get_client_ip(request)

        # Determine number of images in request
        num_images = 1
        if "batch" in request.url.path:
            # For batch endpoints, we'll check this in the route handler
            # Set a reasonable default here
            num_images = self.rate_limiter.batch_limit

        # Check rate limit
        is_allowed, error_message = await self.rate_limiter.check_rate_limit(client_ip, num_images)

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {error_message}")

            # Get remaining quota
            quota = await self.rate_limiter.get_remaining_quota(client_ip)

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": error_message,
                    "quota": quota,
                    "documentation": "https://docs.example.com/rate-limits"
                },
                headers={
                    "X-RateLimit-Limit-Minute": str(self.rate_limiter.requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.rate_limiter.requests_per_hour),
                    "X-RateLimit-Limit-Day": str(self.rate_limiter.requests_per_day),
                    "X-RateLimit-Remaining-Minute": str(quota["requests_remaining"]["per_minute"]),
                    "X-RateLimit-Remaining-Hour": str(quota["requests_remaining"]["per_hour"]),
                    "X-RateLimit-Remaining-Day": str(quota["requests_remaining"]["per_day"]),
                    "Retry-After": "60"
                }
            )

        # Process request (image counting happens in route handlers after successful processing)
        response = await call_next(request)

        # Add rate limit headers to successful responses
        quota = await self.rate_limiter.get_remaining_quota(client_ip)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.rate_limiter.requests_per_hour)
        response.headers["X-RateLimit-Limit-Day"] = str(self.rate_limiter.requests_per_day)
        response.headers["X-RateLimit-Remaining-Minute"] = str(quota["requests_remaining"]["per_minute"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(quota["requests_remaining"]["per_hour"])
        response.headers["X-RateLimit-Remaining-Day"] = str(quota["requests_remaining"]["per_day"])
        response.headers["X-RateLimit-Images-Remaining"] = str(quota["images_remaining"]["per_day"])

        return response


async def record_image_processing(client_ip: str, num_images: int):
    """Record actual image processing after successful request.

    Args:
        client_ip: Client IP address
        num_images: Number of images processed
    """
    rate_limiter = get_rate_limiter()
    await rate_limiter.record_request(client_ip, num_images)
