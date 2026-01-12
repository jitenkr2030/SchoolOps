"""
Academic API endpoints
Management of Classes, Subjects, Academic Years, and Terms
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.database import get_db
from app.schema.academic_schema import (
    AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse,
    TermCreate, TermResponse,
    ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    ClassSubjectAssign, SubjectTeacherAssign, ApiResponse, AcademicPaginatedResponse
)
from app.services.academic_service import (
    AcademicYearService, ClassService, SubjectService
)
from app.core.security import get_current_user, require_admin, require_staff


router = APIRouter(prefix="/academics", tags=["Academic Management"])


# ==================== Academic Year Endpoints ====================

@router.get("/years", response_model=List[AcademicYearResponse])
async def get_academic_years(
    school_id: int = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all academic years for a school.
    """
    service = AcademicYearService(db)
    years = await service.get_academic_years(school_id)
    
    result = await db.execute(
        select(AcademicYear)
        .where(AcademicYear.school_id == school_id)
        .order_by(AcademicYear.start_date.desc())
    )
    
    return result.scalars().all()


@router.get("/years/current", response_model=AcademicYearResponse)
async def get_current_academic_year(
    school_id: int = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the current active academic year.
    """
    service = AcademicYearService(db)
    year = await service.get_current_academic_year(school_id)
    
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current academic year set"
        )
    
    return year


@router.post("/years", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_year(
    year_data: AcademicYearCreate,
    school_id: int = Query(..., description="School ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new academic year.
    Requires admin privileges.
    """
    service = AcademicYearService(db)
    result = await service.create_academic_year(year_data, school_id)
    
    return ApiResponse(
        success=True,
        message="Academic year created",
        data=result
    )


@router.put("/years/{year_id}", response_model=ApiResponse)
async def update_academic_year(
    year_id: int,
    update_data: AcademicYearUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update academic year.
    Requires admin privileges.
    """
    from app.models.models import AcademicYear
    
    result = await db.execute(
        select(AcademicYear).where(AcademicYear.id == year_id)
    )
    year = result.scalar_one_or_none()
    
    if not year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Academic year not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(year, key, value)
    
    await db.commit()
    
    return ApiResponse(success=True, message="Academic year updated")


# ==================== Term Endpoints ====================

@router.post("/terms", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_term(
    term_data: TermCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new term/semester.
    Requires admin privileges.
    """
    service = AcademicYearService(db)
    result = await service.create_term(term_data)
    
    return ApiResponse(
        success=True,
        message="Term created",
        data=result
    )


@router.get("/terms/{year_id}", response_model=List[TermResponse])
async def get_terms_by_year(
    year_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all terms for an academic year.
    """
    from app.models.models import Term
    
    result = await db.execute(
        select(Term)
        .where(Term.academic_year_id == year_id)
        .order_by(Term.term_order)
    )
    
    return result.scalars().all()


# ==================== Class Endpoints ====================

@router.get("/classes", response_model=AcademicPaginatedResponse)
async def get_classes(
    school_id: Optional[int] = Query(None),
    grade: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of all classes/grades.
    """
    service = ClassService(db)
    return await service.get_class_list(school_id, grade, page, per_page)


@router.get("/classes/{class_id}", response_model=ApiResponse)
async def get_class_detail(
    class_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed class information with teacher and student count.
    """
    service = ClassService(db)
    class_obj = await service.get_class_detail(class_id)
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    return ApiResponse(
        success=True,
        message="Class details retrieved",
        data=class_obj
    )


@router.post("/classes", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new class/grade.
    Requires admin privileges.
    """
    service = ClassService(db)
    
    try:
        result = await service.create_class(class_data)
        return ApiResponse(
            success=True,
            message="Class created",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/classes/{class_id}", response_model=ApiResponse)
async def update_class(
    class_id: int,
    update_data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update class information.
    Requires admin privileges.
    """
    service = ClassService(db)
    
    try:
        return await service.update_class(class_id, update_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== Subject Endpoints ====================

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of all subjects.
    """
    service = SubjectService(db)
    subjects = await service.get_subject_list(is_active)
    
    # Return as SubjectResponse objects
    from app.models.models import Subject
    result = await db.execute(
        select(Subject)
        .where(Subject.is_active == is_active)
        .order_by(Subject.name)
    )
    
    return result.scalars().all()


@router.post("/subjects", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Create a new subject.
    Requires admin privileges.
    """
    service = SubjectService(db)
    result = await service.create_subject(subject_data)
    
    return ApiResponse(
        success=True,
        message="Subject created",
        data=result
    )


@router.put("/subjects/{subject_id}", response_model=ApiResponse)
async def update_subject(
    subject_id: int,
    update_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Update subject information.
    Requires admin privileges.
    """
    from app.models.models import Subject
    
    result = await db.execute(
        select(Subject).where(Subject.id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(subject, key, value)
    
    await db.commit()
    
    return ApiResponse(success=True, message="Subject updated")


# ==================== Assignment Endpoints ====================

@router.post("/classes/assign-subject", response_model=ApiResponse)
async def assign_subject_to_class(
    assignment: ClassSubjectAssign,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Assign a subject to a class.
    Requires admin privileges.
    """
    service = SubjectService(db)
    
    try:
        return await service.assign_subject_to_class(assignment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/subjects/assign-teacher", response_model=ApiResponse)
async def assign_teacher_to_subject(
    assignment: SubjectTeacherAssign,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """
    Assign a teacher to teach a subject in a class.
    Requires admin privileges.
    """
    service = SubjectService(db)
    
    try:
        return await service.assign_teacher_to_subject(assignment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/subjects/assignments/{staff_id}", response_model=ApiResponse)
async def get_teacher_assignments(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all subject/class assignments for a teacher.
    """
    service = SubjectService(db)
    assignments = await service.get_subject_assignments(staff_id)
    
    return ApiResponse(
        success=True,
        message="Assignments retrieved",
        data={"assignments": assignments}
    )
