# Base model registry for Alembic
from app.core.database import Base
from app.db.models.session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.user import CandidateProfile, JobDescription, InterviewPreference

# Expose Base metadata for table generation
__all__ = ["Base", "InterviewSession", "InterviewReport", "CandidateProfile", "JobDescription", "InterviewPreference"]