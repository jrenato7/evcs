from typing import Annotated, Any
from uuid import UUID

from fastapi import Body, Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from evcs.database import get_session
from evcs.models import ChargingStatus, Vehicle, ChargePoint, ChargingSession
from evcs.schemas import ChargingStatusPublic, Message, CreateResource
from evcs.service import calculate_estimation_charging_conclusion
from evcs.worker import process_status

app = FastAPI()

Session = Annotated[Session, Depends(get_session)]


@app.get('/')
def get_root():
    return {'message': "I'm alive!"}


@app.post(
    '/charging_status',
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
)
async def add_status(payload: Any = Body(None)):
    process_status.delay(payload)
    return {'detail': 'success'}


@app.get(
    '/charging_status/{charging_id}',
    response_model=ChargingStatusPublic,
)
async def read_status(charging_id: UUID, session: Session):
    charging_status = session.scalar(
        select(ChargingStatus)
        .where(ChargingStatus.charging_session_id == charging_id)
        .order_by(ChargingStatus.id.desc())
        .limit(1)
    )
    if charging_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    charging_status.estimated_conclusion = (
        calculate_estimation_charging_conclusion(charging_status.id)
    )

    return charging_status


@app.post('/add_vehicle')
def create_api_resources(session: Session, payload: CreateResource):
    vehicle = Vehicle(
        id=payload.vehicle_id,
        battery_capacity=payload.battery_capacity,
        max_charging_power=payload.max_charging_power,
    )
    charge_point = ChargePoint(id=payload.charge_point_id)
    charging_session = ChargingSession(id=payload.charging_session_id)
    session.add(charge_point)
    session.add(charging_session)
    session.add(vehicle)

    session.commit()

    return payload
