import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class TemperatureConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        temperature_data = json.loads(text_data)
        temperature = temperature_data['temperature']

        # Faire quelque chose avec la température, par exemple l'enregistrer dans la base de données

        # Envoyer la température à tous les clients connectés
        self.send(text_data=json.dumps({
            'temperature': temperature
        }))