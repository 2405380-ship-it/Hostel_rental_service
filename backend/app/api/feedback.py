import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_optional_user
from app.core.sanitization import sanitize_text
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreateIn, FeedbackOut, FeedbackStatsOut

logger = logging.getLogger("hostelshare.feedback")
router = APIRouter(prefix="/feedback", tags=["Campus & Project Feedback"])

@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreateIn,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Submits project, usability, and campus experience feedback.
    Can be submitted by authenticated users, faculty evaluators, or guests.
    """
    user_id = current_user.id if current_user else None
    
    # Pre-fill name or email from user account if missing and user is logged in
    raw_name = payload.name.strip() if payload.name else None
    email = payload.email.strip() if payload.email else None

    if current_user:
        if not raw_name:
            raw_name = current_user.display_name or current_user.username

    # XSS Protection: Clean and HTML-escape text
    safe_name = sanitize_text(raw_name) or "Anonymous Peer"
    safe_feedback = sanitize_text(payload.feedback_text)
    safe_role = sanitize_text(payload.role) or "Student"
    safe_category = sanitize_text(payload.category) or "Overall Experience"

    feedback = Feedback(
        user_id=user_id,
        name=safe_name,
        email=email,
        role=safe_role,
        category=safe_category,
        overall_rating=payload.overall_rating,
        ease_of_use=payload.ease_of_use or payload.overall_rating,
        trust_safety=payload.trust_safety or payload.overall_rating,
        recommend=payload.recommend or "Definitely",
        feedback_text=safe_feedback,
    )


    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Attach user meta for response if available
    res = FeedbackOut.from_orm(feedback)
    if current_user:
        res.user_display_name = current_user.display_name or current_user.username
        res.user_avatar_url = current_user.avatar_url
    elif feedback.user:
        res.user_display_name = feedback.user.display_name or feedback.user.username
        res.user_avatar_url = feedback.user.avatar_url

    return res

@router.get("", response_model=List[FeedbackOut])
def get_feedbacks(
    category: Optional[str] = Query(None, description="Filter by feedback category"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns recent feedback submissions for community transparency and faculty review.
    """
    query = db.query(Feedback)
    if category and category != "All":
        query = query.filter(Feedback.category == category)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).limit(limit).all()

    output = []
    for fb in feedbacks:
        fb_out = FeedbackOut.from_orm(fb)
        if fb.user:
            fb_out.user_display_name = fb.user.display_name or fb.user.username
            fb_out.user_avatar_url = fb.user.avatar_url
        else:
            fb_out.user_display_name = fb.name or "Anonymous Peer"
        output.append(fb_out)

    return output

@router.get("/stats", response_model=FeedbackStatsOut)
def get_feedback_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated feedback metrics, averages, and distribution for academic review.
    """
    feedbacks = db.query(Feedback).all()
    total = len(feedbacks)
    if total == 0:
        return FeedbackStatsOut(
            total_feedbacks=0,
            average_rating=5.0,
            average_ease_of_use=5.0,
            average_trust_safety=5.0,
            category_counts={},
            rating_distribution={"5": 0, "4": 0, "3": 0, "2": 0, "1": 0},
            recommend_distribution={"Definitely": 0, "Likely": 0, "Neutral": 0, "Unlikely": 0}
        )

    avg_rating = round(sum(f.overall_rating for f in feedbacks) / total, 2)
    avg_ease = round(sum((f.ease_of_use or f.overall_rating) for f in feedbacks) / total, 2)
    avg_trust = round(sum((f.trust_safety or f.overall_rating) for f in feedbacks) / total, 2)

    cat_counts = {}
    for f in feedbacks:
        cat_counts[f.category] = cat_counts.get(f.category, 0) + 1

    rating_dist = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for f in feedbacks:
        key = str(f.overall_rating)
        rating_dist[key] = rating_dist.get(key, 0) + 1

    recommend_dist = {}
    for f in feedbacks:
        rec = f.recommend or "Definitely"
        recommend_dist[rec] = recommend_dist.get(rec, 0) + 1

    return FeedbackStatsOut(
        total_feedbacks=total,
        average_rating=avg_rating,
        average_ease_of_use=avg_ease,
        average_trust_safety=avg_trust,
        category_counts=cat_counts,
        rating_distribution=rating_dist,
        recommend_distribution=recommend_dist
    )
