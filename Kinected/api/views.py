from django.http import HttpResponse
# views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Temperature
from .models import Humidity

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def receive_temperature(request):
    if request.method == 'POST':
        temperature_value = request.POST.get('value')
        temperature = Temperature.objects.create(value=temperature_value)
        return JsonResponse({'status': 'Temperature enregistrée avec succès'})
    elif request.method == 'GET':
        temperatures = Temperature.objects.all()
        data = [{'value': temp.value, 'recorded_at': temp.recorded_at} for temp in temperatures]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    


@csrf_exempt
def receive_humidity(request):
    if request.method == 'POST':
        humidity_value = request.POST.get('value')
        humidity = Humidity.objects.create(value=humidity_value)
        return JsonResponse({'status': 'Humidité enregistrée avec succès'})
    elif request.method == 'GET':
        humidities = Humidity.objects.all()
        data = [{'value': humid.value, 'recorded_at': humid.recorded_at} for humid in humidities]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

