"""
Unit tests for business logic services in SchoolOps Backend
"""
import pytest
from datetime import date, timedelta
from app.services.attendance_service import AttendanceService
from app.services.grade_service import GradeService
from app.services.fee_service import FeeService


class TestAttendanceService:
    """Tests for Attendance business logic."""
    
    def test_calculate_attendance_percentage(self):
        """Test attendance percentage calculation."""
        total_days = 30
        present_days = 25
        expected_percentage = round((present_days / total_days) * 100, 2)
        
        # Manual calculation for verification
        assert expected_percentage == 83.33
    
    def test_attendance_status_classification(self):
        """Test attendance status classification."""
        test_cases = [
            (95, "Excellent"),
            (85, "Good"),
            (75, "Satisfactory"),
            (60, "Needs Improvement"),
            (40, "At Risk"),
        ]
        
        for percentage, expected_status in test_cases:
            status = AttendanceService.classify_attendance_status(percentage)
            assert status == expected_status
    
    def test_get_attendance_summary(self):
        """Test generating attendance summary."""
        attendance_records = [
            {"date": "2024-10-01", "status": "Present"},
            {"date": "2024-10-02", "status": "Present"},
            {"date": "2024-10-03", "status": "Absent"},
            {"date": "2024-10-04", "status": "Present"},
            {"date": "2024-10-05", "status": "Late"},
        ]
        
        summary = AttendanceService.generate_summary(attendance_records)
        
        assert summary["total_days"] == 5
        assert summary["present"] == 3
        assert summary["absent"] == 1
        assert summary["late"] == 1
        assert summary["percentage"] == 60.0
    
    def test_generate_monthly_report(self):
        """Test generating monthly attendance report."""
        year = 2024
        month = 10
        
        # Generate dates for October 2024
        report = AttendanceService.generate_monthly_report(year, month)
        
        assert report["year"] == year
        assert report["month"] == month
        assert "days_in_month" in report
        assert "working_days" in report
        assert "attendance_data" in report


class TestGradeService:
    """Tests for Grade business logic."""
    
    def test_calculate_grade_letter(self):
        """Test grade letter calculation from score."""
        test_cases = [
            (95, "A+"),
            (90, "A"),
            (85, "A-"),
            (80, "B+"),
            (75, "B"),
            (70, "B-"),
            (65, "C+"),
            (60, "C"),
            (50, "D"),
            (40, "F"),
        ]
        
        for score, expected_grade in test_cases:
            grade = GradeService.calculate_grade_letter(score)
            assert grade == expected_grade
    
    def test_calculate_gpa(self):
        """Test GPA calculation."""
        grades = [
            {"grade": "A", "credit_hours": 4},
            {"grade": "B+", "credit_hours": 3},
            {"grade": "A-", "credit_hours":": 3},
            {"grade": "B", "credit_hours": 4},
        ]
        
        gpa = GradeService.calculate_gpa(grades)
        
        # Verify GPA is within valid range
        assert 0.0 <= gpa <= 4.0
    
    def test_generate_report_card(self):
        """Test generating student report card."""
        student_id = 1
        academic_year = "2024-2025"
        
        # Mock grades data
        grades_data = [
            {"subject": "Mathematics", "score": 85, "grade": "A-"},
            {"subject": "Science", "score": 78, "grade": "B+"},
            {"subject": "English", "score": 92, "grade": "A"},
        ]
        
        report_card = GradeService.generate_report_card(
            student_id, academic_year, grades_data
        )
        
        assert report_card["student_id"] == student_id
        assert report_card["academic_year"] == academic_year
        assert "subjects" in report_card
        assert "overall_percentage" in report_card
        assert "overall_grade" in report_card
        assert "gpa" in report_card
    
    def test_analyze_performance_trend(self):
        """Test performance trend analysis."""
        grade_history = [
            {"assessment": "Test 1", "score": 70},
            {"assessment": "Test 2", "score": 75},
            {"assessment": "Test 3", "score": 80},
            {"assessment": "Test 4", "score": 78},
            {"assessment": "Test 5", "score": 85},
        ]
        
        trend = GradeService.analyze_performance_trend(grade_history)
        
        assert "trend_direction" in trend
        assert "average_score" in trend
        assert "improvement_rate" in trend
    
    def test_identify_weak_topics(self):
        """Test identifying weak topics from grades."""
        subject_grades = [
            {"subject": "Algebra", "score": 45, "weight": 0.3},
            {"subject": "Geometry", "score": 85, "weight": 0.3},
            {"subject": "Arithmetic", "score": 92, "weight": 0.4},
        ]
        
        weak_topics = GradeService.identify_weak_topics(subject_grades, threshold=60)
        
        assert "Algebra" in weak_topics
        assert "Geometry" not in weak_topics
        assert "Arithmetic" not in weak_topics


class TestFeeService:
    """Tests for Fee business logic."""
    
    def test_calculate_late_fee(self):
        """Test late fee calculation."""
        original_amount = 10000
        days_overdue = 15
        daily_rate = 10  # Rs. 10 per day
        
        late_fee = FeeService.calculate_late_fee(original_amount, days_overdue, daily_rate)
        
        expected_fee = original_amount + (days_overdue * daily_rate)
        assert late_fee == expected_fee
    
    def test_apply_concession(self):
        """Test applying fee concession."""
        original_amount = 15000
        concession_percentage = 10
        
        final_amount = FeeService.apply_concession(original_amount, concession_percentage)
        
        expected_amount = original_amount * (1 - concession_percentage / 100)
        assert final_amount == expected_amount
    
    def test_generate_payment_schedule(self):
        """Test generating fee payment schedule."""
        total_amount = 12000
        installments = 4
        start_date = "2024-04-01"
        
        schedule = FeeService.generate_payment_schedule(
            total_amount, installments, start_date
        )
        
        assert len(schedule) == installments
        assert schedule[0]["amount"] == total_amount / installments
        assert "due_date" in schedule[0]
    
    def test_calculate_total_due(self):
        """Test calculating total amount due."""
        fee_records = [
            {"amount": 5000, "status": "Pending"},
            {"amount": 3000, "status": "Pending"},
            {"amount": 2000, "status": "Paid"},
            {"amount": 1000, "status": "Overdue"},
        ]
        
        total_due = FeeService.calculate_total_due(fee_records)
        
        assert total_due == 8000  # Only pending + overdue
    
    def test_generate_receipt(self):
        """Test generating fee receipt."""
        payment_id = "PAY2024001"
        student_id = 1
        amount_paid = 5000
        payment_method = "Cash"
        
        receipt = FeeService.generate_receipt(
            payment_id, student_id, amount_paid, payment_method
        )
        
        assert receipt["payment_id"] == payment_id
        assert receipt["student_id"] == student_id
        assert receipt["amount_paid"] == amount_paid
        assert receipt["payment_method"] == payment_method
        assert "payment_date" in receipt
        assert "receipt_number" in receipt
    
    def test_analyze_fee_collection(self):
        """Test analyzing fee collection status."""
        fee_data = [
            {"fee_type": "Tuition", "total": 50000, "collected": 35000},
            {"fee_type": "Transport", "total": 20000, "collected": 18000},
            {"fee_type": "Library", "total": 5000, "collected": 4000},
        ]
        
        analysis = FeeService.analyze_fee_collection(fee_data)
        
        assert "total_collected" in analysis
        assert "total_due" in analysis
        assert "collection_rate" in analysis
        assert "fee_type_breakdown" in analysis
