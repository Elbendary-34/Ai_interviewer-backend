from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta, timezone
import jwt

from app.core.config import settings
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {"sub": str(payload.user_id), "exp": expire}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return TokenResponse(access_token=encoded_jwt)