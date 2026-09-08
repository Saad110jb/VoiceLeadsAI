from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.api.v1.vapi_webhook import router as vapi_router
from app.api.v1.n8n_relay import router as n8n_router
from app.api.v1.leads import router as leads_router
from app.utils.logger import logger

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"[STARTUP] {settings.PROJECT_NAME} v{settings.VERSION} starting on port {settings.PORT}...")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Microservice for VoiceLeads AI / VocalSync CRM",
    lifespan=lifespan
)

# Configure CORS for local development and WebRTC frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(vapi_router, prefix="/api/v1")
app.include_router(n8n_router, prefix="/api/v1")
app.include_router(leads_router, prefix="/api/v1")

START_TIME = time.time()

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy", "timestamp": time.time()}


