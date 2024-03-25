from django.http import HttpResponse
# views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Temperature

@csrf_exempt
def receive_temperature(request):
    if request.method == 'POST':
        print("Yeet")
        temperature_value = request.POST.get('value')
        temperature = Temperature.objects.create(value=temperature_value)
        return JsonResponse({'status': 'Temperature enregistrée avec succès'})
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
