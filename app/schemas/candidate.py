from datetime import datetime
from app.schemas.base import CamelModel


class JobDescriptionRequest(CamelModel):
    job_title: str
    description_text: str


class InterviewPreferenceRequest(CamelModel):
    company_name: str
    job_title: str
    language: str = "en"
    interview_date: datetime


class CvUploadResponse(CamelModel):
    message: str
    profile_id: str
    file_path: str


class JobDescriptionResponse(CamelModel):
    message: str
    job_id: str


class InterviewPreferenceResponse(CamelModel):
    message: str
    preference_id: str