import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

from app.core.sanitization import verify_pin_rate_limit, record_failed_pin_attempt, clear_pin_rate_limit

def run_tests():
    client = TestClient(app)

    print("--- TEST 1: HTTP Security Headers ---")
    res = client.get("/health")
    assert res.status_code == 200
    headers = res.headers
    print("X-Content-Type-Options:", headers.get("X-Content-Type-Options"))
    assert headers.get("X-Content-Type-Options") == "nosniff"
    print("X-Frame-Options:", headers.get("X-Frame-Options"))
    assert headers.get("X-Frame-Options") == "DENY"
    print("X-XSS-Protection:", headers.get("X-XSS-Protection"))
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    print("Referrer-Policy:", headers.get("Referrer-Policy"))
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    print("Permissions-Policy:", headers.get("Permissions-Policy"))
    assert "camera=()" in headers.get("Permissions-Policy")
    print("-> Security Headers Test PASSED!")

    print("\n--- TEST 2: Stored XSS Neutralization ---")
    xss_payload = {
        "name": "<script>alert('XSS_NAME')</script>",
        "email": "student@kiit.ac.in",
        "role": "Student",
        "category": "Bug Report",
        "overall_rating": 4,
        "ease_of_use": 4,
        "trust_safety": 4,
        "recommend": "Likely",
        "feedback_text": "<img src=x onerror=alert('HACKED')> Hello <b>world</b>!"
    }
    fb_res = client.post("/api/feedback", json=xss_payload)
    assert fb_res.status_code == 201, fb_res.text
    fb_data = fb_res.json()
    print("Stored Name:", fb_data["name"])
    assert "<script>" not in fb_data["name"]
    assert "&lt;script&gt;" in fb_data["name"]
    print("Stored Feedback:", fb_data["feedback_text"])
    assert "<img" not in fb_data["feedback_text"]
    assert "&lt;img" in fb_data["feedback_text"]
    print("-> XSS Neutralization Test PASSED!")

    print("\n--- TEST 3: PIN Brute-Force Rate Limiting ---")
    rental_test_id = 999
    user_test_id = 888
    clear_pin_rate_limit(rental_test_id, user_test_id)

    for _ in range(4):
        record_failed_pin_attempt(rental_test_id, user_test_id)
    # 5th failed attempt triggers lockout
    record_failed_pin_attempt(rental_test_id, user_test_id)

    try:
        verify_pin_rate_limit(rental_test_id, user_test_id)
        assert False, "Should have raised 429 Too Many Requests"
    except HTTPException as exc:
        print("Rate limit triggered with code:", exc.status_code, "| Detail:", exc.detail)
        assert exc.status_code == 429
    print("-> PIN Brute-force Throttling Test PASSED!")

    print("\n--- TEST 4: Sensitive Endpoint (OTP) Rate Limiting ---")
    test_phone = "+919999988888"
    for i in range(5):
        otp_res = client.post("/api/auth/send-otp", json={"phone_number": test_phone})
        assert otp_res.status_code == 200, f"Attempt {i+1} failed"
    # 6th attempt should be blocked with 429
    blocked_otp_res = client.post("/api/auth/send-otp", json={"phone_number": test_phone})
    assert blocked_otp_res.status_code == 429
    print("Rate limit response:", blocked_otp_res.json())
    print("-> OTP Endpoint Throttling Test PASSED!")

    print("\n--- TEST 5: Large File Upload Defense (5MB limit) ---")
    from app.core.security import upload_media_file
    oversized_bytes = b"0" * (6 * 1024 * 1024)  # 6 MB
    try:
        upload_media_file(oversized_bytes, folder="items")
        assert False, "Should have rejected file > 5MB"
    except HTTPException as exc:
        print("Upload size limit triggered with code:", exc.status_code, "| Detail:", exc.detail)
        assert exc.status_code == 413
    print("-> Oversized File Upload Defense Test PASSED!")

    print("\n==========================================")
    print("ALL CYBER DEFENSE TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
