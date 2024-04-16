from ninja import Router, Schema, File, UploadedFile
import requests
from models.models import UserProfile, Ilevia_Vlille, Ilevia_Bus
from collections import defaultdict

router = Router(tags=["ilevia"])


def get_borne_data(borne_id):
    url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/vlille-realtime/records?limit=20&refine=libelle%3A%22" + str(
        borne_id) + "%22"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        return None


@router.get("/bus/user")
def get_user_bus_stations(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Bus.objects.filter(user=user)
    data = [{
        "station" : station.station,
        "line": station.line
    } for station in ilevia]
    return data


class Bus (Schema):
    station: str
    line: str


@router.delete("/bus")
def delete_user_bus_station(request, userID: int,payload: Bus):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Bus.objects.get(user=user, station=payload.station, line=payload.line)
    ilevia.delete()
    return {"success": True}



@router.post("/bus")
def create_bus(request, item: Bus, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    try:
        station = item.station
        line = item.line
        try :
            existing = Ilevia_Bus.objects.get(user=user, station=station, line=line)
        except :
            existing = None

        if existing == None:
            print(station, line)
            bus = Ilevia_Bus.objects.create(user=user, line=line, station=station)
            bus.save()
            return {"message": "Nouvelle ligne de bus créée avec succès"}
    except Exception as e:
        print(e)
        return {"error": str(e)}


@router.get("/borne")
def get_borne_info(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Vlille.objects.filter(user=user)
    ilevia_station_id = [station.station for station in ilevia]

    print(ilevia_station_id)

    data = []
    for id in ilevia_station_id:
        station_data = get_borne_data(id)
        print(station_data)
        if station_data:
            data.append({
                "id": id,
                "name": station_data['results'][0]['nom'],
                "nbPlacesDispo": station_data['results'][0]['nbplacesdispo'],
                "nbVelosDispo": station_data['results'][0]['nbvelosdispo']
            })

    return data



def get_arret_data(station_name, lines):
    url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/ilevia-prochainspassages/records?limit=20&refine=nomstation%3A%22" + str(
        station_name) + "%22"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        # filter data with line
        data = [record for record in data['results'] if record['codeligne'] in lines]
        organized_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        # Parcourir les données et ajouter chaque dictionnaire à la liste correspondante
        for item in data:
            organized_data[item['nomstation']][item['codeligne']][item['sensligne']].append(item)

        return organized_data
    else:
        print(response.status_code)
        return None

@router.get("/arret")
def get_arret_info(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Bus.objects.filter(user=user)

    bus_stops_and_lines = defaultdict(set)

    data = []
    for index in ilevia:
        bus_stops_and_lines[index.station].add(index.line)
    for station, lines in bus_stops_and_lines.items():
        station_data = get_arret_data(station, lines)
        if station_data:
            data.append(station_data)
    return data




@router.get("/bornes")
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




    #################
#
#     @api.get("/ilevia/stations")
#     def get_stations(request):
#         try:
#             with open('datasets/ilevia_stations.json', 'r', encoding='utf-8') as file:
#                 data = json.load(file)
#                 unique_station_names = set()
#                 for station in data:
#                     unique_station_names.add(station['stop_name'])
#
#                 station_names = list(unique_station_names)
#
#                 return {"station_names": station_names},
#
#         except FileNotFoundError:
#             return {"error": "Le fichier des stations n'a pas été trouvé"},
#         except Exception as e:
#             return {"error": f"Une erreur s'est produite: {str(e)}"},
#
#     @api.get("/ilevia/bus_ligne")
#     def get_bus(request):
#         try:
#             with open('datasets/lignes_bus.json', 'r', encoding='utf-8') as file:
#                 data = json.load(file)
#                 unique_ligne_names = set()
#                 for station in data:
#                     unique_ligne_names.add(station['ligne'])
#
#                 unique_ligne_names.add("TRAM")
#                 ligne_names = list(unique_ligne_names)
#
#                 return {"ligne_names": ligne_names},
#
#         except FileNotFoundError:
#             return {"error": "Le fichier des stations n'a pas été trouvé"},
#         except Exception as e:
#             return {"error": f"Une erreur s'est produite: {str(e)}"},
#
#     class CreateBus(Schema):
#         station: str
#         line: str
#
#     @api.post("/api/ilevia/bus")
#     def create_bus(request, item: CreateBus, userID: int):
#         user = UserProfile.objects.get(id=int(userID))
#         try:
#             station = item.station
#             line = item.line
#
#             bus = Ilevia_Bus.objects.create(user=user, line=line, arret_id=station)
#             bus.save()
#
#             return {"message": "Nouvelle ligne de bus créée avec succès"}
#         except Exception as e:
#             return {"error": str(e)}
#
#     class CreateVelo(Schema):
#         libelle: str
#
#     @api.post("/ilevia/velo")
#     def create_station_velo(request, item: CreateVelo, userID: int):
#         user = UserProfile.objects.get(id=int(userID))
#         try:
#             libelle = item.libelle
#
#             station_velo = Ilevia_Vlille.objects.create(user=user, borne_id=libelle)
#             station_velo.save()
#
#             return {"message": "Nouvelle station de vélo créée avec succès"}
#         except Exception as e:
#             return {"error": str(e)}
#
#
# ###########################
#
#
# def get_borne_data(borne_id):
#     url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/vlille-realtime/records?limit=20&refine=libelle%3A%22" + str(
#         borne_id) + "%22"
#
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(response.status_code)
#         return None
#
#
# @api.get("/ilevia/borne")
# def get_borne_info(request, userID: int):
#     user = UserProfile.objects.get(id=int(userID))
#     ilevia = Ilevia_Vlille.objects.filter(user=user)
#     ilevia_bornes_id = [borne.borne_id for borne in ilevia]
#
#     print(ilevia_bornes_id)
#
#     data = []
#     for id in ilevia_bornes_id:
#         borne_data = get_borne_data(id)
#         print(borne_data)
#         if borne_data:
#             data.append({
#                 "id": id,
#                 "name": borne_data['results'][0]['nom'],
#                 "nbPlacesDispo": borne_data['results'][0]['nbplacesdispo'],
#                 "nbVelosDispo": borne_data['results'][0]['nbvelosdispo']
#             })
#
#     return data
#
#
# def get_arret_data(station_name, lines):
#     url = f"https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/ilevia-prochainspassages/records?limit=20&refine=nomstation%3A%22" + str(
#         station_name) + "%22"
#
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#
#         # filter data with line
#         data = [record for record in data['results'] if record['codeligne'] in lines]
#         organized_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
#
#         # Parcourir les données et ajouter chaque dictionnaire à la liste correspondante
#         for item in data:
#             organized_data[item['nomstation']][item['codeligne']][item['sensligne']].append(item)
#
#         return organized_data
#     else:
#         print(response.status_code)
#         return None
#
#

