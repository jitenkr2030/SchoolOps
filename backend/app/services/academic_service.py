"""
Staff and Academic Services

Business logic for Staff management and Academic configuration.
"""

from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import (
    Staff, User, UserProfile, UserRole, AcademicYear, Term, Class,
    Subject, ClassSubject, SubjectTeacher, School
)
from app.schema.academic_schema import (
    StaffCreate, StaffUpdate, AcademicYearCreate, AcademicYearUpdate,
    ClassCreate, ClassUpdate, SubjectCreate, SubjectUpdate,
    TermCreate, ClassSubjectAssign, SubjectTeacherAssign
)


class StaffService:
    """Service for staff management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_staff(self, staff_data: StaffCreate, school_id: int) -> dict:
        """Create a new staff member"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Check if email exists
        email_result = await self.db.execute(
            select(User).where(User.email == staff_data.email)
        )
        if email_result.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # Map role string to enum
        role_map = {
            "teacher": UserRole.TEACHER,
            "principal": UserRole.PRINCIPAL,
            "accountant": UserRole.ACCOUNTANT,
            "librarian": UserRole.LIBRARIAN,
            "transport_manager": UserRole.TRANSPORT_MANAGER,
            "admin_staff": UserRole.SUPPORT,
            "counselor": UserRole.SUPPORT,
        }
        role = role_map.get(staff_data.designation.lower(), UserRole.TEACHER)
        
        # Create user
        hashed_password = pwd_context.hash(staff_data.password)
        user = User(
            email=staff_data.email,
            password_hash=hashed_password,
            role=role,
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        await self.db.flush()
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            first_name=staff_data.first_name,
            last_name=staff_data.last_name,
            phone=staff_data.phone,
            address=staff_data.address,
            date_of_birth=staff_data.date_of_birth,
            gender=staff_data.gender
        )
        self.db.add(profile)
        
        # Create staff record
        staff = Staff(
            school_id=school_id,
            employee_id=staff_data.employee_id,
            user_id=user.id,
            department=staff_data.department,
            designation=staff_data.designation,
            date_of_joining=staff_data.date_of_joining,
            qualification=staff_data.qualification,
            experience_years=staff_data.experience_years,
            status=staff_data.status.value if hasattr(staff_data.status, 'value') else staff_data.status
        )
        self.db.add(staff)
        await self.db.commit()
        await self.db.refresh(staff)
        
        return {"staff_id": staff.id, "user_id": user.id, "email": user.email}
    
    async def get_staff_list(
        self,
        school_id: Optional[int] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """Get paginated staff list"""
        query = (
            select(Staff, User, UserProfile)
            .join(User, Staff.user_id == User.id)
            .join(UserProfile, User.id == UserProfile.user_id)
        )
        
        if school_id:
            query = query.where(Staff.school_id == school_id)
        if department:
            query = query.where(Staff.department == department)
        if status:
            query = query.where(Staff.status == status)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    UserProfile.first_name.ilike(search_term),
                    UserProfile.last_name.ilike(search_term),
                    Staff.employee_id.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        rows = result.all()
        
        staff_list = []
        for staff, user, profile in rows:
            staff_list.append({
                "id": staff.id,
                "employee_id": staff.employee_id,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "email": user.email,
                "designation": staff.designation,
                "department": staff.department,
                "status": staff.status
            })
        
        return {
            "success": True,
            "data": staff_list,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    async def get_staff_detail(self, staff_id: int) -> Optional[dict]:
        """Get detailed staff information"""
        result = await self.db.execute(
            select(Staff, User, UserProfile, School)
            .join(User, Staff.user_id == User.id)
            .join(UserProfile, User.id == UserProfile.user_id)
            .outerjoin(School, Staff.school_id == School.id)
            .where(Staff.id == staff_id)
        )
        row = result.first()
        
        if not row:
            return None
        
        staff, user, profile, school = row
        
        # Get assigned subjects
        subject_result = await self.db.execute(
            select(SubjectTeacher, Subject, Class)
            .join(Subject, SubjectTeacher.subject_id == Subject.id)
            .join(Class, SubjectTeacher.class_id == Class.id)
            .where(SubjectTeacher.staff_id == staff_id)
        )
        assignments = []
        for st, subj, cls in subject_result.all():
            assignments.append({
                "subject_id": subj.id,
                "subject_name": subj.name,
                "class_id": cls.id,
                "class_name": cls.name
            })
        
        return {
            "id": staff.id,
            "employee_id": staff.employee_id,
            "school_name": school.name if school else None,
            "email": user.email,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "phone": profile.phone,
            "designation": staff.designation,
            "department": staff.department,
            "qualification": staff.qualification,
            "experience_years": staff.experience_years,
            "date_of_joining": staff.date_of_joining,
            "status": staff.status,
            "subject_assignments": assignments
        }
    
    async def update_staff(self, staff_id: int, update_data: StaffUpdate) -> dict:
        """Update staff member"""
        result = await self.db.execute(
            select(Staff).where(Staff.id == staff_id)
        )
        staff = result.scalar_one_or_none()
        
        if not staff:
            raise ValueError("Staff not found")
        
        # Update staff fields
        staff_data = update_data.model_dump(exclude_unset=True)
        for key, value in staff_data.items():
            setattr(staff, key, value)
        
        await self.db.commit()
        
        return {"success": True, "message": "Staff updated successfully"}
    
    async def get_staff_by_user_id(self, user_id: int) -> Optional[Staff]:
        """Get staff record by user ID"""
        result = await self.db.execute(
            select(Staff).where(Staff.user_id == user_id)
        )
        return result.scalar_one_or_none()


class AcademicYearService:
    """Service for academic year management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_academic_year(self, year_data: AcademicYearCreate, school_id: int) -> dict:
        """Create academic year"""
        # If setting as current, unset others
        if year_data.is_current:
            await self.db.execute(
                select(AcademicYear)
                .where(AcademicYear.school_id == school_id)
                .values(is_current=False)
            )
        
        year = AcademicYear(
            school_id=school_id,
            name=year_data.name,
            start_date=year_data.start_date,
            end_date=year_data.end_date,
            is_current=year_data.is_current
        )
        self.db.add(year)
        await self.db.commit()
        await self.db.refresh(year)
        
        return {"academic_year_id": year.id, "name": year.name}
    
    async def get_academic_years(self, school_id: int) -> list:
        """Get all academic years for a school"""
        result = await self.db.execute(
            select(AcademicYear)
            .where(AcademicYear.school_id == school_id)
            .order_by(AcademicYear.start_date.desc())
        )
        return [row[0].id for row in result.all()]
    
    async def get_current_academic_year(self, school_id: int) -> Optional[AcademicYear]:
        """Get current academic year"""
        result = await self.db.execute(
            select(AcademicYear)
            .where(
                and_(
                    AcademicYear.school_id == school_id,
                    AcademicYear.is_current == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_term(self, term_data: TermCreate) -> dict:
        """Create term/semester"""
        term = Term(
            academic_year_id=term_data.academic_year_id,
            name=term_data.name,
            start_date=term_data.start_date,
            end_date=term_data.end_date,
            term_order=term_data.term_order
        )
        self.db.add(term)
        await self.db.commit()
        await self.db.refresh(term)
        
        return {"term_id": term.id, "name": term.name}


class ClassService:
    """Service for class management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_class(self, class_data: ClassCreate) -> dict:
        """Create a new class/grade"""
        class_obj = Class(
            school_id=class_data.school_id,
            name=class_data.name,
            grade=class_data.grade,
            section=class_data.section,
            capacity=class_data.capacity,
            room_number=class_data.room_number,
            class_teacher_id=class_data.class_teacher_id,
            is_active=True
        )
        self.db.add(class_obj)
        await self.db.commit()
        await self.db.refresh(class_obj)
        
        return {"class_id": class_obj.id, "name": class_obj.name}
    
    async def get_class_list(
        self,
        school_id: Optional[int] = None,
        grade: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """Get paginated class list"""
        query = select(Class)
        
        if school_id:
            query = query.where(Class.school_id == school_id)
        if grade:
            query = query.where(Class.grade == grade)
        
        # Count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        classes = result.scalars().all()
        
        return {
            "success": True,
            "data": [{"id": c.id, "name": c.name, "grade": c.grade, "section": c.section} for c in classes],
            "total": total,
            "page": page,
            "per_page": per_page
        }
    
    async def get_class_detail(self, class_id: int) -> Optional[dict]:
        """Get detailed class information with teacher and student count"""
        result = await self.db.execute(
            select(Class)
            .options(selectinload(Class.class_teacher))
            .where(Class.id == class_id)
        )
        class_obj = result.scalar_one_or_none()
        
        if not class_obj:
            return None
        
        # Get student count
        from app.models.models import Student
        count_result = await self.db.execute(
            select(func.count(Student.id))
            .where(
                and_(
                    Student.class_id == class_id,
                    Student.status == "active"
                )
            )
        )
        student_count = count_result.scalar() or 0
        
        teacher_name = None
        if class_obj.class_teacher:
            profile_result = await self.db.execute(
                select(UserProfile)
                .join(User, UserProfile.user_id == User.id)
                .where(User.id == class_obj.class_teacher.user_id)
            )
            profile = profile_result.scalar_one_or_none()
            if profile:
                teacher_name = f"{profile.first_name} {profile.last_name}"
        
        return {
            "id": class_obj.id,
            "name": class_obj.name,
            "grade": class_obj.grade,
            "section": class_obj.section,
            "capacity": class_obj.capacity,
            "room_number": class_obj.room_number,
            "class_teacher_id": class_obj.class_teacher_id,
            "class_teacher_name": teacher_name,
            "student_count": student_count,
            "is_active": class_obj.is_active
        }
    
    async def update_class(self, class_id: int, update_data: ClassUpdate) -> dict:
        """Update class"""
        result = await self.db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_obj = result.scalar_one_or_none()
        
        if not class_obj:
            raise ValueError("Class not found")
        
        update_data_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(class_obj, key, value)
        
        await self.db.commit()
        
        return {"success": True, "message": "Class updated successfully"}


class SubjectService:
    """Service for subject management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_subject(self, subject_data: SubjectCreate) -> dict:
        """Create a new subject"""
        subject = Subject(
            code=subject_data.code,
            name=subject_data.name,
            description=subject_data.description,
            is_elective=subject_data.is_elective,
            is_active=subject_data.is_active
        )
        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)
        
        return {"subject_id": subject.id, "code": subject.code, "name": subject.name}
    
    async def get_subject_list(self, is_active: bool = True) -> list:
        """Get all subjects"""
        query = select(Subject)
        if is_active:
            query = query.where(Subject.is_active == True)
        
        result = await self.db.execute(query)
        return [{"id": s.id, "code": s.code, "name": s.name, "is_elective": s.is_elective} for s in result.scalars().all()]
    
    async def assign_subject_to_class(self, assignment: ClassSubjectAssign) -> dict:
        """Assign a subject to a class"""
        # Check if already assigned
        existing = await self.db.execute(
            select(ClassSubject).where(
                and_(
                    ClassSubject.class_id == assignment.class_id,
                    ClassSubject.subject_id == assignment.subject_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Subject already assigned to this class")
        
        class_subject = ClassSubject(
            class_id=assignment.class_id,
            subject_id=assignment.subject_id
        )
        self.db.add(class_subject)
        await self.db.commit()
        
        return {"success": True, "message": "Subject assigned to class"}
    
    async def assign_teacher_to_subject(self, assignment: SubjectTeacherAssign) -> dict:
        """Assign a teacher to teach a subject in a class"""
        # Check if already assigned
        existing = await self.db.execute(
            select(SubjectTeacher).where(
                and_(
                    SubjectTeacher.staff_id == assignment.staff_id,
                    SubjectTeacher.subject_id == assignment.subject_id,
                    SubjectTeacher.class_id == assignment.class_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Teacher already assigned to this subject in this class")
        
        subject_teacher = SubjectTeacher(
            staff_id=assignment.staff_id,
            subject_id=assignment.subject_id,
            class_id=assignment.class_id
        )
        self.db.add(subject_teacher)
        await self.db.commit()
        
        return {"success": True, "message": "Teacher assigned to subject"}
    
    async def get_subject_assignments(self, staff_id: int) -> list:
        """Get all subject assignments for a teacher"""
        result = await self.db.execute(
            select(SubjectTeacher, Subject, Class)
            .join(Subject, SubjectTeacher.subject_id == Subject.id)
            .join(Class, SubjectTeacher.class_id == Class.id)
            .where(SubjectTeacher.staff_id == staff_id)
        )
        
        return [
            {
                "assignment_id": st.id,
                "subject_id": subject.id,
                "subject_name": subject.name,
                "class_id": cls.id,
                "class_name": cls.name
            }
            for st, subject, cls in result.all()
        ]
