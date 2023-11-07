from celery import Celery
from fastapi import FastAPI

from evcs.settings import Settings
from evcs.charging import router as charging_router


description = """
Charging Status API

## Users

You will be able to:

* **Create charging status** 
* **Estimate the conclusion time** 
"""

app = FastAPI(
    title='ChargingStatus',
    description=description,
    version='0.0.2',
    terms_of_service='http://example.com/terms/',
    contact={
        'name': 'José Barroso',
        'url': 'https://example.com/contact/',
    },
    license_info={
        'name': 'Apache 2.0',
        'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
)
app.include_router(charging_router.router)

celery = Celery('evcs')
celery.config_from_object(Settings, namespace='CELERY')

celery.conf.imports = [
    'evcs.charging.tasks',
]
