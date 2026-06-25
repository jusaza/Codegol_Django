from django.contrib import admin
from .models import MovimientoInventario


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'id_movimiento',
        'inventario',
        'usuario',
        'tipo_movimiento',
        'cantidad',
        'fecha',
        'movimiento_padre',
    )

    list_filter = (
        'tipo_movimiento',
        'fecha',
        'inventario',
    )

    search_fields = (
        'inventario__nombre_articulo',
        'usuario__nombre_completo',
        'usuario__num_identificacion',
        'observaciones',
    )

    ordering = ('-fecha',)

    readonly_fields = (
        'fecha',
    )

    autocomplete_fields = (
        'inventario',
        'usuario',
        'movimiento_padre',
    )

