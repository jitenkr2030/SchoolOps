# SchoolOps Setup & Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Clone Repository](#clone-repository)
3. [Backend Setup](#backend-setup)
4. [AI Services Setup](#ai-services-setup)
5. [Frontend Setup](#frontend-setup)
6. [Environment Configuration](#environment-configuration)
7. [Database Setup](#database-setup)
8. [Running the Application](#running-the-application)
9. [Docker Setup (Optional)](#docker-setup-optional)
10. [Verification](#verification)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / macOS 10.15+ / Windows 10+
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: Minimum 50GB free space
- **CPU**: Multi-core processor

### Required Software

#### For All Platforms
- **Git**: Version 2.0 or higher
  ```bash
  # Check version
  git --version
  
  # Install if needed
  # Ubuntu/Debian:
  sudo apt-get install git
  
  # macOS:
  brew install git
  
  # Windows:
  # Download from https://git-scm.com/
  ```

- **Python**: Version 3.10 or higher
  ```bash
  # Check version
  python3 --version
  
  # Install if needed
  # Ubuntu/Debian:
  sudo apt-get install python3.10 python3-pip python3-venv
  
  # macOS:
  brew install python@3.10
  
  # Windows:
  # Download from https://www.python.org/downloads/
  ```

- **Node.js**: Version 18.0 or higher
  ```bash
  # Check version
  node --version
  
  # Install if needed
  # Using nvm (recommended):
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
  nvm install 18
  ```

- **PostgreSQL**: Version 14 or higher
  ```bash
  # Check version
  psql --version
  
  # Install if needed
  # Ubuntu/Debian:
  sudo apt-get install postgresql postgresql-contrib
  
  # macOS:
  brew install postgresql
  
  # Windows:
  # Download from https://www.postgresql.org/download/windows/
  ```

#### Optional but Recommended
- **Docker & Docker Compose**: For containerized deployment
  ```bash
  # Check Docker
  docker --version
  docker-compose --version
  
  # Install Docker
  # Ubuntu: https://docs.docker.com/engine/install/ubuntu/
  # macOS: https://docs.docker.com/desktop/mac/install/
  # Windows: https://docs.docker.com/desktop/windows/install/
  ```

---

## Clone Repository

```bash
# Clone the repository
git clone https://github.com/jitenkr2030/SchoolOps.git

# Navigate to project directory
cd SchoolOps

# Navigate to project structure
cd schoolops-system
```

---

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

**Key Dependencies Installed:**
- fastapi==0.104.0
- uvicorn==0.24.0
- sqlalchemy==2.0.0
- strawberry-graphql==0.217.0
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- python-multipart==0.0.6
- httpx==0.25.0
- pytest==7.4.0

### 4. Environment Configuration
Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://schoolops:schoolops123@localhost:5432/schoolops_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=schoolops_db
DATABASE_USER=schoolops
DATABASE_PASSWORD=schoolops123

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Configuration
DEBUG=True
API_VERSION=v1
ENVIRONMENT=development

# AI Services URL
AI_SERVICES_URL=http://localhost:8001

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@schoolops.com

# SMS Configuration (Optional)
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=SCHOOL

# Redis Configuration (Optional, for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 5. Database Setup
```bash
# Create database
sudo -u postgres psql

# In psql shell:
CREATE DATABASE schoolops_db;
CREATE USER schoolops WITH ENCRYPTED PASSWORD 'schoolops123';
GRANT ALL PRIVILEGES ON DATABASE schoolops_db TO schoolops;

# Exit psql
\q
```

### 6. Initialize Database
```bash
# Run database migrations
alembic upgrade head

# Or create tables from models
python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## AI Services Setup

### 1. Navigate to AI Services Directory
```bash
cd ai-services
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

**Key Dependencies Installed:**
- fastapi==0.104.0
- uvicorn==0.24.0
- torch==2.1.0
- transformers==4.35.0
- langchain==0.1.0
- openai==1.3.0
- paddlepaddle==2.5.0
- pytesseract==0.3.10
- pillow==10.0.0
- pytest==7.4.0

### 4. Additional AI Dependencies

**For OCR (Tesseract):**
```bash
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

**For NLP Models:**
```bash
# Download required models (automatically handled on first run)
# Models will be cached in ~/.cache/huggingface/
```

### 5. Environment Configuration
Create a `.env` file in the `ai-services` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=False

# Database (shared with backend)
DATABASE_URL=postgresql://schoolops:schoolops123@localhost:5432/schoolops_db

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Model Configuration
AI_MODEL_PATH=./models
AI_DEVICE=cpu  # or cuda for GPU

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# HuggingFace Configuration
HF_TOKEN=your-huggingface-token

# Document Processing
OCR_ENGINE=tesseract  # or paddle
MAX_IMAGE_SIZE=10485760  # 10MB

# Logging
LOG_LEVEL=INFO
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
# Install Node.js dependencies
npm install
```

**Key Dependencies Installed:**
- next==14.0.0
- react==18.2.0
- react-dom==18.2.0
- @apollo/client==3.8.0
- graphql==16.8.0
- axios==1.6.0
- tailwindcss==3.3.0
- typescript==5.3.0

### 3. Environment Configuration
Create a `.env.local` file in the `frontend` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8000/graphql
NEXT_PUBLIC_AI_SERVICES_URL=http://localhost:8001

# Authentication
NEXTAUTH_SECRET=your-nextauth-secret-key
NEXTAUTH_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_FEATURES=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
```

### 4. Configure TypeScript
Ensure `tsconfig.json` has proper paths configured:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"]
    }
  }
}
```

### 5. Configure Tailwind CSS
Ensure `tailwind.config.js` is properly set up:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
}
```

---

## Running the Application

### Option 1: Run All Services Separately

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - AI Services:**
```bash
cd ai-services
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Run Using Docker Compose

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 3: Run in Production Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

---

## Access the Application

Once running, access the application at:

- **Web Application**: http://localhost:3000
- **REST API**: http://localhost:8000/api/v1
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs
- **AI Services**: http://localhost:8001

---

## Default Login Credentials

After database initialization, you can log in with:

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@schoolops.com | admin123 |
| School Admin | principal@schoolops.com | admin123 |
| Teacher | teacher@schoolops.com | teacher123 |
| Accountant | accountant@schoolops.com | admin123 |

**⚠️ Important**: Change these passwords immediately after first login!

---

## Docker Setup (Optional)

### 1. Create Docker Environment File

Create `.env.docker` in project root:

```env
# Database
POSTGRES_DB=schoolops_db
POSTGRES_USER=schoolops
POSTGRES_PASSWORD=schoolops123

# Backend
DATABASE_URL=postgresql://schoolops:schoolops123@db:5432/schoolops_db

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2. Create Docker Compose File

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: schoolops_db
      POSTGRES_USER: schoolops
      POSTGRES_PASSWORD: schoolops123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U schoolops -d schoolops_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://schoolops:schoolops123@db:5432/schoolops_db
      REDIS_HOST: redis
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - backend_models:/app/models

  ai-services:
    build: ./ai-services
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://schoolops:schoolops123@db:5432/schoolops_db
      REDIS_HOST: redis
    depends_on:
      - backend
    volumes:
      - ./ai-services:/app
      - ai_models:/app/models

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
      NEXT_PUBLIC_GRAPHQL_URL: http://localhost:8000/graphql
      NEXT_PUBLIC_AI_SERVICES_URL: http://localhost:8001
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  backend_models:
  ai_models:
```

### 3. Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Verification

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### 2. Check API Documentation
Open in browser: http://localhost:8000/docs

### 3. Check GraphQL Playground
Open in browser: http://localhost:8000/graphql

### 4. Check Frontend
Open in browser: http://localhost:3000

### 5. Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=app

# AI Services tests
cd ai-services
python -m pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

---

## Troubleshooting

### Database Connection Issues

**Problem**: Cannot connect to database
**Solutions**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check connection
psql -h localhost -U schoolops -d schoolops_db
```

### Port Already in Use

**Problem**: Port 8000/3000 already in use
**Solutions**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill <PID>

# Or use different port
uvicorn main:app --port 8001
```

### Module Not Found Errors

**Problem**: Python module not found
**Solutions**:
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Clear cache
pip cache purge
```

### Node Modules Issues

**Problem**: Node modules not found
**Solutions**:
```bash
# Remove node_modules
rm -rf node_modules

# Clear npm cache
npm cache clean --force

# Reinstall
npm install
```

### Permission Errors

**Problem**: Permission denied
**Solutions**:
```bash
# Linux/macOS
sudo chown -R $USER:$USER .

# Or use virtual environment without sudo
```

### Out of Memory

**Problem**: AI models running out of memory
**Solutions**:
```bash
# Reduce batch size
# Use CPU instead of GPU
# Add swap space
```

### For Additional Help
- Email: support@schoolops.com
- Documentation: https://docs.schoolops.com
- GitHub Issues: https://github.com/jitenkr2030/SchoolOps/issues
