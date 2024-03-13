"""
ASGI config for chat_service project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.urls import path
#from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack

from chat.consumers import ClientConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_service.settings')

application = ProtocolTypeRouter({
#    "http" : get_asgi_application(),
    "websocket" : AllowedHostsOriginValidator(
        SessionMiddlewareStack(
            URLRouter( [path("ws/chat/", ClientConsumer.as_asgi())] )
        )
    )
})
