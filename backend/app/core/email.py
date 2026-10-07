import logging
from typing import Optional, List
import requests
from app.core.config import settings

logger = logging.getLogger("hostelshare.email")

RESEND_API_ENDPOINT = "https://api.resend.com/emails"

def send_email(
    to: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Dispatches transactional email via Resend REST API.
    If RESEND_API_KEY is not configured or in dev mode, gracefully logs to console.
    """
    api_key = settings.RESEND_API_KEY.strip() if settings.RESEND_API_KEY else ""

    if not api_key:
        logger.info(
            "[DEV MODE] Email to <%s> not dispatched via API (RESEND_API_KEY not configured). Subject: '%s'",
            to, subject
        )
        return True

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": settings.EMAILS_FROM,
        "to": [to],
        "subject": subject,
        "html": html_content,
    }
    if text_content:
        payload["text"] = text_content

    try:
        response = requests.post(
            RESEND_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=8
        )
        if response.status_code in (200, 201):
            logger.info("Email successfully dispatched via Resend to <%s>. ID: %s", to, response.json().get("id"))
            return True
        else:
            logger.warning(
                "Resend API error (%s): %s. Fallback logged.",
                response.status_code, response.text
            )
            return False
    except Exception as e:
        logger.error("Failed to connect to Resend API: %s", e)
        return False


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Sends campus authentication OTP code via Resend.
    """
    subject = f"Your HostelShare Verification Code: {otp_code}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 480px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155; }}
        .logo {{ font-size: 24px; font-weight: 800; color: #10b981; letter-spacing: -0.5px; margin-bottom: 8px; }}
        .subtitle {{ font-size: 14px; color: #94a3b8; margin-bottom: 24px; }}
        .code-box {{ background-color: #0f172a; border-radius: 8px; padding: 16px; text-align: center; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #38bdf8; border: 1px dashed #0284c7; margin: 24px 0; }}
        .footer {{ font-size: 12px; color: #64748b; margin-top: 24px; line-height: 1.5; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">HostelShare</div>
        <div class="subtitle">Campus Peer-to-Peer Rental Service</div>
        <p>Hello,</p>
        <p>Use the following 6-digit verification code to log in to your account:</p>
        <div class="code-box">{otp_code}</div>
        <p style="font-size: 14px; color: #cbd5e1;">This code is valid for <strong>10 minutes</strong>. Do not share this code with anyone.</p>
        <div class="footer">
          If you did not request this login code, you can safely ignore this email.<br>
          HostelShare &bull; University Campus Equipment & Utility Sharing
        </div>
      </div>
    </body>
    </html>
    """
    
    text_content = f"Your HostelShare verification code is: {otp_code}. Valid for 10 minutes."
    return send_email(to_email, subject, html_content, text_content)


def send_rental_notification_email(to_email: str, subject: str, headline: str, message: str, pin: Optional[str] = None) -> bool:
    """
    Sends transactional notification for rental requests, acceptances, and returns.
    """
    pin_html = f"""
    <div style="background-color: #0f172a; border-radius: 8px; padding: 12px; text-align: center; margin: 16px 0; border: 1px solid #334155;">
        <span style="font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Handover PIN</span><br>
        <strong style="font-size: 24px; color: #10b981; letter-spacing: 3px;">{pin}</strong>
    </div>
    """ if pin else ""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 480px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155; }}
        .logo {{ font-size: 22px; font-weight: 800; color: #10b981; margin-bottom: 16px; }}
        .headline {{ font-size: 18px; font-weight: 600; color: #f8fafc; margin-bottom: 12px; }}
        .text {{ font-size: 14px; color: #cbd5e1; line-height: 1.6; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">HostelShare</div>
        <div class="headline">{headline}</div>
        <div class="text">{message}</div>
        {pin_html}
        <p style="font-size: 12px; color: #64748b; margin-top: 24px;">HostelShare &bull; Peer-to-Peer Campus Utility Sharing</p>
      </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_content, message)
