from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.panel_posicion_actividad, name='panel_posicion_actividad'),

    path('posicion/editar/<int:id>/', views.editar_posicion, name='editar_posicion'),
    path('posicion/eliminar/<int:id>/', views.eliminar_posicion, name='eliminar_posicion'),

    path('relacion/toggle/<int:id>/', views.toggle_obligatorio, name='toggle_obligatorio'),
    path('relacion/eliminar/<int:id>/', views.eliminar_relacion, name='eliminar_relacion'),

    path('actividad/editar/<int:id>/', views.editar_actividad, name='editar_actividad'),
]