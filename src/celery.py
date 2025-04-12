from celery.schedules import crontab
from celery import Celery

CELERY_BEAT_SCHEDULE = {
    'sync-shopify-data-incremental-every-6-hours': {
        'task': 'sync_shopify_data',
        'schedule': crontab(minute=0, hour='*/6'),  # every 6 hours
        'args': ('"56d3a472-2a5e-4abb-88ea-64aa766a53e7"', 'incremental')  # you can pass dynamic user_ids later
    },
}

app = Celery("myapp")
app.config_from_object("myapp.celeryconfig", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
