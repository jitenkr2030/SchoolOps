"""
Unit tests for database models in SchoolOps Backend
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.models import (
    User, Student, Teacher, Class, Section, Subject,
    AcademicYear, Attendance, FeeRecord, Grade
)


class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self, db_session):
        """Test creating a basic user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            first_name="John",
            last_name="Doe",
            role="teacher",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.role == "teacher"
        assert user.is_active is True
    
    def test_user_email_unique(self, db_session, test_admin_user):
        """Test that email must be unique."""
        duplicate_user = User(
            email="admin@schoolops.test",  # Same as test_admin_user
            hashed_password="hashed_password",
            first_name="Duplicate",
            last_name="User",
            role="admin"
        )
        
        with pytest.raises(IntegrityError):
            db_session.add(duplicate_user)
            db_session.commit()
    
    def test_user_default_values(self, db_session):
        """Test default values for user."""
        user = User(
            email="default@test.com",
            hashed_password="password",
            first_name="Default",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is True
        assert user.role == "user"  # Default role
        assert user.created_at is not None
    
    def test_user_repr(self, test_admin_user):
        """Test user string representation."""
        repr_str = repr(test_admin_user)
        assert "User" in repr_str
        assert test_admin_user.email in repr_str


class TestStudentModel:
    """Tests for Student model."""
    
    def test_create_student(self, db_session):
        """Test creating a basic student."""
        student = Student(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@school.com",
            admission_number="ADM001",
            date_of_birth="2010-05-15",
            gender="Female"
        )
        db_session.add(student)
        db_session.commit()
        
        assert student.id is not None
        assert student.admission_number == "ADM001"
        assert student.gender == "Female"
    
    def test_student_admission_number_unique(self, db_session, test_student):
        """Test that admission number must be unique."""
        duplicate = Student(
            first_name="Duplicate",
            last_name="Student",
            admission_number=test_student.admission_number  # Same as test_student
        )
        
        with pytest.raises(IntegrityError):
            db_session.add(duplicate)
            db_session.commit()
    
    def test_student_default_values(self, db_session):
        """Test default values for student."""
        student = Student(
            first_name="Default",
            last_name="Student",
            admission_number="DEF001"
        )
        db_session.add(student)
        db_session.commit()
        
        assert student.is_active is True
        assert student.attendance_percentage == 0.0
        assert student.created_at is not None


class TestTeacherModel:
    """Tests for Teacher model."""
    
    def test_create_teacher(self, db_session, test_teacher):
        """Test creating a teacher."""
        assert test_teacher.id is not None
        assert test_teacher.email == "teacher@schoolops.test"
        assert test_teacher.subject == "Mathematics"
    
    def test_teacher_email_unique(self, db_session, test_teacher):
        """Test that teacher email must be unique."""
        duplicate = Teacher(
            email=test_teacher.email,
            first_name="Duplicate",
            last_name="Teacher"
        )
        
        with pytest.raises(IntegrityError):
            db_session.add(duplicate)
            db_session.commit()


class TestClassModel:
    """Tests for Class model."""
    
    def test_create_class(self, db_session, test_class):
        """Test creating a class."""
        assert test_class.id is not None
        assert test_class.name == "Class 10"
    
    def test_class_with_academic_year(self, db_session, test_class, test_academic_year):
        """Test class relationship with academic year."""
        assert test_class.academic_year_id == test_academic_year.id
        assert test_class.academic_year.name == "2024-2025"


class TestAcademicYearModel:
    """Tests for AcademicYear model."""
    
    def test_create_academic_year(self, db_session, test_academic_year):
        """Test creating an academic year."""
        assert test_academic_year.id is not None
        assert test_academic_year.name == "2024-2025"
        assert test_academic_year.is_active is True
    
    def test_academic_year_dates(self, db_session):
        """Test academic year date validation."""
        year = AcademicYear(
            name="2025-2026",
            start_date="2025-04-01",
            end_date="2026-03-31",
            is_active=False
        )
        db_session.add(year)
        db_session.commit()
        
        assert year.start_date == "2025-04-01"
        assert year.end_date == "2026-03-31"


class TestAttendanceModel:
    """Tests for Attendance model."""
    
    def test_create_attendance(self, db_session, test_student, test_class):
        """Test creating an attendance record."""
        attendance = Attendance(
            student_id=test_student.id,
            class_id=test_class.id,
            date="2024-10-15",
            status="Present",
            marked_by="admin@schoolops.test"
        )
        db_session.add(attendance)
        db_session.commit()
        
        assert attendance.id is not None
        assert attendance.status == "Present"
        assert attendance.student_id == test_student.id
    
    def test_attendance_status_enum(self, db_session, test_student, test_class):
        """Test attendance status values."""
        for status in ["Present", "Absent", "Late", "Excused"]:
            attendance = Attendance(
                student_id=test_student.id,
                class_id=test_class.id,
                date="2024-10-20",
                status=status
            )
            db_session.add(attendance)
            db_session.commit()
            assert attendance.status == status


class TestGradeModel:
    """Tests for Grade model."""
    
    def test_create_grade(self, db_session, test_student, test_class, test_teacher):
        """Test creating a grade record."""
        grade = Grade(
            student_id=test_student.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject="Mathematics",
            grade="A",
            score=95,
            max_score=100,
            assessment_type="Midterm",
            assessment_date="2024-10-15"
        )
        db_session.add(grade)
        db_session.commit()
        
        assert grade.id is not None
        assert grade.grade == "A"
        assert grade.score == 95


class TestFeeRecordModel:
    """Tests for FeeRecord model."""
    
    def test_create_fee_record(self, db_session, test_student):
        """Test creating a fee record."""
        fee = FeeRecord(
            student_id=test_student.id,
            fee_type="Tuition",
            amount=10000,
            due_date="2024-10-30",
            status="Pending"
        )
        db_session.add(fee)
        db_session.commit()
        
        assert fee.id is not None
        assert fee.amount == 10000
        assert fee.status == "Pending"
    
    def test_fee_status_enum(self, db_session, test_student):
        """Test fee status values."""
        for status in ["Pending", "Paid", "Overdue", "Waived"]:
            fee = FeeRecord(
                student_id=test_student.id,
                fee_type="Test Fee",
                amount=1000,
                status=status
            )
            db_session.add(fee)
            db_session.commit()
            assert fee.status == status
