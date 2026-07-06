from django.apps import AppConfig


class PagoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pago'

    def ready(self):
        from django.db.models.signals import post_migrate

        def inicializar_conceptos(sender, **kwargs):
            if sender.name != 'pago':
                return
            from .models import ConceptoPago
            ConceptoPago.inicializar_conceptos()

        post_migrate.connect(inicializar_conceptos, sender=self)
