from django.urls import path
from app.consumers import UserConsumer
from pong.consumers import PongConsumer

websocket_urlpatterns = [
    path("ws/app/", UserConsumer.as_asgi()),
    path("pong/", PongConsumer.as_asgi()),
]
