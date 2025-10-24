# Data Model: Policy Warehouse

**Feature**: Policy Warehouse  
**Phase**: 1 - Design  
**Date**: 2025-10-24

## Overview

This document defines the relational data model for the policy warehouse system, including all entities, attributes, relationships, validation rules, and state transitions.

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ 1
       │ creates/modifies
       │ *
┌──────▼──────────────┐         ┌──────────────┐
│ Processing Job      │────────▶│    Payer     │
└──────┬──────────────┘ *     1 └──────────────┘
       │ processes
       │ 1
       │
       │ *
┌──────▼──────────────┐
│ Policy Document     │
└──────┬──────────────┘
       │ contains
       │ 1
       │
       │ *
┌──────▼──────────────┐
│ Policy Section      │
└──────┬──────────────┘
       │ contains
       │ 1
       │
       ├─────────────────┬──────────────────┐
       │ *               │ *                │ *
┌──────▼──────────┐ ┌───▼────────────┐ ┌──▼──────────┐
│Coverage Criteria│ │   Exclusion    │ │ Requirement │
└─────────────────┘ └────────────────┘ └─────────────┘
```

## Core Entities

### 1. User

Represents a system user with role-based access control.

**Attributes**:
- `id` (UUID, PK): Unique user identifier
- `username` (String, unique, required): Login username
- `email` (String, unique, required): User email address
- `password_hash` (String, required): Hashed password (bcrypt)
- `role` (Enum, required): User role - `ANALYST` or `ADMINISTRATOR`
- `first_name` (String, optional): User's first name
- `last_name` (String, optional): User's last name
- `is_active` (Boolean, default=True): Account active status
- `last_login_at` (Timestamp, nullable): Last successful login timestamp
- `created_at` (Timestamp, required): Account creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Username must be 3-50 characters, alphanumeric + underscore/hyphen
- Password must be minimum 12 characters with complexity requirements
- Role must be one of: `ANALYST`, `ADMINISTRATOR`

**Indexes**:
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`
- Index on `role` for access control queries

### 2. Payer

Represents a healthcare payer organization.

**Attributes**:
- `id` (UUID, PK): Unique payer identifier
- `name` (String, unique, required): Payer organization name (e.g., "Cigna")
- `website_url` (String, nullable): Payer's official website URL
- `scraping_enabled` (Boolean, default=False): Whether automated scraping is enabled
- `scraping_config` (JSONB, nullable): Payer-specific scraping configuration
  - `base_url`: Starting URL for scraping
  - `policy_list_selector`: CSS/XPath selector for policy list
  - `policy_link_selector`: CSS/XPath selector for policy PDF links
  - `requires_auth`: Boolean indicating if authentication needed
  - `auth_config`: Authentication credentials/method (encrypted)
  - `schedule_cron`: Cron expression for scraping schedule
- `last_scrape_at` (Timestamp, nullable): Last successful scrape timestamp
- `next_scrape_at` (Timestamp, nullable): Next scheduled scrape timestamp
- `is_active` (Boolean, default=True): Payer active status
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Validation Rules**:
- Name must be 2-200 characters
- Website URL must be valid HTTP/HTTPS URL if provided
- Scraping config must validate against JSON schema if provided

**Indexes**:
- Primary key on `id`
- Unique index on `name`
- Index on `scraping_enabled` for scraping job queries
- Index on `next_scrape_at` for scheduler queries

### 3. Policy Document

Represents a complete payer policy document.

**Attributes**:
- `id` (UUID, PK): Unique policy document identifier
- `payer_id` (UUID, FK → Payer, required): Associated payer
- `policy_name` (String, required): Policy title/name
- `policy_number` (String, nullable): Official policy number/identifier
- `effective_date` (Date, required): Policy effective date
- `expiration_date` (Date, nullable): Policy expiration date (null if ongoing)
- `version` (Integer, required): Version number (starts at 1, increments on update)
- `previous_version_id` (UUID, FK → Policy Document, nullable): Link to previous version
- `document_type` (Enum, required): Type of policy - `MEDICAL`, `PHARMACY`, `DENTAL`, `VISION`, `OTHER`
- `source_url` (String, nullable): URL where policy was scraped from
- `pdf_storage_path` (String, required): S3/MinIO path to original PDF file
- `pdf_file_size_bytes` (Integer, required): PDF file size in bytes
- `pdf_page_count` (Integer, required): Number of pages in PDF
- `processing_status` (Enum, required): Current processing status
- `processing_started_at` (Timestamp, nullable): When processing began
- `processing_completed_at` (Timestamp, nullable): When processing completed
- `extraction_confidence_score` (Float, nullable): Overall extraction confidence (0.0-1.0)
- `requires_manual_review` (Boolean, default=False): Flagged for human review
- `reviewed_by_user_id` (UUID, FK → User, nullable): User who reviewed (if applicable)
- `reviewed_at` (Timestamp, nullable): When manual review completed
- `is_deleted` (Boolean, default=False): Soft-delete flag
- `deleted_at` (Timestamp, nullable): Soft-delete timestamp
- `deleted_by_user_id` (UUID, FK → User, nullable): User who soft-deleted
- `created_by_user_id` (UUID, FK → User, nullable): User who uploaded (null if scraped)
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Processing Status Enum**:
- `QUEUED`: Document uploaded, waiting for processing
- `EXTRACTING_TEXT`: Extracting text from PDF (OCR if needed)
- `STRUCTURING_DATA`: LLM extracting structured entities
- `COMPLETE`: Processing successfully completed
- `FAILED`: Processing failed after retries
- `PENDING_REVIEW`: Awaiting manual review (low confidence or first N per payer)

**Validation Rules**:
- Policy name must be 5-500 characters
- Effective date cannot be in future (at time of upload)
- Expiration date must be after effective date if provided
- Version must be positive integer
- Extraction confidence score must be 0.0-1.0 if provided
- Processing status transitions must follow valid state machine

**Indexes**:
- Primary key on `id`
- Foreign key index on `payer_id`
- Foreign key index on `previous_version_id`
- Index on `processing_status` for job queue queries
- Index on `requires_manual_review` for review queue
- Composite index on `(payer_id, policy_number, version)` for version lookups
- Index on `effective_date` for date range queries
- Index on `is_deleted` for filtering soft-deleted records
- Full-text search index on `policy_name` (PostgreSQL ts_vector)

**State Transitions**:
```
QUEUED → EXTRACTING_TEXT → STRUCTURING_DATA → COMPLETE
                                            ↓
                                       PENDING_REVIEW → COMPLETE
   ↓
FAILED (after max retries)
```

### 4. Policy Section

Represents a logical section within a policy document.

**Attributes**:
- `id` (UUID, PK): Unique section identifier
- `policy_document_id` (UUID, FK → Policy Document, required): Parent policy document
- `section_type` (Enum, required): Type of section
- `section_number` (String, nullable): Section number (e.g., "2.1.3")
- `title` (String, required): Section title/heading
- `content_text` (Text, required): Extracted section text content
- `content_structured` (JSONB, nullable): Structured data extracted from section
- `extraction_confidence_score` (Float, nullable): Section-level confidence (0.0-1.0)
- `page_numbers` (Array[Integer], nullable): PDF page numbers where section appears
- `order_index` (Integer, required): Order of section within document (for display)
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Section Type Enum**:
- `COVERAGE_CRITERIA`: Conditions for coverage
- `EXCLUSIONS`: Explicitly not covered scenarios
- `REQUIREMENTS`: Documentation or procedural requirements
- `DEFINITIONS`: Term definitions
- `PRIOR_AUTHORIZATION`: Prior auth requirements
- `LIMITATIONS`: Coverage limitations
- `APPEALS_PROCESS`: How to appeal decisions
- `OTHER`: Miscellaneous sections

**Validation Rules**:
- Title must be 1-500 characters
- Content text must not be empty
- Extraction confidence score must be 0.0-1.0 if provided
- Order index must be non-negative

**Indexes**:
- Primary key on `id`
- Foreign key index on `policy_document_id`
- Index on `section_type` for filtering by type
- Composite index on `(policy_document_id, order_index)` for ordered retrieval
- Full-text search index on `content_text` (PostgreSQL ts_vector)

### 5. Coverage Criteria

Represents specific conditions under which a medical service/procedure is covered.

**Attributes**:
- `id` (UUID, PK): Unique criteria identifier
- `policy_section_id` (UUID, FK → Policy Section, required): Parent section
- `procedure_name` (String, required): Medical procedure/service name
- `procedure_code` (String, nullable): CPT/HCPCS code if specified
- `covered_scenarios` (Text, required): Description of when covered
- `required_documentation` (Text, nullable): Documentation requirements
- `prior_authorization_required` (Boolean, default=False): Whether prior auth needed
- `age_restrictions` (String, nullable): Age-based restrictions (e.g., "18-65 years")
- `frequency_limitations` (String, nullable): How often covered (e.g., "once per year")
- `extraction_confidence_score` (Float, nullable): Criteria-level confidence (0.0-1.0)
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Validation Rules**:
- Procedure name must be 2-500 characters
- Covered scenarios must not be empty
- Extraction confidence score must be 0.0-1.0 if provided

**Indexes**:
- Primary key on `id`
- Foreign key index on `policy_section_id`
- Index on `procedure_name` for search
- Index on `procedure_code` for code-based lookups
- Full-text search index on `procedure_name` and `covered_scenarios`

### 6. Exclusion

Represents conditions or scenarios explicitly not covered.

**Attributes**:
- `id` (UUID, PK): Unique exclusion identifier
- `policy_section_id` (UUID, FK → Policy Section, required): Parent section
- `excluded_procedure` (String, required): What is excluded
- `exclusion_rationale` (Text, nullable): Why it's excluded
- `exceptions_to_exclusion` (Text, nullable): Scenarios where exclusion doesn't apply
- `extraction_confidence_score` (Float, nullable): Exclusion-level confidence (0.0-1.0)
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Validation Rules**:
- Excluded procedure must be 2-500 characters
- Extraction confidence score must be 0.0-1.0 if provided

**Indexes**:
- Primary key on `id`
- Foreign key index on `policy_section_id`
- Full-text search index on `excluded_procedure`

### 7. Processing Job

Represents a document processing or scraping task.

**Attributes**:
- `id` (UUID, PK): Unique job identifier
- `job_type` (Enum, required): Type of job - `INGESTION` or `SCRAPING`
- `status` (Enum, required): Current job status
- `payer_id` (UUID, FK → Payer, nullable): Associated payer (for scraping jobs)
- `policy_document_id` (UUID, FK → Policy Document, nullable): Associated document (for ingestion jobs)
- `started_at` (Timestamp, nullable): Job start timestamp
- `completed_at` (Timestamp, nullable): Job completion timestamp
- `retry_count` (Integer, default=0): Number of retry attempts
- `max_retries` (Integer, default=3): Maximum retry attempts
- `error_message` (Text, nullable): Error details if failed
- `error_stacktrace` (Text, nullable): Full stacktrace for debugging
- `celery_task_id` (String, nullable): Celery task ID for tracking
- `created_by_user_id` (UUID, FK → User, nullable): User who triggered (null if scheduled)
- `created_at` (Timestamp, required): Record creation timestamp
- `updated_at` (Timestamp, required): Last update timestamp

**Job Status Enum**:
- `PENDING`: Job queued, not started
- `RUNNING`: Job currently executing
- `RETRYING`: Job failed, will retry
- `COMPLETED`: Job successfully completed
- `FAILED`: Job failed after max retries
- `CANCELLED`: Job manually cancelled

**Validation Rules**:
- Retry count must be non-negative
- Max retries must be positive
- Status transitions must follow valid state machine

**Indexes**:
- Primary key on `id`
- Foreign key index on `payer_id`
- Foreign key index on `policy_document_id`
- Index on `status` for job queue queries
- Index on `job_type` for filtering
- Index on `celery_task_id` for Celery integration

**State Transitions**:
```
PENDING → RUNNING → COMPLETED
            ↓
         RETRYING → RUNNING (up to max_retries)
            ↓
         FAILED (after max retries)
            
PENDING/RUNNING → CANCELLED (manual intervention)
```

## Audit Log Entity

### 8. Audit Log

Tracks all user actions for compliance and security (FR-017).

**Attributes**:
- `id` (UUID, PK): Unique log entry identifier
- `user_id` (UUID, FK → User, nullable): User who performed action (null if system)
- `action_type` (Enum, required): Type of action performed
- `resource_type` (String, required): Type of resource affected (e.g., "PolicyDocument", "User")
- `resource_id` (UUID, nullable): ID of affected resource
- `action_details` (JSONB, nullable): Additional action context
- `ip_address` (String, nullable): User's IP address
- `user_agent` (String, nullable): User's browser/client info
- `timestamp` (Timestamp, required): When action occurred

**Action Type Enum**:
- `LOGIN`: User logged in
- `LOGOUT`: User logged out
- `UPLOAD_DOCUMENT`: Document uploaded
- `DELETE_DOCUMENT`: Document soft-deleted
- `UPDATE_SCRAPING_CONFIG`: Scraping configuration changed
- `MANUAL_REVIEW_COMPLETE`: Manual review completed
- `SEARCH_QUERY`: Search performed
- `POLICY_COMPARISON`: Policy comparison viewed
- `USER_CREATED`: New user created
- `USER_ROLE_CHANGED`: User role modified

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id`
- Index on `timestamp` for time-range queries
- Composite index on `(resource_type, resource_id)` for resource audit trails

## Relationships Summary

- **User** → **Processing Job**: 1:N (user creates jobs)
- **User** → **Policy Document**: 1:N (user uploads documents, reviews documents, soft-deletes documents)
- **User** → **Audit Log**: 1:N (user performs audited actions)
- **Payer** → **Policy Document**: 1:N (payer has many policies)
- **Payer** → **Processing Job**: 1:N (payer has scraping jobs)
- **Policy Document** → **Policy Document**: 1:1 (self-referential for versioning)
- **Policy Document** → **Policy Section**: 1:N (document contains sections)
- **Policy Document** → **Processing Job**: 1:1 (document has processing job)
- **Policy Section** → **Coverage Criteria**: 1:N (section contains criteria)
- **Policy Section** → **Exclusion**: 1:N (section contains exclusions)

## Database Constraints

### Foreign Key Constraints
- All foreign keys have `ON DELETE RESTRICT` to prevent orphaned records
- Exception: `previous_version_id` has `ON DELETE SET NULL` for version chain integrity

### Check Constraints
- `effective_date <= expiration_date` (if expiration_date not null)
- `extraction_confidence_score BETWEEN 0.0 AND 1.0` (if not null)
- `retry_count <= max_retries`
- `version >= 1`

### Unique Constraints
- `(payer_id, policy_number, version)` for policy versioning
- `username` for user accounts
- `email` for user accounts
- `name` for payers

## Soft Delete Strategy

Entities supporting soft delete (per FR-010):
- **Policy Document**: `is_deleted`, `deleted_at`, `deleted_by_user_id`

Soft-deleted records:
- Remain in database for audit/compliance
- Excluded from default queries via `WHERE is_deleted = FALSE`
- Can be restored by administrators
- Historical versions never physically deleted

## Migration Strategy

1. **Initial Schema**: Create all tables with indexes
2. **Seed Data**: Insert default admin user, initial payers
3. **Version Control**: Use Alembic for schema migrations
4. **Rollback Plan**: Each migration includes downgrade script

## Performance Considerations

- Full-text search indexes on searchable text fields
- Composite indexes for common query patterns
- JSONB indexes for structured content queries
- Partitioning strategy for audit logs (by month) if volume high
- Connection pooling (SQLAlchemy async pool)
- Read replicas for search queries if needed
