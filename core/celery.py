from __future__ import absolute_import, unicode_literals
import os
import pytz
import datetime
from django.utils import timezone
from celery import Celery
import logging
logger = logging.getLogger("Celery")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


app = Celery('django_boilerplate')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    worker_pool_restarts=True,
)

app.autodiscover_tasks()


def utc_now():
    return datetime.datetime.now(pytz.utc)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
