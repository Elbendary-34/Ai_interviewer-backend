import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import aiofiles

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models.user import CandidateProfile, JobDescription, InterviewPreference
from app.workers.tasks import process_cv_analysis

router = APIRouter()

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#Pydantic Schemas
class JobDescriptionRequest(BaseModel):
    job_title: str
    description_text: str

class InterviewPreferenceRequest(BaseModel):
    company_name: str
    job_title: str
    language: str = "en"
    interview_date: datetime


#1. Upload CV Endpoint
@router.post("/upload-cv")
async def upload_cv(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed."
        )

    #Saving the file to the server
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)

    #Saving data to the database
    profile = CandidateProfile(
        user_id=user_id,
        cv_file_path=file_path,
        full_name=file.filename
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    #Sending the text extraction and CV analysis task to a Celery worker in the background
    process_cv_analysis.delay(str(profile.id))

    #Returning the file path in the response
    base_url = str(request.base_url).rstrip('/')
    file_url = f"{base_url}/{file_path.replace('\\', '/')}"

    return {
        "message": "CV uploaded successfully and analysis queued",
        "profile_id": str(profile.id),
        "file_path": file_path
    }


#2. Add Job Description Endpoint
@router.post("/job-description")
async def add_job_description(
    payload: JobDescriptionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    job = JobDescription(
        user_id=user_id,
        job_title=payload.job_title,
        description_text=payload.description_text
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return {
        "message": "Job Description saved successfully",
        "job_id": str(job.id)
    }


#3. Save Interview Preferences Endpoint
@router.post("/preferences")
async def save_interview_preferences(
    payload: InterviewPreferenceRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    pref = InterviewPreference(
        user_id=user_id,
        company_name=payload.company_name,
        job_title=payload.job_title,
        language=payload.language,
        interview_date=payload.interview_date
    )
    db.add(pref)
    await db.commit()
    await db.refresh(pref)

    return {
        "message": "Interview preferences saved successfully",
        "preference_id": str(pref.id)
    }