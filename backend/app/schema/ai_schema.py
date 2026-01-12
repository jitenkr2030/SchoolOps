"""
AI Analysis Schemas
Pydantic models for AI-powered analysis results
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ==================== Risk Assessment Schemas ====================

class RiskLevel(str, Literal):
    """Risk level classification"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class RiskFactor(BaseModel):
    """Individual risk factor identified by AI analysis"""
    factor: str = Field(..., description="Description of the risk factor")
    weight: float = Field(..., ge=0, le=1, description="Importance weight of this factor")
    trend: RiskLevel = Field(..., description="Current trend direction")


class RiskAnalysisResult(BaseModel):
    """
    Result of AI-powered student risk analysis
    
    This schema represents the output of the risk detection service,
    providing a comprehensive assessment of student academic risk.
    """
    student_id: int = Field(..., description="Student identifier")
    student_name: str = Field(..., description="Student full name")
    risk_level: RiskLevel = Field(
        ...,
        description="Overall risk classification"
    )
    risk_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Numerical risk score (0-100)"
    )
    risk_factors: List[RiskFactor] = Field(
        default_factory=list,
        description="Identified risk factors"
    )
    suggested_interventions: List[str] = Field(
        default_factory=list,
        description="AI-suggested intervention strategies"
    )
    attendance_concerns: Optional[str] = Field(
        None,
        description="Summary of attendance-related concerns"
    )
    academic_concerns: Optional[str] = Field(
        None,
        description="Summary of academic performance concerns"
    )
    behavioral_observations: Optional[List[str]] = Field(
        default_factory=list,
        description="AI-observed behavioral patterns"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the analysis was performed"
    )
    confidence_score: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="AI confidence in this analysis"
    )


class BulkRiskAnalysisRequest(BaseModel):
    """Request for analyzing multiple students"""
    class_ids: Optional[List[int]] = Field(
        None,
        description="Filter by class IDs"
    )
    risk_threshold: Optional[RiskLevel] = Field(
        None,
        description="Only return students at or above this risk level"
    )
    include_details: bool = Field(
        default=True,
        description="Include full analysis details for each student"
    )


class BulkRiskAnalysisResult(BaseModel):
    """Bulk risk analysis response"""
    analyzed_count: int = Field(..., description="Total students analyzed")
    high_risk_count: int = Field(..., description="Students with HIGH or CRITICAL risk")
    results: List[RiskAnalysisResult] = Field(
        ..., 
        description="Individual analysis results"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== Academic Forecasting Schemas ====================

class TrendDirection(str, Literal):
    """Academic trend direction"""
    UP = "UP"
    DOWN = "DOWN"
    STABLE = "STABLE"


class SubjectForecast(BaseModel):
    """Forecast for a specific subject"""
    subject_id: int
    subject_name: str = Field(..., description="Subject name")
    current_grade: Optional[float] = Field(
        None,
        description="Current grade percentage"
    )
    predicted_grade: float = Field(
        ...,
        description="AI-predicted end-of-term grade"
    )
    predicted_letter_grade: Optional[str] = Field(
        None,
        description="Predicted letter grade (A, B, C, etc.)"
    )
    trend: TrendDirection = Field(
        ...,
        description="Predicted trend direction"
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence in this prediction"
    )
    key_factors: List[str] = Field(
        default_factory=list,
        description="Factors influencing this prediction"
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="AI suggestions for improvement"
    )


class AcademicForecastResult(BaseModel):
    """Complete academic forecast for a student"""
    student_id: int
    student_name: str
    academic_year_id: int
    term_id: int
    forecasts: List[SubjectForecast] = Field(
        ...,
        description="Subject-by-subject forecasts"
    )
    overall_trend: TrendDirection = Field(
        ...,
        description="Overall academic trend"
    )
    overall_predicted_gpa: Optional[float] = Field(
        None,
        description="Predicted GPA for the term"
    )
    at_risk_subjects: List[str] = Field(
        default_factory=list,
        description="Subjects predicted to fail or underperform"
    )
    analysis_summary: str = Field(
        ...,
        description="AI-generated summary of academic trajectory"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HistoricalTrendAnalysis(BaseModel):
    """Analysis of historical academic performance"""
    student_id: int
    period_start: datetime
    period_end: datetime
    grade_history: List[Dict[str, Any]] = Field(
        ...,
        description="Grade data points over time"
    )
    performance_patterns: List[str] = Field(
        ...,
        description="Identified performance patterns"
    )
    seasonal_factors: List[str] = Field(
        default_factory=list,
        description="Seasonal or temporal factors affecting performance"
    )
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Areas identified for improvement"
    )


# ==================== Intelligent Notification Schemas ====================

class RecipientType(str, Literal):
    """Notification recipient type"""
    PARENT = "PARENT"
    STUDENT = "STUDENT"
    STAFF = "STAFF"


class NotificationContextType(str, Literal):
    """Type of notification context"""
    ATTENDANCE_WARNING = "ATTENDANCE_WARNING"
    ATTENDANCE_CELEBRATION = "ATTENDANCE_CELEBRATION"
    GRADE_WARNING = "GRADE_WARNING"
    GRADE_CELEBRATION = "GRADE_CELEBRATION"
    BEHAVIOR_CONCERN = "BEHAVIOR_CONCERN"
    EVENT_REMINDER = "EVENT_REMINDER"
    FEE_REMINDER = "FEE_REMINDER"
    GENERAL_ANNOUNCEMENT = "GENERAL_ANNOUNCEMENT"
    CUSTOM = "CUSTOM"


class MessageGenerationRequest(BaseModel):
    """Request for AI-generated notification message"""
    recipient_type: RecipientType
    context_type: NotificationContextType
    student_id: Optional[int] = Field(
        None,
        description="Student ID for context (if applicable)"
    )
    student_name: Optional[str] = Field(
        None,
        description="Student name for personalization"
    )
    key_data: Dict[str, Any] = Field(
        ...,
        description="Context-specific data (grades, absences, dates, etc.)"
    )
    custom_instructions: Optional[str] = Field(
        None,
        description="Additional instructions for message tone/content"
    )
    language: str = Field(
        default="en",
        description="Message language code"
    )
    max_length: int = Field(
        default=160,
        ge=10,
        le=500,
        description="Maximum message length (SMS limit)"
    )


class GeneratedMessage(BaseModel):
    """AI-generated notification message"""
    content: str = Field(
        ...,
        description="Generated message content"
    )
    tone: str = Field(
        ...,
        description="Message tone (formal, friendly, urgent, etc.)"
    )
    language: str = Field(..., description="Message language")
    placeholders_used: List[str] = Field(
        default_factory=list,
        description="Dynamic placeholders that were filled"
    )
    character_count: int = Field(..., description="Message character count")
    sms_segments: int = Field(
        default=1,
        description="Number of SMS segments needed"
    )
    confidence_score: float = Field(
        default=0.8,
        ge=0,
        le=1,
        description="AI confidence in message quality"
    )
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative message versions"
    )


class BulkMessageRequest(BaseModel):
    """Request to generate messages for multiple recipients"""
    base_request: MessageGenerationRequest
    recipient_ids: List[int] = Field(
        ...,
        description="List of student/parent IDs to generate messages for"
    )
    combine_recipients: bool = Field(
        default=False,
        description="Combine all recipients into single message (announcements)"
    )


# ==================== AI Health and Status Schemas ====================

class AIHealthStatus(BaseModel):
    """AI service health check response"""
    status: Literal["healthy", "degraded", "unhealthy"]
    provider: str
    model: str
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    last_health_check: datetime


class ModelInfo(BaseModel):
    """Information about the loaded AI model"""
    name: str
    size: Optional[str] = None
    format: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)


# ==================== Analysis Configuration Schemas ====================

class AnalysisConfig(BaseModel):
    """Configuration for AI analysis parameters"""
    risk_threshold: float = Field(
        default=70.0,
        ge=0,
        le=100,
        description="Score threshold for HIGH risk classification"
    )
    critical_threshold: float = Field(
        default=85.0,
        ge=0,
        le=100,
        description="Score threshold for CRITICAL risk classification"
    )
    min_attendance_rate: float = Field(
        default=75.0,
        ge=0,
        le=100,
        description="Minimum acceptable attendance percentage"
    )
    min_grade_point: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Minimum acceptable grade point"
    )
    analysis_days_lookback: int = Field(
        default=30,
        ge=1,
        description="Number of days to look back for analysis"
    )
    auto_analyze_on_update: bool = Field(
        default=True,
        description="Automatically analyze when student data changes"
    )
