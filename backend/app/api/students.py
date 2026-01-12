"""
Student API endpoints
Implements comprehensive CRUD operations for Student Information System (SIS)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import date

from app.db.database import get_db
from app.schema.student_schema import (
    StudentCreate, StudentUpdate, StudentResponse, StudentListResponse,
    StudentFilter, GuardianCreate, GuardianResponse, StudentGuardianLink,
    ApiResponse, PaginatedResponse
)
from app.models.models import (
    User, UserProfile, Student, Class, School, Guardian, 
    StudentGuardian, Attendance, UserRole
)

# Student router
router = APIRouter(prefix="/students", tags=["Students"])


async def generate_admission_number(db: AsyncSession, school_id: int) -> str:
    """Generate unique admission number for school"""
    # Get count of existing students in school
    result = await db.execute(
        select(func.count(Student.id)).where(Student.school_id == school_id)
    )
    count = result.scalar() or 0
    
    # Format: SCH-{YEAR}-{NUMBER}
    year = date.today().year
    admission_number = f"SCH-{year}-{str(count + 1).zfill(5)}"
    
    return admission_number


@router.get("", response_model=PaginatedResponse)
async def get_students(
    school_id: Optional[int] = Query(None, description="Filter by school ID"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    grade: Optional[int] = Query(None, description="Filter by grade level"),
    section: Optional[str] = Query(None, description="Filter by section"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name, email, admission_number"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of students with optional filters
    
    Supports filtering by school, class, grade, section, status.
    Supports search across name, email, and admission number.
    """
    # Build query
    query = (
        select(Student, User, UserProfile, Class)
        .outerjoin(User, Student.user_id == User.id)
        .outerjoin(UserProfile, User.id == UserProfile.user_id)
        .outerjoin(Class, Student.class_id == Class.id)
    )
    
    # Apply filters
    if school_id:
        query = query.where(Student.school_id == school_id)
    if class_id:
        query = query.where(Student.class_id == class_id)
    if grade:
        query = query.where(Class.grade == grade)
    if section:
        query = query.where(Class.section == section)
    if status:
        query = query.where(Student.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                UserProfile.first_name.ilike(search_term),
                UserProfile.last_name.ilike(search_term),
                User.email.ilike(search_term),
                Student.admission_number.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    rows = result.all()
    
    # Build response
    students = []
    for student, user, profile, class_ in rows:
        # Calculate attendance rate (placeholder - implement actual calculation)
        attendance_rate = 95.0  # Placeholder
        
        students.append({
            "id": student.id,
            "admission_number": student.admission_number,
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "email": user.email if user else "",
            "class_name": class_.name if class_ else None,
            "grade": class_.grade if class_ else None,
            "section": class_.section if class_ else None,
            "roll_number": student.roll_number,
            "status": student.status,
            "attendance_rate": attendance_rate
        })
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        success=True,
        message="Students retrieved successfully",
        data=students,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information for a specific student
    
    Returns complete student profile including personal details,
    class information, guardians, and academic records.
    """
    # Query student with relationships
    result = await db.execute(
        select(Student, User, UserProfile, Class, School)
        .outerjoin(User, Student.user_id == User.id)
        .outerjoin(UserProfile, User.id == UserProfile.user_id)
        .outerjoin(Class, Student.class_id == Class.id)
        .outerjoin(School, Student.school_id == School.id)
        .where(Student.id == student_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student, user, profile, class_, school = row
    
    return StudentResponse(
        id=student.id,
        school_id=student.school_id,
        admission_number=student.admission_number,
        admission_date=student.admission_date,
        user_id=student.user_id,
        class_id=student.class_id,
        status=student.status,
        roll_number=student.roll_number,
        house=student.house,
        bus_route=student.bus_route,
        special_needs=student.special_needs,
        health_info=student.health_info,
        created_at=student.created_at,
        updated_at=student.updated_at,
        first_name=profile.first_name if profile else "",
        last_name=profile.last_name if profile else "",
        email=user.email if user else "",
        phone=profile.phone if profile else None,
        date_of_birth=profile.date_of_birth if profile else None,
        gender=profile.gender if profile else None,
        class_name=class_.name if class_ else None,
        grade=class_.grade if class_ else None,
        section=class_.section if class_ else None
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student_data: StudentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new student with user account
    
    Creates both User, UserProfile, and Student records.
    Generates unique admission number automatically.
    """
    # Verify school exists
    school_result = await db.execute(select(School).where(School.id == student_data.school_id))
    if not school_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School not found"
        )
    
    # Verify class exists
    class_result = await db.execute(select(Class).where(Class.id == student_data.class_id))
    if not class_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class not found"
        )
    
    # Check if email already exists
    email_result = await db.execute(select(User).where(User.email == student_data.email))
    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(student_data.password)
    
    # Create user account
    db_user = User(
        email=student_data.email,
        password_hash=hashed_password,
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    await db.flush()
    
    # Create user profile
    db_profile = UserProfile(
        user_id=db_user.id,
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        phone=student_data.phone,
        address=student_data.address,
        date_of_birth=student_data.date_of_birth,
        gender=student_data.gender
    )
    db.add(db_profile)
    
    # Generate admission number
    admission_number = await generate_admission_number(db, student_data.school_id)
    
    # Create student record
    db_student = Student(
        school_id=student_data.school_id,
        admission_number=admission_number,
        admission_date=student_data.admission_date or date.today(),
        user_id=db_user.id,
        class_id=student_data.class_id,
        roll_number=student_data.roll_number,
        status="active",
        house=student_data.house,
        bus_route=student_data.bus_route,
        special_needs=student_data.special_needs,
        health_info=student_data.health_info
    )
    db.add(db_student)
    
    await db.commit()
    await db.refresh(db_student)
    
    return ApiResponse(
        success=True,
        message="Student created successfully",
        data={
            "student_id": db_student.id,
            "admission_number": db_student.admission_number,
            "user_id": db_user.id,
            "email": db_user.email
        }
    )


@router.put("/{student_id}", response_model=ApiResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update student information
    
    Supports partial updates - only provided fields will be updated.
    """
    # Get student
    result = await db.execute(select(Student).where(Student.id == student_id))
    db_student = result.scalar_one_or_none()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get user profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == db_student.user_id)
    )
    db_profile = profile_result.scalar_one_or_none()
    
    # Build update data
    update_data = student_data.model_dump(exclude_unset=True)
    
    # Update student fields
    student_fields = ['class_id', 'roll_number', 'status', 'house', 'bus_route', 
                      'special_needs', 'health_info']
    student_update = {k: v for k, v in update_data.items() if k in student_fields}
    
    if student_update:
        await db.execute(
            update(Student).where(Student.id == student_id).values(**student_update)
        )
    
    # Update profile fields
    profile_fields = ['first_name', 'last_name', 'phone', 'address', 
                      'date_of_birth', 'gender']
    profile_update = {k: v for k, v in update_data.items() if k in profile_fields}
    
    if profile_update and db_profile:
        await db.execute(
            update(UserProfile).where(UserProfile.id == db_profile.id).values(**profile_update)
        )
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="Student updated successfully"
    )


@router.delete("/{student_id}", response_model=ApiResponse)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a student (soft delete by changing status to 'transferred')
    
    Note: For GDPR compliance, consider implementing hard delete with
    data anonymization instead of actual deletion.
    """
    result = await db.execute(select(Student).where(Student.id == student_id))
    db_student = result.scalar_one_or_none()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Soft delete - change status instead of deleting
    await db.execute(
        update(Student).where(Student.id == student_id).values(status="transferred")
    )
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="Student transferred successfully (status updated)"
    )


@router.get("/{student_id}/guardians", response_model=ApiResponse)
async def get_student_guardians(student_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all guardians for a specific student
    """
    # Verify student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get guardians
    guardians_result = await db.execute(
        select(Guardian, User, UserProfile, StudentGuardian)
        .join(User, Guardian.user_id == User.id)
        .join(UserProfile, User.id == UserProfile.user_id)
        .join(StudentGuardian, Guardian.id == StudentGuardian.guardian_id)
        .where(StudentGuardian.student_id == student_id)
    )
    
    guardians = []
    for guardian, user, profile, link in guardians_result:
        guardians.append({
            "id": guardian.id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": user.email,
            "phone": profile.phone,
            "relationship": guardian.relationship,
            "is_primary": link.is_emergency_contact,
            "can_pickup": link.can_pickup,
            "is_emergency_contact": link.is_emergency_contact
        })
    
    return ApiResponse(
        success=True,
        message="Guardians retrieved successfully",
        data={"guardians": guardians}
    )


@router.post("/{student_id}/guardians", response_model=ApiResponse)
async def add_guardian(
    student_id: int,
    guardian_data: GuardianCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a guardian to a student
    
    Creates new guardian account and links to student.
    """
    # Verify student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if guardian email exists
    email_result = await db.execute(select(User).where(User.email == guardian_data.email))
    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(guardian_data.password)
    
    # Create guardian user
    db_user = User(
        email=guardian_data.email,
        password_hash=hashed_password,
        role=UserRole.PARENT,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    await db.flush()
    
    # Create guardian profile
    db_profile = UserProfile(
        user_id=db_user.id,
        first_name=guardian_data.first_name,
        last_name=guardian_data.last_name,
        phone=guardian_data.phone,
        address=guardian_data.address
    )
    db.add(db_profile)
    
    # Create guardian record
    db_guardian = Guardian(
        user_id=db_user.id,
        occupation=guardian_data.occupation,
        office_address=guardian_data.office_address,
        relationship=guardian_data.relationship,
        is_primary=guardian_data.is_primary
    )
    db.add(db_guardian)
    await db.flush()
    
    # Link student to guardian
    db_link = StudentGuardian(
        student_id=student_id,
        guardian_id=db_guardian.id,
        is_emergency_contact=guardian_data.is_emergency_contact,
        can_pickup=guardian_data.can_pickup
    )
    db.add(db_link)
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        message="Guardian added successfully",
        data={"guardian_id": db_guardian.id}
    )


@router.get("/{student_id}/attendance", response_model=ApiResponse)
async def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get attendance records for a student
    
    Supports date range filtering.
    """
    # Verify student exists
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Build query
    query = select(Attendance).where(Attendance.student_id == student_id)
    
    if start_date:
        query = query.where(Attendance.date >= start_date)
    if end_date:
        query = query.where(Attendance.date <= end_date)
    
    query = query.order_by(Attendance.date.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # Calculate attendance rate
    total = len(records)
    present = sum(1 for r in records if r.status.value == "present")
    rate = (present / total * 100) if total > 0 else 100.0
    
    attendance_data = [{
        "id": r.id,
        "date": r.date,
        "status": r.status.value,
        "check_in_time": r.check_in_time,
        "remarks": r.remarks
    } for r in records]
    
    return ApiResponse(
        success=True,
        message="Attendance records retrieved successfully",
        data={
            "attendance_records": attendance_data,
            "total_days": total,
            "present_days": present,
            "absent_days": total - present,
            "attendance_rate": round(rate, 2)
        }
    )
