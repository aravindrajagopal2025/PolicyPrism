# Implementation Tasks: Policy Warehouse

**Feature**: Policy Warehouse  
**Branch**: `001-policy-warehouse`  
**Generated**: 2025-10-24

## Overview

This document provides a complete, dependency-ordered task list for implementing the Policy Warehouse feature. Tasks are organized by user story priority (P1 → P2 → P3 → P4) to enable incremental delivery and independent testing.

**Tech Stack**:
- Backend: Python 3.11+, FastAPI 0.104+, Pydantic AI
- Database: PostgreSQL 17, SQLAlchemy 2.0+
- Storage: Azure Blob Storage
- Cache/Queue: Azure Cache for Redis, Celery 5.3+
- Testing: pytest 7+
- Deployment: Azure Kubernetes Service (AKS)

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - Ingest Policy Documents
- Provides immediate value: Upload PDF → Extract structured data → Store in database
- Independently testable and deployable
- Foundation for all other features

**Incremental Delivery**:
1. **Phase 1-2**: Setup + Foundational infrastructure
2. **Phase 3 (P1)**: Document ingestion and extraction (MVP)
3. **Phase 4 (P2)**: Search and query capabilities
4. **Phase 5 (P3)**: Cross-payer comparison
5. **Phase 6 (P4)**: Automated scraping
6. **Phase 7**: Polish and cross-cutting concerns

## Dependencies

### User Story Completion Order

```
Setup (Phase 1) → Foundational (Phase 2) → P1 → P2 → P3 → P4 → Polish
                                            ↓    ↓    ↓    ↓
                                         (Independent after foundational)
```

**Story Dependencies**:
- **P1 (Ingest)**: No dependencies (can start after foundational)
- **P2 (Search)**: Requires P1 (needs policies in database)
- **P3 (Compare)**: Requires P1 + P2 (needs multiple policies and search capability)
- **P4 (Scraping)**: Requires P1 (uses same ingestion pipeline)

### Parallel Execution Opportunities

**Phase 1-2 (Setup/Foundational)**:
- Database schema creation [P]
- Azure Blob Storage setup [P]
- Redis configuration [P]
- Authentication setup [P]

**Phase 3 (P1 - Ingest)**:
- PDF validation service [P]
- Pydantic AI extraction agent [P]
- Celery task configuration [P]
- API routes (after models complete)

**Phase 4 (P2 - Search)**:
- Search service implementation [P]
- Search API routes [P]
- Frontend search components [P]

**Phase 5 (P3 - Compare)**:
- Comparison service [P]
- Comparison API routes [P]
- Frontend comparison UI [P]

**Phase 6 (P4 - Scraping)**:
- Scraper implementation [P]
- Scheduler configuration [P]
- Admin UI for scraping config [P]

---

## Phase 1: Setup

**Goal**: Initialize project structure and development environment

**Tasks**:

- [x] T001 Create backend directory structure per plan.md (backend/src/{models,services,api,utils}, backend/tests/{unit,integration,contract})
- [x] T002 Create frontend directory structure per plan.md (frontend/src/{components,pages,services}, frontend/tests/e2e)
- [x] T003 Create backend/requirements.txt with all dependencies from quickstart.md
- [x] T004 Create backend/.env.example with all configuration variables from quickstart.md
- [x] T005 Create docker-compose.yml for local PostgreSQL 17 and Redis per quickstart.md
- [x] T006 Create backend/alembic.ini for database migrations
- [x] T007 Create backend/src/config.py for environment configuration using pydantic-settings
- [x] T008 Create backend/src/__init__.py and all package __init__.py files
- [x] T009 Create frontend/package.json with React 18+, TypeScript 5+, Vite dependencies
- [x] T010 Create frontend/.env.example with VITE_API_BASE_URL configuration
- [x] T011 Create README.md in project root with quickstart instructions
- [x] T012 Create .gitignore for Python, Node.js, and IDE files

---

## Phase 2: Foundational

**Goal**: Implement blocking prerequisites required by all user stories

**Independent Test**: Database connection successful, authentication working, basic API health check responds

**Tasks**:

### Database Schema

- [x] T013 [P] Create backend/src/models/base.py with SQLAlchemy Base and common mixins (timestamps, soft-delete)
- [x] T014 [P] Create backend/src/models/user.py implementing User entity from data-model.md
- [x] T015 [P] Create backend/src/models/payer.py implementing Payer entity from data-model.md
- [x] T016 [P] Create backend/src/models/policy_document.py implementing PolicyDocument entity with processing status enum from data-model.md
- [x] T017 [P] Create backend/src/models/policy_section.py implementing PolicySection entity with section type enum from data-model.md
- [x] T018 [P] Create backend/src/models/coverage_criteria.py implementing CoverageCriteria entity from data-model.md
- [x] T019 [P] Create backend/src/models/exclusion.py implementing Exclusion entity from data-model.md
- [x] T020 [P] Create backend/src/models/processing_job.py implementing ProcessingJob entity with job status enum from data-model.md
- [x] T021 [P] Create backend/src/models/audit_log.py implementing AuditLog entity with action type enum from data-model.md
- [x] T022 Create backend/alembic/versions/001_initial_schema.py migration for all entities
- [x] T023 Create backend/scripts/seed_data.py to create admin user and Cigna payer per quickstart.md

### Authentication & Authorization

- [ ] T024 [P] Create backend/src/api/auth/jwt.py implementing JWT token generation and validation
- [ ] T025 [P] Create backend/src/api/auth/dependencies.py with get_current_user and require_admin dependencies
- [ ] T026 [P] Create backend/src/api/routes/auth.py implementing /auth/login and /auth/me endpoints from api-spec.yaml
- [ ] T027 [P] Create backend/src/api/middleware/audit_logger.py to log all user actions to AuditLog table

### Core Infrastructure

- [x] T028 [P] Create backend/src/utils/azure_storage.py for Azure Blob Storage operations (upload, download, delete)
- [ ] T029 [P] Create backend/src/utils/validators.py for PDF validation (file type, size, corruption checks)
- [ ] T030 [P] Create backend/src/celery_app.py with Celery configuration and exponential backoff retry logic per quickstart.md
- [ ] T031 [P] Create backend/src/api/middleware/error_handler.py for global exception handling and error responses
- [x] T032 Create backend/src/main.py with FastAPI app initialization, CORS, middleware, and route registration
- [x] T033 Create backend/src/database.py with async SQLAlchemy engine and session management

---

## Phase 3: User Story 1 - Ingest Policy Documents (P1) 🎯 MVP

**Story Goal**: Enable administrators to upload PDF policy documents that are automatically extracted into structured, queryable data

**Why P1**: Foundational capability - without ingestion, no other features are possible. Delivers immediate value by converting unstructured PDFs to structured data.

**Independent Test**: 
1. Upload a sample Cigna medical policy PDF via API
2. Verify processing job is created and status is trackable
3. Confirm PDF text is extracted (including OCR for scanned PDFs)
4. Validate Pydantic AI agent extracts structured entities (policy name, dates, sections, coverage criteria, exclusions)
5. Verify structured data is stored in PostgreSQL and retrievable via API
6. Test error handling for corrupted/invalid PDFs

**Acceptance Criteria**:
- ✅ Valid PDF accepted, queued for processing, returns tracking ID
- ✅ Processing status visible (queued → extracting → structuring → complete)
- ✅ Structured data includes policy name, effective dates, sections, coverage criteria, exclusions
- ✅ Corrupted/invalid PDFs rejected with clear error message
- ✅ Processing completes in <5 minutes for 100-page documents (SC-001)
- ✅ 90% extraction accuracy validated against manual review (SC-002)
- ✅ First 5 Cigna policies flagged for manual review (FR-018)
- ✅ Automatic retry with exponential backoff (max 3 attempts) on failure (FR-015)

**Tasks**:

### PDF Processing Services

- [x] T034 [P] [US1] Create backend/src/services/ingestion/pdf_extractor.py using pymupdf for text-based PDFs
- [x] T035 [P] [US1] Create backend/src/services/ingestion/ocr_processor.py using pytesseract for scanned/image-based PDFs
- [x] T036 [P] [US1] Create backend/src/services/ingestion/document_chunker.py to split extracted text into semantic sections
- [x] T037 [P] [US1] Create backend/src/services/ingestion/uploader.py to handle PDF upload, validation, and Azure Blob Storage upload
- [x] T038 [P] [US1] Create backend/src/services/extraction/schemas.py with Pydantic models for PolicyExtraction, PolicySection, CoverageCriteria, Exclusion per quickstart.md example
- [x] T039 [P] [US1] Create backend/src/services/extraction/llm_agent.py with Pydantic AI Agent configured for policy extraction per quickstart.md
- [x] T040 [P] [US1] Create backend/src/services/extraction/confidence_scorer.py to calculate extraction confidence scores and flag low-confidence extractions
- [ ] T041 [US1] Create backend/src/services/extraction/extractor.py orchestrating PDF extraction → chunking → LLM extraction → confidence scoring

### Processing Pipeline

- [ ] T042 [US1] Create backend/src/services/ingestion/processor.py to coordinate full ingestion workflow (upload → extract → structure → store)
- [ ] T043 [US1] Create backend/src/celery_app.py task process_policy_document implementing retry logic and status updates per quickstart.md
- [ ] T044 [US1] Create backend/src/services/ingestion/storage_service.py to persist extracted data to PostgreSQL (PolicyDocument, PolicySection, CoverageCriteria, Exclusion)
- [ ] T045 [US1] Create backend/src/services/ingestion/review_queue.py to implement first-N-per-payer and confidence-threshold review flagging (FR-018)

### API Endpoints

- [x] T046 [US1] Create backend/src/api/routes/ingestion.py implementing POST /ingestion/upload endpoint from api-spec.yaml
- [x] T047 [US1] Create backend/src/api/routes/ingestion.py implementing GET /ingestion/jobs/{job_id} endpoint from api-spec.yaml
- [x] T048 [US1] Create backend/src/api/routes/policies.py implementing GET /policies endpoint from api-spec.yaml
- [x] T049 [US1] Create backend/src/api/routes/policies.py implementing GET /policies/{policy_id} endpoint from api-spec.yaml
- [x] T050 [US1] Create backend/src/api/routes/policies.py implementing GET /policies/{policy_id}/sections/{section_id} endpoint from api-spec.yaml

### Frontend Components

- [ ] T051 [P] [US1] Create frontend/src/components/upload/FileUploader.tsx for PDF file selection and upload
- [ ] T052 [P] [US1] Create frontend/src/components/upload/ProcessingStatus.tsx to display job status with progress indicators
- [ ] T053 [P] [US1] Create frontend/src/pages/upload/UploadPage.tsx integrating file uploader and status tracking
- [ ] T054 [P] [US1] Create frontend/src/services/api/ingestion.ts with API client functions for upload and job status
- [ ] T055 [US1] Create frontend/src/pages/policy-detail/PolicyDetailPage.tsx to display structured policy data

**Parallel Execution**: T034-T037 (PDF services), T038-T040 (Pydantic AI), T051-T054 (Frontend) can run in parallel. T042-T045 depend on T034-T041. T046-T050 depend on T042-T045.

---

## Phase 4: User Story 2 - Search and Query Policies (P2)

**Story Goal**: Enable analysts to search across all ingested policies to find specific coverage criteria, requirements, or exclusions

**Why P2**: Primary user value after ingestion - transforms warehouse from data store into decision-making tool

**Independent Test**:
1. Pre-load 3-5 structured policies into database
2. Search for keyword "prior authorization" and verify results include all matching policies
3. Apply filters (payer name, effective date range, policy type) and verify results are filtered correctly
4. Verify search results include policy metadata, relevant sections, and highlighted search terms
5. Test "no results" scenario with clear messaging

**Acceptance Criteria**:
- ✅ Search returns all policies containing search term with context highlighted
- ✅ Filters work correctly (payer, date range, policy type)
- ✅ Results include policy metadata, relevant sections, and links to related sections
- ✅ "No results" message with suggestions displayed when no matches
- ✅ Search response time <30 seconds (SC-003)
- ✅ Search reduces manual PDF reading time by 80% (SC-003)

**Tasks**:

### Search Service

- [ ] T056 [P] [US2] Create backend/src/services/search/search_engine.py implementing PostgreSQL full-text search using ts_vector
- [ ] T057 [P] [US2] Create backend/src/services/search/highlighter.py to highlight search terms in result context
- [ ] T058 [P] [US2] Create backend/src/services/search/filter_builder.py to construct SQL queries from search filters
- [ ] T059 [US2] Create backend/src/services/search/search_service.py orchestrating search, filtering, and highlighting

### API Endpoints

- [ ] T060 [US2] Create backend/src/api/routes/search.py implementing POST /search endpoint from api-spec.yaml

### Frontend Components

- [ ] T061 [P] [US2] Create frontend/src/components/search/SearchBar.tsx with keyword input and search button
- [ ] T062 [P] [US2] Create frontend/src/components/search/SearchFilters.tsx for payer, date range, policy type filters
- [ ] T063 [P] [US2] Create frontend/src/components/search/SearchResults.tsx to display results with highlighting
- [ ] T064 [P] [US2] Create frontend/src/services/api/search.ts with API client functions for search
- [ ] T065 [US2] Create frontend/src/pages/dashboard/DashboardPage.tsx integrating search bar, filters, and results

**Parallel Execution**: T056-T058 (search services), T061-T064 (frontend) can run in parallel. T059-T060 depend on T056-T058. T065 depends on T061-T064.

---

## Phase 5: User Story 3 - Compare Policies Across Payers (P3)

**Story Goal**: Enable analysts to compare how different payers handle the same medical procedure or condition

**Why P3**: Higher-value use case building on search - provides comparative analysis requiring multiple structured policies

**Independent Test**:
1. Pre-load policies from 2-3 different payers covering the same topic (e.g., "knee replacement")
2. Request comparison for specific topic and verify side-by-side view of coverage criteria, requirements, exclusions
3. Verify system aligns comparable sections across different policy structures
4. Test export/save functionality for comparison results
5. Verify "no policy found" handling for payers without matching policies

**Acceptance Criteria**:
- ✅ Side-by-side view of coverage criteria, requirements, exclusions from each payer
- ✅ Comparable sections aligned (e.g., all "prior authorization" requirements together)
- ✅ Comparison can be exported/saved for reporting
- ✅ Payers without policies clearly marked as "no policy found"
- ✅ 90% of surfaced differences confirmed accurate by domain experts (SC-005)

**Tasks**:

### Comparison Service

- [ ] T066 [P] [US3] Create backend/src/services/comparison/section_aligner.py to align comparable sections across policies
- [ ] T067 [P] [US3] Create backend/src/services/comparison/difference_detector.py to identify and summarize policy differences
- [ ] T068 [US3] Create backend/src/services/comparison/comparator.py orchestrating policy retrieval, alignment, and difference detection

### API Endpoints

- [ ] T069 [US3] Create backend/src/api/routes/comparison.py implementing POST /comparison endpoint from api-spec.yaml

### Frontend Components

- [ ] T070 [P] [US3] Create frontend/src/components/comparison/PolicySelector.tsx to select policies for comparison
- [ ] T071 [P] [US3] Create frontend/src/components/comparison/ComparisonView.tsx for side-by-side policy display
- [ ] T072 [P] [US3] Create frontend/src/components/comparison/DifferencesHighlight.tsx to highlight key differences
- [ ] T073 [P] [US3] Create frontend/src/components/comparison/ExportButton.tsx to export comparison results
- [ ] T074 [P] [US3] Create frontend/src/services/api/comparison.ts with API client functions for comparison
- [ ] T075 [US3] Create frontend/src/pages/compare/ComparePage.tsx integrating policy selector and comparison view

**Parallel Execution**: T066-T067 (comparison services), T070-T074 (frontend) can run in parallel. T068-T069 depend on T066-T067. T075 depends on T070-T074.

---

## Phase 6: User Story 4 - Bulk Policy Scraping (P4)

**Story Goal**: Enable administrators to automatically scrape and ingest policy documents from payer websites on a scheduled basis

**Why P4**: Automation for long-term maintenance - not critical for initial value delivery (manual uploads sustain system)

**Independent Test**:
1. Configure scraper for Cigna website with base URL and selectors
2. Manually trigger scraping job and verify new/updated policies are discovered
3. Verify discovered policies are automatically queued for ingestion (reusing P1 pipeline)
4. Test version detection (new policy vs. update to existing policy)
5. Verify scheduled scraping runs on cron schedule
6. Test error handling for website structure changes

**Acceptance Criteria**:
- ✅ Scraper periodically checks for new/updated policy documents based on schedule
- ✅ New documents automatically downloaded and queued for processing
- ✅ Updated policies create new version while preserving historical version
- ✅ Scraping failures show clear error message and alert for manual intervention
- ✅ Automated scraping reduces manual update effort by 70% (SC-006)

**Tasks**:

### Scraping Service

- [ ] T076 [P] [US4] Create backend/src/services/scraping/web_scraper.py using httpx and BeautifulSoup for HTML parsing
- [ ] T077 [P] [US4] Create backend/src/services/scraping/pdf_downloader.py to download discovered PDF files
- [ ] T078 [P] [US4] Create backend/src/services/scraping/version_detector.py to detect new vs. updated policies
- [ ] T079 [US4] Create backend/src/services/scraping/scraper.py orchestrating scraping, downloading, and version detection
- [ ] T080 [US4] Create backend/src/services/scraping/scheduler.py using Celery Beat for scheduled scraping jobs
- [ ] T081 [US4] Create backend/src/celery_app.py task run_scraping_job implementing scraping workflow with error handling

### API Endpoints

- [ ] T082 [US4] Create backend/src/api/routes/scraping.py implementing GET /scraping/payers endpoint from api-spec.yaml
- [ ] T083 [US4] Create backend/src/api/routes/scraping.py implementing PUT /scraping/payers/{payer_id}/config endpoint from api-spec.yaml
- [ ] T084 [US4] Create backend/src/api/routes/scraping.py implementing POST /scraping/payers/{payer_id}/trigger endpoint from api-spec.yaml

### Frontend Components (Admin)

- [ ] T085 [P] [US4] Create frontend/src/components/admin/ScrapingConfig.tsx for configuring scraper settings per payer
- [ ] T086 [P] [US4] Create frontend/src/components/admin/ScrapingSchedule.tsx for setting cron schedule
- [ ] T087 [P] [US4] Create frontend/src/components/admin/ScrapingJobsList.tsx to display scraping job history and status
- [ ] T088 [P] [US4] Create frontend/src/services/api/scraping.ts with API client functions for scraping management
- [ ] T089 [US4] Create frontend/src/pages/admin/ScrapingPage.tsx integrating scraping configuration and job management

**Parallel Execution**: T076-T078 (scraping services), T085-T088 (frontend) can run in parallel. T079-T081 depend on T076-T078. T082-T084 depend on T079-T081. T089 depends on T085-T088.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Complete remaining features and improve overall system quality

**Tasks**:

### Admin Features

- [ ] T090 [P] Create backend/src/api/routes/admin.py implementing GET /admin/users endpoint from api-spec.yaml
- [ ] T091 [P] Create backend/src/api/routes/admin.py implementing POST /admin/users endpoint from api-spec.yaml
- [ ] T092 [P] Create backend/src/api/routes/admin.py implementing GET /admin/audit-logs endpoint from api-spec.yaml
- [ ] T093 [P] Create frontend/src/components/admin/UserManagement.tsx for user CRUD operations
- [ ] T094 [P] Create frontend/src/components/admin/AuditLogViewer.tsx to display audit logs with filtering
- [ ] T095 Create frontend/src/pages/admin/AdminPanel.tsx integrating user management and audit logs

### Error Handling & Validation

- [ ] T096 [P] Add comprehensive error handling to all API routes with appropriate HTTP status codes
- [ ] T097 [P] Add input validation to all API endpoints using Pydantic models
- [ ] T098 [P] Add rate limiting middleware to prevent API abuse
- [ ] T099 [P] Add request/response logging for debugging and monitoring

### Performance Optimization

- [ ] T100 [P] Add database query optimization (indexes, query analysis) based on common access patterns
- [ ] T101 [P] Add Redis caching for frequently accessed policies and search results
- [ ] T102 [P] Add connection pooling configuration for PostgreSQL and Redis
- [ ] T103 [P] Add pagination to all list endpoints (policies, search results, audit logs)

### Documentation

- [ ] T104 [P] Add API documentation using FastAPI automatic OpenAPI docs
- [ ] T105 [P] Add inline code documentation (docstrings) to all services and utilities
- [ ] T106 [P] Create deployment guide for Azure AKS in docs/deployment.md
- [ ] T107 [P] Create monitoring and observability guide in docs/monitoring.md

### Deployment Preparation

- [ ] T108 [P] Create Dockerfile for backend application
- [ ] T109 [P] Create Dockerfile for frontend application
- [ ] T110 [P] Create Kubernetes manifests for AKS deployment (deployments, services, ingress)
- [ ] T111 [P] Create CI/CD pipeline configuration (GitHub Actions or Azure DevOps)
- [ ] T112 [P] Configure Azure resources (AKS cluster, PostgreSQL, Blob Storage, Redis)

**Parallel Execution**: Most tasks in this phase can run in parallel as they are independent improvements.

---

## Task Summary

**Total Tasks**: 112

**Tasks by Phase**:
- Phase 1 (Setup): 12 tasks
- Phase 2 (Foundational): 21 tasks
- Phase 3 (P1 - Ingest): 22 tasks 🎯 **MVP**
- Phase 4 (P2 - Search): 10 tasks
- Phase 5 (P3 - Compare): 10 tasks
- Phase 6 (P4 - Scraping): 14 tasks
- Phase 7 (Polish): 23 tasks

**Parallelizable Tasks**: 67 tasks marked with [P]

**MVP Delivery**: Phases 1-3 (55 tasks) deliver complete document ingestion capability

**Estimated Timeline**:
- MVP (P1): 2-3 weeks
- P2 (Search): 1 week
- P3 (Compare): 1 week
- P4 (Scraping): 1-2 weeks
- Polish: 1-2 weeks
- **Total**: 6-9 weeks for complete feature

## Validation Checklist

✅ All tasks follow checklist format (checkbox, ID, labels, file paths)  
✅ Tasks organized by user story priority (P1 → P2 → P3 → P4)  
✅ Each user story phase has independent test criteria  
✅ Dependencies clearly documented  
✅ Parallel execution opportunities identified  
✅ MVP scope clearly defined (Phase 3 - P1)  
✅ All entities from data-model.md mapped to tasks  
✅ All API endpoints from api-spec.yaml mapped to tasks  
✅ Technology stack from research.md reflected in tasks  
✅ Setup instructions from quickstart.md incorporated  

## Next Steps

1. **Start with MVP**: Execute Phases 1-3 (Setup → Foundational → P1 Ingest)
2. **Validate MVP**: Test complete ingestion workflow with real Cigna policy PDFs
3. **Iterate**: Proceed to P2 (Search) after MVP validation
4. **Deploy incrementally**: Deploy each phase to staging for validation before proceeding
5. **Monitor metrics**: Track SC-001 through SC-006 success criteria throughout implementation

**Ready to begin implementation! Start with T001.**
