import time
import uuid
import asyncio
from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.db.models.session import InterviewSession  
from app.db.models.report import InterviewReport
from app.db.models.user import CandidateProfile
from app.services.cv_parser import extract_text_from_file

@celery_app.task(name="generate_final_interview_report")
def process_interview_post_session(session_id: str, audio_file_path: str = None):
    print(f"[Celery Worker] Starting post-processing for Session: {session_id}")
    time.sleep(5)  # Simulate AI processing

    report_metrics = {
        "overall_score": 88.5,
        "eye_contact_score": 90.0,
        "posture_score": 85.0,
        "speech_clarity_score": 90.5,
        "feedback_summary": "Great overall performance with stable body posture and strong eye contact."
    }

    async def save_to_db():
        async with AsyncSessionLocal() as db:
            report = InterviewReport(
                id=f"rep_{session_id[:8]}",
                session_id=session_id,
                **report_metrics
            )
            db.add(report)
            await db.commit()

    # Simulate saving to database with proper cleanup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(save_to_db())
    finally:
        loop.run_until_complete(engine.dispose())
        loop.close()

    print(f"[Celery Worker] Report successfully saved to PostgreSQL for Session: {session_id}")
    return {"session_id": session_id, **report_metrics}


@celery_app.task(name="process_cv_analysis", bind=True, max_retries=3)
def process_cv_analysis(self, profile_id: str):
    """Celery task to process CV parsing and analysis for a given candidate profile."""
    print(f"[Celery Worker] Starting CV Parsing for Profile ID: {profile_id}")
    
    async def run_pipeline():
        async with AsyncSessionLocal() as db:
            #1. Fetching profile data
            result = await db.execute(
                select(CandidateProfile).where(CandidateProfile.id == uuid.UUID(profile_id))
            )
            profile = result.scalar_one_or_none()
            if not profile or not profile.cv_file_path:
                print(f"[Celery Worker] Profile or file path not found for ID: {profile_id}")
                return

            # 2. Extracting text from the PDF/DOCX
            raw_text = extract_text_from_file(profile.cv_file_path)
            profile.raw_cv_text = raw_text

            # 3. Place to call the AI Agent
            mock_skills = "Python, FastAPI, PostgreSQL, Docker, AsyncIO, REST APIs"
            profile.skills = mock_skills

            # 4. Saving updates to the database
            await db.commit()
            print(f"[Celery Worker] CV Parsed & Analyzed successfully for Profile: {profile_id}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_pipeline())
    except Exception as exc:
        print(f"[Celery Worker] Error parsing CV: {exc}")
        raise self.retry(exc=exc, countdown=10)
    finally:
        loop.run_until_complete(engine.dispose())
        loop.close()