from django.contrib import admin
from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):

    list_display = (
        'id_categoria',
        'nombre_categoria',
        'estado'
    )

    list_filter = (
        'estado',
    )

    search_fields = (
        'nombre_categoria',
    )

    ordering = (
        'nombre_categoria',
    )
