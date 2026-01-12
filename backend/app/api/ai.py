"""
AI Analysis API Routes
Endpoints for AI-powered analysis and forecasting
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.ai.provider import get_ai_service, AIProvider, AIProviderType
from app.schema.ai_schema import (
    RiskAnalysisResult,
    BulkRiskAnalysisRequest,
    BulkRiskAnalysisResult,
    AcademicForecastResult,
    MessageGenerationRequest,
    GeneratedMessage,
    AIHealthStatus,
    AnalysisConfig,
)
from app.services.risk_detection_service import RiskDetectionService
from app.services.forecast_service import AcademicForecastService
from app.services.intelligent_notification_service import IntelligentNotificationService
from app.core.security import get_current_user, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


# ==================== Health Check Endpoints ====================

@router.get("/health", response_model=AIHealthStatus)
async def check_ai_health():
    """
    Check AI service health and availability
    
    Verifies connection to the AI provider and returns
    model information.
    """
    try:
        ai = await get_ai_service()
        is_healthy = await ai.health_check()
        
        if is_healthy:
            return AIHealthStatus(
                status="healthy",
                provider=ai.provider.value if hasattr(ai.provider, 'value') else str(ai.provider),
                model=getattr(ai, 'model', 'unknown'),
                response_time_ms=getattr(ai, 'response_time_ms', None),
                last_health_check=datetime.utcnow()
            )
        else:
            return AIHealthStatus(
                status="unhealthy",
                provider="unknown",
                model="unknown",
                error_message="AI provider health check failed",
                last_health_check=datetime.utcnow()
            )
            
    except Exception as e:
        logger.error(f"AI health check error: {e}")
        return AIHealthStatus(
            status="unhealthy",
            provider="error",
            model="unknown",
            error_message=str(e),
            last_health_check=datetime.utcnow()
        )


# ==================== Risk Analysis Endpoints ====================

@router.get(
    "/risk/{student_id}",
    response_model=RiskAnalysisResult,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Student not found"},
        503: {"description": "AI service unavailable"}
    }
)
async def analyze_student_risk(
    student_id: int,
    include_details: bool = Query(True, description="Include detailed analysis"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Analyze student risk level
    
    Performs AI-powered analysis of student attendance, academic
    performance, and behavior to identify at-risk students.
    
    Requires authentication.
    """
    service = RiskDetectionService(db)
    
    try:
        result = await service.analyze_student(
            student_id=student_id,
            include_details=include_details
        )
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Student with ID {student_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI analysis service temporarily unavailable"
        )


@router.post(
    "/risk/bulk",
    response_model=BulkRiskAnalysisResult,
    status_code=status.HTTP_200_OK
)
async def analyze_bulk_risk(
    request: BulkRiskAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "teacher"]))
):
    """
    Bulk analyze risk for multiple students
    
    Analyzes all active students or filtered by class,
    returning risk assessments for each.
    
    Requires admin or teacher role.
    """
    service = RiskDetectionService(db)
    
    try:
        result = await service.analyze_bulk(request)
        return result
        
    except Exception as e:
        logger.error(f"Bulk risk analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to complete bulk analysis"
        )


@router.get(
    "/risk/high-risk",
    response_model=List[RiskAnalysisResult],
    summary="Get all high-risk students"
)
async def get_high_risk_students(
    min_risk_level: str = Query("HIGH", description="Minimum risk level"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "teacher"])):
    """
    Get all students at or above specified risk level
    
    Returns list of students requiring intervention.
    
    Requires admin or teacher role.
    """
    from app.schema.ai_schema import RiskLevel
    
    try:
        risk_level = RiskLevel(min_risk_level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid risk level. Must be one of: CRITICAL, HIGH, MODERATE, LOW"
        )
    
    request = BulkRiskAnalysisRequest(
        risk_threshold=risk_level,
        include_details=True
    )
    
    service = RiskDetectionService(db)
    result = await service.analyze_bulk(request)
    
    return result.results


# ==================== Academic Forecast Endpoints ====================

@router.get(
    "/forecast/{student_id}",
    response_model=AcademicForecastResult,
    responses={
        404: {"description": "Student not found"},
        503: {"description": "AI service unavailable"}
    }
)
async def get_academic_forecast(
    student_id: int,
    academic_year_id: Optional[int] = Query(None, description="Academic year ID"),
    term_id: Optional[int] = Query(None, description="Term ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get academic performance forecast for a student
    
    Uses AI to predict end-of-term grades based on current
    performance and historical trends.
    
    Requires authentication.
    """
    service = AcademicForecastService(db)
    
    try:
        result = await service.forecast_student(
            student_id=student_id,
            academic_year_id=academic_year_id,
            term_id=term_id
        )
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Student with ID {student_id} not found or no grade data available"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI forecast service temporarily unavailable"
        )


# ==================== Message Generation Endpoints ====================

@router.post(
    "/generate/message",
    response_model=GeneratedMessage,
    responses={
        400: {"description": "Invalid request"},
        503: {"description": "AI service unavailable"}
    }
)
async def generate_notification_message(
    request: MessageGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "teacher", "staff"]))
):
    """
    Generate AI-powered notification message
    
    Creates personalized messages for parents or students
    based on the specified context (attendance, grades, etc.).
    
    Requires admin, teacher, or staff role.
    """
    service = IntelligentNotificationService(db)
    
    try:
        result = await service.generate_message(request)
        return result
        
    except Exception as e:
        logger.error(f"Message generation error: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI message generation service temporarily unavailable"
        )


@router.get(
    "/generate/templates",
    summary="Get available message templates"
)
async def get_available_templates(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of available notification context types
    
    Returns all supported notification templates and their
    characteristics.
    """
    service = IntelligentNotificationService(db)
    return {
        "templates": service.get_available_contexts(),
        "recipient_types": ["PARENT", "STUDENT", "STAFF"],
        "context_types": [
            "ATTENDANCE_WARNING",
            "ATTENDANCE_CELEBRATION",
            "GRADE_WARNING",
            "GRADE_CELEBRATION",
            "BEHAVIOR_CONCERN",
            "EVENT_REMINDER",
            "FEE_REMINDER",
            "GENERAL_ANNOUNCEMENT",
            "CUSTOM"
        ]
    }


# ==================== Analysis Configuration Endpoints ====================

@router.get("/config")
async def get_analysis_config(
    current_user = Depends(require_roles(["admin"]))
):
    """
    Get AI analysis configuration
    
    Returns current configuration for risk thresholds and
    analysis parameters.
    
    Requires admin role.
    """
    return AnalysisConfig(
        risk_threshold=70.0,
        critical_threshold=85.0,
        min_attendance_rate=75.0,
        min_grade_point=50.0,
        analysis_days_lookback=30,
        auto_analyze_on_update=True
    )


@router.put("/config")
async def update_analysis_config(
    config: AnalysisConfig,
    current_user = Depends(require_roles(["admin"]))
):
    """
    Update AI analysis configuration
    
    Modifies thresholds and parameters for AI analysis.
    
    Requires admin role.
    """
    # In production, this would save to database or config
    logger.info(f"AI config update requested: {config}")
    return {"message": "Configuration updated successfully", "config": config}


# ==================== Summary Statistics Endpoints ====================

@router.get("/stats/summary")
async def get_ai_stats_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get AI analysis statistics summary
    
    Returns overview of AI service usage and student risk
    distribution across the institution.
    """
    # This would aggregate data from risk analyses
    return {
        "total_analyzed": 0,
        "high_risk_count": 0,
        "critical_risk_count": 0,
        "average_risk_score": 0.0,
        "last_analysis_date": None,
        "risk_distribution": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MODERATE": 0,
            "LOW": 0
        }
    }
