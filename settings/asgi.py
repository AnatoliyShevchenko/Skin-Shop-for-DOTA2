import os

from django.core.asgi import get_asgi_application
from django.conf import settings

from logging.config import dictConfig
from channels.routing import ProtocolTypeRouter, URLRouter

from .routing import websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')

dictConfig(settings.LOGGING)

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(websocket_urlpatterns),
})

