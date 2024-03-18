from django.urls import path
from user.consumers import UserConsumer

websocket_urlpatterns = [
    path("ws/user/", UserConsumer.as_asgi()),
]
