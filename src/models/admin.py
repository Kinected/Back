from django.contrib import admin
from django.apps import apps

models = apps.get_app_config('models').get_models()

for model in models:
    try:
        admin.site.register(model)
    except Exception:
        """ debug
        print("Erreur pas de rendu pour le model model:", model)
        print(Exception)
        """
        pass


# admin.site.register(UserProfile)
# admin.site.register(UserFace)
# admin.site.register(Spotify_Credentials)
# admin.site.register(Mauria_Credentials)
# admin.site.register(Mauria_Plannings)
# admin.site.register(Ilevia_Bus)
# admin.site.register(Ilevia_Vlille)
# # Register your models here.
