"""
Report Service - Analytics and Dashboard Logic
"""
from typing import Optional, List, Dict
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta
from collections import defaultdict

from app.db.models.models import (
    Student, User, Class, Section, Subject, 
    Attendance, Fee, FeePayment, StudentClass
)
from app.db.models.transport import (
    Vehicle, Route, TransportAllocation
)
from app.db.models.hostel import (
    HostelBlock, Room, HostelAllocation as HostelAlloc
)
from app.db.models.library import (
    Book, BookTransaction, LibraryMember
)


class ReportService:
    """Service class for reports and analytics"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # ==================== Dashboard Operations ====================
    
    async def get_dashboard_stats(self) -> dict:
        """Get dashboard statistics"""
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # Student statistics
        students_result = await self.session.execute(
            select(func.count(Student.id))
        )
        total_students = students_result.scalar() or 0
        
        # Staff statistics
        staff_result = await self.session.execute(
            select(func.count(User.id)).where(User.role.in_(["teacher", "staff"]))
        )
        total_staff = staff_result.scalar() or 0
        
        # Class statistics
        classes_result = await self.session.execute(
            select(func.count(Class.id))
        )
        total_classes = classes_result.scalar() or 0
        
        # Attendance statistics
        attendance_result = await self.session.execute(
            select(
                func.sum(Attendance.status == "present").label("present"),
                func.count(Attendance.id).label("total")
            ).where(Attendance.date == today)
        )
        attendance_data = attendance_result.one()
        today_present = attendance_data.present or 0
        today_total = attendance_data.total or 0
        today_percentage = round((today_present / today_total * 100) if today_total > 0 else 0, 2)
        
        # Finance statistics
        finance_result = await self.session.execute(
            select(
                func.sum(FeePayment.amount).label("total_collected"),
                func.sum(Fee.amount).label("total_fee")
            ).join(Fee, Fee.id == FeePayment.fee_id)
        )
        finance_data = finance_result.one()
        total_collected = finance_data.total_collected or 0
        total_fee = finance_data.total_fee or 0
        
        today_payment_result = await self.session.execute(
            select(func.sum(FeePayment.amount)).where(
                func.date(FeePayment.payment_date) == today
            )
        )
        today_collection = today_payment_result.scalar() or 0
        
        # Transport statistics
        transport_result = await self.session.execute(
            select(
                func.count(Vehicle.id).label("vehicles"),
                func.count(TransportAllocation.id).label("allocations")
            )
        )
        transport_data = transport_result.one()
        
        # Hostel statistics
        hostel_result = await self.session.execute(
            select(
                func.count(HostelAlloc.id).label("hostel_students"),
                func.sum(Room.capacity).label("capacity"),
                func.sum(Room.current_occupancy).label("occupancy")
            ).join(Room, Room.id == HostelAlloc.room_id)
        )
        hostel_data = hostel_result.one()
        hostel_occupancy = round(
            ((hostel_data.occupancy or 0) / (hostel_data.capacity or 1)) * 100, 2
        )
        
        # Library statistics
        library_result = await self.session.execute(
            select(
                func.count(BookTransaction.id).label("issued"),
                func.sum(BookTransaction.status == "overdue").label("overdue")
            ).where(BookTransaction.status.in_(["issued", "overdue"]))
        )
        library_data = library_result.one()
        
        return {
            "total_students": total_students,
            "total_teachers": total_staff,
            "total_staff": total_staff,
            "total_classes": total_classes,
            "today_attendance_percentage": today_percentage,
            "week_attendance_percentage": today_percentage,  # Would need week calculation
            "total_fee_collection": total_collected,
            "pending_fee_amount": total_fee - total_collected,
            "today_collection": today_collection,
            "total_vehicles": transport_data.vehicles or 0,
            "active_allocations": transport_data.allocations or 0,
            "total_hostel_students": hostel_data.hostel_students or 0,
            "hostel_occupancy_percentage": hostel_occupancy,
            "books_issued": library_data.issued or 0,
            "books_overdue": library_data.overdue or 0,
            "report_date": datetime.utcnow()
        }
    
    async def get_admin_dashboard(self) -> dict:
        """Get comprehensive admin dashboard"""
        stats = await self.get_dashboard_stats()
        
        return {
            "students": await self.get_student_stats(),
            "staff": await self.get_staff_stats(),
            "academics": await self.get_academic_stats(),
            "finance": await self.get_finance_stats(),
            "attendance": await self.get_attendance_stats(),
            "transport": await self.get_transport_stats(),
            "hostel": await self.get_hostel_stats(),
            "library": await self.get_library_stats(),
            "generated_at": datetime.utcnow()
        }
    
    # ==================== Student Statistics ====================
    
    async def get_student_stats(self) -> dict:
        """Get student statistics"""
        today = date.today()
        start_of_month = today.replace(day=1)
        
        total_result = await self.session.execute(
            select(func.count(Student.id))
        )
        total = total_result.scalar() or 0
        
        new_result = await self.session.execute(
            select(func.count(Student.id)).where(
                Student.created_at >= start_of_month
            )
        )
        new_admissions = new_result.scalar() or 0
        
        # Students by class
        class_result = await self.session.execute(
            select(
                Class.id,
                Class.name,
                func.count(StudentClass.student_id).label("count")
            ).outerjoin(StudentClass, and_(
                StudentClass.class_id == Class.id,
                StudentClass.is_active == True
            )).group_by(Class.id)
        )
        students_by_class = [
            {"class_id": row.id, "class_name": row.name, "count": row.count or 0}
            for row in class_result.all()
        ]
        
        return {
            "total_students": total,
            "active_students": total,
            "new_admissions_this_month": new_admissions,
            "students_by_class": students_by_class,
            "students_by_section": []  # Would need section join
        }
    
    async def get_staff_stats(self) -> dict:
        """Get staff statistics"""
        teachers_result = await self.session.execute(
            select(func.count(User.id)).where(User.role == "teacher")
        )
        total_teachers = teachers_result.scalar() or 0
        
        staff_result = await self.session.execute(
            select(func.count(User.id)).where(User.role == "staff")
        )
        total_staff = staff_result.scalar() or 0
        
        return {
            "total_teachers": total_teachers,
            "total_staff": total_staff,
            "teachers_by_department": [],
            "staff_by_role": []
        }
    
    async def get_academic_stats(self) -> dict:
        """Get academic statistics"""
        classes_result = await self.session.execute(
            select(func.count(Class.id))
        )
        total_classes = classes_result.scalar() or 0
        
        subjects_result = await self.session.execute(
            select(func.count(Subject.id))
        )
        total_subjects = subjects_result.scalar() or 0
        
        return {
            "total_classes": total_classes,
            "total_subjects": total_subjects,
            "total_examscheduled": 0,
            "exams_completed": 0,
            "passing_percentage": 0.0
        }
    
    async def get_finance_stats(self) -> dict:
        """Get finance statistics"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        
        total_result = await self.session.execute(
            select(func.sum(Fee.amount))
        )
        total_fee = total_result.scalar() or 0
        
        collected_result = await self.session.execute(
            select(func.sum(FeePayment.amount))
        )
        total_collected = collected_result.scalar() or 0
        
        today_result = await self.session.execute(
            select(func.sum(FeePayment.amount)).where(
                func.date(FeePayment.payment_date) == today
            )
        )
        today_collection = today_result.scalar() or 0
        
        week_result = await self.session.execute(
            select(func.sum(FeePayment.amount)).where(
                FeePayment.payment_date >= start_of_week
            )
        )
        week_collection = week_result.scalar() or 0
        
        month_result = await self.session.execute(
            select(func.sum(FeePayment.amount)).where(
                FeePayment.payment_date >= start_of_month
            )
        )
        month_collection = month_result.scalar() or 0
        
        return {
            "total_fee_collection": total_collected,
            "pending_fee_amount": total_fee - total_collected,
            "today_collection": today_collection,
            "week_collection": week_collection,
            "month_collection": month_collection,
            "collection_by_class": [],
            "defaulters_count": 0,
            "defaulters_amount": total_fee - total_collected
        }
    
    async def get_attendance_stats(self) -> dict:
        """Get attendance statistics"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Today
        today_result = await self.session.execute(
            select(
                func.sum(Attendance.status == "present").label("present"),
                func.sum(Attendance.status == "absent").label("absent"),
                func.sum(Attendance.status == "leave").label("leave"),
                func.count(Attendance.id).label("total")
            ).where(Attendance.date == today)
        )
        today_data = today_result.one()
        
        # Week
        week_result = await self.session.execute(
            select(
                func.sum(Attendance.status == "present").label("present"),
                func.sum(Attendance.status == "absent").label("absent")
            ).where(Attendance.date >= week_start)
        )
        week_data = week_result.one()
        
        # Month
        month_result = await self.session.execute(
            select(
                func.sum(Attendance.status == "present").label("present"),
                func.sum(Attendance.status == "absent").label("absent")
            ).where(Attendance.date >= month_start)
        )
        month_data = month_result.one()
        
        total_today = today_data.total or 0
        total_week = week_data.present or 0 + week_data.absent or 0
        total_month = month_data.present or 0 + month_data.absent or 0
        
        return {
            "today_present": today_data.present or 0,
            "today_absent": today_data.absent or 0,
            "today_leave": today_data.leave or 0,
            "today_percentage": round((today_data.present or 0) / total_today * 100, 2) if total_today > 0 else 0,
            "week_present": week_data.present or 0,
            "week_absent": week_data.absent or 0,
            "week_percentage": round((week_data.present or 0) / total_week * 100, 2) if total_week > 0 else 0,
            "month_present": month_data.present or 0,
            "month_absent": month_data.absent or 0,
            "month_percentage": round((month_data.present or 0) / total_month * 100, 2) if total_month > 0 else 0
        }
    
    async def get_transport_stats(self) -> dict:
        """Get transport statistics"""
        vehicles_result = await self.session.execute(
            select(func.count(Vehicle.id))
        )
        total_vehicles = vehicles_result.scalar() or 0
        
        active_result = await self.session.execute(
            select(func.count(Vehicle.id)).where(Vehicle.status == "active")
        )
        active_vehicles = active_result.scalar() or 0
        
        maintenance_result = await self.session.execute(
            select(func.count(Vehicle.id)).where(Vehicle.status == "maintenance")
        )
        vehicles_in_maintenance = maintenance_result.scalar() or 0
        
        routes_result = await self.session.execute(
            select(func.count(Route.id))
        )
        total_routes = routes_result.scalar() or 0
        
        allocations_result = await self.session.execute(
            select(func.count(TransportAllocation.id))
        )
        total_allocations = allocations_result.scalar() or 0
        
        active_allocations_result = await self.session.execute(
            select(func.count(TransportAllocation.id)).where(
                TransportAllocation.status == "allocated"
            )
        )
        active_allocations = active_allocations_result.scalar() or 0
        
        return {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "vehicles_in_maintenance": vehicles_in_maintenance,
            "total_routes": total_routes,
            "total_allocations": total_allocations,
            "active_allocations": active_allocations,
            "vehicle_utilization": [],
            "revenue_collected": 0,
            "pending_fees": 0
        }
    
    async def get_hostel_stats(self) -> dict:
        """Get hostel statistics"""
        blocks_result = await self.session.execute(
            select(func.count(HostelBlock.id))
        )
        total_blocks = blocks_result.scalar() or 0
        
        rooms_result = await self.session.execute(
            select(func.count(Room.id))
        )
        total_rooms = rooms_result.scalar() or 0
        
        capacity_result = await self.session.execute(
            select(
                func.sum(Room.capacity).label("capacity"),
                func.sum(Room.current_occupancy).label("occupancy")
            )
        )
        capacity_data = capacity_result.one()
        
        maintenance_result = await self.session.execute(
            select(func.count(text("id"))).select_from(text("maintenance_requests")).where(
                text("status = 'pending'")
            )
        )
        pending_maintenance = maintenance_result.scalar() or 0
        
        return {
            "total_blocks": total_blocks,
            "total_rooms": total_rooms,
            "total_capacity": capacity_data.capacity or 0,
            "total_occupancy": capacity_data.occupancy or 0,
            "occupancy_percentage": round(
                ((capacity_data.occupancy or 0) / (capacity_data.capacity or 1)) * 100, 2
            ),
            "boys_occupancy": 0,
            "girls_occupancy": 0,
            "available_beds": (capacity_data.capacity or 0) - (capacity_data.occupancy or 0),
            "pending_maintenance": pending_maintenance
        }
    
    async def get_library_stats(self) -> dict:
        """Get library statistics"""
        books_result = await self.session.execute(
            select(func.count(Book.id))
        )
        total_books = books_result.scalar() or 0
        
        members_result = await self.session.execute(
            select(func.count(LibraryMember.id))
        )
        total_members = members_result.scalar() or 0
        
        issued_result = await self.session.execute(
            select(func.count(BookTransaction.id)).where(
                BookTransaction.status == "issued"
            )
        )
        books_issued = issued_result.scalar() or 0
        
        overdue_result = await self.session.execute(
            select(func.count(BookTransaction.id)).where(
                BookTransaction.status == "overdue"
            )
        )
        books_overdue = overdue_result.scalar() or 0
        
        return {
            "total_books": total_books,
            "total_members": total_members,
            "books_issued": books_issued,
            "books_returned_today": 0,
            "books_overdue": books_overdue,
            "overdue_fines_collected": 0,
            "popular_books": []
        }
    
    # ==================== Report Generation ====================
    
    async def get_attendance_report(
        self,
        start_date: date,
        end_date: date,
        class_id: Optional[int] = None
    ) -> dict:
        """Generate attendance report"""
        # Calculate total days
        total_days = (end_date - start_date).days + 1
        
        # Get attendance data
        query = select(
            Attendance.student_id,
            func.sum(Attendance.status == "present").label("present"),
            func.count(Attendance.id).label("total")
        ).where(
            and_(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        )
        
        if class_id:
            query = query.join(StudentClass).where(
                and_(
                    StudentClass.class_id == class_id,
                    StudentClass.is_active == True
                )
            )
        
        query = query.group_by(Attendance.student_id)
        result = await self.session.execute(query)
        
        student_data = []
        for row in result.all():
            present = row.present or 0
            attendance_pct = round((present / total_days) * 100, 2)
            student_data.append({
                "student_id": row.student_id,
                "present_days": present,
                "absent_days": total_days - present,
                "attendance_percentage": attendance_pct
            })
        
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "total_students": len(student_data),
            "total_days": total_days,
            "overall_attendance_percentage": round(
                sum(s["present_days"] for s in student_data) / 
                (len(student_data) * total_days if student_data else 1) * 100, 2
            ),
            "student_wise_data": student_data,
            "class_wise_data": [],
            "daily_data": []
        }
    
    async def get_fee_collection_report(
        self,
        start_date: date,
        end_date: date
    ) -> dict:
        """Generate fee collection report"""
        # Get total collected
        collected_result = await self.session.execute(
            select(func.sum(FeePayment.amount)).where(
                and_(
                    FeePayment.payment_date >= datetime.combine(start_date, datetime.min.time()),
                    FeePayment.payment_date <= datetime.combine(end_date, datetime.max.time())
                )
            )
        )
        total_collected = collected_result.scalar() or 0
        
        # Get total fee
        fee_result = await self.session.execute(
            select(func.sum(Fee.amount))
        )
        total_fee = fee_result.scalar() or 0
        
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "total_collected": total_collected,
            "total_pending": total_fee - total_collected,
            "collection_by_date": [],
            "collection_by_class": [],
            "collection_by_payment_mode": [],
            "top_defaulters": [],
            "collection_trend": []
        }
    
    async def get_transport_utilization_report(self) -> dict:
        """Generate transport utilization report"""
        vehicles_result = await self.session.execute(
            select(Vehicle)
            .options(selectinload(Vehicle.allocations))
        )
        vehicles = vehicles_result.scalars().all()
        
        utilization = []
        for vehicle in vehicles:
            active_allocations = len([
                a for a in vehicle.allocations 
                if a.status.value == "allocated"
            ])
            utilization.append({
                "vehicle_id": vehicle.id,
                "registration": vehicle.registration_number,
                "capacity": vehicle.capacity,
                "allocated": active_allocations,
                "utilization_percentage": round(
                    (active_allocations / vehicle.capacity * 100) 
                    if vehicle.capacity > 0 else 0, 2
                )
            })
        
        avg_utilization = round(
            sum(v["utilization_percentage"] for v in utilization) / len(utilization)
            if utilization else 0, 2
        )
        
        return {
            "period": {"start_date": date.today(), "end_date": date.today()},
            "vehicles": utilization,
            "routes": [],
            "overall_utilization": avg_utilization,
            "revenue_summary": {"total": 0, "pending": 0}
        }
    
    async def get_hostel_occupancy_report(self) -> dict:
        """Generate hostel occupancy report"""
        blocks_result = await self.session.execute(
            select(HostelBlock)
            .options(selectinload(Room))
        )
        blocks = blocks_result.scalars().all()
        
        total_beds = 0
        occupied_beds = 0
        
        block_data = []
        for block in blocks:
            block_beds = sum(room.capacity for room in block.rooms)
            block_occupied = sum(room.current_occupancy for room in block.rooms)
            
            total_beds += block_beds
            occupied_beds += block_occupied
            
            block_data.append({
                "block_id": block.id,
                "block_name": block.name,
                "block_type": block.block_type.value,
                "total_rooms": len(block.rooms),
                "total_beds": block_beds,
                "occupied_beds": block_occupied,
                "available_beds": block_beds - block_occupied,
                "occupancy_percentage": round(
                    (block_occupied / block_beds * 100) if block_beds > 0 else 0, 2
                )
            })
        
        return {
            "total_blocks": len(blocks),
            "total_rooms": sum(len(b.rooms) for b in blocks),
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": total_beds - occupied_beds,
            "occupancy_percentage": round(
                (occupied_beds / total_beds * 100) if total_beds > 0 else 0, 2
            ),
            "block_wise_data": block_data,
            "room_type_distribution": []
        }
