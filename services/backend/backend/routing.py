# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from pong.consumers import PongConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
			path("ws/pong/", PongConsumer.as_asgi()),
        )
    ),
})
