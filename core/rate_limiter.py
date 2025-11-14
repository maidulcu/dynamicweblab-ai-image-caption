"""Rate limiting and usage tracking to prevent API abuse."""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class RateLimiter:
    """IP-based rate limiter for free API service."""

    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_hour: int = 100,
        requests_per_day: int = 500,
        images_per_day: int = 1000,
        batch_limit: int = 50
    ):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            requests_per_day: Max requests per day per IP
            images_per_day: Max images processed per day per IP
            batch_limit: Max images per batch request
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.images_per_day = images_per_day
        self.batch_limit = batch_limit

        # In-memory storage (use Redis in production)
        self.request_history: Dict[str, list] = defaultdict(list)
        self.image_count: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "date": None})
        self.blocked_ips: Dict[str, datetime] = {}

        # Usage analytics
        self.usage_file = Path("usage_analytics.json")
        self.load_analytics()

    def load_analytics(self):
        """Load usage analytics from file."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    self.request_history = defaultdict(list, data.get("request_history", {}))
                    self.image_count = defaultdict(
                        lambda: {"count": 0, "date": None},
                        data.get("image_count", {})
                    )
            except Exception as e:
                logger.error(f"Error loading analytics: {e}")

    def save_analytics(self):
        """Save usage analytics to file."""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump({
                    "request_history": dict(self.request_history),
                    "image_count": dict(self.image_count),
                    "last_updated": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def check_rate_limit(self, ip: str, num_images: int = 1) -> tuple[bool, Optional[str]]:
        """Check if IP is within rate limits.

        Args:
            ip: Client IP address
            num_images: Number of images in this request

        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Check if IP is blocked
        if ip in self.blocked_ips:
            unblock_time = self.blocked_ips[ip]
            if datetime.utcnow() < unblock_time:
                remaining = (unblock_time - datetime.utcnow()).seconds
                return False, f"IP temporarily blocked. Try again in {remaining} seconds."
            else:
                del self.blocked_ips[ip]

        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(ip, current_time)

        # Check batch size limit
        if num_images > self.batch_limit:
            return False, f"Batch size exceeds limit. Maximum {self.batch_limit} images per request."

        # Check requests per minute
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_history[ip] if t > minute_ago]
        if len(recent_requests) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute. Try again in {int(60 - (current_time - recent_requests[0]))} seconds."

        # Check requests per hour
        hour_ago = current_time - 3600
        hour_requests = [t for t in self.request_history[ip] if t > hour_ago]
        if len(hour_requests) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour. Try again later."

        # Check requests per day
        day_ago = current_time - 86400
        day_requests = [t for t in self.request_history[ip] if t > day_ago]
        if len(day_requests) >= self.requests_per_day:
            return False, f"Daily limit reached: {self.requests_per_day} requests per day. Resets in {self._time_until_reset(day_requests[0], 86400)}."

        # Check images per day
        today = datetime.utcnow().date()
        ip_data = self.image_count[ip]

        if ip_data["date"] == str(today):
            if ip_data["count"] + num_images > self.images_per_day:
                remaining = self.images_per_day - ip_data["count"]
                return False, f"Daily image limit reached: {self.images_per_day} images per day. You can process {remaining} more images today."
        else:
            # Reset daily counter
            ip_data["date"] = str(today)
            ip_data["count"] = 0

        return True, None

    def record_request(self, ip: str, num_images: int = 1):
        """Record a successful request.

        Args:
            ip: Client IP address
            num_images: Number of images processed
        """
        current_time = time.time()
        self.request_history[ip].append(current_time)

        # Update image count
        today = datetime.utcnow().date()
        ip_data = self.image_count[ip]
        if ip_data["date"] != str(today):
            ip_data["date"] = str(today)
            ip_data["count"] = 0
        ip_data["count"] += num_images

        # Save analytics periodically
        if len(self.request_history[ip]) % 10 == 0:
            self.save_analytics()

    def block_ip(self, ip: str, duration_minutes: int = 60):
        """Temporarily block an IP.

        Args:
            ip: IP address to block
            duration_minutes: Block duration in minutes
        """
        unblock_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip] = unblock_time
        logger.warning(f"Blocked IP {ip} until {unblock_time}")

    def get_remaining_quota(self, ip: str) -> Dict:
        """Get remaining quota for an IP.

        Args:
            ip: Client IP address

        Returns:
            Dictionary with remaining quotas
        """
        current_time = time.time()
        self._clean_old_requests(ip, current_time)

        # Calculate remaining requests
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        day_ago = current_time - 86400

        minute_requests = len([t for t in self.request_history[ip] if t > minute_ago])
        hour_requests = len([t for t in self.request_history[ip] if t > hour_ago])
        day_requests = len([t for t in self.request_history[ip] if t > day_ago])

        # Calculate remaining images
        today = datetime.utcnow().date()
        ip_data = self.image_count[ip]
        images_today = ip_data["count"] if ip_data["date"] == str(today) else 0

        return {
            "requests_remaining": {
                "per_minute": max(0, self.requests_per_minute - minute_requests),
                "per_hour": max(0, self.requests_per_hour - hour_requests),
                "per_day": max(0, self.requests_per_day - day_requests)
            },
            "images_remaining": {
                "per_day": max(0, self.images_per_day - images_today)
            },
            "limits": {
                "requests_per_minute": self.requests_per_minute,
                "requests_per_hour": self.requests_per_hour,
                "requests_per_day": self.requests_per_day,
                "images_per_day": self.images_per_day,
                "batch_limit": self.batch_limit
            }
        }

    def _clean_old_requests(self, ip: str, current_time: float):
        """Remove requests older than 24 hours.

        Args:
            ip: Client IP address
            current_time: Current timestamp
        """
        day_ago = current_time - 86400
        self.request_history[ip] = [t for t in self.request_history[ip] if t > day_ago]

    def _time_until_reset(self, first_request_time: float, window: int) -> str:
        """Calculate time until rate limit resets.

        Args:
            first_request_time: Timestamp of first request in window
            window: Time window in seconds

        Returns:
            Human-readable time string
        """
        reset_time = first_request_time + window
        remaining = int(reset_time - time.time())

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_analytics(self) -> Dict:
        """Get overall usage analytics.

        Returns:
            Dictionary with usage statistics
        """
        total_requests = sum(len(requests) for requests in self.request_history.values())
        total_images = sum(data["count"] for data in self.image_count.values())
        unique_ips = len(self.request_history)
        blocked_count = len(self.blocked_ips)

        return {
            "total_requests": total_requests,
            "total_images_processed": total_images,
            "unique_ips": unique_ips,
            "blocked_ips": blocked_count,
            "active_ips_today": len([
                ip for ip, data in self.image_count.items()
                if data["date"] == str(datetime.utcnow().date())
            ])
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(
    requests_per_minute: int = 10,
    requests_per_hour: int = 100,
    requests_per_day: int = 500,
    images_per_day: int = 1000,
    batch_limit: int = 50
) -> RateLimiter:
    """Get or create rate limiter instance.

    Args:
        requests_per_minute: Max requests per minute
        requests_per_hour: Max requests per hour
        requests_per_day: Max requests per day
        images_per_day: Max images per day
        batch_limit: Max batch size

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day,
            images_per_day=images_per_day,
            batch_limit=batch_limit
        )
    return _rate_limiter
