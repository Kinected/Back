from django.urls import re_path
from .consumers import TemperatureConsumer

websocket_urlpatterns = [
    re_path(r'ws/sensors$', TemperatureConsumer.as_asgi()),
]