from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine
from app.db.base import Base
from app.api.v1.router import api_router
from app.services.redis_service import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("PostgreSQL Tables created successfully!")

    await redis_service.connect()
    print("Redis connection established.")

    yield

    await redis_service.close()
    await engine.dispose()
    print("Database & Redis connections closed gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# JWT auth is header-based (Authorization: Bearer <token>), not
# cookie-based, so allow_credentials is not needed — and combining it
# with a wildcard origin is invalid per the CORS spec anyway (browsers,
# including Flutter Web, will reject it).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root_health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Removed: /api/test-connection (duplicate of the "/" health check above)
# Removed: /sessions/setup-test (leftover debug endpoint — see sessions.py)