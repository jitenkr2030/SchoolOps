"""
Pydantic schemas for Staff and Academic Management
Comprehensive schemas for Staff, Classes, Subjects, and Academic Years
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class StaffRoleEnum(str, Enum):
    """Staff role enumeration"""
    TEACHER = "teacher"
    PRINCIPAL = "principal"
    VICE_PRINCIPAL = "vice_principal"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    TRANSPORT_MANAGER = "transport_manager"
    ADMIN_STAFF = "admin_staff"
    COUNSELOR = "counselor"


class StaffStatusEnum(str, Enum):
    """Staff employment status"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    RESIGNED = "resigned"


# ==================== Staff Schemas ====================

class StaffBase(BaseModel):
    """Base staff schema"""
    employee_id: str = Field(..., max_length=50, description="Unique employee ID")
    department: Optional[str] = Field(None, max_length=100)
    designation: str = Field(..., max_length=100)
    date_of_joining: Optional[date] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    status: StaffStatusEnum = StaffStatusEnum.ACTIVE


class StaffCreate(StaffBase):
    """Schema for creating staff member"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=128)


class StaffUpdate(BaseModel):
    """Schema for updating staff member"""
    department: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Optional[date] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    status: Optional[StaffStatusEnum] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class StaffResponse(StaffBase):
    """Schema for staff response"""
    id: int
    school_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # Profile data
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    
    class Config:
        from_attributes = True


class StaffListResponse(BaseModel):
    """Staff list item"""
    id: int
    employee_id: str
    first_name: str
    last_name: str
    email: str
    designation: str
    department: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


class StaffFilter(BaseModel):
    """Schema for filtering staff"""
    school_id: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[StaffStatusEnum] = None
    role: Optional[StaffRoleEnum] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


# ==================== Academic Year Schemas ====================

class AcademicYearCreate(BaseModel):
    """Schema for creating academic year"""
    name: str = Field(..., max_length=100, description="e.g., 2024-2025")
    start_date: date
    end_date: date
    is_current: bool = False


class AcademicYearResponse(BaseModel):
    """Schema for academic year response"""
    id: int
    school_id: int
    name: str
    start_date: date
    end_date: date
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AcademicYearUpdate(BaseModel):
    """Schema for updating academic year"""
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None


# ==================== Term Schemas ====================

class TermCreate(BaseModel):
    """Schema for creating term/semester"""
    academic_year_id: int
    name: str = Field(..., max_length=100, description="e.g., Fall 2024")
    start_date: date
    end_date: date
    term_order: int = Field(1, ge=1)


class TermResponse(BaseModel):
    """Schema for term response"""
    id: int
    academic_year_id: int
    name: str
    start_date: date
    end_date: date
    term_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Class/Grade Schemas ====================

class ClassCreate(BaseModel):
    """Schema for creating class/grade"""
    school_id: int
    name: str = Field(..., max_length=100, description="e.g., Grade 10-A")
    grade: int = Field(..., ge=1, le=12)
    section: Optional[str] = Field(None, max_length=10)
    capacity: int = Field(default=40, ge=1)
    room_number: Optional[str] = Field(None, max_length=20)
    class_teacher_id: Optional[int] = None


class ClassUpdate(BaseModel):
    """Schema for updating class"""
    name: Optional[str] = None
    grade: Optional[int] = None
    section: Optional[str] = None
    capacity: Optional[int] = None
    room_number: Optional[str] = None
    class_teacher_id: Optional[int] = None
    is_active: Optional[bool] = None


class ClassResponse(BaseModel):
    """Schema for class response"""
    id: int
    school_id: int
    name: str
    grade: int
    section: Optional[str]
    capacity: int
    room_number: Optional[str]
    class_teacher_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClassDetailResponse(ClassResponse):
    """Detailed class response with teacher and student count"""
    class_teacher_name: Optional[str]
    student_count: int
    
    class Config:
        from_attributes = True


# ==================== Subject Schemas ====================

class SubjectCreate(BaseModel):
    """Schema for creating subject"""
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_elective: bool = False
    is_active: bool = True


class SubjectUpdate(BaseModel):
    """Schema for updating subject"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_elective: Optional[bool] = None
    is_active: Optional[bool] = None


class SubjectResponse(BaseModel):
    """Schema for subject response"""
    id: int
    code: str
    name: str
    description: Optional[str]
    is_elective: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Class-Subject Linking Schemas ====================

class ClassSubjectAssign(BaseModel):
    """Schema for assigning subject to class"""
    class_id: int
    subject_id: int


class ClassSubjectResponse(BaseModel):
    """Class-Subject response"""
    id: int
    class_id: int
    subject_id: int
    class_name: str
    subject_name: str
    
    class Config:
        from_attributes = True


# ==================== Subject Teacher Assignment Schemas ====================

class SubjectTeacherAssign(BaseModel):
    """Schema for assigning teacher to subject in a class"""
    staff_id: int
    subject_id: int
    class_id: int


class SubjectTeacherResponse(BaseModel):
    """Subject teacher assignment response"""
    id: int
    staff_id: int
    subject_id: int
    class_id: int
    staff_name: str
    subject_name: str
    class_name: str
    
    class Config:
        from_attributes = True


# ==================== API Response Schemas ====================

class AcademicPaginatedResponse(BaseModel):
    """Paginated response for academic endpoints"""
    success: bool
    message: str
    data: list
    total: int
    page: int
    per_page: int
    total_pages: int


class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    message: str
    data: Optional[dict] = None
