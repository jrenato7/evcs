from sqlalchemy import func, select
from evcs.models import ErrorLog

from evcs.worker import process_status


def test_process_status_invalid_payload(session):
    statement = select(func.count()).select_from(ErrorLog)
    previous_errors_table_count = session.execute(statement).scalar()

    process_status({'invalid': 'payload'})

    assert previous_errors_table_count == 0
