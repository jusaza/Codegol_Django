from django.contrib import admin
from .models import Entrenamiento

@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('id_entrenamiento', 'descripcion', 'estado', 'lugar')
    search_fields = ('descripcion', 'lugar')
    list_filter = ('estado',)
