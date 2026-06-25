from django.contrib import admin
from .models import Inventario


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):

    list_display = (
        'id_inventario',
        'nombre_articulo',
        'estado'
    )

    list_filter = (
        'estado',
    )

    search_fields = (
        'nombre_articulo',
        'descripcion'
    )

    ordering = (
        'nombre_articulo',
    )

    list_editable = (
        'estado',
    )