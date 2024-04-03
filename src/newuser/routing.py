from django.urls import re_path
from .consumers import NewUserConsumer

websocket_urlpatterns = [
    re_path(r'ws/new_user$', NewUserConsumer.as_asgi()),
]