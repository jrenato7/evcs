import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from evcs.database import Base


# I'm abstracting the vehicle class here, expecting that it should be an object
# response from the endpoint
# https://doc.ampcontrol.io/#tag/Vehicles/paths/~1v2~1vehicles~1%7Bid%7D/get
class Vehicle(Base):
    __tablename__ = 'vehicle'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    battery_capacity: Mapped[float]
    max_charging_power: Mapped[float]


# I'm abstracting the ChargePoint, expecting that it should be an object
# response from the endpoint
# https://doc.ampcontrol.io/#tag/Charge-points/paths/~1v2~1charge_points~1/get
class ChargePoint(Base):
    __tablename__ = 'charge_point'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)


# I'm abstracting the Charging Session here, expecting that it should be an object
# response from the endpoint
# https://doc.ampcontrol.io/#tag/Charging-sessions/paths/~1v2~1charging_sessions~1/get
class ChargingSession(Base):
    __tablename__ = 'charging_session'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    charging_status: Mapped[list['ChargingStatus']] = relationship(
        back_populates='', cascade='all, delete-orphan'
    )


class ChargingStatus(Base):
    __tablename__ = 'charging_status'

    id: Mapped[int] = mapped_column(primary_key=True)
    current_progress: Mapped[float]
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    charge_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('charge_point.id')
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('vehicle.id'))
    charging_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('charging_session.id')
    )

    charging_session: Mapped[ChargingSession] = relationship(
        back_populates='charging_status'
    )
