from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import json

class Face(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    values = models.TextField(default='[]')

    def set_values(self, array):
        self.values = json.dumps(array)

    def get_values(self):
        return json.loads(self.values)

    def __str__(self):
        return f"Face Data for user_id {self.user.id}"


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=30, blank=True)
    lastname = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.id} {self.firstname} {self.lastname}"
    


class Spotify_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255)  

    def __str__(self):
        return f"Spotify Credentials for {self.user.firstname} {self.user.lastname}"


class Mauria_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, unique=True)
    mdp = models.CharField(max_length=128)
    
    def __str__(self):
        return f"Mauria Credentials for {self.email}"


class Mauria_Plannings(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    planning = models.TextField(default='[]')

    def set_planning(self, array):
        self.planning = json.dumps(array)

    def get_planning(self):
        return json.loads(self.planning)

    def __str__(self):
        return f"Plannings for {self.user.id} {self.user.firstname} {self.user.lastname}"


class Ilevia_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    borne_id = models.CharField(max_length=4)