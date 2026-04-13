from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_jugadores, name='lista_jugadores'),
    

]