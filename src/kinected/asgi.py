"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from swipes.routing import websocket_urlpatterns as swipes_patterns
from faces.routing import websocket_urlpatterns as faces_patterns
from sensors.routing import websocket_urlpatterns as sensors_patterns
from newuser.routing import websocket_urlpatterns as newuser_patterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinected.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(swipes_patterns + faces_patterns + sensors_patterns + newuser_patterns)
        ),
    }
)