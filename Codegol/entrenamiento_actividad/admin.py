from django.contrib import admin
from .models import EntrenamientoActividad


@admin.register(EntrenamientoActividad)
class EntrenamientoActividadAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'entrenamiento',
        'actividad',
        'orden',
        'duracion_min'
    )

    list_filter = (
        'entrenamiento',
        'actividad'
    )

    search_fields = (
        'entrenamiento__descripcion',
        'actividad__nombre'
    )

    ordering = (
        'entrenamiento',
        'orden'
    )

    autocomplete_fields = (
        'entrenamiento',
        'actividad'
    )
