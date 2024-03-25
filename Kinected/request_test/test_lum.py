import requests

luminosity_data = {
    'value': 80.0  # Exemple de valeur de luminosité
}

response = requests.post('http://127.0.0.1:8000/api/lum_data/', data=luminosity_data)

try:
    response_data = response.json()
    print(response_data)
except ValueError as e:
    print("Erreur lors de la lecture de la réponse JSON :", e)
