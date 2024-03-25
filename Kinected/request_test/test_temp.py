import requests

temperature_data = {
    'value': 25.5  # Exemple de valeur de température
}

response = requests.post('http://127.0.0.1:8000/api/temp_data/', data=temperature_data)

print("Status Code:", response.status_code)
print("Content-Type:", response.headers['content-type'])
#print("Response Body:", response.text)
