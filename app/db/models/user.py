# User Database Model
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_cv_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True) 
    cv_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class InterviewPreference(Base):
    __tablename__ = "interview_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False) 
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)    
    language: Mapped[str] = mapped_column(String(20), default="en")        
    interview_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False) 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())