from django.urls import path
from .views import panel_actividad_atributo

urlpatterns = [
    path('panel/', panel_actividad_atributo, name='panel_actividad_atributo'),
]