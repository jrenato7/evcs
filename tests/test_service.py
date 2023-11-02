# from datetime import datetime
#
# from freezegun import freeze_time
#
# from evcs.models import ChargingStatus
from evcs.service import charging_is_taking_longer


def test_charging_is_taking_longer_first_record(session, charging_status_1):
    assert not charging_is_taking_longer(charging_status_1.id)


def test_charging_is_taking_longer_last_record(session, charging_status_3):
    assert not charging_is_taking_longer(charging_status_3.id)


# def test_charging_is_taking_longer_has_fifteen(session, charging_status_2):
#     charging_status = ChargingStatus(
#         current_progress=51.65,
#         charge_point_id=charging_status_2.charge_point_id,
#         vehicle_id=charging_status_2.vehicle_id,
#         charging_session_id=charging_status_2.charging_session_id,
#     )
#     with freeze_time('2023-11-02 02:44:10'):
#         charging_status.create_date = datetime.now()
#         session.add(charging_status)
#         session.commit()
#         session.refresh(charging_status)
#
#     assert charging_is_taking_longer(charging_status_2.id)
