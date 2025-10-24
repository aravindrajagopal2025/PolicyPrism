# Getting Started with Policy Warehouse

## Quick Start Guide

This guide will help you get the Policy Warehouse application running locally.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI or Anthropic API key

## Step 1: Start Database Services

```bash
# Start PostgreSQL 17 and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Step 3: Configure Environment

Edit `backend/.env` and set:

```bash
# Required: Set your API key
OPENAI_API_KEY=your-openai-api-key-here
# OR
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database (default works with docker-compose)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/policywarehouse

# For local development, use local storage
LOCAL_STORAGE_PATH=./storage/pdfs
```

## Step 4: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed initial data (creates admin user and Cigna payer)
python scripts/seed_data.py
```

You should see:
```
✅ Database seeded successfully!

Default credentials:
  Admin - username: admin, password: admin123
  Analyst - username: analyst, password: analyst123
```

## Step 5: Start Backend Server

```bash
# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Step 6: Test the API

### Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Upload a Policy Document

```bash
# Get the Cigna payer ID first
# You can find it in the database or use the API once we add payers endpoint

# Upload a PDF (replace with actual PDF path and payer ID)
curl -X POST "http://localhost:8000/v1/ingestion/upload" \
  -F "file=@/path/to/policy.pdf" \
  -F "payer_id=<cigna-payer-uuid>"
```

Expected response:
```json
{
  "policy_document_id": "uuid-here",
  "processing_job_id": "uuid-here",
  "status": "QUEUED",
  "message": "Document uploaded successfully and queued for processing"
}
```

### Check Job Status

```bash
curl http://localhost:8000/v1/ingestion/jobs/<job-id>
```

### List Policies

```bash
curl http://localhost:8000/v1/policies
```

## Current Features

✅ **Working**:
- Database models and migrations
- PDF upload and validation
- Basic API endpoints (ingestion, policies)
- Health check
- Local file storage

⏳ **In Progress** (not yet implemented):
- Celery worker for async processing
- Pydantic AI extraction pipeline
- Authentication/authorization
- Frontend UI
- Search functionality
- Policy comparison

## Development Workflow

### View API Documentation

Open http://localhost:8000/docs in your browser to see:
- All available endpoints
- Request/response schemas
- Try out API calls interactively

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it policyprism-postgres-1 psql -U postgres -d policywarehouse

# List tables
\dt

# Query data
SELECT * FROM users;
SELECT * FROM payers;
SELECT * FROM policy_documents;

# Exit
\q
```

### View Logs

```bash
# Backend logs (in terminal where uvicorn is running)

# Docker logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

## Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart postgres

# Check connection
docker exec -it policyprism-postgres-1 psql -U postgres -c "SELECT 1"
```

### Import Errors

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration Errors

```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
python scripts/seed_data.py
```

## Next Steps

To complete the MVP, you'll need to implement:

1. **Celery Worker** (T043): For async document processing
2. **Extraction Pipeline** (T041): Orchestrate PDF → Pydantic AI → Database
3. **Storage Service** (T044): Persist extracted data
4. **Frontend** (T051-T055): Upload interface and policy viewer

See `specs/001-policy-warehouse/tasks.md` for the complete task list.

## Project Structure

```
PolicyPrism/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app ✅
│   │   ├── config.py            # Configuration ✅
│   │   ├── database.py          # DB session ✅
│   │   ├── models/              # SQLAlchemy models ✅
│   │   ├── services/            # Business logic (partial)
│   │   ├── api/routes/          # API endpoints (partial)
│   │   └── utils/               # Utilities (partial)
│   ├── alembic/                 # Migrations ✅
│   ├── scripts/                 # Seed data ✅
│   └── requirements.txt         # Dependencies ✅
├── docker-compose.yml           # Local services ✅
└── README.md                    # Project overview ✅
```

## Support

For issues or questions:
- Check `specs/001-policy-warehouse/` for detailed documentation
- Review API docs at http://localhost:8000/docs
- See `tasks.md` for implementation status
