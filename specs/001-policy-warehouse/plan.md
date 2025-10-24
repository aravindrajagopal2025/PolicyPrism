# Implementation Plan: Policy Warehouse

**Branch**: `001-policy-warehouse` | **Date**: 2025-10-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-policy-warehouse/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a policy warehouse system that ingests medical/pharma policy documents (PDFs) from healthcare payers, uses an agentic AI/LLM framework to extract and structure policy content into a queryable relational format, and provides search, comparison, and automated scraping capabilities. Initial focus on Cigna policies with incremental expansion based on extraction accuracy validation.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+ (rich LLM/AI ecosystem, mature PDF processing libraries)  
**Primary Dependencies**: FastAPI 0.104+ (web), Pydantic AI (agentic AI framework), pymupdf 1.23+ (PDF), SQLAlchemy 2.0+ (ORM), Celery 5.3+ (task queue), Azure Cache for Redis 7+ (cache/broker)  
**Storage**: PostgreSQL 17 (structured data, versioning, full-text search), Azure Blob Storage (PDF files), Azure Cache for Redis (cache)  
**Testing**: pytest 7+ (unit/integration), testcontainers (isolated test environments), Playwright (E2E), mock LLM responses + validation dataset  
**Target Platform**: Docker containers on Azure Kubernetes Service (AKS), Azure Database for PostgreSQL 17, Azure Blob Storage, Azure Cache for Redis
**Project Type**: web (backend API + frontend for search/comparison UI)  
**Performance Goals**: Process 100-page PDFs in <5 minutes (SC-001), search response <30 seconds (SC-003), 90% extraction accuracy (SC-002)  
**Constraints**: Must handle OCR for scanned PDFs, support role-based access control, maintain audit logs for compliance, preserve all historical versions indefinitely  
**Scale/Scope**: Initial deployment for single organization, hundreds of policies, tens of concurrent users, expandable to multiple payers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. User Story Independence ✅ PASS

- **P1 - Ingest Policy Documents**: Independently testable with single PDF upload → extraction → structured data retrieval
- **P2 - Search and Query Policies**: Independently testable with pre-loaded policies → search → filtered results
- **P3 - Compare Policies Across Payers**: Independently testable with multiple policies → comparison → side-by-side view
- **P4 - Bulk Policy Scraping**: Independently testable with scraper configuration → automated ingestion → verification

All user stories are properly prioritized and can be implemented/deployed independently.

### II. Specification-First Development ✅ PASS

- Specification completed with 18 functional requirements (FR-001 to FR-018)
- All user stories include Given-When-Then acceptance scenarios
- 6 measurable success criteria defined (SC-001 to SC-006)
- 5 clarifications resolved during `/speckit.clarify` session
- Edge cases documented (8 scenarios)

### III. Template-Driven Consistency ✅ PASS

- Specification follows spec-template.md structure precisely
- All mandatory sections completed (User Scenarios, Requirements, Success Criteria)
- Key entities defined (7 entities with attributes)
- This plan follows plan-template.md structure

### IV. Phased Implementation with Gates ✅ PASS

- Phase 0 (Research): Will resolve 5 NEEDS CLARIFICATION items in Technical Context
- Phase 1 (Design): Will produce data-model.md, contracts/, quickstart.md
- Phase 2 (Tasks): Will be generated via `/speckit.tasks` after Phase 1 completion
- Phase 3+ (Implementation): User stories will be implemented P1 → P2 → P3 → P4

### V. Explicit Over Implicit ✅ PASS

- Technical constraints explicitly documented (performance goals, scale, constraints)
- 5 NEEDS CLARIFICATION markers in Technical Context (to be resolved in Phase 0)
- Design decisions will include rationale in research.md
- All functional requirements use explicit MUST language

### VI. Testability and Validation ⚠️ ADVISORY

- Tests are OPTIONAL per constitution
- Specification does not explicitly request automated tests
- FR-018 includes human-in-the-loop validation for extraction quality
- Integration testing recommended for AI extraction pipeline accuracy validation

**Gate Status**: ✅ **PASS** - All mandatory principles satisfied, ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── src/
│   ├── models/           # Policy Document, Policy Section, Coverage Criteria, Exclusion, Payer, User, Processing Job
│   ├── services/
│   │   ├── ingestion/    # PDF upload, validation, queueing
│   │   ├── extraction/   # LLM-based entity extraction, OCR handling
│   │   ├── search/       # Full-text search, filtering, highlighting
│   │   ├── comparison/   # Cross-payer policy comparison logic
│   │   └── scraping/     # Scheduled scraping, payer-specific scrapers
│   ├── api/
│   │   ├── routes/       # REST endpoints for upload, search, comparison, admin
│   │   ├── auth/         # Role-based access control (Analyst/Administrator)
│   │   └── middleware/   # Audit logging, error handling
│   └── utils/            # PDF processing, retry logic, validation helpers
└── tests/
    ├── contract/         # API contract tests
    ├── integration/      # End-to-end extraction pipeline tests
    └── unit/             # Service and model unit tests

frontend/
├── src/
│   ├── components/
│   │   ├── upload/       # PDF upload interface
│   │   ├── search/       # Search bar, filters, results display
│   │   ├── comparison/   # Side-by-side policy comparison view
│   │   └── admin/        # Scraping configuration, user management
│   ├── pages/
│   │   ├── dashboard/    # Main search and navigation
│   │   ├── policy-detail/# Individual policy view
│   │   ├── compare/      # Comparison interface
│   │   └── admin/        # Admin panel
│   └── services/         # API client, authentication
└── tests/
    └── e2e/              # End-to-end user journey tests
```

**Structure Decision**: Web application structure selected (Option 2) due to requirement for user interface to support search, comparison, and administrative functions. Backend handles PDF processing, LLM extraction, and data management. Frontend provides analyst and administrator interfaces with role-based views.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations identified. Architecture follows standard patterns for web applications with AI/LLM integration.

## Phase 0: Research ✅ COMPLETE

**Output**: `research.md`

All NEEDS CLARIFICATION items resolved:
- Language/Version: Python 3.11+
- Primary Dependencies: FastAPI, Pydantic AI, pymupdf, SQLAlchemy, Celery, Azure services
- Storage: PostgreSQL 17, Azure Blob Storage, Azure Cache for Redis
- Testing: pytest, testcontainers, Playwright
- Target Platform: Azure Kubernetes Service (AKS)

## Phase 1: Design ✅ COMPLETE

**Outputs**:
- `data-model.md`: 8 entities with full schemas, relationships, validation rules
- `contracts/api-spec.yaml`: OpenAPI 3.1 specification with 15+ endpoints
- `quickstart.md`: Complete development setup guide
- `.windsurf/rules/specify-rules.md`: Agent context updated with tech stack

### Post-Design Constitution Check

#### I. User Story Independence ✅ PASS

No changes from initial check. All 4 user stories remain independently implementable.

#### II. Specification-First Development ✅ PASS

Design artifacts created without implementation details leaking into specification.

#### III. Template-Driven Consistency ✅ PASS

All Phase 1 artifacts follow their respective templates:
- Data model includes entities, relationships, validation rules, state transitions
- API contracts follow OpenAPI 3.1 standard
- Quickstart includes prerequisites, setup steps, development workflow

#### IV. Phased Implementation with Gates ✅ PASS

- Phase 0 (Research): ✅ Complete
- Phase 1 (Design): ✅ Complete
- Phase 2 (Tasks): Ready to proceed with `/speckit.tasks`
- Phase 3+ (Implementation): Blocked until Phase 2 complete

#### V. Explicit Over Implicit ✅ PASS

All design decisions documented with rationale in research.md:
- Technology choices include alternatives considered
- Architecture diagrams show component relationships
- API contracts specify all request/response schemas
- Data model includes all constraints and validation rules

#### VI. Testability and Validation ✅ PASS

- Testing strategy defined in research.md
- API contracts enable contract testing
- Data model supports test data generation
- Quickstart includes test execution commands

**Final Gate Status**: ✅ **PASS** - Ready for Phase 2 (Task Generation)

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Tasks will be organized by user story priority (P1 → P2 → P3 → P4)
3. Each task will reference specific files and include acceptance criteria
4. Begin implementation with P1: Ingest Policy Documents
