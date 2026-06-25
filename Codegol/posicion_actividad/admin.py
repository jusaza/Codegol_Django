from django.contrib import admin
from .models import PosicionActividad


@admin.register(PosicionActividad)
class PosicionActividadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'posicion',
        'actividad',
        'obligatorio',
    )

    list_filter = (
        'obligatorio',
        'posicion',
        'actividad',
    )

    search_fields = (
        'posicion__nombre',
        'actividad__nombre',
    )

    ordering = (
        'posicion__nombre',
        'actividad__nombre',
    )

    list_editable = (
        'obligatorio',
    )

    autocomplete_fields = (
        'posicion',
        'actividad',
    )
