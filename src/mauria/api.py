from asgiref.sync import sync_to_async
from ninja import Router, Schema
from models.models import UserProfile, Mauria_Credentials, Mauria_Plannings
import httpx
import json

router = Router(tags=["mauria"])

@router.delete("/")
def delete_mauria(request, userID: int):
    userID = int(userID)
    user = UserProfile.objects.get(id=userID)
    mauria = Mauria_Credentials.objects.get(user=user)
    mauria.delete()
    return {"success": True}


class MauriaSchema(Schema):
    email: str
    password: str


@router.post("/")
def post_mauria(request, userID, payload: MauriaSchema):
    user = UserProfile.objects.get(id=userID)
    print(payload.email, payload.password)
    mauria = Mauria_Credentials.objects.create(user=user, email=payload.email, password=payload.password)
    return {"success": True}


@router.get("/credentials")
def get_mauria_credentials(request, userID: int):
    user = UserProfile.objects.get(id=userID)
    try :
        mauria = Mauria_Credentials.objects.get(user=user)
        password = mauria.password
        password = password[0] + password[1] + "*" * (len(password)-2)
        return {"email": mauria.email, "password": password}
    except:
        return None



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


@router.get("/update")
async def update_mauria(request, userID: int):
    user = await sync_to_async(UserProfile.objects.get)(id=int(userID))
    mauria = await sync_to_async(Mauria_Credentials.objects.get)(user=user)
    planning = await get_mauria_courses(mauria.email, mauria.password)

    planning = [] if planning == {} else planning

    # Update the user's planning in the database
    user_planning, created = await sync_to_async(Mauria_Plannings.objects.get_or_create)(user=user)
    await sync_to_async(user_planning.set_planning)(planning)
    await sync_to_async(user_planning.save)()

    return planning


@router.get("/")
async def get_mauria(request, userID: int):
    try:
        user = await sync_to_async(UserProfile.objects.get)(id=int(userID))
        user_planning = await sync_to_async(Mauria_Plannings.objects.get)(user=user)
        return user_planning.get_planning()
    except:
        return []
