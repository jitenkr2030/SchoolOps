"""
Personalization & Learning Router
AI-powered adaptive learning paths, personalized recommendations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class LearningPathRequest(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    current_level: str
    target_level: str
    learning_style: Optional[str] = None
    time_available: Optional[int] = None  # minutes per day


class LearningPathResponse(BaseModel):
    learning_path_id: int
    student_id: int
    subject: str
    current_level: str
    target_level: str
    modules: List[dict]
    estimated_duration: int  # days
    milestones: List[dict]


class AdaptiveContentRequest(BaseModel):
    student_id: int
    subject_id: int
    topic: str
    completed_content: List[str]
    performance_history: List[dict]


class AdaptiveContentResponse(BaseModel):
    recommended_content: List[dict]
    skipped_content: List[str]
    difficulty_adjustment: str
    estimated_improvement: float


class RemedialAssignmentRequest(BaseModel):
    student_id: int
    subject_id: int
    weak_competencies: List[str]
    difficulty_level: str


class RemedialAssignmentResponse(BaseModel):
    assignments: List[dict]
    practice_exercises: List[dict]
    estimated_completion_time: int


class CurriculumGapRequest(BaseModel):
    class_id: int
    subject_id: int
    assessment_results: List[dict]


class CurriculumGapResponse(BaseModel):
    identified_gaps: List[dict]
    priority_topics: List[dict]
    remediation_plan: List[dict]


# Mock competency database
COMPETENCY_FRAMEWORK = {
    "Mathematics": {
        "Grade 9": ["algebra_basics", "geometry_fundamentals", "data_interpretation", "number_operations"],
        "Grade 10": ["advanced_algebra", "trigonometry", "probability", "linear_equations"],
        "Grade 11": ["calculus_intro", "statistics", "coordinate_geometry", "functions"],
        "Grade 12": ["differential_calculus", "integral_calculus", "vectors_3d", "probability_distributions"]
    },
    "Physics": {
        "Grade 9": ["motion_basics", "forces", "energy", "matter_states"],
        "Grade 10": ["newton_laws", "thermodynamics", "waves", "electricity_basics"],
        "Grade 11": ["mechanics", "shm_waves", "gravitation", "electrostatics"],
        "Grade 12": ["electromagnetism", "optics", "modern_physics", "nuclear_physics"]
    },
    "Chemistry": {
        "Grade 9": ["atomic_structure", "periodic_table", "chemical_bonding", "mole_concept"],
        "Grade 10": ["thermochemistry", "reaction_rates", "acids_bases", "electrochemistry"],
        "Grade 11": ["organic_basics", "hydrocarbons", "functional_groups", "stereochemistry"],
        "Grade 12": ["polymer_chemistry", "biomolecules", "coordination_chemistry", "analytical_chemistry"]
    }
}


# Endpoints
@router.post("/generate-learning-path", response_model=LearningPathResponse)
async def generate_learning_path(request: LearningPathRequest):
    """
    Generate personalized learning path based on student profile
    Uses AI to recommend lessons and practice questions
    """
    try:
        logger.info(f"Generating learning path for student {request.student_id}")
        
        # Mock learning path generation (in production: use AI model)
        modules = [
            {
                "module_id": 1,
                "title": "Foundation Building",
                "topics": ["Core Concepts", "Basic Applications"],
                "content_type": ["video", "reading", "quiz"],
                "duration_days": 5,
                "difficulty": "easy",
                "prerequisites": [],
                "ai_recommendation": "Start with fundamentals to build strong base"
            },
            {
                "module_id": 2,
                "title": "Skill Development",
                "topics": ["Problem Solving", "Practical Applications"],
                "content_type": ["interactive", "practice", "discussion"],
                "duration_days": 7,
                "difficulty": "medium",
                "prerequisites": [1],
                "ai_recommendation": "Focus on application-based learning"
            },
            {
                "module_id": 3,
                "title": "Advanced Topics",
                "topics": ["Complex Problems", "Critical Thinking"],
                "content_type": ["case_study", "project", "peer_review"],
                "duration_days": 7,
                "difficulty": "hard",
                "prerequisites": [2],
                "ai_recommendation": "Challenge with advanced scenarios"
            },
            {
                "module_id": 4,
                "title": "Assessment & Review",
                "topics": ["Mock Tests", "Error Analysis"],
                "content_type": ["test", "review", "feedback"],
                "duration_days": 3,
                "difficulty": "varied",
                "prerequisites": [1, 2, 3],
                "ai_recommendation": "Comprehensive review and assessment"
            }
        ]
        
        milestones = [
            {"day": 5, "title": "Foundation Complete", "criteria": "80% quiz score"},
            {"day": 12, "title": "Skills Assessment", "criteria": "Practice problems accuracy"},
            {"day": 19, "title": "Advanced Topics", "criteria": "Project completion"},
            {"day": 22, "title": "Final Assessment", "criteria": "Mock test 70%+"}
        ]
        
        return LearningPathResponse(
            learning_path_id=1,
            student_id=request.student_id,
            subject="Mathematics",
            current_level=request.current_level,
            target_level=request.target_level,
            modules=modules,
            estimated_duration=22,
            milestones=milestones
        )
        
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adaptive-content", response_model=AdaptiveContentResponse)
async def get_adaptive_content(request: AdaptiveContentRequest):
    """
    Recommend content based on student performance and learning patterns
    """
    try:
        logger.info(f"Generating adaptive content for student {request.student_id}")
        
        # Analyze performance history
        avg_score = np.mean([p.get("score", 0) for p in request.performance_history]) if request.performance_history else 70
        
        # Determine difficulty adjustment
        if avg_score < 50:
            difficulty_adjustment = "decrease_difficulty"
            recommended_content = [
                {"type": "video", "title": "Concept Explanation", "difficulty": "easy"},
                {"type": "reading", "title": "Simplified Guide", "difficulty": "easy"},
                {"type": "practice", "title": "Basic Problems", "difficulty": "easy"},
                {"type": "quiz", "title": "Foundation Quiz", "difficulty": "easy"}
            ]
        elif avg_score < 70:
            difficulty_adjustment = "maintain_difficulty"
            recommended_content = [
                {"type": "video", "title": "Advanced Concepts", "difficulty": "medium"},
                {"type": "practice", "title": "Practice Set", "difficulty": "medium"},
                {"type": "quiz", "title": "Topic Assessment", "difficulty": "medium"},
                {"type": "discussion", "title": "Peer Learning", "difficulty": "medium"}
            ]
        else:
            difficulty_adjustment = "increase_difficulty"
            recommended_content = [
                {"type": "video", "title": "Expert Tutorials", "difficulty": "hard"},
                {"type": "project", "title": "Real-world Application", "difficulty": "hard"},
                {"type": "competition", "title": "Challenge Problems", "difficulty": "hard"},
                {"type": "mentoring", "title": "Peer Teaching", "difficulty": "varied"}
            ]
        
        return AdaptiveContentResponse(
            recommended_content=recommended_content,
            skipped_content=["review_basics"],  # Content student has mastered
            difficulty_adjustment=difficulty_adjustment,
            estimated_improvement=5.0 + (avg_score < 50 ? 10 : 5)
        )
        
    except Exception as e:
        logger.error(f"Error generating adaptive content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remedial-assignments", response_model=RemedialAssignmentResponse)
async def generate_remedial_assignments(request: RemedialAssignmentRequest):
    """
    Generate automated remedial assignments for weak competencies
    """
    try:
        logger.info(f"Generating remedial assignments for student {request.student_id}")
        
        # Generate assignments for each weak competency
        assignments = []
        practice_exercises = []
        
        for competency in request.weak_competencies:
            assignments.append({
                "assignment_id": len(assignments) + 1,
                "title": f"Mastering {competency.replace('_', ' ').title()}",
                "type": "remedial",
                "competency": competency,
                "questions": 10,
                "difficulty": request.difficulty_level,
                "estimated_time": 30,
                "ai_generated": True,
                "resources": [
                    f"Video tutorial on {competency}",
                    f"Practice worksheet for {competency}",
                    f"Interactive simulation for {competency}"
                ]
            })
            
            practice_exercises.append({
                "exercise_id": len(practice_exercises) + 1,
                "focus_area": competency,
                "exercise_type": "drill",
                "difficulty": "easy",
                "questions_count": 20,
                "adaptive": True
            })
        
        return RemedialAssignmentResponse(
            assignments=assignments,
            practice_exercises=practice_exercises,
            estimated_completion_time=len(request.weak_competencies) * 30
        )
        
    except Exception as e:
        logger.error(f"Error generating remedial assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-curriculum-gaps", response_model=CurriculumGapResponse)
async def detect_curriculum_gaps(request: CurriculumGapRequest):
    """
    Detect topic-level weaknesses across the cohort
    """
    try:
        logger.info(f"Detecting curriculum gaps for class {request.class_id}")
        
        # Analyze assessment results
        topic_scores = {}
        for result in request.assessment_results:
            topic = result.get("topic", "Unknown")
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(result.get("score", 0))
        
        # Calculate average scores per topic
        topic_averages = {
            topic: np.mean(scores) 
            for topic, scores in topic_scores.items()
        }
        
        # Identify gaps (topics with low scores)
        identified_gaps = []
        for topic, avg_score in topic_averages.items():
            if avg_score < 60:
                identified_gaps.append({
                    "topic": topic,
                    "average_score": round(avg_score, 2),
                    "students_struggling": sum(1 for s in topic_scores[topic] if s < 60),
                    "severity": "high" if avg_score < 40 else "medium" if avg_score < 50 else "low"
                })
        
        # Sort by severity
        identified_gaps.sort(key=lambda x: x["severity"], reverse=True)
        
        # Generate priority topics
        priority_topics = [
            {
                "topic": gap["topic"],
                "priority": idx + 1,
                "recommended_action": f"Review session on {gap['topic']}",
                "suggested_duration": "2-3 classes"
            }
            for idx, gap in enumerate(identified_gaps[:5])
        ]
        
        # Remediation plan
        remediation_plan = [
            {
                "phase": 1,
                "duration": "1 week",
                "actions": [
                    "Identify students needing extra help",
                    "Schedule remedial sessions",
                    "Provide supplementary materials"
                ]
            },
            {
                "phase": 2,
                "duration": "2 weeks",
                "actions": [
                    "Conduct review classes",
                    "Monitor progress closely",
                    "Adjust teaching pace if needed"
                ]
            },
            {
                "phase": 3,
                "duration": "Ongoing",
                "actions": [
                    "Re-assess topic mastery",
                    "Provide ongoing support",
                    "Update curriculum based on findings"
                ]
            }
        ]
        
        return CurriculumGapResponse(
            identified_gaps=identified_gaps,
            priority_topics=priority_topics,
            remediation_plan=remediation_plan
        )
        
    except Exception as e:
        logger.error(f"Error detecting curriculum gaps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper import
import numpy as np
