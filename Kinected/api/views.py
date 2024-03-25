from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TemperatureData
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def temperature_data(request):
    return HttpResponse("temp_1065")