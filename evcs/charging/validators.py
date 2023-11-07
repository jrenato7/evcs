from typing import Any

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session

from evcs import database
from evcs.charging.schemas import ChargingStatusInput
from evcs.models import ErrorType
from evcs.service import create_error


async def validate_changing_status_payload(
    payload: Any, db: Session = Depends(database.get_session)
):
    try:
        charging_status = ChargingStatusInput.model_validate(payload)
    except ValidationError as exc:
        await create_error(
            ErrorType.payload_validation, exc.errors(include_url=False), db
        )
        return None

    return charging_status
