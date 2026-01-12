"""
Attendance and Timetable Services

Business logic for attendance tracking and schedule management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import (
    Attendance, StaffAttendance, Timetable, Student, User, UserProfile,
    Class, Subject, Staff, ClassSubject, SubjectTeacher
)
from app.schema.attendance_schema import (
    AttendanceStatusEnum, StaffAttendanceStatusEnum, DayOfWeekEnum
)


class AttendanceService:
    """Service for attendance management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def mark_attendance(self, class_id: int, date_: date, records: List[Dict], 
                               marked_by: int, period: Optional[int] = None) -> dict:
        """
        Mark attendance for multiple students in a class.
        
        Args:
            class_id: Class ID
            date_: Date of attendance
            records: List of {'student_id': int, 'status': str, 'remarks': optional}
            marked_by: Staff ID who marked attendance
            period: Optional period number for period-based attendance
        """
        created_count = 0
        updated_count = 0
        
        for record in records:
            student_id = record.get("student_id")
            status = record.get("status", "present")
            
            # Check if attendance already marked
            existing = await self.db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.student_id == student_id,
                        Attendance.date == date_,
                        Attendance.period == period
                    )
                )
            )
            
            status_enum = AttendanceStatusEnum(status)
            
            if existing.scalar_one_or_none():
                # Update existing
                await self.db.execute(
                    select(Attendance)
                    .where(
                        and_(
                            Attendance.student_id == student_id,
                            Attendance.date == date_,
                            Attendance.period == period
                        )
                    )
                    .values(
                        status=status_enum,
                        remarks=record.get("remarks"),
                        marked_by=marked_by
                    )
                )
                updated_count += 1
            else:
                # Create new
                attendance = Attendance(
                    student_id=student_id,
                    class_id=class_id,
                    date=date_,
                    status=status_enum,
                    period=period,
                    marked_by=marked_by,
                    remarks=record.get("remarks"),
                    check_in_time=datetime.now() if status_enum == AttendanceStatusEnum.PRESENT else None
                )
                self.db.add(attendance)
                created_count += 1
        
        await self.db.commit()
        
        return {
            "success": True,
            "message": f"Attendance marked: {created_count} new, {updated_count} updated",
            "created": created_count,
            "updated": updated_count
        }
    
    async def get_student_attendance(
        self,
        student_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get attendance history for a student"""
        query = (
            select(Attendance, Class)
            .join(Class, Attendance.class_id == Class.id)
            .where(Attendance.student_id == student_id)
        )
        
        if start_date:
            query = query.where(Attendance.date >= start_date)
        if end_date:
            query = query.where(Attendance.date <= end_date)
        
        query = query.order_by(Attendance.date.desc())
        
        result = await self.db.execute(query)
        records = result.all()
        
        # Get student info
        student_result = await self.db.execute(
            select(Student, UserProfile)
            .join(UserProfile, Student.user_id == UserProfile.user_id)
            .where(Student.id == student_id)
        )
        student_row = student_result.first()
        
        if not student_row:
            raise ValueError("Student not found")
        
        student, profile = student_row
        student_name = f"{profile.first_name} {profile.last_name}"
        
        # Calculate statistics
        total = len(records)
        present = sum(1 for r, c in records if r.status.value == "present")
        absent = sum(1 for r, c in records if r.status.value == "absent")
        late = sum(1 for r, c in records if r.status.value == "late")
        excused = sum(1 for r, c in records if r.status.value == "excused")
        
        attendance_percentage = (present / total * 100) if total > 0 else 100.0
        
        # Determine status
        if attendance_percentage >= 90:
            status = "Excellent"
        elif attendance_percentage >= 75:
            status = "Satisfactory"
        elif attendance_percentage >= 60:
            status = "At Risk"
        else:
            status = "Critical"
        
        return {
            "student_id": student_id,
            "student_name": student_name,
            "admission_number": student.admission_number,
            "total_days": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_percentage": round(attendance_percentage, 2),
            "status": status,
            "records": [
                {
                    "date": r.date,
                    "status": r.status.value,
                    "class_name": c.name,
                    "period": r.period,
                    "remarks": r.remarks
                }
                for r, c in records
            ]
        }
    
    async def get_class_attendance_summary(
        self,
        class_id: int,
        date_: date,
        period: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get attendance summary for a class on a date"""
        query = (
            select(Attendance)
            .where(
                and_(
                    Attendance.class_id == class_id,
                    Attendance.date == date_,
                    Attendance.period == period
                )
            )
        )
        
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        # Get class info
        class_result = await self.db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_obj = class_result.scalar_one_or_none()
        
        if not class_obj:
            raise ValueError("Class not found")
        
        # Get total students
        student_count = await self.db.execute(
            select(func.count(Student.id))
            .where(
                and_(
                    Student.class_id == class_id,
                    Student.status == "active"
                )
            )
        )
        total_students = student_count.scalar() or 0
        
        present = sum(1 for r in records if r.status.value == "present")
        absent = total_students - present
        
        return {
            "class_id": class_id,
            "class_name": class_obj.name,
            "date": date_,
            "period": period,
            "total_students": total_students,
            "present": present,
            "absent": absent,
            "attendance_percentage": round((present / total_students * 100), 2) if total_students > 0 else 0
        }
    
    async def get_monthly_attendance_report(
        self,
        class_id: int,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get monthly attendance report for a class"""
        # Get all dates in the month
        start_date = date(year, month, 1)
        end_date = start_date.replace(day=28) + timedelta(days=4)
        end_date = end_date - timedelta(days=end_date.day)
        
        # Get class info
        class_result = await self.db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_obj = class_result.scalar_one_or_none()
        
        if not class_obj:
            raise ValueError("Class not found")
        
        # Get attendance for each day
        result = await self.db.execute(
            select(Attendance)
            .where(
                and_(
                    Attendance.class_id == class_id,
                    Attendance.date >= start_date,
                    Attendance.date <= end_date
                )
            )
        )
        records = result.scalars().all()
        
        # Group by date
        by_date = {}
        for r in records:
            if r.date not in by_date:
                by_date[r.date] = []
            by_date[r.date].append(r.status.value)
        
        daily_summaries = []
        total_present = 0
        total_possible = 0
        
        # Get student count
        student_count = await self.db.execute(
            select(func.count(Student.id))
            .where(
                and_(
                    Student.class_id == class_id,
                    Student.status == "active"
                )
            )
        )
        student_count = student_count.scalar() or 0
        
        current = start_date
        while current <= end_date:
            statuses = by_date.get(current, [])
            present = sum(1 for s in statuses if s == "present")
            absent = student_count - present
            
            daily_summaries.append({
                "date": current,
                "present": present,
                "absent": absent,
                "attendance_percentage": round((present / student_count * 100), 2) if student_count > 0 else 0
            })
            
            total_present += present
            total_possible += student_count
            current += timedelta(days=1)
        
        overall = round((total_present / total_possible * 100), 2) if total_possible > 0 else 0
        
        return {
            "class_id": class_id,
            "class_name": class_obj.name,
            "month": month,
            "year": year,
            "daily_summaries": daily_summaries,
            "overall_attendance": overall
        }
    
    async def mark_staff_attendance(
        self,
        staff_id: int,
        date_: date,
        status: StaffAttendanceStatusEnum,
        check_in: Optional[datetime] = None,
        check_out: Optional[datetime] = None,
        remarks: Optional[str] = None
    ) -> dict:
        """Mark staff attendance"""
        # Check existing
        existing = await self.db.execute(
            select(StaffAttendance)
            .where(
                and_(
                    StaffAttendance.staff_id == staff_id,
                    StaffAttendance.date == date_
                )
            )
        )
        
        if existing.scalar_one_or_none():
            # Update
            await self.db.execute(
                select(StaffAttendance)
                .where(
                    and_(
                        StaffAttendance.staff_id == staff_id,
                        StaffAttendance.date == date_
                    )
                )
                .values(
                    status=status.value,
                    check_in=check_in,
                    check_out=check_out,
                    remarks=remarks
                )
            )
        else:
            # Create
            staff_attendance = StaffAttendance(
                staff_id=staff_id,
                date=date_,
                status=status.value,
                check_in=check_in,
                check_out=check_out,
                remarks=remarks
            )
            self.db.add(staff_attendance)
        
        await self.db.commit()
        
        return {"success": True, "message": "Staff attendance marked"}


class TimetableService:
    """Service for timetable management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_timetable_slot(self, slot_data: Dict) -> dict:
        """Create a timetable slot with conflict detection"""
        class_id = slot_data["class_id"]
        staff_id = slot_data["staff_id"]
        day = slot_data["day_of_week"]
        period = slot_data["period_number"]
        start_time = slot_data["start_time"]
        end_time = slot_data["end_time"]
        
        # Check for conflicts
        conflicts = await self._check_conflicts(
            class_id=class_id,
            staff_id=staff_id,
            day=day,
            period=period,
            start_time=start_time,
            end_time=end_time,
            room_number=slot_data.get("room_number")
        )
        
        if conflicts["has_conflicts"]:
            return {
                "success": False,
                "message": "Cannot create timetable slot due to conflicts",
                "conflicts": conflicts["conflicts"]
            }
        
        # Create slot
        slot = Timetable(
            class_id=class_id,
            day_of_week=day,
            period_number=period,
            subject_id=slot_data["subject_id"],
            staff_id=staff_id,
            room_number=slot_data.get("room_number"),
            start_time=start_time,
            end_time=end_time,
            is_active=True
        )
        self.db.add(slot)
        await self.db.commit()
        await self.db.refresh(slot)
        
        return {
            "success": True,
            "message": "Timetable slot created",
            "slot_id": slot.id
        }
    
    async def _check_conflicts(
        self,
        class_id: int,
        staff_id: int,
        day: int,
        period: int,
        start_time: time,
        end_time: time,
        room_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        # Check if teacher is already teaching another class at this time
        teacher_conflict = await self.db.execute(
            select(Timetable).where(
                and_(
                    Timetable.staff_id == staff_id,
                    Timetable.day_of_week == day,
                    Timetable.period_number == period,
                    Timetable.is_active == True
                )
            )
        )
        existing = teacher_conflict.scalars().all()
        if existing:
            for slot in existing:
                if slot.class_id != class_id:  # Different class
                    conflicts.append({
                        "conflict_type": "teacher",
                        "message": f"Teacher is already scheduled for class {slot.class_id} at this time",
                        "existing_slot": {
                            "class_id": slot.class_id,
                            "period": slot.period_number,
                            "time": f"{slot.start_time} - {slot.end_time}"
                        }
                    })
        
        # Check if room is already booked
        if room_number:
            room_conflict = await self.db.execute(
                select(Timetable).where(
                    and_(
                        Timetable.room_number == room_number,
                        Timetable.day_of_week == day,
                        Timetable.period_number == period,
                        Timetable.is_active == True
                    )
                )
            )
            existing = room_conflict.scalars().all()
            if existing:
                for slot in existing:
                    if slot.class_id != class_id:
                        conflicts.append({
                            "conflict_type": "room",
                            "message": f"Room {room_number} is already booked for class {slot.class_id}",
                            "existing_slot": {
                                "class_id": slot.class_id,
                                "period": slot.period_number,
                                "time": f"{slot.start_time} - {slot.end_time}"
                            }
                        })
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts
        }
    
    async def get_class_timetable(
        self,
        class_id: int,
        day_of_week: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get timetable for a class"""
        query = (
            select(Timetable, Subject, Class, Staff)
            .join(Subject, Timetable.subject_id == Subject.id)
            .join(Class, Timetable.class_id == Class.id)
            .join(Staff, Timetable.staff_id == Staff.id)
            .where(Timetable.class_id == class_id)
            .where(Timetable.is_active == True)
        )
        
        if day_of_week:
            query = query.where(Timetable.day_of_week == day_of_week)
        
        query = query.order_by(Timetable.period_number)
        
        result = await self.db.execute(query)
        slots = result.all()
        
        # Get class info
        class_result = await self.db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_obj = class_result.scalar_one_or_none()
        
        # Group by day
        by_day = {}
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        
        for slot, subject, class_, staff in slots:
            if slot.day_of_week not in by_day:
                by_day[slot.day_of_week] = []
            
            by_day[slot.day_of_week].append({
                "id": slot.id,
                "period": slot.period_number,
                "subject_name": subject.name,
                "staff_name": f"Staff {staff.id}",  # Would need to join with UserProfile
                "room_number": slot.room_number,
                "start_time": slot.start_time.isoformat() if slot.start_time else None,
                "end_time": slot.end_time.isoformat() if slot.end_time else None
            })
        
        return {
            "class_id": class_id,
            "class_name": class_obj.name if class_obj else "Unknown",
            "timetable": {
                day_names.get(day, f"Day {day}"): slots_list
                for day, slots_list in by_day.items()
            }
        }
    
    async def get_teacher_timetable(self, staff_id: int) -> Dict[str, Any]:
        """Get timetable for a teacher"""
        result = await self.db.execute(
            select(Timetable, Subject, Class)
            .join(Subject, Timetable.subject_id == Subject.id)
            .join(Class, Timetable.class_id == Class.id)
            .where(
                and_(
                    Timetable.staff_id == staff_id,
                    Timetable.is_active == True
                )
            )
            .order_by(Timetable.day_of_week, Timetable.period_number)
        )
        slots = result.all()
        
        # Group by day
        by_day = {}
        day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}
        
        for slot, subject, class_ in slots:
            if slot.day_of_week not in by_day:
                by_day[slot.day_of_week] = []
            
            by_day[slot.day_of_week].append({
                "id": slot.id,
                "period": slot.period_number,
                "class_name": class_.name,
                "subject_name": subject.name,
                "room_number": slot.room_number,
                "start_time": slot.start_time.isoformat() if slot.start_time else None,
                "end_time": slot.end_time.isoformat() if slot.end_time else None
            })
        
        return {
            "staff_id": staff_id,
            "timetable": {
                day_names.get(day, f"Day {day}"): slots_list
                for day, slots_list in by_day.items()
            }
        }
    
    async def delete_timetable_slot(self, slot_id: int) -> dict:
        """Delete (deactivate) a timetable slot"""
        await self.db.execute(
            select(Timetable)
            .where(Timetable.id == slot_id)
            .values(is_active=False)
        )
        await self.db.commit()
        
        return {"success": True, "message": "Timetable slot deleted"}
