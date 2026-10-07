from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class FeedbackCreateIn(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    role: Optional[str] = Field("Student", max_length=50)
    category: str = Field(..., max_length=50)
    overall_rating: int = Field(..., ge=1, le=5)
    ease_of_use: Optional[int] = Field(5, ge=1, le=5)
    trust_safety: Optional[int] = Field(5, ge=1, le=5)
    recommend: Optional[str] = Field("Definitely", max_length=20)
    feedback_text: str = Field(..., min_length=3, max_length=2000)

class FeedbackOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = "Student"
    category: str
    overall_rating: int
    ease_of_use: Optional[int] = None
    trust_safety: Optional[int] = None
    recommend: Optional[str] = None
    feedback_text: str
    created_at: datetime
    user_display_name: Optional[str] = None
    user_avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class FeedbackStatsOut(BaseModel):
    total_feedbacks: int
    average_rating: float
    average_ease_of_use: float
    average_trust_safety: float
    category_counts: Dict[str, int]
    rating_distribution: Dict[str, int]
    recommend_distribution: Dict[str, int]
