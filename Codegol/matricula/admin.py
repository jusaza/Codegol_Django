from django.contrib import admin
from .models import Matricula

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_jugador', 'fecha_inicio', 'fecha_fin', 'nivel', 'estado')
    search_fields = ('id_jugador__nombre_completo', 'nivel')
    list_filter = ('nivel', 'estado')
