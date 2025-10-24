"""Seed initial data: admin user and Cigna payer."""
import asyncio
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bcrypt

from models.user import User, UserRole
from models.payer import Payer
from config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


async def seed_database():
    """Seed initial data into the database."""
    print("🌱 Seeding database...")
    
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username="admin",
            email="admin@policywarehouse.local",
            password_hash=hash_password("admin123"),  # Change in production!
            role=UserRole.ADMINISTRATOR,
            first_name="System",
            last_name="Administrator",
            is_active=True
        )
        session.add(admin)
        
        # Create analyst user for testing
        print("Creating analyst user...")
        analyst = User(
            username="analyst",
            email="analyst@policywarehouse.local",
            password_hash=hash_password("analyst123"),  # Change in production!
            role=UserRole.ANALYST,
            first_name="Test",
            last_name="Analyst",
            is_active=True
        )
        session.add(analyst)
        
        # Create Cigna payer
        print("Creating Cigna payer...")
        cigna = Payer(
            name="Cigna",
            website_url="https://www.cigna.com",
            scraping_enabled=False,  # Will be configured later
            is_active=True
        )
        session.add(cigna)
        
        # Commit all changes
        await session.commit()
        
        print("✅ Database seeded successfully!")
        print("\nDefault credentials:")
        print("  Admin - username: admin, password: admin123")
        print("  Analyst - username: analyst, password: analyst123")
        print("\n⚠️  IMPORTANT: Change these passwords in production!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
