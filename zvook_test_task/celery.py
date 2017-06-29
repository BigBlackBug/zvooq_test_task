from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zvook_test_task.settings')

app = Celery('zvook_test_task')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
