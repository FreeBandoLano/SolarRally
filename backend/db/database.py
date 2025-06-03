"""
Database configuration for SolarRally
Handles both telemetry data and user authentication
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://solarrally:solarrally123@localhost:5432/solarrally_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session

async def create_db_and_tables():
    """Create database tables"""
    from models.user import Base as UserBase
    
    async with engine.begin() as conn:
        # Create tables for user authentication
        await conn.run_sync(UserBase.metadata.create_all)
        
async def init_default_roles():
    """Initialize default roles in the database"""
    from models.user import Role
    
    default_roles = [
        {
            "id": 1,
            "name": "admin", 
            "description": "Full system access and user management",
            "permissions": [
                "users:read", "users:write", "users:delete",
                "evse:read", "evse:write", "evse:control",
                "sessions:read", "sessions:write", "sessions:delete",
                "analytics:read", "system:configure"
            ]
        },
        {
            "id": 2,
            "name": "operator",
            "description": "EVSE monitoring and session management", 
            "permissions": [
                "evse:read", "evse:control",
                "sessions:read", "sessions:write",
                "analytics:read"
            ]
        },
        {
            "id": 3,
            "name": "user",
            "description": "Personal charging sessions and statistics",
            "permissions": [
                "sessions:read_own", "sessions:write_own",
                "profile:read", "profile:write"
            ]
        },
        {
            "id": 4,
            "name": "guest",
            "description": "Limited read-only access",
            "permissions": [
                "system:status"
            ]
        }
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if roles already exist
            for role_data in default_roles:
                existing_role = await session.get(Role, role_data["id"])
                if not existing_role:
                    role = Role(**role_data)
                    session.add(role)
            
            await session.commit()
            print("✅ Default roles initialized")
        except Exception as e:
            await session.rollback()
            print(f"⚠️  Error initializing roles: {e}")
        finally:
            await session.close() 