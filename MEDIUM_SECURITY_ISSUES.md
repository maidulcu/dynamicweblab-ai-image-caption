# MEDIUM SEVERITY SECURITY ISSUES

These issues don't pose immediate critical risks but should be addressed for production hardening.

---

## 📋 MEDIUM SEVERITY ISSUES (15 Total)

### 1. **Missing Security Headers** - MEDIUM
**File:** `main.py`
**Risk:** Clickjacking, MIME-sniffing attacks, XSS

**Required Fix:**
Add security headers middleware:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (for HTTPS)
- `Content-Security-Policy`

---

### 2. **API Documentation Exposed in Production** - MEDIUM
**File:** `main.py` (Lines: 25-26)
**Risk:** Information disclosure, API enumeration

**Current Code:**
```python
docs_url="/docs",
redoc_url="/redoc"
```

**Required Fix:**
Disable in production:
```python
docs_url="/docs" if settings.debug else None,
redoc_url="/redoc" if settings.debug else None
```

---

### 3. **No Request Size Limits** - MEDIUM
**File:** `main.py`
**Risk:** DoS via large request bodies

**Required Fix:**
```python
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(
    title="AI Image Caption Generator",
    # ... other config ...
    max_request_size=50 * 1024 * 1024  # 50MB
)
```

---

### 4. **No Health Check Endpoint** - MEDIUM
**File:** `api/routes.py`
**Risk:** Cannot monitor service health

**Required Fix:**
Add `/health` endpoint:
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

---

### 5. **Executor Not Shutdown on App Shutdown** - MEDIUM
**File:** `main.py` (shutdown_event)
**Risk:** Orphaned threads, incomplete processing

**Required Fix:**
```python
from utils import shutdown_executor

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Image Caption API...")
    shutdown_executor()
```

---

### 6. **No Security Event Logging** - MEDIUM
**Files:** `api/routes.py`, `middleware/rate_limit_middleware.py`
**Risk:** Cannot audit security events

**Required Fix:**
Log security events:
- Failed authentication attempts
- Rate limit violations (already logged partially)
- Invalid file uploads
- Suspicious activity

---

### 7. **Generic Error Messages Expose Info** - MEDIUM
**File:** `api/routes.py`
**Risk:** Information disclosure

**Current Code:**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

**Required Fix:**
```python
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise HTTPException(
        status_code=500,
        detail="Internal server error. Please try again later."
    )
```

---

### 8. **File Magic Bytes Not Validated** - MEDIUM
**File:** `utils/security.py`
**Risk:** Malicious file upload with fake content-type

**Current Code:**
Only checks `content_type` header (user-controlled)

**Required Fix:**
Use `python-magic` to verify actual file type:
```python
import magic

# After reading content:
mime_type = magic.from_buffer(content, mime=True)
if mime_type not in allowed_types:
    raise HTTPException(status_code=400, detail="Invalid file type")
```

---

### 9. **No Structured Logging** - MEDIUM
**File:** `main.py` (logging configuration)
**Risk:** Difficult to parse logs, poor monitoring

**Current Code:**
```python
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Required Fix:**
Use JSON structured logging:
```python
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.StreamHandler()
json_handler.setFormatter(formatter)
logger.addHandler(json_handler)
```

---

### 10. **Batch Results in Memory Only** - MEDIUM
**File:** `core/batch_processor.py`
**Risk:** Data loss on restart, memory exhaustion

**Current Code:**
```python
self.active_batches = {}  # In-memory only
```

**Required Fix:**
Persist to Redis or database

---

### 11. **No Request Timeout Configuration** - MEDIUM
**File:** `main.py`
**Risk:** Slow requests can block workers

**Required Fix:**
```python
uvicorn.run(
    "main:app",
    host=settings.api_host,
    port=settings.api_port,
    timeout_keep_alive=30,
    timeout_notify=30,
    reload=settings.debug
)
```

---

### 12. **No HTTPS Enforcement** - MEDIUM
**File:** `main.py`
**Risk:** Traffic not encrypted in production

**Required Fix:**
Add HTTPS redirect middleware (for production):
```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

### 13. **Environment Variables Not Validated at Startup** - MEDIUM
**File:** `main.py`, `config.py`
**Risk:** Runtime failures due to misconfiguration

**Required Fix:**
Validate critical settings at startup:
```python
@app.on_event("startup")
async def startup_event():
    # Validate required settings
    if not settings.admin_api_key and not settings.debug:
        raise RuntimeError("ADMIN_API_KEY must be set in production")

    if settings.allowed_origins == "*" and not settings.debug:
        raise RuntimeError("ALLOWED_ORIGINS must be configured in production")
```

---

### 14. **No API Rate Limit Per Endpoint** - MEDIUM
**File:** `middleware/rate_limit_middleware.py`
**Risk:** Some endpoints more expensive than others

**Required Fix:**
Different limits for different endpoints:
- `/analyze`: 10/min
- `/generate/complete`: 5/min (more expensive)
- `/batch/upload`: 2/min (very expensive)

---

### 15. **Static File Serving Without Cache Headers** - MEDIUM
**File:** `main.py` (Line 60)
**Risk:** Poor performance, unnecessary bandwidth

**Required Fix:**
```python
app.mount(
    "/static",
    StaticFiles(directory="static", html=True),
    name="static"
)

# Add cache headers for static files
from starlette.middleware import Middleware
from starlette.responses import Response

# Set cache headers
```

---

## 🔧 PRIORITY ORDER

1. **HIGH IMPACT, QUICK FIXES:**
   - #2: Disable docs in production
   - #5: Shutdown executor gracefully
   - #4: Add health check endpoint
   - #7: Generic error messages

2. **MEDIUM IMPACT:**
   - #1: Security headers
   - #3: Request size limits
   - #13: Environment validation
   - #6: Security event logging

3. **LOWER IMPACT:**
   - #8: File magic bytes validation
   - #9: Structured logging
   - #11: Timeout configuration
   - #12: HTTPS enforcement
   - #14: Per-endpoint rate limits
   - #15: Static file caching
   - #10: Batch result persistence

---

**Status:** 0/15 completed
**Recommendation:** Address top 8 issues before production launch
