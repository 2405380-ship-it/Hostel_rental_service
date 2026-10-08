import re
import html
import time
from typing import Optional, Dict, Tuple
from fastapi import HTTPException, status

# In-memory rate limiting store for PIN attempts: (rental_id, user_id) -> (failed_count, lock_until_timestamp)
_PIN_ATTEMPT_STORE: Dict[Tuple[int, int], Tuple[int, float]] = {}
MAX_PIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes

def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Sanitizes user string input to eliminate XSS (Cross-Site Scripting) vectors:
    - Normalizes null bytes and control chars
    - HTML-escapes (<, >, &, \", \') so malicious script tags cannot execute
    - Strips leading/trailing whitespace
    """
    if text is None:
        return None
    # Strip null bytes and non-printable control chars (except newline and tab)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(text))
    # Escape HTML special chars
    escaped = html.escape(cleaned.strip(), quote=True)
    return escaped

def sanitize_url(url: Optional[str]) -> Optional[str]:
    """
    Validates and sanitizes image / avatar URLs against URI scheme injection (e.g. javascript:, data:).
    Only allows http://, https://, and local static paths /uploads/.
    """
    if not url:
        return None
    clean_url = url.strip()
    # Reject dangerous schemes
    lower = clean_url.lower()
    if lower.startswith("javascript:") or lower.startswith("vbscript:") or lower.startswith("data:text/html"):
        return None
    if lower.startswith("http://") or lower.startswith("https://") or lower.startswith("/uploads/"):
        return clean_url
    return None

def verify_pin_rate_limit(rental_id: int, user_id: int):
    """
    Prevents brute-force attacks against 6-digit Handshake & Return PINs.
    Locks attempts if max failed tries exceeded.
    """
    key = (rental_id, user_id)
    now = time.time()
    if key in _PIN_ATTEMPT_STORE:
        failed_count, lock_until = _PIN_ATTEMPT_STORE[key]
        if now < lock_until:
            remaining = int(lock_until - now)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed PIN attempts. Verification is locked for {remaining} seconds to protect this rental."
            )
        elif lock_until > 0 and now >= lock_until:
            # Lock expired, reset
            _PIN_ATTEMPT_STORE[key] = (0, 0.0)

def record_failed_pin_attempt(rental_id: int, user_id: int):
    """Increments failed attempt count and triggers lock if threshold reached."""
    key = (rental_id, user_id)
    now = time.time()
    failed_count, _ = _PIN_ATTEMPT_STORE.get(key, (0, 0.0))
    failed_count += 1
    if failed_count >= MAX_PIN_ATTEMPTS:
        _PIN_ATTEMPT_STORE[key] = (failed_count, now + LOCKOUT_DURATION_SECONDS)
    else:
        _PIN_ATTEMPT_STORE[key] = (failed_count, 0.0)

def clear_pin_rate_limit(rental_id: int, user_id: int):
    """Clears rate limiter after a successful PIN verification."""
    key = (rental_id, user_id)
    _PIN_ATTEMPT_STORE.pop(key, None)

# In-memory sliding-window request store: identifier_key -> list of request timestamps
_ENDPOINT_RATE_STORE: Dict[str, list[float]] = {}

def check_endpoint_rate_limit(key: str, max_requests: int = 5, window_seconds: int = 60, action: str = "requests"):
    """
    Generic in-memory sliding-window rate limiter for sensitive endpoints (OTP, Feedback, Uploads).
    Raises HTTP 429 when max_requests within window_seconds is exceeded.
    """
    now = time.time()
    timestamps = _ENDPOINT_RATE_STORE.get(key, [])
    # Filter timestamps within current window
    valid_timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(valid_timestamps) >= max_requests:
        retry_after = int(window_seconds - (now - valid_timestamps[0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many {action}. Please try again in {max(1, retry_after)} seconds."
        )
    valid_timestamps.append(now)
    _ENDPOINT_RATE_STORE[key] = valid_timestamps

