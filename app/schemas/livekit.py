from typing import Optional
from app.schemas.base import CamelModel
class TokenRequest(CamelModel):
    room_name: str
    participant_identity: str
    participant_name: Optional[str] = None

class TokenResponse(CamelModel):
    token: str
    # `to_camel` on CamelModel turns this into "serverUrl" automatically —
    # no more dead `class Config: fields = {...}` (that was Pydantic v1
    # syntax and had zero effect under Pydantic v2).
    server_url: str