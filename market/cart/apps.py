from django.apps import AppConfig


class CartConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals  # noqa F401
