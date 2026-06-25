# urls.py COMPLETO

from django.urls import path
from . import views

urlpatterns = [

    path(
        'actividades/',
        views.lista_actividades,
        name='lista_actividades'
    ),

    path(
        'crear-actividad/',
        views.crear_actividad,
        name='crear_actividad'
    ),

    path(
        'editar-actividad-lista/<int:id>/',
        views.editar_actividad_lista,
        name='editar_actividad_lista'
    ),

    path(
        'eliminar-actividad-lista/<int:id>/',
        views.eliminar_actividad_lista,
        name='eliminar_actividad_lista'
    ),

    path(
        'panel/',
        views.panel_posicion_actividad,
        name='panel_posicion_actividad'
    ),

    path(
        'posicion/editar/<int:id>/',
        views.editar_posicion,
        name='editar_posicion'
    ),

    path(
        'posicion/eliminar/<int:id>/',
        views.eliminar_posicion,
        name='eliminar_posicion'
    ),

    path(
        'actividad/editar/<int:id>/',
        views.editar_actividad,
        name='editar_actividad'
    ),

    path(
        'actividad/eliminar/<int:id>/',
        views.eliminar_actividad,
        name='eliminar_actividad'
    ),

    path(
        'relacion/eliminar/<int:id>/',
        views.eliminar_relacion,
        name='eliminar_relacion'
    ),

]