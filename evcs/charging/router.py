from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from evcs.schemas import Message
from evcs import database

from . import service
from .schemas import ChargingStatusPublic, CreateResource
from .tasks import process_status_payload

router = APIRouter(tags=['charging_status'])


@router.post(
    '/charging_status',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
)
async def add_status(payload: Any = Body(None)):
    process_status_payload.delay(payload)
    return {'detail': 'success'}


@router.get(
    '/charging_status/{charging_id}',
    response_model=ChargingStatusPublic,
)
async def read_status(
    charging_id: UUID, db: Session = Depends(database.get_session)
):
    charging_status = await service.get_charging_status(charging_id, db)

    if charging_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    charging_status.estimated_conclusion = (
        service.calculate_estimation_charging_conclusion(
            charging_status.id, db
        )
    )

    return charging_status


@router.post('/create_resources', status_code=status.HTTP_201_CREATED)
async def create_api_resources(
    payload: CreateResource, db: Session = Depends(database.get_session)
):
    await service.create_api_resources(payload, db)

    return payload
