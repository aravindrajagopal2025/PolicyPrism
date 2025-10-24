# Policy Warehouse - Quick Reference

## 🚀 Start the Application (3 Commands)

```bash
# 1. Start database services
docker-compose up -d

# 2. Setup and start backend (first time)
cd backend
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add OPENAI_API_KEY=your-key
alembic upgrade head
python scripts/seed_data.py

# 3. Run server
uvicorn src.main:app --reload
```

**Access**: http://localhost:8000/docs

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload Policy PDF
```bash
curl -X POST "http://localhost:8000/v1/ingestion/upload" \
  -F "file=@policy.pdf" \
  -F "payer_id=<cigna-uuid>"
```

### Check Job Status
```bash
curl http://localhost:8000/v1/ingestion/jobs/<job-id>
```

### List Policies
```bash
curl http://localhost:8000/v1/policies
```

### Get Policy Details
```bash
curl http://localhost:8000/v1/policies/<policy-id>
```

## 🔑 Default Credentials

```
Admin:
  username: admin
  password: admin123

Analyst:
  username: analyst
  password: analyst123
```

## 📊 Database Access

```bash
# Connect to PostgreSQL
docker exec -it policyprism-postgres-1 psql -U postgres -d policywarehouse

# Useful queries
SELECT * FROM users;
SELECT * FROM payers;
SELECT * FROM policy_documents;
SELECT * FROM processing_jobs;

# Get Cigna payer ID
SELECT id, name FROM payers WHERE name = 'Cigna';
```

## 🛠️ Common Tasks

### Reset Database
```bash
docker-compose down -v
docker-compose up -d
cd backend
alembic upgrade head
python scripts/seed_data.py
```

### View Logs
```bash
# Backend (in uvicorn terminal)
# Docker services
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Stop Services
```bash
docker-compose down
```

## 📁 Project Structure

```
PolicyPrism/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB sessions
│   │   ├── models/              # 9 SQLAlchemy models
│   │   ├── services/            # Business logic
│   │   ├── api/routes/          # API endpoints
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Migrations
│   ├── scripts/seed_data.py     # Initial data
│   └── requirements.txt         # Dependencies
├── docker-compose.yml           # PostgreSQL + Redis
├── GETTING_STARTED.md           # Detailed setup
└── IMPLEMENTATION_STATUS.md     # What's built
```

## ✅ What Works

- ✅ API server running
- ✅ Database with 8 entities
- ✅ PDF upload and validation
- ✅ Job tracking
- ✅ Policy listing
- ✅ Interactive API docs

## ❌ What's Missing

- ❌ Automatic PDF processing (needs Celery worker)
- ❌ LLM extraction (needs orchestration)
- ❌ Authentication (endpoints are open)
- ❌ Search functionality
- ❌ Frontend UI

## 🔗 Documentation

- **Getting Started**: `GETTING_STARTED.md`
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
- **API Docs**: http://localhost:8000/docs
- **Specification**: `specs/001-policy-warehouse/spec.md`
- **Tasks**: `specs/001-policy-warehouse/tasks.md`

## 💡 Tips

1. **Always activate venv**: `source backend/venv/bin/activate`
2. **Check health first**: `curl http://localhost:8000/health`
3. **Use API docs**: Interactive testing at `/docs`
4. **Get payer ID**: Query database for Cigna UUID
5. **Watch logs**: Keep uvicorn terminal visible

## 🐛 Troubleshooting

**Can't connect to database?**
```bash
docker-compose ps  # Check if running
docker-compose restart postgres
```

**Import errors?**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Port already in use?**
```bash
# Change port in command
uvicorn src.main:app --reload --port 8001
```

## 📈 Progress

**43/112 tasks complete (38%)**
- Phase 1: Setup ✅ 12/12
- Phase 2: Foundational 🟡 11/21
- Phase 3: P1 Ingest 🟡 12/22
- Phases 4-7: ⏸️ 0/57

**MVP Status**: Foundation complete, app is runnable with core API endpoints.

---

**Quick Start**: See `GETTING_STARTED.md` for detailed instructions.
