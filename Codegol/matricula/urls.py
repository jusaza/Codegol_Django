from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_matricula, name='lista_matricula'),
    path('crear/', views.crear_matricula, name='crear_matricula'),
    path('editar/<int:id>/', views.editar_matricula, name='editar_matricula'),
    path('eliminar/<int:id>/', views.eliminar_matricula, name='eliminar_matricula'),
]
