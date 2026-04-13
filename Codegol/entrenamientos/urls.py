from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.lista_entrenamientos, name='lista_entrenamientos'),
    path('crear/', views.crear_entrenamiento, name='crear_entrenamiento'),
    path('editar/<int:id>/', views.editar_entrenamiento, name='editar_entrenamiento'),
    path('eliminar/<int:id>/', views.eliminar_entrenamiento, name='eliminar_entrenamiento'),
    path('sesiones/', include('sesion_entrenamiento.urls')),
]