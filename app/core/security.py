import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_scheme = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    token = credentials.credentials
    # Retrieve the secret key from settings or use a default value
    secret_key = str(getattr(settings, "SECRET_KEY", "super-secret-key-12345"))
    
    try:
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials / Invalid JWT Token"
        )