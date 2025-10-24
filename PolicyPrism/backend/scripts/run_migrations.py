"""Run database migrations directly using asyncpg."""
import asyncio
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine
from config import settings
from models.base import Base
from models.user import User
from models.payer import Payer
from models.policy_document import PolicyDocument
from models.policy_section import PolicySection
from models.coverage_criteria import CoverageCriteria
from models.exclusion import Exclusion
from models.processing_job import ProcessingJob
from models.audit_log import AuditLog


async def run_migrations():
    """Create all database tables."""
    print("🔄 Creating database tables...")
    
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Drop all tables (for clean slate)
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ Dropped existing tables")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Created all tables")
        
        print("\n✅ Database migration completed successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - payers")
        print("  - policy_documents")
        print("  - policy_sections")
        print("  - coverage_criteria")
        print("  - exclusions")
        print("  - processing_jobs")
        print("  - audit_logs")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migrations())
