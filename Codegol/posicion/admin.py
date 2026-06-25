from django.contrib import admin
from .models import Posicion


@admin.register(Posicion)
class PosicionAdmin(admin.ModelAdmin):
    list_display = (
        'id_posicion',
        'nombre',
    )

    search_fields = (
        'nombre',
    )

    ordering = (
        'nombre',
    )
