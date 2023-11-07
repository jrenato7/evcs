from celery import shared_task

from .service import process_status, check_taking_longer


@shared_task
def process_status_payload(payload):
    charging_status = process_status(payload)
    if charging_status is not None:
        monitoring_task_process.delay(charging_status.id)


@shared_task
def monitoring_task_process(charging_status_id: int):
    check_taking_longer(charging_status_id)
