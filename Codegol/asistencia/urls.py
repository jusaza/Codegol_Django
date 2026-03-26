from django.urls import path
from . import views

urlpatterns = [

    # 🔥 Vista principal (tabla dinámica)
    path(
        'sesion/<int:id_sesion>/',
        views.tabla_asistencia,
        name='tabla_asistencia'
    ),

    # 🔥 Guardado AJAX
    path(
        'sesion/<int:id_sesion>/guardar/',
        views.guardar_asistencia,
        name='guardar_asistencia'
    ),
]