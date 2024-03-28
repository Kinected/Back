from django.urls import re_path
from .consumers import SwipeConsumer

websocket_urlpatterns = [
    re_path(r'ws/swipes$', SwipeConsumer.as_asgi()),
]
