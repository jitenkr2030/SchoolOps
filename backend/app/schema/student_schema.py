"""
Pydantic schemas for Student operations
Comprehensive schemas for Student Information System (SIS) CRUD operations
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentStatusEnum(str, Enum):
    ACTIVE = "active"
    TRANSFERRED = "transferred"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"


# ==================== Student Schemas ====================

class StudentBase(BaseModel):
    """Base student schema with common fields"""
    admission_number: Optional[str] = None
    roll_number: Optional[str] = Field(None, max_length=20)
    house: Optional[str] = Field(None, max_length=100)
    bus_route: Optional[str] = Field(None, max_length=100)
    special_needs: Optional[str] = None
    health_info: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    # User/Profile information
    email: EmailStr = Field(..., description="Student email address")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    
    # Academic information
    school_id: int = Field(..., description="School ID")
    class_id: int = Field(..., description="Class/Grade ID")
    admission_date: Optional[date] = Field(None, description="Date of admission")
    
    # Login password for student account
    password: str = Field(..., min_length=8, max_length=128, description="Initial password")


class StudentUpdate(BaseModel):
    """Schema for updating student information"""
    # Academic information
    class_id: Optional[int] = Field(None, description="New class ID")
    roll_number: Optional[str] = Field(None, max_length=20)
    status: Optional[StudentStatusEnum] = Field(None, description="Student status")
    house: Optional[str] = Field(None, max_length=100)
    bus_route: Optional[str] = Field(None, max_length=100)
    special_needs: Optional[str] = None
    health_info: Optional[str] = None
    
    # Profile information
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    school_id: int
    admission_number: Optional[str]
    admission_date: Optional[date]
    user_id: int
    class_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Profile data (from joined UserProfile)
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    
    # Class information
    class_name: Optional[str]
    grade: Optional[int]
    section: Optional[str]
    
    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    """Schema for paginated student list"""
    id: int
    admission_number: Optional[str]
    first_name: str
    last_name: str
    email: str
    class_name: Optional[str]
    grade: Optional[int]
    section: Optional[str]
    roll_number: Optional[str]
    status: str
    attendance_rate: Optional[float] = None
    
    class Config:
        from_attributes = True


# ==================== Guardian/Parent Schemas ====================

class GuardianCreate(BaseModel):
    """Schema for creating a guardian/parent"""
    email: EmailStr = Field(..., description="Guardian email")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., max_length=20)
    address: Optional[str] = None
    occupation: Optional[str] = Field(None, max_length=100)
    office_address: Optional[str] = None
    relationship: str = Field(..., description="father, mother, guardian")
    is_primary: bool = Field(False, description="Primary contact")
    can_pickup: bool = Field(False, description="Authorized for pickup")
    is_emergency_contact: bool = Field(False, description="Emergency contact")
    password: str = Field(..., min_length=8, max_length=128)


class GuardianResponse(BaseModel):
    """Schema for guardian response"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    occupation: Optional[str]
    relationship: str
    is_primary: bool
    can_pickup: bool
    is_emergency_contact: bool
    
    class Config:
        from_attributes = True


class StudentGuardianLink(BaseModel):
    """Schema for linking student to guardian"""
    student_id: int
    guardian_id: int
    is_emergency_contact: bool = False
    can_pickup: bool = False


# ==================== Filter Schemas ====================

class StudentFilter(BaseModel):
    """Schema for filtering students"""
    school_id: Optional[int] = None
    class_id: Optional[int] = None
    grade: Optional[int] = None
    section: Optional[str] = None
    status: Optional[StudentStatusEnum] = None
    search: Optional[str] = Field(None, description="Search in name, email, admission_number")
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


# ==================== Bulk Operations ====================

class BulkStudentCreate(BaseModel):
    """Schema for bulk student creation via CSV/Excel"""
    students: List[StudentCreate]


class BulkStudentUpdate(BaseModel):
    """Schema for bulk student updates"""
    student_ids: List[int]
    update_data: StudentUpdate


class StudentTransfer(BaseModel):
    """Schema for student class transfer"""
    student_ids: List[int]
    new_class_id: int
    effective_date: date
