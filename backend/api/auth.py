"""
Authentication API endpoints for SolarRally
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from models.user import (
    User, UserCreate, UserUpdate, UserRead, 
    Role, RoleSchema, ChargingSession, ChargingSessionSchema, UserStats
)
from db.database import get_async_session
from utils.auth import (
    fastapi_users, auth_backend, current_active_user,
    get_user_with_role, require_admin, require_operator, require_user,
    check_user_owns_resource, get_current_user_role_name
)

# Create router
router = APIRouter()

# Include FastAPI Users authentication routes
auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router(UserRead)

# Include all FastAPI Users routes
router.include_router(auth_router, prefix="/jwt", tags=["auth"])
router.include_router(register_router, prefix="/register", tags=["auth"])
router.include_router(reset_password_router, prefix="/reset", tags=["auth"])
router.include_router(verify_router, prefix="/verify", tags=["auth"])

# Custom authentication endpoints

@router.get("/me", response_model=UserRead, tags=["auth"])
async def get_current_user(user: User = Depends(get_user_with_role)):
    """Get current user information with role"""
    return user

@router.get("/me/role", tags=["auth"])
async def get_current_user_role(role_name: str = Depends(get_current_user_role_name)):
    """Get current user's role name"""
    return {"role": role_name}

@router.put("/me", response_model=UserRead, tags=["auth"])
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update current user profile"""
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    
    return current_user

# User management endpoints (Admin only)

@router.get("/users", response_model=List[UserRead], tags=["admin"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """List all users (Admin only)"""
    query = select(User).options(selectinload(User.role)).offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()
    return users

@router.get("/users/{user_id}", response_model=UserRead, tags=["admin"])
async def get_user(
    user_id: uuid.UUID,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """Get specific user (Admin only)"""
    query = select(User).options(selectinload(User.role)).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserRead, tags=["admin"])
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """Update specific user (Admin only)"""
    user = await session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.delete("/users/{user_id}", tags=["admin"])
async def delete_user(
    user_id: uuid.UUID,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete specific user (Admin only)"""
    user = await session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await session.delete(user)
    await session.commit()
    
    return {"message": "User deleted successfully"}

# Role management endpoints

@router.get("/roles", response_model=List[RoleSchema], tags=["roles"])
async def list_roles(
    user: User = Depends(require_operator),
    session: AsyncSession = Depends(get_async_session)
):
    """List all roles (Operator+ access)"""
    query = select(Role)
    result = await session.execute(query)
    roles = result.scalars().all()
    return roles

@router.put("/users/{user_id}/role", response_model=UserRead, tags=["admin"])
async def assign_user_role(
    user_id: uuid.UUID,
    role_id: int,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """Assign role to user (Admin only)"""
    user = await session.get(User, user_id)
    role = await session.get(Role, role_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    user.role_id = role_id
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

# User session management

@router.get("/me/sessions", response_model=List[ChargingSessionSchema], tags=["sessions"])
async def get_user_sessions(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current user's charging sessions"""
    query = select(ChargingSession).where(ChargingSession.user_id == current_user.id)
    result = await session.execute(query)
    sessions = result.scalars().all()
    return sessions

@router.get("/me/stats", response_model=UserStats, tags=["sessions"])
async def get_user_stats(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current user's charging statistics"""
    query = select(ChargingSession).where(ChargingSession.user_id == current_user.id)
    result = await session.execute(query)
    sessions = result.scalars().all()
    
    if not sessions:
        return UserStats(
            total_sessions=0,
            total_energy_kwh=0.0,
            total_cost_jmd=0.0,
            energy_solar_kwh=0.0,
            energy_grid_kwh=0.0,
            cost_solar_jmd=0.0,
            cost_grid_jmd=0.0,
            avg_session_energy=0.0,
            solar_percentage=0.0
        )
    
    # Calculate statistics
    total_sessions = len(sessions)
    total_energy_wh = sum(s.total_energy_kwh for s in sessions)
    total_energy_kwh = total_energy_wh / 1000.0  # Convert Wh to kWh
    
    energy_solar_wh = sum(s.energy_solar_kwh for s in sessions)
    energy_grid_wh = sum(s.energy_grid_kwh for s in sessions)
    energy_solar_kwh = energy_solar_wh / 1000.0
    energy_grid_kwh = energy_grid_wh / 1000.0
    
    total_cost_cents = sum(s.total_cost_jmd for s in sessions)
    cost_solar_cents = sum(s.cost_solar_jmd for s in sessions)
    cost_grid_cents = sum(s.cost_grid_jmd for s in sessions)
    
    total_cost_jmd = total_cost_cents / 100.0  # Convert cents to JMD
    cost_solar_jmd = cost_solar_cents / 100.0
    cost_grid_jmd = cost_grid_cents / 100.0
    
    avg_session_energy = total_energy_kwh / total_sessions if total_sessions > 0 else 0.0
    solar_percentage = (energy_solar_kwh / total_energy_kwh * 100) if total_energy_kwh > 0 else 0.0
    
    return UserStats(
        total_sessions=total_sessions,
        total_energy_kwh=total_energy_kwh,
        total_cost_jmd=total_cost_jmd,
        energy_solar_kwh=energy_solar_kwh,
        energy_grid_kwh=energy_grid_kwh,
        cost_solar_jmd=cost_solar_jmd,
        cost_grid_jmd=cost_grid_jmd,
        avg_session_energy=avg_session_energy,
        solar_percentage=solar_percentage
    )

# Admin session management

@router.get("/sessions", response_model=List[ChargingSessionSchema], tags=["admin"])
async def list_all_sessions(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """List all charging sessions (Admin only)"""
    query = select(ChargingSession).offset(skip).limit(limit)
    result = await session.execute(query)
    sessions = result.scalars().all()
    return sessions

@router.get("/users/{user_id}/sessions", response_model=List[ChargingSessionSchema], tags=["admin"])
async def get_user_sessions_admin(
    user_id: uuid.UUID,
    admin_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_async_session)
):
    """Get specific user's sessions (Admin only)"""
    query = select(ChargingSession).where(ChargingSession.user_id == user_id)
    result = await session.execute(query)
    sessions = result.scalars().all()
    return sessions 