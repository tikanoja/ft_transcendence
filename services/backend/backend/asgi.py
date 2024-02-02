"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from backend.routing import websocket_urlpatterns
# from channels.auth import AuthMiddlewareStack Add this is authentication needed
from pong.consumers import PongConsumer
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# wrap URLrouter in authmiddlewarestack if auth needed
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        [
            path("ws/pong/", PongConsumer.as_asgi()),
        ]
    ),
})
