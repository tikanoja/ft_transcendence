from django.urls import path
from pong.consumers import PongConsumer

websocket_urlpatterns = [
    path("ws/pong/", PongConsumer.as_asgi()),
]
