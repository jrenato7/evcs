from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from evcs.database import Base


class ErrorType(str, Enum):
    payload_validation = 'payload_validation'
    missing_resource = 'missing_resource'


class ErrorLog(Base):
    __tablename__ = 'charging_error_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    errors: Mapped[JSON] = mapped_column(type_=JSON, nullable=False)
    type: Mapped[ErrorType]
