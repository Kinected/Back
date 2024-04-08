import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import SensorsData

class SensorsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        # Add this connection to the group
        async_to_sync(self.channel_layer.group_add)("sensors", self.channel_name)

    def disconnect(self, close_code):
        # Remove this connection from the group
        async_to_sync(self.channel_layer.group_discard)("sensors", self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Send a message to all connections in the group
        async_to_sync(self.channel_layer.group_send)(
            "sensors",
            {
                "type": "Sensors_message",
                "text": json.dumps(text_data_json)
            })
        print(text_data_json)
        temperature = text_data_json.get('temperature')
        humidity = text_data_json.get('humidity')
        luminosity = text_data_json.get('luminosity')
        data = SensorsData(temperature=temperature, humidity=humidity, luminosity=luminosity)
        data.save()

    
    # This method will receive messages from the group
    def Sensors_message(self, event):
        self.send(text_data=event["text"])
