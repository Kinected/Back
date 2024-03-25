import requests

temperature_data = {'temperature': 25.5}  # Exemple de données de température
response = requests.post('http://127.0.0.1:8000/temperature_data/', json=temperature_data)

print(response.status_code)  # Vérifiez le code d'état de la réponse
