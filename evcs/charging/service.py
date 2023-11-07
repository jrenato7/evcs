from datetime import timedelta
from typing import Any
from uuid import UUID

import httpx
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from evcs import database
from evcs.models import ErrorType
from evcs.service import create_error

from . import schemas
from .models import ChargingStatus, Vehicle, ChargePoint, ChargingSession
from .validators import validate_changing_status_payload


async def process_status(
    event: Any, db: Session = Depends(database.get_session)
):
    charging_status = await validate_changing_status_payload(event, db)
    if charging_status is None:
        return

    vehicle = db.scalar(
        select(Vehicle).where(Vehicle.id == charging_status.vehicle_id)
    )
    charge_point = db.scalar(
        select(ChargePoint).where(
            ChargePoint.id == charging_status.charge_point_id
        )
    )
    charging_session = db.scalar(
        select(ChargingSession).where(
            ChargingSession.id == charging_status.charging_session_id
        )
    )

    if all((vehicle, charge_point, charging_session)):
        db_charging_status = await create_charging_status(charging_status)

        return db_charging_status.id

    else:
        errors = [
            {'msg': f'The record {obj} was not found in the table {table}'}
            for obj, missing, table in (
                (charging_status.vehicle_id, vehicle, Vehicle),
                (charging_status.charge_point_id, charge_point, ChargePoint),
                (
                    charging_status.charging_session_id,
                    charging_session,
                    ChargingSession,
                ),
            )
            if not missing
        ]
        await create_error(ErrorType.missing_resource, errors, db)
        return


async def create_charging_status(
    charging_status: schemas.ChargingStatusInput,
    db: Session = Depends(database.get_session),
):
    db_charging_status = ChargingStatus(**charging_status.model_dump())
    db.add(db_charging_status)
    db.commit()
    db.refresh(db_charging_status)
    return db_charging_status


async def get_charging_status(
    charging_id: UUID, db: Session = Depends(database.get_session)
):
    charging_status = db.scalar(
        select(ChargingStatus)
        .where(ChargingStatus.charging_session_id == charging_id)
        .order_by(ChargingStatus.id.desc())
        .limit(1)
    )
    return charging_status


async def check_taking_longer(
    charging_status_id: int, db: Session = Depends(database.get_session)
):
    # The idea here is to push to a dashboard or any monitoring app.
    external_url = 'https://webhook.site/9f4d7984-9235-4481-b6c6-a25cc488a316'
    if await charging_is_taking_longer(charging_status_id):
        charging_status = db.scalar(
            select(ChargingStatus).where(
                ChargingStatus.id == charging_status_id
            )
        )
        headers = {'Content-Type': 'application/json', 'Accept': '*/*'}
        payload = schemas.ChargingStatusSlowMonitor(
            **{
                'msg': 'Session is taking longer to charge',
                'watch': {
                    'charge_point_id': charging_status.charge_point_id,
                    'vehicle_id': charging_status.vehicle_id,
                    'charging_session_id': charging_status.charging_session_id,
                    'current_progress': charging_status.current_progress,
                },
            }
        )

        httpx.post(
            external_url, json=payload.model_dump_json(), headers=headers
        )


async def create_api_resources(
    payload: schemas.CreateResource,
    db: Session = Depends(database.get_session),
):
    vehicle = Vehicle(
        id=payload.vehicle_id,
        battery_capacity=payload.battery_capacity,
        max_charging_power=payload.max_charging_power,
    )
    charge_point = ChargePoint(id=payload.charge_point_id)
    charging_session = ChargingSession(id=payload.charging_session_id)
    db.add(charge_point)
    db.add(charging_session)
    db.add(vehicle)

    db.commit()
    return vehicle


def calculate_estimation_charging_conclusion(
    charging_status_id: int, db: Session = Depends(database.get_session)
):
    """
    Calculates the time when the charging will conclude based on the session
    start time, charging status created time, charging status current_progress

    Take a look at https://footprinthero.com/battery-charge-time-calculator

    :param charging_status_id:
    :param db:
    :return: datetime
    """
    charging_status = db.scalar(
        select(ChargingStatus).where(ChargingStatus.id == charging_status_id)
    )
    vehicle = db.scalar(
        select(Vehicle).where(Vehicle.id == charging_status.vehicle_id)
    )
    charge_missing = vehicle.battery_capacity - (
        vehicle.battery_capacity * charging_status.current_progress / 100
    )
    missing_hours = charge_missing / vehicle.max_charging_power
    date_to_calculate = charging_status.create_date.replace(
        second=0, microsecond=0
    )
    result = date_to_calculate + timedelta(hours=missing_hours)
    return result.replace(second=0, microsecond=0)


async def charging_is_taking_longer(
    charging_status_id: int, db: Session = Depends(database.get_session)
):
    charging_status = db.scalar(
        select(ChargingStatus).where(ChargingStatus.id == charging_status_id)
    )
    fifteen_minutes_ago = charging_status.create_date - timedelta(minutes=15)
    status_fifteen_ago = db.scalar(
        select(ChargingStatus)
        .where(
            and_(
                ChargingStatus.create_date <= fifteen_minutes_ago,
                ChargingStatus.charging_session_id
                == charging_status.charging_session_id,
            )
        )
        .order_by(ChargingStatus.create_date.desc())
        .limit(1)
    )
    if status_fifteen_ago is None:
        return False

    # current_estimation = calculate_estimation_charging_conclusion(
    #     charging_status.id
    # )
    # previous_estimation = calculate_estimation_charging_conclusion(
    #     status_fifteen_ago.id
    # )
    # return current_estimation == previous_estimation
    return (
        charging_status.current_progress == status_fifteen_ago.current_progress
    )
