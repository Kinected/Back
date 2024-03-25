import requests

humidity_data = {
    'value': 60.5  # Exemple de valeur d'humidité
}

response = requests.post('http://127.0.0.1:8000/api/humi_data/', data=humidity_data)

try:
    response_data = response.json()
    print(response_data)
except ValueError as e:
    print("Erreur lors de la lecture de la réponse JSON :", e)
