"""
User authentication models for SolarRally
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class Role(Base):
    """User roles table"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = relationship("User", back_populates="role")

class User(SQLAlchemyBaseUserTable[uuid.UUID], Base):
    """User table extending FastAPI Users base table"""
    __tablename__ = "users"
    
    # Additional user fields beyond FastAPI Users base
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    
    # Role relationship
    role_id = Column(Integer, ForeignKey("roles.id"), default=3)  # Default to 'user' role
    role = relationship("Role", back_populates="users")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True))
    
    # User preferences
    preferences = Column(JSON, default=dict)

class ChargingSession(Base):
    """Charging sessions linked to users"""
    __tablename__ = "charging_sessions"
    
    id = Column(String, primary_key=True, index=True)  # session_id from MQTT
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    evse_unit_id = Column(String(50), nullable=False)
    
    # Session data
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True))
    energy_solar_kwh = Column(Integer, default=0)  # Store as Wh for precision
    energy_grid_kwh = Column(Integer, default=0)   # Store as Wh for precision
    total_energy_kwh = Column(Integer, default=0)  # Store as Wh for precision
    
    # Cost calculation (in JMD cents for precision)
    cost_solar_jmd = Column(Integer, default=0)    # JMD cents
    cost_grid_jmd = Column(Integer, default=0)     # JMD cents
    total_cost_jmd = Column(Integer, default=0)    # JMD cents
    
    # Status
    status = Column(String(20), default="active")  # active, completed, terminated
    
    # Relationships
    user = relationship("User")

# Pydantic schemas for API

class UserRead(schemas.BaseUser[uuid.UUID]):
    """User read schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    preferences: Optional[dict] = None

class UserCreate(schemas.BaseUserCreate):
    """User creation schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = 3  # Default to 'user' role

class UserUpdate(schemas.BaseUserUpdate):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = None

class RoleSchema(BaseModel):
    """Role schema"""
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[list] = []
    
    class Config:
        from_attributes = True

class ChargingSessionSchema(BaseModel):
    """Charging session schema"""
    id: str
    user_id: Optional[uuid.UUID] = None
    evse_unit_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_solar_kwh: float
    energy_grid_kwh: float
    total_energy_kwh: float
    cost_solar_jmd: float
    cost_grid_jmd: float
    total_cost_jmd: float
    status: str
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """User statistics schema"""
    total_sessions: int
    total_energy_kwh: float
    total_cost_jmd: float
    energy_solar_kwh: float
    energy_grid_kwh: float
    cost_solar_jmd: float
    cost_grid_jmd: float
    avg_session_energy: float
    solar_percentage: float 