import uuid
from datetime import datetime

import pytest

from freezegun import freeze_time

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from evcs.app import app
from evcs.database import get_session
from evcs.models import (
    Base,
    ChargingStatus,
    ChargePoint,
    ChargingSession,
    Vehicle,
)


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    yield Session()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def vehicle(session):

    vehicle = Vehicle(
        id=uuid.uuid4(),
        battery_capacity=100.0,
        max_charging_power=11.5,
    )
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    return vehicle


@pytest.fixture
def charge_point(session):
    charge_point = ChargePoint(id=uuid.uuid4())
    session.add(charge_point)
    session.commit()
    session.refresh(charge_point)

    return charge_point


@pytest.fixture
def charging_session(session):
    charging_session = ChargingSession(id=uuid.uuid4())
    session.add(charging_session)
    session.commit()
    session.refresh(charging_session)

    return charging_session


@pytest.fixture
def charging_status_1(session, vehicle, charge_point, charging_session):
    charging_status = ChargingStatus(
        id=1,
        current_progress=35.10,
        charge_point_id=charge_point.id,
        vehicle_id=vehicle.id,
        charging_session_id=charging_session.id,
    )
    with freeze_time('2023-11-02 01:23:27'):
        charging_status.create_date = datetime.now()
        session.add(charging_status)
        session.commit()
        session.refresh(charging_status)

    return charging_status


@pytest.fixture
def charging_status_2(session, vehicle, charge_point, charging_session):
    charging_status = ChargingStatus(
        id=1,
        current_progress=51.65,
        charge_point_id=charge_point.id,
        vehicle_id=vehicle.id,
        charging_session_id=charging_session.id,
    )
    with freeze_time('2023-11-02 03:00:10'):
        charging_status.create_date = datetime.now()
        session.add(charging_status)
        session.commit()
        session.refresh(charging_status)

    return charging_status


@pytest.fixture
def charging_status_3(session, vehicle, charge_point, charging_session):
    charging_status = ChargingStatus(
        id=1,
        current_progress=87.95,
        charge_point_id=charge_point.id,
        vehicle_id=vehicle.id,
        charging_session_id=charging_session.id,
    )
    with freeze_time('2023-11-02 08:50:12'):
        charging_status.create_date = datetime.now()
        session.add(charging_status)
        session.commit()
        session.refresh(charging_status)

    return charging_status
