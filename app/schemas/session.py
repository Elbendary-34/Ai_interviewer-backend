from typing import Optional
from app.schemas.base import CamelModel


# --- Session lifecycle schemas ---

class SessionResponse(CamelModel):
    id: str
    user_id: str
    room_name: str
    status: str


class SessionStartResponse(CamelModel):
    id: str
    user_id: str
    room_name: str
    status: str
    livekit_token: str
    livekit_server_url: str
    interviewer_name: str = "Aria"
    interviewer_title: str
    total_questions: int = 5


class EndSessionResponse(CamelModel):
    message: str
    session_id: str
    task_id: str


# --- LiveKit reconnect schemas (formerly schemas/livekit.py) ---

class ReconnectTokenRequest(CamelModel):
    participant_name: Optional[str] = None


class ReconnectTokenResponse(CamelModel):
    token: str
    server_url: str
    room_name: str