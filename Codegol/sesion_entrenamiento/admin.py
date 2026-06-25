from django.contrib import admin
from .models import SesionEntrenamiento


@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = (
        'id_sesion',
        'id_entrenamiento',
        'id_entrenador',
        'fecha',
        'hora_inicio',
        'hora_fin',
        'estado',
    )

    list_filter = (
        'estado',
        'fecha',
        'id_entrenador',
        'id_entrenamiento',
    )

    search_fields = (
        'id_entrenador__nombre_completo',
        'id_entrenador__num_identificacion',
        'id_entrenamiento__lugar',
    )

    ordering = (
        '-fecha',
        '-hora_inicio',
    )

    list_editable = (
        'estado',
    )

    readonly_fields = (
        'id_sesion',
    )

    autocomplete_fields = (
        'id_entrenamiento',
        'id_entrenador',
    )

    date_hierarchy = 'fecha'

    list_per_page = 25