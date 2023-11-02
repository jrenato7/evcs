from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, Json

from evcs.models import ErrorType


class Message(BaseModel):
    detail: str


class ChargingStatusInput(BaseModel):
    vehicle_id: UUID
    charge_point_id: UUID
    charging_session_id: UUID
    current_progress: float = Field(ge=0.0, le=100.0)


class ChargingStatusPublic(BaseModel):
    vehicle_id: UUID | None = None
    charge_point_id: UUID | None = None
    charging_session_id: UUID | None = None
    estimated_conclusion: datetime | None = None


class ChargingStatusSlowMonitor(BaseModel):
    msg: str
    watch: ChargingStatusInput


class Error(BaseModel):
    errors: Json[Any]
    type: ErrorType
