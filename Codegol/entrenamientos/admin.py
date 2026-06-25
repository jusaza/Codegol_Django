from django.contrib import admin
from .models import Entrenamiento


@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):

    list_display = (
        'id_entrenamiento',
        'descripcion',
        'lugar',
        'estado'
    )

    list_filter = (
        'estado',
        'lugar'
    )

    search_fields = (
        'descripcion',
        'lugar',
        'observaciones'
    )

    ordering = (
        'id_entrenamiento',
    )
