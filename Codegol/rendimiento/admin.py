from django.contrib import admin
from .models import Rendimiento


@admin.register(Rendimiento)
class RendimientoAdmin(admin.ModelAdmin):
    list_display = (
        'id_rendimiento',
        'matricula',
        'sesion',
        'actividad',
        'atributo',
        'id_categoria',
        'valor',
        'fecha',
    )

    list_filter = (
        'actividad',
        'atributo',
        'id_categoria',
        'fecha',
    )

    search_fields = (
        'matricula__id_jugador__nombre_completo',
        'matricula__id_jugador__num_identificacion',
        'actividad__nombre',
        'atributo__nombre',
        'id_categoria__nombre_categoria',
    )

    ordering = (
        '-fecha',
    )

    readonly_fields = (
        'fecha',
    )

    autocomplete_fields = (
        'matricula',
        'sesion',
        'actividad',
        'atributo',
        'id_categoria',
    )
