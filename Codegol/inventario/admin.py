from django.contrib import admin
from .models import Inventario
# Register your models here.
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('id_inventario', 'nombre_articulo', 'descripcion', 'estado')
    search_fields = ('nombre_articulo', 'descripcion')
    list_filter = ('estado',)