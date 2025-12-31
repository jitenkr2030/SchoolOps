"""
Pytest configuration and fixtures for SchoolOps Backend Tests
"""
import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import test database and models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Base, get_db
from app.models.models import User, Student, Teacher, Class, Section, Subject, AcademicYear
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    """Create an async test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user."""
    user = User(
        email="admin@schoolops.test",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="Admin",
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_teacher(db_session):
    """Create a test teacher."""
    teacher = Teacher(
        email="teacher@schoolops.test",
        first_name="Test",
        last_name="Teacher",
        subject="Mathematics",
        phone="+1234567890"
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher


@pytest.fixture
def test_student(db_session):
    """Create a test student."""
    student = Student(
        first_name="Test",
        last_name="Student",
        email="student@schoolops.test",
        admission_number="TEST001",
        date_of_birth="2010-01-01",
        gender="Male"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_academic_year(db_session):
    """Create a test academic year."""
    academic_year = AcademicYear(
        name="2024-2025",
        start_date="2024-04-01",
        end_date="2025-03-31",
        is_active=True
    )
    db_session.add(academic_year)
    db_session.commit()
    db_session.refresh(academic_year)
    return academic_year


@pytest.fixture
def test_class(db_session, test_academic_year):
    """Create a test class."""
    class_obj = Class(
        name="Class 10",
        academic_year_id=test_academic_year.id
    )
    db_session.add(class_obj)
    db_session.commit()
    db_session.refresh(class_obj)
    return class_obj


@pytest.fixture
def auth_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@schoolops.test",
            "password": "test_password"
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {}
