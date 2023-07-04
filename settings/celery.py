# Python
from os import environ

# Celery
from celery import Celery
from celery.schedules import crontab

# Django
from django.conf import settings


environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')
app: Celery = Celery(
    'settings',
    broker=settings.CELERY_BROKER_URL,
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.beat_schedule = {
    'every-week': {
        'task': 'clean-invites',
        'schedule': crontab(day_of_week='mon')
    },
    'every-day': {
        'task': 'send-mail-new-skins',
        'schedule': crontab(hour=20, minute=30)
    }
}
app.conf.timezone = 'Asia/Almaty'

