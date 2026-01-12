# SchoolOps Backend - Phase 1: Core API Foundation

## Overview

Phase 1 implements the foundational REST API for the SchoolOps school management system. This phase establishes authentication, student management, and prepares the infrastructure for self-hosted AI integration.

## Key Features Implemented

### 1. Authentication System (JWT + bcrypt)
- **User Registration**: Create accounts with email verification flow
- **Secure Login**: JWT-based authentication with access and refresh tokens
- **Password Security**: bcrypt hashing with configurable work factors
- **Role-Based Access Control**: granular permissions based on user roles
- **Token Management**: Automatic token expiration and refresh capability

### 2. Student Information System (SIS)
- **Complete CRUD Operations**: Create, read, update, delete students
- **Smart Filtering**: Filter by school, class, grade, section, status
- **Full-Text Search**: Search across names, emails, admission numbers
- **Pagination**: Efficient data loading with configurable page sizes
- **Guardian Management**: Link parents/guardians to students
- **Attendance Integration**: Built-in attendance tracking endpoints

### 3. Self-Hosted AI Architecture
- **Ollama Integration**: Ready for local LLM deployment (Llama 2, Mistral)
- **HuggingFace Support**: Configure local transformers models
- **Fallback Systems**: Rule-based fallbacks when AI is unavailable
- **Zero Per-Token Costs**: Runs entirely on your infrastructure

### 4. Performance Optimizations
- **Async Database**: PostgreSQL with asyncpg for high concurrency
- **Connection Pooling**: Configurable pool sizes with overflow protection
- **Prepared Statements**: Optimized query execution
- **Efficient Pagination**: OFFSET/LIMIT with count optimization

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user account |
| POST | `/api/v1/auth/login` | Authenticate and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout (client-side) |
| POST | `/api/v1/auth/change-password` | Change password (authenticated) |
| GET | `/api/v1/auth/me` | Get current user info |

### Students (`/api/v1/students`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/students` | List students with filters |
| GET | `/api/v1/students/{id}` | Get student details |
| POST | `/api/v1/students` | Create new student |
| PUT | `/api/v1/students/{id}` | Update student |
| DELETE | `/api/v1/students/{id}` | Soft delete (transfer) |
| GET | `/api/v1/students/{id}/guardians` | Get student guardians |
| POST | `/api/v1/students/{id}/guardians` | Add guardian to student |
| GET | `/api/v1/students/{id}/attendance` | Get attendance records |

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `super_admin` | Platform administrator | Full system access |
| `school_admin` | School administrator | Full school access |
| `principal` | School principal | Academic oversight |
| `teacher` | Teaching staff | Class management |
| `accountant` | Finance staff | Fee management |
| `librarian` | Library staff | Book management |
| `transport_manager` | Transport staff | Bus routing |
| `parent` | Parent/Guardian | View child records |
| `student` | Student | View own records |

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

```bash
# Clone the repository
cd schoolops-system/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
python -m app.db.database init_db

# Start the server
python main.py
```

### Environment Variables

```env
# Application
APP_NAME=SchoolOps API
DEBUG=True
API_VERSION=v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/schoolops
REDIS_URL=redis://localhost:6379

# JWT Authentication
SECRET_KEY=your-secure-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Self-Hosted AI (Ollama)
AI_SERVICE_URL=http://localhost:8001
```

## Self-Hosted AI Setup

### Option 1: Ollama (Recommended for LLMs)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model (Llama 2, Mistral, CodeLlama)
ollama pull llama2

# Configure in .env
AI_SERVICE_URL=http://localhost:11434
```

### Option 2: HuggingFace Local Models

```bash
# Install transformers with GPU support
pip install transformers accelerate torch

# Configure AI service for HuggingFace
```

### Fallback: Rule-Based Analysis

When AI services are unavailable, the system automatically falls back to rule-based analysis for:
- At-risk student detection (threshold-based)
- Lesson plan templates
- Performance recommendations

## Project Structure

```
backend/
├── app/
│   ├── api/                    # REST API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   └── students.py        # Student CRUD endpoints
│   ├── core/                  # Core utilities
│   │   └── security.py        # JWT & authorization
│   ├── db/                    # Database layer
│   │   └── database.py        # Async SQLAlchemy setup
│   ├── schema/                # Pydantic schemas
│   │   ├── auth_schema.py     # Auth request/response
│   │   └── student_schema.py  # Student schemas
│   ├── services/              # Business logic
│   │   └── ai_service.py      # Self-hosted AI
│   ├── config.py              # Settings
│   └── main.py                # Application entry
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## API Documentation

Access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/api/test_endpoints.py -v
```

## Performance Considerations

### Database Optimization
- Connection pooling: 10-20 connections
- Async queries with connection reuse
- Proper indexing on frequently queried columns

### Caching Strategy
- Redis for session management
- Query result caching for read-heavy endpoints
- Token blacklist for logout support

### Scaling
- Horizontal scaling with multiple workers
- Database read replicas for heavy reads
- CDN for static assets

## Security Best Practices

1. **Password Policy**: Minimum 8 characters, bcrypt hashing
2. **Token Security**: Short-lived access tokens (24h), refresh tokens (7d)
3. **CORS**: Configure allowed origins for your domain
4. **Rate Limiting**: Implement per-IP rate limiting (Redis-based)
5. **Audit Logging**: All sensitive actions logged with user, IP, timestamp

## Phase 1 Completion Checklist

- [x] Database models defined and verified
- [x] JWT authentication implemented
- [x] User registration and login endpoints
- [x] Student CRUD operations
- [x] Role-based access control
- [x] Pagination and filtering
- [x] Self-hosted AI architecture
- [x] API documentation generated
- [x] Unit tests written
- [x] Performance optimized

## Next Steps (Phase 2)

- Complete remaining CRUD operations (Staff, Classes, Subjects)
- Implement attendance marking system
- Add fee management and payment processing
- Integrate SMS gateway for notifications
- Complete AI service integration

## License

MIT License - See LICENSE file for details.
