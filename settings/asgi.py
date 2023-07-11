import os

from django.core.asgi import get_asgi_application
from django.conf import settings

from logging.config import dictConfig


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')

dictConfig(settings.LOGGING)

application = get_asgi_application()
