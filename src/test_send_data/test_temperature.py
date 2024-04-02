import asyncio
import websockets
import json

async def send_temperature():
    uri = "ws://localhost:8000/ws/sensors"  # Remplacez par l'URL WebSocket appropriée
    async with websockets.connect(uri) as websocket:
        while True:
            # Simuler la génération de températures aléatoires (vous pouvez remplacer cela par votre propre logique)
            temperature = generate_random_temperature()

            # Créer un dictionnaire contenant la température
            temperature_data = {
                'temperature': temperature
            }

            # Convertir le dictionnaire en chaîne JSON
            temperature_json = json.dumps(temperature_data)

            # Envoyer la température via WebSocket
            await websocket.send(temperature_json)

            await asyncio.sleep(2)  # Attendre 5 secondes avant d'envoyer la prochaine température

def generate_random_temperature():
    # Simuler la génération de températures aléatoires entre 0 et 100 degrés Celsius
    import random
    return round(random.uniform(0, 100), 2)

asyncio.get_event_loop().run_until_complete(send_temperature())
