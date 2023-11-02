import httpx
from celery import Celery
from pydantic import ValidationError
from sqlalchemy import select

from evcs.database import get_session
from evcs.models import (
    ChargePoint,
    ChargingSession,
    ChargingStatus,
    ErrorLog,
    ErrorType,
    Vehicle,
)
from evcs.schemas import ChargingStatusInput, ChargingStatusSlowMonitor
from evcs.service import charging_is_taking_longer
from evcs.settings import Settings

celery = Celery('evcs')
celery.config_from_object(Settings, namespace='CELERY')

session = next(get_session())


@celery.task(name='process_status')
def process_status(event):
    try:
        charging_status = ChargingStatusInput.model_validate(event)
    except ValidationError as exc:
        error = ErrorLog(
            type=ErrorType.payload_validation,
            errors=exc.errors(include_url=False),
        )
        session.add(error)
        session.commit()
        return

    vehicle = session.scalar(
        select(Vehicle).where(Vehicle.id == charging_status.vehicle_id)
    )
    charge_point = session.scalar(
        select(ChargePoint).where(
            ChargePoint.id == charging_status.charge_point_id
        )
    )
    charging_session = session.scalar(
        select(ChargingSession).where(
            ChargingSession.id == charging_status.charging_session_id
        )
    )

    if all((vehicle, charge_point, charging_session)):
        db_charging_status = ChargingStatus(**charging_status.model_dump())
        session.add(db_charging_status)
        session.commit()
        session.refresh(db_charging_status)

        check_taking_longer.delay(db_charging_status.id)

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
        error = ErrorLog(type=ErrorType.missing_resource, errors=errors)
        session.add(error)
        session.commit()


@celery.task(name='check_taking_longer')
def check_taking_longer(charging_status_id: int):
    # The idea here is to push to a dashboard or any monitoring app.
    external_url = 'https://webhook.site/9f4d7984-9235-4481-b6c6-a25cc488a316'
    if charging_is_taking_longer(charging_status_id):
        charging_status = session.scalar(
            select(ChargingStatus).where(
                ChargingStatus.id == charging_status_id
            )
        )
        headers = {'Content-Type': 'application/json', 'Accept': '*/*'}
        payload = ChargingStatusSlowMonitor(
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
