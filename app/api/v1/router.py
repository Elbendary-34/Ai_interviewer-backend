# API Router Aggregator
from fastapi import APIRouter
from app.api.v1.endpoints import ws_analytics, sessions, auth, candidate

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(ws_analytics.router, tags=["Real-time Analytics"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(candidate.router, prefix="/candidates", tags=["Candidates"])