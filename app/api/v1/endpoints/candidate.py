import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models.user import CandidateProfile, JobDescription, InterviewPreference
from app.workers.tasks import process_cv_analysis
from app.schemas.candidate import (
    JobDescriptionRequest,
    InterviewPreferenceRequest,
    CvUploadResponse,
    JobDescriptionResponse,
    InterviewPreferenceResponse,
)

router = APIRouter()

UPLOAD_DIR = "uploads/cvs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-cv", response_model=CvUploadResponse)
async def upload_cv(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed.",
        )

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    content = await file.read()
    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(content)

    profile = CandidateProfile(
        user_id=user_id,
        cv_file_path=file_path,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    process_cv_analysis.delay(str(profile.id))

    normalized_path = file_path.replace("\\", "/")
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/{normalized_path}"

    return CvUploadResponse(
        message="CV uploaded successfully and analysis queued",
        profile_id=str(profile.id),
        file_path=file_url,
    )


@router.post("/job-description", response_model=JobDescriptionResponse)
async def add_job_description(
    payload: JobDescriptionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    job = JobDescription(
        user_id=user_id,
        job_title=payload.job_title,
        description_text=payload.description_text,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return JobDescriptionResponse(message="Job Description saved successfully", job_id=str(job.id))


@router.post("/preferences", response_model=InterviewPreferenceResponse)
async def save_interview_preferences(
    payload: InterviewPreferenceRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    pref = InterviewPreference(
        user_id=user_id,
        company_name=payload.company_name,
        job_title=payload.job_title,
        language=payload.language,
        interview_date=payload.interview_date,
    )
    db.add(pref)
    await db.commit()
    await db.refresh(pref)

    return InterviewPreferenceResponse(
        message="Interview preferences saved successfully", preference_id=str(pref.id)
    )