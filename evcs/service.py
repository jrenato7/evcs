from fastapi import Depends
from sqlalchemy.orm import Session

from evcs import database
from evcs.models import ErrorLog


async def create_error(
    error_type: str,
    errors: list[dict],
    db: Session = Depends(database.get_session),
):
    error = ErrorLog(
        type=error_type,
        errors=errors,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error
