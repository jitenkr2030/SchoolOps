"""
GraphQL Schema Definition for SchoolOps
Using Strawberry GraphQL
"""

import strawberry
from typing import List, Optional
from datetime import datetime, date
from enum import Enum
from strawberry.types import Info

from app.models.models import (
    UserRole as UserRoleEnum,
    Gender as GenderEnum,
    AttendanceStatus as AttendanceStatusEnum,
    FeeStatus as FeeStatusEnum
)


# Enums
@strawberry.enum
class UserRole(Enum):
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


@strawberry.enum
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@strawberry.enum
class AttendanceStatus(Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


@strawberry.enum
class FeeStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    PARTIAL = "partial"


# Types
@strawberry.type
class UserType:
    id: int
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime


@strawberry.type
class UserProfileType:
    id: int
    user_id: int
    first_name: str
    last_name: str
    phone: Optional[str]
    email: Optional[str]
    photo_url: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[Gender]


@strawberry.type
class SchoolType:
    id: int
    name: str
    code: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_active: bool


@strawberry.type
class AcademicYearType:
    id: int
    school_id: int
    name: str
    start_date: date
    end_date: date
    is_current: bool


@strawberry.type
class ClassType:
    id: int
    school_id: int
    name: str
    grade: int
    section: Optional[str]
    capacity: int
    room_number: Optional[str]
    student_count: int


@strawberry.type
class StudentType:
    id: int
    admission_number: str
    first_name: str
    last_name: str
    email: Optional[str]
    grade: Optional[str]
    section: Optional[str]
    roll_number: Optional[str]
    attendance_rate: Optional[float]
    status: str


@strawberry.type
class StaffType:
    id: int
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    status: str


@strawberry.type
class SubjectType:
    id: int
    code: str
    name: str
    description: Optional[str]
    is_elective: bool


@strawberry.type
class AttendanceRecordType:
    id: int
    student_id: int
    student_name: str
    date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime]
    remarks: Optional[str]


@strawberry.type
class FeeStructureType:
    id: int
    name: str
    description: Optional[str]
    amount: float
    frequency: str
    due_date: Optional[date]


@strawberry.type
class FeeRecordType:
    id: int
    student_id: int
    student_name: str
    fee_name: str
    amount_due: float
    amount_paid: float
    status: FeeStatus
    due_date: date


@strawberry.type
class PaymentType:
    id: int
    fee_record_id: int
    amount: float
    payment_date: datetime
    payment_method: str
    receipt_number: str


@strawberry.type
class DashboardStatsType:
    total_students: int
    total_teachers: int
    attendance_rate: float
    fee_collection_rate: float
    monthly_enrollment: int
    monthly_revenue: float


@strawberry.type
class AIInsightType:
    id: int
    insight_type: str
    title: str
    description: str
    confidence_score: float
    recommendation: Optional[str]
    created_at: datetime


@strawberry.type
class TimetableEntryType:
    id: int
    class_name: str
    subject_name: str
    teacher_name: str
    day_of_week: int
    period_number: int
    start_time: str
    end_time: str
    room_number: Optional[str]


# Input Types
@strawberry.input
class StudentCreateInput:
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    grade: int
    section: str
    admission_date: Optional[date] = None


@strawberry.input
class AttendanceMarkInput:
    student_id: int
    class_id: int
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None


@strawberry.input
class FeePaymentInput:
    fee_record_id: int
    amount: float
    payment_method: str
    notes: Optional[str] = None


@strawberry.input
class AssignmentCreateInput:
    class_id: int
    subject_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    max_marks: int = 100


# Queries
@strawberry.type
class Query:
    @strawberry.field
    def school(self, info: Info, school_id: int) -> Optional[SchoolType]:
        """Get school by ID"""
        return None
    
    @strawberry.field
    def schools(self, info: Info) -> List[SchoolType]:
        """Get all schools"""
        return []
    
    @strawberry.field
    def students(
        self, 
        info: Info, 
        school_id: Optional[int] = None,
        grade: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[StudentType]:
        """Get students with filters"""
        return []
    
    @strawberry.field
    def student(self, info: Info, student_id: int) -> Optional[StudentType]:
        """Get student by ID"""
        return None
    
    @strawberry.field
    def teachers(
        self,
        info: Info,
        school_id: Optional[int] = None,
        department: Optional[str] = None
    ) -> List[StaffType]:
        """Get teachers/staff"""
        return []
    
    @strawberry.field
    def classes(
        self,
        info: Info,
        school_id: Optional[int] = None
    ) -> List[ClassType]:
        """Get all classes"""
        return []
    
    @strawberry.field
    def subjects(self, info: Info) -> List[SubjectType]:
        """Get all subjects"""
        return []
    
    @strawberry.field
    def attendance(
        self,
        info: Info,
        class_id: int,
        date: date
    ) -> List[AttendanceRecordType]:
        """Get attendance records for a class on a date"""
        return []
    
    @strawberry.field
    def fee_records(
        self,
        info: Info,
        student_id: Optional[int] = None,
        status: Optional[FeeStatus] = None
    ) -> List[FeeRecordType]:
        """Get fee records"""
        return []
    
    @strawberry.field
    def dashboard_stats(self, info: Info, school_id: int) -> DashboardStatsType:
        """Get dashboard statistics"""
        return DashboardStatsType(
            total_students=0,
            total_teachers=0,
            attendance_rate=0.0,
            fee_collection_rate=0.0,
            monthly_enrollment=0,
            monthly_revenue=0.0
        )
    
    @strawberry.field
    def ai_insights(
        self,
        info: Info,
        school_id: int,
        insight_type: Optional[str] = None
    ) -> List[AIInsightType]:
        """Get AI-generated insights"""
        return []
    
    @strawberry.field
    def timetable(
        self,
        info: Info,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        day_of_week: Optional[int] = None
    ) -> List[TimetableEntryType]:
        """Get timetable entries"""
        return []


# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_student(self, info: Info, input: StudentCreateInput) -> StudentType:
        """Create a new student"""
        return StudentType(
            id=1,
            admission_number="STU001",
            first_name=input.first_name,
            last_name=input.last_name,
            email=input.email,
            grade=str(input.grade),
            section=input.section,
            roll_number="1",
            attendance_rate=100.0,
            status="active"
        )
    
    @strawberry.mutation
    def mark_attendance(
        self,
        info: Info,
        records: List[AttendanceMarkInput]
    ) -> bool:
        """Mark attendance for multiple students"""
        return True
    
    @strawberry.mutation
    def process_payment(self, info: Info, input: FeePaymentInput) -> PaymentType:
        """Process a fee payment"""
        return PaymentType(
            id=1,
            fee_record_id=input.fee_record_id,
            amount=input.amount,
            payment_date=datetime.now(),
            payment_method=input.payment_method,
            receipt_number="RCP-001"
        )
    
    @strawberry.mutation
    def create_assignment(self, info: Info, input: AssignmentCreateInput) -> bool:
        """Create a new assignment"""
        return True
    
    @strawberry.mutation
    def update_student_class(
        self,
        info: Info,
        student_id: int,
        new_class_id: int
    ) -> bool:
        """Update student class assignment"""
        return True
    
    @strawberry.mutation
    def generate_ai_quiz(
        self,
        info: Info,
        subject_id: int,
        topic: str,
        difficulty: str,
        question_count: int
    ) -> bool:
        """Generate AI-powered quiz questions"""
        return True


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
