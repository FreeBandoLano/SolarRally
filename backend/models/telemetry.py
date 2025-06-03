"""
Pydantic models for telemetry data
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class EnergySource(str, Enum):
    """Energy source enumeration"""
    SOLAR = "solar"
    GRID = "grid"
    NONE = "none"


class ChargingStatus(str, Enum):
    """Charging status enumeration"""
    AVAILABLE = "available"
    PREPARING = "preparing"
    CHARGING = "charging"
    FINISHING = "finishing"
    FAULTED = "faulted"


class TelemetryData(BaseModel):
    """Real-time telemetry data from the charging station"""
    timestamp: datetime
    session_id: Optional[str] = None
    voltage_v: float = Field(ge=0, description="Voltage in volts")
    current_a: float = Field(ge=0, description="Current in amperes")
    power_w: float = Field(ge=0, description="Power in watts")
    session_energy_kwh_solar: float = Field(ge=0, description="Session energy from solar (kWh)")
    session_energy_kwh_grid: float = Field(ge=0, description="Session energy from grid (kWh)")
    session_total_energy_kwh: float = Field(ge=0, description="Total session energy (kWh)")
    energy_source: EnergySource
    temperature_c: float = Field(description="Temperature in Celsius")
    status: ChargingStatus

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionSummary(BaseModel):
    """Summary of a charging session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_energy_kwh: float = Field(ge=0)
    solar_energy_kwh: float = Field(ge=0)
    grid_energy_kwh: float = Field(ge=0)
    duration_minutes: Optional[int] = None
    cost_solar: float = Field(ge=0, description="Cost for solar energy")
    cost_grid: float = Field(ge=0, description="Cost for grid energy")
    total_cost: float = Field(ge=0, description="Total session cost")
    final_status: ChargingStatus

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TariffRates(BaseModel):
    """Energy pricing configuration"""
    solar_rate_per_kwh: float = Field(default=10.0, ge=0, description="JM$ per kWh for solar")
    grid_rate_per_kwh: float = Field(default=50.0, ge=0, description="JM$ per kWh for grid")

    class Config:
        schema_extra = {
            "example": {
                "solar_rate_per_kwh": 10.0,
                "grid_rate_per_kwh": 50.0
            }
        } 