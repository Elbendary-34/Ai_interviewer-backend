# LiveKit Room & Token Endpoints
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import get_current_user_id
from app.schemas.livekit import TokenRequest, TokenResponse
from app.services.livekit_service import livekit_service

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def get_livekit_token(
    request: TokenRequest,
    user_id: str = Depends(get_current_user_id),  # was completely unauthenticated before
):
    try:
        token = livekit_service.generate_token(
            room_name=request.room_name,
            participant_identity=request.participant_identity,
            participant_name=request.participant_name,
        )
        return TokenResponse(
            token=token,
            server_url=settings.LIVEKIT_URL,  # was settings.LIVEKIT_SERVER_URL, which doesn't exist
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")