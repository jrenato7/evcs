import uuid
from unittest import mock

import pytest
from sqlalchemy import select

from evcs.models import Vehicle


def test_root_must_return_200_and_message(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': "I'm alive!"}


@pytest.mark.parametrize(
    'payload,status_code',
    [
        ({}, 201),
        ({'foo': 'bar'}, 201),
        (
            {
                'vehicle_id': '33fe5b42-f717-43f6-ba0a-eab4cae81bfa',
                'charge_point_id': '33fe5b42-f717-43f6-ba0a-eab4cae81bfa',
                'charging_session_id': '33fe5b42-f717-43f6-ba0a-eab4cae81bfa',
                'current_progress': 63.23,
            },
            201,
        ),
    ],
)
def test_add_status_should_work_with_anything(client, payload, status_code):
    with mock.patch('evcs.worker.process_status.delay'):
        response = client.post('/charging_status', data=payload)

    assert response.status_code == status_code
    assert response.json() == {'detail': 'success'}


def test_read_status_invalid_id(client, session):
    charging_id = uuid.uuid4()
    response = client.get(f'/charging_status/{charging_id}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_status_valid(client, session, charging_status_1):
    response = client.get(
        f'/charging_status/{charging_status_1.charging_session_id}'
    )
    assert response.status_code == 200
    assert response.json() == {
        'charge_point_id': str(charging_status_1.charge_point_id),
        'charging_session_id': str(charging_status_1.charging_session_id),
        'estimated_conclusion': '2023-11-02T10:55:00',
        'vehicle_id': str(charging_status_1.vehicle_id),
    }


def test_create_api_resources(client, session):
    response = client.post(
        '/create_resources',
        json={
            'vehicle_id': '06884e7c-09b6-41a2-9ed8-1d68c46082a8',
            'charge_point_id': 'c0e6d068-4fd8-4a03-b6de-2e429dcdbfd5',
            'charging_session_id': '4b56a8b6-9bdc-40c4-96a7-06d9f24a9c66',
            'battery_capacity': 378,
            'max_charging_power': 22.97,
        },
    )
    db_vehicle = session.scalar(
        select(Vehicle).where(
            Vehicle.id == uuid.UUID('06884e7c-09b6-41a2-9ed8-1d68c46082a8')
        )
    )
    assert response.status_code == 201
    assert db_vehicle
