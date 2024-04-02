from ninja import NinjaAPI
import requests
import base64

from api.models import UserProfile, Spotify_Credentials

api = NinjaAPI()

@api.get("/hello")
def hello(request):
    # get first user from database
    user = UserProfile.objects.first()
    return user.firstname + " " + user.lastname + " " + str(user.id)


def get_access_token(refresh_token, client_id, client_secret):
    client_creds = f"{client_id}:{client_secret}"
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

@api.get("/spotify")
def spotify(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    spotify = Spotify_Credentials.objects.get(user=user)
    access_token = get_access_token(spotify.refresh_token, "e4073db5b2a64a4f9d807e9c6bb71c3b", "88204c90ac414b8da1408dd4eee69d1d")
    return access_token


