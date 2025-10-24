"""Initial schema with all entities

Revision ID: 001
Revises: 
Create Date: 2025-10-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    op.execute("CREATE TYPE user_role AS ENUM ('ANALYST', 'ADMINISTRATOR')")
    op.execute("CREATE TYPE document_type AS ENUM ('MEDICAL', 'PHARMACY', 'DENTAL', 'VISION', 'OTHER')")
    op.execute("CREATE TYPE processing_status AS ENUM ('QUEUED', 'EXTRACTING_TEXT', 'STRUCTURING_DATA', 'COMPLETE', 'FAILED', 'PENDING_REVIEW')")
    op.execute("CREATE TYPE section_type AS ENUM ('COVERAGE_CRITERIA', 'EXCLUSIONS', 'REQUIREMENTS', 'DEFINITIONS', 'PRIOR_AUTHORIZATION', 'LIMITATIONS', 'APPEALS_PROCESS', 'OTHER')")
    op.execute("CREATE TYPE job_type AS ENUM ('INGESTION', 'SCRAPING')")
    op.execute("CREATE TYPE job_status AS ENUM ('PENDING', 'RUNNING', 'RETRYING', 'COMPLETED', 'FAILED', 'CANCELLED')")
    op.execute("CREATE TYPE action_type AS ENUM ('LOGIN', 'LOGOUT', 'UPLOAD_DOCUMENT', 'DELETE_DOCUMENT', 'UPDATE_SCRAPING_CONFIG', 'MANUAL_REVIEW_COMPLETE', 'SEARCH_QUERY', 'POLICY_COMPARISON', 'USER_CREATED', 'USER_ROLE_CHANGED')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('ANALYST', 'ADMINISTRATOR', name='user_role'), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    
    # Create payers table
    op.create_table(
        'payers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, unique=True),
        sa.Column('website_url', sa.String(500), nullable=True),
        sa.Column('scraping_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('scraping_config', postgresql.JSONB(), nullable=True),
        sa.Column('last_scrape_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_scrape_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_payers_name', 'payers', ['name'])
    op.create_index('ix_payers_scraping_enabled', 'payers', ['scraping_enabled'])
    op.create_index('ix_payers_next_scrape_at', 'payers', ['next_scrape_at'])
    
    # Create policy_documents table
    op.create_table(
        'policy_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('previous_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policy_documents.id', ondelete='SET NULL'), nullable=True),
        sa.Column('policy_name', sa.String(500), nullable=False),
        sa.Column('policy_number', sa.String(100), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiration_date', sa.Date(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('document_type', sa.Enum('MEDICAL', 'PHARMACY', 'DENTAL', 'VISION', 'OTHER', name='document_type'), nullable=False),
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('pdf_storage_path', sa.String(500), nullable=False),
        sa.Column('pdf_file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('pdf_page_count', sa.Integer(), nullable=False),
        sa.Column('processing_status', sa.Enum('QUEUED', 'EXTRACTING_TEXT', 'STRUCTURING_DATA', 'COMPLETE', 'FAILED', 'PENDING_REVIEW', name='processing_status'), nullable=False),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('extraction_confidence_score', sa.Float(), nullable=True),
        sa.Column('requires_manual_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reviewed_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('version >= 1', name='check_version_positive'),
        sa.CheckConstraint('extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)', name='check_confidence_score_range'),
        sa.CheckConstraint('expiration_date IS NULL OR expiration_date >= effective_date', name='check_expiration_after_effective')
    )
    op.create_index('ix_policy_documents_payer_id', 'policy_documents', ['payer_id'])
    op.create_index('ix_policy_documents_previous_version_id', 'policy_documents', ['previous_version_id'])
    op.create_index('ix_policy_documents_processing_status', 'policy_documents', ['processing_status'])
    op.create_index('ix_policy_documents_requires_manual_review', 'policy_documents', ['requires_manual_review'])
    op.create_index('ix_policy_documents_effective_date', 'policy_documents', ['effective_date'])
    op.create_index('ix_policy_documents_is_deleted', 'policy_documents', ['is_deleted'])
    
    # Create policy_sections table
    op.create_table(
        'policy_sections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policy_documents.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('section_type', sa.Enum('COVERAGE_CRITERIA', 'EXCLUSIONS', 'REQUIREMENTS', 'DEFINITIONS', 'PRIOR_AUTHORIZATION', 'LIMITATIONS', 'APPEALS_PROCESS', 'OTHER', name='section_type'), nullable=False),
        sa.Column('section_number', sa.String(50), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('content_structured', postgresql.JSONB(), nullable=True),
        sa.Column('extraction_confidence_score', sa.Float(), nullable=True),
        sa.Column('page_numbers', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)', name='check_section_confidence_score_range'),
        sa.CheckConstraint('order_index >= 0', name='check_order_index_non_negative')
    )
    op.create_index('ix_policy_sections_policy_document_id', 'policy_sections', ['policy_document_id'])
    op.create_index('ix_policy_sections_section_type', 'policy_sections', ['section_type'])
    
    # Create coverage_criteria table
    op.create_table(
        'coverage_criteria',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_section_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policy_sections.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('procedure_name', sa.String(500), nullable=False),
        sa.Column('procedure_code', sa.String(50), nullable=True),
        sa.Column('covered_scenarios', sa.Text(), nullable=False),
        sa.Column('required_documentation', sa.Text(), nullable=True),
        sa.Column('prior_authorization_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('age_restrictions', sa.String(200), nullable=True),
        sa.Column('frequency_limitations', sa.String(200), nullable=True),
        sa.Column('extraction_confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)', name='check_coverage_confidence_score_range')
    )
    op.create_index('ix_coverage_criteria_policy_section_id', 'coverage_criteria', ['policy_section_id'])
    op.create_index('ix_coverage_criteria_procedure_name', 'coverage_criteria', ['procedure_name'])
    op.create_index('ix_coverage_criteria_procedure_code', 'coverage_criteria', ['procedure_code'])
    
    # Create exclusions table
    op.create_table(
        'exclusions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_section_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policy_sections.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('excluded_procedure', sa.String(500), nullable=False),
        sa.Column('exclusion_rationale', sa.Text(), nullable=True),
        sa.Column('exceptions_to_exclusion', sa.Text(), nullable=True),
        sa.Column('extraction_confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('extraction_confidence_score IS NULL OR (extraction_confidence_score >= 0.0 AND extraction_confidence_score <= 1.0)', name='check_exclusion_confidence_score_range')
    )
    op.create_index('ix_exclusions_policy_section_id', 'exclusions', ['policy_section_id'])
    
    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_type', sa.Enum('INGESTION', 'SCRAPING', name='job_type'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'RETRYING', 'COMPLETED', 'FAILED', 'CANCELLED', name='job_status'), nullable=False),
        sa.Column('payer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payers.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('policy_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('policy_documents.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_stacktrace', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.String(255), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('retry_count >= 0', name='check_retry_count_non_negative'),
        sa.CheckConstraint('max_retries > 0', name='check_max_retries_positive'),
        sa.CheckConstraint('retry_count <= max_retries', name='check_retry_count_within_max')
    )
    op.create_index('ix_processing_jobs_job_type', 'processing_jobs', ['job_type'])
    op.create_index('ix_processing_jobs_status', 'processing_jobs', ['status'])
    op.create_index('ix_processing_jobs_payer_id', 'processing_jobs', ['payer_id'])
    op.create_index('ix_processing_jobs_policy_document_id', 'processing_jobs', ['policy_document_id'])
    op.create_index('ix_processing_jobs_celery_task_id', 'processing_jobs', ['celery_task_id'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('action_type', sa.Enum('LOGIN', 'LOGOUT', 'UPLOAD_DOCUMENT', 'DELETE_DOCUMENT', 'UPDATE_SCRAPING_CONFIG', 'MANUAL_REVIEW_COMPLETE', 'SEARCH_QUERY', 'POLICY_COMPARISON', 'USER_CREATED', 'USER_ROLE_CHANGED', name='action_type'), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_logs')
    op.drop_table('processing_jobs')
    op.drop_table('exclusions')
    op.drop_table('coverage_criteria')
    op.drop_table('policy_sections')
    op.drop_table('policy_documents')
    op.drop_table('payers')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE action_type")
    op.execute("DROP TYPE job_status")
    op.execute("DROP TYPE job_type")
    op.execute("DROP TYPE section_type")
    op.execute("DROP TYPE processing_status")
    op.execute("DROP TYPE document_type")
    op.execute("DROP TYPE user_role")
