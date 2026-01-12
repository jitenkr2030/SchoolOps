"""
Risk Detection Service
AI-powered student at-risk detection and analysis
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.provider import AIProvider, get_ai_service
from app.schema.ai_schema import (
    RiskLevel,
    RiskFactor,
    RiskAnalysisResult,
    BulkRiskAnalysisRequest,
    BulkRiskAnalysisResult,
)
from app.db.models import Student, Attendance, Grade, AcademicYear, Term

logger = logging.getLogger(__name__)


class RiskDetectionService:
    """
    Service for detecting and analyzing at-risk students
    
    Uses AI to analyze attendance patterns, academic performance,
    and behavioral indicators to identify students who may need
    additional support.
    """
    
    def __init__(self, db: AsyncSession, ai_provider: Optional[AIProvider] = None):
        self.db = db
        self.ai = ai_provider or None
    
    async def _get_ai(self) -> AIProvider:
        """Get AI provider lazily"""
        if self.ai is None:
            self.ai = await get_ai_service()
        return self.ai
    
    async def analyze_student(
        self, 
        student_id: int,
        include_details: bool = True
    ) -> Optional[RiskAnalysisResult]:
        """
        Perform comprehensive risk analysis for a single student
        
        Args:
            student_id: Student to analyze
            include_details: Include full analysis details
            
        Returns:
            RiskAnalysisResult with risk assessment
        """
        # Fetch student data
        student = await self._get_student_data(student_id)
        if not student:
            return None
        
        # Gather analysis context
        context = await self._gather_student_context(student_id)
        
        # Generate AI analysis
        ai = await self._get_ai()
        
        prompt = self._build_risk_analysis_prompt(student, context)
        
        response = await ai.analyze_json(
            prompt=prompt,
            context_data=context,
            response_schema=RiskAnalysisResult
        )
        
        if not response.success:
            logger.error(f"Risk analysis failed for student {student_id}: {response.error_message}")
            # Return a basic analysis without AI insights
            return self._create_basic_analysis(student, context)
        
        # Parse and return result
        import json
        try:
            result_data = json.loads(response.content)
            result = RiskAnalysisResult(**result_data)
            result.student_id = student_id
            result.student_name = f"{student.first_name} {student.last_name}"
            return result
        except Exception as e:
            logger.error(f"Failed to parse risk analysis result: {e}")
            return self._create_basic_analysis(student, context)
    
    async def analyze_bulk(
        self, 
        request: BulkRiskAnalysisRequest
    ) -> BulkRiskAnalysisResult:
        """
        Perform risk analysis for multiple students
        
        Args:
            request: Bulk analysis configuration
            
        Returns:
            BulkRiskAnalysisResult with all student analyses
        """
        # Build query for students
        query = select(Student.id, Student.first_name, Student.last_name)
        
        if request.class_ids:
            # Filter by classes if specified
            query = query.where(Student.current_class_id.in_(request.class_ids))
        
        # Exclude inactive students
        query = query.where(Student.is_active == True)
        
        result = await self.db.execute(query)
        students = result.all()
        
        analyses = []
        high_risk_count = 0
        
        for student_id, first_name, last_name in students:
            analysis = await self.analyze_student(
                student_id=student_id,
                include_details=request.include_details
            )
            
            if analysis:
                if request.risk_threshold:
                    if self._risk_level_to_score(analysis.risk_level) >= \
                       self._risk_level_to_score(request.risk_threshold):
                        analyses.append(analysis)
                else:
                    analyses.append(analysis)
                
                if analysis.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_risk_count += 1
        
        return BulkRiskAnalysisResult(
            analyzed_count=len(students),
            high_risk_count=high_risk_count,
            results=analyses
        )
    
    async def _get_student_data(self, student_id: int) -> Optional[Student]:
        """Fetch student record"""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def _gather_student_context(self, student_id: int) -> Dict[str, Any]:
        """
        Gather all relevant data for risk analysis
        
        Returns a comprehensive context dictionary for AI analysis.
        """
        # Get current academic year and term
        current_date = datetime.utcnow()
        
        year_result = await self.db.execute(
            select(AcademicYear)
            .where(and_(
                AcademicYear.start_date <= current_date,
                AcademicYear.end_date >= current_date
            ))
        )
        current_year = year_result.scalar_one_or_none()
        
        term_id = None
        if current_year:
            term_result = await self.db.execute(
                select(Term.id)
                .where(and_(
                    Term.academic_year_id == current_year.id,
                    Term.start_date <= current_date,
                    Term.end_date >= current_date
                ))
            )
            term_row = term_result.first()
            if term_row:
                term_id = term_row[0]
        
        # Attendance statistics (last 30 days)
        attendance_stats = await self._get_attendance_stats(student_id)
        
        # Grade performance
        grade_data = await self._get_grade_data(student_id, term_id)
        
        # Recent behavior incidents (placeholder)
        behavior_data = await self._get_behavior_data(student_id)
        
        return {
            "student_id": student_id,
            "analysis_date": current_date.isoformat(),
            "academic_context": {
                "current_year_id": current_year.id if current_year else None,
                "current_term_id": term_id
            },
            "attendance": attendance_stats,
            "academic_performance": grade_data,
            "behavior": behavior_data,
            "metadata": {
                "days_lookback": 30,
                "analysis_version": "1.0"
            }
        }
    
    async def _get_attendance_stats(
        self, 
        student_id: int
    ) -> Dict[str, Any]:
        """Calculate attendance statistics"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Total attendance records in period
        result = await self.db.execute(
            select(
                func.count(Attendance.id).label("total"),
                func.sum(
                    func.cast(Attendance.is_present == True, int)
                ).label("present")
            )
            .where(and_(
                Attendance.student_id == student_id,
                Attendance.date >= thirty_days_ago
            ))
        )
        row = result.first()
        
        total = row.total or 0
        present = row.present or 0
        attendance_rate = (present / total * 100) if total > 0 else 100
        
        # Get recent absence dates
        absence_result = await self.db.execute(
            select(Attendance.date, Attendance.reason)
            .where(and_(
                Attendance.student_id == student_id,
                Attendance.is_present == False,
                Attendance.date >= thirty_days_ago
            ))
            .order_by(Attendance.date.desc())
            .limit(10)
        )
        absences = [
            {"date": d.isoformat(), "reason": r}
            for d, r in absence_result.all()
        ]
        
        return {
            "total_sessions": total,
            "present": present,
            "absent": total - present,
            "attendance_rate": round(attendance_rate, 2),
            "recent_absences": absences,
            "consecutive_absences": self._count_consecutive_absences(absences)
        }
    
    def _count_consecutive_absences(self, absences: List[Dict]) -> int:
        """Count consecutive absences from recent dates"""
        if not absences:
            return 0
        
        consecutive = 0
        today = datetime.utcnow().date()
        
        for absence in absences:
            absence_date = datetime.fromisoformat(absence["date"]).date()
            days_diff = (today - absence_date).days
            
            if days_diff <= consecutive + 1:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    async def _get_grade_data(
        self, 
        student_id: int,
        term_id: Optional[int]
    ) -> Dict[str, Any]:
        """Get academic performance data"""
        query = select(Grade).where(Grade.student_id == student_id)
        
        if term_id:
            query = query.where(Grade.term_id == term_id)
        
        result = await self.db.execute(query)
        grades = result.scalars().all()
        
        if not grades:
            return {"has_grades": False}
        
        grade_list = []
        for grade in grades:
            grade_list.append({
                "subject": grade.subject_id,  # Would resolve to subject name
                "score": grade.score,
                "max_score": grade.max_score,
                "percentage": (grade.score / grade.max_score * 100) if grade.max_score > 0 else 0,
                "date": grade.date.isoformat() if grade.date else None,
                "type": grade.grade_type
            })
        
        # Calculate averages
        percentages = [g["percentage"] for g in grade_list]
        avg_percentage = sum(percentages) / len(percentages) if percentages else 0
        
        # Identify struggling subjects
        struggling = [
            g["subject"] for g in grade_list 
            if g["percentage"] < 50
        ]
        
        # Calculate trend (compare recent to earlier grades)
        sorted_grades = sorted(grade_list, key=lambda x: x["date"] or "")
        if len(sorted_grades) >= 4:
            early_avg = sum(g["percentage"] for g in sorted_grades[:2]) / 2
            recent_avg = sum(g["percentage"] for g in sorted_grades[-2:]) / 2
            trend = "IMPROVING" if recent_avg > early_avg else "DECLINING"
        else:
            trend = "STABLE"
        
        return {
            "has_grades": True,
            "total_assessments": len(grades),
            "average_percentage": round(avg_percentage, 2),
            "grade_list": grade_list,
            "struggling_subjects": struggling,
            "performance_trend": trend
        }
    
    async def _get_behavior_data(self, student_id: int) -> Dict[str, Any]:
        """Get behavior-related data (placeholder for incident records)"""
        # This would integrate with a behavior/incidents module
        return {
            "recent_incidents": [],
            "positive_recognitions": [],
            "overall_conduct": "GOOD"
        }
    
    def _build_risk_analysis_prompt(
        self,
        student: Student,
        context: Dict[str, Any]
    ) -> str:
        """Build the AI prompt for risk analysis"""
        return f"""Analyze the following student data and determine their academic risk level.

## STUDENT INFORMATION:
- Name: {student.first_name} {student.last_name}
- Student ID: {student.id}
- Current Class: {student.current_class_id}

## TASK:
Evaluate the student for academic risk based on the provided data. Consider:
1. Attendance rate and patterns
2. Academic performance and trends
3. Any behavioral concerns

Classify the risk as one of: CRITICAL, HIGH, MODERATE, or LOW

Provide:
- Risk level (one word)
- Risk score (0-100)
- Top 3 risk factors
- 3-5 suggested interventions

Output the analysis with your reasoning for the risk classification."""
    
    def _create_basic_analysis(
        self,
        student: Student,
        context: Dict[str, Any]
    ) -> RiskAnalysisResult:
        """Create a basic analysis without AI when AI is unavailable"""
        attendance = context.get("attendance", {})
        academics = context.get("academic_performance", {})
        
        # Calculate basic risk score
        risk_score = 0
        
        attendance_rate = attendance.get("attendance_rate", 100)
        if attendance_rate < 75:
            risk_score += 40
        elif attendance_rate < 85:
            risk_score += 25
        elif attendance_rate < 90:
            risk_score += 10
        
        avg_grade = academics.get("average_percentage", 100)
        if avg_grade < 50:
            risk_score += 40
        elif avg_grade < 60:
            risk_score += 25
        elif avg_grade < 70:
            risk_score += 10
        
        consecutive = attendance.get("consecutive_absences", 0)
        if consecutive >= 3:
            risk_score += 20
        elif consecutive >= 2:
            risk_score += 10
        
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_level := RiskLevel.HIGH if risk_score >= 60 else \
             RiskLevel.MODERATE if risk_score >= 40 else RiskLevel.LOW:
            pass
        
        risk_factors = []
        if attendance_rate < 85:
            risk_factors.append(RiskFactor(
                factor=f"Attendance rate of {attendance_rate}% is below target",
                weight=0.4,
                trend=RiskLevel.MODERATE
            ))
        if avg_grade < 70:
            risk_factors.append(RiskFactor(
                factor=f"Average grade of {avg_grade}% needs improvement",
                weight=0.4,
                trend=RiskLevel.MODERATE
            ))
        
        return RiskAnalysisResult(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            suggested_interventions=[
                "Schedule parent-teacher meeting",
                "Review and strengthen study habits",
                "Monitor attendance closely"
            ],
            analysis_timestamp=datetime.utcnow()
        )
    
    def _risk_level_to_score(self, level: RiskLevel) -> int:
        """Convert risk level to numeric score"""
        scores = {
            RiskLevel.CRITICAL: 80,
            RiskLevel.HIGH: 60,
            RiskLevel.MODERATE: 40,
            RiskLevel.LOW: 20
        }
        return scores.get(level, 0)
