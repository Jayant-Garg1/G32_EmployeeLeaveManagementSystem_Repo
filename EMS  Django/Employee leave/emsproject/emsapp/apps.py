from django.apps import AppConfig


class EmsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emsapp'

class EmsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emsapp'

    def ready(self):
        import emsapp.signals
