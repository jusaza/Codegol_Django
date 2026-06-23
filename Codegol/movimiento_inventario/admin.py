from django.contrib import admin
from .models import MovimientoInventario

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('id_movimiento', 'inventario', 'cantidad', 'tipo_movimiento', 'fecha')
    search_fields = ('inventario__nombre_articulo',)
    list_filter = ('tipo_movimiento', 'fecha')

