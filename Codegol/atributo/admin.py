from django.contrib import admin
from .models import Atributo


@admin.register(Atributo)
class AtributoAdmin(admin.ModelAdmin):

    list_display = (
        'id_atributo',
        'nombre',
        'descripcion'
    )

    search_fields = (
        'nombre',
        'descripcion'
    )

    ordering = (
        'nombre',
    )
