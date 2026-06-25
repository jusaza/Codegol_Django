from django.contrib import admin
from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'concepto_pago',
        'id_matricula',
        'fecha_pago',
        'metodo_pago',
        'valor_total',
        'cancelado',
    )

    list_filter = (
        'cancelado',
        'metodo_pago',
        'fecha_pago',
    )

    search_fields = (
        'concepto_pago',
        'id_matricula__id_jugador__nombre_completo',
        'id_matricula__id_jugador__num_identificacion',
        'observaciones',
    )

    ordering = (
        '-fecha_pago',
    )

    list_editable = (
        'cancelado',
    )

    autocomplete_fields = (
        'id_matricula',
    )
