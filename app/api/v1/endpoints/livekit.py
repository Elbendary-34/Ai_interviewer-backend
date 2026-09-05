# LiveKit Room & Token Endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.livekit_service import livekit_service
from app.core.config import settings

router = APIRouter()

class TokenRequest(BaseModel):
    room_name: str
    participant_identity: str
    participant_name: str = None

class TokenResponse(BaseModel):
    token: str
    server_url: str

    class Config:
        fields = {'server_url': 'serverUrl'}

@router.post("/token", response_model=TokenResponse)
async def get_livekit_token(request: TokenRequest):
    try:
        token = livekit_service.generate_token(
            room_name=request.room_name,
            participant_identity=request.participant_identity,
            participant_name=request.participant_name
        )
        return TokenResponse(
            token=token,
            server_url=settings.LIVEKIT_SERVER_URL
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")