"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
#add!
from channel.routing import ProtocolTypeRouter, URLRouter
#add!
from your_app.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Default:
# application = get_asgi_application()

#add!
application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": URLRouter(
		#websocket routing here!!!
		websocket_urlpatterns
	),
})
