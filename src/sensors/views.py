from django.shortcuts import render

# chat/views.py
from django.shortcuts import render

def index(request):
    return render(request, "sensors.html")