from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('<int:id_entrenamiento>/', views.lista_sesiones, name='lista_sesiones'),
    path('crear/<int:id_entrenamiento>/', views.crear_sesion, name='crear_sesion'),
    path('editar/<int:id>/', views.editar_sesion, name='editar_sesion'),
    path('eliminar/<int:id>/', views.eliminar_sesion, name='eliminar_sesion'),
    path('salidas/', include('movimiento_inventario.urls')),
    path('asistencia/', include('asistencia.urls')),
]