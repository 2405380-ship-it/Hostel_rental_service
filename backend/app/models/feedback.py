from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    role = Column(String(50), default="Student")  # Student, Faculty Evaluator, Hostel Resident, Guest
    category = Column(String(50), nullable=False, default="Overall Experience")
    overall_rating = Column(Integer, nullable=False, default=5)  # 1 to 5
    ease_of_use = Column(Integer, nullable=True, default=5)       # 1 to 5
    trust_safety = Column(Integer, nullable=True, default=5)      # 1 to 5
    recommend = Column(String(20), nullable=True, default="Definitely") # Definitely, Likely, Neutral, Unlikely
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional relationship to user
    user = relationship("User", foreign_keys=[user_id])
