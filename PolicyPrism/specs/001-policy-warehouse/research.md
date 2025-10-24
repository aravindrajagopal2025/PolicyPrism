# Research: Policy Warehouse

**Feature**: Policy Warehouse  
**Phase**: 0 - Research & Technology Selection  
**Date**: 2025-10-24

## Overview

This document resolves the 5 NEEDS CLARIFICATION items from the Technical Context and provides research-backed technology recommendations for building the policy warehouse system.

## Research Tasks

### 1. Language/Version Selection

**Decision**: Python 3.11 or above

**Rationale**:
- **LLM Ecosystem**: Python has the richest ecosystem for LLM/AI frameworks (LangChain, LlamaIndex, Haystack, OpenAI SDK, Anthropic SDK)
- **PDF Processing**: Mature libraries (PyPDF2, pdfplumber, pymupdf, pytesseract for OCR)
- **Web Frameworks**: FastAPI provides async support, automatic API documentation, and high performance
- **Data Science**: Strong support for data extraction, transformation, and validation (Pydantic, pandas)
- **Healthcare Domain**: Many healthcare data processing libraries available in Python

**Alternatives Considered**:
- **Node.js/TypeScript**: Good for web applications but weaker LLM/PDF ecosystem
- **Java/Kotlin**: Enterprise-ready but slower development velocity for AI/ML integration
- **Go**: Excellent performance but limited LLM framework support

### 2. Primary Dependencies

**Decision**: 
- **Web Framework**: FastAPI 0.104+ (async REST API with automatic OpenAPI docs)
- **AI Agentic Framework**: Pydantic AI (type-safe agentic AI framework with Pydantic integration)
- **PDF Processing**: pymupdf (PyMuPDF) 1.23+ for text extraction + pytesseract 0.3+ for OCR
- **Database ORM**: SQLAlchemy 2.0+ (async support, type safety, migration management)
- **Task Queue**: Celery 5.3+ with Redis (async document processing, retry logic, scheduling)
- **Search**: PostgreSQL full-text search (depending on scale requirements)
- **Authentication**: FastAPI-Users 12+ or Auth0 integration (role-based access control)

**Rationale**:
- **FastAPI**: Industry standard for Python APIs, excellent async support for long-running LLM calls
- **Pydantic AI**: Type-safe agentic AI framework with native Pydantic integration, excellent for structured data extraction from documents
- **pymupdf**: Fastest Python PDF library, handles both text and image-based PDFs
- **SQLAlchemy 2.0**: Modern async ORM with strong typing, supports complex relationships
- **Celery**: Battle-tested task queue for background processing, supports exponential backoff retry
- **PostgreSQL FTS**: Simpler deployment and integration with PostgreSQL database

**Alternatives Considered**:
- **LangChain vs Pydantic AI**: LangChain more mature but Pydantic AI offers better type safety and integration with FastAPI/Pydantic models
- **Django vs FastAPI**: Django more batteries-included but FastAPI better for async AI workloads
- **RabbitMQ vs Redis**: Redis simpler for task queue, RabbitMQ if complex routing needed

### 3. Storage Architecture

**Decision**:
- **Relational Database**: PostgreSQL 17 (structured policy data, relationships, versioning)
- **Object Storage**: Azure Blob (original PDF files)
- **Cache Layer**: Redis 7+ (search results, extraction confidence scores, session data)

**Rationale**:
- **PostgreSQL 17**: 
  - Latest features including improved JSON performance
  - Enhanced full-text search capabilities (pg_trgm, ts_vector)
  - ACID compliance for audit trails and versioning
  - Soft-delete support via deleted_at columns
  - Strong support for complex queries (policy comparisons)
  - Better performance for concurrent workloads
- **Object Storage**: 
  - Cost-effective for large PDF files
  - Scalable without database bloat
  - Supports versioning (S3 versioning, MinIO retention policies)
- **Redis**:
  - Fast caching for frequently accessed policies
  - Celery broker for task queue
  - Session storage for authentication

**Alternatives Considered**:
- **MongoDB**: Flexible schema but weaker for complex relational queries (policy comparisons)
- **MySQL**: Viable but PostgreSQL has better JSON and full-text search support
- **File System Storage**: Simple but doesn't scale, lacks versioning, no cloud-native support

### 4. Testing Strategy

**Decision**:
- **Unit Testing**: pytest 7+ with pytest-asyncio (async test support)
- **Integration Testing**: pytest with testcontainers (isolated database/Redis instances)
- **Contract Testing**: pytest with FastAPI TestClient (API endpoint validation)
- **LLM Testing**: pytest with mock LLM responses + small validation dataset
- **E2E Testing**: Playwright (frontend user journeys)

**Rationale**:
- **pytest**: Industry standard for Python, excellent plugin ecosystem
- **testcontainers**: Ensures tests run against real database/Redis without manual setup
- **Mock LLM**: Avoid API costs and rate limits in CI/CD, use fixtures for deterministic tests
- **Validation Dataset**: Small set of real Cigna policies (5-10) for extraction accuracy validation
- **Playwright**: Modern E2E framework, supports multiple browsers, good for testing search/comparison UI

**Test Coverage Goals**:
- Unit tests: 80%+ coverage for services and models
- Integration tests: All API endpoints, extraction pipeline end-to-end
- Contract tests: OpenAPI schema validation
- LLM validation: 90% accuracy on validation dataset (per SC-002)

**Alternatives Considered**:
- **unittest vs pytest**: pytest more Pythonic, better fixtures
- **Selenium vs Playwright**: Playwright faster, better async support
- **Real LLM vs Mock**: Real LLM in CI too slow/expensive, use staging environment for periodic validation

### 5. Target Platform & Deployment

**Decision**:
- **Platform**: Docker containers on Azure Kubernetes Service (AKS)
- **Cloud Provider**: Azure (AKS, Azure Database for PostgreSQL 17, Blob Storage, Azure Cache for Redis)
- **CI/CD**: GitHub Actions or GitLab CI
- **Monitoring**: Prometheus + Grafana (metrics), ELK Stack or CloudWatch (logs)

**Rationale**:
- **Containers**: Consistent environment across dev/staging/prod, easy scaling
- **Kubernetes**: Industry standard orchestration, supports auto-scaling for processing jobs
- **AWS/Azure**: Managed services reduce operational overhead (RDS, S3, Redis)
- **Cloud-Agnostic**: Docker + K8s allows migration between clouds if needed

**Deployment Architecture**:
```
┌──────────────────────────────────────────────────────────┐
│              Azure Load Balancer                          │
└────────────┬─────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼────┐
│Frontend│      │ Backend │
│ (React)│      │(FastAPI)│
│  (AKS) │      │  (AKS)  │
└────────┘      └────┬────┘
                     │
        ┌────────────┼──────────────────┐
        │            │                  │
   ┌────▼───────┐   ┌───▼──────────┐  ┌───▼─────────┐
   │ PostgreSQL │   │ Azure Cache  │  │Azure Blob   │
   │     17     │   │  for Redis   │  │Storage(PDFs)│
   │(Azure DB)  │   │              │  │             │
   └────────────┘   └───┬──────────┘  └─────────────┘
                        │
                  ┌─────▼──────┐
                  │   Celery   │
                  │  Workers   │
                  │(Extraction)│
                  │   (AKS)    │
                  └────────────┘
```

**Alternatives Considered**:
- **Serverless (Lambda)**: Not ideal for long-running LLM extraction (15min timeout)
- **VM-based**: More operational overhead than containers
- **Single-server**: Doesn't scale, no high availability

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | Backend development |
| Web Framework | FastAPI | 0.104+ | REST API |
| AI Agentic Framework | Pydantic AI | Latest | Document extraction |
| PDF Processing | pymupdf + pytesseract | 1.23+ / 0.3+ | Text/OCR extraction |
| Database | PostgreSQL | 17 | Structured data |
| ORM | SQLAlchemy | 2.0+ | Database access |
| Object Storage | Azure Blob Storage | - | PDF storage |
| Cache/Queue | Azure Cache for Redis | 7+ | Caching + Celery broker |
| Task Queue | Celery | 5.3+ | Async processing |
| Search | PostgreSQL FTS | 17 | Full-text search |
| Auth | FastAPI-Users or Auth0 | 12+ | RBAC |
| Testing | pytest + Playwright | 7+ / 1.40+ | Unit/Integration/E2E |
| Frontend | React + TypeScript | 18+ / 5+ | User interface |
| Deployment | Docker + AKS | - | Container orchestration |
| Cloud | Azure (AKS, PostgreSQL 17, Blob) | - | Infrastructure |

## LLM Provider Selection

**Decision**: OpenAI GPT-4 or Anthropic Claude 3 for initial development with Pydantic AI

**Rationale**:
- **GPT-4**: Strong structured output support, function calling for entity extraction
- **Claude 3**: Excellent for long documents (100K+ context), good at following extraction schemas
- **Pydantic AI Support**: Both providers supported through Pydantic AI's unified interface
- **Fallback Strategy**: Pydantic AI's abstraction layer enables easy provider switching

**Cost Considerations**:
- Estimate $0.01-0.05 per policy document for extraction (depending on length and model)
- Budget for ~1000 policies initially = $10-50 in LLM costs
- Consider fine-tuning smaller models (GPT-3.5) after validation dataset grows

**Alternatives Considered**:
- **Open-source LLMs (Llama 2, Mistral)**: Lower cost but requires self-hosting, lower accuracy
- **Azure OpenAI**: Good for enterprise compliance, similar to OpenAI
- **Google PaLM/Gemini**: Less mature LangChain integration

## Extraction Pipeline Design

**Approach**: Multi-stage extraction with confidence scoring using Pydantic AI

**Stages**:
1. **PDF Text Extraction**: pymupdf for text-based, pytesseract OCR for scanned
2. **Document Chunking**: Semantic chunking by section using custom logic
3. **Entity Extraction**: Pydantic AI agents with structured output (Pydantic models)
4. **Confidence Scoring**: LLM self-evaluation + rule-based validation
5. **Human Review Queue**: Policies with <85% confidence flagged (per FR-018)

**Extraction Schema Example**:
```python
class PolicyExtraction(BaseModel):
    policy_name: str
    payer_name: str
    effective_date: date
    expiration_date: Optional[date]
    sections: List[PolicySection]
    confidence_score: float  # 0.0-1.0

class PolicySection(BaseModel):
    section_type: Literal["coverage_criteria", "exclusions", "requirements", "definitions"]
    title: str
    content: str
    extracted_entities: Dict[str, Any]
    confidence_score: float
```

## Next Steps (Phase 1)

1. Create `data-model.md` with detailed entity schemas
2. Generate API contracts in `contracts/` directory
3. Create `quickstart.md` with development setup instructions
4. Update agent context files with technology stack
5. Re-run Constitution Check to validate design decisions

## Open Questions for Phase 1

- Should we use Elasticsearch or PostgreSQL FTS for search? (Depends on scale requirements)
- Which LLM provider should be primary? (Can decide based on initial testing)
- Should frontend be React or Vue.js? (React has larger ecosystem)
- Do we need real-time extraction status updates (WebSockets) or polling sufficient?
