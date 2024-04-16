import requests
from ninja import Router
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import base64
import gzip
import shutil
from models.models import UserProfile

router = Router(tags=["whisper"])

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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


def gpt_prompt(firstname, borneVlille, places_dispo, velo_dispo):

    prompt1 = f"Tu es un assistant vocal. Ton utilisateur s'appelle {firstname} et il a besoin de ton aide."
    prompt1 += f"SI ET SEULEMENT SI ton utilisateur te demande combien de places sont disponibles à sa station V'Lille {borneVlille}, tu dois lui répondre qu'il y a {places_dispo} places disponibles et {velo_dispo} vélos disponibles. L'utilisateur peut te poser n'importe quelle question, tu dois adapter ta réponse en fonction de la question."
    prompt2 = "Voici la question de ton utilisateur, tu y réponds obligatoirement :"

    prompt = f"{prompt1} {prompt2}"

    return prompt


def get_response(question, userID):
    user = UserProfile.objects.get(id=int(userID))

    borne_info = requests.get(f"http://localhost:8000/api/ilevia/borne?userID={userID}").json()

    if borne_info:
        borne_name = borne_info[0]['name']
        places_dispo = borne_info[0]['nbPlacesDispo']
        velo_dispo = borne_info[0]['nbVelosDispo']
        print(f"Le nombre de places dispo est : {velo_dispo}")
        prompt = gpt_prompt(user.firstname, borne_name, places_dispo, velo_dispo)
    else:
        print("Aucune information de borne disponible.")
        prompt = gpt_prompt(user.firstname)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt + " " + question,
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
    response.stream_to_file('speech.mp3')

    return FileResponse('speech.mp3', media_type='audio/mpeg')


@router.post("/audio/transcription")
def audio(request):
    audio_file = request.FILES['audio']
    transcription = get_trancription(audio_file)
    return {"transcription": transcription}


@router.post("/audio/chatvoc")
def audio(request, userID):
    audio_file = request.FILES['audio']
    question = get_trancription(audio_file)
    response = get_response(question, userID)
    print("traitement fichier audio")
    get_audio_transcription(response)
    return {"question": question, "response": response}


@router.get("/audio/transcription")
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



