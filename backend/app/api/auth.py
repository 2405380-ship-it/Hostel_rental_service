import time
import random
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.sanitization import check_endpoint_rate_limit
from app.core.email import send_otp_email
from app.models.user import User
from app.schemas.user import SendOTPIn, VerifyOTPIn, TokenOut, UserOut

logger = logging.getLogger("hostelshare.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory store for dynamic email OTPs: clean_email -> (otp_code, expires_at_timestamp)
_ACTIVE_EMAIL_OTPS = {}

@router.post("/send-otp")
def send_otp(payload: SendOTPIn):
    """
    Initiates login by sending a 6-digit OTP code to a phone number or university email.
    If email is provided, dispatches branded campus verification code via Resend.
    Throttled to max 5 requests per 60 seconds.
    """
    raw_id = payload.phone_number.strip()
    is_email = "@" in raw_id

    if is_email:
        clean_id = raw_id.lower().replace(" ", "")
        if "." not in clean_id or len(clean_id) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a valid university email address."
            )
    else:
        clean_id = raw_id.replace(" ", "").replace("-", "")
        if len(clean_id) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a valid phone number with country code."
            )

    # Prevent SMS/Email bombing and spamming
    check_rate_limit_key = f"otp_send_{clean_id}"
    check_endpoint_rate_limit(check_rate_limit_key, max_requests=5, window_seconds=60, action="OTP requests")

    if is_email:
        # Generate random 6-digit code or fallback to mock in local dev
        has_email_service = bool(settings.BREVO_API_KEY and settings.BREVO_SENDER_EMAIL)
        otp_code = f"{random.randint(100000, 999999)}" if has_email_service else settings.DEV_MOCK_OTP
        _ACTIVE_EMAIL_OTPS[clean_id] = (otp_code, time.time() + 600)  # 10 minutes expiry
        send_otp_email(clean_id, otp_code)
        logger.info("Dispatched verification OTP to email %s", clean_id)
        return {
            "success": True,
            "message": f"Verification code sent to {clean_id}",
            "dev_mock_otp": otp_code if not has_email_service else None
        }

    # Phone flow (mock for local dev, SMS provider in production)
    logger.info("Mock OTP for phone %s is %s", clean_id, settings.DEV_MOCK_OTP)
    return {
        "success": True,
        "message": f"Verification code sent to {clean_id}",
        "dev_mock_otp": settings.DEV_MOCK_OTP
    }

@router.post("/verify-otp", response_model=TokenOut)
def verify_otp(payload: VerifyOTPIn, db: Session = Depends(get_db)):
    """
    Verifies the OTP code. If user is new, an account shell is provisioned.
    Returns JWT bearer token and onboarding status.
    """
    raw_id = payload.phone_number.strip()
    is_email = "@" in raw_id
    clean_id = raw_id.lower().replace(" ", "") if is_email else raw_id.replace(" ", "").replace("-", "")
    code = payload.otp_code.strip()

    # Rate limit verification attempts to prevent brute force
    check_endpoint_rate_limit(f"otp_verify_{clean_id}", max_requests=5, window_seconds=120, action="verification attempts")

    # Validate OTP against dynamic email OTP store or mock OTP
    is_valid = False
    if is_email and clean_id in _ACTIVE_EMAIL_OTPS:
        stored_code, expires_at = _ACTIVE_EMAIL_OTPS[clean_id]
        if time.time() <= expires_at and stored_code == code:
            is_valid = True
            _ACTIVE_EMAIL_OTPS.pop(clean_id, None)

    # Fallback to configured mock OTP (e.g. 123456)
    if not is_valid and (code == settings.DEV_MOCK_OTP or code == "123456"):
        is_valid = True

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code."
        )

    user = None
    if is_email:
        user = db.query(User).filter((User.email == clean_id) | (User.phone_number == clean_id)).first()
    else:
        user = db.query(User).filter(User.phone_number == clean_id).first()

    if not user:
        user = User(
            email=clean_id if is_email else None,
            # Assign clean_id to phone_number to ensure legacy NOT NULL & UNIQUE constraints pass on SQLite/PostgreSQL
            phone_number=clean_id,
            display_name=None,
            username=None,
            hostel_block=None,
            trust_rating=None,
            completed_rentals=0,
            is_onboarded=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Provisioned new user account with identifier %s", clean_id)
    else:
        if is_email and not user.email:
            user.email = clean_id
            db.commit()
            db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "identifier": clean_id})
    
    return TokenOut(
        access_token=token,
        token_type="bearer",
        is_onboarded=bool(user.is_onboarded and user.username),
        user=UserOut.model_validate(user)
    )
