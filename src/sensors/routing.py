from django.urls import re_path
from .consumers import SensorsConsumer

websocket_urlpatterns = [
    re_path(r'ws/sensors$', SensorsConsumer.as_asgi()),
]