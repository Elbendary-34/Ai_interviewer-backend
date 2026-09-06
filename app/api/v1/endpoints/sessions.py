import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.config import settings
from app.db.models.session import InterviewSession, SessionStatus
from app.db.models.report import InterviewReport
from app.workers.tasks import process_interview_post_session
from app.services.livekit_service import livekit_service
from app.schemas.session import (
    SessionStartResponse,
    EndSessionResponse,
    ReconnectTokenRequest,
    ReconnectTokenResponse,
)
from app.schemas.report import ReportResponse

router = APIRouter()


@router.post("/start", response_model=SessionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    session_id = str(uuid.uuid4())
    room_name = f"room_{session_id[:8]}"

    new_session = InterviewSession(
        id=session_id,
        user_id=user_id,
        room_name=room_name,
        status=SessionStatus.IN_PROGRESS,
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    livekit_token = livekit_service.generate_token(
        room_name=room_name,
        participant_identity=user_id,
    )

    return SessionStartResponse(
        id=new_session.id,
        user_id=new_session.user_id,
        room_name=new_session.room_name,
        status=new_session.status.value,
        livekit_token=livekit_token,
        livekit_server_url=settings.LIVEKIT_URL,
        interviewer_title="AI Interview Specialist",
        total_questions=5,
    )


@router.post("/{session_id}/reconnect-token", response_model=ReconnectTokenResponse)
async def get_reconnect_token(
    session_id: str,
    payload: ReconnectTokenRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Formerly the standalone POST /livekit/token endpoint. Now scoped to an
    existing session: a client can only request a fresh LiveKit token for
    a room it's actually the owner of (e.g. after a dropped connection),
    instead of generating a token for an arbitrary room_name string.
    """
    result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session_obj = result.scalars().first()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")
    if session_obj.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")
    if session_obj.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Session has already ended")

    try:
        token = livekit_service.generate_token(
            room_name=session_obj.room_name,
            participant_identity=user_id,
            participant_name=payload.participant_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")

    return ReconnectTokenResponse(
        token=token,
        server_url=settings.LIVEKIT_URL,
        room_name=session_obj.room_name,
    )


@router.post("/end/{session_id}", response_model=EndSessionResponse)
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
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

    return EndSessionResponse(
        message="Session finished successfully. Report generation started in background.",
        session_id=session_id,
        task_id=task.id,
    )


@router.get("/{session_id}/report", response_model=ReportResponse)
async def get_session_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(InterviewReport).where(InterviewReport.session_id == session_id))
    report = result.scalars().first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found. The session might still be processing in the background.",
        )

    return ReportResponse.model_validate(report)