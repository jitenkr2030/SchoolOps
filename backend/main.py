"""
SchoolOps Backend - FastAPI with REST and GraphQL APIs
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
import logging

from app.schema import schema
from app.db.database import engine, Base
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown"""
    # Startup: Create database tables
    logger.info("Starting SchoolOps API...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Continue anyway - tables might already exist
    yield
    # Shutdown: Cleanup
    logger.info("Shutting down SchoolOps API...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="SchoolOps API",
    description="""
    AI-Powered School Management System API
    
    ## Features
    - **Authentication**: JWT-based authentication with role-based access control
    - **Student Management**: Complete CRUD operations for Student Information System
    - **Staff Management**: Teacher and staff management
    - **Academics**: Classes, subjects, timetables, and assessments
    - **Attendance**: Student and staff attendance tracking
    - **Finance**: Fee management and payment processing
    - **Transport**: Bus tracking, routes, and student transport allocation
    - **Hostel**: Building, room, and bed management with allocation
    - **Inventory**: Asset and stock management
    - **Library**: Book catalog, circulation, and member management
    - **Communication**: Real-time chat, announcements, and meetings
    - **Reports**: Comprehensive analytics and dashboard statistics
    - **AI Insights**: Self-hosted AI for at-risk student detection and forecasting
    
    ## Authentication
    All protected endpoints require a valid JWT access token in the Authorization header:
    `Authorization: Bearer <token>`
    
    ## Self-Hosted AI
    This system is configured to work with self-hosted AI models (Ollama, local transformers)
    to avoid dependency on paid APIs like OpenAI.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REST API Routes ====================

# Import API routers
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.fees import router as fees_router
from app.api.payments import router as payments_router
from app.api.sms import router as sms_router
from app.api.staff import router as staff_router
from app.api.academics import router as academics_router
from app.api.attendance import router as attendance_router
from app.api.ai import router as ai_router
from app.api.inventory import router as inventory_router
from app.api.assets import router as assets_router
from app.api.suppliers import router as suppliers_router
from app.api.library import router as library_router
from app.api.transport import router as transport_router
from app.api.hostel import router as hostel_router
from app.api.communication import router as communication_router
from app.api.reports import router as reports_router

# Include REST API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(fees_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(sms_router, prefix="/api/v1")
app.include_router(staff_router, prefix="/api/v1")
app.include_router(academics_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(suppliers_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
app.include_router(transport_router, prefix="/api/v1")
app.include_router(hostel_router, prefix="/api/v1")
app.include_router(communication_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")

# ==================== GraphQL Router ====================

graphql_router = GraphQLRouter(schema)
app.include_router(graphql_router, prefix="/graphql")


# ==================== Health Check Endpoints ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "schoolops-api"
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies database connectivity
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}


# ==================== API Documentation ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SchoolOps API",
        "version": "1.0.0",
        "description": "AI-Powered School Management System",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "rest_api": "/api/v1",
            "graphql": "/graphql",
            "health": "/health"
        },
        "features": [
            "JWT Authentication",
            "Role-Based Access Control",
            "Student Information System",
            "Staff Management",
            "Attendance Tracking",
            "Fee Management",
            "Transport Management",
            "Hostel Management",
            "Inventory & Assets",
            "Library Management",
            "Communication (Chat & Announcements)",
            "Reports & Dashboards",
            "Self-Hosted AI Integration"
        ]
    }


# ==================== Error Handlers ====================

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Custom handler for validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# ==================== Run with uvicorn ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
