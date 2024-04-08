from django.contrib import admin
from .models import UserProfile, Face, Spotify_Credentials, Mauria_Credentials, Mauria_Plannings, Ilevia_Credentials

admin.site.register(UserProfile)
admin.site.register(Face)
admin.site.register(Spotify_Credentials)
admin.site.register(Mauria_Credentials)
admin.site.register(Mauria_Plannings)
admin.site.register(Ilevia_Credentials)