import uuid
from unittest import mock

import pytest


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
