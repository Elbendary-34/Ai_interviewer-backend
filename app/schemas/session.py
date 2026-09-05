from typing import Optional
from app.schemas.base import CamelModel


class SessionResponse(CamelModel):
    id: str
    user_id: str
    room_name: str
    status: str


class SessionStartResponse(CamelModel):
    """
    Returned by POST /sessions/start. Bundles the session record with
    everything the Flutter client needs to immediately join the LiveKit
    room and render the live-interview screen in a single round trip —
    no separate /livekit/token call required on the happy path.
    """
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