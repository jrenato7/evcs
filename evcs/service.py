from datetime import timedelta

from sqlalchemy import and_, select

from evcs.database import get_session
from evcs.models import ChargingStatus, Vehicle

session = next(get_session())


def calculate_estimation_charging_conclusion(charging_status_id: int):
    """
    Calculates the time when the charging will conclude based on the session
    start time, charging status created time, charging status current_progress

    Take a look at https://footprinthero.com/battery-charge-time-calculator

    :param charging_status_id:
    :return: datetime
    """
    charging_status = session.scalar(
        select(ChargingStatus).where(ChargingStatus.id == charging_status_id)
    )
    vehicle = session.scalar(
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


def charging_is_taking_longer(charging_status_id: int):
    charging_status = session.scalar(
        select(ChargingStatus).where(ChargingStatus.id == charging_status_id)
    )
    fifteen_minutes_ago = charging_status.create_date - timedelta(minutes=15)
    status_fifteen_ago = session.scalar(
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
