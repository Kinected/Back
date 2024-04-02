from ninja import NinjaAPI, Schema
import requests
import base64
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
import httpx
import json
from base64 import b64decode
import face_recognition


from api.models import UserProfile, Spotify_Credentials, Mauria_Credentials, Face

api = NinjaAPI()

load_dotenv()

def get_access_token(refresh_token):
    client_creds = f"{os.getenv("CLIENT_ID")}:{os.getenv("CLIENT_SECRET")}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    
    endpoint = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    r = requests.post(endpoint, data=data, headers=headers)
    return r.json().get('access_token')

@api.get("/hello")
def hello(request):
    # get first user from database
    user = UserProfile.objects.first()
    return user.firstname + " " + user.lastname + " " + str(user.id)


@api.get("/user")
def user(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,    
    }



@api.get("/spotify")
def spotify(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    spotify = Spotify_Credentials.objects.get(user=user)
    access_token = get_access_token(spotify.refresh_token)
    return access_token



async def get_mauria_courses(username, password):
    # Define the endpoint
    endpoint = "https://mauriaapi.fly.dev/planning?start=2024-04-02"
    
    # Define the data
    data = {
        "username": username,
        "password": password
    }
    
    # Make the post request
    async with httpx.AsyncClient() as client:
        r = await client.post(endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json'},  timeout=30.0)
    
    return r.json()


@api.get("/mauria")
async def mauria(request, userID: int):
    userID = int(userID)
    user = await sync_to_async(UserProfile.objects.get)(id=userID)
    mauria = await sync_to_async(Mauria_Credentials.objects.get)(user=user)
    print(mauria.email, mauria.mdp)
    return await get_mauria_courses(mauria.email, mauria.mdp)


class ImageSchema(Schema):
    image: str

@api.post("/user")
def upload(request, img: ImageSchema):
    
        image_data = b64decode(img.image.split(',')[1])
        if not os.path.exists('images'):
            os.makedirs('images')

        with open('images/image.png', 'wb') as f:
            f.write(image_data)
            f.close()

        image = face_recognition.load_image_file("images/image.png")
        face_locations = face_recognition.face_locations(image)[0]
        print(face_locations)

        user = UserProfile.objects.create()
        user.save()

        face = Face.objects.create(user=user)
        face.test = str(face_locations)
        face.save()

        return {"success": True}
    
    # except Exception as e:
    #     print(e)
    #     return {"success": False}


@api.get("/user")
def get_user(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,    
    }

