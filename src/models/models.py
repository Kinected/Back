import json
import os

from django.db import models
from dotenv import load_dotenv

load_dotenv()


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=30, blank=True)
    lastname = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.id} {self.firstname} {self.lastname}"






class UserFace(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    values = models.TextField(default='[]')

    def set_values(self, array):
        self.values = json.dumps(array)

    def get_values(self):
        return json.loads(self.values)

    def __str__(self):
        return f"Face Data for user_id {self.user.id}"

class Spotify_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, default=os.getenv('SPOTIFY_REFRESH_TOKEN'))

    def __str__(self):
        return f"Spotify Credentials for {self.user.firstname} {self.user.lastname}"


class Mauria_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, default=os.getenv('MAURIA_EMAIL'))
    password = models.CharField(max_length=128, default=os.getenv('MAURIA_MDP'))

    def __str__(self):
        return f"Mauria Credentials for {self.email}"


class Mauria_Plannings(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    planning = models.TextField(default='[]')

    def set_planning(self, array):
        if array != {}:
            self.planning = json.dumps(array)

    def get_planning(self):
        return json.loads(self.planning)

    def __str__(self):
        return f"Plannings for {self.user.id} {self.user.firstname} {self.user.lastname}"


class Ilevia_Bus(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    station = models.CharField(max_length=50, default="CORMONTAIGNE")
    line = models.CharField(max_length=50, default="L5")


class Ilevia_Vlille(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    station = models.CharField(max_length=4, default="28")
