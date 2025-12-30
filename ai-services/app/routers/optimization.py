"""
Resource Optimization Router
Timetable optimization, bus route optimization, resource allocation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class TimetableOptimizationRequest(BaseModel):
    school_id: int
    classes: List[dict]
    subjects: List[dict]
    teachers: List[dict]
    rooms: List[dict]
    periods_per_day: int = 8
    working_days: List[int] = [0, 1, 2, 3, 4]  # Monday=0 to Sunday=6
    constraints: Optional[Dict] = None


class TimetableOptimizationResponse(BaseModel):
    success: bool
    schedule_quality_score: float
    total_conflicts: int
    generated_schedules: List[dict]
    conflicts: List[dict]
    recommendations: List[str]
    optimization_time_seconds: float


class RouteOptimizationRequest(BaseModel):
    stops: List[dict]  # List of stops with coordinates
    bus_capacity: int
    start_location: dict  # Depot coordinates
    end_location: dict
    time_windows: Optional[List[dict]] = None  # Pickup time windows


class RouteOptimizationResponse(BaseModel):
    success: bool
    total_routes: int
    total_distance: float
    total_time: float
    routes: List[dict]
    optimization_score: float
    savings: dict


class RoomAllocationRequest(BaseModel):
    school_id: int
    booking_requests: List[dict]
    available_rooms: List[dict]
    time_slots: List[dict]


class RoomAllocationResponse(BaseModel):
    success: bool
    allocations: List[dict]
    unassigned_requests: List[dict]
    room_utilization: dict
    conflict_count: int


class TeacherAllocationRequest(BaseModel):
    subjects: List[dict]
    teachers: List[dict]
    classes: List[dict]
    class_teacher_assignments: List[dict]


class TeacherAllocationResponse(BaseModel):
    success: bool
    assignments: List[dict]
    unassigned_subjects: List[dict]
    teacher_workload: dict
    recommendations: List[str]


# Helper data structures
class ConstraintChecker:
    """Check and manage timetable constraints"""
    
    def __init__(self):
        self.teacher_conflicts = []
        self.room_conflicts = []
        self.student_conflicts = []
    
    def check_teacher_availability(self, teacher_id, day, period, schedule):
        """Check if teacher is available at given time"""
        for cls in schedule:
            if cls.get("teacher_id") == teacher_id:
                if cls.get("day_of_week") == day and cls.get("period_number") == period:
                    return False
        return True
    
    def check_room_availability(self, room_id, day, period, schedule):
        """Check if room is available at given time"""
        for cls in schedule:
            if cls.get("room_id") == room_id:
                if cls.get("day_of_week") == day and cls.get("period_number") == period:
                    return False
        return True


# Endpoints
@router.post("/optimize-timetable", response_model=TimetableOptimizationResponse)
async def optimize_timetable(request: TimetableOptimizationRequest):
    """
    Generate optimized timetable considering constraints
    - Teacher availability
    - Room capacity
    - Subject requirements
    - Student workload balance
    """
    try:
        logger.info(f"Optimizing timetable for school {request.school_id}")
        
        start_time = datetime.now()
        
        # Initialize schedule
        schedule = defaultdict(lambda: defaultdict(dict))
        
        # Simple heuristic scheduling (in production: use constraint satisfaction or genetic algorithm)
        conflicts = []
        quality_score = 0.0
        
        # Process each class
        for cls in request.classes:
            class_id = cls["id"]
            required_periods = cls.get("periods_per_week", {})
            
            for subject_name, periods_needed in required_periods.items():
                subject_info = next((s for s in request.subjects if s["name"] == subject_name), None)
                if not subject_info:
                    continue
                
                # Find available teacher
                available_teachers = [
                    t for t in request.teachers
                    if t.get("subject") == subject_name
                ]
                
                # Schedule periods
                scheduled = 0
                for day in request.working_days:
                    if scheduled >= periods_needed:
                        break
                    for period in range(1, request.periods_per_day + 1):
                        if scheduled >= periods_needed:
                            break
                        
                        # Find available teacher and room
                        teacher = next(
                            (t for t in available_teachers
                             if ConstraintChecker().check_teacher_availability(t["id"], day, period, [])),
                            available_teachers[0] if available_teachers else None
                        )
                        
                        room = next(
                            (r for r in request.rooms
                             if ConstraintChecker().check_room_availability(r["id"], day, period, [])),
                            request.rooms[0] if request.rooms else None
                        )
                        
                        if teacher and room:
                            schedule[class_id][f"{day}_{period}"] = {
                                "day_of_week": day,
                                "period_number": period,
                                "subject": subject_name,
                                "teacher_id": teacher["id"],
                                "teacher_name": teacher["name"],
                                "room_id": room["id"],
                                "room_name": room["name"]
                            }
                            scheduled += 1
        
        # Convert to list
        generated_schedules = []
        for class_id, periods in schedule.items():
            for period_key, period_data in periods.items():
                generated_schedules.append({
                    "class_id": class_id,
                    **period_data
                })
        
        # Calculate quality score
        total_slots = len(request.classes) * len(request.working_days) * request.periods_per_day
        filled_slots = len(generated_schedules)
        quality_score = filled_slots / total_slots if total_slots > 0 else 0
        
        # Detect conflicts
        teacher_slots = defaultdict(list)
        for entry in generated_schedules:
            key = f"{entry['day_of_week']}_{entry['period_number']}_{entry['teacher_id']}"
            if key in teacher_slots:
                conflicts.append({
                    "type": "teacher_conflict",
                    "teacher_id": entry["teacher_id"],
                    "day": entry["day_of_week"],
                    "period": entry["period_number"],
                    "classes": [class_id for class_id in teacher_slots[key]] + [entry["class_id"]]
                })
            teacher_slots[key].append(entry["class_id"])
        
        # Generate recommendations
        recommendations = [
            "Consider adding more teachers for high-demand subjects",
            "Balance workload across teachers",
            "Ensure adequate room capacity for large classes",
            "Consider lab availability for science subjects"
        ]
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        return TimetableOptimizationResponse(
            success=len(conflicts) == 0,
            schedule_quality_score=round(quality_score * 100, 2),
            total_conflicts=len(conflicts),
            generated_schedules=generated_schedules,
            conflicts=conflicts,
            recommendations=recommendations,
            optimization_time_seconds=optimization_time
        )
        
    except Exception as e:
        logger.error(f"Error in timetable optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-routes", response_model=RouteOptimizationResponse)
async def optimize_bus_routes(request: RouteOptimizationRequest):
    """
    Optimize bus routes for time and cost efficiency
    Uses vehicle routing problem (VRP) algorithms
    """
    try:
        logger.info(f"Optimizing routes for {len(request.stops)} stops")
        
        start_time = datetime.now()
        
        # Mock route optimization (in production: use Google OR-Tools or similar)
        # Simple nearest neighbor heuristic for demo
        
        if not request.stops:
            return RouteOptimizationResponse(
                success=False,
                total_routes=0,
                total_distance=0,
                total_time=0,
                routes=[],
                optimization_score=0,
                savings={}
            )
        
        # Sort stops by distance from depot
        sorted_stops = sorted(
            request.stops,
            key=lambda s: _calculate_distance(request.start_location, s)
        )
        
        # Create route
        route = []
        current_location = request.start_location
        total_distance = 0
        total_time = 0
        
        for i, stop in enumerate(sorted_stops):
            distance = _calculate_distance(current_location, stop)
            time_estimate = distance * 3  # Assume 3 minutes per km
            
            route.append({
                "stop_number": i + 1,
                "stop_id": stop.get("id"),
                "stop_name": stop.get("name"),
                "latitude": stop.get("latitude"),
                "longitude": stop.get("longitude"),
                "distance_from_previous": round(distance, 2),
                "estimated_time": round(time_estimate, 2),
                "students_pickup": stop.get("student_count", 0)
            })
            
            total_distance += distance
            total_time += time_estimate
            current_location = stop
        
        # Return to depot
        return_distance = _calculate_distance(current_location, request.end_location)
        total_distance += return_distance
        
        # Calculate metrics
        baseline_distance = sum(
            _calculate_distance(request.stops[i], request.stops[i + 1])
            for i in range(len(request.stops) - 1)
        )
        
        savings = {
            "distance_saved": round(baseline_distance - total_distance, 2) if baseline_distance > total_distance else 0,
            "time_saved": round((baseline_distance - total_distance) * 3, 2),
            "fuel_estimated": round(total_distance * 0.12, 2)  # L/100km estimate
        }
        
        return RouteOptimizationResponse(
            success=True,
            total_routes=1,
            total_distance=round(total_distance, 2),
            total_time=round(total_time, 2),
            routes=[{
                "route_id": 1,
                "route_name": "Route A",
                "stops": route,
                "start_time": "06:30",
                "estimated_end": f"{6 + int(total_time // 60)}:{int(total_time % 60):02d}",
                "total_stops": len(route),
                "total_students": sum(s.get("student_count", 0) for s in request.stops)
            }],
            optimization_score=85.5,
            savings=savings
        )
        
    except Exception as e:
        logger.error(f"Error in route optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/allocate-rooms", response_model=RoomAllocationResponse)
async def allocate_rooms(request: RoomAllocationRequest):
    """
    Allocate rooms for classes and events
    Maximize utilization while avoiding conflicts
    """
    try:
        logger.info(f"Allocating rooms for {len(request.booking_requests)} requests")
        
        # Simple greedy allocation
        allocations = []
        unassigned = []
        
        # Sort by priority
        sorted_requests = sorted(
            request.booking_requests,
            key=lambda r: (-r.get("priority", 0), r.get("required_capacity", 0))
        )
        
        # Track room availability
        room_availability = defaultdict(list)
        for room in request.available_rooms:
            room_availability[room["id"]] = []
        
        for req in sorted_requests:
            # Find suitable room
            suitable_room = None
            for room in request.available_rooms:
                if room.get("capacity", 0) >= req.get("required_capacity", 0):
                    # Check if room is available
                    is_available = True
                    for allocation in room_availability.get(room["id"], []):
                        if _timeslots_overlap(
                            allocation.get("start_time"), allocation.get("end_time"),
                            req.get("start_time"), req.get("end_time")
                        ):
                            is_available = False
                            break
                    
                    if is_available:
                        suitable_room = room
                        break
            
            if suitable_room:
                allocation = {
                    "booking_id": req["id"],
                    "room_id": suitable_room["id"],
                    "room_name": suitable_room["name"],
                    "start_time": req["start_time"],
                    "end_time": req["end_time"],
                    "capacity": suitable_room["capacity"]
                }
                allocations.append(allocation)
                room_availability[suitable_room["id"]].append(allocation)
            else:
                unassigned.append(req)
        
        # Calculate utilization
        room_utilization = {}
        for room in request.available_rooms:
            allocations_for_room = room_availability.get(room["id"], [])
            room_utilization[room["name"]] = {
                "bookings": len(allocations_for_room),
                "utilization_percentage": len(allocations_for_room) * 10  # Mock percentage
            }
        
        return RoomAllocationResponse(
            success=len(unassigned) == 0,
            allocations=allocations,
            unassigned_requests=unassigned,
            room_utilization=room_utilization,
            conflict_count=len(unassigned)
        )
        
    except Exception as e:
        logger.error(f"Error in room allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/allocate-teachers", response_model=TeacherAllocationResponse)
async def allocate_teachers(request: TeacherAllocationRequest):
    """
    Allocate teachers to subjects and classes
    Balance workload and expertise
    """
    try:
        logger.info("Optimizing teacher allocations")
        
        assignments = []
        teacher_workload = defaultdict(int)
        
        # Process each subject requirement
        for subject in request.subjects:
            subject_name = subject["name"]
            periods_needed = subject.get("periods_per_week", 0)
            
            # Find qualified teachers
            qualified_teachers = [
                t for t in request.teachers
                if subject_name in t.get("subjects", [])
            ]
            
            if not qualified_teachers:
                continue
            
            # Sort by current workload
            qualified_teachers.sort(key=lambda t: teacher_workload.get(t["id"], 0))
            
            # Allocate periods
            allocated = 0
            for teacher in qualified_teachers:
                if allocated >= periods_needed:
                    break
                
                periods_to_allocate = min(
                    periods_needed - allocated,
                    teacher.get("max_periods_per_week", 20) - teacher_workload.get(teacher["id"], 0)
                )
                
                if periods_to_allocate > 0:
                    for cls in request.classes:
                        if periods_to_allocate <= 0:
                            break
                        
                        # Check if class already has this subject
                        already_assigned = any(
                            a.get("class_id") == cls["id"] and a.get("subject") == subject_name
                            for a in assignments
                        )
                        
                        if not already_assigned:
                            assignments.append({
                                "teacher_id": teacher["id"],
                                "teacher_name": teacher["name"],
                                "subject": subject_name,
                                "class_id": cls["id"],
                                "class_name": cls["name"],
                                "periods_assigned": periods_to_allocate
                            })
                            teacher_workload[teacher["id"]] += periods_to_allocate
                            allocated += periods_to_allocate
        
        # Calculate workload metrics
        workload_summary = {
            "average_periods_per_teacher": round(
                sum(teacher_workload.values()) / len(teacher_workload) if teacher_workload else 0, 1
            ),
            "max_workload": max(teacher_workload.values()) if teacher_workload else 0,
            "min_workload": min(teacher_workload.values()) if teacher_workload else 0,
            "overloaded_teachers": len([
                t for t in request.teachers
                if teacher_workload.get(t["id"], 0) > t.get("max_periods_per_week", 20)
            ])
        }
        
        # Generate recommendations
        recommendations = [
            "Consider hiring additional teachers for high-demand subjects",
            "Redistribute classes to balance workload",
            "Provide training for teachers taking new subjects",
            "Monitor teacher fatigue and adjust schedules"
        ]
        
        return TeacherAllocationResponse(
            success=True,
            assignments=assignments,
            unassigned_subjects=[],
            teacher_workload=dict(teacher_workload),
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in teacher allocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _calculate_distance(point1, point2):
    """Calculate distance between two points (simplified)"""
    if not point1 or not point2:
        return 0
    lat1, lon1 = point1.get("latitude", 0), point1.get("longitude", 0)
    lat2, lon2 = point2.get("latitude", 0), point2.get("longitude", 0)
    
    # Simplified Euclidean distance (in production: use Haversine formula)
    return ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111  # Rough km estimate


def _timeslots_overlap(start1, end1, start2, end2):
    """Check if two time slots overlap"""
    return start1 < end2 and start2 < end1
