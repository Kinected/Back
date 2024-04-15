import base64
import json
import os
from base64 import b64decode
from io import BytesIO
import face_recognition
import httpx
import numpy as np
import requests
import websockets
from PIL import Image
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from ninja import NinjaAPI, Schema
from openai import OpenAI
from fastapi import File, HTTPException
from fastapi.responses import FileResponse
import gzip
import shutil
from fastapi import APIRouter
router = APIRouter()

from .models import UserProfile, Mauria_Credentials, Spotify_Credentials, Face, Mauria_Plannings, Ilevia_Vlille, Ilevia_Bus, Ligne

api = NinjaAPI()
websocket = None
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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


@api.get("/spotify")
def spotify(request, userID: int):
    userID = int(userID)
    user: UserProfile = UserProfile.objects.get(id=userID)
    spotify = Spotify_Credentials.objects.get(user=user)
    access_token = get_spotify_access_token(spotify.refresh_token)
    return access_token


async def get_mauria_courses(username, password):
    endpoint = "https://mauriaapi.fly.dev/planning?start=2024-04-02"
    data = {
        "username": username,
        "password": password
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json'},
                              timeout=30.0)

        return r.json()


@api.get("/mauria/update")
async def update_mauria(request, userID: int):
    user = await sync_to_async(UserProfile.objects.get)(id=int(userID))
    mauria = await sync_to_async(Mauria_Credentials.objects.get)(user=user)
    planning = await get_mauria_courses(mauria.email, mauria.mdp)

    planning = [] if planning == {} else planning

    # Update the user's planning in the database
    user_planning, created = await sync_to_async(Mauria_Plannings.objects.get_or_create)(user=user)
    await sync_to_async(user_planning.set_planning)(planning)
    await sync_to_async(user_planning.save)()

    return planning


@api.get("/mauria")
async def get_mauria(request, userID: int):
    try:
        user = await sync_to_async(UserProfile.objects.get)(id=int(userID))
        user_planning = await sync_to_async(Mauria_Plannings.objects.get)(user=user)
        return user_planning.get_planning()
    except:
        return []


async def send_websocket_create_user(id, face):
    global websocket
    uri = "ws://localhost:8000/ws/new_user"
    payload = {
        "type": True,
        "userID": id,
        "face": face
    }
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(uri)
    await websocket.send(json.dumps(payload))


class ImageSchema(Schema):
    image: str


@api.post("/user")
async def post_user(request, img: ImageSchema):
    '''
    Create a new user using an image of his face
    '''
    image_data = b64decode(img.image.split(',')[1])
    image_pil = Image.open(BytesIO(image_data))
    image_np = np.array(image_pil)
    face_encoding = face_recognition.face_encodings(image_np)[0]

    user = await sync_to_async(UserProfile.objects.create)()
    user.firstname = "Utilisateur" + str(user.id)
    user.lastname = ""
    await sync_to_async(user.save)()

    face = await sync_to_async(Face.objects.create)(user=user)
    await sync_to_async(face.set_values)(face_encoding.tolist())
    await sync_to_async(face.save)()

    # A supprimer sur du long terme (refresh_token de sam car il est premium)
    first_user = await sync_to_async(UserProfile.objects.get)(id=1)

    first_user_spotify = await sync_to_async(Spotify_Credentials.objects.get)(user=first_user)
    user_spotify = await sync_to_async(Spotify_Credentials.objects.create)(user=user,
                                                                           refresh_token=first_user_spotify.refresh_token)
    await sync_to_async(user_spotify.save)()

    first_user_mauria = await sync_to_async(Mauria_Credentials.objects.get)(user=first_user)
    user_mauria = await sync_to_async(Mauria_Credentials.objects.create)(user=user, email=first_user_mauria.email,
                                                                         mdp=first_user_mauria.mdp)
    await sync_to_async(user_mauria.save)()
    ##########

    await send_websocket_create_user(user.id, face.get_values())

    return {"success": True}


@api.get("/user")
def get_user(request, userID: int):
    print(userID)
    user = UserProfile.objects.get(id=int(userID))
    gotSpotify = Spotify_Credentials.objects.filter(user=user).exists()
    gotMauria = Mauria_Credentials.objects.filter(user=user).exists()
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "gotSpotify": gotSpotify,
        "gotMauria": gotMauria
    }


@api.get("/users/faces")
def get_users_face(request):
    users = UserProfile.objects.all()
    data = [{"id": user.id, "face": Face.objects.get(user=user).get_values()} for user in users]
    return data


def get_trancription(audio_file):
    # Save the file to disk
    with open('audio.mp3', 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    # Now read the file
    with open('audio.mp3', 'rb') as f:
        audio_data = f.read()
        audio_file = open("audio.mp3", "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        return transcription.text


def get_response(question):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model="gpt-3.5-turbo",
    )

    response = chat_completion.choices[0].message.content

    return response

def get_audio_transcription(response):
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova", # other voices: 'echo', 'fable', 'onyx', 'nova', 'shimmer'
    input=response
)
    audio_transcription = response.stream_to_file('speech.mp3')
    
    return FileResponse('speech.mp3', media_type='audio/mpeg')

@api.post("/audio/transcription")
def audio(request):
    audio_file = request.FILES['audio']
    transcription = get_trancription(audio_file)
    return {"transcription": transcription}


@api.post("/audio/chatvoc")
def audio(request):
    audio_file = request.FILES['audio']
    question = get_trancription(audio_file)
    response = get_response(question)
    # audio_transcription = get_audio_transcription(response)
    print("traitement fichier audio")
    get_audio_transcription(response)
        
    return {"question": question, "response": response}

@api.get("/audio/transcription")
def audio_transcription(request):
    print("audio transcription")
    print("compression fichier audio")

    # Compresser le fichier
    with open('speech.mp3', 'rb') as f_in, gzip.open('speech.mp3.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    # Lire le fichier compressé et le convertir en Base64
    with open('speech.mp3.gz', 'rb') as f:
        data = f.read()
        base64_data = base64.b64encode(data).decode('utf-8')
    
    # return FileResponse('speech.mp3', media_type='audio/mpeg')
    return {"audio": base64_data}
    
    
class UpdateFirstnameSchema(Schema):
    userID: int
    firstname: str


@api.put("/user/firstname")
def put_firstname(request, payload: UpdateFirstnameSchema):
    user = UserProfile.objects.get(id=payload.userID)
    user.firstname = payload.firstname
    user.save()
    return {"success": True}


def get_borne_data(borne_id):
    url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/vlille-realtime/records?limit=20&refine=libelle%3A%22"+str(borne_id)+"%22"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        return None


@api.get("/ilevia/borne")
def get_borne_info(request, userID: int):
    user = UserProfile.objects.get(id = int(userID))
    ilevia = Ilevia_Vlille.objects.filter(user=user)
    ilevia_bornes_id = [borne.borne_id for borne in ilevia]

    print(ilevia_bornes_id)

    data = []
    for id in ilevia_bornes_id :
        borne_data = get_borne_data(id)
        print(borne_data)
        if borne_data:
            data.append({
                "id" : id,
                "name" : borne_data['results'][0]['nom'],
                "nbPlacesDispo": borne_data['results'][0]['nbplacesdispo'],
                "nbVelosDispo": borne_data['results'][0]['nbvelosdispo']
            })

    return data
    
    

def get_arret_data(station_name, line):
    url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/ilevia-prochainspassages/records?limit=20&refine=codeligne%3A%22"+str(line)+"%22&refine=nomstation%3A%22"+str(station_name)+"%22"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        return None

@api.get("/ilevia/arret")
def get_arret_info(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Bus.objects.filter(user=user)

    data = []
    for index in ilevia :
        arret_data = get_arret_data(index.arret_id, "L5")
        print(arret_data)
        if arret_data :
            data.append(arret_data)

    return data

@api.get("/ilevia/bornes")
def get_vlille_stations():
    url = '/api/explore/v2.1/catalog/datasets/vlille-realtime/records?limit=20'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        vlille_data = []
        for record in data['records']:
            fields = record['fields']
            station_name = fields.get('nom')
            station_id = fields.get('libelle')
            city = fields.get('commune')

            vlille_data.append({
                'station_name': station_name,
                'station_id': station_id,
                'city': city
            })
            
        return vlille_data
    else:
        print(response.status_code)
        return None


@api.get("/ilevia/stations")
def get_stations(request):
    try:
        with open('datasets/ilevia_stations.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            unique_station_names = set()  
            for station in data:
                unique_station_names.add(station['stop_name']) 

            station_names = list(unique_station_names)  

            return {"station_names": station_names},
        
    except FileNotFoundError:
        return {"error": "Le fichier des stations n'a pas été trouvé"},
    except Exception as e:
        return {"error": f"Une erreur s'est produite: {str(e)}"},

@api.get("/ilevia/bus_ligne")
def get_bus(request):
    try:
        with open('datasets/lignes_bus.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            unique_ligne_names = set()  
            for station in data:
                unique_ligne_names.add(station['ligne']) 

            unique_ligne_names.add("TRAM")
            ligne_names = list( unique_ligne_names)  

            return {"ligne_names": ligne_names},
        
    except FileNotFoundError:
        return {"error": "Le fichier des stations n'a pas été trouvé"},
    except Exception as e:
        return {"error": f"Une erreur s'est produite: {str(e)}"},

class CreateBus(Schema):
    station : str
    ligne : str
@api.post("/ilevia/bus")
def create_bus(request, item: CreateBus, userID):
    try:
        station = item.station
        ligne = item.ligne
        ligne_user = Ligne.objects.create(name=ligne, station=station, user_id=userID)
        return {"message": "Nouvelle ligne créée avec succès"}
    except FileNotFoundError:
        return {"error": "Le fichier des stations n'a pas été trouvé"}
    except Exception as e:
        return {"error": str(e)}



    

################################################################################################
##########################################Debug routes##########################################
################################################################################################

@api.get("/sendwebsockets")
async def send_websockets(request):
    '''
    send websockets to add antoine's face
    '''
    payload = {
        "userID": 1,
        "face": [-0.14382493495941162, 0.12402696162462234, 0.028164608404040337, -0.05453520640730858,
                 -0.10281238704919815, -0.027236519381403923, -0.017055578529834747, -0.1342238038778305,
                 0.17950372397899628, -0.17651887238025665, 0.20157113671302795, -0.023758722469210625,
                 -0.2124142050743103, 0.12319142371416092, -0.07277821004390717, 0.12483835220336914,
                 -0.15636517107486725, -0.11901789903640747, -0.07725968211889267, -0.11562544107437134,
                 0.012777861207723618, 0.11437080800533295, -0.04052203148603439, 0.10564544051885605,
                 -0.13924461603164673, -0.2388746291399002, -0.0982949435710907, -0.1137874498963356,
                 0.06870286166667938, -0.05627858266234398, 0.025579774752259254, 0.006506465841084719,
                 -0.08937405794858932, 0.04578724876046181, 0.04706959053874016, 0.06365662813186646,
                 -0.04433044046163559, -0.04842141270637512, 0.28238898515701294, -0.008851082995533943,
                 -0.15186023712158203, -0.0557732880115509, 0.08104865252971649, 0.3201756179332733,
                 0.08281391859054565, 0.07051801681518555, 0.0371842235326767, -0.11790759861469269,
                 0.16142313182353973, -0.18217387795448303, 0.09717210382223129, 0.11201084405183792,
                 0.1300341784954071, 0.11497584730386734, 0.01118047907948494, -0.22117528319358826,
                 0.08179108798503876, 0.1287299245595932, -0.18784353137016296, 0.1445068120956421, 0.17344942688941956,
                 -0.09555695205926895, -0.01811794564127922, 0.017101729288697243, 0.28711172938346863,
                 0.07462870329618454, -0.13285821676254272, -0.14379291236400604, 0.2117156684398651,
                 -0.21916867792606354, -0.09128544479608536, 0.09863462299108505, -0.10803689807653427,
                 -0.17185692489147186, -0.21897421777248383, 0.029105201363563538, 0.45529410243034363,
                 0.200552299618721, -0.09884856641292572, -0.02808101288974285, -0.019950293004512787,
                 -0.028993546962738037, 0.11726189404726028, 0.10089295357465744, -0.15149281919002533,
                 -0.1013832837343216, -0.10389295965433121, 0.045524995774030685, 0.29575419425964355,
                 0.042572226375341415, -0.060558561235666275, 0.20016324520111084, 0.06225011870265007,
                 0.015277216210961342, -0.027149535715579987, 0.05079396814107895, -0.1398947387933731,
                 -0.0028957079630345106, -0.02992800436913967, 0.03657587245106697, 0.03395119681954384,
                 -0.045189276337623596, 0.010016550309956074, 0.18271127343177795, -0.20823882520198822,
                 0.26679033041000366, -0.06313163042068481, -0.010738039389252663, -0.01579080894589424,
                 0.1093161553144455, -0.13038669526576996, -0.034184299409389496, 0.202422097325325,
                 -0.18999530375003815, 0.15802158415317535, 0.13866087794303894, 0.10268323123455048,
                 0.1403530389070511, 0.04336081072688103, 0.1007731705904007, 0.020267341285943985,
                 -0.004047813359647989, -0.28158220648765564, -0.10232589393854141, 0.06816042959690094,
                 -0.11282040923833847, 0.11894199252128601, 0.07058180123567581]
    }
    await send_websocket_create_user(payload["userID"], payload["face"])


@api.get("/ObamaFace")
def test(request):
    '''
    all users are updated with the face of Obama
    '''
    obama_image = face_recognition.load_image_file("images/obama.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0].tolist()

    users = UserProfile.objects.all()
    for user in users:
        face = Face.objects.get(user=user)
        face.set_values(obama_face_encoding)
        face.save()

    return {"success": True}
