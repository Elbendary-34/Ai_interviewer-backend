# API Router Aggregator
from fastapi import APIRouter
from app.api.v1.endpoints import livekit, ws_analytics, session, auth
from app.api.v1.endpoints import candidate

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# Include LiveKit REST Router
api_router.include_router(livekit.router, prefix="/livekit", tags=["LiveKit"])

# Include WebSocket Router
api_router.include_router(ws_analytics.router, tags=["Real-time Analytics"])

# Include Sessions Router
api_router.include_router(session.router, prefix="/sessions", tags=["Sessions"])

# Include Candidate Router
api_router.include_router(candidate.router, prefix="/candidates", tags=["Candidates"])