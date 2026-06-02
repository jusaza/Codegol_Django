from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_categoria, name='lista_categoria'),
    path('crear/', views.crear_categoria, name='crear_categoria'),
    path('editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
]