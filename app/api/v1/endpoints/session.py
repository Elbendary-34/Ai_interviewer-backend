from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.db.models.session import InterviewSession, SessionStatus
from app.db.models.report import InterviewReport
from app.workers.tasks import process_interview_post_session
from app.core.security import get_current_user_id  # Import JWT dependency

router = APIRouter()

class SessionResponse(BaseModel):
    id: str
    user_id: str
    room_name: str
    status: str

@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)  # Protected route
):
    session_id = str(uuid.uuid4())
    room_name = f"room_{session_id[:8]}"
    
    new_session = InterviewSession(
        id=session_id,
        user_id=user_id,  # Uses authenticated user ID
        room_name=room_name,
        status=SessionStatus.IN_PROGRESS
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    return SessionResponse(
        id=new_session.id,
        user_id=new_session.user_id,
        room_name=new_session.room_name,
        status=new_session.status.value if hasattr(new_session.status, 'value') else str(new_session.status)
    )

@router.post("/end/{session_id}")
async def end_session(
    session_id: str, 
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)  # Protected route
):
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session_obj = result.scalars().first()
    
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if session_obj.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to end this session")
        
    session_obj.status = SessionStatus.COMPLETED
    await db.commit()
    
    task = process_interview_post_session.delay(session_id=session_id)
    
    return {
        "message": "Session finished successfully. Report generation started in background.",
        "session_id": session_id,
        "task_id": task.id
    }

@router.get("/{session_id}/report")
async def get_session_report(
    session_id: str, 
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)  # Protected route
):
    result = await db.execute(select(InterviewReport).where(InterviewReport.session_id == session_id))
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(
            status_code=404, 
            detail="Report not found. The session might still be processing in the background."
        )
        
    return {
        "session_id": report.session_id,
        "overall_score": report.overall_score,
        "eye_contact_score": report.eye_contact_score,
        "posture_score": report.posture_score,
        "speech_clarity_score": report.speech_clarity_score,
        "feedback_summary": report.feedback_summary
    }