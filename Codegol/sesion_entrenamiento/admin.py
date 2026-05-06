from django.contrib import admin

# Register your models here.
from .models import SesionEntrenamiento

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('id_sesion', 'id_entrenamiento', 'id_entrenador', 'fecha', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('id_entrenamiento__id_entrenamiento',)