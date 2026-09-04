from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

router = APIRouter()

class LoginRequest(BaseModel):#define data from the user to login
    user_id: str

class TokenResponse(BaseModel):#define the response model for the login endpoint
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
        
    secret_key = str(getattr(settings, "SECRET_KEY", "super-secret-key-12345"))
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    
    to_encode = {
        "sub": str(payload.user_id), 
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return TokenResponse(access_token=encoded_jwt)