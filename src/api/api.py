from ninja import NinjaAPI
import requests
import base64
import os
from dotenv import load_dotenv

from api.models import UserProfile, Spotify_Credentials

api = NinjaAPI()

load_dotenv()

def get_access_token(refresh_token):
    client_creds = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
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


