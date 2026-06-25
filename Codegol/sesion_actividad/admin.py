from django.contrib import admin
from .models import SesionActividad


@admin.register(SesionActividad)
class SesionActividadAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sesion',
        'actividad',
        'orden',
        'duracion_min',
    )

    list_filter = (
        'actividad',
        'sesion',
    )

    search_fields = (
        'actividad__nombre',
        'sesion__id_sesion',
    )

    ordering = (
        'sesion',
        'orden',
    )

    autocomplete_fields = (
        'sesion',
        'actividad',
    )

    list_per_page = 25
