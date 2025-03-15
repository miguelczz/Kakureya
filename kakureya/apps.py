from django.apps import AppConfig


class KakureyaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kakureya'

    def ready(self):
        import kakureya.signals