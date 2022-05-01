import os
from celery import Celery
from django.conf import settings

# import django

# django.setup()
# from apps.sensors_group.tasks import poll_source_dirs

MODE = os.environ.get('MODE', "dev")

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      f'houm_challenge.settings.base')

# print("DSM",os.environ.get("DJANGO_SETTINGS_MODULE"))

app = Celery('houm_challenge')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_TIMEZONE = settings.CELERY_TIMEZONE

CELERY_IMPORTS ={
    'apps.tracking.tasks.property_presence',
}


# app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


