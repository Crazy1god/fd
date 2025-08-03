from django.apps import AppConfig

def ready(self):
    import yourapp.signals


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
