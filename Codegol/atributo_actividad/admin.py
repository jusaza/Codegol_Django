from django.contrib import admin
from .models import ActividadAtributo


@admin.register(ActividadAtributo)
class ActividadAtributoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'actividad',
        'atributo',
        'peso'
    )

    list_filter = (
        'actividad',
        'atributo'
    )

    search_fields = (
        'actividad__nombre',
        'atributo__nombre'
    )

    ordering = (
        'actividad',
        'atributo'
    )
