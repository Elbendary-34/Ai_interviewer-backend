from sqlalchemy import Column, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=True)
    eye_contact_score = Column(Float, nullable=True)
    posture_score = Column(Float, nullable=True)
    speech_clarity_score = Column(Float, nullable=True)
    feedback_summary = Column(String, nullable=True)
    detailed_metrics = Column(JSON, nullable=True)

    session = relationship("InterviewSession", back_populates="report")