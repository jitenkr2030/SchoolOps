"""
SchoolOps AI Services - Main Entry Point
FastAPI microservice for all AI capabilities
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routers import (
    analytics,
    personalization,
    automation,
    nlp,
    vision,
    optimization
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SchoolOps AI Services...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    yield
    logger.info("Shutting down SchoolOps AI Services...")


# Create FastAPI app
app = FastAPI(
    title="SchoolOps AI Services",
    description="AI-Powered features for School Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Predictions"])
app.include_router(personalization.router, prefix="/personalization", tags=["Personalization & Learning"])
app.include_router(automation.router, prefix="/automation", tags=["Automation & Assistants"])
app.include_router(nlp.router, prefix="/nlp", tags=["NLP & Conversational UX"])
app.include_router(vision.router, prefix="/vision", tags=["Document & Image Intelligence"])
app.include_router(optimization.router, prefix="/optimization", tags=["Resource Optimization"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "analytics": True,
            "personalization": True,
            "automation": True,
            "nlp": True,
            "vision": True,
            "optimization": True
        }
    }


@app.get("/")
async def root():
    return {
        "name": "SchoolOps AI Services",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/analytics",
            "/personalization",
            "/automation",
            "/nlp",
            "/vision",
            "/optimization"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
