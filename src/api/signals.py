from django.db.models.signals import post_delete
from django.dispatch import receiver
from api.models import UserProfile, Face
import websockets
import json
from asgiref.sync import sync_to_async

websocket = None

@receiver(post_delete, sender=UserProfile)
async def post_delete_user(sender, instance, **kwargs):
    global websocket
    uri = "ws://localhost:8000/ws/new_user"
    print("User deleted")
    id = instance.id
    print(id)
    
    payload = {
        "type" : False,
        "userID": id,
        "face" : []
    }
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(uri)

    await websocket.send(json.dumps(payload))