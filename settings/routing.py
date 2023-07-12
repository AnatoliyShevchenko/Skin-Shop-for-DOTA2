from django.urls import re_path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from .consumers import ChatConsumer


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"^ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
                    ]
                )
            )
        ),
    }
)
