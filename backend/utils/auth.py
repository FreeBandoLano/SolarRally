"""
Authentication utilities for SolarRally
Uses FastAPI Users for comprehensive user management
"""

import os
import uuid
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTAuthentication,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from dotenv import load_dotenv

from models.user import User, UserCreate, UserUpdate, UserRead, Role
from db.database import get_async_session

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET = os.getenv("JWT_SECRET_KEY", "your-super-secure-secret-key-change-in-production")
JWT_LIFETIME_SECONDS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")) * 60

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Custom user manager with additional functionality"""
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[any] = None):
        """Called after successful user registration"""
        print(f"✅ User {user.email} has registered.")

    async def on_after_login(
        self,
        user: User,
        request: Optional[any] = None,
        response: Optional[any] = None,
    ):
        """Called after successful login"""
        # Update last_login timestamp
        from datetime import datetime, timezone
        user.last_login = datetime.now(timezone.utc)
        print(f"🔐 User {user.email} logged in.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[any] = None
    ):
        """Called after forgot password request"""
        print(f"📧 User {user.email} has forgotten their password. Reset token: {token}")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get user database dependency"""
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager dependency"""
    yield UserManager(user_db)

# Authentication backends
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=JWT_LIFETIME_SECONDS,
    tokenUrl="auth/jwt/login",
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=lambda: jwt_authentication,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# Dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Permission checking utilities

async def get_user_with_role(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """Get current user with role information loaded"""
    # Reload user with role relationship
    query = select(User).options(selectinload(User.role)).where(User.id == user.id)
    result = await session.execute(query)
    user_with_role = result.scalar_one_or_none()
    
    if not user_with_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_with_role

def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""
    async def permission_checker(
        user: User = Depends(get_user_with_role)
    ) -> User:
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )
        
        user_permissions = user.role.permissions or []
        
        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - set(user_permissions)
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}"
            )
        
        return user
    
    return permission_checker

# Role-based dependencies
require_admin = require_permissions([
    "users:read", "users:write", "users:delete",
    "evse:read", "evse:write", "evse:control",
    "sessions:read", "sessions:write", "sessions:delete",
    "analytics:read", "system:configure"
])

require_operator = require_permissions([
    "evse:read", "evse:control",
    "sessions:read", "sessions:write",
    "analytics:read"
])

require_user = require_permissions([
    "sessions:read_own", "sessions:write_own",
    "profile:read", "profile:write"
])

# Utility functions

async def check_user_owns_resource(
    user: User,
    resource_user_id: uuid.UUID
) -> bool:
    """Check if user owns a resource or is admin"""
    if user.role and "admin" in user.role.name:
        return True  # Admins can access all resources
    
    return user.id == resource_user_id

async def get_current_user_role_name(
    user: User = Depends(get_user_with_role)
) -> str:
    """Get current user's role name"""
    return user.role.name if user.role else "no_role" 