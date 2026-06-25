from django.contrib import admin
from .models import SesionCategoria


@admin.register(SesionCategoria)
class SesionCategoriaAdmin(admin.ModelAdmin):
    list_display = (
        'id_sesion_categoria',
        'id_sesion',
        'id_categoria',
        'estado',
    )

    list_filter = (
        'estado',
        'id_categoria',
    )

    search_fields = (
        'id_categoria__nombre_categoria',
        'id_sesion__id_sesion',
    )

    ordering = (
        '-id_sesion_categoria',
    )

    list_editable = (
        'estado',
    )

    autocomplete_fields = (
        'id_sesion',
        'id_categoria',
    )
