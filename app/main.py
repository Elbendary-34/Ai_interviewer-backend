from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware #allow frontend to request data from backend

from app.core.config import settings
from app.core.database import engine
from app.db.base import Base
from app.api.v1.router import api_router #center of all endpoints for layer 2 of the application


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create PostgreSQL tables automatically if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("PostgreSQL Tables created successfully!")
    
    yield
    
    # Shutdown: Dispose engine connection pool gracefully
    await engine.dispose()
    print("Database connection closed gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for Frontend (Flutter / Web) integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #allow frontend to request data from backend
    allow_credentials=True,
    allow_methods=["*"], #allow methods and headers from frontend to backend and headers 
    allow_headers=["*"],
)

# Root Health Check Endpoint
@app.get("/", tags=["Health"])
async def root_health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

# Include API Router for Layer 2 Endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)