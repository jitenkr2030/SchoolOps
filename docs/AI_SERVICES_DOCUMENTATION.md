# SchoolOps AI Services API Documentation

## Overview
SchoolOps provides AI-powered services for analytics, predictions, personalization, and automation. This documentation covers all AI service endpoints.

## Base URL
- **AI Services**: `https://ai.schoolops.com/api/v1`

## Authentication
All AI service requests require authentication using the same JWT token as the main API.

---

## Analytics & Predictions

### POST /analytics/predict-student-risk
Predict student at-risk status based on historical data.

**Request:**
```json
{
    "student_id": "STU001",
    "attendance_history": [
        {"date": "2024-09-01", "status": "Present"},
        {"date": "2024-09-02", "status": "Absent"},
        {"date": "2024-09-03", "status": "Present"}
    ],
    "grade_history": [
        {"subject": "Mathematics", "score": 75},
        {"subject": "Science", "score": 82}
    ],
    "behavior_records": []
}
```

**Response:**
```json
{
    "student_id": "STU001",
    "risk_score": 0.65,
    "risk_level": "Medium Risk",
    "confidence": 0.87,
    "contributing_factors": [
        {
            "factor": "Low Attendance",
            "impact": "High",
            "description": "Attendance rate dropped below 80%"
        },
        {
            "factor": "Academic Performance",
            "impact": "Medium",
            "description": "Scores below class average in Mathematics"
        }
    ],
    "recommendations": [
        "Schedule parent-teacher meeting",
        "Consider remedial classes for Mathematics",
        "Monitor attendance closely for next 2 weeks"
    ]
}
```

### POST /analytics/forecast-enrollment
Forecast enrollment for upcoming periods.

**Request:**
```json
{
    "historical_enrollment": [
        {"year": 2020, "month": 4, "enrollments": 150},
        {"year": 2021, "month": 4, "enrollments": 165},
        {"year": 2022, "month": 4, "enrollments": 180},
        {"year": 2023, "month": 4, "enrollments": 195}
    ],
    "forecast_periods": 6,
    "include_seasonal": true
}
```

**Response:**
```json
{
    "predictions": [
        {"month": "April 2024", "predicted_enrollments": 210, "lower_bound": 200, "upper_bound": 220},
        {"month": "May 2024", "predicted_enrollments": 215, "lower_bound": 205, "upper_bound": 225}
    ],
    "growth_rate": 7.5,
    "trend": "increasing",
    "seasonal_patterns": {
        "peak_month": "April",
        "low_month": "September",
        "average_growth": "8% annually"
    }
}
```

### POST /analytics/predict-fee-churn
Predict likelihood of fee payment default.

**Request:**
```json
{
    "student_id": "STU001",
    "fee_history": [
        {"due_date": "2024-04-30", "amount": 5000, "status": "Paid", "paid_date": "2024-04-25"},
        {"due_date": "2024-05-31", "amount": 5000, "status": "Overdue", "paid_date": null}
    ],
    "parent_income_bracket": "Middle"
}
```

**Response:**
```json
{
    "student_id": "STU001",
    "churn_probability": 0.72,
    "risk_level": "High",
    "indicators": [
        "Previous payment delays",
        "Current outstanding balance"
    ],
    "intervention_suggestions": [
        "Send payment reminder",
        "Offer installment plan",
        "Contact parent to discuss"
    ]
}
```

---

## Personalization & Learning

### POST /personalization/adaptive-learning-path
Generate personalized learning path for student.

**Request:**
```json
{
    "student_id": "STU001",
    "current_level": "Intermediate",
    "subject": "Mathematics",
    "learning_goals": ["Improve Algebra", "Master Geometry"],
    "available_time": "2 hours/week"
}
```

**Response:**
```json
{
    "student_id": "STU001",
    "learning_path": [
        {
            "week": 1,
            "topics": ["Linear Equations", "Variables"],
            "activities": [
                {"type": "Video", "title": "Introduction to Algebra", "duration": "15 min"},
                {"type": "Quiz", "title": "Basic Equations", "questions": 10}
            ],
            "resources": [
                {"type": "PDF", "title": "Algebra Basics", "url": "..."}
            ]
        }
    ],
    "estimated_completion": "6 weeks",
    "prerequisites": ["Basic Arithmetic"]
}
```

### POST /personalization/recommend-content
Recommend learning content based on performance.

**Request:**
```json
{
    "student_id": "STU001",
    "subject": "Science",
    "recent_scores": [
        {"topic": "Physics", "score": 65},
        {"topic": "Chemistry", "score": 78}
    ],
    "learning_style": "Visual"
}
```

**Response:**
```json
{
    "recommendations": [
        {
            "content_id": "VID001",
            "type": "Video",
            "title": "Physics Fundamentals",
            "reason": "Weak area detected - score below 70%",
            "match_score": 0.92
        },
        {
            "content_id": "QZ002",
            "type": "Practice Quiz",
            "title": "Chemistry Equations",
            "reason": "Strengthen current progress",
            "match_score": 0.85
        }
    ]
}
```

---

## Automation & Assistants

### POST /automation/generate-quiz
Generate quiz from lesson content.

**Request:**
```json
{
    "lesson_content": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
    "num_questions": 5,
    "question_types": ["multiple_choice", "short_answer"],
    "difficulty": "Medium",
    "topic": "Biology"
}
```

**Response:**
```json
{
    "quiz_id": "QZ2024001",
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "What is the primary function of photosynthesis?",
            "options": [
                {"text": "Convert light energy to chemical energy", "correct": true},
                {"text": "Convert chemical energy to light", "correct": false},
                {"text": "Store water", "correct": false},
                {"text": "Release oxygen", "correct": false}
            ],
            "difficulty": "Easy",
            "points": 10
        }
    ],
    "total_points": 50,
    "estimated_time": "15 minutes"
}
```

### POST /automation/summarize-text
Summarize long text content.

**Request:**
```json
{
    "text": "Long text content to summarize...",
    "max_length": 100,
    "style": "concise"
}
```

**Response:**
```json
{
    "summary": "Concise summary of the text...",
    "key_points": [
        "Point 1",
        "Point 2",
        "Point 3"
    ],
    "reading_time": "2 minutes",
    "compression_ratio": 0.3
}
```

---

## NLP & Conversational AI

### POST /nlp/chatbot/query
Process chatbot query.

**Request:**
```json
{
    "query": "What is my child's attendance percentage?",
    "user_id": "PAR001",
    "student_id": "STU001",
    "language": "English"
}
```

**Response:**
```json
{
    "intent": "attendance_inquiry",
    "entities": {
        "student_id": "STU001",
        "query_type": "percentage"
    },
    "response": "Your child John has an attendance rate of 92% for the current month. They were present for 23 out of 25 days.",
    "suggested_actions": [
        "View detailed attendance report",
        "Set attendance alerts"
    ]
}
```

### POST /nlp/translate
Translate text to specified language.

**Request:**
```json
{
    "text": "What is the homework for today?",
    "target_language": "Hindi",
    "source_language": "English"
}
```

**Response:**
```json
{
    "translated_text": "आज का गृहकार्य क्या है?",
    "source_language": "English",
    "target_language": "Hindi",
    "confidence": 0.95
}
```

### POST /nlp/sentiment-analyze
Analyze sentiment of text.

**Request:**
```json
{
    "text": "Very happy with the school's progress report system!",
    "context": "parent_feedback"
}
```

**Response:**
```json
{
    "sentiment": "positive",
    "score": 0.89,
    "emotions": {
        "joy": 0.75,
        "satisfaction": 0.82
    },
    "key_phrases": ["happy with", "progress report system"]
}
```

---

## Document & Vision AI

### POST /vision/extract-text
Extract text from image/document.

**Request:**
```json
{
    "image_base64": "base64_encoded_image_data",
    "language": "English",
    "is_handwritten": false
}
```

**Response:**
```json
{
    "extracted_text": "Invoice #12345\nDate: 2024-10-15\nAmount: Rs. 5,000",
    "confidence": 0.95,
    "regions": [
        {
            "text": "Invoice #12345",
            "type": "invoice_number",
            "confidence": 0.98
        }
    ]
}
```

### POST /vision/verify-document
Verify authenticity of document.

**Request:**
```json
{
    "document_type": "id_card",
    "image_base64": "base64_encoded_image"
}
```

**Response:**
```json
{
    "is_valid": true,
    "confidence": 0.92,
    "extracted_fields": {
        "name": "John Doe",
        "dob": "2010-05-15",
        "id_number": "ID123456"
    },
    "verification_checks": {
        "format_valid": true,
        "photo_matches": true,
        "expiration_valid": true
    }
}
```

### POST /vision/process-invoice
Process and extract data from invoices.

**Request:**
```json
{
    "image_base64": "base64_encoded_invoice",
    "extract_line_items": true
}
```

**Response:**
```json
{
    "invoice_number": "INV-2024-001",
    "date": "2024-10-15",
    "vendor": {
        "name": "School Supplies Co.",
        "address": "123 Market St"
    },
    "total_amount": 15000,
    "tax_amount": 1500,
    "currency": "INR",
    "line_items": [
        {
            "description": "Textbooks",
            "quantity": 50,
            "unit_price": 200,
            "total": 10000
        }
    ]
}
```

---

## Optimization Services

### POST /optimization/timetable
Generate optimized timetable.

**Request:**
```json
{
    "teachers": [
        {"id": "T001", "subject": "Mathematics", "availability": ["Mon", "Tue", "Wed", "Thu", "Fri"]}
    ],
    "classes": [
        {"id": "C001", "name": "Class 10", "sections": ["A", "B"]}
    ],
    "rooms": [
        {"id": "R001", "capacity": 40, "type": "classroom"}
    ],
    "subjects_per_week": {
        "Mathematics": 6,
        "Science": 5,
        "English": 5
    },
    "constraints": {
        "max_consecutive_periods": 2,
        "no_double_periods_for": ["Science"]
    }
}
```

**Response:**
```json
{
    "timetable_id": "TT2024001",
    "schedule": [
        {
            "day": "Monday",
            "periods": [
                {"time": "09:00-10:00", "class": "10-A", "subject": "Mathematics", "teacher": "T001", "room": "R001"},
                {"time": "10:00-11:00", "class": "10-B", "subject": "Science", "teacher": "T002", "room": "R002"}
            ]
        }
    ],
    "metrics": {
        "teacher_utilization": 0.85,
        "room_utilization": 0.75,
        "constraint_violations": 0
    }
}
```

### POST /optimize/bus-routes
Optimize school bus routes.

**Request:**
```json
{
    "stops": [
        {"id": "S001", "name": "Stop A", "lat": 12.9716, "lng": 77.5946},
        {"id": "S002", "name": "Stop B", "lat": 12.9721, "lng": 77.5950}
    ],
    "students": [
        {"id": "STU001", "stop_id": "S001", "pickup_time": "07:00"}
    ],
    "bus_capacity": 30,
    "school_start_time": "08:00"
}
```

**Response:**
```json
{
    "routes": [
        {
            "route_id": "RT001",
            "bus_id": "BUS001",
            "stops": [
                {"stop": "S001", "arrival_time": "07:15", "students_boarded": 5},
                {"stop": "S002", "arrival_time": "07:25", "students_boarded": 3}
            ],
            "total_travel_time": "45 minutes",
            "total_distance": "12.5 km"
        }
    ],
    "optimization_metrics": {
        "total_buses_used": 2,
        "average_route_efficiency": 0.88,
        "estimated_fuel_savings": "15%"
    }
}
```

---

## Error Handling

All endpoints return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 400 | Invalid input or model error |
| 401 | Unauthorized |
| 422 | Validation error |
| 500 | Internal server error |

**Error Response:**
```json
{
    "error": {
        "code": "INVALID_INPUT",
        "message": "Missing required field: student_id",
        "details": {
            "field": "student_id",
            "issue": "Field is required"
        }
    }
}
```

---

## Rate Limits
- 50 requests per minute per endpoint
- Batch processing available for large datasets
