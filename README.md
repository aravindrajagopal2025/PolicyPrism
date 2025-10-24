# Policy Warehouse

A healthcare policy document management system that uses AI to extract and structure policy information from PDFs.

## Features

- **Document Ingestion**: Upload PDF policy documents with automatic text extraction (including OCR)
- **AI-Powered Extraction**: Uses Pydantic AI with LLMs to structure unstructured policy data
- **Search & Query**: Full-text search across all ingested policies
- **Policy Comparison**: Compare coverage criteria across different payers
- **Automated Scraping**: Schedule automatic policy document updates from payer websites

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic AI
- **Database**: PostgreSQL 17
- **Storage**: Azure Blob Storage
- **Cache/Queue**: Azure Cache for Redis, Celery
- **Frontend**: React 18+, TypeScript, Vite
- **Deployment**: Azure Kubernetes Service (AKS)

## 🚀 Quick Start (3 Steps)

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI or Anthropic API key

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Setup Backend
```bash
cd backend
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add your OPENAI_API_KEY or ANTHROPIC_API_KEY
alembic upgrade head
python scripts/seed_data.py
```

### 3. Run Application
```bash
uvicorn src.main:app --reload
```

**Access**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Default Credentials**:
- Admin: `admin` / `admin123`
- Analyst: `analyst` / `analyst123`

📖 **Detailed Guide**: See [GETTING_STARTED.md](GETTING_STARTED.md)

## Development

### Project Structure

```
PolicyPrism/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── services/        # Business logic
│   │   ├── api/             # FastAPI routes
│   │   └── utils/           # Utilities
│   └── tests/               # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   └── services/        # API clients
│   └── tests/               # Frontend tests
└── specs/                   # Feature specifications
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend E2E tests
cd frontend
npm run test:e2e
```

## 📚 Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Commands and API examples
- **[Getting Started](GETTING_STARTED.md)** - Detailed setup guide
- **[Implementation Status](IMPLEMENTATION_STATUS.md)** - What's built and what's next
- **[Feature Specification](specs/001-policy-warehouse/spec.md)** - Requirements and user stories
- **[Implementation Plan](specs/001-policy-warehouse/plan.md)** - Technical architecture
- **[Data Model](specs/001-policy-warehouse/data-model.md)** - Database schema
- **[API Specification](specs/001-policy-warehouse/contracts/api-spec.yaml)** - OpenAPI contract
- **[Tasks](specs/001-policy-warehouse/tasks.md)** - Implementation checklist

## 📊 Current Status

**Progress**: 43/112 tasks complete (38%)

✅ **Working**:
- FastAPI backend with 7 endpoints
- PostgreSQL 17 database with 8 entities
- PDF upload and validation
- Policy listing and retrieval
- Interactive API documentation

⏳ **In Progress**:
- Async processing pipeline (Celery)
- Pydantic AI extraction
- Authentication/authorization
- Frontend UI

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for details.

## License

Proprietary
