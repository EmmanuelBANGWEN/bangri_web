from django.apps import AppConfig


class SitewebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'siteweb'

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        import siteweb.signals  

