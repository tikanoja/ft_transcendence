from django.urls import path
from app.consumers import UserConsumer

websocket_urlpatterns = [
    path("ws/app/", UserConsumer.as_asgi()),
]
