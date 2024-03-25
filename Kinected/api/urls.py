from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("temp_data/", views.receive_temperature, name='receive_temperature'),
]