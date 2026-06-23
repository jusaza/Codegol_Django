from django.urls import path
from . import views

urlpatterns = [
    path('sesion/<int:id_sesion>/categoria/<int:id_categoria>/', views.tabla_asistencia, name='tabla_asistencia'),
    path(
    'sesion/<int:id_sesion>/categoria/<int:id_categoria>/guardar/',
    views.guardar_asistencia,
    name='guardar_asistencia'
),
]