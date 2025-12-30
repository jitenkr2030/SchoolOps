"""
SQLAlchemy database models for SchoolOps
Covers all core modules: SIS, Attendance, Academics, Finance, Transport, etc.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Boolean, 
    ForeignKey, Float, Enum, JSON, ManyToOne, OneToMany, ManyToMany
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


# Enums
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    PRINCIPAL = "principal"
    TEACHER = "teacher"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    TRANSPORT_MANAGER = "transport_manager"
    PARENT = "parent"
    STUDENT = "student"
    SUPPORT = "support"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatus(str, enum.Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIAL = "partial"


# ================== User & Authentication Models ==================

class User(Base):
    """Base user model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    school_users = relationship("SchoolUser", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class UserProfile(Base):
    """User profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    photo_url = Column(String(500))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")


# ================== School & Admin Models ==================

class School(Base):
    """School/Institution model"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
    logo_url = Column(String(500))
    timezone = Column(String(50), default="UTC")
    academic_year_start = Column(Integer, default=8)  # Month
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("SchoolUser", back_populates="school")
    academic_years = relationship("AcademicYear", back_populates="school")
    classes = relationship("Class", back_populates="school")
    students = relationship("Student", back_populates="school")
    staff = relationship("Staff", back_populates="school")


class SchoolUser(Base):
    """Many-to-many relationship between users and schools"""
    __tablename__ = "school_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    role = Column(String(100))  # Role within the school
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="school_users")
    school = relationship("School", back_populates="users")


class AcademicYear(Base):
    """Academic year management"""
    __tablename__ = "academic_years"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    name = Column(String(100), nullable=False)  # e.g., "2024-2025"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    school = relationship("School", back_populates="academic_years")
    terms = relationship("Term", back_populates="academic_year")


class Term(Base):
    """Academic terms/semesters"""
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    name = Column(String(100), nullable=False)  # e.g., "Fall 2024"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    term_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    academic_year = relationship("AcademicYear", back_populates="terms")


# ================== Student Information System (SIS) Models ==================

class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    admission_number = Column(String(50), unique=True, index=True)
    admission_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    roll_number = Column(String(20))
    status = Column(String(50), default="active")  # active, transferred, suspended, graduated
    house = Column(String(100))
    bus_route = Column(String(100))
    special_needs = Column(Text)
    health_info = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    school = relationship("School", back_populates="students")
    user = relationship("User")
    class_ = relationship("Class", back_populates="students")
    guardians = relationship("StudentGuardian", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    enrollments = relationship("SubjectEnrollment", back_populates="student")
    fee_records = relationship("FeeRecord", back_populates="student")
    academic_records = relationship("AcademicRecord", back_populates="student")


class Guardian(Base):
    """Parent/Guardian model"""
    __tablename__ = "guardians"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    occupation = Column(String(100))
    office_address = Column(Text)
    relationship = Column(String(50))  # father, mother, guardian
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    student_guardians = relationship("StudentGuardian", back_populates="guardian")


class StudentGuardian(Base):
    """Many-to-many relationship between students and guardians"""
    __tablename__ = "student_guardians"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    guardian_id = Column(Integer, ForeignKey("guardians.id"))
    is_emergency_contact = Column(Boolean, default=False)
    can_pickup = Column(Boolean, default=False)
    
    # Relationships
    student = relationship("Student", back_populates="guardians")
    guardian = relationship("Guardian", back_populates="student_guardians")


# ================== Class & Subject Models ==================

class Class(Base):
    """Class/Grade model"""
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    name = Column(String(100), nullable=False)  # e.g., "Grade 10-A"
    grade = Column(Integer)  # e.g., 10
    section = Column(String(10))  # e.g., "A"
    class_teacher_id = Column(Integer, ForeignKey("staff.id"))
    capacity = Column(Integer, default=40)
    room_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    school = relationship("School", back_populates="classes")
    students = relationship("Student", back_populates="class_")
    class_teacher = relationship("Staff", foreign_keys=[class_teacher_id])
    timetables = relationship("Timetable", back_populates="class_")
    subjects = relationship("ClassSubject", back_populates="class_")


class Subject(Base):
    """Subject model"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_elective = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    class_subjects = relationship("ClassSubject", back_populates="subject")
    teachers = relationship("SubjectTeacher", back_populates="subject")
    lessons = relationship("Lesson", back_populates="subject")


class ClassSubject(Base):
    """Many-to-many relationship between classes and subjects"""
    __tablename__ = "class_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    # Relationships
    class_ = relationship("Class", back_populates="subjects")
    subject = relationship("Subject", back_populates="class_subjects")


class SubjectTeacher(Base):
    """Subject teacher assignment"""
    __tablename__ = "subject_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Relationships
    staff = relationship("Staff", back_populates="subject_teachers")
    subject = relationship("Subject", back_populates="teachers")


# ================== Staff Models ==================

class Staff(Base):
    """Staff/Teacher model"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    employee_id = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department = Column(String(100))
    designation = Column(String(100))
    date_of_joining = Column(Date)
    qualification = Column(Text)
    experience_years = Column(Integer)
    status = Column(String(50), default="active")  # active, on_leave, terminated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    school = relationship("School", back_populates="staff")
    user = relationship("User")
    subject_teachers = relationship("SubjectTeacher", back_populates="staff")
    attendance_records = relationship("StaffAttendance", back_populates="staff")
    payroll = relationship("Payroll", back_populates="staff")


# ================== Attendance Models ==================

class Attendance(Base):
    """Student attendance record"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    marked_by = Column(Integer, ForeignKey("staff.id"))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")


class StaffAttendance(Base):
    """Staff attendance record"""
    __tablename__ = "staff_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"))
    date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(String(50), nullable=False)  # present, absent, late
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    staff = relationship("Staff", back_populates="attendance_records")


# ================== Timetable Models ==================

class Timetable(Base):
    """Timetable/Schedule model"""
    __tablename__ = "timetable"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    period_number = Column(Integer)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    room_number = Column(String(20))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    class_ = relationship("Class", back_populates="timetables")
    subject = relationship("Subject")


# ================== Academic & Assessment Models ==================

class Lesson(Base):
    """Lesson/Class session model"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    lesson_date = Column(Date)
    period = Column(Integer)
    ai_generated = Column(Boolean, default=False)
    ai_metadata = Column(JSON)  # AI-generated content metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="lessons")
    assignments = relationship("Assignment", back_populates="lesson")


class Assignment(Base):
    """Assignment/Homework model"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    max_marks = Column(Integer, default=100)
    assignment_type = Column(String(50))  # homework, quiz, project, exam
    ai_generated = Column(Boolean, default=False)
    ai_metadata = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="assignments")
    submissions = relationship("AssignmentSubmission", back_populates="assignment")


class AssignmentSubmission(Base):
    """Student assignment submission"""
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text)
    file_url = Column(String(500))
    marks = Column(Float)
    feedback = Column(Text)
    ai_graded = Column(Boolean, default=False)
    ai_feedback = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")


class SubjectEnrollment(Base):
    """Student subject enrollment (for elective subjects)"""
    __tablename__ = "subject_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    enrollment_date = Column(Date)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")


class AcademicRecord(Base):
    """Student academic record/grades"""
    __tablename__ = "academic_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    assessment_type = Column(String(100))
    marks = Column(Float)
    grade = Column(String(5))
    term_id = Column(Integer, ForeignKey("terms.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="academic_records")


# ================== Fee & Finance Models ==================

class FeeStructure(Base):
    """Fee structure/structure definition"""
    __tablename__ = "fee_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    frequency = Column(String(50))  # yearly, monthly, quarterly
    applicable_grades = Column(JSON)  # List of applicable grade levels
    due_date = Column(Date)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    records = relationship("FeeRecord", back_populates="fee_structure")


class FeeRecord(Base):
    """Individual student fee record"""
    __tablename__ = "fee_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id"))
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0)
    status = Column(Enum(FeeStatus), default=FeeStatus.PENDING)
    due_date = Column(Date)
    payment_date = Column(DateTime)
    payment_method = Column(String(50))
    concession_amount = Column(Float, default=0)
    concession_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="fee_records")
    fee_structure = relationship("FeeStructure", back_populates="records")
    payments = relationship("Payment", back_populates="fee_record")


class Payment(Base):
    """Payment transaction"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    fee_record_id = Column(Integer, ForeignKey("fee_records.id"))
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String(50))  # cash, card, bank_transfer, online
    transaction_id = Column(String(100))
    receipt_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fee_record = relationship("FeeRecord", back_populates="payments")


class Payroll(Base):
    """Staff payroll"""
    __tablename__ = "payroll"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"))
    month = Column(Integer)
    year = Column(Integer)
    basic_salary = Column(Float)
    allowances = Column(Float, default=0)
    deductions = Column(Float, default=0)
    net_salary = Column(Float)
    payment_date = Column(Date)
    payment_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    staff = relationship("Staff", back_populates="payroll")


# ================== Transport Models ==================

class TransportRoute(Base):
    """Transport route"""
    __tablename__ = "transport_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String(255), nullable=False)
    route_number = Column(String(50), unique=True)
    start_location = Column(String(255))
    end_location = Column(String(255)
    stops = Column(JSON)  # List of stops with coordinates
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Bus(Base):
    """School bus"""
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String(50), unique=True, index=True)
    registration_number = Column(String(100))
    capacity = Column(Integer)
    driver_name = Column(String(100))
    driver_phone = Column(String(20))
    route_id = Column(Integer, ForeignKey("transport_routes.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    route = relationship("TransportRoute")


class BusTracking(Base):
    """Bus GPS tracking data"""
    __tablename__ = "bus_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


# ================== Library Models ==================

class Book(Base):
    """Library book"""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(50), unique=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    publisher = Column(String(255))
    year = Column(Integer)
    edition = Column(String(50))
    category = Column(String(100))
    location = Column(String(100))  # Shelf number
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BookIssue(Base):
    """Book checkout/issue record"""
    __tablename__ = "book_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    issue_date = Column(Date)
    due_date = Column(Date)
    return_date = Column(Date)
    status = Column(String(50), default="issued")  # issued, returned, lost
    fine_amount = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================== Hostel Models ==================

class Hostel(Base):
    """Hostel/ dormitory"""
    __tablename__ = "hostels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    capacity = Column(Integer)
    warden_name = Column(String(100))
    warden_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HostelRoom(Base):
    """Hostel room"""
    __tablename__ = "hostel_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    room_number = Column(String(20))
    floor = Column(Integer)
    capacity = Column(Integer)
    occupied = Column(Integer, default=0)
    room_type = Column(String(50))  # single, double, triple
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hostel = relationship("Hostel")
    allocations = relationship("HostelAllocation", back_populates="room")


class HostelAllocation(Base):
    """Student hostel room allocation"""
    __tablename__ = "hostel_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    room_id = Column(Integer, ForeignKey("hostel_rooms.id"))
    allocation_date = Column(Date)
    bed_number = Column(String(10))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student")
    room = relationship("HostelRoom", back_populates="allocations")


# ================== Communication Models ==================

class Announcement(Base):
    """School announcement"""
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    priority = Column(String(50), default="normal")  # normal, urgent
    target_audience = Column(JSON)  # roles, classes
    published_by = Column(Integer, ForeignKey("users.id"))
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Message(Base):
    """Message/chat"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(255))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())


class Meeting(Base):
    """Parent-teacher meeting"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("staff.id"))
    parent_id = Column(Integer, ForeignKey("guardians.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    scheduled_date = Column(DateTime)
    duration = Column(Integer, default=30)  # minutes
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled
    meeting_link = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ================== AI & Analytics Models ==================

class AIInsight(Base):
    """AI-generated insights and predictions"""
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String(100))  # at_risk, enrollment_forecast, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_entity_type = Column(String(50))  # student, class, school
    target_entity_id = Column(Integer)
    confidence_score = Column(Float)
    recommendation = Column(Text)
    metadata = Column(JSON)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LearningPath(Base):
    """AI-generated personalized learning path"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    current_level = Column(String(50))
    target_level = Column(String(50))
    recommendations = Column(JSON)
    progress = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ================== Audit & Compliance Models ==================

class AuditLog(Base):
    """System audit log"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class DataRetentionPolicy(Base):
    """Data retention policy"""
    __tablename__ = "data_retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), nullable=False)
    retention_period_years = Column(Integer)
    deletion_date = Column(DateTime)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
