from typing import Any

from pydantic import BaseModel, Json

from evcs.models import ErrorType


class Message(BaseModel):
    detail: str


class Error(BaseModel):
    errors: Json[Any]
    type: ErrorType
