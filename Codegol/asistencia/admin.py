from django.contrib import admin
from .models import Asistencia


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):

    list_display = (
        'id_asistencia',
        'id_sesion',
        'id_matricula',
        'id_categoria',
        'tipo_asistencia'
    )

    list_filter = (
        'tipo_asistencia',
        'id_categoria'
    )

    search_fields = (
        'id_matricula__id_jugador__nombre_completo',
        'justificacion',
        'observaciones'
    )

    autocomplete_fields = (
        'id_sesion',
        'id_matricula',
        'id_categoria'
    )

    ordering = (
        '-id_asistencia',
    )
