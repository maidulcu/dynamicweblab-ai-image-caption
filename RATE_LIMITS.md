# Rate Limits & API Usage Policy

## Overview

This is a **FREE service** without login requirements. To prevent abuse and ensure fair usage for all users, we implement IP-based rate limiting.

## Rate Limits (Per IP Address)

| Limit Type | Free Tier | Time Window |
|-----------|-----------|-------------|
| **Requests** | 10 | Per minute |
| **Requests** | 100 | Per hour |
| **Requests** | 500 | Per day |
| **Images** | 1,000 | Per day |
| **Batch Size** | 50 | Per request |

## How It Works

### IP-Based Tracking
- Limits are enforced per IP address
- No login or API key required
- Resets automatically based on time windows

### Request Counting
- Each API call counts as 1 request
- Batch uploads count as 1 request (but images count separately)
- Failed requests still count toward limits

### Image Counting
- Single image upload = 1 image
- Batch upload of 50 images = 50 images
- Daily limit: 1,000 images per IP

## Rate Limit Headers

All API responses include rate limit information in headers:

```
X-RateLimit-Limit-Minute: 10
X-RateLimit-Limit-Hour: 100
X-RateLimit-Limit-Day: 500
X-RateLimit-Remaining-Minute: 8
X-RateLimit-Remaining-Hour: 95
X-RateLimit-Remaining-Day: 487
X-RateLimit-Images-Remaining: 950
```

## Checking Your Rate Limit Status

### API Endpoint
```bash
GET /api/v1/rate-limit/status
```

**Response:**
```json
{
  "ip": "123.45.67.89",
  "quota": {
    "requests_remaining": {
      "per_minute": 8,
      "per_hour": 95,
      "per_day": 487
    },
    "images_remaining": {
      "per_day": 950
    },
    "limits": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "requests_per_day": 500,
      "images_per_day": 1000,
      "batch_limit": 50
    }
  },
  "message": "Free service with usage limits. Upgrade for higher limits.",
  "documentation": "/docs"
}
```

## Error Responses

### 429 Too Many Requests

When you exceed rate limits, you'll receive a `429` response:

```json
{
  "error": "Rate limit exceeded",
  "message": "Rate limit exceeded: 10 requests per minute. Try again in 45 seconds.",
  "quota": {
    "requests_remaining": {
      "per_minute": 0,
      "per_hour": 85,
      "per_day": 450
    }
  },
  "documentation": "https://docs.example.com/rate-limits"
}
```

**HTTP Headers:**
```
Status: 429 Too Many Requests
Retry-After: 60
X-RateLimit-Remaining-Minute: 0
```

## Best Practices

### 1. Monitor Your Usage
```javascript
// Check rate limit before making requests
const checkRateLimit = async () => {
  const response = await fetch('/api/v1/rate-limit/status')
  const data = await response.json()
  console.log('Remaining requests:', data.quota.requests_remaining)
}
```

### 2. Handle Rate Limit Errors
```javascript
async function makeRequest(url, data) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      body: data
    })

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After')
      console.log(`Rate limited. Retry after ${retryAfter} seconds`)

      // Wait and retry
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000))
      return makeRequest(url, data)
    }

    return response
  } catch (error) {
    console.error('Request failed:', error)
  }
}
```

### 3. Batch Your Requests
Instead of processing images one by one, use batch upload:

```bash
# ❌ BAD: 50 individual requests
for i in {1..50}; do
  curl -X POST "/api/v1/generate/complete" -F "image=@img$i.jpg"
done

# ✅ GOOD: 1 batch request
curl -X POST "/api/v1/batch/upload" \
  -F "images=@img1.jpg" \
  -F "images=@img2.jpg" \
  ... (50 images)
```

### 4. Respect Retry-After Header
```python
import time
import requests

def make_request_with_retry(url, data):
    response = requests.post(url, data=data)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        print(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return make_request_with_retry(url, data)

    return response
```

## Rate Limit Reset Times

| Limit | Reset Period |
|-------|--------------|
| Per Minute | 60 seconds from first request |
| Per Hour | 60 minutes from first request |
| Per Day | 24 hours from first request |
| Images/Day | Midnight UTC |

## Temporary Blocking

Repeated abuse may result in temporary IP blocking:

- **First offense:** 1 hour block
- **Repeated offenses:** 24 hour block
- **Severe abuse:** Permanent block

## Excluded Endpoints

These endpoints are **NOT** rate limited:
- `GET /docs` - API documentation
- `GET /redoc` - API documentation (alternate)
- `GET /health` - Health check
- `GET /platforms` - Platform list
- `GET /openapi.json` - OpenAPI spec

## Upgrading Limits

For higher rate limits or commercial use:

1. **Contact us** for custom quotas
2. **API key authentication** for business accounts
3. **Dedicated instances** for enterprise

## Fair Use Policy

This free service is provided for:
- ✅ Personal projects
- ✅ Testing and evaluation
- ✅ Small businesses (< 1000 images/day)
- ✅ Educational use

**Not intended for:**
- ❌ High-volume commercial use
- ❌ Reselling API access
- ❌ Automated scraping
- ❌ Bulk processing (>1000 images/day)

## FAQ

### Why are there rate limits?
AI model inference is expensive. Rate limits ensure fair access for all users and prevent abuse.

### Can I get higher limits?
Yes! Contact us for business plans with higher limits and priority support.

### What if I'm behind a corporate proxy?
Rate limits are per IP. Multiple users behind the same IP share the same limits. Contact us for alternative solutions.

### How do I track my usage?
Use `GET /api/v1/rate-limit/status` to check your current usage and remaining quota.

### What happens to batch jobs if I hit limits?
Batch jobs that have already started will complete. New batch requests will be rejected until limits reset.

### Can I cache results?
Yes! Feel free to cache generated captions locally to reduce API usage.

## Usage Analytics

Administrators can view overall usage statistics:

```bash
GET /api/v1/admin/analytics?api_key=YOUR_ADMIN_KEY
```

**Response:**
```json
{
  "analytics": {
    "total_requests": 5234,
    "total_images_processed": 12450,
    "unique_ips": 127,
    "blocked_ips": 3,
    "active_ips_today": 42
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Support

For rate limit questions or upgrades:
- Email: support@dynamicweblab.com
- GitHub Issues: https://github.com/maidulcu/dynamicweblab-ai-image-caption/issues
- Documentation: https://docs.example.com

---

**Last Updated:** January 2025
**Version:** 1.0
