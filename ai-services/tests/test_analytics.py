"""
Unit tests for AI Analytics and Prediction Services
"""
import pytest
from app.routers.analytics import (
    predict_student_risk,
    forecast_enrollment,
    predict_fee_churn,
    analyze_attendance_trends,
    predict_exam_performance
)


class TestRiskPrediction:
    """Tests for Student Risk Prediction."""
    
    def test_predict_student_risk_success(self, sample_student_data, mock_ml_model):
        """Test successful risk prediction."""
        result = predict_student_risk(sample_student_data)
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "recommendations" in result
        assert "confidence" in result
        assert 0.0 <= result["risk_score"] <= 1.0
    
    def test_risk_level_classification(self):
        """Test risk level classification."""
        risk_levels = [
            (0.8, "High Risk"),
            (0.6, "Medium Risk"),
            (0.4, "Low Risk"),
            (0.2, "Minimal Risk"),
        ]
        
        for score, expected_level in risk_levels:
            level = predict_student_risk.get_risk_level(score)
            assert level == expected_level
    
    def test_missing_data_handling(self):
        """Test handling of incomplete student data."""
        incomplete_data = {
            "student_id": "STU001",
            # Missing attendance and grades
        }
        
        result = predict_student_risk(incomplete_data)
        
        # Should still return a result with appropriate warnings
        assert "risk_score" in result
        assert "data_quality_warning" in result
    
    def test_recommendations_generation(self, sample_student_data):
        """Test recommendation generation based on risk."""
        result = predict_student_risk(sample_student_data)
        
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0


class TestEnrollmentForecasting:
    """Tests for Enrollment Forecasting."""
    
    def test_forecast_enrollment_success(self, sample_enrollment_data):
        """Test successful enrollment forecast."""
        result = forecast_enrollment(
            historical_data=sample_enrollment_data["historical_enrollment"],
            forecast_periods=6
        )
        
        assert "predictions" in result
        assert len(result["predictions"]) == 6
        assert "trend" in result
        assert "seasonal_factors" in result
    
    def test_seasonal_patterns(self, sample_enrollment_data):
        """Test seasonal pattern detection."""
        result = forecast_enrollment(
            historical_data=sample_enrollment_data["historical_enrollment"],
            forecast_periods=12
        )
        
        assert "seasonal_patterns" in result
        # Peak enrollment should be around April (index 3 in our data)
        assert result["peak_month"] in ["April", "March", "May"]
    
    def test_growth_trend_analysis(self, sample_enrollment_data):
        """Test growth trend analysis."""
        result = forecast_enrollment(
            historical_data=sample_enrollment_data["historical_enrollment"],
            forecast_periods=1
        )
        
        assert "growth_rate" in result
        assert isinstance(result["growth_rate"], (int, float))
        assert result["growth_rate"] > 0  # Based on our sample data
    
    def test_forecast_confidence(self, sample_enrollment_data):
        """Test forecast confidence intervals."""
        result = forecast_enrollment(
            historical_data=sample_enrollment_data["historical_enrollment"],
            forecast_periods=3
        )
        
        assert "confidence_intervals" in result
        assert len(result["confidence_intervals"]) == 3
        for interval in result["confidence_intervals"]:
            assert "lower_bound" in interval
            assert "upper_bound" in interval


class TestFeeChurnPrediction:
    """Tests for Fee Churn Prediction."""
    
    def test_predict_fee_churn_success(self, sample_fee_data):
        """Test successful fee churn prediction."""
        result = predict_fee_churn(sample_fee_data)
        
        assert "churn_probability" in result
        assert "risk_factors" in result
        assert "intervention_suggestions" in result
        assert 0.0 <= result["churn_probability"] <= 1.0
    
    def test_churn_indicators(self, sample_fee_data):
        """Test churn indicator detection."""
        result = predict_fee_churn(sample_fee_data)
        
        assert "indicators" in result
        # Should detect overdue payments as churn indicator
        indicators = result["indicators"]
        assert any("overdue" in str(i).lower() for i in indicators)
    
    def test_intervention_suggestions(self, sample_fee_data):
        """Test intervention suggestion generation."""
        result = predict_fee_churn(sample_fee_data)
        
        assert "intervention_suggestions" in result
        assert isinstance(result["intervention_suggestions"], list)


class TestAttendanceTrendAnalysis:
    """Tests for Attendance Trend Analysis."""
    
    def test_analyze_attendance_trends(self, sample_student_data):
        """Test attendance trend analysis."""
        result = analyze_attendance_trends(sample_student_data["attendance_history"])
        
        assert "trend" in result
        assert "average_attendance" in result
        assert "pattern" in result
        assert "predictions" in result
    
    def test_pattern_detection(self, sample_student_data):
        """Test attendance pattern detection."""
        result = analyze_attendance_trends(sample_student_data["attendance_history"])
        
        # Should detect Monday/Friday patterns if present
        assert "pattern_analysis" in result
    
    def test_weekly_comparison(self, sample_student_data):
        """Test weekly attendance comparison."""
        result = analyze_attendance_trends(sample_student_data["attendance_history"])
        
        assert "weekly_comparison" in result
        assert "improvement" in result or "decline" in result


class TestExamPerformancePrediction:
    """Tests for Exam Performance Prediction."""
    
    def test_predict_exam_performance(self, sample_student_data):
        """Test exam performance prediction."""
        result = predict_exam_performance(
            student_id=sample_student_data["student_id"],
            historical_data=sample_student_data["grade_history"],
            upcoming_exam="Mathematics - Unit Test"
        )
        
        assert "predicted_score" in result
        assert "confidence_interval" in result
        assert "subject_analysis" in result
        assert "recommendations" in result
    
    def test_subject_specific_analysis(self, sample_student_data):
        """Test subject-specific performance analysis."""
        result = predict_exam_performance(
            student_id=sample_student_data["student_id"],
            historical_data=sample_student_data["grade_history"],
            upcoming_exam="Mathematics - Unit Test"
        )
        
        # Should provide analysis for Mathematics
        assert "Mathematics" in result["subject_analysis"]
    
    def test_recommendations_for_improvement(self, sample_student_data):
        """Test recommendations for performance improvement."""
        result = predict_exam_performance(
            student_id=sample_student_data["student_id"],
            historical_data=sample_student_data["grade_history"],
            upcoming_exam="Mathematics - Unit Test"
        )
        
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
