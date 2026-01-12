"""
AI Service Configuration for Self-Hosted Models

This module configures AI services to work with self-hosted models
(Ollama, HuggingFace Local Transformers) instead of paid APIs like OpenAI.

Budget-Friendly AI Options:
1. Ollama - Run local LLMs like Llama 2, Mistral locally
2. HuggingFace Transformers - Run BERT, GPT-2 locally
3. vLLM - High-performance local inference server
"""

import asyncio
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from app.config import settings


@dataclass
class AIResponse:
    """Response from AI service"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class SelfHostedAIService:
    """
    Self-hosted AI service that supports multiple local model providers.
    
    Supports:
    - Ollama (Llama 2, Mistral, CodeLlama, etc.)
    - HuggingFace Inference Endpoints (local or cloud)
    - vLLM serving local models
    
    All models run locally or on your own infrastructure,
    eliminating per-token costs from OpenAI/Anthropic.
    """
    
    def __init__(self):
        self.service_url = settings.AI_SERVICE_URL
        self.provider = "ollama"  # Default provider
        
    async def analyze_at_risk_students(
        self,
        attendance_data: List[Dict],
        performance_data: List[Dict]
    ) -> AIResponse:
        """
        Identify at-risk students based on attendance and performance patterns.
        
        Uses local LLM to analyze patterns and generate insights.
        Free and runs entirely on your hardware.
        """
        prompt = self._build_at_risk_prompt(attendance_data, performance_data)
        
        try:
            # Try self-hosted Ollama first (free)
            response = await self._query_ollama(prompt, "at-risk-analysis")
            
            if response.success:
                return response
            
            # Fallback to rule-based analysis if AI unavailable
            return self._rule_based_at_risk_analysis(attendance_data, performance_data)
            
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"At-risk analysis failed: {str(e)}"
            )
    
    async def generate_lesson_plan(
        self,
        subject: str,
        topic: str,
        grade_level: int,
        duration_minutes: int = 45
    ) -> AIResponse:
        """
        Generate a lesson plan using local AI model.
        
        Completely free with self-hosted models.
        """
        prompt = self._build_lesson_plan_prompt(
            subject, topic, grade_level, duration_minutes
        )
        
        try:
            response = await self._query_ollama(prompt, "lesson-plan")
            
            if response.success:
                return response
            
            # Fallback template-based generation
            return self._template_lesson_plan(subject, topic, grade_level, duration_minutes)
            
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"Lesson plan generation failed: {str(e)}"
            )
    
    async def generate_quiz_questions(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        question_count: int = 10
    ) -> AIResponse:
        """
        Generate quiz questions using local AI.
        
        No per-question costs - runs on your infrastructure.
        """
        prompt = self._build_quiz_prompt(subject, topic, difficulty, question_count)
        
        try:
            response = await self._query_ollama(prompt, "quiz-generator")
            
            if response.success:
                return response
            
            return AIResponse(
                success=False,
                error="Quiz generation unavailable - AI service not configured"
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"Quiz generation failed: {str(e)}"
            )
    
    async def analyze_student_performance(
        self,
        student_data: Dict,
        recent_grades: List[Dict],
        attendance_records: List[Dict]
    ) -> AIResponse:
        """
        Generate personalized learning recommendations using local AI.
        """
        prompt = self._build_performance_prompt(
            student_data, recent_grades, attendance_records
        )
        
        try:
            response = await self._query_ollama(prompt, "performance-analysis")
            
            if response.success:
                return response
            
            return AIResponse(
                success=False,
                error="Performance analysis unavailable"
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"Performance analysis failed: {str(e)}"
            )
    
    async def _query_ollama(self, prompt: str, model_type: str) -> AIResponse:
        """
        Query Ollama local model server.
        
        Setup instructions:
        1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
        2. Pull a model: ollama pull llama2
        3. Start server: ollama serve
        4. Configure AI_SERVICE_URL in .env to point to Ollama server
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Ollama API format
                response = await client.post(
                    f"{self.service_url}/api/generate",
                    json={
                        "model": "llama2",  # Or "mistral", "codellama", etc.
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 2048
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return AIResponse(
                        success=True,
                        content=data.get("response", ""),
                        metadata={"model": "ollama-llama2"}
                    )
                else:
                    return AIResponse(
                        success=False,
                        error=f"Ollama API error: {response.status_code}"
                    )
                    
        except httpx.RequestError as e:
            return AIResponse(
                success=False,
                error=f"Cannot connect to Ollama server at {self.service_url}. "
                      "Install Ollama and run: ollama serve"
            )
    
    def _build_at_risk_prompt(
        self,
        attendance_data: List[Dict],
        performance_data: List[Dict]
    ) -> str:
        """Build prompt for at-risk student analysis"""
        return f"""
        Analyze the following student data to identify at-risk students.
        
        Attendance Data: {attendance_data}
        Performance Data: {performance_data}
        
        Identify students who may be at risk of falling behind based on:
        1. Declining attendance (<80%)
        2. Declining grades
        3. Multiple consecutive absences
        4. Sudden performance drops
        
        Provide a list of at-risk students with specific concerns and suggested interventions.
        Format as JSON with student_id, risk_level, concerns, and recommendations.
        """
    
    def _build_lesson_plan_prompt(
        self,
        subject: str,
        topic: str,
        grade_level: int,
        duration: int
    ) -> str:
        """Build prompt for lesson plan generation"""
        return f"""
        Create a detailed lesson plan for:
        - Subject: {subject}
        - Topic: {topic}
        - Grade Level: {grade_level}
        - Duration: {duration} minutes
        
        Include:
        1. Learning Objectives
        2. Materials Needed
        3. Introduction/Hook
        4. Main Activities
        5. Assessment Methods
        6. Homework/Follow-up
        
        Format as a structured lesson plan.
        """
    
    def _build_quiz_prompt(
        self,
        subject: str,
        topic: str,
        difficulty: str,
        count: int
    ) -> str:
        """Build prompt for quiz generation"""
        return f"""
        Generate {count} multiple choice questions about:
        - Subject: {subject}
        - Topic: {topic}
        - Difficulty: {difficulty}
        
        Format each question as:
        Question: <question_text>
        A) <option1>
        B) <option2>
        C) <option3>
        D) <option4>
        Answer: <correct_option>
        
        Return all questions in a numbered list.
        """
    
    def _build_performance_prompt(
        self,
        student_data: Dict,
        grades: List[Dict],
        attendance: List[Dict]
    ) -> str:
        """Build prompt for performance analysis"""
        return f"""
        Analyze this student's performance and provide personalized recommendations:
        
        Student: {student_data}
        Recent Grades: {grades}
        Attendance: {attendance}
        
        Provide:
        1. Performance Summary
        2. Strengths Identified
        3. Areas for Improvement
        4. Specific Study Recommendations
        5. Suggested Resources
        """
    
    def _rule_based_at_risk_analysis(
        self,
        attendance_data: List[Dict],
        performance_data: List[Dict]
    ) -> AIResponse:
        """
        Fallback rule-based analysis when AI is unavailable.
        Completely free and always available.
        """
        at_risk_students = []
        
        for student in attendance_data:
            attendance_rate = student.get("attendance_rate", 100)
            if attendance_rate < 80:
                at_risk_students.append({
                    "student_id": student.get("student_id"),
                    "risk_level": "high" if attendance_rate < 60 else "medium",
                    "concerns": [f"Low attendance: {attendance_rate}%"],
                    "recommendations": [
                        "Schedule meeting with parents",
                        "Review transportation issues",
                        "Consider tutoring support"
                    ]
                })
        
        return AIResponse(
            success=True,
            content="Rule-based analysis completed",
            metadata={
                "method": "rule-based",
                "at_risk_count": len(at_risk_students),
                "students": at_risk_students
            }
        )
    
    def _template_lesson_plan(
        self,
        subject: str,
        topic: str,
        grade: int,
        duration: int
    ) -> AIResponse:
        """Fallback template-based lesson plan when AI is unavailable"""
        plan = {
            "subject": subject,
            "topic": topic,
            "grade": grade,
            "duration": duration,
            "objectives": [f"Understand key concepts of {topic}"],
            "materials": ["Textbook", "Notebook", "Writing implements"],
            "activities": [
                {"time": "5 min", "activity": "Introduction and warm-up"},
                {"time": f"{duration-30} min", "activity": f"Main lesson on {topic}"},
                {"time": "15 min", "activity": "Practice exercises"},
                {"time": "10 min", "activity": "Review and Q&A"}
            ],
            "assessment": "Informal observation during practice",
            "note": "Template plan - AI-generated plans available when Ollama is configured"
        }
        
        return AIResponse(
            success=True,
            content="Template-based lesson plan generated",
            metadata={"method": "template", "plan": plan}
        )


# Singleton instance
ai_service = SelfHostedAIService()


async def get_ai_service() -> SelfHostedAIService:
    """Dependency to get AI service instance"""
    return ai_service
