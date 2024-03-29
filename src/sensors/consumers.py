import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

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

    # This method will receive messages from the group
    def Sensors_message(self, event):
        self.send(text_data=event["text"])
