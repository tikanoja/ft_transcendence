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
from pong.consumers import PongConsumer
# add this if need AuthMiddlewareStack
# from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Default:
# application = get_asgi_application()

# Maybe create routing.py for these if list starts to grow...
websocket_urlpatterns = [
    path('ws/pong/', PongConsumer.as_asgi()),
    # Add paths for other WS consumers if needed
]

application = ProtocolTypeRouter({
	#Wrap URLRouter inside AuthMiddlewareStack() if needed!
	# "http": get_asgi_application(),
	"websocket": URLRouter(
		websocket_urlpatterns
	),
})
