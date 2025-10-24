# Quickstart Guide: Policy Warehouse

**Feature**: Policy Warehouse  
**Branch**: `001-policy-warehouse`  
**Date**: 2025-10-24

## Overview

This guide provides step-by-step instructions for setting up the Policy Warehouse development environment and running the system locally.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Policy Warehouse System                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Frontend   │───▶│   FastAPI    │───▶│ PostgreSQL   │ │
│  │   (React)    │    │   Backend    │    │      17      │ │
│  └──────────────┘    └──────┬───────┘    └──────────────┘ │
│                              │                               │
│                              ▼                               │
│                      ┌──────────────┐                       │
│                      │  Pydantic AI │                       │
│                      │    Agent     │                       │
│                      └──────┬───────┘                       │
│                              │                               │
│                              ▼                               │
│                      ┌──────────────┐                       │
│                      │    Celery    │                       │
│                      │   Workers    │                       │
│                      └──────┬───────┘                       │
│                              │                               │
│                    ┌─────────┴─────────┐                   │
│                    ▼                   ▼                     │
│            ┌──────────────┐    ┌──────────────┐           │
│            │ Azure Blob   │    │ Azure Cache  │           │
│            │   Storage    │    │  for Redis   │           │
│            │   (PDFs)     │    │              │           │
│            └──────────────┘    └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Software

- **Python**: 3.11 or above
- **Node.js**: 18+ (for frontend)
- **Docker**: Latest version (for local PostgreSQL and Redis)
- **Git**: Latest version

### Required Accounts

- **Azure Account**: For Blob Storage and Cache for Redis (or use local alternatives)
- **OpenAI or Anthropic API Key**: For LLM-based extraction

### Recommended Tools

- **VS Code** or **PyCharm**: IDE with Python support
- **Postman** or **Insomnia**: API testing
- **pgAdmin** or **DBeaver**: Database management
- **Azure Storage Explorer**: For managing blob storage

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd PolicyPrism
git checkout 001-policy-warehouse
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt** (create if not exists):
```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI/LLM
pydantic-ai==0.0.1  # Latest version
openai==1.3.0
anthropic==0.7.0

# PDF Processing
pymupdf==1.23.8
pytesseract==0.3.10
Pillow==10.1.0

# Database
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1

# Task Queue
celery==5.3.4
redis==5.0.1

# Authentication
fastapi-users[sqlalchemy]==12.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Azure SDK
azure-storage-blob==12.19.0
azure-identity==1.15.0

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
testcontainers==3.7.1
playwright==1.40.0
```

#### Configure Environment

Create `.env` file in `backend/` directory:

```bash
# Application
APP_NAME=PolicyWarehouse
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/policywarehouse
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Azure Storage (or use local storage for development)
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=policy-pdfs
# For local development, use local file storage:
# LOCAL_STORAGE_PATH=./storage/pdfs

# LLM Provider
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key

# Pydantic AI Configuration
PYDANTIC_AI_MODEL=gpt-4  # or claude-3-opus-20240229
PYDANTIC_AI_TEMPERATURE=0.1
PYDANTIC_AI_MAX_TOKENS=4000

# Processing Configuration
MAX_RETRIES=3
RETRY_BACKOFF_BASE=2
EXTRACTION_CONFIDENCE_THRESHOLD=0.85
HUMAN_REVIEW_FIRST_N_POLICIES=5

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### Start Local Services

Using Docker Compose:

```bash
# Create docker-compose.yml in project root
docker-compose up -d
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: policywarehouse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

#### Seed Initial Data

```bash
# Create seed script
python scripts/seed_data.py
```

**scripts/seed_data.py**:
```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models import User, Payer
from src.auth import get_password_hash
import os

async def seed_database():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="ADMINISTRATOR",
            is_active=True
        )
        session.add(admin)
        
        # Create Cigna payer
        cigna = Payer(
            name="Cigna",
            website_url="https://www.cigna.com",
            is_active=True
        )
        session.add(cigna)
        
        await session.commit()
        print("✅ Database seeded successfully")

if __name__ == "__main__":
    asyncio.run(seed_database())
```

#### Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

#### Start Celery Worker

In a separate terminal:

```bash
cd backend
source venv/bin/activate
celery -A src.celery_app worker --loglevel=info
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

#### Configure Environment

Create `.env` file in `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/v1
VITE_APP_NAME=Policy Warehouse
```

#### Start Frontend Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173` or `http://localhost:3000`

## Development Workflow

### 1. Upload a Policy Document

```bash
curl -X POST http://localhost:8000/v1/ingestion/upload \
  -H "Authorization: Bearer <your-token>" \
  -F "payer_id=<cigna-uuid>" \
  -F "file=@/path/to/policy.pdf"
```

### 2. Check Processing Status

```bash
curl http://localhost:8000/v1/ingestion/jobs/<job-id> \
  -H "Authorization: Bearer <your-token>"
```

### 3. Search Policies

```bash
curl -X POST http://localhost:8000/v1/search \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "prior authorization",
    "limit": 10
  }'
```

### 4. Compare Policies

```bash
curl -X POST http://localhost:8000/v1/comparison \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_document_ids": ["<uuid1>", "<uuid2>"],
    "comparison_topic": "knee replacement surgery"
  }'
```

## Testing

### Run Unit Tests

```bash
cd backend
pytest tests/unit -v
```

### Run Integration Tests

```bash
pytest tests/integration -v
```

### Run Contract Tests

```bash
pytest tests/contract -v
```

### Run E2E Tests

```bash
cd frontend
npm run test:e2e
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

## Key Components

### Backend Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── policy.py
│   │   ├── user.py
│   │   └── payer.py
│   ├── services/
│   │   ├── ingestion/          # PDF upload and validation
│   │   │   ├── uploader.py
│   │   │   └── validator.py
│   │   ├── extraction/         # Pydantic AI extraction
│   │   │   ├── pdf_extractor.py
│   │   │   ├── llm_agent.py
│   │   │   └── confidence_scorer.py
│   │   ├── search/             # Full-text search
│   │   │   └── search_engine.py
│   │   ├── comparison/         # Policy comparison
│   │   │   └── comparator.py
│   │   └── scraping/           # Automated scraping
│   │       ├── scraper.py
│   │       └── scheduler.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ingestion.py
│   │   │   ├── policies.py
│   │   │   ├── search.py
│   │   │   ├── comparison.py
│   │   │   ├── scraping.py
│   │   │   └── admin.py
│   │   ├── auth/
│   │   │   └── jwt.py
│   │   └── middleware/
│   │       ├── audit_logger.py
│   │       └── error_handler.py
│   ├── utils/
│   │   ├── pdf_processor.py
│   │   ├── retry_logic.py
│   │   └── validators.py
│   └── celery_app.py           # Celery configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── alembic/                    # Database migrations
├── requirements.txt
└── .env
```

### Pydantic AI Integration

Example extraction agent:

```python
# src/services/extraction/llm_agent.py
from pydantic import BaseModel
from pydantic_ai import Agent
from datetime import date
from typing import Optional, List

class PolicyExtraction(BaseModel):
    policy_name: str
    payer_name: str
    effective_date: date
    expiration_date: Optional[date]
    sections: List['PolicySection']
    confidence_score: float

class PolicySection(BaseModel):
    section_type: str
    title: str
    content: str
    confidence_score: float

# Create Pydantic AI agent
policy_agent = Agent(
    model='openai:gpt-4',
    result_type=PolicyExtraction,
    system_prompt="""
    You are an expert at extracting structured information from healthcare policy documents.
    Extract the policy name, payer, dates, and organize content into logical sections.
    Provide a confidence score (0.0-1.0) for each extraction.
    """
)

async def extract_policy_data(pdf_text: str) -> PolicyExtraction:
    result = await policy_agent.run(pdf_text)
    return result.data
```

### Celery Tasks

```python
# src/celery_app.py
from celery import Celery
from src.config import settings

celery_app = Celery(
    'policy_warehouse',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
)

# Task for processing policy documents
@celery_app.task(bind=True, max_retries=3)
def process_policy_document(self, policy_document_id: str):
    try:
        # Extract text from PDF
        # Run Pydantic AI extraction
        # Store structured data in PostgreSQL
        pass
    except Exception as exc:
        # Exponential backoff retry
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U postgres -d policywarehouse
```

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

### Celery Worker Not Processing

```bash
# Check Celery worker logs
celery -A src.celery_app inspect active

# Purge queue
celery -A src.celery_app purge
```

### LLM API Errors

- Verify API key is set correctly in `.env`
- Check API rate limits
- Review error logs for specific error messages

### PDF Extraction Failures

- Ensure Tesseract OCR is installed: `brew install tesseract` (Mac) or `apt-get install tesseract-ocr` (Linux)
- Verify PDF file is not corrupted
- Check PDF file size limits

## Next Steps

1. **Implement User Stories**: Start with P1 (Ingest Policy Documents)
2. **Add Tests**: Write tests for each service component
3. **Configure CI/CD**: Set up GitHub Actions or Azure DevOps pipelines
4. **Deploy to Azure**: Set up AKS cluster and deploy containers
5. **Monitor**: Configure Application Insights and logging

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Azure Kubernetes Service](https://learn.microsoft.com/en-us/azure/aks/)
- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/17/release-17.html)

## Support

For questions or issues:
- Check existing documentation in `specs/001-policy-warehouse/`
- Review API contracts in `contracts/api-spec.yaml`
- Consult data model in `data-model.md`
- Review research decisions in `research.md`
