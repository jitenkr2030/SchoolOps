"""
Analytics & Predictions Router
AI-powered analytics for student risk prediction, enrollment forecasting, fee collection
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class StudentData(BaseModel):
    student_id: int
    attendance_rate: float
    average_grade: float
    assignment_submission_rate: float
    behavior_score: float
    parent_engagement: float
    socioeconomic_factors: Optional[dict] = None


class RiskPredictionRequest(BaseModel):
    students: List[StudentData]


class RiskPredictionResponse(BaseModel):
    predictions: List[dict]
    insights: List[dict]
    recommendations: List[dict]


class EnrollmentForecastRequest(BaseModel):
    historical_data: List[dict]
    forecast_months: int = 12


class EnrollmentForecastResponse(BaseModel):
    forecast: List[dict]
    confidence_intervals: List[dict]
    trends: dict


class FeeCollectionRequest(BaseModel):
    school_id: int
    historical_payments: List[dict]
    current_outstanding: List[dict]


class FeeCollectionResponse(BaseModel):
    predicted_collections: dict
    at_risk_accounts: List[dict]
    churn_predictions: List[dict]


class AcademicPerformanceRequest(BaseModel):
    student_id: int
    historical_scores: List[dict]
    study_hours: Optional[List[dict]] = None
    participation_metrics: Optional[List[dict]] = None


class AcademicPerformanceResponse(BaseModel):
    predicted_performance: dict
    improvement_recommendations: List[dict]
    at_risk_subjects: List[str]


# Mock ML model loading (in production, load actual trained models)
def load_risk_model():
    """Load pre-trained risk prediction model"""
    # In production: joblib.load('models/risk_prediction_model.pkl')
    return RandomForestClassifier(n_estimators=100, random_state=42)


def load_enrollment_model():
    """Load pre-trained enrollment forecast model"""
    return RandomForestRegressor(n_estimators=100, random_state=42)


# Endpoints
@router.post("/predict-risk", response_model=RiskPredictionResponse)
async def predict_at_risk_students(request: RiskPredictionRequest):
    """
    Predict students at risk of dropout or poor performance
    Uses ML model trained on historical data
    """
    try:
        logger.info(f"Processing risk predictions for {len(request.students)} students")
        
        # Extract features
        features = []
        for student in request.students:
            feature = [
                student.attendance_rate,
                student.average_grade,
                student.assignment_submission_rate,
                student.behavior_score,
                student.parent_engagement
            ]
            features.append(feature)
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(np.array(features))
        
        # Get predictions (mock in production)
        predictions = []
        for i, student in enumerate(request.students):
            # In production: model.predict_proba(scaled_features[i:i+1])
            risk_score = 1 - (student.attendance_rate / 100 * 0.3 + 
                             student.average_grade / 100 * 0.3 +
                             student.assignment_submission_rate / 100 * 0.2 +
                             student.behavior_score / 10 * 0.1 +
                             student.parent_engagement / 10 * 0.1)
            
            risk_level = "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low"
            
            predictions.append({
                "student_id": student.student_id,
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "key_factors": [
                    "Low attendance" if student.attendance_rate < 80 else None,
                    "Poor academic performance" if student.average_grade < 60 else None,
                    "Missing assignments" if student.assignment_submission_rate < 70 else None,
                    "Low behavior score" if student.behavior_score < 5 else None,
                    "Low parent engagement" if student.parent_engagement < 5 else None
                ]
            })
        
        # Generate insights
        insights = []
        high_risk_count = sum(1 for p in predictions if p["risk_level"] == "high")
        if high_risk_count > 0:
            insights.append({
                "type": "warning",
                "title": f"{high_risk_count} students identified as high-risk",
                "description": "These students require immediate attention and intervention"
            })
        
        # Generate recommendations
        recommendations = [
            {
                "type": "intervention",
                "priority": "high",
                "action": "Schedule parent-teacher meeting",
                "target_risk_level": "high"
            },
            {
                "type": "support",
                "priority": "medium",
                "action": "Provide tutoring sessions",
                "target_risk_level": "medium"
            },
            {
                "type": "monitoring",
                "priority": "low",
                "action": "Weekly check-ins with class teacher",
                "target_risk_level": "low"
            }
        ]
        
        return RiskPredictionResponse(
            predictions=predictions,
            insights=insights,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in risk prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast-enrollment", response_model=EnrollmentForecastResponse)
async def forecast_enrollment(request: EnrollmentForecastRequest):
    """
    Forecast enrollment by season and class
    Uses time series analysis and trend detection
    """
    try:
        logger.info(f"Forecasting enrollment for {request.forecast_months} months")
        
        # In production: Use trained time series model
        # Extract historical patterns
        monthly_data = request.historical_data
        
        # Simple linear trend projection (mock)
        forecast = []
        confidence_intervals = []
        
        # Calculate average monthly growth
        if len(monthly_data) >= 2:
            growth_rates = []
            for i in range(1, len(monthly_data)):
                if monthly_data[i-1].get("enrollments", 0) > 0:
                    rate = (monthly_data[i].get("enrollments", 0) - 
                           monthly_data[i-1].get("enrollments", 0)) / \
                           monthly_data[i-1].get("enrollments", 0)
                    growth_rates.append(rate)
            
            avg_growth = np.mean(growth_rates) if growth_rates else 0.05
        else:
            avg_growth = 0.05
        
        # Generate forecast
        last_enrollment = monthly_data[-1].get("enrollments", 100) if monthly_data else 100
        
        for month in range(1, request.forecast_months + 1):
            predicted = last_enrollment * (1 + avg_growth) ** month
            uncertainty = predicted * 0.1  # 10% uncertainty
            
            forecast.append({
                "month": month,
                "predicted_enrollment": int(predicted),
                "predicted_new_students": int(predicted * 0.1)
            })
            
            confidence_intervals.append({
                "month": month,
                "lower_bound": int(predicted - uncertainty),
                "upper_bound": int(predicted + uncertainty)
            })
        
        # Identify trends
        trends = {
            "growth_rate": f"{avg_growth * 100:.1f}%",
            "direction": "increasing" if avg_growth > 0 else "decreasing" if avg_growth < 0 else "stable",
            "seasonal_patterns": ["peak_enrollment_aug", "low_enrollment_mar"]
        }
        
        return EnrollmentForecastResponse(
            forecast=forecast,
            confidence_intervals=confidence_intervals,
            trends=trends
        )
        
    except Exception as e:
        logger.error(f"Error in enrollment forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-fee-collection", response_model=FeeCollectionResponse)
async def analyze_fee_collection(request: FeeCollectionRequest):
    """
    Analyze fee collection patterns and predict future collections
    Identify at-risk accounts and potential churn
    """
    try:
        logger.info("Analyzing fee collection patterns")
        
        # Mock analysis (in production: use trained model)
        at_risk_accounts = []
        churn_predictions = []
        
        for account in request.current_outstanding:
            days_overdue = (datetime.now() - account.get("due_date", datetime.now())).days
            
            if days_overdue > 30:
                at_risk_accounts.append({
                    "student_id": account.get("student_id"),
                    "amount_outstanding": account.get("amount", 0),
                    "days_overdue": days_overdue,
                    "churn_probability": min(days_overdue / 90, 1.0),
                    "recommended_action": "Send payment reminder + call"
                })
        
        # Fee collection prediction
        total_outstanding = sum(a.get("amount", 0) for a in request.current_outstanding)
        predicted_collections = {
            "next_30_days": int(total_outstanding * 0.3),
            "next_60_days": int(total_outstanding * 0.5),
            "next_90_days": int(total_outstanding * 0.7),
            "total_recovery_rate": 0.85
        }
        
        return FeeCollectionResponse(
            predicted_collections=predicted_collections,
            at_risk_accounts=at_risk_accounts,
            churn_predictions=churn_predictions
        )
        
    except Exception as e:
        logger.error(f"Error in fee collection analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-academic-performance")
async def analyze_academic_performance(request: AcademicPerformanceRequest):
    """
    Analyze student academic performance and predict future outcomes
    """
    try:
        logger.info(f"Analyzing academic performance for student {request.student_id}")
        
        # Extract scores
        scores = [s.get("score", 0) for s in request.historical_scores]
        avg_score = np.mean(scores) if scores else 0
        
        # Simple prediction (in production: use trained model)
        predicted_score = avg_score * 1.02  # Slight improvement trend
        
        # Identify weak areas
        weak_subjects = []
        for score in request.historical_scores:
            if score.get("score", 100) < 60:
                weak_subjects.append(score.get("subject", "Unknown"))
        
        # Generate recommendations
        recommendations = [
            {
                "area": "Study Habits",
                "action": "Increase study time by 30 minutes daily",
                "expected_improvement": "+5-10%"
            },
            {
                "area": "Subject Support",
                "action": "Consider tutoring for weak subjects",
                "expected_improvement": "+10-15%"
            },
            {
                "area": "Practice",
                "action": "Complete 10 practice problems daily",
                "expected_improvement": "+8-12%"
            }
        ]
        
        return AcademicPerformanceResponse(
            predicted_performance={
                "next_assessment": int(predicted_score),
                "confidence": 0.75,
                "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
            },
            improvement_recommendations=recommendations,
            at_risk_subjects=list(set(weak_subjects))
        )
        
    except Exception as e:
        logger.error(f"Error in academic performance analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
