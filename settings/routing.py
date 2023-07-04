from django.urls import re_path

from .consumers import ActivationAccountConsumer


websocket_urlpatterns = [
    re_path('account_activation/', ActivationAccountConsumer.as_asgi()),
]
