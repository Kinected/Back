import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class NewUserConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        # Add this connection to the group
        async_to_sync(self.channel_layer.group_add)("new_user", self.channel_name)

    def disconnect(self, close_code):
        # Remove this connection from the group
        async_to_sync(self.channel_layer.group_discard)("new_user", self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # print(text_data_json)
        # Send a message to all connections in the group
        async_to_sync(self.channel_layer.group_send)(
            "new_user",
            {
                "type": "new_user_message",
                "text": json.dumps(text_data_json)
            })

    # This method will receive messages from the group
    def new_user_message(self, event):
        print("send")
        self.send(text_data=event["text"])
