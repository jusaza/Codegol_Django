from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('', views.lista_inventario, name='lista_inventario'),
    path('crear/', views.crear_inventario, name='crear_inventario'),
    path('editar/<int:id>/', views.editar_inventario, name='editar_inventario'),
    path('eliminar/<int:id>/', views.eliminar_inventario, name='eliminar_inventario'),
    path('movimientos/', include('movimiento_inventario.urls')),

]