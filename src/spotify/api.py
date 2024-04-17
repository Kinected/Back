from ninja import Router, Schema, File, UploadedFile
from models.models import UserProfile, Spotify_Credentials
import os
import requests
import base64

router = Router(tags=["spotify"])


def get_spotify_access_token(refresh_token):
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


@router.get("/")
def spotify(request, userID: int):
    userID = int(userID)
    user: UserProfile = UserProfile.objects.get(id=userID)
    spotify = Spotify_Credentials.objects.get(user=user)
    access_token = get_spotify_access_token(spotify.refresh_token)
    return access_token


@router.delete("/")
def delete_spotify(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    spotify = Spotify_Credentials.objects.get(user=user)
    spotify.delete()
    return {"success": True}





def get_spotify_refresh_token(code):
    client_creds = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    endpoint = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}"
    }
    data = {
        "redirect_uri": "http://172.20.10.6:3001/user",
        "grant_type": "authorization_code",""
        "code": code,
    }
    r = requests.post(endpoint, data=data, headers=headers)
    print(r.json())
    return r.json().get('refresh_token')



class SpotifySchema(Schema):
    code: str


@router.post("/")
def post_spotify(request, userID: int, payload: SpotifySchema):
    user = UserProfile.objects.get(id=userID)
    refresh_token = get_spotify_refresh_token(payload.code)
    print(refresh_token)
    spotify = Spotify_Credentials.objects.create(user=user, refresh_token=refresh_token)
    spotify.save()
    return {"success": True}

