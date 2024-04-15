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


@router.get("/borne")
def get_borne_info(request, userID: int):
    user = UserProfile.objects.get(id=int(userID))
    ilevia = Ilevia_Vlille.objects.filter(user=user)
    ilevia_bornes_id = [borne.borne_id for borne in ilevia]

    print(ilevia_bornes_id)

    data = []
    for id in ilevia_bornes_id:
        borne_data = get_borne_data(id)
        print(borne_data)
        if borne_data:
            data.append({
                "id": id,
                "name": borne_data['results'][0]['nom'],
                "nbPlacesDispo": borne_data['results'][0]['nbplacesdispo'],
                "nbVelosDispo": borne_data['results'][0]['nbvelosdispo']
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

    # get all the line of each arret knowing that ilevia contain multiple time the same arret with different line

    data = []
    for index in ilevia:
        bus_stops_and_lines[index.arret_id].add(index.line)

    for arret, lines in bus_stops_and_lines.items():
        arret_data = get_arret_data(arret, lines)
        if arret_data:
            data.append(arret_data)
        # else :
        #     data.append({
        #         "results" : [
        #             {
        #                 "codeLigne": index.line,
        #                 "nomStation": index.arret_id,
        #             }
        #         ]
        #     })
    print(bus_stops_and_lines)
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

