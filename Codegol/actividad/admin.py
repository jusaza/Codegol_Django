from django.contrib import admin
from .models import Actividad


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):

    list_display = (
        'id_actividad',
        'nombre',
        'estado'
    )

    list_filter = (
        'estado',
    )

    search_fields = (
        'nombre',
        'descripcion'
    )

    ordering = (
        'nombre',
    )
