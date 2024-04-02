from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class Face(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    test = models.CharField(max_length=1024, blank=True)

    # # Neutral Face
    # neutral = models.FloatField()

    # # Brow Movements
    # browDownLeft = models.FloatField()
    # browDownRight = models.FloatField()
    # browInnerUp = models.FloatField()
    # browOuterUpLeft = models.FloatField()
    # browOuterUpRight = models.FloatField()

    # # Cheek Movements
    # cheekPuff = models.FloatField()
    # cheekSquintLeft = models.FloatField()
    # cheekSquintRight = models.FloatField()

    # # Eye Movements
    # eyeBlinkLeft = models.FloatField()
    # eyeBlinkRight = models.FloatField()
    # eyeLookDownLeft = models.FloatField()
    # eyeLookDownRight = models.FloatField()
    # eyeLookInLeft = models.FloatField()
    # eyeLookInRight = models.FloatField()
    # eyeLookOutLeft = models.FloatField()
    # eyeLookOutRight = models.FloatField()
    # eyeLookUpLeft = models.FloatField()
    # eyeLookUpRight = models.FloatField()
    # eyeSquintLeft = models.FloatField()
    # eyeSquintRight = models.FloatField()
    # eyeWideLeft = models.FloatField()
    # eyeWideRight = models.FloatField()

    # # Jaw Movements
    # jawForward = models.FloatField()
    # jawLeft = models.FloatField()
    # jawOpen = models.FloatField()
    # jawRight = models.FloatField()

    # # Mouth Movements
    # mouthClose = models.FloatField()
    # mouthDimpleLeft = models.FloatField()
    # mouthDimpleRight = models.FloatField()
    # mouthFrownLeft = models.FloatField()
    # mouthFrownRight = models.FloatField()
    # mouthFunnel = models.FloatField()
    # mouthLeft = models.FloatField()
    # mouthLowerDownLeft = models.FloatField()
    # mouthLowerDownRight = models.FloatField()
    # mouthPressLeft = models.FloatField()
    # mouthPressRight = models.FloatField()
    # mouthPucker = models.FloatField()
    # mouthRight = models.FloatField()
    # mouthRollLower = models.FloatField()
    # mouthRollUpper = models.FloatField()
    # mouthShrugLower = models.FloatField()
    # mouthShrugUpper = models.FloatField()
    # mouthSmileLeft = models.FloatField()
    # mouthSmileRight = models.FloatField()
    # mouthStretchLeft = models.FloatField()
    # mouthStretchRight = models.FloatField()
    # mouthUpperUpLeft = models.FloatField()
    # mouthUpperUpRight = models.FloatField()

    # # Nose Movements
    # noseSneerLeft = models.FloatField()
    # noseSneerRight = models.FloatField()

    def __str__(self):
        return f"Face Data for user_id {self.user.id}"


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=30, blank=True)
    lastname = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Spotify_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, unique=True)  

    def __str__(self):
        return f"Spotify Credentials for {self.user.firstname} {self.user.lastname}"


class Mauria_Credentials(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, unique=True)
    mdp = models.CharField(max_length=128)
    
    def __str__(self):
        return f"Mauria Credentials for {self.email}"
