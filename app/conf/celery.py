from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('conf')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'get-stats-every-30-seconds': {
        'task': 'main.tasks.get_current_stats',
        'schedule': 31.0,
        'args': ()
    },

    'compire-chaos-configs-every-5-minutes': {
        'task': 'main.tasks.compire_chaos_configs',
        'schedule': crontab(minute='*/5'),
        'args': ()
    },

}

app.autodiscover_tasks()
