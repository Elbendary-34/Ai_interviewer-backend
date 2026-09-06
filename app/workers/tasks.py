import asyncio
import uuid
import time
from typing import Coroutine, Any

from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.db.models.session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.user import CandidateProfile
from app.services.cv_parser import extract_text_from_file


def run_async(coro: Coroutine[Any, Any, None]) -> None:
    """
    Shared event-loop lifecycle for every Celery task in this module.
    Previously this exact 6-line block (new_event_loop / set_event_loop /
    run_until_complete / engine.dispose / close) was duplicated verbatim
    in both tasks below. Any new async Celery task now just calls
    run_async(my_coroutine(...)) instead of re-writing the boilerplate.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    finally:
        loop.run_until_complete(engine.dispose())
        loop.close()


@celery_app.task(name="generate_final_interview_report", bind=True, max_retries=3)
def process_interview_post_session(self, session_id: str, audio_file_path: str = None):
    print(f"[Celery Worker] Starting post-processing for Session: {session_id}")
    time.sleep(5)  # Simulate AI processing — replace with the real scoring pipeline

    report_metrics = {
        "overall_score": 88.5,
        "eye_contact_score": 90.0,
        "posture_score": 85.0,
        "speech_clarity_score": 90.5,
        "feedback_summary": "Great overall performance with stable body posture and strong eye contact.",
    }

    async def save_to_db():
        async with AsyncSessionLocal() as db:
            report = InterviewReport(
                id=f"rep_{session_id[:8]}",
                session_id=session_id,
                **report_metrics,
            )
            db.add(report)
            await db.commit()

    try:
        run_async(save_to_db())
    except Exception as exc:
        print(f"[Celery Worker] Error generating report: {exc}")
        raise self.retry(exc=exc, countdown=10)

    print(f"[Celery Worker] Report successfully saved to PostgreSQL for Session: {session_id}")
    return {"session_id": session_id, **report_metrics}


@celery_app.task(name="process_cv_analysis", bind=True, max_retries=3)
def process_cv_analysis(self, profile_id: str):
    print(f"[Celery Worker] Starting CV Parsing for Profile ID: {profile_id}")

    async def run_pipeline():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(CandidateProfile).where(CandidateProfile.id == uuid.UUID(profile_id))
            )
            profile = result.scalar_one_or_none()
            if not profile or not profile.cv_file_path:
                print(f"[Celery Worker] Profile or file path not found for ID: {profile_id}")
                return

            raw_text = extract_text_from_file(profile.cv_file_path)
            profile.raw_cv_text = raw_text

            # TODO: replace with a real skills-extraction AI call
            profile.skills = "Python, FastAPI, PostgreSQL, Docker, AsyncIO, REST APIs"

            await db.commit()
            print(f"[Celery Worker] CV Parsed & Analyzed successfully for Profile: {profile_id}")

    try:
        run_async(run_pipeline())
    except Exception as exc:
        print(f"[Celery Worker] Error parsing CV: {exc}")
        raise self.retry(exc=exc, countdown=10)