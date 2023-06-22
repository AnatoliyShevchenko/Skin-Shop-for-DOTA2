from django.apps import AppConfig


class SkinsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'skins'

    def ready(self) -> None:
        import skins.signals