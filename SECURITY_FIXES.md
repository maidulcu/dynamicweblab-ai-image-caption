# CRITICAL SECURITY FIXES REQUIRED BEFORE LAUNCH

## ⚠️ STATUS: NOT PRODUCTION READY

This document lists critical security vulnerabilities that **MUST** be fixed before deploying to production.

---

## ✅ FIXES COMPLETED

### 1. Secure Configuration Defaults
- ✅ Changed `API_HOST` default from `0.0.0.0` to `127.0.0.1`
- ✅ Changed `DEBUG` default from `True` to `False`
- ✅ Added `ADMIN_API_KEY` to environment variables
- ✅ Added `ALLOWED_ORIGINS` configuration
- ✅ Fixed CORS to use specific origins instead of `*`

### 2. Security Utilities Created
- ✅ Created `utils/security.py` with:
  - `sanitize_filename()` - Prevents path traversal
  - `validate_and_save_upload()` - Secure file upload with size validation
  - `validate_input_text()` - Input sanitization
  - `validate_batch_id()` - UUID validation
  - `get_client_ip()` - Secure IP extraction

---

## 🔴 CRITICAL FIXES STILL REQUIRED

### 1. **PATH TRAVERSAL in File Uploads** - CRITICAL
**Files:** `api/routes.py` (Lines: 122, 172, 263, 339, 430, 597)
**Risk:** Remote code execution, arbitrary file writes

**Current Code (UNSAFE):**
```python
file_path = upload_dir / image.filename  # VULNERABLE!
```

**Required Fix:**
```python
from utils import validate_and_save_upload

# Replace all file upload logic with:
file_path = await validate_and_save_upload(
    image,
    upload_dir,
    max_size=MAX_FILE_SIZE
)
```

**Affected Endpoints:**
- `/analyze`
- `/generate/alt-text`
- `/generate/social-caption`
- `/generate/seo-metadata`
- `/generate/complete`
- `/batch/upload`

---

### 2. **HARDCODED ADMIN CREDENTIALS** - CRITICAL
**File:** `api/routes.py` (Line: 556)
**Risk:** Unauthorized admin access

**Current Code (UNSAFE):**
```python
if api_key != "admin_secret_key_change_in_production":
```

**Required Fix:**
```python
from fastapi import Header

@router.get("/admin/analytics")
async def admin_analytics(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    if not settings.admin_api_key or token != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid credentials")
```

---

### 3. **MEMORY LEAK - Missing Cleanup** - CRITICAL
**Files:** All route handlers
**Risk:** Disk space exhaustion, OOM crashes

**Current Code (UNSAFE):**
```python
try:
    file_path = upload_dir / image.filename
    await save_upload_file(image, file_path)
    # ... processing ...
    file_path.unlink()  # Never reached if exception!
except Exception as e:
    raise HTTPException(...)
```

**Required Fix:**
```python
file_path = None
try:
    file_path = await validate_and_save_upload(image, upload_dir)
    # ... processing ...
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
finally:
    if file_path and file_path.exists():
        try:
            file_path.unlink()
        except Exception as cleanup_error:
            logger.error(f"Cleanup failed: {cleanup_error}")
```

---

### 4. **RATE LIMITING BYPASS** - CRITICAL
**File:** `middleware/rate_limit_middleware.py` (Line: 78)
**Risk:** Users can exceed image limits

**Current Code (BROKEN):**
```python
self.rate_limiter.record_request(client_ip, num_images=0)  # BUG!
```

**Required Fix:**
```python
# Remove line 78 from middleware entirely

# In each route handler AFTER successful processing:
from utils import get_client_ip
from core.rate_limiter import get_rate_limiter

client_ip = get_client_ip(request)
rate_limiter = get_rate_limiter()
rate_limiter.record_request(client_ip, num_images=1)  # or actual count
```

---

### 5. **IP SPOOFING** - CRITICAL
**File:** `middleware/rate_limit_middleware.py` (Lines: 104-110)
**Risk:** Rate limit bypass

**Current Code (UNSAFE):**
```python
forwarded = request.headers.get("X-Forwarded-For")
if forwarded:
    return forwarded.split(",")[0].strip()  # Trusts user input!
```

**Required Fix:**
```python
from utils import get_client_ip

# Use the secure utility function
client_ip = get_client_ip(request)
```

**Note:** Only trust proxy headers in production if behind a trusted reverse proxy and `TRUST_PROXY_HEADERS=True`.

---

### 6. **NO FILE SIZE VALIDATION** - HIGH
**Files:** All upload endpoints
**Risk:** DoS, disk exhaustion

**Required Fix:**
Already implemented in `validate_and_save_upload()`. Must use it in all endpoints.

---

### 7. **RACE CONDITIONS in Rate Limiter** - HIGH
**File:** `core/rate_limiter.py`
**Risk:** Corrupted data, inaccurate limits

**Required Fix:**
```python
import asyncio
from typing import Dict

class RateLimiter:
    def __init__(self, ...):
        self._lock = asyncio.Lock()
        self.request_history: Dict[str, list] = {}
        self.image_count: Dict[str, Dict] = {}

    async def check_rate_limit(self, ip: str, num_images: int = 1):
        async with self._lock:
            # ... existing logic ...

    async def record_request(self, ip: str, num_images: int = 1):
        async with self._lock:
            # ... existing logic ...
```

**Note:** All methods accessing shared state must be async and use the lock.

---

### 8. **INFINITE GROWTH Data Structures** - HIGH
**File:** `core/rate_limiter.py`
**Risk:** Memory leak

**Required Fix:**
```python
def _cleanup_old_data(self, max_age_days: int = 30):
    """Clean up data older than max_age_days."""
    cutoff_date = (datetime.utcnow() - timedelta(days=max_age_days)).date()

    # Clean image counts
    self.image_count = {
        ip: data for ip, data in self.image_count.items()
        if data.get("date") and
           datetime.fromisoformat(data["date"]).date() >= cutoff_date
    }

    # Clean blocked IPs
    now = datetime.utcnow()
    self.blocked_ips = {
        ip: time for ip, time in self.blocked_ips.items()
        if time > now
    }

# Call periodically in record_request:
if len(self.request_history) % 1000 == 0:
    self._cleanup_old_data()
```

---

### 9. **BATCH DIRECTORY CLEANUP Missing** - HIGH
**File:** `api/routes.py` (batch endpoints)
**Risk:** Disk space leak

**Required Fix:**
```python
import shutil

# After batch completion or on error:
batch_dir = Path(settings.upload_dir) / batch_id
if batch_dir.exists():
    try:
        shutil.rmtree(batch_dir)
    except Exception as e:
        logger.error(f"Failed to cleanup batch dir: {e}")
```

---

### 10. **BLOCKING OPERATIONS in Async** - HIGH
**Files:** All route handlers calling AI models
**Risk:** Event loop blocking, poor performance

**Required Fix:**
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Create executor (in main.py or as global)
executor = ThreadPoolExecutor(max_workers=4)

# In route handlers:
loop = asyncio.get_event_loop()
analysis = await loop.run_in_executor(
    executor,
    analyzer.analyze_image,
    str(file_path)
)
```

---

## 📋 STEP-BY-STEP FIX GUIDE

### Phase 1: Critical Security (DO FIRST)
1. ✅ Update `config.py` with security settings
2. ✅ Create `utils/security.py`
3. ✅ Fix CORS in `main.py`
4. ❌ Fix admin API key in `api/routes.py` (line 555)
5. ❌ Update all file upload handlers to use `validate_and_save_upload()`
6. ❌ Add `finally` blocks for cleanup in all handlers
7. ❌ Fix IP extraction in `middleware/rate_limit_middleware.py`
8. ❌ Fix rate limiter image counting

### Phase 2: High Priority
9. ❌ Make `RateLimiter` thread-safe with `asyncio.Lock`
10. ❌ Add data cleanup to `RateLimiter`
11. ❌ Add batch directory cleanup
12. ❌ Move AI operations to thread pool

### Phase 3: Testing
13. ❌ Test path traversal prevention
14. ❌ Test rate limiting accuracy
15. ❌ Test file size limits
16. ❌ Load test for race conditions
17. ❌ Test cleanup mechanisms

---

## 🔧 QUICK FIX SCRIPT

```bash
# 1. Set environment variables
cp .env.example .env
# Edit .env and set:
# - ADMIN_API_KEY=<generate strong random key>
# - ALLOWED_ORIGINS=<your domains>
# - DEBUG=False
# - API_HOST=127.0.0.1 (or 0.0.0.0 if behind proxy)

# 2. Install any missing dependencies
pip install -r requirements.txt

# 3. Run security audit
python -m pytest tests/test_security.py  # Create this!

# 4. Review logs
tail -f logs/security.log
```

---

## 🚨 DO NOT DEPLOY UNTIL

- [ ] All CRITICAL issues fixed
- [ ] All HIGH issues fixed
- [ ] Security tests passing
- [ ] Admin API key set
- [ ] CORS configured for production domains
- [ ] Debug mode disabled
- [ ] Rate limiting tested
- [ ] File upload security tested
- [ ] Memory leak tests passed

---

## 📞 NEED HELP?

If you need assistance fixing these issues:
1. Review each fix carefully
2. Test thoroughly in development
3. Consider security audit by professional
4. Set up monitoring and alerting

---

**Last Updated:** 2025-01-14
**Severity:** CRITICAL - DO NOT DEPLOY TO PRODUCTION
