from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field='django.db.models.BigAutoField'
    name = 'payment_app'
    def ready(self):
        import payment_app.signals

