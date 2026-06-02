from django.urls import path
from . import views

urlpatterns = [

    path(
        'sesion/<int:id_sesion>/categoria/<int:id_categoria>/',
        views.tabla_rendimiento,
        name='tabla_rendimiento'
    ),

    path(
        'sesion/<int:id_sesion>/guardar/',
        views.guardar_rendimiento,
        name='guardar_rendimiento'
    ),

    path(
        'historial/',
        views.historial_rendimiento,
        name='historial_rendimiento'
    ),
]