from django.contrib import admin
from .models import Matricula, HistorialCategoria


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_jugador',
        'posicion',
        'nivel',
        'fecha_inicio',
        'fecha_fin',
        'fecha_matricula',
        'estado',
    )

    list_filter = (
        'estado',
        'nivel',
        'fecha_inicio',
        'fecha_fin',
        'fecha_matricula',
        'posicion',
    )

    search_fields = (
        'id_jugador__nombre_completo',
        'id_jugador__num_identificacion',
        'observaciones',
    )

    ordering = ('-fecha_matricula',)

    readonly_fields = (
        'fecha_matricula',
    )


@admin.register(HistorialCategoria)
class HistorialCategoriaAdmin(admin.ModelAdmin):
    list_display = (
        'id_historial',
        'id_matricula',
        'id_categoria',
        'fecha_registro',
        'estado',
    )

    list_filter = (
        'estado',
        'fecha_registro',
        'id_categoria',
    )

    search_fields = (
        'id_matricula__id_jugador__nombre_completo',
        'id_matricula__id_jugador__num_identificacion',
        'id_categoria__nombre_categoria',
        'observacion',
    )

    ordering = ('-fecha_registro',)
