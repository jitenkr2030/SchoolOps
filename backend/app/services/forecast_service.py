"""
Academic Forecasting Service
AI-powered academic performance prediction and analysis
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.provider import AIProvider, get_ai_service
from app.schema.ai_schema import (
    TrendDirection,
    SubjectForecast,
    AcademicForecastResult,
    HistoricalTrendAnalysis,
)
from app.db.models import Student, Grade, AcademicYear, Term, Subject

logger = logging.getLogger(__name__)


class AcademicForecastService:
    """
    Service for predicting academic performance outcomes
    
    Uses AI to analyze historical performance patterns and predict
    end-of-term grades and overall academic trajectories.
    """
    
    def __init__(self, db: AsyncSession, ai_provider: Optional[AIProvider] = None):
        self.db = db
        self.ai = ai_provider or None
    
    async def _get_ai(self) -> AIProvider:
        """Get AI provider lazily"""
        if self.ai is None:
            self.ai = await get_ai_service()
        return self.ai
    
    async def forecast_student(
        self, 
        student_id: int,
        academic_year_id: Optional[int] = None,
        term_id: Optional[int] = None
    ) -> Optional[AcademicForecastResult]:
        """
        Generate academic forecast for a student
        
        Args:
            student_id: Student to forecast
            academic_year_id: Target academic year (current if not specified)
            term_id: Target term (current if not specified)
            
        Returns:
            AcademicForecastResult with predictions
        """
        # Get student data
        student = await self._get_student(student_id)
        if not student:
            return None
        
        # Get current academic period if not specified
        year_id, term_id = await self._get_current_period(year_id=academic_year_id, term_id=term_id)
        
        # Gather historical and current data
        context = await self._gather_forecast_context(
            student_id, year_id, term_id
        )
        
        # Generate AI forecast
        ai = await self._get_ai()
        
        prompt = self._build_forecast_prompt(student, context)
        
        # Use a wrapper schema for the AI response
        class ForecastWrapper(BaseModel):
            forecasts: List[Dict[str, Any]]
            overall_trend: str
            predicted_gpa: Optional[float]
            at_risk_subjects: List[str]
            summary: str
        
        response = await ai.analyze_json(
            prompt=prompt,
            context_data=context,
            response_schema=ForecastWrapper
        )
        
        if not response.success:
            logger.error(f"Forecast failed for student {student_id}: {response.error_message}")
            return self._create_basic_forecast(student, context)
        
        # Parse and return result
        import json
        try:
            result_data = json.loads(response.content)
            
            forecasts = []
            at_risk = []
            
            for f in result_data.get("forecasts", []):
                subject_id = f.get("subject_id")
                # Get subject name
                subject_result = await self.db.execute(
                    select(Subject.name).where(Subject.id == subject_id)
                )
                subject_name = subject_result.scalar_one_or_none() or f"Subject {subject_id}"
                
                forecast = SubjectForecast(
                    subject_id=subject_id,
                    subject_name=subject_name,
                    current_grade=f.get("current_grade"),
                    predicted_grade=f.get("predicted_grade", f.get("current_grade", 0)),
                    predicted_letter_grade=f.get("predicted_letter_grade"),
                    trend=TrendDirection(f.get("trend", "STABLE")),
                    confidence_score=f.get("confidence_score", 0.7),
                    key_factors=f.get("key_factors", []),
                    improvement_suggestions=f.get("improvement_suggestions", [])
                )
                forecasts.append(forecast)
                
                if forecast.predicted_grade < 50:
                    at_risk.append(forecast.subject_name)
            
            return AcademicForecastResult(
                student_id=student_id,
                student_name=f"{student.first_name} {student.last_name}",
                academic_year_id=year_id,
                term_id=term_id,
                forecasts=forecasts,
                overall_trend=TrendDirection(result_data.get("overall_trend", "STABLE")),
                overall_predicted_gpa=result_data.get("predicted_gpa"),
                at_risk_subjects=at_risk,
                analysis_summary=result_data.get("summary", "Analysis completed.")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse forecast result: {e}")
            return self._create_basic_forecast(student, context)
    
    async def analyze_historical_trends(
        self,
        student_id: int,
        days_lookback: int = 365
    ) -> Optional[HistoricalTrendAnalysis]:
        """
        Analyze historical performance trends for a student
        
        Args:
            student_id: Student to analyze
            days_lookback: Number of days to analyze
            
        Returns:
            HistoricalTrendAnalysis with patterns and insights
        """
        # Get all grades for the period
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_lookback)
        
        result = await self.db.execute(
            select(Grade)
            .where(and_(
                Grade.student_id == student_id,
                Grade.date >= cutoff_date
            ))
            .order_by(Grade.date)
        )
        grades = result.scalars().all()
        
        if not grades:
            return None
        
        # Build grade history
        grade_history = []
        for grade in grades:
            grade_history.append({
                "date": grade.date.isoformat(),
                "subject_id": grade.subject_id,
                "score": grade.score,
                "max_score": grade.max_score,
                "percentage": (grade.score / grade.max_score * 100) if grade.max_score > 0 else 0,
                "grade_type": grade.grade_type
            })
        
        # Analyze patterns
        patterns = await self._identify_performance_patterns(grade_history)
        
        return HistoricalTrendAnalysis(
            student_id=student_id,
            period_start=cutoff_date,
            period_end=datetime.utcnow(),
            grade_history=grade_history,
            performance_patterns=patterns["patterns"],
            seasonal_factors=patterns.get("seasonal", []),
            improvement_areas=patterns.get("improvement_areas", [])
        )
    
    async def _get_student(self, student_id: int) -> Optional[Student]:
        """Fetch student record"""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_current_period(
        self,
        year_id: Optional[int] = None,
        term_id: Optional[int] = None
    ) -> tuple[Optional[int], Optional[int]]:
        """Get current academic year and term IDs"""
        current_date = datetime.utcnow()
        
        if year_id is None:
            year_result = await self.db.execute(
                select(AcademicYear.id)
                .where(and_(
                    AcademicYear.start_date <= current_date,
                    AcademicYear.end_date >= current_date
                ))
            )
            year_row = year_result.first()
            year_id = year_row[0] if year_row else None
        
        if term_id is None and year_id:
            term_result = await self.db.execute(
                select(Term.id)
                .where(and_(
                    Term.academic_year_id == year_id,
                    Term.start_date <= current_date,
                    Term.end_date >= current_date
                ))
            )
            term_row = term_result.first()
            term_id = term_row[0] if term_row else None
        
        return year_id, term_id
    
    async def _gather_forecast_context(
        self,
        student_id: int,
        academic_year_id: Optional[int],
        term_id: Optional[int]
    ) -> Dict[str, Any]:
        """Gather all data needed for forecasting"""
        
        # Current term grades
        current_grades = await self._get_grades_for_period(
            student_id, academic_year_id, term_id
        )
        
        # Historical grades for trend analysis
        historical_grades = await self._get_historical_grades(
            student_id, academic_year_id
        )
        
        # Subject information
        subjects = await self._get_student_subjects(student_id)
        
        return {
            "student_id": student_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "current_period": {
                "academic_year_id": academic_year_id,
                "term_id": term_id
            },
            "current_grades": current_grades,
            "historical_grades": historical_grades,
            "subjects": subjects,
            "metadata": {
                "model": "academic_forecast_v1",
                "confidence_threshold": 0.7
            }
        }
    
    async def _get_grades_for_period(
        self,
        student_id: int,
        year_id: Optional[int],
        term_id: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get grades for a specific period"""
        query = select(Grade).where(Grade.student_id == student_id)
        
        if term_id:
            query = query.where(Grade.term_id == term_id)
        elif year_id:
            # If we have year but not term, get all terms in year
            query = query.join(Term).where(Term.academic_year_id == year_id)
        
        result = await self.db.execute(query)
        grades = result.scalars().all()
        
        return [
            {
                "subject_id": g.subject_id,
                "score": g.score,
                "max_score": g.max_score,
                "percentage": round(g.score / g.max_score * 100, 2) if g.max_score > 0 else 0,
                "assessment_type": g.grade_type,
                "date": g.date.isoformat()
            }
            for g in grades
        ]
    
    async def _get_historical_grades(
        self,
        student_id: int,
        year_id: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Get historical grades from previous terms"""
        if year_id is None:
            return []
        
        # Get grades from previous terms in same year
        result = await self.db.execute(
            select(Grade)
            .join(Term)
            .where(and_(
                Grade.student_id == student_id,
                Term.academic_year_id == year_id,
                Term.is_current == False
            ))
        )
        grades = result.scalars().all()
        
        return [
            {
                "term_id": g.term_id,
                "subject_id": g.subject_id,
                "score": g.score,
                "max_score": g.max_score,
                "percentage": round(g.score / g.max_score * 100, 2) if g.max_score > 0 else 0,
                "grade_type": g.grade_type
            }
            for g in grades
        ]
    
    async def _get_student_subjects(self, student_id: int) -> List[Dict[str, Any]]:
        """Get all subjects the student is enrolled in"""
        # This would typically come from enrollment/assignment tables
        # For now, get subjects from grades
        result = await self.db.execute(
            select(Grade.subject_id, Subject.name)
            .distinct()
            .join(Subject)
            .where(Grade.student_id == student_id)
        )
        
        return [
            {"id": row[0], "name": row[1]}
            for row in result.all()
        ]
    
    async def _identify_performance_patterns(
        self,
        grade_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify performance patterns from grade history"""
        patterns = []
        improvement_areas = []
        
        if not grade_history:
            return {"patterns": [], "improvement_areas": []}
        
        # Sort by date
        sorted_grades = sorted(grade_history, key=lambda x: x.get("date", ""))
        
        # Calculate overall average
        percentages = [g["percentage"] for g in sorted_grades]
        overall_avg = sum(percentages) / len(percentages) if percentages else 0
        
        # Check for improvement trend
        if len(sorted_grades) >= 4:
            early = sorted_grades[:len(sorted_grades)//2]
            late = sorted_grades[len(sorted_grades)//2:]
            
            early_avg = sum(g["percentage"] for g in early) / len(early)
            late_avg = sum(g["percentage"] for g in late) / len(late)
            
            if late_avg > early_avg + 5:
                patterns.append("Showing improving trend over the analyzed period")
            elif late_avg < early_avg - 5:
                patterns.append("Performance declining over the analyzed period")
            else:
                patterns.append("Maintaining consistent performance level")
        
        # Identify struggling subjects
        subject_scores = {}
        for grade in sorted_grades:
            subj = grade["subject_id"]
            if subj not in subject_scores:
                subject_scores[subj] = []
            subject_scores[subj].append(grade["percentage"])
        
        for subj, scores in subject_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 60:
                improvement_areas.append(f"Subject {subj}: Average {round(avg, 1)}%")
        
        # Overall assessment
        if overall_avg >= 80:
            patterns.append("Excellent overall academic performance")
        elif overall_avg >= 70:
            patterns.append("Good academic performance with room for improvement")
        elif overall_avg >= 60:
            patterns.append("Satisfactory performance requiring attention")
        else:
            patterns.append("Academic performance needs significant improvement")
        
        return {
            "patterns": patterns,
            "improvement_areas": improvement_areas,
            "overall_average": round(overall_avg, 2)
        }
    
    def _build_forecast_prompt(
        self,
        student: Student,
        context: Dict[str, Any]
    ) -> str:
        """Build the AI prompt for academic forecasting"""
        current_grades = context.get("current_grades", [])
        historical_grades = context.get("historical_grades", [])
        
        grades_summary = "Current Grades:\n"
        for g in current_grades:
            grades_summary += f"- Subject {g['subject_id']}: {g['percentage']}%\n"
        
        hist_summary = "Previous Term Grades:\n"
        for g in historical_grades:
            hist_summary += f"- Term {g['term_id']}, Subject {g['subject_id']}: {g['percentage']}%\n"
        
        return f"""Predict end-of-term academic performance for this student.

## STUDENT:
- Name: {student.first_name} {student.last_name}
- ID: {student.id}

## CURRENT GRADES:
{grades_summary}

## HISTORICAL PERFORMANCE:
{hist_summary}

## TASK:
1. Analyze the student's current performance and historical trends
2. Predict end-of-term grades for each subject
3. Identify subjects at risk of underperformance
4. Determine overall academic trend direction

## OUTPUT FORMAT:
Provide a JSON object with:
- forecasts: Array of {{subject_id, current_grade, predicted_grade, trend, confidence_score, key_factors, improvement_suggestions}}
- overall_trend: "UP", "DOWN", or "STABLE"
- predicted_gpa: Numeric GPA prediction (0-100 scale)
- at_risk_subjects: Array of subject names predicted below 50%
- summary: Brief summary of the analysis

Focus on actionable insights and specific recommendations for improvement."""
    
    def _create_basic_forecast(
        self,
        student: Student,
        context: Dict[str, Any]
    ) -> AcademicForecastResult:
        """Create a basic forecast without AI"""
        current_grades = context.get("current_grades", [])
        subjects = context.get("subjects", [])
        
        forecasts = []
        at_risk = []
        
        # Calculate predictions based on current grades
        grade_dict = {g["subject_id"]: g["percentage"] for g in current_grades}
        
        for subj in subjects:
            subj_id = subj["id"]
            current = grade_dict.get(subj_id, 0)
            
            # Basic prediction (current grade with minor adjustment)
            predicted = current * 1.02 if current > 70 else current  # Slight boost for good performers
            
            trend = TrendDirection.STABLE
            if current < 50:
                trend = TrendDirection.DOWN
                at_risk.append(subj["name"])
            elif current > 80:
                trend = TrendDirection.UP
            
            forecasts.append(SubjectForecast(
                subject_id=subj_id,
                subject_name=subj["name"],
                current_grade=current,
                predicted_grade=round(predicted, 1),
                trend=trend,
                confidence_score=0.65,
                key_factors=["Current performance level"],
                improvement_suggestions=["Continue consistent effort"] if predicted >= 70 else ["Seek additional support"]
            ))
        
        # Calculate overall
        predicted_grades = [f.predicted_grade for f in forecasts]
        avg_predicted = sum(predicted_grades) / len(predicted_grades) if predicted_grades else 0
        
        # Determine overall trend
        if at_risk:
            overall_trend = TrendDirection.DOWN
        elif avg_predicted > 75:
            overall_trend = TrendDirection.UP
        else:
            overall_trend = TrendDirection.STABLE
        
        return AcademicForecastResult(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            academic_year_id=context.get("current_period", {}).get("academic_year_id"),
            term_id=context.get("current_period", {}).get("term_id"),
            forecasts=forecasts,
            overall_trend=overall_trend,
            overall_predicted_gpa=round(avg_predicted, 1),
            at_risk_subjects=at_risk,
            analysis_summary=f"Based on current performance, predicted average is {round(avg_predicted, 1)}%."
        )
