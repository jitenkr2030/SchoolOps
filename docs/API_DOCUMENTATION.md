# SchoolOps API Documentation

## Overview
SchoolOps provides a comprehensive REST API and GraphQL API for managing school operations. This documentation covers all available endpoints, authentication, and data models.

## Base URLs
- **REST API**: `https://api.schoolops.com/api/v1`
- **GraphQL API**: `https://api.schoolops.com/graphql`
- **AI Services**: `https://ai.schoolops.com/api/v1`

## Authentication
All API requests require authentication using JWT tokens.

### Obtaining a Token
```bash
POST /api/auth/login
Content-Type: application/json

{
    "email": "admin@school.com",
    "password": "your_password"
}
```

### Using the Token
Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and obtain JWT token.

**Request:**
```json
{
    "email": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### POST /api/auth/register
Register a new user.

**Request:**
```json
{
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "string"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user_id": "integer"
}
```

### POST /api/auth/logout
Logout and invalidate token.

**Headers:** Authorization: Bearer \<token\>

---

## Student Management Endpoints

### GET /api/students
Retrieve all students with optional filters.

**Query Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `search` (string): Search by name/admission number
- `class_id` (integer): Filter by class
- `status` (string): Filter by status (active/inactive)

**Response:**
```json
{
    "data": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@school.com",
            "admission_number": "STU001",
            "class": "Class 10-A",
            "status": "active"
        }
    ],
    "total": 150,
    "page": 1,
    "limit": 20
}
```

### GET /api/students/{id}
Retrieve a specific student.

### POST /api/students
Create a new student.

**Request:**
```json
{
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "admission_number": "string",
    "date_of_birth": "string (YYYY-MM-DD)",
    "gender": "string",
    "class_id": "integer",
    "parent_name": "string",
    "parent_phone": "string",
    "address": "string"
}
```

### PUT /api/students/{id}
Update student information.

### DELETE /api/students/{id}
Delete a student (soft delete).

---

## Teacher Management Endpoints

### GET /api/teachers
Retrieve all teachers.

**Response:**
```json
{
    "data": [
        {
            "id": 1,
            "first_name": "Mr.",
            "last_name": "Sharma",
            "email": "sharma@school.com",
            "subject": "Mathematics",
            "phone": "+1234567890"
        }
    ],
    "total": 25
}
```

### POST /api/teachers
Create a new teacher.

**Request:**
```json
{
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "subject": "string",
    "phone": "string",
    "qualification": "string",
    "experience": "integer"
}
```

### PUT /api/teachers/{id}
Update teacher information.

---

## Class Management Endpoints

### GET /api/classes
Retrieve all classes.

### POST /api/classes
Create a new class.

**Request:**
```json
{
    "name": "string",
    "section": "string",
    "academic_year_id": "integer",
    "class_teacher_id": "integer",
    "room_number": "string"
}
```

### GET /api/classes/{id}/students
Get all students in a class.

---

## Attendance Endpoints

### POST /api/attendance
Mark attendance for a student.

**Request:**
```json
{
    "student_id": "integer",
    "class_id": "integer",
    "date": "string (YYYY-MM-DD)",
    "status": "string (Present/Absent/Late/Excused)",
    "remarks": "string"
}
```

### GET /api/attendance/student/{student_id}
Get attendance records for a student.

**Query Parameters:**
- `start_date` (string)
- `end_date` (string)

**Response:**
```json
{
    "student_id": 1,
    "attendance_percentage": 92.5,
    "records": [
        {
            "date": "2024-10-15",
            "status": "Present",
            "class": "Class 10-A"
        }
    ]
}
```

### GET /api/attendance/class/{class_id}
Get attendance summary for a class.

### POST /api/attendance/bulk
Bulk mark attendance for a class.

---

## Academic Management Endpoints

### GET /api/grades
Get grades for students.

**Query Parameters:**
- `student_id` (integer)
- `class_id` (integer)
- `subject` (string)
- `exam_type` (string)

### POST /api/grades
Add a grade.

**Request:**
```json
{
    "student_id": "integer",
    "class_id": "integer",
    "subject": "string",
    "exam_type": "string",
    "score": "number",
    "max_score": "number",
    "grade": "string",
    "remarks": "string"
}
```

### GET /api/report-cards/{student_id}
Generate student report card.

---

## Fee Management Endpoints

### GET /api/fees/student/{student_id}
Get fee records for a student.

### POST /api/fees
Create a fee record.

**Request:**
```json
{
    "student_id": "integer",
    "fee_type": "string",
    "amount": "number",
    "due_date": "string (YYYY-MM-DD)",
    "concession": "number",
    "concession_reason": "string"
}
```

### POST /api/fees/pay
Record fee payment.

**Request:**
```json
{
    "fee_id": "integer",
    "amount_paid": "number",
    "payment_method": "string",
    "transaction_id": "string"
}
```

### GET /api/fees/collection-report
Get fee collection report.

---

## Academic Year Endpoints

### GET /api/academic-years
Get all academic years.

### POST /api/academic-years
Create academic year.

**Request:**
```json
{
    "name": "2024-2025",
    "start_date": "2024-04-01",
    "end_date": "2025-03-31",
    "is_active": "boolean"
}
```

---

## GraphQL API

### Example Queries

#### Get All Students
```graphql
query {
  students {
    id
    firstName
    lastName
    email
    admissionNumber
    class {
      name
      section
    }
  }
}
```

#### Get Student by ID
```graphql
query {
  student(id: 1) {
    id
    firstName
    lastName
    attendance {
      date
      status
    }
    grades {
      subject
      score
      grade
    }
  }
}
```

#### Create Student
```graphql
mutation {
  createStudent(
    firstName: "John"
    lastName: "Doe"
    email: "john@school.com"
    admissionNumber: "STU001"
  ) {
    id
    firstName
    lastName
  }
}
```

### GraphQL Types
See the GraphQL schema documentation for complete type definitions.

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid data format |
| 500 | Internal Server Error |

---

## Rate Limiting
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

---

## API Versioning
All API endpoints are versioned. Current version: v1

Example: `/api/v1/students`
