"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from user_service.routing import websocket_urlpatterns
from user.consumers import UserConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')

application = ProtocolTypeRouter({
	'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter(
				websocket_urlpatterns
			)
		)
    ),
})
