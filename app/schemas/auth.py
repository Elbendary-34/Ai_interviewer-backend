from app.schemas.base import CamelModel
class LoginRequest(CamelModel):
    user_id: str

class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"