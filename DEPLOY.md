# SchoolOps Deployment Guide

This document provides comprehensive instructions for deploying the SchoolOps School Management System using Docker containers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Configuration](#environment-configuration)
4. [Available Deployment Options](#available-deployment-options)
5. [Post-Deployment Setup](#post-deployment-setup)
6. [Managing the Deployment](#managing-the-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Production Considerations](#production-considerations)

---

## Prerequisites

Before you begin, ensure your system meets the following requirements:

### System Requirements

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (or Docker Desktop)
- **Memory**: Minimum 4GB RAM (8GB recommended for AI features)
- **Storage**: Minimum 10GB free disk space

### Required Software

Verify your installation by running:

```bash
docker --version
docker-compose --version
```

For GPU support (optional, for faster AI inference):
- NVIDIA Driver: Version 525.0 or higher
- NVIDIA Container Toolkit

---

## Quick Start

The fastest way to get SchoolOps running:

```bash
# 1. Navigate to the project directory
cd schoolops-system

# 2. Copy the environment template
cp .env.example .env

# 3. Create data directories
mkdir -p data/postgres data/ollama

# 4. Start all services
docker-compose up -d

# 5. Verify services are running
docker-compose ps
```

Access the application:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Environment Configuration

### Required Settings

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_USER=schoolops
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=schoolops

# Application Configuration
SECRET_KEY=your-32-character-secret-key-here
ENVIRONMENT=production
DEBUG=false

# AI Configuration (Optional)
OLLAMA_BASE_URL=http://ollama:11434
AI_MODEL=llama3
```

### Security Recommendations

For production deployments:

1. **Generate a strong secret key**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use strong database passwords**: At least 16 characters with mixed case, numbers, and symbols.

3. **Never commit `.env` to version control**: Add it to your `.gitignore`.

---

## Available Deployment Options

### Option 1: Full Stack (Recommended)

Deploys all services including AI features:

```bash
docker-compose --profile full-stack up -d
```

**Includes**:
- PostgreSQL Database
- Redis Cache
- Ollama AI Service
- Backend API
- Frontend (development)

### Option 2: Backend Only

For environments with external database and AI services:

```bash
docker-compose --profile backend-only up -d
```

**Includes**:
- PostgreSQL Database
- Redis Cache
- Ollama AI Service
- Backend API

### Option 3: Minimal

Lightweight deployment for testing:

```bash
docker-compose --profile minimal up -d
```

**Includes**:
- PostgreSQL Database
- Backend API only

### Option 4: Custom Services

Start specific services only:

```bash
# Database only
docker-compose up -d db

# Database + Backend
docker-compose up -d db backend

# Database + Backend + Ollama
docker-compose up -d db backend ollama
```

---

## Post-Deployment Setup

### 1. Initialize the Database

The database tables are automatically created on application startup. To run migrations manually:

```bash
docker-compose exec backend python -m alembic upgrade head
```

### 2. Pull AI Model (Optional)

For AI features, pull a language model:

```bash
# Pull the default model (llama3, ~4GB)
docker-compose exec ollama ollama pull llama3

# Or use a smaller model for limited resources
docker-compose exec ollama ollama pull llama3.2:1b
```

### 3. Create Initial Admin User

```bash
docker-compose exec backend python -c "
from app.db.database import async_session
from app.db.models.user import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with async_session() as session:
        admin = User(
            email='admin@schoolops.local',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True,
            role='admin'
        )
        session.add(admin)
        await session.commit()
        print('Admin user created')

asyncio.run(create_admin())
"

# Change default password immediately after first login!
```

### 4. Verify Installation

Run the built-in tests:

```bash
docker-compose exec backend pytest tests/ -v --tb=short
```

---

## Managing the Deployment

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d db backend

# Start with rebuild
docker-compose up -d --build
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (data will be lost!)
docker-compose down -v

# Stop specific services
docker-compose stop db
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail 100 backend
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backing Up Data

```bash
# Backup PostgreSQL database
docker-compose exec db pg_dump -U schoolops schoolops > backup_$(date +%Y%m%d).sql

# Backup all volumes
docker run --rm -v schoolops-system_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v schoolops-system_ollama_models:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz -C /data .
```

### Restoring Data

```bash
# Restore PostgreSQL database
docker-compose exec -T db psql -U schoolops schoolops < backup_20240101.sql
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Refused

**Error**: `could not connect to server: Connection refused`

**Solution**:
```bash
# Check if database is healthy
docker-compose ps

# Wait for database to be ready
docker-compose exec db pg_isready -U schoolops

# Restart database
docker-compose restart db
```

#### 2. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Check what's using the port
lsof -i :8000

# Change the port in .env
BACKEND_PORT=8001
```

#### 3. Out of Memory

**Error**: `Killed signal terminated program`

**Solution**:
```bash
# Increase Docker memory limit
# Or use a smaller AI model
docker-compose exec ollama ollama pull llama3.2:1b
```

#### 4. AI Model Not Found

**Error**: `model not found`

**Solution**:
```bash
# Pull the model
docker-compose exec ollama ollama pull llama3

# Or pull a smaller model
docker-compose exec ollama ollama pull llama3.2:1b
```

#### 5. Permission Denied

**Error**: `Permission denied` when creating directories

**Solution**:
```bash
# Create directories with proper permissions
sudo mkdir -p data/postgres data/ollama
sudo chown -R $(id -u):$(id -g) data/
```

### Health Check Commands

```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
docker-compose exec backend python -c "from app.db.database import engine; import asyncio; asyncio.run(engine.connect())"

# Check Ollama status
curl http://localhost:11434/api/tags

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Viewing Service Status

```bash
# All containers
docker-compose ps

# Detailed container info
docker-compose inspect backend

# Resource usage
docker stats
```

---

## Production Considerations

### 1. Security Hardening

#### Use a Reverse Proxy
Deploy behind Nginx or Traefik for:
- HTTPS termination
- Rate limiting
- Request caching
- Load balancing

#### Enable HTTPS
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Set Up Firewall
```bash
# Allow only necessary ports
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Resource Management

#### Monitor Resource Usage
```bash
# Docker stats
docker stats

# Container resource limits (add to docker-compose.yml)
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

#### Set Up Logging
```yaml
# In docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

For production logging, consider:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki with Grafana
- CloudWatch (AWS)
- Azure Monitor (Azure)

### 3. High Availability

#### Multiple Replicas
```yaml
services:
  backend:
    deploy:
      replicas: 3
    
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

Use a database cluster (Patroni, pgBouncer) for PostgreSQL high availability.

#### Load Balancer
```nginx
upstream schoolops_backend {
    server backend:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### 4. Backup Strategy

#### Automated Backups
```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T db pg_dump -U schoolops schoolops | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Retain last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

### 5. Environment-Specific Configurations

#### Development
```bash
ENVIRONMENT=development
DEBUG=true
AI_MODEL=llama3.2:1b
```

#### Staging
```bash
ENVIRONMENT=staging
DEBUG=false
AI_MODEL=llama3
```

#### Production
```bash
ENVIRONMENT=production
DEBUG=false
AI_MODEL=llama3
CORS_ORIGINS=https://your-domain.com
```

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Project Repository**: [GitHub Link]
- **Issue Tracker**: [Link]
- **Community Support**: [Link]

---

## Support

For deployment issues:
1. Check this troubleshooting guide
2. Review container logs: `docker-compose logs`
3. Search existing issues
4. Create a new issue with:
   - Docker and Docker Compose versions
   - Operating system
   - Complete error messages
   - Steps to reproduce
