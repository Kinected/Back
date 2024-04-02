from django.urls import re_path
from .consumers import FaceConsumer

websocket_urlpatterns = [
    re_path(r'ws/faces$', FaceConsumer.as_asgi()),
]
