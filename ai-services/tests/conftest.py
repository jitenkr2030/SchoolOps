"""
Pytest configuration and fixtures for AI Services Tests
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ml_model():
    """Mock ML model for testing without actual inference."""
    class MockModel:
        def predict(self, input_data):
            return {"prediction": 0.85, "confidence": 0.92}
        
        def predict_batch(self, input_data_list):
            return [
                {"prediction": 0.85, "confidence": 0.92}
                for _ in input_data_list
            ]
    
    return MockModel()


@pytest.fixture
def mock_nlp_model():
    """Mock NLP model for testing."""
    class MockNLP:
        def analyze_sentiment(self, text):
            return {"sentiment": "positive", "score": 0.85}
        
        def translate(self, text, target_lang):
            return {"translated_text": f"[{target_lang}] {text}"}
        
        def summarize(self, text, max_length=100):
            return {"summary": text[:max_length] + "..."}
    
    return MockNLP()


@pytest.fixture
def mock_vision_model():
    """Mock Vision model for testing."""
    class MockVision:
        def extract_text(self, image_data):
            return {"extracted_text": "Sample extracted text", "confidence": 0.95}
        
        def verify_document(self, document_data):
            return {"is_valid": True, "confidence": 0.88}
    
    return MockVision()


@pytest_asyncio.fixture(scope="function")
async def ai_client():
    """Create an async test client for AI services."""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_student_data():
    """Sample student data for AI testing."""
    return {
        "student_id": "STU001",
        "attendance_history": [
            {"date": "2024-09-01", "status": "Present"},
            {"date": "2024-09-02", "status": "Present"},
            {"date": "2024-09-03", "status": "Absent"},
            {"date": "2024-09-04", "status": "Present"},
            {"date": "2024-09-05", "status": "Late"},
        ],
        "grade_history": [
            {"subject": "Mathematics", "score": 75},
            {"subject": "Science", "score": 82},
            {"subject": "English", "score": 68},
            {"subject": "Social Studies", "score": 90},
        ],
        "behavior_records": [
            {"date": "2024-09-01", "incident": None},
            {"date": "2024-09-05", "incident": "Late arrival"},
        ]
    }


@pytest.fixture
def sample_fee_data():
    """Sample fee data for AI testing."""
    return {
        "student_id": "STU001",
        "fee_history": [
            {"due_date": "2024-04-30", "amount": 5000, "status": "Paid", "paid_date": "2024-04-25"},
            {"due_date": "2024-05-31", "amount": 5000, "status": "Paid", "paid_date": "2024-05-30"},
            {"due_date": "2024-06-30", "amount": 5000, "status": "Overdue", "paid_date": None},
        ]
    }


@pytest.fixture
def sample_enrollment_data():
    """Sample enrollment data for forecasting."""
    return {
        "historical_enrollment": [
            {"year": 2020, "month": 4, "enrollments": 150},
            {"year": 2021, "month": 4, "enrollments": 165},
            {"year": 2022, "month": 4, "enrollments": 180},
            {"year": 2023, "month": 4, "enrollments": 195},
            {"year": 2024, "month": 4, "enrollments": 210},
        ],
        "seasonal_factors": {
            "April": 1.0,
            "May": 0.8,
            "June": 0.6,
            "July": 0.4,
            "August": 0.3,
            "September": 0.2,
            "October": 0.1,
            "November": 0.1,
            "December": 0.1,
            "January": 0.3,
            "February": 0.5,
            "March": 0.7,
        }
    }


@pytest.fixture
def sample_timetable_constraints():
    """Sample timetable constraints for optimization."""
    return {
        "teachers": [
            {"id": "T001", "name": "Mr. Sharma", "subject": "Mathematics", "availability": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
            {"id": "T002", "name": "Ms. Patel", "subject": "Science", "availability": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
            {"id": "T003", "name": "Mr. Singh", "subject": "English", "availability": ["Mon", "Tue", "Wed", "Thu"]},
        ],
        "classes": [
            {"id": "C001", "name": "Class 10"},
            {"id": "C002", "name": "Class 9"},
        ],
        "rooms": [
            {"id": "R001", "capacity": 40, "type": "classroom"},
            {"id": "R002", "capacity": 30, "type": "lab"},
        ],
        "time_slots": ["09:00-10:00", "10:00-11:00", "11:00-12:00", "13:00-14:00", "14:00-15:00"],
        "subjects_per_week": {
            "Mathematics": 6,
            "Science": 5,
            "English": 5,
        }
    }


@pytest.fixture
def sample_chatbot_query():
    """Sample chatbot queries for NLP testing."""
    return {
        "queries": [
            "What is my child's attendance?",
            "When are the fees due?",
            "Show my homework assignments",
            "What is the school timing?",
            "When are the parent-teacher meetings?",
        ]
    }


@pytest.fixture
def sample_document_image():
    """Sample document image data for OCR testing."""
    return {
        "image_base64": "base64_encoded_image_data",
        "document_type": "invoice",
        "expected_fields": ["invoice_number", "date", "amount", "vendor"]
    }
