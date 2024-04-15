from asgiref.sync import sync_to_async
from ninja import Router, Schema, File, UploadedFile
import face_recognition
from PIL import Image
import numpy as np
from base64 import b64decode
from io import BytesIO
import json
import websockets
from models.models import UserProfile, UserFace, Spotify_Credentials, Mauria_Credentials, Ilevia_Bus, Ilevia_Vlille


router = Router(tags=["user"])
websocket = None


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


@router.delete("/")
def delete_user(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    user.delete()
    return {"success": True}


class ImageSchema(Schema):
    image: str


@router.post("/")
async def post_user(request, img: ImageSchema):
    '''
    Create a new user using an image of his face
    '''
    image_data = b64decode(img.image.split(',')[1])
    image_pil = Image.open(BytesIO(image_data))
    image_np = np.array(image_pil)

    image_pil.save("images/original.jpg")

    face_locations = face_recognition.face_locations(image_np)
    if face_locations and len(face_locations[0]) == 4:
        top, right, bottom, left = face_locations[0]

        top = min(image_np.shape[0], round(top - 25))
        right = min(image_np.shape[1], right + 25)
        bottom = min(image_np.shape[0], bottom + 25)
        left = min(image_np.shape[1], round(left - 25))

        print(top, right, bottom, left)
        image_np = image_np[top:bottom, left:right]
        image_pil = Image.fromarray(image_np)
        image_pil.save("images/face.jpg")
        image_np = np.array(image_pil)

    face_encodings = face_recognition.face_encodings(image_np)
    print(face_encodings)
    face_encoding = face_encodings[0]

    user = await sync_to_async(UserProfile.objects.create)()
    user.firstname = "Utilisateur "+ str(user.id)
    await sync_to_async(user.save)()

    image_pil.save(f"images/{user.id}.jpg")

    face = await sync_to_async(UserFace.objects.create)(user=user)
    await sync_to_async(face.set_values)(face_encoding.tolist())
    await sync_to_async(face.save)()

    user_spotify = await sync_to_async(Spotify_Credentials.objects.create)(user=user)
    await sync_to_async(user_spotify.save)()

    user_mauria = await sync_to_async(Mauria_Credentials.objects.create)(user=user)
    await sync_to_async(user_mauria.save)()

    user_ilevia_bus = await sync_to_async(Ilevia_Bus.objects.create)(user=user)
    await sync_to_async(user_ilevia_bus.save)()

    user_ilevia_vlille = await sync_to_async(Ilevia_Vlille.objects.create)(user=user)
    await sync_to_async(user_ilevia_vlille.save)()

    await send_websocket_create_user(user.id, face.get_values())

    return {"success": True}


@router.get("/debug")
def get_user_debug(request):

    user = UserProfile.objects.get_or_create(firstname="Debug")[0]
    user.save()

    spotify = Spotify_Credentials.objects.get_or_create(user=user)[0]
    spotify.save()

    mauria = Mauria_Credentials.objects.get_or_create(user=user)[0]
    mauria.save()

    ilevia_bus = Ilevia_Bus.objects.get_or_create(user=user)[0]
    ilevia_bus.save()

    ilevia_vlille = Ilevia_Vlille.objects.get_or_create(user=user)[0]
    ilevia_vlille.save()

    face = UserFace.objects.get_or_create(user=user)[0]
    img = face_recognition.load_image_file("images/obama.jpg")
    face.set_values(face_recognition.face_encodings(img)[0].tolist())
    face.save()

    return {"userID" : user.id}



@router.get("/")
def get_user(request, userID: int):
    print(userID)
    user = UserProfile.objects.get(id=int(userID))
    gotSpotify = Spotify_Credentials.objects.filter(user=user).exists()
    gotMauria = Mauria_Credentials.objects.filter(user=user).exists()
    gotIleviaBus = Ilevia_Bus.objects.filter(user=user).exists()
    gotIleviaVlille = Ilevia_Vlille.objects.filter(user=user).exists()
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "gotSpotify": gotSpotify,
        "gotMauria": gotMauria,
        "gotIleviaBus": gotIleviaBus,
        "gotIleviaVlille": gotIleviaVlille
    }


@router.get("/all")
def get_users(request):
    users = UserProfile.objects.all()
    data = [{"id": user.id, "firstname": user.firstname, "lastname": user.lastname} for user in users]
    return data


@router.get("/face/all")
def get_users_face(request):
    users = UserProfile.objects.all()
    data = [{"id": user.id, "face": UserFace.objects.get(user=user).get_values()} for user in users]
    return data


class UpdateUserSchema(Schema):
    firstname: str
    lastname: str


@router.put("/")
def put_user(request, userID: int, payload: UpdateUserSchema):
    user = UserProfile.objects.get(id=int(userID))
    user.firstname = payload.firstname
    user.lastname = payload.lastname
    user.save()
    return {"success": True}


class UpdateFirstnameSchema(Schema):
    userID: int
    firstname: str


@router.put("/firstname")
def put_firstname(request, payload: UpdateFirstnameSchema):
    print(payload.userID, payload.firstname)
    user = UserProfile.objects.get(id=payload.userID)
    user.firstname = payload.firstname
    user.save()
    return {"success": True}


@router.get("/ObamaFace")
def test(request):
    '''
    all users are updated with the face of Obama
    '''
    obama_image = face_recognition.load_image_file("images/obama.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0].tolist()

    users = UserProfile.objects.all()
    for user in users:
        face = UserFace.objects.get(user=user)
        face.set_values(obama_face_encoding)
        face.save()

    return {"success": True}

